from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base, now_utc


class Job(Base):
    """Represents a processing job for document analysis."""

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    uuid: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: str(uuid4()))

    # Status lifecycle fields
    status: Mapped[str] = mapped_column(String(32), index=True, default="pending")  # pending, running, completed, failed
    phase: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)  # e.g., upload, extract, analyze, map, report
    percent: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc, onupdate=now_utc)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    files = relationship("File", back_populates="job", cascade="all, delete-orphan")
    result = relationship("Result", back_populates="job", uselist=False, cascade="all, delete-orphan")
    progress_events = relationship("Progress", back_populates="job", cascade="all, delete-orphan")

    # PUBLIC_INTERFACE
    @staticmethod
    def new(status: str = "pending", phase: Optional[str] = None, percent: int = 0) -> "Job":
        """Factory to create a new Job instance with defaults."""
        return Job(status=status, phase=phase, percent=percent)
