from celery_app import app
from db.models import Job, Resume, MatchResult
from db.sessions import get_session, init_db
from matcher import compute_match
from scrapers.microsoft import MicrosoftScraper
from sqlmodel import select
from sqlalchemy import delete
from datetime import datetime, timedelta

import config
from services.extractor import extract_job_metadata

# Registry of available scrapers
SCRAPERS = {
    "Microsoft": MicrosoftScraper,
}

@app.task(name="scrape_company")
def scrape_company(company_name: str, resume_id: int | None=None):
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
                )
            ).first()
            if not existing:
                session.add(job)
                session.flush()          # assigns job.id without committing
                saved_ids.append(job.id)
                saved_count += 1

    # Extract metadata for new jobs (location, education, experience)
    for job_id in saved_ids:
        with get_session() as session:
            job = session.get(Job, job_id)
            if job:
                metadata = extract_job_metadata(job)
                job.location = metadata.get("location")
                job.min_experience = metadata.get("min_experience")
                job.max_experience = metadata.get("max_experience")
                job.education_levels = metadata.get("education_levels", [])
                session.add(job)

    # Match new jobs against the resume (only if resume provided)
    if resume_id and saved_ids:
        match_jobs(resume_id, saved_ids)
    return {"status": "ok", "new_jobs": saved_count}

def refresh_company_data(company_name: str):
    """
    Refresh a company's jobs in the DB without doing resume matching.
    This is what the manual refresh button and scheduler will use.
    """
    return scrape_company(company_name, None)

@app.task(name="match_jobs")
def match_jobs(resume_id: int, job_ids: list[int]):
    """
    Match a resume against a specific list of job ids.
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
                overall_score=result.overall_score,
                skills_score=result.skills_score,
                experience_score=result.experience_score,
                reasoning=result.reasoning,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
                matched_at=datetime.utcnow(),
            )

            session.add(match_result)
    return {"status": "ok", "matched": len(job_ids)}

@app.task(name="match_existing_jobs")
def match_existing_jobs(resume_id: int, companies: list[str] | None = None):
    """
    Match a resume against existing DB jobs only. No scraping.
    Only creates matches for jobs that do not already have a MatchResult
    for this resume.
    """
    cutoff = datetime.utcnow() - timedelta(days=config.JOB_RETENTION_DAYS)

    with get_session() as session:
        resume = session.get(Resume, resume_id)
        if not resume:
            return {"status": "error", "message": "Resume not found"}

        query = (
            select(Job.id)
            .where(Job.date_posted >= cutoff)
            .where(
                ~Job.id.in_(
                    select(MatchResult.job_id).where(MatchResult.resume_id == resume_id)
                )
            )
        )

        if companies:
            query = query.where(Job.company.in_(companies))

        job_ids = list(session.exec(query).all())

    if not job_ids:
        return {"status": "ok", "matched": 0}

    return match_jobs(resume_id, job_ids)