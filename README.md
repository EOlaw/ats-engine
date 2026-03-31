# ATS Engine

## Purpose

The ATS Engine repository contains a full-stack system for parsing, analyzing, optimizing, and exporting resumes with an emphasis on Applicant Tracking System (ATS) scoring and tailoring. It combines a Next.js frontend UI with a Python backend AI/resume processing engine to provide resume upload, analysis, improvement suggestions, scoring, and export features.

## High-level overview

- **Frontend (Next.js)**: Located under `src/` and `components/`. Handles user authentication, upload UI, preview, and result presentation.
- **Backend (resume_engine/app)**: FastAPI-style Python application that manages requests, coordinates parsing, scoring, and exports. Contains services, schemas, models, and DB session logic.
- **AI / Prompting**: The `prompts/` folder contains domain-specific prompts (extraction, optimization, scoring, tailoring, templates, and validation) which the system uses with an LLM service to extract resume structure, generate improvements, and compute ATS-related guidance.
- **Database & Migrations**: `prisma/` and `alembic/` indicate database schema management and migrations for persistent storage (users, resumes, job profiles, and reports).
- **Exporters & Parsers**: `app/services`, `parsers/`, and `exporters/` contain logic to transform parsed resume data into structured schema and downloadable formats (PDF, DOCX, JSON).

## How the system operates (textual flow)

1. A user uploads a resume via the frontend UI.
2. Frontend sends the file and metadata to the backend API (`/api/resume` endpoint).
3. Backend stores the raw file (temporary or object storage) and creates a resume record in the DB.
4. Parsing service extracts raw text and structure (sections, bullets, dates).
5. Extraction prompts + LLM produce structured fields (experience, education, skills, projects).
6. Scoring module computes an ATS score based on keyword matches, section presence, formatting, and recruiter heuristics.
7. Optimization module (prompts + rules) suggests improvements and generates tailored versions for a target job description.
8. Exporters generate final artifacts (PDF, DOCX, JSON) and the API returns download links and a score report to the frontend.

## Data Flow Diagram (DFD)

Below is a mermaid diagram showing the main entities, processes, and data stores.

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
