from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.db import Base


class File(Base):
    """Represents a file uploaded for a job."""

    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), index=True)

    name: Mapped[str] = mapped_column(String(255))
    ext: Mapped[str] = mapped_column(String(32))
    type: Mapped[str] = mapped_column(String(64))  # e.g., input, template, image
    path: Mapped[str] = mapped_column(String(1024))  # absolute or container path
    size: Mapped[int] = mapped_column(BigInteger, default=0)

    job = relationship("Job", back_populates="files")
