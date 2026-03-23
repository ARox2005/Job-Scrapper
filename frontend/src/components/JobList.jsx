function JobList({ jobs }) {
    if (jobs.length === 0) {
        return (
            <div className="card">
                <h2>📋 Recent Job Postings</h2>
                <p className="empty-state">No jobs yet. Select companies and run the scraper!</p>
            </div>
        );
    }

    return (
        <div className="card">
            <h2>📋 Recent Job Postings ({jobs.length})</h2>
            {jobs.map((job) => (
                <div key={job.id} className="job-item">
                    <div className="job-info">
                        <h3>
                            <a href={job.url} target="_blank" rel="noreferrer">
                                {job.title}
                            </a>
                        </h3>
                        <span className="job-meta">{job.company}</span>
                    </div>
                    <span className="job-date">
                        {new Date(job.date_posted).toLocaleDateString()}
                    </span>
                </div>
            ))}
        </div>
    );
}

export default JobList;
