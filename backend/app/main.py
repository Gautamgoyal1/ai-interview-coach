from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.security import validate_jwt_configuration
from app.core.config import settings
from app.core.body_limit import RequestBodyLimitMiddleware
from app.core.response_headers import ResponseHeadersMiddleware
from app.db.session import engine
from app.modules.auth.router import router as auth_router
from app.modules.interview.router import router as interview_router
from app.modules.practice.router import router as practice_router
from app.modules.reports.router import router as reports_router
from app.modules.resume.router import router as resume_router
from app.modules.speech.router import router as speech_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_jwt_configuration()
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    title="AI Interview Coach",
    lifespan=lifespan,
    docs_url=None if settings.app_env == "production" else "/docs",
    redoc_url=None if settings.app_env == "production" else "/redoc",
    openapi_url=None if settings.app_env == "production" else "/openapi.json",
)

app.add_middleware(RequestBodyLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,  # Authentication uses an explicit Bearer header, not cookies.
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ResponseHeadersMiddleware, production=settings.app_env == "production")

app.include_router(auth_router)
app.include_router(resume_router)
app.include_router(interview_router)
app.include_router(reports_router)
app.include_router(practice_router)
app.include_router(speech_router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/ready")
def readiness():
    """Database/schema/vector readiness, without provider calls or private data."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            ready = connection.execute(text(
                "SELECT to_regclass('public.users') IS NOT NULL "
                "AND to_regclass('public.chunks') IS NOT NULL "
                "AND to_regclass('public.alembic_version') IS NOT NULL "
                "AND EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            )).scalar()
            if not ready:
                raise HTTPException(503, "Database initialization is incomplete.")
            if settings.staging_enabled and not connection.execute(text(
                "SELECT to_regclass('public.staging_ai_usage') IS NOT NULL"
            )).scalar():
                raise HTTPException(503, "Staging usage initialization is incomplete.")
    except SQLAlchemyError:
        raise HTTPException(503, "Database is temporarily unavailable.") from None
    return {"status": "ready"}
