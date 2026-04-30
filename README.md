# 🚀 ATS Engine — Resume Intelligence Platform

> An enterprise-grade platform that parses resumes, scores ATS readiness, tailors content to job descriptions, and exports recruiter-ready artifacts — all powered by LLM extraction and a clean full-stack architecture.

<p align="center">
  <img alt="Next.js" src="https://img.shields.io/badge/frontend-Next.js%20%2B%20TypeScript-111827?style=for-the-badge" />
  <img alt="FastAPI" src="https://img.shields.io/badge/backend-FastAPI%20%2B%20Python-0F766E?style=for-the-badge" />
  <img alt="PostgreSQL" src="https://img.shields.io/badge/database-PostgreSQL-1D4ED8?style=for-the-badge" />
  <img alt="LLM" src="https://img.shields.io/badge/AI-LLM%20Extraction%20%26%20Optimization-7C3AED?style=for-the-badge" />
</p>

---

## 🔍 Problem

Job seekers apply to hundreds of roles without knowing whether their resume will survive an ATS filter. Most resumes fail — not because the candidate is unqualified, but because the document is structured in a way that ATS systems can't parse, rank, or match to a job posting.

**Who is affected:**
- Candidates who get rejected before a recruiter ever reads their resume
- Recruiters who receive poorly structured submissions that don't extract cleanly into their systems
- Career platforms that want to offer intelligent resume feedback but lack the backend to power it

**Why it matters:**
- ATS filters eliminate up to 75% of applicants before human review — often incorrectly
- Candidates have no visibility into why they're being screened out
- Manually tailoring a resume for each application is time-consuming and inconsistent

---

## 💡 Solution

Built a **full-stack ATS intelligence platform** that takes a raw resume and produces a structured candidate profile, an explainable ATS score, a tailored variant aligned to a specific job, and a polished exportable artifact.

- **Document parser** (`parsers/`) extracts clean text from PDF and DOCX files using `pdfplumber` and `python-docx`, with section detection and heading normalization
- **AI extraction pipeline** (`services/ai/`) uses Claude to convert raw text into a validated, structured JSON resume through a multi-stage prompt chain — extraction → validation → optimization
- **Scoring engine** (`services/ai/scoring_service.py`) produces a 0–100 ATS readiness score with per-category breakdowns and actionable remediation feedback
- **Tailoring service** (`services/ai/tailoring_service.py`) aligns resume content to a target job description, identifies keyword gaps, and rewrites weak bullets without fabricating facts
- **Export layer** (`services/exporters/`) renders structured content into ATS-safe PDF and DOCX artifacts using a template registry
- **Next.js frontend** (`src/`) surfaces the full pipeline through a polished dashboard with drag-and-drop upload, score visualization, and diff-based tailoring review

---

## 🧠 Tech Stack

| Category | Tools |
|---|---|
| **Frontend** | Next.js 14, TypeScript, TailwindCSS, React Query, Recharts |
| **Forms & Validation** | React Hook Form, Zod, react-dropzone |
| **Backend** | FastAPI 0.115, Python 3.10+, Uvicorn |
| **ORM & Migrations** | SQLAlchemy 2.0 (async), Alembic |
| **Database** | PostgreSQL (asyncpg driver) |
| **AI / LLM** | Anthropic Claude (via `anthropic` SDK) |
| **Document Parsing** | pdfplumber, python-docx |
| **Export Generation** | WeasyPrint (PDF), python-docx (DOCX) |
| **Authentication** | JWT (python-jose + passlib/bcrypt) |
| **Resilience** | tenacity (retry), structlog (structured logging) |
| **File Handling** | aiofiles, python-multipart |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Browser (Next.js 14)                      │
│  Upload zone  ·  ATS score card  ·  Analysis panel          │
│  Tailor modal  ·  Export modal  ·  Resume history            │
└──────────────────────────┬──────────────────────────────────┘
                           │  HTTP / JSON  (REST API)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│               FastAPI Backend  (resume_engine/)              │
│  /upload  ·  /resumes  ·  /analysis  ·  /export  ·  /auth   │
└──────────────────────────┬──────────────────────────────────┘
                           │  async service calls
          ┌────────────────┼──────────────────────┐
          ▼                ▼                      ▼
