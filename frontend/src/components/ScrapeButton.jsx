import { scrapeJobs } from "../api";

function ScrapeButton({ selectedCompanies, resumeId, sessionId, loading, setLoading, onComplete }) {

    async function handleScrape() {
        if (selectedCompanies.length === 0) return;

        setLoading(true);
        try {
            const results = await scrapeJobs(selectedCompanies, resumeId, sessionId);
            onComplete(results);
        } catch (err) {
            console.error("Scrape failed:", err);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="card">
            <button
                className="scrape-btn"
                onClick={handleScrape}
                disabled={loading || selectedCompanies.length === 0}
            >
                {loading ? (
                    <>
                        <span className="spinner" />
                        Scraping...
                    </>
                ) : (
                    "🔍 Run Scraper"
                )}
            </button>
        </div>
    );
}

export default ScrapeButton;
