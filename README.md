---
title: Job Scrapper API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

<div align="center">

# 🔍 Job Scrapper

**AI-Powered Resume-Matched Job Aggregator**

Scrapes job postings from major tech companies and ranks them by relevance to your resume using **LLM-driven skill extraction** and a **deterministic scoring formula**.

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 🚀 Live Demo

Experience my Job Scrapper instantly via live deployed frontend:
- **Job Scrapper**: [Job Scrapper Live App](https://job-scrapper-eight.vercel.app/)

---


## 📑 Table of Contents

- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Matching Algorithm](#-matching-algorithm)
- [Run Locally](#-run-locally)
- [Environment Variables](#-environment-variables)
- [Deploy — Vercel (Frontend)](#-deploy--vercel-frontend)
- [Deploy — Hugging Face Spaces (Backend)](#-deploy--hugging-face-spaces-backend)
- [Cloud Services Setup](#-cloud-services-setup)
  - [Supabase (PostgreSQL)](#supabase-postgresql)
  - [Upstash (Redis)](#upstash-redis)
- [API Reference](#-api-reference)
- [Adding a New Company Scraper](#-adding-a-new-company-scraper)
- [Scheduled Refresh](#-scheduled-refresh)

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19 + Vite 8 | Single-page application |
| **Backend API** | FastAPI | REST endpoints, CORS, file uploads |
| **Database** | PostgreSQL (via Supabase) | Jobs, resumes, match results |
| **Cache / Broker** | Redis (via Upstash) | Embedding cache, Celery broker |
| **Task Queue** | Celery | Async scraping & matching tasks |
| **LLM Matching** | NVIDIA API (Llama 3.3 70B) | Skill extraction & scoring |
| **Metadata Extraction** | LLM-based | Location, education, experience from JDs |
| **Scraping** | Requests + Microsoft Careers API | Job data fetching |
| **PDF Parsing** | pdfplumber + pytesseract | Resume text extraction |
| **Scheduling** | APScheduler | Automated periodic job refresh |
| **Container** | Docker | Deployment on HF Spaces |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vercel)                           │
│                                                                     │
│   React + Vite (:5173)                                              │
│   ┌──────────┐ ┌────────────────┐ ┌───────────┐ ┌──────────────┐   │
│   │ Resume   │ │ Company        │ │ Filter    │ │ Match Results│   │
│   │ Upload   │ │ Selector       │ │ Sidebar   │ │ / Job List   │   │
│   └────┬─────┘ └───────┬────────┘ └─────┬─────┘ └──────────────┘   │
│        │               │                │                           │
│        └───────────────┼────────────────┘                           │
│                        │  Axios (VITE_API_URL)                      │
└────────────────────────┼────────────────────────────────────────────┘
                         │  HTTPS
┌────────────────────────┼────────────────────────────────────────────┐
│                   BACKEND (HF Spaces / Docker)                      │
│                        ▼                                            │
│              FastAPI (:7860)                                        │
│              ┌─────────────────┐                                    │
│              │  REST Endpoints │                                    │
│              └───┬────────┬────┘                                    │
│                  │        │                                         │
│        ┌─────────▼──┐  ┌──▼───────────┐                            │
│        │  Scraper    │  │  Matcher     │                            │
│        │  Workers    │  │  (LLM-based) │                            │
│        │             │  │              │                            │
│        │ Microsoft   │  │ NVIDIA API   │───── Llama 3.3 70B        │
│        │ (+ more)    │  │ (35 RPM)     │                            │
│        └──────┬──────┘  └──────┬───────┘                            │
│               │                │                                    │
│        ┌──────▼────────────────▼───────┐                            │
│        │        Celery Task Queue      │                            │
│        └──────┬────────────────┬───────┘                            │
│               │                │                                    │
└───────────────┼────────────────┼────────────────────────────────────┘
                │                │
    ┌───────────▼──┐      ┌──────▼──────────┐
    │  PostgreSQL  │      │     Redis       │
    │  (Supabase)  │      │   (Upstash)     │
    │              │      │                 │
    │ • jobs       │      │ • embedding     │
    │ • resumes    │      │   cache (24h)   │
    │ • matches    │      │ • Celery broker │
    └──────────────┘      └─────────────────┘
```

### Data Flow

```
1. User uploads resume (PDF)
       │
       ▼
2. pdfplumber extracts text → stored in PostgreSQL
       │
       ▼
3. User selects companies → triggers scrape
       │
       ▼
4. Scraper fetches jobs via company API
       │
       ▼
5. LLM extracts metadata (location, education, experience) per job
       │
       ▼
6. Jobs saved to PostgreSQL (deduped by company + external_job_id)
       │
       ▼
7. LLM compares resume vs each job → skills_score + experience_score
       │
       ▼
8. Results saved & returned sorted by overall_score
       │
       ▼
9. Frontend displays results with filter sidebar
```

---

## 📂 Project Structure

```
Job-Scrapper/
├── api.py                      # FastAPI app — all REST endpoints
├── matcher.py                  # LLM-driven matching (skill extraction + scoring)
├── utils.py                    # PDF & image text extraction helpers
├── config.py                   # Centralised configuration (env vars + defaults)
├── celery_app.py               # Celery broker/backend setup
├── Dockerfile                  # Production container (Python 3.13-slim)
├── docker-compose.yml          # Local Postgres + Redis containers
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not committed)
│
├── db/
│   ├── models.py               # SQLModel: Job, Resume, MatchResult
│   └── sessions.py             # Engine + context-managed sessions
│
├── scrapers/
│   ├── base.py                 # Abstract BaseScraper class
│   └── microsoft.py            # Microsoft Careers API scraper
│
├── services/
│   ├── cache.py                # Redis embedding cache (get/set with TTL)
│   ├── extractor.py            # LLM-based job metadata extraction
│   ├── llm.py                  # NVIDIA LLM client (rate-limited, JSON parsing)
│   ├── scheduler.py            # APScheduler — periodic job refresh
│   └── tasks.py                # Celery tasks: scrape, match, refresh
│
└── frontend/                   # React SPA (Vite)
    ├── src/
    │   ├── api.js              # Axios client with all API calls
    │   ├── App.jsx             # Root component — state management & layout
    │   ├── App.css             # Global styles
    │   ├── index.css           # Base reset & typography
    │   └── components/
    │       ├── ResumeUpload.jsx      # PDF drag-and-drop upload
    │       ├── CompanySelector.jsx    # Company toggle cards
    │       ├── FilterSidebar.jsx      # Location / education / experience filters
    │       ├── ScrapeButton.jsx       # Trigger scraping
    │       ├── JobList.jsx            # Unmatched job listings
    │       └── MatchResults.jsx       # Scored & ranked match cards
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ How It Works

1. **Upload** your resume (PDF) — text is extracted via `pdfplumber` and stored with a SHA-256 hash to avoid re-uploads.
2. **Select companies** — toggle which companies to scrape (currently Microsoft, with IBM/Oracle/Adobe coming soon).
3. **Refresh** — the scraper fetches new job postings from the company's API, deduplicates against existing jobs, and saves them to PostgreSQL. The LLM then extracts structured metadata (location, education levels, experience range) from each new job description.
4. **Match** — each job is scored against your resume via the NVIDIA LLM. The LLM extracts skills from both the resume and job description, computes overlap, and evaluates experience alignment using a fixed formula.
5. **Filter & View** — results are displayed sorted by overall relevance score. Use the sidebar filters to narrow by location, education level, and experience range.

Without a resume, all jobs are displayed sorted by date.

---

## 🧠 Matching Algorithm

The matching is powered by **Llama 3.3 70B** via the NVIDIA API. Unlike traditional keyword/embedding approaches, the LLM performs **semantic skill extraction** from both the resume and job description.

### Scoring Formula

```
skills_score     = (matched_skills / required_skills) × 100
experience_score = min(resume_years / required_years, 1.0) × 100
overall_score    = 0.6 × skills_score + 0.4 × experience_score
```

### What the LLM Returns

| Field | Description |
|---|---|
| `matched_skills` | Skills found in both resume and JD (semantic match: "React.js" ≈ "React") |
| `missing_skills` | JD skills not found in the resume |
| `skills_score` | Percentage of required skills covered |
| `experience_score` | Experience alignment (capped at 100%) |
| `overall_score` | Weighted composite score |
| `reasoning` | 2–3 sentence natural language explanation |

### Rate Limiting

The LLM client enforces a **1.75s minimum gap** between requests (≈ 35 RPM) to stay within NVIDIA API limits.

---

## 🚀 Run Locally

### Prerequisites

- **Python 3.13+**
- **Node.js 18+**
- **Docker** (for Postgres & Redis) OR native Postgres + Redis installations
- **NVIDIA API key** (free at [build.nvidia.com](https://build.nvidia.com/))

### Step 1 — Start Infrastructure

**Option A — Docker (recommended):**

```bash
docker-compose up -d
```

This starts PostgreSQL (`localhost:5432`) and Redis (`localhost:6379`).

**Option B — Native installations:**

- Install [PostgreSQL](https://www.postgresql.org/download/) and create a database named `jobscrapper`
- Install [Redis](https://redis.io/download/) (on Windows, use [Memurai](https://www.memurai.com/) or WSL)

### Step 2 — Backend Setup

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3 — Frontend Setup

```bash
cd frontend
npm install
```

### Step 4 — Configure Environment

Create a `.env` file in the project root:

```env
# ── Database ──────────────────────────────────────────
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobscrapper

# ── Redis ─────────────────────────────────────────────
REDIS_URL=redis://localhost:6379/0

# ── NVIDIA LLM ────────────────────────────────────────
LLM_API_KEY=nvapi-your-key-here
LLM_MODEL=meta/llama-3.3-70b-instruct
LLM_ENDPOINT=https://integrate.api.nvidia.com/v1/chat/completions

# ── Scheduler (optional) ──────────────────────────────
SCHEDULE_REFRESH_ENABLED=false
SCHEDULE_REFRESH_HOURS_UTC=2,14
SCHEDULE_REFRESH_COMPANIES=Microsoft
```

### Step 5 — Run

Open **3 terminals**:

```bash
# Terminal 1 — Celery worker
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 2 — FastAPI backend
uvicorn api:app --reload --port 8000

# Terminal 3 — React frontend
cd frontend && npm run dev
```

Open **http://localhost:5173** in your browser.

> **Note:** The frontend connects to `http://localhost:8000` by default. To change this, set `VITE_API_URL` in the frontend environment or in `frontend/.env`.

---

## 🔐 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | `postgresql://postgres:postgres@localhost:5432/jobscrapper` | PostgreSQL connection string |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` | Redis connection string (use `rediss://` for TLS) |
| `LLM_API_KEY` | ✅ | — | NVIDIA API key for LLM matching |
| `LLM_MODEL` | ❌ | `nvidia/llama-3.1-nemotron-70b-instruct` | LLM model identifier |
| `LLM_ENDPOINT` | ❌ | `https://integrate.api.nvidia.com/v1/chat/completions` | LLM API endpoint |
| `CORS_ORIGIN` | ❌ | `http://localhost:5173` | Allowed CORS origin for frontend |
| `SCHEDULE_REFRESH_ENABLED` | ❌ | `true` | Enable/disable automatic job refresh |
| `SCHEDULE_REFRESH_HOURS_UTC` | ❌ | `2,14` | Comma-separated UTC hours for auto-refresh |
| `SCHEDULE_REFRESH_COMPANIES` | ❌ | `Microsoft` | Companies to auto-refresh |
| `VITE_API_URL` | ❌ | `http://localhost:8000` | Backend URL (set in frontend `.env`) |

---

## ▲ Deploy — Vercel (Frontend)

The React frontend can be deployed to Vercel for free.

### Step 1 — Push to GitHub

Ensure your repository is pushed to GitHub.

### Step 2 — Import to Vercel

1. Go to [vercel.com](https://vercel.com/) and sign in with GitHub
2. Click **"Add New" → "Project"**
3. Import your GitHub repository

### Step 3 — Configure Build Settings

| Setting | Value |
|---|---|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### Step 4 — Set Environment Variables

Add the following in the Vercel project settings → **Environment Variables**:

```
VITE_API_URL = https://your-hf-space-url.hf.space
```

> Replace with your actual Hugging Face Spaces backend URL (see next section).

### Step 5 — Deploy

Click **Deploy**. Vercel will build and serve the frontend. On every push to `main`, it redeploys automatically.

### Update CORS on Backend

After deployment, update the `CORS_ORIGIN` environment variable on your backend to match your Vercel domain:

```
CORS_ORIGIN=https://your-app.vercel.app
```

---

## 🤗 Deploy — Hugging Face Spaces (Backend)

The FastAPI backend is containerised and deployable on Hugging Face Spaces as a **Docker Space**.

### Step 1 — Create a New Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **Docker** as the SDK
3. Set visibility to **Public** (or Private with a Pro account)

### Step 2 — Push Code

Clone your HF Space repo and push the backend files:

```bash
# Clone the HF Space repo
git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
cd YOUR_SPACE_NAME

# Copy backend files
cp /path/to/Job-Scrapper/Dockerfile .
cp /path/to/Job-Scrapper/requirements.txt .
cp /path/to/Job-Scrapper/*.py .
cp -r /path/to/Job-Scrapper/db ./db
cp -r /path/to/Job-Scrapper/scrapers ./scrapers
cp -r /path/to/Job-Scrapper/services ./services

# Push
git add .
git commit -m "Deploy backend"
git push
```

### Step 3 — Set Secrets

In your Space's **Settings → Repository secrets**, add:

| Secret | Value |
|---|---|
| `DATABASE_URL` | Your Supabase connection string |
| `REDIS_URL` | Your Upstash Redis URL (with `rediss://`) |
| `LLM_API_KEY` | Your NVIDIA API key |
| `LLM_MODEL` | `meta/llama-3.3-70b-instruct` |
| `LLM_ENDPOINT` | `https://integrate.api.nvidia.com/v1/chat/completions` |
| `CORS_ORIGIN` | `https://your-app.vercel.app` |
| `SCHEDULE_REFRESH_ENABLED` | `false` (or `true` if you want auto-refresh) |

### Step 4 — Verify

Once the Space builds, your backend will be live at:

```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space
```

Test with:

```
https://YOUR_USERNAME-YOUR_SPACE_NAME.hf.space/docs
```

> **Note:** The Dockerfile exposes port `7860` (HF Spaces default). The `CMD` runs `uvicorn api:app --host 0.0.0.0 --port 7860`.

---

## ☁️ Cloud Services Setup

### Supabase (PostgreSQL)

[Supabase](https://supabase.com/) provides a free managed PostgreSQL database.

#### 1. Create a Project

1. Go to [supabase.com](https://supabase.com/) → **New Project**
2. Choose a region close to your HF Space (e.g., `ap-northeast-2` for Asia)
3. Set a strong database password — **save it**

#### 2. Get the Connection String

1. Go to **Project Settings → Database**
2. Copy the **Connection string (URI)** under "Connection pooling" (Transaction mode)
3. It will look like:

```
postgresql://postgres.XXXX:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

#### 3. Use in `.env`

```env
DATABASE_URL=postgresql://postgres.XXXX:YOUR_PASSWORD@aws-0-REGION.pooler.supabase.com:5432/postgres
```

> **Tip:** URL-encode special characters in your password (e.g., `@` → `%40`, `!` → `%21`).

#### 4. Tables

Tables are created automatically by SQLModel on first startup (`init_db()` in `api.py`). The schema includes:

| Table | Description |
|---|---|
| `job` | Scraped job postings with metadata |
| `resume` | Uploaded resumes with extracted text |
| `matchresult` | LLM-computed match scores |

---

### Upstash (Redis)

[Upstash](https://upstash.com/) provides a serverless Redis database with a generous free tier.

#### 1. Create a Database

1. Go to [console.upstash.com](https://console.upstash.com/) → **Create Database**
2. Choose a region close to your backend
3. Select **TLS** enabled (recommended)

#### 2. Get the Connection String

1. Go to your database dashboard → **Details**
2. Copy the **Redis URL** — it will look like:

```
rediss://default:YOUR_TOKEN@YOUR_DB.upstash.io:6379
```

> **Important:** Use `rediss://` (with double `s`) for TLS connections. Use `redis://` only for local/non-TLS connections.

#### 3. Use in `.env`

```env
REDIS_URL=rediss://default:YOUR_TOKEN@YOUR_DB.upstash.io:6379
```

---

## 📡 API Reference

**Base URL:** `http://localhost:8000` (local) or your HF Space URL

**Interactive docs:** `GET /docs` (Swagger UI)

### Companies

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/companies` | List all companies with scraper availability |

**Response:**
```json
[
  { "name": "Microsoft", "available": true },
  { "name": "IBM", "available": false }
]
```

### Resume

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/resume/upload` | Upload a PDF resume (multipart form-data) |

**Response:**
```json
{ "resume_id": 1, "filename": "resume.pdf", "is_new": true }
```

### Scraping & Matching

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/scrape` | Scrape companies + optionally match against resume |
| `POST` | `/api/refresh` | Re-scrape companies (no matching) |
| `POST` | `/api/resume/{resume_id}/match` | Match resume against existing DB jobs |

**`POST /api/scrape` body:**
```json
{ "companies": ["Microsoft"], "resume_id": 1 }
```

### Jobs & Results

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| `GET` | `/api/jobs` | `companies` | Recent jobs (no resume needed) |
| `GET` | `/api/results/{resume_id}` | `companies`, `locations`, `min_exp`, `max_exp`, `education` | Scored match results with filtering |
| `GET` | `/api/filters` | `companies` | Available filter options for current jobs |

**`GET /api/results/1` response:**
```json
[
  {
    "job_id": 42,
    "title": "Software Engineer",
    "company": "Microsoft",
    "url": "https://apply.careers.microsoft.com/...",
    "location": "Redmond, Washington, United States",
    "min_experience": 3,
    "education_levels": ["ug", "pg"],
    "date_posted": "2026-05-01T00:00:00",
    "overall_score": 78.5,
    "skills_score": 85.0,
    "experience_score": 68.8,
    "reasoning": "Strong match in Python and cloud skills...",
    "matched_skills": ["Python", "Azure", "REST APIs"],
    "missing_skills": ["Kubernetes", "Terraform"]
  }
]
```

---

## 🔧 Adding a New Company Scraper

1. **Create the scraper** — `scrapers/<company>.py`:

```python
from scrapers.base import BaseScraper
from db.models import Job

class AcmeScraper(BaseScraper):
    company_name = "Acme"

    def fetch_jobs(self, last_scraped_date=None) -> list[Job]:
        # Implement API/web scraping logic
        # Return list of Job model instances
        ...
```

2. **Create the metadata extractor** — add to `services/extractor.py`:

```python
def _extract_acme_metadata(job) -> dict:
    # Company-specific metadata extraction
    return {
        "location": ...,
        "education_levels": [...],
        "min_experience": ...,
        "max_experience": ...,
    }

# Add to registry
EXTRACTORS = {
    "Microsoft": _extract_microsoft_metadata,
    "Acme": _extract_acme_metadata,           # ← add here
}
```

3. **Register the scraper** — in `services/tasks.py`:

```python
from scrapers.acme import AcmeScraper

SCRAPERS = {
    "Microsoft": MicrosoftScraper,
    "Acme": AcmeScraper,                      # ← add here
}
```

4. **Enable in the API** — in `api.py`:

```python
AVAILABLE_SCRAPERS = {"Microsoft", "Acme"}    # ← add here
ALL_COMPANIES = ["Microsoft", "IBM", "Oracle", "Adobe", "Acme"]
```

---

## ⏱ Scheduled Refresh

The backend uses **APScheduler** to automatically re-scrape companies at fixed UTC hours.

| Variable | Default | Description |
|---|---|---|
| `SCHEDULE_REFRESH_ENABLED` | `true` | Toggle on/off |
| `SCHEDULE_REFRESH_HOURS_UTC` | `2,14` | Comma-separated hours (24h format) |
| `SCHEDULE_REFRESH_COMPANIES` | `Microsoft` | Comma-separated company names |

The scheduler starts on app startup and runs `refresh_company_data()` for each configured company at the specified hours. Disable it in development by setting `SCHEDULE_REFRESH_ENABLED=false`.

---

## 🧩 Deployment Summary

| Component | Service | URL |
|---|---|---|
| **Frontend** | Vercel | `https://your-app.vercel.app` |
| **Backend** | Hugging Face Spaces (Docker) | `https://user-space.hf.space` |
| **Database** | Supabase (PostgreSQL) | Managed — connection string only |
| **Cache** | Upstash (Redis) | Managed — connection string only |
| **LLM** | NVIDIA API | `https://integrate.api.nvidia.com/v1/chat/completions` |

```
User → Vercel (React) → HF Spaces (FastAPI) → NVIDIA LLM
                                    ↕                ↕
                              Supabase (PG)    Upstash (Redis)
```

---

## 📄 License

This project is open source. Feel free to fork, modify, and deploy.