┌──────────────┐  ┌────────────────────┐  ┌──────────────────┐
│   Parsers    │  │    AI Services     │  │    Exporters     │
│  pdf_parser  │  │  extraction        │  │  pdf_exporter    │
│  docx_parser │  │  validation        │  │  docx_exporter   │
│  doc_factory │  │  scoring           │  │  export_factory  │
└──────┬───────┘  │  optimization      │  └──────────────────┘
       │          │  tailoring         │
       │          └────────┬───────────┘
       │                   │  Anthropic API
       │                   ▼
       │          ┌──────────────────┐
       │          │  Prompt Chain    │
       │          │  extraction →    │
       │          │  validation →    │
       │          │  scoring →       │
       │          │  optimization →  │
       │          │  tailoring       │
       │          └──────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  PostgreSQL  ·  Local filesystem  ·  (S3-compatible in prod) │
└─────────────────────────────────────────────────────────────┘
```

**Data flow:**
- Raw uploads → parsed text → structured JSON resume (stored in `structured_resumes`)
- ATS report → score breakdown + remediation items (stored in `reports`)
- Tailored variants → re-scored and linked to originating resume
- Export artifacts → stored and returned as download URLs

---

## ⚙️ How It Works

1. **Upload** — user drags a PDF or DOCX onto the upload zone; the frontend posts the file to `POST /api/v1/upload`, which validates the MIME type, stores the raw file, and creates a resume record with status `queued`
2. **Parsing** — `document_factory.py` routes to the correct parser; `pdf_parser.py` uses `pdfplumber` to extract text, detect section boundaries, and normalize headings; `docx_parser.py` handles DOCX using `python-docx`
3. **AI Extraction** — `extraction_service.py` sends parsed text through a structured Claude prompt; the response is validated against a Pydantic schema by `validation_service.py`; fields that fail validation are flagged with a confidence marker rather than silently accepted
4. **Scoring** — `scoring_service.py` evaluates the structured resume across categories: contact completeness, section coverage, keyword density, chronology consistency, formatting safety, bullet impact, and recruiter readability; produces a 0–100 score with per-category breakdowns and critical fixes
5. **Score display** — `ats-score-card.tsx` and `analysis-panel.tsx` surface the score ring, category bars, and remediation checklist to the user in real time via `status-poller.tsx`
6. **Tailoring** — user pastes a job description into `tailor-modal.tsx`; `tailoring_service.py` identifies keyword and relevance gaps, rewrites the summary and bullets using `optimization_service.py`, and re-scores the tailored variant
7. **Export** — `export_factory.py` routes to `pdf_exporter.py` (WeasyPrint + template engine) or `docx_exporter.py`; the artifact is stored and returned as a download link from `GET /api/v1/export/{id}/download`

---

## 🧠 Key Techniques

- **Multi-stage prompt chain** — extraction, validation, scoring, optimization, and tailoring are separate prompts in sequence, each with strict JSON output schemas and retry logic via `tenacity`
- **Schema-validated AI output** — every Claude response is parsed through Pydantic models; anything that fails validation is flagged rather than passed downstream, preventing silent hallucination propagation
- **Async FastAPI** — all database and file I/O uses SQLAlchemy async + asyncpg; long-running AI calls are non-blocking
- **Provider-abstracted AI layer** — `services/ai/base.py` defines a clean adapter interface so the underlying LLM provider can be swapped without touching business logic
- **Template-driven export** — `template_registry.py` manages named resume templates; `template_engine.py` renders structured JSON into ATS-safe HTML before PDF generation, keeping layout and data fully separated
- **Real-time status polling** — `status-poller.tsx` drives the frontend state machine (`uploaded → parsing → extracting → scoring → ready`) without websockets
- **Structured logging** — `structlog` emits machine-readable log events at every stage of the pipeline, enabling per-request traceability in production

---

## 📊 Results / Impact

- Processes a resume from upload to scored, structured JSON in **under 10 seconds** for standard PDF and DOCX files
- Scores resumes across **7 ATS readiness categories** with line-item remediation feedback, not just a single opaque number
- Supports **PDF and DOCX export** from the same structured data source, with template swapping at render time
- Full pipeline is **async end-to-end** — the API never blocks on file I/O, database writes, or LLM calls
- Tailored variants are **re-scored automatically** so users can compare original vs. tailored ATS readiness side by side

---

## 💡 Business Impact

- **Removes the black box** — candidates see exactly why their resume scored the way it did and what to fix, turning rejection into actionable improvement
- **Accelerates recruiter workflows** — clean structured output means ATS systems ingest candidate data correctly the first time, reducing manual re-entry
- **Differentiates career platforms** — teams can embed this pipeline to offer intelligent resume analysis without building the AI infrastructure themselves
- **Scales to volume** — async architecture and stateless AI adapters mean processing throughput grows by adding workers, not by redesigning the system
- **Audit-ready by design** — every processing state, structured extract, score report, and export artifact is versioned and linked back to the originating resume record

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.10+
- PostgreSQL
- An Anthropic API key

### Backend

```bash
cd resume_engine
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # fill in DATABASE_URL, ANTHROPIC_API_KEY, JWT_SECRET
alembic upgrade head
uvicorn main:app --reload
```

### Frontend

```bash
# from repo root
npm install
cp .env.local.example .env.local  # set NEXT_PUBLIC_API_BASE_URL
npm run dev
```

### Run both together

```bash
npm run dev:all
```

### Environment Variables

```env
# Backend  (resume_engine/.env)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ats_engine
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=change-me
STORAGE_DIR=./uploads

