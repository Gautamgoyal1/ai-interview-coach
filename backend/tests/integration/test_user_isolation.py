"""HTTP integration tests for resume analysis persistence and user isolation."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.user import User
from app.db.session import get_db
from app.main import app
from app.modules.resume.router import service
from app.modules.resume.schemas import ResumeAnalysisResult


@pytest.fixture
def isolated_client(monkeypatch):
    """Provide a TestClient with real SQLite persistence for auth + resume."""
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        "test-jwt-secret-key-at-least-32-bytes-long",
    )

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    User.__table__.create(bind=engine)
    Resume.__table__.create(bind=engine)
    ResumeAnalysis.__table__.create(bind=engine)

    TestingSession = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    sample_result = ResumeAnalysisResult(
        job_role="Machine Learning Engineer",
        resume_skills=["python", "scikit-learn"],
        matched_skills=["python", "scikit-learn"],
        missing_skills=["docker"],
        match_score=82.5,
        strengths=["Strong Python and ML modeling background."],
        improvement_suggestions=["Add Docker deployment experience."],
        likely_interview_questions=["How do you evaluate model drift?"],
    )
    monkeypatch.setattr(service, "analyze", AsyncMock(return_value=sample_result))

    try:
        with TestClient(app) as client:
            yield client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def _register_and_login(client: TestClient, email: str) -> dict[str, str]:
    reg = client.post(
        "/auth/register",
        json={"email": email, "password": "strongpassword123"},
    )
    assert reg.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "strongpassword123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_isolation_and_history_persistence(isolated_client: TestClient):
    """Analyses persist per user and cannot be read across accounts."""
    headers_a = _register_and_login(isolated_client, "usera@example.com")
    headers_b = _register_and_login(isolated_client, "userb@example.com")

    # Initially both users have empty history.
    assert isolated_client.get("/resume/analyses", headers=headers_a).json() == []
    assert isolated_client.get("/resume/analyses", headers=headers_b).json() == []

    # User A analyzes a resume.
    analyze_res = isolated_client.post(
        "/resume/analyze",
        headers=headers_a,
        files={"file": ("alice_cv.pdf", b"%PDF-1.4 sample", "application/pdf")},
        data={"job_role": "Machine Learning Engineer"},
    )
    assert analyze_res.status_code == 200
    assert analyze_res.json()["match_score"] == 82.5

    # User A sees it in history and can reopen it.
    history_a = isolated_client.get("/resume/analyses", headers=headers_a)
    assert history_a.status_code == 200
    items_a = history_a.json()
    assert len(items_a) == 1
    assert items_a[0]["filename"] == "alice_cv.pdf"
    assert items_a[0]["job_role"] == "Machine Learning Engineer"
    assert items_a[0]["match_score"] == 82.5

    analysis_id = items_a[0]["id"]
    detail_a = isolated_client.get(
        f"/resume/analyses/{analysis_id}",
        headers=headers_a,
    )
    assert detail_a.status_code == 200
    assert detail_a.json()["filename"] == "alice_cv.pdf"
    assert detail_a.json()["result"]["match_score"] == 82.5

    # User B does not see User A's analysis in history or by ID.
    history_b = isolated_client.get("/resume/analyses", headers=headers_b)
    assert history_b.status_code == 200
    assert history_b.json() == []

    cross_user_detail = isolated_client.get(
        f"/resume/analyses/{analysis_id}",
        headers=headers_b,
    )
    assert cross_user_detail.status_code == 404

    # Unknown analysis ID returns 404.
    unknown_detail = isolated_client.get(
        "/resume/analyses/99999",
        headers=headers_a,
    )
    assert unknown_detail.status_code == 404
