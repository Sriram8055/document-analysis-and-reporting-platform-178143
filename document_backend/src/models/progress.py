from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, now_utc


class Progress(Base):
    """Optional granular progress log for a job."""

    __tablename__ = "progress"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)

    phase: Mapped[str] = mapped_column(String(64))
    percent: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(String(1024), default="")
    ts: Mapped[datetime] = mapped_column(DateTime, default=now_utc)

    job = relationship("Job", back_populates="progress_events")
