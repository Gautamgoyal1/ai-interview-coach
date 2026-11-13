from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

_engine_kwargs: dict[str, object] = {"pool_pre_ping": True}
if not settings.database_url.startswith("sqlite"):
    _engine_kwargs.update(
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_recycle=1800,
    )

engine = create_engine(settings.database_url, **_engine_kwargs)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()