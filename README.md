# ATS Engine
# ATS Engine

## Table of contents

1. Purpose
2. Executive summary
3. System goals and non-goals
4. High-level architecture
5. Detailed component reference
    - Frontend
    - Backend API
    - Parsing service
    - AI / prompts
    - Scoring
    - Optimization / Tailoring
    - Exporters
    - Storage & database
    - Authentication & user management
6. Data Flow Diagram (DFD)
7. Sequence flows and examples
8. API reference (endpoints, payloads, examples)
9. Database schema overview
10. Prompts and prompt engineering guide
11. Development environment & quickstart
12. Testing and CI
13. Deployment and infrastructure guidance
14. Security, privacy, and compliance considerations
15. Operational runbook
16. Troubleshooting
17. Extending the system
18. Contributing guidelines
19. FAQs
20. Glossary
21. Changelog
22. License

---

## 1. Purpose

This repository implements the ATS Engine: an integrated system for parsing resumes, extracting structured data, scoring resumes against Applicant Tracking Systems (ATS) heuristics, and producing tailored resume variants and export artifacts. The system is intended for recruiters, career platforms, and resume-improvement services who need a repeatable, auditable pipeline to transform raw resume files into structured, analyzable data and human-readable artifacts.

Key motivations:

- Reduce manual resume parsing labor by automating extraction and normalization.
- Provide an objective, repeatable ATS score and remediation suggestions.
- Enable tailored resume generation for specific job descriptions.
- Offer export formats suitable for applicant submissions and archival.

Intended users:

- Product teams building resume tooling.
- Recruiters and hiring platforms.
- Developers integrating resume features into HR systems.

Out of scope (non-goals):

- Serving as a full applicant tracking system (we focus on resume processing and scoring).
- Building a complete job matching recommendation engine (can be integrated later).

---

## 2. Executive summary

The ATS Engine combines three core capabilities:

1. File ingestion and parsing: robust extraction of text and structure from PDF, DOCX, and plain-text resumes.
2. AI-assisted extraction and transformation: prompts and LLM workflows convert raw text into structured records (work experience, education, skills, achievements).
3. Scoring and optimization: a scoring engine provides ATS-sensitivity metrics and guided optimizations; an optimizer can produce tailored resume variants.

The architecture decouples concerns: the frontend handles user interaction, the backend orchestrates processing, and specialized services perform parsing, scoring, and exporting. This separation allows scaling of computationally intensive tasks and substitution of AI providers.

---

## 3. System goals and non-goals (expanded)

Goals (detailed):

- Accuracy: Achieve high recall for section detection (experience, education, skills) across varied resume templates.
- Explainability: Produce explainable scoring components so users can see why specific suggestions were made.
- Extensibility: Make it straightforward to add new exporters, scoring rules, or prompt variants.
- Privacy-preserving: Minimize retention of sensitive content and provide clear purge policies.
- Practical performance: Support typical resume parsing and scoring in under a few seconds per file (depending on provider and compute).

Non-goals (detailed):

- Real-time collaborative editing of resumes inside the tool.
- Full HR lifecycle management (interviews, offers, onboarding).

---

## 4. High-level architecture

Components and relationships (summary):

- Frontend (Next.js): upload, preview, history, user settings, and visualization of scores.
- Backend API (FastAPI): request handling, job orchestration, storage management, authentication.
- Parsing Service: file transformation (PDF/DOCX -> plain text), heuristic extraction, initial normalization.
- AI / LLM Service: prompt-based extraction, refinement, and content generation.
- Scoring Service: rule-based + ML heuristics to compute ATS compatibility scores.
- Optimization Service: generates recommended edits and tailored resume variants.
- Exporters: produce PDF/DOCX/JSON and other deliverables.
- Database (Postgres / Prisma and Alembic migrations): stores users, resumes, reports, and job-target mappings.
- File Storage (local, S3, or equivalent): stores uploaded files, intermediate artifacts, and exports.

Diagram (visualization is below in section 6). The system is designed so that the backend orchestrates long-running tasks using a queuing system (optional) and worker processes.

---

## 5. Detailed component reference

This section describes each major component, responsibilities, key files, and extension points. Use this as a developer reference when making changes or adding features.

### 5.1 Frontend (Next.js)

Location: `src/`

Responsibilities:

