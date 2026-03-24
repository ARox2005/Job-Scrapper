from celery_app import app
from db.models import Job, Resume, MatchResult
from db.sessions import get_session, init_db
from matcher import compute_match
from scrapers.microsoft import MicrosoftScraper
from sqlmodel import select
from datetime import datetime

# Registry of available scrapers
SCRAPERS = {
    "Microsoft": MicrosoftScraper,
}

@app.task(name="scrape_company")
def scrape_company(company_name: str, resume_id: int | None=None, session_id: str | None=None):
    """
    Scrape jobs for a company, save to DB, then match against the resume.
    """
    scraper_class = SCRAPERS.get(company_name)
    if not scraper_class:
        return {"status": "error", "message": f"{company_name} scraper not available"}

    init_db()

    # Find the last scraped date for this company
    with get_session() as session:
        last_job = session.exec(
            select(Job)
            .where(Job.company == company_name)
            .order_by(Job.date_posted.desc())  
        ).first()
        last_date = last_job.date_posted if last_job else None

    # Scrape new jobs
    scraper = scraper_class()
    new_jobs = scraper.fetch_jobs(last_scraped_date=last_date)
    if not new_jobs:
        return {"status": "ok", "new_jobs": 0}

    # Save jobs to DB (skip duplicates)
    saved_count = 0
    saved_ids = []
    with get_session() as session:
        for job in new_jobs:
            existing = session.exec(
                select(Job).where(
                    Job.company == job.company,
                    Job.external_job_id == job.external_job_id,
                    Job.session_id == session_id,
                )
            ).first()
            if not existing:
                job.session_id = session_id
                session.add(job)
                session.flush()          # assigns job.id without committing
                saved_ids.append(job.id)
                saved_count += 1

    # Match new jobs against the resume (only if resume provided)
    if resume_id and saved_ids:
        match_jobs.delay(resume_id, saved_ids)
        # match_jobs(resume_id, saved_ids)
    return {"status": "ok", "new_jobs": saved_count}

@app.task(name="match_jobs")
def match_jobs(resume_id: int, job_ids: list[int]):
    """
    Run the hybrid matcher on each job against the resume.
    """
    with get_session() as session:
        resume = session.get(Resume, resume_id)
        if not resume:
            return {"status": "error", "message": "Resume not found"}
        for job_id in job_ids:
            job = session.get(Job, job_id)
            if not job:
                continue

            # Use qualifications if available, otherwise description
            job_text = job.qualifications or job.description or ""
            if not job_text:
                continue
            result = compute_match(resume.extracted_text, job_text)
            match_result = MatchResult(
                job_id=job.id,
                resume_id=resume.id,
                semantic_score=result.semantic_score,
                keyword_score=result.keyword_score,
                hybrid_score=result.hybrid_score,
                matched_keywords=result.matched_keywords,
                matched_at=datetime.utcnow(),
            )
            session.add(match_result)
    return {"status": "ok", "matched": len(job_ids)}