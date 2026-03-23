import hashlib
import os
from datetime import datetime, timedelta

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import select

from db.sessions import get_session, init_db
from db.models import Job, Resume, MatchResult
from services.tasks import scrape_company, match_jobs
from utils import extract_text_from_pdf
import config

# ── App Setup ─────────────────────────────────────────────
app = FastAPI(title="Job Scrapper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "http://localhost:5173")],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

AVAILABLE_SCRAPERS = {"Microsoft"}
ALL_COMPANIES = ["Microsoft", "IBM", "Oracle", "Adobe"]

# Create DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# ── Request / Response Schemas ────────────────────────────
class ScrapeRequest(BaseModel):
    companies: list[str]
    resume_id: int | None = None

class ScrapeResult(BaseModel):
    company: str
    status: str
    new_jobs: int = 0
    message: str = ""

class JobOut(BaseModel):
    id: int
    company: str
    title: str
    url: str
    date_posted: datetime

class MatchOut(BaseModel):
    job_id: int
    title: str
    company: str
    url: str
    date_posted: datetime
    semantic_score: float
    keyword_score: float
    hybrid_score: float
    matched_keywords: list[str] | None = None

# ── Endpoints ─────────────────────────────────────────────
@app.get("/api/companies")
def get_companies():
    """Return all companies with their availability status."""
    return [
        {"name": c, "available": c in AVAILABLE_SCRAPERS}
        for c in ALL_COMPANIES
    ]

@app.post("/api/resume/upload")
def upload_resume(file: UploadFile = File(...)):
    """Upload a PDF resume, extract text, save to DB, return resume_id."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save temp file and extract text
    temp_path = "temp_resume.pdf"
    with open(temp_path, "wb") as f:
        f.write(file.file.read())

    resume_text = extract_text_from_pdf(temp_path)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    text_hash = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()

    # Check for duplicate or create new
    with get_session() as session:
        existing = session.exec(
            select(Resume).where(Resume.text_hash == text_hash)
        ).first()

        if existing:
            return {"resume_id": existing.id, "filename": file.filename, "is_new": False}

        resume = Resume(
            filename=file.filename,
            text_hash=text_hash,
            extracted_text=resume_text,
        )

        session.add(resume)
        session.flush()
        resume_id = resume.id

    return {"resume_id": resume_id, "filename": file.filename, "is_new": True}

@app.post("/api/scrape", response_model=list[ScrapeResult])
def scrape(request: ScrapeRequest):
    """Scrape selected companies and optionally match against a resume."""
    results = []

    for company in request.companies:
        if company not in AVAILABLE_SCRAPERS:
            results.append(ScrapeResult(
                company=company,
                status="coming_soon",
                message=f"{company} scraper coming soon!",
            ))
            continue

        # Run scraping synchronously
        result = scrape_company(company, request.resume_id)
        # Run matching synchronously (if resume provided and new jobs found)
        if request.resume_id and result.get("new_jobs", 0) > 0:
            # Get all job IDs for this company that don't have a match yet
            with get_session() as session:
                unmatched_jobs = session.exec(
                    select(Job.id)
                    .where(Job.company == company)
                    .where(
                        ~Job.id.in_(
                            select(MatchResult.job_id)
                            .where(MatchResult.resume_id == request.resume_id)
                        )
                    )
                ).all()
            if unmatched_jobs:
                match_jobs(request.resume_id, list(unmatched_jobs))
        results.append(ScrapeResult(
            company=company,
            status=result.get("status", "error"),
            new_jobs=result.get("new_jobs", 0),
            message=result.get("message", ""),
        ))
    return results

@app.get("/api/jobs", response_model=list[JobOut])
def get_jobs():
    """Return all recent jobs sorted by date (no resume mode)."""
    cutoff = datetime.utcnow() - timedelta(days=config.JOB_RETENTION_DAYS)
    with get_session() as session:
        jobs = session.exec(
            select(Job)
            .where(Job.date_posted >= cutoff)
            .order_by(Job.date_posted.desc())
        ).all()
    return [
        JobOut(
            id=job.id,
            company=job.company,
            title=job.title,
            url=job.url,
            date_posted=job.date_posted,
        )
        for job in jobs
    ]

@app.get("/api/results/{resume_id}", response_model=list[MatchOut])
def get_results(resume_id: int):
    """Return match results for a resume, sorted by hybrid score."""
    with get_session() as session:
        rows = session.exec(
            select(MatchResult, Job)
            .join(Job, MatchResult.job_id == Job.id)
            .where(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.hybrid_score.desc())
        ).all()
    return [
        MatchOut(
            job_id=job.id,
            title=job.title,
            company=job.company,
            url=job.url,
            date_posted=job.date_posted,
            semantic_score=match.semantic_score,
            keyword_score=match.keyword_score,
            hybrid_score=match.hybrid_score,
            matched_keywords=match.matched_keywords,
        )
        for match, job in rows
    ]