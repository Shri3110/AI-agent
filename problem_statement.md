# Problem Statement — Weekly Product Review Pulse (Groww)

## Overview

We are building an automated weekly "pulse" that turns public Google Play Store reviews for **Groww** into a one-page insight report and delivers it to stakeholders through Google Workspace. All writes to Google Docs and Gmail go through dedicated **MCP (Model Context Protocol) servers** that are created and provided within this project — not through ad hoc API calls inside the agent.

---

## The Problem We Are Solving

Product, support, and leadership teams currently have no repeatable, automated way to understand what customers are saying in app store reviews. Insights require manual copy-paste, one-off spreadsheets, and periodic human effort. There is no system of record, no consistent cadence, and no audit trail of what was observed and when.

---

## What We Are Building

A weekly automated pipeline that:

1. **Ingests** public reviews from the **Google Play Store** for Groww, covering a rolling 8–12 week window (configurable).
2. **Clusters and ranks** feedback using embeddings and density-based clustering (UMAP + HDBSCAN), then uses an LLM to name themes, surface verbatim quotes, and propose action ideas. Quotes are validated to appear in real review text.
3. **Renders** a concise one-page narrative covering: top themes, real user quotes, action ideas, and a short "who this helps" summary.
4. **Delivers outputs** exclusively through MCP servers provided in this project:
   - **Google Docs MCP** — appends each week's report as a new dated section to a single running document (*Weekly Review Pulse — Groww*). This Doc is the system of record and preserves history.
   - **Gmail MCP** — sends a short stakeholder email with a deep link to the new section in the Doc (not a duplicate full report in the email).

---

## Scope for This Build

| Dimension | Decision |
|---|---|
| Product | Groww only |
| Review source | Google Play Store only (Apple App Store excluded) |
| MCP servers | Built and provided within this project |
| Delivery | Google Docs (append) + Gmail (send/draft) via project MCP servers |
| Cadence | Once per week per run; CLI available for backfill by ISO week |

---

## System Modularity

| Concern | Where it lives |
|---|---|
| Data retrieval | Ingestion module — Google Play Store scraper |
| Reasoning | Clustering + LLM summarisation (themes, quotes, actions) |
| Output generation | Report renderer + email renderer |
| Human-visible delivery | MCP tools only → Google Docs MCP + Gmail MCP |

The agent acts as an MCP host/client. It does not embed Google credentials or call Docs/Gmail REST APIs directly for delivery — those concerns belong to the MCP servers.

---

## Key Requirements

- **MCP-based delivery**: All writes to Google Docs and all email sends/drafts go through the MCP servers provided in this project.
- **Weekly cadence**: Designed to run once per week (e.g. scheduled Monday morning IST), with CLI support for backfilling any ISO week.
- **Idempotent runs**: Re-running the same ISO week must not create duplicate Doc sections or send duplicate emails. Enforced via a stable section anchor in the Doc and a run-scoped idempotency check on email.
- **Auditable**: Each run records delivery identifiers (Doc heading, Gmail message IDs) and enough metadata to answer "what was sent, when, for which week?"
- **Safety and quality**: PII scrubbing on review text before LLM processing and before publishing. Reviews are treated as data, not instructions. Cost/token limits enforced per run.

---

## Non-Goals (Explicit)

- Apple App Store reviews — excluded from this build.
- Multi-product support — only Groww in this build.
- Real-time streaming analytics or a BI dashboard.
- Social sources (Twitter, Reddit, etc.).
- Storing Google OAuth secrets in the agent codebase — they belong in the MCP server configuration.

---

## Who This Helps

| Audience | Value |
|---|---|
| Product | Prioritise roadmap from recurring themes |
| Support | Spot repeating complaints and quality issues |
| Leadership | Fast weekly health snapshot tied to customer voice |

---

## Illustrative Output

**Groww — Weekly Review Pulse**
*Period: Rolling 8–12 week window*

**Top themes**
- App performance & bugs — Lag, crashes during trading hours; login/session timeouts.
- Customer support friction — Slow responses; unresolved tickets.
- UX & feature gaps — Confusing navigation for portfolio insights; missing advanced analytics.

**Real user quotes**
- "The app freezes exactly when the market opens, very frustrating."
- "Support takes days to reply and doesn't solve the issue."
- "Good for beginners but lacks detailed analysis tools."

**Action ideas**
- Stabilise peak-time performance — Scale infra during market hours; improve crash visibility.
- Improve support SLA visibility — Show expected response time in-app; add ticket status tracking.
- Enhance power-user features — Advanced portfolio analytics; clearer investments navigation.

---

## Delivery Expectations

- Each run adds one clearly labelled, dated section to the Groww pulse Google Doc.
- The email is a brief teaser (top themes as bullets) plus a "Read full report" link to that section.
- Development/staging defaults to **draft-only email** until explicit confirmation to send.
