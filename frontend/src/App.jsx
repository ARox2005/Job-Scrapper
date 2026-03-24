import { useState, useEffect } from "react";
import { getCompanies, getJobs, getResults } from "./api";
import ResumeUpload from "./components/ResumeUpload";
import CompanySelector from "./components/CompanySelector";
import ScrapeButton from "./components/ScrapeButton";
import JobList from "./components/JobList";
import MatchResults from "./components/MatchResults";
import "./App.css";

function App() {
  // ── State ────────────────────────────────────────────
  const [resumeId, setResumeId] = useState(null);
  const [resumeName, setResumeName] = useState("");
  const [companies, setCompanies] = useState([]);
  const [selectedCompanies, setSelectedCompanies] = useState([]);
  const [scrapedCompanies, setScrapedCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scrapeMessages, setScrapeMessages] = useState([]);

  // ── Load companies on mount ──────────────────────────
  useEffect(() => {
    getCompanies().then(setCompanies);
  }, []);

  // ── Load results whenever resumeId changes ───────────
  useEffect(() => {
    if (resumeId && scrapedCompanies.length > 0) {
      getResults(resumeId).then(setMatches);
    }
  }, [resumeId]);

  // ── After scraping completes, refresh results ────────
  function handleScrapeComplete(messages) {
    setScrapeMessages(messages);
    // Track which companies were successfully scraped
    const successCompanies = messages
      .filter((m) => m.status === "ok")
      .map((m) => m.company);
    const allScraped = [...new Set([...scrapedCompanies, ...successCompanies])];
    setScrapedCompanies(allScraped);

    if (resumeId) {
      getResults(resumeId).then(setMatches);
    } else {
      getJobs(allScraped).then(setJobs);
    }
  }

  // ── Toggle company selection ─────────────────────────
  function toggleCompany(name) {
    setSelectedCompanies((prev) =>
      prev.includes(name)
        ? prev.filter((c) => c !== name)
        : [...prev, name]
    );
  }

  // ── Render ───────────────────────────────────────────
  return (
    <div className="app">
      <header className="app-header">
        <h1>📄 Job Scraper</h1>
        <p>Upload your resume to find the best matching jobs</p>
      </header>
      <ResumeUpload
        resumeName={resumeName}
        onUpload={(id, filename) => {
          setResumeId(id);
          setResumeName(filename);
        }}
      />
      <CompanySelector
        companies={companies}
        selected={selectedCompanies}
        onToggle={toggleCompany}
      />
      <ScrapeButton
        selectedCompanies={selectedCompanies}
        resumeId={resumeId}
        loading={loading}
        setLoading={setLoading}
        onComplete={handleScrapeComplete}
      />
      {scrapeMessages.length > 0 && (
        <div className="card">
          <div className="scrape-status">
            {scrapeMessages.map((msg, i) => (
              <p key={i} className={msg.status === "ok" ? "success" : "coming-soon"}>
                {msg.status === "ok"
                  ? `✅ ${msg.company}: ${msg.new_jobs} new jobs`
                  : `🚧 ${msg.company}: ${msg.message}`}
              </p>
            ))}
          </div>
        </div>
      )}
      <hr className="divider" />
      {resumeId ? (
        <MatchResults matches={matches} />
      ) : (
        <JobList jobs={jobs} />
      )}
    </div>
  );
}
export default App;