- User authentication flows (login, register, password reset).
- Resume upload UI with drag-and-drop and file validation.
- Job-target input for tailoring (paste job description or select job profile).
- Display of parsing results, section extraction, and ATS score breakdown.
- Editor for suggested edits and side-by-side comparison of original vs tailored versions.
- Download links for exports.

Key components (examples):

- Upload zone: `src/components/resume/upload-zone.tsx` — handles file selection, drag-and-drop, and upload progress.
- ATS Score card: `src/components/resume/ats-score-card.tsx` — visual score and breakdown.
- Preview/editor: `src/resume/editor/` — editing UI for results.

Extension points:

- Add new views for additional export types.
- Plug in analytics or product telemetry for feature usage.

Frontend environment variables:

- `NEXT_PUBLIC_API_BASE_URL` — base URL for the backend API.
- `NEXT_PUBLIC_SENTRY_DSN` — optional error tracking.

Local dev commands (see Quickstart for full flow):

```bash
npm install
npm run dev
```

### 5.2 Backend API (resume_engine/app)

Location: `resume_engine/app/`

Responsibilities:

- Expose REST endpoints for resume ingestion, retrieval, scoring, and exporting.
- Coordinate parsing, AI calls, scoring, and exporting workflows.
- Manage user accounts, permissions, and records in the database.

Key modules:

- `app/api/` — endpoint definitions and exception handlers.
- `app/services/` — high-level orchestration services (resume_service, user_service, export_service).
- `app/models/` — ORM or schema models.
- `app/schemas/` — Pydantic request/response schemas.
- `app/db/` — database session and migration helpers.

Important considerations:

- Keep API handlers thin; delegate heavy work to services and background workers.
- Implement idempotency for resume ingestion endpoints to avoid duplicate processing.

Authentication:

- JWT-based sessions with refresh tokens are typical; `app/core/security.py` contains helpers.

Start the API locally:

```bash
uvicorn resume_engine.main:app --reload
```

### 5.3 Parsing Service

Location: `resume_engine/app/services/parsers` (or similar)

Responsibilities:

- Convert input files (PDF, DOCX, TXT) to a canonical plain-text representation.
- Detect sections (experience, education, skills) using heuristics and rules.
- Normalize dates, extract bullet lists, and detect inline formatting cues (bold for headings).

Approach details:

- Use robust PDF extraction libraries (pdfminer, pdfplumber, or external OCR for scanned PDFs).
- Use python-docx for DOCX parsing.
- Implement fallback heuristics for ambiguous formatting.

Outputs:

- Raw text file stored in storage.
- Parsed JSON with candidate sections and offsets for downstream LLM extraction.

### 5.4 AI / Prompts

Location: `prompts/` and `resume_engine/app/services/ai`

Responsibilities:

- Use prompt templates to guide LLMs to extract structured fields from raw text.
- Provide optimization guidance: suggest rewritten bullet points, quantify achievements, and add keywords.
- Validate outputs and map them back to internal schemas.

Prompt engineering best practices:

- Use system-level context to define the desired output format (JSON schema, strict keys).
- Provide few-shot examples for tricky extraction cases (dates in multiple formats, multi-job entries).
- Validate LLM output: schema-check (Pydantic) and fallback to heuristics if extraction confidence is low.

LLM integration patterns:

- Synchronous call: for small files and quick extraction.
- Async/queued: for heavy or batched processing.

Configuration:

- Support multiple providers (OpenAI, Anthropic, local LLMs) via an adapter layer.

### 5.5 Scoring Service

Location: `resume_engine/app/services/scoring` (or similar)

Responsibilities:

- Compute an ATS compatibility score using a set of rules and heuristics.
- Break down the score by categories: keywords, sections present, formatting, contact info, chronology, and readability.
- Provide actionable feedback that can be presented to users.

Scoring approach (example):

- Keywords: match against job description keywords using fuzzy matching and synonyms.
- Sections: reward presence of Experience, Education, Skills, Contact Info.
- Formatting: reward machine-readable sections and penalize unusual fonts or images-only content.
- Chronology: detect gaps and inconsistent date ranges.

Scoring outputs:

- Numeric score (0-100).
- Category breakdown with weights and recommendations.

### 5.6 Optimization / Tailoring Service

Location: `resume_engine/app/services/optimization` or `prompts/tailoring`

Responsibilities:

