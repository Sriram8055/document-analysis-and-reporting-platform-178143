from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class Result(Base):
    """Stores the outcome of a job: extracted entities, mapped rows, validation issues, and report path."""

    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), unique=True, index=True)

    # JSON represented as text for SQLite compatibility; API can load/dump as needed
    entities_json: Mapped[str] = mapped_column(String, default="[]")
    mapped_rows_json: Mapped[str] = mapped_column(String, default="[]")
    validation_issues_json: Mapped[str] = mapped_column(String, default="[]")
    report_path: Mapped[str] = mapped_column(String(1024), default="")

    job = relationship("Job", back_populates="result")
