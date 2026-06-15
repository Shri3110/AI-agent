# Edge Cases & Corner Cases: Weekly Review Pulse (Groww)

This document outlines potential edge cases, failure modes, and corner cases for the Weekly Product Review Pulse system, categorized by module. 

## 1. Data Ingestion (Scraper)

* **Zero Reviews in Window**: The scraper finds absolutely no reviews in the designated 8-12 week rolling window (e.g., if the app was temporarily removed from the Play Store or reviews were wiped).
  * *Mitigation*: The orchestrator should gracefully log a warning and exit without triggering the LLM or sending empty emails.
* **Massive Review Spike (Viral Event)**: A sudden influx of 100,000+ reviews within a week, potentially causing out-of-memory (OOM) errors during clustering or massive token usage costs with the LLM.
  * *Mitigation*: Enforce a hard `max_results` cap (currently 50,000 in scraper, but can be strictly bounded) and prioritize reviews by "thumbs up count" or length if truncation is necessary.
* **Scraper Dependency Breakage**: Google Play Store updates its undocumented internal APIs or DOM structure, causing the `google-play-scraper` library to fail silently or throw parsing errors.
  * *Mitigation*: Wrap the scraper in a broad `try/except` block and alert an admin if ingestion fails completely.

## 2. PII Scrubbing & Analysis Engine

* **Non-English or Gibberish Reviews**: Users submitting reviews in Hindi, Hinglish, regional languages, or pure emojis. 
  * *Impact*: The embedding model (`all-MiniLM-L6-v2`) is English-focused and may cluster these poorly.
  * *Mitigation*: Add a language detection filter (e.g., `langdetect`) before embedding, dropping non-English reviews, or upgrade to a multilingual embedding model.
* **PII Scrubber False Positives/Negatives**: 
  * *False Positives*: A user types "My order number is 9876543210" and it gets scrubbed as a phone number, losing context.
  * *False Negatives*: Unconventional PII formats slip through to the LLM.
* **LLM Hallucinations (Fake Quotes)**: The LLM generates a "verbatim" quote that sounds realistic but never actually appeared in the source reviews.
  * *Mitigation*: Implement a post-LLM validation step checking if `quote in raw_review_text`. If false, drop the quote.
* **Groq API Downtime/Rate Limits**: The Groq API is unreachable, or the agent hits rate limits (HTTP 429).
  * *Mitigation*: Implement exponential backoff and retries in the `AnalysisEngine`. 
* **Zero Variance Clustering**: All fetched reviews are identical (e.g., a bot attack saying "Good app"). HDBSCAN may fail to find distinct clusters.

## 3. Delivery & MCP Servers

* **Stale or Revoked OAuth Tokens**: The Google Workspace credentials used by the MCP servers expire or are revoked by IT.
  * *Impact*: Silent failures during the final delivery step.
  * *Mitigation*: MCP servers must return clear authentication error codes back to the orchestrator to trigger an alert.
* **Google Doc Deletion/Corruption**: The target "Weekly Review Pulse" Google Doc is accidentally deleted by a stakeholder, or its ID changes.
  * *Mitigation*: The Doc MCP server should verify the Doc exists before attempting to append, and fail gracefully if not found.
* **Email Size Limits**: If the LLM generates an exceptionally long teaser, the Gmail API might reject the payload.

## 4. Orchestration & Idempotency

* **Mid-Execution Crashes (Partial State)**: The script crashes *after* appending the Google Doc, but *before* sending the Gmail, and *before* writing to the local SQLite audit database. 
  * *Impact*: The next run will think the week hasn't been processed and will append a duplicate section to the Google Doc.
  * *Mitigation*: Use a transactional approach where the Doc anchor is checked via the Docs API directly instead of relying solely on the local SQLite state, or use a robust queue.
* **Timezone / ISO Week Boundary Shifts**: A cron job runs exactly at Sunday 11:59 PM vs Monday 12:01 AM, accidentally classifying the run into the wrong ISO week.
  * *Mitigation*: The CLI strictly accepts an explicit `--iso-week` parameter when invoked by the cron scheduler, rather than relying on the script's internal clock at runtime.
* **Backfill Overlap**: A manual CLI run attempts to backfill `2026-W40` using an 8-week window, but the current date is `2026-W48`. The "rolling 8 weeks" logic from the scraper might ingest the wrong dates if not anchored to the requested ISO week.
  * *Mitigation*: The scraper logic must dynamically calculate its `cutoff_date` and `end_date` relative to the requested `--iso-week`, not relative to `datetime.now()`.
