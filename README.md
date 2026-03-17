# Job-Scrapper

A resume-matched job aggregation tool that scrapes job postings from major tech companies and ranks them by relevance to your resume using **semantic similarity (MiniLM)** and **keyword matching**.

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **Database** | PostgreSQL (SQLModel ORM) |
| **Cache & Broker** | Redis |
| **Task Queue** | Celery |
| **Matching** | Sentence-Transformers (`all-MiniLM-L6-v2`) + keyword overlap |
| **Scraping** | Requests, BeautifulSoup, Selenium |

## Architecture

```
Streamlit UI → Celery Task Queue (Redis broker)
                    ↓
              Scraper Workers (per company)
                    ↓
              Matcher (MiniLM + keywords)
                    ↓
              PostgreSQL (jobs, resumes, match results)
                    ↑
              Redis (embedding cache)
```

## Project Structure

```
├── app.py                  # Streamlit UI
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

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/jobscrapper
REDIS_URL=redis://localhost:6379/0
```

### 4. Run

```bash
# Terminal 1 — Celery worker
celery -A celery_app worker --loglevel=info --pool=solo

# Terminal 2 — Streamlit app
streamlit run app.py
```

## How It Works

1. **Upload** your resume (PDF)
2. **Select** companies to scrape
3. **Run** — the scraper fetches recent job postings, stores them in PostgreSQL, then the matcher scores each job against your resume
4. **View** results sorted by relevance with semantic score, keyword score, and matched keywords

## Matching Algorithm

The hybrid matcher combines two scoring methods:

- **Semantic (60%)** — MiniLM embeddings with cosine similarity. Understands meaning (e.g., "ML" ≈ "machine learning")
- **Keyword (40%)** — Direct word overlap after stopword removal. Catches exact skill mentions

```
hybrid_score = 0.6 × semantic + 0.4 × keyword
```

Embeddings are cached in Redis (24h TTL) to avoid recomputation.

## Adding a New Company

1. Create `scrapers/<company>.py`
2. Extend `BaseScraper` and implement `fetch_jobs()`
3. Add to `SCRAPERS` registry in `services/tasks.py`
4. Add to `AVAILABLE_SCRAPERS` in `app.py`