---
title: Job Scrapper API
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Job-Scrapper

A resume-matched job aggregation tool that scrapes job postings from major tech companies and ranks them by relevance to your resume using **semantic similarity (MiniLM)** and **keyword matching**.

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (Vite) |
| **Backend API** | FastAPI |
| **Database** | PostgreSQL (SQLModel ORM) |
| **Cache & Broker** | Redis |
| **Task Queue** | Celery |
| **Matching** | Sentence-Transformers (`all-MiniLM-L6-v2`) + keyword overlap |
| **Scraping** | Requests, BeautifulSoup, Selenium |

## Architecture

```
React UI (Vite :5173)
    ↓  HTTP
FastAPI (:8000)
    ↓
Celery Task Queue (Redis broker)
    ↓
Scraper Workers → Matcher (MiniLM + keywords)
    ↓
PostgreSQL (jobs, resumes, match results)
    ↑
Redis (embedding cache)
```

## Project Structure

```
├── api.py                  # FastAPI backend (REST endpoints)
├── matcher.py              # Hybrid matcher (MiniLM + keywords)
├── utils.py                # PDF/image text extraction
├── config.py               # Central configuration
├── celery_app.py           # Celery application config
├── db/
│   ├── models.py           # Job, Resume, MatchResult models
│   └── sessions.py         # Postgres engine & sessions
├── scrapers/
│   ├── base.py             # Abstract base scraper
│   └── microsoft.py        # Microsoft Careers scraper
├── services/
│   ├── cache.py            # Redis embedding cache
│   └── tasks.py            # Celery async tasks
├── frontend/               # React app (Vite)
│   ├── src/
│   │   ├── api.js          # Axios API helper
│   │   ├── App.jsx         # Root component
│   │   ├── App.css         # Global styles
│   │   └── components/
│   │       ├── ResumeUpload.jsx
│   │       ├── CompanySelector.jsx
│   │       ├── ScrapeButton.jsx
│   │       ├── JobList.jsx
│   │       └── MatchResults.jsx
│   └── package.json
├── docker-compose.yml      # Postgres + Redis
├── .env                    # Connection strings (not committed)
└── requirements.txt
```

## Setup

### 1. Start Services

**Option A — Docker:**
```bash
docker-compose up -d
```

**Option B — Native:**
- Install [PostgreSQL](https://www.postgresql.org/download/windows/) and create database `jobscrapper`
- Install [Memurai](https://www.memurai.com/) (Redis for Windows) or use WSL

### 2. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 4. Configure Environment

Create a `.env` file:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobscrapper
REDIS_URL=redis://localhost:6379/0
```

### 5. Run

Open 3 terminals:

```bash
# Terminal 1 — Celery worker
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 2 — FastAPI backend
uvicorn api:app --reload --port 8000

# Terminal 3 — React frontend
cd frontend && npm run dev
```

Then open **http://localhost:5173** in your browser.

## How It Works

1. **Upload** your resume (PDF)
2. **Select** companies to scrape
3. **Run** — the scraper fetches recent job postings, stores them in PostgreSQL, then the matcher scores each job against your resume
4. **View** results sorted by relevance with semantic score, keyword score, and matched keywords

Without a resume, all jobs are displayed sorted by date.

## Matching Algorithm

The hybrid matcher combines two scoring methods:

- **Semantic (60%)** — MiniLM embeddings with cosine similarity. Understands meaning (e.g., "ML" ≈ "machine learning")
- **Keyword (40%)** — Direct word overlap after stopword removal. Catches exact skill mentions

```
hybrid_score = 0.6 × semantic + 0.4 × keyword
```

Embeddings are cached in Redis (24h TTL) to avoid recomputation.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/companies` | List all companies with availability |
| `POST` | `/api/resume/upload` | Upload PDF resume |
| `POST` | `/api/scrape` | Scrape + match jobs |
| `GET` | `/api/jobs` | All recent jobs (no resume) |
| `GET` | `/api/results/{resume_id}` | Match results for a resume |

Interactive API docs: **http://localhost:8000/docs**

## Adding a New Company

1. Create `scrapers/<company>.py`
2. Extend `BaseScraper` and implement `fetch_jobs()`
3. Add to `SCRAPERS` registry in `services/tasks.py`
4. Add to `AVAILABLE_SCRAPERS` and `ALL_COMPANIES` in `api.py`