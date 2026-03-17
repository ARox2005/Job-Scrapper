import requests
from datetime import datetime, timedelta

from scrapers.base import BaseScraper
from db.models import Job
import config

class MicrosoftScraper(BaseScraper):
    """Scraper for Microsoft Careers API."""
    company_name = "Microsoft"
    SEARCH_URL = "https://apply.careers.microsoft.com/api/pcsx/search"
    JOB_URL = "https://apply.careers.microsoft.com/api/pcsx/position_details"

    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    def fetch_jobs(self, last_scraped_date: datetime | None=None) -> list[Job]:
        """Scrape new jobs from Microsoft Careers API."""
        if last_scraped_date is None:
            last_scraped_date = datetime.utcnow() - timedelta(days=config.JOB_RETENTION_DAYS)

        raw_jobs = self.__search_jobs(last_scraped_date)
        jobs = self.__enrich_with_qualifications(raw_jobs)

        return jobs

    def __search_jobs(self, since: datetime):
        """Paginate through the search API and collect raw job dicts."""
        collected = []
        pg = 0

        while True:
            url = f"{self.SEARCH_URL}?domain=microsoft.com&query=&location=&start={pg}&sort_by=timestamp&"
            response = requests.get(url, headers=self.HEADERS)

            if response.headers.get("Content-Type")!="application/json":
                print(f"Unexpected content type: {response.headers.get('Content-Type')}")
                break

            jobs = response.json()["data"]["positions"]
            if not jobs:
                break

            for item in jobs:
                posted = item["postedTs"]

                # Stop if we've gone past our date window
                if posted < int(since.timestamp()):
                    return collected

                collected.append(item)

            pg+=10

        return collected

    def __enrich_with_qualifications(self, raw_jobs: list[dict]) -> list[Job]:
        """Fetch qualifications for each job and build Job model instances."""
        jobs = []
        for item in raw_jobs:
            job_id = item["id"]
            url = f"{self.JOB_URL}?position_id={job_id}&domain=microsoft.com&hl=en"

            try:
                response = requests.get(url, headers=self.HEADERS)
                if response.headers.get("Content-Type") != "application/json":
                    continue

                qualifications = response.json()["data"]["jobDescription"]
            
            except Exception as e:
                print(f"Failed to fetch qualifications for {job_id}: {e}")
                qualifications = None

            job = Job(
                company=self.company_name,
                external_job_id=str(job_id),
                title=item["name"],
                url=f"https://apply.careers.microsoft.com{item['positionUrl']}",
                date_posted=datetime.fromtimestamp(item["postedTs"]),
                qualifications=qualifications,
                raw_data=item,
            )
            jobs.append(job)

        return jobs

            