- Generate tailored resume variants for a target job description.
- Rephrase bullets, emphasize matching keywords, and reorder sections when beneficial.

Approach:

- Use the extracted structured data as the authoritative source for transformations.
- Preserve factual content; avoid inventing unsupported facts.
- Generate multiple candidate variants and score them automatically.

Human-in-the-loop:

- Present suggestions and let users accept/reject edits in the frontend editor.

### 5.7 Exporters

Location: `resume_engine/app/services/exporters` or `exporters/`

Responsibilities:

- Render structured or tailored resume content into deliverables: PDF, DOCX, and JSON.
- Ensure consistent styling for templates and preserve applicant data.

Implementation notes:

- Use templating engines (WeasyPrint, ReportLab, or native DOCX templates) to produce high-quality PDFs.
- Ensure exports are sanitized and do not leak internal metadata unless requested.

### 5.8 Storage & Database

Storage:

- Use object storage (S3-compatible) for file durability and scalable storage.
- Keep uploads in a private bucket, generate presigned URLs for downloads.

Database:

- Use Postgres with Prisma (or SQLAlchemy) for schema migrations and data access.
- Store normalized resume records, user profiles, job profiles, and report metadata.

Schema considerations:

- Resume records should reference stored files and structured JSON versions.
- Reports should be versioned to track changes and tailored variants.

### 5.9 Authentication & User Management

Responsibilities:

- Secure access to resume data via authentication and role-based access control.
- Allow users to manage their data and authorship of tailored variants.

Implementation:

- JWT for API access with refresh tokens.
- Optional OAuth integration for enterprise use (Google, Microsoft).

---

## 6. Data Flow Diagram (DFD)

This section contains multiple visualizations and text descriptions to help architects and devs understand the flows.

High-level DFD (mermaid):

```mermaid
flowchart LR
   U[User]
   FE[Frontend (Next.js)]
   API[Backend API (resume_engine/app)]
   Parser[Parsing Service]
   AI[AI / LLM Service]
   Score[Scoring Service]
   Opt[Optimization Service]
   Export[Exporters]
   DB[(Database)]
   Storage[(File Storage / S3)]

   U -->|upload resume| FE
   FE -->|POST /resumes| API
   API -->|save raw file| Storage
   API -->|create record| DB
   API -->|queue parse job| Parser
   Parser -->|extract text| Storage
   Parser -->|structured payload| API
   API -->|call prompts| AI
   AI -->|extracted entities| API
   API -->|compute score| Score
   Score -->|score result| API
   API -->|request tailoring| Opt
   Opt -->|tailored resume| API
   API -->|generate artifacts| Export
   Export -->|artifact files| Storage
   API -->|return results| FE
   FE -->|display downloads & report| U

   DB -->|store metadata & reports| API

   classDef service fill:#f9f,stroke:#333,stroke-width:1px;
   class Parser,AI,Score,Opt,Export service;
```

DFD explanation (detailed):

- User uploads a resume through the frontend; the frontend streams the file to the backend API.
- The backend persists the raw file in Storage and inserts a resume record in the Database with status `uploaded`.
- The backend enqueues a parse job for the Parsing Service. A worker picks up the job and converts the file to canonical text and a candidate JSON structure.
- The parsing output is written back to Storage and a draft structured payload is returned to the API.
- The API invokes the AI Service to refine extraction using prompt templates. The LLM returns a validated JSON following the schema.
- The Scoring Service computes the ATS compatibility score and stores the report in the Database.
- If tailoring is requested, the Optimization Service generates tailored variants and scores them; the best variants are stored and exported.
- The Exporters produce final artifacts and write them to Storage; their download links are returned to the frontend.

Security boundaries:

- The LLM provider endpoint is external; credentials must be kept secret and rate-limited.
- Storage access should be limited to the backend and worker processes.

---

## 7. Sequence flows and examples

This section provides example sequences for common actions: "Upload and score a resume", "Tailor resume for a job", and "Regenerate exports".

### 7.1 Upload and score

1. Frontend POSTs file to `POST /api/resumes` with minimal metadata.
2. Backend responds with `202 Accepted` and a resume `id`.
3. Backend writes raw file to Storage and creates DB record with status `queued`.
4. Worker picks up parse job, writes canonical text to Storage, and creates a draft JSON.
5. Backend calls AI Service with the draft JSON and prompt instructions.
6. AI returns structured entities; backend validates and writes final structured JSON to the DB.
7. Scoring service computes a score and stores the report.
8. Backend notifies frontend (via websocket or polling); frontend fetches report and displays it.

