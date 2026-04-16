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
export async function getJobs(companies) {
    const param = companies.join(",");
    const { data } = await API.get(`/api/jobs?companies=${param}`);
    return data; // [{ id, company, title, url, date_posted }]
}

// ── Match Results ────────────────────────────────────────
// export async function getResults(resumeId) {
//     const { data } = await API.get(`/api/results/${resumeId}`);
//     return data;
// }

export async function getResults(resumeId, filters = {}) {
    const params = new URLSearchParams();
    if (filters.locations?.length) params.set("locations", filters.locations.join(","));
    if (filters.education) params.set("education", filters.education);
    if (filters.minExp != null) params.set("min_exp", filters.minExp);
    if (filters.maxExp != null) params.set("max_exp", filters.maxExp);
    const query = params.toString() ? `?${params.toString()}` : "";
    const { data } = await API.get(`/api/results/${resumeId}${query}`);
    return data;
}

export async function getFilters(companies) {
    const params = new URLSearchParams();
    if (companies?.length) params.set("companies", companies.join(","));
    const query = params.toString() ? `?${params.toString()}` : "";
    const { data } = await API.get(`/api/filters${query}`);
    return data;
}