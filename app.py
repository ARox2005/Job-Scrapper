import hashlib
import streamlit as st
from sqlmodel import select
from datetime import datetime, timedelta

from db.sessions import get_session, init_db
from db.models import Job, Resume, MatchResult
from services.tasks import scrape_company
from utils import extract_text_from_pdf
import config


# ── Page Config ───────────────────────────────────────────

st.set_page_config(page_title="Job Scraper", page_icon="📄", layout="wide")
st.title("📄 Job Scraper Dashboard")

init_db()

# ── Available Companies ───────────────────────────────────

AVAILABLE_SCRAPERS = {"Microsoft"}
ALL_COMPANIES = ["Microsoft", "IBM", "Oracle", "Adobe"]

# ── Resume Upload (optional) ──────────────────────────────

resume_file = st.file_uploader("Upload your Resume (PDF) — optional", type=["pdf"])

resume_id = None

if resume_file:
    with open("temp_resume.pdf", "wb") as f:
        f.write(resume_file.read())

    resume_text = extract_text_from_pdf("temp_resume.pdf")
    text_hash = hashlib.sha256(resume_text.encode("utf-8")).hexdigest()

    with get_session() as session:
        existing = session.exec(
            select(Resume).where(Resume.text_hash == text_hash)
        ).first()

        if existing:
            resume_id = existing.id
        else:
            resume = Resume(
                filename=resume_file.name,
                text_hash=text_hash,
                extracted_text=resume_text,
            )
            session.add(resume)
            session.flush()
            resume_id = resume.id

    st.success(f"✅ Resume loaded: **{resume_file.name}**")

# ── Company Selection ─────────────────────────────────────

st.subheader("Select Companies")
selected_companies = []
cols = st.columns(len(ALL_COMPANIES))

for i, comp in enumerate(ALL_COMPANIES):
    with cols[i]:
        if st.checkbox(comp, key=comp):
            selected_companies.append(comp)

# ── Scrape Button ─────────────────────────────────────────

if st.button("🔍 Run Scraper", type="primary"):
    if not selected_companies:
        st.warning("Please select at least one company.")
    else:
        for company in selected_companies:
            if company not in AVAILABLE_SCRAPERS:
                st.info(f"🚧 **{company}** — Coming Soon!")
                continue

            with st.spinner(f"Scraping {company}..."):
                result = scrape_company(company, resume_id)
                # result = scrape_company.apply_async(args=[company, resume_id]).get()

            if result["status"] == "ok":
                st.success(f"✅ **{company}**: {result['new_jobs']} new jobs found!")
            else:
                st.error(f"❌ **{company}**: {result.get('message', 'Unknown error')}")

# ── Results Display ───────────────────────────────────────

st.divider()

if resume_id:
    # With resume: show matched results sorted by score
    st.subheader("📊 Match Results")

    with get_session() as session:
        results = session.exec(
            select(MatchResult, Job)
            .join(Job, MatchResult.job_id == Job.id)
            .where(MatchResult.resume_id == resume_id)
            .order_by(MatchResult.hybrid_score.desc())
        ).all()

    if results:
        for match, job in results:
            with st.expander(
                f"**{job.title}** — {job.company} | Score: {match.hybrid_score:.1f}%"
            ):
                col1, col2, col3 = st.columns(3)
                col1.metric("Semantic", f"{match.semantic_score:.1f}%")
                col2.metric("Keyword", f"{match.keyword_score:.1f}%")
                col3.metric("Hybrid", f"{match.hybrid_score:.1f}%")

                st.markdown(f"🔗 [View Job]({job.url})")
                st.caption(f"Posted: {job.date_posted.strftime('%Y-%m-%d')}")

                if match.matched_keywords:
                    st.markdown(
                        "**Matched Keywords:** "
                        + ", ".join(f"`{kw}`" for kw in match.matched_keywords)
                    )
    else:
        st.info("No match results yet. Run the scraper to find matching jobs!")

else:
    # Without resume: show all recent jobs sorted by date
    st.subheader("📋 Recent Job Postings")

    cutoff = datetime.utcnow() - timedelta(days=config.JOB_RETENTION_DAYS)

    with get_session() as session:
        jobs = session.exec(
            select(Job)
            .where(Job.date_posted >= cutoff)
            .order_by(Job.date_posted.desc())
        ).all()

    if jobs:
        for job in jobs:
            with st.expander(f"**{job.title}** — {job.company}"):
                st.markdown(f"🔗 [View Job]({job.url})")
                st.caption(f"Posted: {job.date_posted.strftime('%Y-%m-%d')}")
    else:
        st.info("No jobs yet. Select companies and run the scraper!")
