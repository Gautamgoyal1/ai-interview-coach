"""Atomic UTC daily reservations survive sleep/restart. No success refunds."""
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.db.models.staging_usage import StagingAIUsage
from app.db.session import SessionLocal


def reserve_staging_request(user_id: int) -> None:
    now = datetime.now(timezone.utc)
    tomorrow = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), timezone.utc)
    retry = max(1, int((tomorrow - now).total_seconds()) + 1)
    try:
        # Independent transaction: an endpoint rollback/crash must not refund a
        # possibly charged request. Global and user reservations commit together.
        with SessionLocal.begin() as db:
            dialect = db.bind.dialect.name
            if dialect == "postgresql":
                from sqlalchemy.dialects.postgresql import insert
            elif dialect == "sqlite":  # deterministic unit tests only
                from sqlalchemy.dialects.sqlite import insert
            else:
                raise HTTPException(503, "Staging usage control is unavailable.")
            for bucket, limit in [("global", settings.staging_ai_global_daily_limit), (f"user:{user_id}", settings.staging_ai_user_daily_limit)]:
                statement = insert(StagingAIUsage).values(utc_day=now.date(), bucket=bucket, requests=1)
                statement = statement.on_conflict_do_update(
                    index_elements=[StagingAIUsage.utc_day, StagingAIUsage.bucket],
                    set_={"requests": StagingAIUsage.requests + 1},
                    where=StagingAIUsage.requests < limit,
                ).returning(StagingAIUsage.requests)
                if db.scalar(statement) is None:
                    raise HTTPException(429, "Private staging daily usage limit reached.", headers={"Retry-After": str(retry)})
    except SQLAlchemyError:
        raise HTTPException(503, "Staging usage control is temporarily unavailable.") from None
