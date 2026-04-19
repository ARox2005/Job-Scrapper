import { useState, useEffect } from "react";
import {
  getCompanies,
  getJobs,
  getResults,
  getFilters,
  refreshJobs,
  matchResume,
} from "./api";
import ResumeUpload from "./components/ResumeUpload";
import CompanySelector from "./components/CompanySelector";
import JobList from "./components/JobList";
import MatchResults from "./components/MatchResults";
import FilterSidebar from "./components/FilterSidebar";
import "./App.css";

const EMPTY_FILTERS = {
  locations: [],
  education_levels: [],
  experience_range: [0, 0],
};

const EMPTY_SELECTED_FILTERS = {
  locations: [],
  education: null,
  minExp: null,
  maxExp: null,
};

function App() {
  const [resumeId, setResumeId] = useState(null);
  const [resumeName, setResumeName] = useState("");
  const [companies, setCompanies] = useState([]);
  const [selectedCompanies, setSelectedCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [matches, setMatches] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [refreshMessages, setRefreshMessages] = useState([]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [selectedFilters, setSelectedFilters] = useState(EMPTY_SELECTED_FILTERS);

  useEffect(() => {
    getCompanies().then(setCompanies);
  }, []);

  useEffect(() => {
    if (selectedCompanies.length === 0) {
      setJobs([]);
      setMatches([]);
      setFilters(EMPTY_FILTERS);
      setRefreshMessages([]);
      return;
    }

    getFilters(selectedCompanies).then(setFilters);

    if (resumeId) {
      matchResume(resumeId, selectedCompanies)
        .then(() => getResults(resumeId, selectedFilters, selectedCompanies))
        .then(setMatches)
        .catch((err) => console.error("DB match failed:", err));
    } else {
      getJobs(selectedCompanies)
        .then(setJobs)
        .catch((err) => console.error("Loading jobs failed:", err));
    }
  }, [selectedCompanies, resumeId]);

  useEffect(() => {
    if (resumeId && selectedCompanies.length > 0) {
      getResults(resumeId, selectedFilters, selectedCompanies)
        .then(setMatches)
        .catch((err) => console.error("Loading filtered matches failed:", err));
    }
  }, [resumeId, selectedCompanies, selectedFilters]);

  function toggleCompany(name) {
    setSelectedCompanies((prev) =>
      prev.includes(name)
        ? prev.filter((c) => c !== name)
        : [...prev, name]
    );
  }

  async function handleManualRefresh() {
    if (selectedCompanies.length === 0 || refreshing) return;

    setRefreshing(true);
    try {
      const results = await refreshJobs(selectedCompanies);
      setRefreshMessages(results);

      const latestFilters = await getFilters(selectedCompanies);
      setFilters(latestFilters);

      if (resumeId) {
        await matchResume(resumeId, selectedCompanies);
        const latestMatches = await getResults(
          resumeId,
          selectedFilters,
          selectedCompanies
        );
        setMatches(latestMatches);
      } else {
        const latestJobs = await getJobs(selectedCompanies);
        setJobs(latestJobs);
      }
    } catch (err) {
      console.error("Manual refresh failed:", err);
    } finally {
      setRefreshing(false);
    }
  }

  function jobMatchesFilters(job) {
    if (
      selectedFilters.locations.length > 0 &&
      !selectedFilters.locations.includes(job.location)
    ) {
      return false;
    }

    if (
      selectedFilters.education &&
      !(job.education_levels || []).includes(selectedFilters.education)
    ) {
      return false;
    }

    if (
      selectedFilters.minExp != null &&
      job.min_experience != null &&
      job.min_experience < selectedFilters.minExp
    ) {
      return false;
    }

    if (
      selectedFilters.maxExp != null &&
      job.min_experience != null &&
      job.min_experience > selectedFilters.maxExp
    ) {
      return false;
    }

    return true;
  }

  const filteredJobs = jobs.filter(jobMatchesFilters);

  return (
    <div className="app">
      <button
        className={`refresh-icon-btn ${refreshing ? "spinning" : ""}`}
        onClick={handleManualRefresh}
        disabled={refreshing || selectedCompanies.length === 0}
        title="Refresh selected companies"
      >
        ↻
      </button>

      <header className="app-header">
        <h1>Job Scraper</h1>
        <p>Upload your resume to match against jobs already stored in the database</p>
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

      {refreshMessages.length > 0 && (
        <div className="card">
          <div className="scrape-status">
            {refreshMessages.map((msg, i) => (
              <p key={i} className={msg.status === "ok" ? "success" : "coming-soon"}>
                {msg.status === "ok"
                  ? `${msg.company}: ${msg.new_jobs} new jobs added`
                  : `${msg.company}: ${msg.message}`}
              </p>
            ))}
          </div>
        </div>
      )}

      <div className="app-layout">
        {selectedCompanies.length > 0 && (
          <aside className="sidebar">
            <FilterSidebar
              filters={filters}
              selected={selectedFilters}
              onChange={setSelectedFilters}
            />
          </aside>
        )}

        <main className="main-content">
          {resumeId ? (
            <MatchResults matches={matches} />
          ) : (
            <JobList jobs={filteredJobs} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;