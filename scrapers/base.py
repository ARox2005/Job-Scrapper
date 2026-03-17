from abc import ABC, abstractmethod
from datetime import datetime

from db.models import Job

class BaseScraper(ABC):
    """Base class for all company scrapers."""

    @abstractmethod
    def fetch_jobs(self, last_scraped_data: datetime | None=None) -> list[Job]:
        """
        Scrape new jobs since last_scraped_date.
        Returns a list of Job model instances.
        If last_scraped_date is None, fetch jobs from the last 7 days.
        """
        ...