Payload examples (abbreviated):

Request: `POST /api/resumes`

```json
{
   "filename": "jane_doe_resume.pdf",
   "user_id": "user_123",
   "target_job_id": null
}
```

Response: `202 Accepted`

```json
{
   "resume_id": "resume_456",
   "status": "queued"
}
```

### 7.2 Tailor for a job

1. User provides a job description or selects a saved job target.
2. Frontend calls `POST /api/resumes/{id}/tailor` with `job_text` or `job_id`.
3. Backend creates an optimization job and sets status `tailoring`.
4. Optimizer uses extracted structured data and job keywords, runs LLM prompts to rephrase and emphasize matching skills.
5. Tailored variant is scored and stored.
6. Frontend displays diff and download options.

---

## 8. API reference (selected endpoints)

This section documents primary endpoints. For a complete OpenAPI spec, see `resume_engine/openapi.json` or generate one from the codebase.

### POST /api/resumes

- Description: Upload a new resume.
- Request: multipart/form-data with `file` and optional JSON `metadata`.
- Response: `202 Accepted` with `resume_id`.

Example curl:

```bash
curl -X POST "${API_BASE}/api/resumes" \
   -H "Authorization: Bearer ${TOKEN}" \
   -F file=@jane_resume.pdf \
   -F metadata='{"user_id":"user_123"}'
```

### GET /api/resumes/{id}

- Description: Retrieve resume metadata and processing status.
- Response: JSON with `status`, `score`, `structured_data` (if ready), and `exports`.

### POST /api/resumes/{id}/tailor

- Description: Create a tailored variant for a job description.
- Request: `{ "job_text": "..." }` or `{ "job_id": "..." }`.
- Response: `202 Accepted` with `job_id`.

### GET /api/resumes/{id}/exports

- Description: List generated export artifacts and presigned download URLs.

Authentication / errors

- `401 Unauthorized` if the token is missing or invalid.
- `404 Not Found` if resume id is invalid.
- `429 Too Many Requests` if rate limits are exceeded.

---

## 9. Database schema overview

This section describes primary tables/collections and key fields. The exact schema lives in `prisma/` and migration files.

Core entities:

- `users` — id, email, hashed_password, created_at, last_login.
- `resumes` — id, user_id, original_filename, storage_key, structured_json_id, status, created_at.
- `structured_json` — id, resume_id, json_payload, parsed_at.
- `reports` — id, resume_id, score, breakdown_json, created_at.
- `exports` — id, resume_id, type (pdf, docx, json), storage_key, created_at.

Indexing recommendations:

- Index `resumes.user_id` for fast user-specific queries.
- Index `reports.created_at` for retention cleanup.

Migration strategy:

- Use Alembic (for SQLAlchemy) or `prisma migrate` to manage schema changes.

---

## 10. Prompts and prompt engineering guide

This section documents the prompt patterns used across extraction, validation, optimization, and tailoring.

Principles:

- Always supply a strict JSON schema in the system prompt and require `json` output.
- Give examples for ambiguous cases.
- Use a two-step approach: (1) ask the LLM to extract raw fields, (2) validate and normalize outputs programmatically.

Example extraction prompt (simplified):

```
System: You are a resume parsing assistant. Given the raw resume text, return JSON with keys: contact, experience[], education[], skills[]. Each experience record must include {title, company, start_date, end_date, bullets[]}.

User: <raw_text_here>

Assistant: (must reply with valid JSON only)
```

Validation:

- Use Pydantic models to validate and coerce types.
- If dates are ambiguous, record the original string and a `confidence` score.

Versioning prompts:

- Keep prompt templates in `prompts/` with versioned filenames (e.g., `extraction_v1.md`, `extraction_v2.md`).

---

## 11. Development environment & quickstart (detailed)

The project contains both a frontend and backend. This section explains how to run both locally for development.

Prerequisites:

- Node.js >= 18
- Python 3.10+
- Postgres database (local or container)
- Optional: MinIO or S3 for storage emulation

Backend setup:

1. Create and activate a Python virtual environment.

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install backend dependencies.

```bash
pip install -r resume_engine/requirements.txt
```

3. Configure environment variables.

