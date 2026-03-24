from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, UniqueConstraint
from sqlalchemy import Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB

class Job(SQLModel, table=True):
    """A scraped job posting from any company."""

    __table_args__ = (
        UniqueConstraint("company", "external_job_id", name="uq_company_job"),
        {"extend_existing": True}
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    company: str = Field(index=True)
    external_job_id: str
    title: str
    url: str
    date_posted: datetime = Field(sa_column=Column(DateTime, index=True))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    qualifications: Optional[str] = Field(default=None, sa_column=Column(Text))
    raw_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(default=None, index=True)

class Resume(SQLModel, table=True):
    """An uploaded resume."""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    text_hash: str = Field(unique=True)                 # SHA-256 of extracted text
    extracted_text: str = Field(sa_column=Column(Text))
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class MatchResult(SQLModel, table=True):
    """A match score between a resume and a job."""
    __table_args__ = {"extend_existing": True}
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: int = Field(foreign_key="job.id")
    resume_id: int = Field(foreign_key="resume.id")
    semantic_score: float
    keyword_score: float
    hybrid_score: float = Field(index=True)
    matched_keywords: Optional[list] = Field(default=None, sa_column=Column(JSONB))
    matched_at: datetime = Field(default_factory=datetime.utcnow)