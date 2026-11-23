"""Conservative endpoint reservations, not provider token or currency billing."""
from datetime import date
from sqlalchemy import CheckConstraint, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class StagingAIUsage(Base):
    __tablename__ = "staging_ai_usage"
    __table_args__ = (CheckConstraint("requests >= 0", name="ck_staging_ai_usage_nonnegative"),)
    utc_day: Mapped[date] = mapped_column(Date, primary_key=True)
    bucket: Mapped[str] = mapped_column(String(64), primary_key=True)
    requests: Mapped[int] = mapped_column(Integer, nullable=False)