Create a `.env` file at `resume_engine/.env` with:

```
DATABASE_URL=postgres://user:pass@localhost:5432/resume_engine
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_KEY=local-key
STORAGE_SECRET=local-secret
LLM_API_KEY=your_key_here
JWT_SECRET=supersecret
```

4. Run migrations.

```bash
alembic upgrade head
```

5. Start the API.

```bash
uvicorn resume_engine.main:app --reload
```

Frontend setup:

1. Install packages.

```bash
npm install
```

2. Create `.env.local`.

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3. Start dev server.

```bash
npm run dev
```

Local end-to-end flow:

1. Start Postgres and optional MinIO.
2. Start backend and frontend.
3. Create a user account via UI or API, upload a resume.

---

## 12. Testing and CI

Testing strategy:

- Unit tests: focus on parsing heuristics, Pydantic schemas, scoring rules.
- Integration tests: simulate file uploads, check parser output and end-to-end flows using test DB.
- Contract tests: ensure API responses match OpenAPI schema.

Recommended frameworks:

- Python: pytest with factory-boys and pytest-asyncio for async endpoints.
- Frontend: vitest or jest + React Testing Library for component tests.

CI pipeline (example):

1. Lint and format (pre-commit hooks).
2. Run unit tests for backend.
3. Run frontend tests.
4. Build artifacts and optionally run integration smoke tests against a test deployment.

Example GitHub Actions snippet (conceptual):

```yaml
name: CI
on: [push, pull_request]
jobs:
   backend-tests:
      runs-on: ubuntu-latest
      steps:
         - uses: actions/checkout@v3
         - uses: actions/setup-python@v4
            with: {python-version: '3.10'}
         - run: pip install -r resume_engine/requirements.txt
         - run: pytest -q
```

---

## 13. Deployment and infrastructure guidance

This section outlines production deployment recommendations and architecture choices for scaling.

Suggested architecture for production:

- API service behind an API gateway (e.g., AWS ALB, Cloud Run proxy).
- Workers for parsing and optimization tasks (separate horizontally scalable worker pool).
- Managed Postgres (RDS, Cloud SQL) with read replicas for analytics.
- Object storage with lifecycle policies (S3 + lifecycle to move to Glacier if needed).
- Monitoring (Prometheus + Grafana) and centralized logging (ELK).

Scaling guidelines:

- Autoscale workers based on queue length and average job time.
- Cache frequent LLM prompt responses when deterministic.

Cost controls:

- Rate-limit LLM calls and provide user quotas.
- Batch small operations to reduce per-call overhead.

---

## 14. Security, privacy, and compliance considerations

Data handling best practices:

- Minimize retention of raw resume text; store redacted or hashed forms when possible.
- Encrypt sensitive fields at rest and in transit.
- Use role-based access control and least-privilege for services accessing storage.

LLM-specific guidance:

- Avoid sending sensitive PII to external LLMs unless permitted and necessary.
- Use prompt redaction to remove SSNs or other identifiers before sending.

Privacy & compliance:

- Implement data deletion endpoints to comply with user requests (e.g., GDPR Right to Erasure).
- Maintain an audit log for data access and deletions.

Security checklist:

- Rotate secrets regularly and store them in a secrets manager.
- Monitor for abnormal export/download activity.

---

## 15. Operational runbook

This runbook provides steps for common operational tasks.

15.1 Restarting workers

```bash
systemctl restart resume_engine-workers
```

15.2 Purging old resumes (example cron job)

Run a scheduled job that:

- Identifies `resumes` older than retention period (e.g., 90 days).
- Deletes associated storage objects.
- Marks resume record as `deleted` and optionally anonymizes structured JSON.

15.3 Scaling the optimizer

- Increase worker pool size and ensure LLM provider rate limits are respected.

---

## 16. Troubleshooting

Common issues and steps:

- PDF parsing yields empty text: check if file is image-only; enable OCR pipeline.
- LLM extraction incorrect format: validate prompt template and add stronger schema constraints.
- Slow processing: profile parsing and LLM latency; consider async batching.

Logging and observability:

- Ensure error logs include correlation ids and resume ids for tracing.

---

## 17. Extending the system

Examples of extensibility:

- Add a new exporter: implement `exporters/<format>.py` and register it in the exporter registry.
- Add a new scoring rule: extend `scoring/rules.py` and update weighting configuration.
- Replace LLM provider: implement a new adapter under `app/services/ai/providers` and update the configuration.

