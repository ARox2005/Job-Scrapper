import { useState, useEffect } from "react";
// import { getCompanies, getJobs, getResults } from "./api";
import { getCompanies, getJobs, getResults, getFilters } from "./api";
import ResumeUpload from "./components/ResumeUpload";
import CompanySelector from "./components/CompanySelector";
import ScrapeButton from "./components/ScrapeButton";
import JobList from "./components/JobList";
import MatchResults from "./components/MatchResults";
import "./App.css";
import FilterSidebar from "./components/FilterSidebar";

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
  const [filters, setFilters] = useState({ locations: [], education_levels: [], experience_range: [0, 0] });
  const [selectedFilters, setSelectedFilters] = useState({ locations: [], education: null, minExp: null, maxExp: null });

  // ── Load companies on mount ──────────────────────────
  useEffect(() => {
    getCompanies().then(setCompanies);
  }, []);

  // ── Load results whenever resumeId changes ───────────
  // useEffect(() => {
  //   if (resumeId && scrapedCompanies.length > 0) {
  //     getResults(resumeId).then(setMatches);
  //   }
  // }, [resumeId]);

  useEffect(() => {
    if (resumeId && scrapedCompanies.length > 0) {
      getResults(resumeId, selectedFilters).then(setMatches);
    }
  }, [resumeId, scrapedCompanies, selectedFilters]);

  useEffect(() => {
    if (scrapedCompanies.length > 0) {
      getFilters(scrapedCompanies).then(setFilters);
    }
  }, [scrapedCompanies]);

  // ── After scraping completes, refresh results ────────
  function handleScrapeComplete(messages) {
    setScrapeMessages(messages);
    // Track which companies were successfully scraped
    const successCompanies = messages
      .filter((m) => m.status === "ok")
      .map((m) => m.company);
    const allScraped = [...new Set([...scrapedCompanies, ...successCompanies])];
    setScrapedCompanies(allScraped);
    getFilters(allScraped).then(setFilters)

    // if (resumeId) {
    //   getResults(resumeId).then(setMatches);
    // } else {
    //   getJobs(allScraped).then(setJobs);
    // }
    if (resumeId) {
      getResults(resumeId, selectedFilters).then(setMatches);
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

  // ── Render ───────────────────────────────────────────
  // return (
  //   <div className="app">
  //     <header className="app-header">
  //       <h1>📄 Job Scraper</h1>
  //       <p>Upload your resume to find the best matching jobs</p>
  //     </header>
  //     <ResumeUpload
  //       resumeName={resumeName}
  //       onUpload={(id, filename) => {
  //         setResumeId(id);
  //         setResumeName(filename);
  //       }}
  //     />
  //     <CompanySelector
  //       companies={companies}
  //       selected={selectedCompanies}
  //       onToggle={toggleCompany}
  //     />
  //     <ScrapeButton
  //       selectedCompanies={selectedCompanies}
  //       resumeId={resumeId}
  //       loading={loading}
  //       setLoading={setLoading}
  //       onComplete={handleScrapeComplete}
  //     />
  //     {scrapeMessages.length > 0 && (
  //       <div className="card">
  //         <div className="scrape-status">
  //           {scrapeMessages.map((msg, i) => (
  //             <p key={i} className={msg.status === "ok" ? "success" : "coming-soon"}>
  //               {msg.status === "ok"
  //                 ? `✅ ${msg.company}: ${msg.new_jobs} new jobs`
  //                 : `🚧 ${msg.company}: ${msg.message}`}
  //             </p>
  //           ))}
  //         </div>
  //       </div>
  //     )}

  //     <div className="app-layout">
  //       {resumeId && scrapedCompanies.length > 0 && (
  //         <aside className="sidebar">
  //           <FilterSidebar filters={filters} selected={selectedFilters} onChange={setSelectedFilters} />
  //         </aside>
  //       )}
  //       <main className="main-content">
  //         {resumeId ? <MatchResults matches={matches} /> : <JobList jobs={jobs} />}
  //       </main>
  //     </div>


  //     <hr className="divider" />
  //     {resumeId ? (
  //       <MatchResults matches={matches} />
  //     ) : (
  //       <JobList jobs={jobs} />
  //     )}
  //   </div>
  // );

  return (
    <div className="app">
      <header className="app-header">
        <h1>Job Scraper</h1>
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
                  ? `${msg.company}: ${msg.new_jobs} new jobs`
                  : `${msg.company}: ${msg.message}`}
              </p>
            ))}
          </div>
        </div>
      )}

      {/* <div className="app-layout">
        {resumeId && scrapedCompanies.length > 0 && (
          <aside className="sidebar">
            <FilterSidebar
              filters={filters}
              selected={selectedFilters}
              onChange={setSelectedFilters}
            />
          </aside>
        )}

        <main className="main-content">
          {resumeId ? <MatchResults matches={matches} /> : <JobList jobs={jobs} />}
        </main>
      </div> */}

      <div className="app-layout">
        {scrapedCompanies.length > 0 && (
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