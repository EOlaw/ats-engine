# ATS Engine

> An enterprise-grade ATS resume intelligence platform for parsing resumes, extracting structured candidate data, scoring ATS readiness, tailoring content to job descriptions, and exporting recruiter-friendly resume artifacts.

<p align="center">
  <img alt="Next.js" src="https://img.shields.io/badge/frontend-Next.js%20%2B%20TypeScript-111827?style=for-the-badge" />
  <img alt="FastAPI" src="https://img.shields.io/badge/backend-FastAPI%20%2B%20Python-0F766E?style=for-the-badge" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/database-PostgreSQL-1D4ED8?style=for-the-badge" />
  <img alt="LLM" src="https://img.shields.io/badge/AI-LLM%20Extraction%20%26%20Optimization-7C3AED?style=for-the-badge" />
</p>

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Executive Summary](#2-executive-summary)
- [3. System Goals and Non-Goals](#3-system-goals-and-non-goals)
- [4. Product Capabilities](#4-product-capabilities)
- [5. High-Level Architecture](#5-high-level-architecture)
- [6. Detailed Component Reference](#6-detailed-component-reference)
  - [6.1 Frontend](#61-frontend-nextjs)
  - [6.2 Backend API](#62-backend-api-fastapi)
  - [6.3 Parsing Service](#63-parsing-service)
  - [6.4 AI / Prompt Engine](#64-ai--prompt-engine)
  - [6.5 Scoring Service](#65-scoring-service)
  - [6.6 Optimization / Tailoring Service](#66-optimization--tailoring-service)
  - [6.7 Exporters](#67-exporters)
  - [6.8 Storage & Database](#68-storage--database)
  - [6.9 Authentication & User Management](#69-authentication--user-management)
- [7. Data Flow Diagram (DFD)](#7-data-flow-diagram-dfd)
- [8. Sequence Flows and Examples](#8-sequence-flows-and-examples)
- [9. API Reference](#9-api-reference)
- [10. Database Schema Overview](#10-database-schema-overview)
- [11. Prompts and Prompt Engineering Guide](#11-prompts-and-prompt-engineering-guide)
- [12. Development Environment & Quickstart](#12-development-environment--quickstart)
- [13. Testing and CI](#13-testing-and-ci)
- [14. Deployment and Infrastructure Guidance](#14-deployment-and-infrastructure-guidance)
- [15. Security, Privacy, and Compliance](#15-security-privacy-and-compliance)
- [16. Operational Runbook](#16-operational-runbook)
- [17. Troubleshooting](#17-troubleshooting)
- [18. Extending the System](#18-extending-the-system)
- [19. Contributing Guidelines](#19-contributing-guidelines)
- [20. FAQs](#20-faqs)
- [21. Glossary](#21-glossary)
- [22. Changelog](#22-changelog)
- [23. License](#23-license)

---

## 1. Purpose

The **ATS Engine** is an integrated resume intelligence system designed to:

- ingest resumes in PDF, DOCX, and TXT formats
- extract and normalize candidate information into structured data
- evaluate resumes against ATS-friendly heuristics
- generate optimization suggestions and tailored resume variants
- export recruiter-ready artifacts in multiple formats

This project is built for:

- career platforms
- resume optimization tools
- recruiting software vendors
- internal HR tooling teams
- product teams building AI-assisted job application experiences

### In Scope

- resume upload and storage
- text extraction and parsing
- structured resume JSON generation
- ATS scoring and explainable feedback
- job-specific tailoring
- template-based resume export
- user dashboards and processing history

### Out of Scope

- a full applicant tracking system for hiring workflows
- interview scheduling and candidate pipeline management
- job board aggregation and recommendation engines
- offer letter, onboarding, or payroll workflows

---

## 2. Executive Summary

ATS Engine combines **document processing**, **AI-driven extraction**, and **resume optimization** into one auditable pipeline.

At a high level, the system works like this:

1. A user uploads a resume.
2. The system parses the file and extracts raw text and section candidates.
3. An AI layer converts that content into validated, structured resume data.
4. A scoring engine evaluates ATS readiness.
5. An optimization layer improves clarity, alignment, and recruiter readability.
6. An exporter generates polished, ATS-safe output formats.

The design intentionally separates the frontend, orchestration layer, parsing logic, AI services, scoring logic, and exporters so each part can scale independently and be replaced without rewriting the entire product.

---

## 3. System Goals and Non-Goals

### Goals

- **Accuracy:** Extract candidate data reliably from diverse resume formats.
- **Explainability:** Show users why a resume scored the way it did.
- **Extensibility:** Add new prompts, exporters, and scoring rules with minimal refactoring.
- **Security:** Protect user documents and sensitive personal information.
- **Performance:** Process standard resumes within a few seconds in common cases.
- **Auditability:** Maintain clear processing states, versioned outputs, and traceable transformations.

### Non-Goals

- collaborative document editing like Google Docs
- full recruitment lifecycle management
- automatic fabrication of missing candidate details
- replacing recruiter judgment with a black-box score

---

## 4. Product Capabilities

### Core Features

- Resume upload with validation
- PDF/DOCX/TXT parsing
- Structured extraction into machine-readable JSON
- ATS score breakdown and remediation feedback
- Job-description tailoring
- Template-based ATS-safe rendering
- Downloadable PDF, DOCX, and JSON outputs
- Resume version history and artifact tracking

### Enterprise Features

- role-based access control
- queue-based background processing
- provider-agnostic AI adapter layer
- storage abstraction for local and cloud object storage
- export versioning and audit logging
- observability hooks for logs, metrics, and tracing

---

## 5. High-Level Architecture

```text
User
  ↓
Frontend (Next.js)
  ↓
Backend API (FastAPI)
  ├── Parsing Service
  ├── AI / Prompt Engine
  ├── Scoring Service
  ├── Optimization Service
  ├── Exporters
  ├── Database
  └── File Storage
```

### Architectural Principles

- **Thin API, strong services:** API routes orchestrate; services do the heavy lifting.
- **Structured data first:** Resume content becomes normalized JSON before optimization or export.
- **Async where it matters:** Expensive jobs should run through worker queues.
- **Provider abstraction:** AI and storage layers should be replaceable.
- **Human review friendly:** Suggestions should be inspectable, editable, and explainable.

---

## 6. Detailed Component Reference

## 6.1 Frontend (Next.js)

**Location:** `src/`

### Responsibilities

- authentication and session flows
- resume upload experience
- job description input or selection
- parsing preview and field editor
- ATS score visualization
- resume diff viewer for tailored variants
- export downloads and artifact history

### Suggested Feature Areas

- `src/app/(dashboard)/resumes`
- `src/components/resume/upload-zone.tsx`
- `src/components/resume/ats-score-card.tsx`
- `src/components/resume/template-gallery.tsx`
- `src/components/resume/diff-viewer.tsx`
- `src/components/resume/export-actions.tsx`

### Frontend Notes

- Use drag-and-drop uploads with file type and size validation.
- Show processing states clearly: `uploaded`, `queued`, `parsing`, `extracting`, `scoring`, `ready`, `failed`.
- Prefer optimistic but honest UX: show progress, not fake completion.
- Keep template previews visually polished while the final export remains ATS-safe.

---

## 6.2 Backend API (FastAPI)

**Location:** `resume_engine/app/`

### Responsibilities

- receive uploads and validate metadata
- create processing jobs and persist state
- orchestrate parsing, AI extraction, scoring, tailoring, and export generation
- expose read/write endpoints for resumes, reports, and exports
- manage authentication and access control

### Suggested Modules

- `app/api/` — endpoints, exception handlers, dependencies
- `app/services/` — orchestration services
- `app/models/` — ORM models
- `app/schemas/` — Pydantic schemas
- `app/core/` — security, config, logging
- `app/db/` — sessions, migrations, repositories

### Backend Principles

- keep route handlers thin
- make ingestion idempotent when possible
- validate all AI outputs against schemas
- support retries for transient provider failures
- never expose raw storage keys directly to the client

---

## 6.3 Parsing Service

### Responsibilities

- convert PDF, DOCX, and TXT files into canonical plain text
- detect likely resume sections
- extract headings, bullet groups, and date ranges
- handle formatting ambiguity with heuristics and fallbacks

### Recommended Approach

- `pdfplumber` or equivalent for PDF extraction
- `python-docx` for DOCX parsing
- OCR fallback for scanned or image-based PDFs
- heuristics for:
  - section detection
  - heading normalization
  - date standardization
  - bullet segmentation

### Outputs

- canonical extracted text
- intermediate parse metadata
- candidate structured draft payload for downstream AI validation

---

## 6.4 AI / Prompt Engine

### Responsibilities

- transform raw resume text into structured JSON
- improve bullet points without inventing facts
- classify and validate unclear content
- tailor resume content to target jobs
- support multiple model providers through adapters

### Best Practices

- enforce strict output schemas
- separate extraction from optimization
- use confidence flags for ambiguous fields
- version prompt templates
- never let rewritten content overwrite source truth silently

### Prompt Pipeline

1. Extraction prompt
2. Validation prompt
3. ATS analysis prompt
4. Optimization prompt
5. Template rendering prompt

---

## 6.5 Scoring Service

### Responsibilities

- compute an ATS readiness score
- break down score categories
- produce explainable recommendations

### Example Scoring Categories

- contact completeness
- section coverage
- chronology consistency
- keyword alignment
- formatting safety
- bullet clarity and impact
- recruiter readability

### Output

```json
{
  "score": 82,
  "categories": {
    "contact": 10,
    "sections": 18,
    "keywords": 20,
    "formatting": 14,
    "clarity": 12,
    "impact": 8
  },
  "critical_fixes": ["Add a stronger summary", "Clarify one employment date range"],
  "notes": ["Resume is ATS-safe but could use more role-specific keywords"]
}
```

---

## 6.6 Optimization / Tailoring Service

### Responsibilities

- tailor the resume to a job description
- rewrite weak bullets using supported facts
- reorder content to improve relevance
- generate multiple candidate variants when needed

### Rules

- preserve truthfulness
- never fabricate skills, achievements, or credentials
- optimize for both ATS parsing and recruiter readability
- present suggestions in a reviewable form

### Typical Flow

- compare extracted resume data to target job text
- identify keyword gaps and relevance gaps
- produce a tailored summary and refined bullets
- re-score the tailored version

---

## 6.7 Exporters

### Responsibilities

- render structured data into ATS-safe templates
- support PDF, DOCX, and JSON output
- preserve consistent layout and metadata hygiene

### Suggested Export Types

- `pdf`
- `docx`
- `json`
- optional `html` preview for internal rendering

### ATS-Safe Rendering Rules

- single-column layout by default
- minimal decorative elements
- no icons or text boxes in submission exports
- consistent section headings
- stable spacing and readable typography

---

## 6.8 Storage & Database

### Storage

Use object storage for:

- raw uploads
- extracted text artifacts
- optimized variants
- exported files

Examples:

- local filesystem for development
- S3 / MinIO / compatible object storage in production

### Database

Recommended: **PostgreSQL**

Store:

- users
- resumes
- parsed JSON records
- ATS reports
- tailored variants
- export artifacts
- audit events

---

## 6.9 Authentication & User Management

### Responsibilities

- secure access to private resume data
- support user-level isolation
- enable organization and admin roles where needed

### Recommended Features

- JWT or session-based auth
- refresh tokens
- optional OAuth with Google/Microsoft
- role-based authorization
- secure account recovery flows

---

## 7. Data Flow Diagram (DFD)

```mermaid
flowchart LR
   U[User]
   FE[Frontend\nNext.js]
   API[Backend API\nFastAPI]
   Parser[Parsing Service]
   AI[AI / Prompt Engine]
   Score[Scoring Service]
   Opt[Optimization Service]
   Export[Exporters]
   DB[(Database)]
   Storage[(File Storage / S3)]

   U -->|Upload resume| FE
   FE -->|POST /api/resumes| API
   API -->|Store raw file| Storage
   API -->|Create record| DB
   API -->|Queue parse job| Parser
   Parser -->|Extract text| Storage
   Parser -->|Structured draft| API
   API -->|LLM extraction| AI
   AI -->|Validated entities| API
   API -->|Compute ATS score| Score
   Score -->|Score report| API
   API -->|Request tailoring| Opt
   Opt -->|Tailored variants| API
   API -->|Generate artifacts| Export
   Export -->|PDF / DOCX / JSON| Storage
   API -->|Return results| FE
   FE -->|Display insights| U
```

### DFD Notes

- The backend is the orchestrator.
- The AI layer refines but does not become the source of truth without schema validation.
- Long-running operations should be delegated to workers.
- Storage and database access should remain private to trusted services.

---

## 8. Sequence Flows and Examples

### 8.1 Upload and Score a Resume

1. User uploads a file from the frontend.
2. Backend stores the file and creates a processing record.
3. Parser extracts text and section candidates.
4. AI converts the parsed content to structured JSON.
5. Scoring service computes ATS score and explanations.
6. Frontend fetches and displays the report.

### 8.2 Tailor a Resume for a Job

1. User pastes or selects a job description.
2. Backend starts a tailoring job.
3. Optimization layer aligns content to target role requirements.
4. Tailored version is re-scored.
5. Frontend displays differences and exports.

### 8.3 Regenerate an Export

1. User selects a template.
2. Exporter renders the latest approved structured content.
3. Artifact is stored and linked back to the resume record.

---

## 9. API Reference

### `POST /api/resumes`
Upload a new resume.

**Request:** `multipart/form-data`

- `file`: resume file
- `metadata`: optional JSON metadata

**Response:** `202 Accepted`

```json
{
  "resume_id": "resume_456",
  "status": "queued"
}
```

### `GET /api/resumes/{id}`
Retrieve resume metadata, processing status, structured data, and ATS results.

### `POST /api/resumes/{id}/tailor`
Create a tailored resume variant for a target role.

**Request Example**

```json
{
  "job_text": "We are hiring a Data Analyst with SQL, Python, Tableau, and stakeholder communication skills..."
}
```

### `GET /api/resumes/{id}/exports`
List generated artifacts and download URLs.

### Common Error Codes

- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `429 Too Many Requests`

---

## 10. Database Schema Overview

### Core Tables

#### `users`
- `id`
- `email`
- `hashed_password`
- `created_at`
- `last_login_at`

#### `resumes`
- `id`
- `user_id`
- `original_filename`
- `storage_key`
- `status`
- `created_at`

#### `structured_resumes`
- `id`
- `resume_id`
- `json_payload`
- `parsed_at`

#### `reports`
- `id`
- `resume_id`
- `score`
- `breakdown_json`
- `created_at`

#### `exports`
- `id`
- `resume_id`
- `format`
- `storage_key`
- `created_at`

#### `tailored_variants`
- `id`
- `resume_id`
- `job_target_id`
- `variant_json`
- `score`
- `created_at`

---

## 11. Prompts and Prompt Engineering Guide

### Principles

- Use strict JSON schemas.
- Separate extraction from rewriting.
- Validate all outputs programmatically.
- Flag uncertainty instead of guessing.
- Version prompt files for safe iteration.

### Example Prompt Strategy

**System prompt:**

```text
You are an enterprise-grade ATS resume intelligence engine.
You must extract resume facts accurately, avoid hallucination, and return valid JSON when requested.
```

**Extraction prompt:**

```text
Extract the resume into structured JSON with fields for contact, summary, skills, work_experience, education, certifications, and projects. Return JSON only.
```

**Optimization prompt:**

```text
Rewrite the professional summary and work bullets to be stronger, ATS-friendly, and recruiter-readable without inventing facts.
```

---

## 12. Development Environment & Quickstart

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL
- Redis (recommended for queues)
- optional MinIO / S3-compatible storage

### Backend Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r resume_engine/requirements.txt
cp resume_engine/.env.example resume_engine/.env
alembic upgrade head
uvicorn resume_engine.main:app --reload
```

### Frontend Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

### Suggested Environment Variables

```env
DATABASE_URL=postgres://user:pass@localhost:5432/ats_engine
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=change-me
LLM_API_KEY=your-provider-key
STORAGE_ENDPOINT=http://localhost:9000
STORAGE_BUCKET=ats-engine
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 13. Testing and CI

### Testing Strategy

- unit tests for parsing, scoring, and schema validation
- integration tests for upload-to-report workflows
- frontend component tests for major user flows
- contract tests to verify API response shape

### Recommended Tooling

- **Backend:** `pytest`, `pytest-asyncio`
- **Frontend:** `vitest`, `@testing-library/react`
- **Linting:** `ruff`, `black`, `eslint`, `prettier`

### CI Pipeline

1. install dependencies
2. lint backend and frontend
3. run tests
4. build frontend
5. optionally run smoke tests against a preview environment

---

## 14. Deployment and Infrastructure Guidance

### Production Recommendations

- containerize frontend and backend separately
- run worker processes independently from API pods
- use managed PostgreSQL and object storage
- use an API gateway / load balancer
- centralize metrics, logs, and tracing

### Scaling Tips

- autoscale workers by queue depth
- cache repeatable operations when safe
- isolate OCR-heavy workloads
- use provider timeouts and retry policies for LLM calls

---

## 15. Security, Privacy, and Compliance

### Security Practices

- encrypt data in transit and at rest
- apply least-privilege access to storage and database systems
- redact highly sensitive data before external AI calls where possible
- use short-lived download URLs
- rotate secrets regularly

### Privacy Practices

- define retention windows for uploads and generated artifacts
- support deletion workflows for users
- maintain audit logs for administrative access
- avoid logging full resume text in production logs

### Compliance Considerations

- GDPR-style deletion support
- data export capability
- access traceability
- configurable retention and purge jobs

---

## 16. Operational Runbook

### Restart Workers

```bash
systemctl restart ats-engine-workers
```

### Purge Stale Files

- identify expired resume records
- remove linked storage artifacts
- anonymize or delete structured data where required
- write audit events for purge actions

### Increase Throughput

- raise worker count
- validate provider rate limits
- split OCR and LLM workloads into separate queues

---

## 17. Troubleshooting

### Problem: PDF extracts empty text
Possible causes:
- scanned image-only PDF
- parser limitations
- corrupted file

**Fix:** route through OCR fallback and validate page text output.

### Problem: AI output fails schema validation
Possible causes:
- prompt drift
- oversized context
- malformed provider response

**Fix:** tighten output instructions, chunk input, and retry with a validation-focused prompt.

### Problem: Slow end-to-end processing
Possible causes:
- OCR-heavy documents
- large model latency
- synchronous export generation

**Fix:** move expensive steps to background jobs and measure per-stage latency.

---

## 18. Extending the System

### Add a New Exporter

1. create a module under `app/services/exporters/`
2. implement a renderer interface
3. register it in the exporter registry
4. add tests for output shape and artifact creation

### Add a New Scoring Rule

1. extend scoring rules module
2. assign a category weight
3. update explanation strings
4. add regression tests

### Add a New AI Provider

1. implement a provider adapter
2. map provider responses to internal schema
3. add configuration toggles
4. validate fallback behavior

---

## 19. Contributing Guidelines

1. fork the repository
2. create a feature branch
3. add or update tests
4. run linters locally
5. submit a pull request with context and screenshots when relevant

### Coding Standards

- keep APIs thin and explicit
- separate source truth from generated suggestions
- write tests for new business logic
- avoid hidden side effects in service layers

---

## 20. FAQs

### Can the system parse scanned PDFs?
Yes, with OCR enabled, though OCR adds latency and may reduce extraction accuracy.

### Can I switch LLM providers later?
Yes. The architecture should keep provider integrations behind an adapter layer.

### Is this a full ATS product?
No. This project focuses on resume intelligence, scoring, tailoring, and exporting.

### Can it run without external AI providers?
Yes for basic parsing and rules-based scoring; advanced extraction and optimization may require an external or self-hosted model.

---

## 21. Glossary

- **ATS:** Applicant Tracking System
- **LLM:** Large Language Model
- **OCR:** Optical Character Recognition
- **DTO:** Data Transfer Object
- **Artifact:** Generated output such as a PDF, DOCX, or JSON file
- **Tailored Variant:** A resume version optimized for a specific role or job description

---

## 22. Changelog

### v0.1.0
- initial proof of concept for parsing and scoring

### v0.2.0
- added AI extraction and tailored resume generation

### v0.3.0
- added structured README, linked table of contents, and expanded architecture guidance

---

## 23. License

Choose the license that matches your distribution model.

Common options:
- MIT
- Apache-2.0
- Proprietary / commercial

If open source, place the license text in a top-level `LICENSE` file.

---

## Suggested Repository Structure

```text
.
├── src/                         # Next.js frontend
├── resume_engine/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── prompts/
│   ├── tests/
│   └── main.py
├── prisma/                      # Optional schema definitions
├── alembic/                     # DB migrations
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## Final Notes

This README is intentionally written as both a **product overview** and a **developer handoff document**. It should help engineers, founders, product stakeholders, and future contributors understand how the ATS Engine is meant to work, where major logic belongs, and how to extend it safely.