# Frontend  (.env.local)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 📁 Project Structure

```
ats-engine/
├── src/                                  # Next.js 14 frontend
│   ├── app/
│   │   ├── (auth)/                       # login, register, forgot-password
│   │   ├── dashboard/                    # resume list and stats
│   │   └── resume/                       # upload, editor, preview, history
│   ├── components/
│   │   ├── resume/                       # upload-zone, ats-score-card, analysis-panel
│   │   │                                 # tailor-modal, export-modal, status-poller
│   │   └── ui/                           # button, card, modal, progress, score-ring
│   └── lib/
│       ├── api/                          # typed API clients (resume, export, auth)
│       └── hooks/                        # use-resume, use-export, use-auth
│
├── resume_engine/                        # FastAPI backend
│   ├── app/
│   │   ├── api/v1/endpoints/             # upload, resume, analysis, export, auth
│   │   ├── services/
│   │   │   ├── ai/                       # extraction, validation, scoring,
│   │   │   │                             # optimization, tailoring
│   │   │   ├── parsers/                  # pdf_parser, docx_parser, document_factory
│   │   │   ├── exporters/                # pdf_exporter, docx_exporter, export_factory
│   │   │   └── templates/               # template_engine, template_registry
│   │   ├── models/                       # SQLAlchemy ORM (user, resume, export)
│   │   ├── schemas/                      # Pydantic schemas (resume, user, export, job)
│   │   └── core/                         # config, security, logging, exceptions
│   ├── prompts/                          # versioned prompt modules
│   │   ├── extraction/
│   │   ├── validation/
│   │   ├── scoring/
│   │   ├── optimization/
│   │   ├── tailoring/
│   │   └── template/
│   ├── alembic/                          # database migrations
│   ├── main.py
│   └── requirements.txt
│
├── package.json
└── README.md
```

---

## 🌐 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/auth/register` | POST | Create a new user account |
| `/api/v1/auth/login` | POST | Authenticate and receive JWT |
| `/api/v1/upload` | POST | Upload a PDF or DOCX resume |
| `/api/v1/resumes` | GET | List all resumes for the authenticated user |
| `/api/v1/resumes/{id}` | GET | Get resume metadata, status, and structured data |
| `/api/v1/analysis/{id}/extract` | POST | Run AI extraction on a parsed resume |
| `/api/v1/analysis/{id}/score` | POST | Compute ATS score and generate report |
| `/api/v1/analysis/{id}/tailor` | POST | Tailor resume to a target job description |
| `/api/v1/export/{id}` | POST | Generate a PDF or DOCX export artifact |
| `/api/v1/export/{id}/download` | GET | Download a generated export artifact |

---

## 🔧 Configuration

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/ats_engine

# Anthropic Claude — used for extraction, scoring, optimization, tailoring
ANTHROPIC_API_KEY=sk-ant-...

# JWT auth
JWT_SECRET=change-me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# File storage (local path or S3-compatible endpoint)
STORAGE_DIR=./uploads

# Frontend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## 📌 Key Takeaways

- Demonstrates full-stack product engineering — async Python API, React frontend, PostgreSQL schema, and a multi-stage LLM pipeline working end-to-end
- Built a **schema-validated AI pipeline** where every LLM output is checked programmatically before it influences downstream state — hallucination is surfaced, not silently accepted
- Applied **real-world engineering practices**: provider abstraction, structured logging, retry policies, template-based export, and JWT auth
- Clean separation of concerns across parsers, AI services, exporters, and API orchestration makes each layer independently testable and replaceable

---

## 📝 License

MIT
