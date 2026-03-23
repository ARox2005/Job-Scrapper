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
                        <span className="match-score-badge">{m.hybrid_score.toFixed(1)}%</span>
                    </div>

                    <div className="score-bars">
                        <div className="score-bar">
                            <div className="label">
                                <span>Semantic</span>
                                <span>{m.semantic_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill semantic"
                                    style={{ width: `${m.semantic_score}%` }}
                                />
                            </div>
                        </div>

                        <div className="score-bar">
                            <div className="label">
                                <span>Keyword</span>
                                <span>{m.keyword_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill keyword"
                                    style={{ width: `${m.keyword_score}%` }}
                                />
                            </div>
                        </div>

                        <div className="score-bar">
                            <div className="label">
                                <span>Hybrid</span>
                                <span>{m.hybrid_score.toFixed(1)}%</span>
                            </div>
                            <div className="track">
                                <div
                                    className="fill hybrid"
                                    style={{ width: `${m.hybrid_score}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {m.matched_keywords && m.matched_keywords.length > 0 && (
                        <div className="keywords">
                            {m.matched_keywords.map((kw, i) => (
                                <span key={i} className="keyword-tag">{kw}</span>
                            ))}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}

export default MatchResults;