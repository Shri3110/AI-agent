# Implementation Plan: Weekly Product Review Pulse (Groww)

This document outlines the phased implementation plan for the automated weekly product review pulse system, based on the `problem_statement.md` and `architecture.md` specifications.

## User Review Required

> [!IMPORTANT]
> Please review the proposed phases below. Pay special attention to the choice of technologies (e.g., Python as the primary language, specific LLMs/Embedding models) and let me know if there are any specific constraints or preferred tech stacks for the MCP servers or the main pipeline before execution begins.

## Open Questions

> [!WARNING]
> 1. **Tech Stack**: Are we standardizing on Python for the main agent and TypeScript/Python for the MCP servers? 
> 2. **Infrastructure**: Where will this pipeline and the MCP servers be hosted (e.g., AWS, GCP, local server)?

## Proposed Changes

### Phase 1: Foundation & Data Ingestion
*Focus: Setting up the core project and retrieving raw data.*

- **Repository Setup**: Initialize the project structure, configuration management, and logging frameworks.
- **CLI Entrypoint**: Create the basic CLI structure for manual execution and backfilling by ISO week.
- **Play Store Scraper**: Implement the ingestion module to fetch public reviews for Groww from the Google Play Store, filtering by a rolling 8–12 week window.
- **Data Models**: Define the schemas/classes for raw reviews to ensure typed data flow.

### Phase 2: Processing & Analysis Engine
*Focus: Turning raw text into clustered, sanitized insights.*

- **PII Scrubbing**: Implement safety filters/heuristics (or use a local/lightweight NLP model) to redact phone numbers, emails, names, etc., from raw reviews.
- **Hinglish/Language Normalization (Groq)**: Use Groq's fast LLM inference (`llama-3.3-70b-versatile`) to batch translate all reviews (especially Romanized Hindi/Hinglish) into pure English before embedding, ensuring high-quality semantic vectors. Includes exponential backoff/pacing for the 12K TPM limit.
- **Embedding Generation**: Integrate an embedding model API to generate dense vectors for the scrubbed reviews.
- **Clustering (UMAP + HDBSCAN)**: Implement the density-based clustering pipeline to group semantically similar reviews together.
- **LLM Summarization (Groq)**: Integrate Groq's fast inference API (`llama-3.3-70b-versatile`) to process each cluster, prompting the LLM to extract concise themes, select verbatim user quotes (with validation against source text), and propose action ideas. Includes built-in pacing to respect API rate limits.

### Phase 3: MCP Servers Development
*Focus: Building the delivery infrastructure isolated from the main agent.*

- **Google Docs MCP Server**:
  - Implement OAuth/Service Account authentication to Google Workspace.
  - Expose a tool to append a formatted Markdown/Text section to a specific Google Doc ID.
  - Return a stable anchor/bookmark link to the newly appended section.
- **Gmail MCP Server**:
  - Implement Gmail API integration.
  - Expose a tool to create a draft or send an email (controlled by environment/config).
  - Support adding links (specifically the Doc anchor) to the email body.

### Phase 4: Rendering & Orchestration
*Focus: Formatting outputs and tying the pipeline together safely.*

- **Output Renderers**: Create templates to format the LLM outputs into the target Google Doc narrative format and the brief Email teaser format.
- **Idempotency & Auditing**:
  - Implement a check to verify if the current ISO week has already been successfully processed (e.g., by checking a local SQLite DB or a specific metadata file/log).
  - Implement audit logging to record Doc heading links, Gmail message IDs, and token usage per run.
- **Integration**: Wire the Orchestrator to sequentially call Ingestion -> Analysis -> Renderer -> MCP Delivery.

### Phase 5: Testing, Validation & Deployment
*Focus: Ensuring reliability and setting up the weekly schedule.*

- **End-to-End Testing**: Run the full pipeline in a staging environment (draft-only emails, test Google Doc).
- **Validation**: Verify that PII is correctly scrubbed and that generated quotes are truly verbatim from the raw data.
- **Scheduling**: Set up the cron job or external scheduler (e.g., GitHub Actions, Airflow, or local cron) to trigger the pipeline every Monday morning IST.

## Verification Plan

### Automated Tests
- Unit tests for the Play Store scraper (mocking HTTP requests).
- Unit tests for the clustering logic with dummy embeddings.
- Tests for the PII scrubber to ensure sensitive formats are caught.

### Manual Verification
- Execute a dry run for the current ISO week and manually verify the generated report formatting in a test Google Doc.
- Verify that the Gmail MCP server successfully creates an email draft containing the correct deep link to the test Google Doc.
- Test the CLI backfill command for a previous ISO week to ensure idempotency is correctly respected on consecutive runs.
