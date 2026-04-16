function MatchResults({ matches }) {
    if (matches.length === 0) {
        return (
            <div className="card">
                <h2>📊 Match Results</h2>
                <p className="empty-state">No match results yet. Run the scraper to find matching jobs!</p>
            </div>
        );
    }

    return (
        <div className="card">
            <h2>📊 Match Results ({matches.length})</h2>
            {matches.map((m) => (
                <div key={m.job_id} className="match-item">
                    <div className="match-header">
                        <div className="job-info">
                            <h3>
                                <a href={m.url} target="_blank" rel="noreferrer">
                                    {m.title}
                                </a>
                            </h3>
                            <span className="job-meta">
                                {m.company} · {new Date(m.date_posted).toLocaleDateString()}
                            </span>
                        </div>
                        <span className="match-score-badge">{m.overall_score.toFixed(1)}%</span>
                    </div>

                    <div className="meta-tags">
                        {m.location && <span className="meta-tag">{m.location}</span>}
                        {m.min_experience != null && (
                            <span className="meta-tag">{m.min_experience}+ years</span>
                        )}
                        {m.education_levels?.length > 0 && (
                            <span className="meta-tag">{m.education_levels.join(", ").toUpperCase()}</span>
                        )}
                    </div>

                    <div className="score-bars">
                        <div className="score-bar">
                            <div className="label">
                                <span>Semantic</span>
                                <span>{m.skills_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill semantic"
                                    style={{ width: `${m.skills_score}%` }}
                                />
                            </div>
                        </div>

                        <div className="score-bar">
                            <div className="label">
                                <span>Experience</span>
                                <span>{m.experience_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill keyword"
                                    style={{ width: `${m.experience_score}%` }}
                                />
                            </div>
                        </div>

                        <div className="score-bar">
                            <div className="label">
                                <span>Overall</span>
                                <span>{m.overall_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill hybrid"
                                    style={{ width: `${m.overall_score}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {m.reasoning && <p className="match-reasoning">{m.reasoning}</p>}

                    {m.matched_skills && m.matched_skills.length > 0 && (
                        <div className="keywords">
                            {m.matched_skills.map((skill, i) => (
                                <span key={i} className="keyword-tag">{skill}</span>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

export default MatchResults;