Code conventions:

- Follow black/ruff/isort formatting for Python and Prettier/ESLint for JS/TS.

---

## 18. Contributing guidelines

- Fork the repo and open a feature branch.
- Add tests for new logic and run linters locally.
- Open a PR describing the change, rationale, and migration steps if necessary.

For large changes involving prompts or scoring, open an issue first to discuss design and impacts on existing reports.

---

## 19. FAQs

Q: Can the system parse scanned PDFs?

A: Yes, but enable OCR in the parsing pipeline. OCR adds latency and potential errors; validate extracted text.

Q: How are LLM costs controlled?

A: Use caching, batch prompts, and user quotas. Offer an on-premise or lower-cost provider option for high-volume users.

Q: Can I run the system offline?

A: The frontend and core parsing tools can run offline, but LLM-based extraction requires connectivity unless an on-prem model is deployed.

---

## 20. Glossary

- ATS: Applicant Tracking System.
- LLM: Large Language Model.
- DTO: Data Transfer Object.
- OCR: Optical Character Recognition.

---

## 21. Changelog (high level)

- v0.1 — Initial proof-of-concept: parsing and scoring.
- v0.2 — LLM integration and tailored resume generation.

---

## 22. License

This repository is open-source. Include an appropriate license file (e.g., MIT) at the repo root if desired.

---

Appendix: Example prompt templates, JSON schemas, and sample request/response bodies are maintained in the `prompts/` and `app/schemas/` folders. Refer to those files for authoritative formats.

End of document.

  Opt[Optimization Service]
  Export[Exporters]
  DB[(Database)]
  Storage[(File Storage / S3)]

  U -->|upload resume| FE
  FE -->|POST /resumes| API
  API -->|save raw file| Storage
  API -->|create record| DB
  API -->|queue parse job| Parser
  Parser -->|extract text| Storage
  Parser -->|structured payload| API
  API -->|call prompts| AI
  AI -->|extracted entities| API
  API -->|compute score| Score
  Score -->|score result| API
  API -->|request tailoring| Opt
  Opt -->|tailored resume| API
  API -->|generate artifacts| Export
  Export -->|artifact files| Storage
  API -->|return results| FE
  FE -->|display downloads & report| U

  DB -->|store metadata & reports| API

  classDef service fill:#f9f,stroke:#333,stroke-width:1px;
  class Parser,AI,Score,Opt,Export service;
```

### DFD notes

- External entity: **User** interacts via the frontend.
- Data stores: **Storage** holds raw and generated files; **Database** stores metadata, reports, and user info.
- Key processes: parsing, AI extraction, scoring, optimization, and exporting.

## Components (short)

- `src/`: Frontend app and components (upload, preview, editor, history).
- `resume_engine/app/`: Backend API, models, schemas, services, DB session.
- `prompts/`: Prompt templates for all AI-driven operations.
- `prisma/` and `alembic/`: DB schema and migrations.
- `app/services/ai`: Integrations with LLM providers.

## Quickstart (development)

1. Backend (Python):

   - Create and activate a virtual environment.
   - Install dependencies: `pip install -r resume_engine/requirements.txt`.
   - Configure environment variables (DB URL, LLM API keys, storage credentials).
   - Run migrations (Alembic) and start the API (e.g., `uvicorn resume_engine.main:app --reload`).

2. Frontend (Next.js):

   - Install: `npm install` or `pnpm install`.
   - Configure environment variables in `.env.local`.
   - Start dev server: `npm run dev`.

3. Using the app:

   - Open the frontend in the browser, sign in, and upload a resume to see parsing, scoring, and export options.

## Development notes & extension points

- Swap LLM providers by updating the AI integration layer under `app/services/ai` and adjusting prompt templates in `prompts/`.
- Add more exporters by implementing new modules under `exporters/`.
- Add worker/queue (e.g., Celery, RQ) to handle long-running parse/optimize tasks.

## Security and privacy

- Avoid logging raw resume content in plaintext to production logs.
- Ensure file storage permissions are restrictive and temporary files are purged on schedule.
- Protect LLM API keys and other secrets via environment management.

## Contact / Contributing

Open issues and PRs in this repo. For major changes (new exporters, major prompt refactors), open an issue first to discuss design and compatibility.
