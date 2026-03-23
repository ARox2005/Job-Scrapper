import axios from "axios";

const API = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

// ── Resume ───────────────────────────────────────────────
export async function uploadResume(file) {
    const formData = new FormData();
    formData.append("file", file);

    const { data } = await API.post("/api/resume/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
    return data; // { resume_id, filename, is_new }
}

// ── Companies ────────────────────────────────────────────
export async function getCompanies() {
    const { data } = await API.get("/api/companies");
    return data; // [{ name, available }]
}

// ── Scrape ───────────────────────────────────────────────
export async function scrapeJobs(companies, resumeId = null) {
    const { data } = await API.post("/api/scrape", {
        companies,
        resume_id: resumeId,
    });
    return data; // [{ company, status, new_jobs, message }]
}

// ── Jobs (no resume) ─────────────────────────────────────
export async function getJobs() {
    const { data } = await API.get("/api/jobs");
    return data; // [{ id, company, title, url, date_posted }]
}

// ── Match Results ────────────────────────────────────────
export async function getResults(resumeId) {
    const { data } = await API.get(`/api/results/${resumeId}`);
    return data; // [{ job_id, title, company, url, date_posted, semantic_score, keyword_score, hybrid_score, matched_keywords }]
}