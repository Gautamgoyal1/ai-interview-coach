
"""Database models for uploaded resumes and their analyses."""

from datetime import datetime
import uuid

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    analyses: Mapped[list["ResumeAnalysis"]] = relationship(
        back_populates="resume",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"
    __table_args__ = (
        Index(
            "uq_resume_analyses_active_fingerprint",
            "user_id",
            "analysis_fingerprint",
            unique=True,
            postgresql_where=text(
                "deleted_at IS NULL AND status IN ('processing', 'completed')"
            ),
            sqlite_where=text(
                "deleted_at IS NULL AND status IN ('processing', 'completed')"
            ),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    job_role: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    job_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    resume_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex,
    )

    analysis_fingerprint: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        default=lambda: uuid.uuid4().hex,
    )

    status: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
        default="completed",
        server_default="completed",
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
    )

    result_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    resume: Mapped["Resume"] = relationship(
        back_populates="analyses",
    )
