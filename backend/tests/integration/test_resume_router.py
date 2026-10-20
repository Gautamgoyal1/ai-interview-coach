
"""HTTP endpoint tests for authenticated resume uploads, persistence, and history."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.dependencies import get_current_user
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.session import get_db
from app.main import app
from app.modules.resume.router import service
from app.modules.resume.schemas import ResumeAnalysisResult


class FakeUser:
    """Minimal authenticated user for endpoint tests."""

    id = 1
    email = "resume-test@example.com"


class FakeDB:
    """Small in-memory session fake for endpoint tests."""

    def __init__(self):
        self.added = []
        self.committed = False
        self.rolled_back = False
        self.flush_count = 0

    def add(self, instance):
        self.added.append(instance)
        if isinstance(instance, Resume):
            instance.id = 101

    def flush(self):
        self.flush_count += 1

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True


@pytest.fixture
def fake_db():
    return FakeDB()


@pytest.fixture
def authenticated_client(fake_db):
    """Override authentication and database access for each test."""

    previous_user_override = app.dependency_overrides.get(
        get_current_user
    )
    previous_db_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_current_user] = lambda: FakeUser()
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_user_override is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = (
                previous_user_override
            )

        if previous_db_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_db_override


@pytest.fixture
def mock_analysis(monkeypatch):
    """Mock the analysis service to avoid real LLM/API calls."""

    result = ResumeAnalysisResult(
        job_role="Machine Learning Engineer",
        resume_skills=["python"],
        matched_skills=["python"],
        missing_skills=[],
        match_score=100.0,
        strengths=["Python experience is demonstrated."],
        improvement_suggestions=[],
        likely_interview_questions=[],
    )

    mock = AsyncMock(return_value=result)
    monkeypatch.setattr(service, "analyze", mock)
    return mock


def test_rejects_unauthenticated_request():
    """The endpoint must reject requests without authentication."""

    with TestClient(app) as client:
        response = client.post(
            "/resume/analyze",
            files={
                "file": (
                    "resume.pdf",
                    b"%PDF-1.4",
                    "application/pdf",
                )
            },
            data={"job_role": "Machine Learning Engineer"},
        )

    assert response.status_code == 401


def test_rejects_non_pdf_content_type(authenticated_client):
    response = authenticated_client.post(
        "/resume/analyze",
        files={"file": ("resume.txt", b"hello", "text/plain")},
        data={"job_role": "Machine Learning Engineer"},
    )

    assert response.status_code == 415
    assert response.json()["detail"] == "Please upload a PDF file."


def test_rejects_invalid_pdf_signature(
    authenticated_client,
    mock_analysis,
    fake_db,
):
    response = authenticated_client.post(
        "/resume/analyze",
        files={
            "file": (
                "resume.pdf",
                b"This is not a PDF file",
                "application/pdf",
            )
        },
        data={"job_role": "Machine Learning Engineer"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "The uploaded file is not a valid PDF."
    )
    mock_analysis.assert_not_awaited()
    assert fake_db.added == []


def test_rejects_oversized_pdf(
    authenticated_client,
    mock_analysis,
    fake_db,
):
    oversized_content = b"%PDF-1.4\n" + (
        b"A" * (10 * 1024 * 1024)
    )

    response = authenticated_client.post(
        "/resume/analyze",
        files={
            "file": (
                "large.pdf",
                oversized_content,
                "application/pdf",
            )
        },
        data={"job_role": "Machine Learning Engineer"},
    )

    assert response.status_code == 413
    assert response.json()["detail"] == (
        "Resume PDF must be 10 MB or smaller."
    )
    mock_analysis.assert_not_awaited()
    assert fake_db.added == []


def test_valid_pdf_saves_resume_and_analysis(
    authenticated_client,
    mock_analysis,
    fake_db,
):
    pdf_content = b"%PDF-1.4\nMock PDF content"

    response = authenticated_client.post(
        "/resume/analyze",
        files={
            "file": (
                "resume.pdf",
                pdf_content,
                "application/pdf",
            )
        },
        data={
            "job_role": "Machine Learning Engineer",
            "job_description": "Python and machine learning experience",
        },
    )

    assert response.status_code == 200
    assert response.json()["job_role"] == "Machine Learning Engineer"
    assert response.json()["match_score"] == 100.0
    mock_analysis.assert_awaited_once()

    saved_resumes = [
        item for item in fake_db.added
        if isinstance(item, Resume)
    ]
    saved_analyses = [
        item for item in fake_db.added
        if isinstance(item, ResumeAnalysis)
    ]

    assert len(saved_resumes) == 1
    assert saved_resumes[0].user_id == FakeUser.id
    assert saved_resumes[0].filename == "resume.pdf"

    assert len(saved_analyses) == 1
    assert saved_analyses[0].resume_id == saved_resumes[0].id
    assert saved_analyses[0].job_role == "Machine Learning Engineer"
    assert (
        saved_analyses[0].job_description
        == "Python and machine learning experience"
    )
    assert saved_analyses[0].result_json["match_score"] == 100.0

    assert fake_db.flush_count == 1
    assert fake_db.committed is True
    assert fake_db.rolled_back is False


def test_database_failure_rolls_back(
    authenticated_client,
    mock_analysis,
    fake_db,
    monkeypatch,
):
    def fail_commit():
        raise SQLAlchemyError("simulated database failure")

    monkeypatch.setattr(fake_db, "commit", fail_commit)

    response = authenticated_client.post(
        "/resume/analyze",
        files={
            "file": (
                "resume.pdf",
                b"%PDF-1.4\nMock PDF content",
                "application/pdf",
            )
        },
        data={"job_role": "Machine Learning Engineer"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "The resume analysis could not be saved. Please retry."
    )
    assert fake_db.rolled_back is True


def configure_history_query(fake_db, records):
    """Configure a mock SQLAlchemy query chain for history endpoints."""

    query = MagicMock()
    query.join.return_value = query
    query.filter.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.all.return_value = records
    query.first.return_value = records[0] if records else None
    fake_db.query = MagicMock(return_value=query)
    return query


def test_lists_current_users_resume_history(
    authenticated_client,
    fake_db,
):
    created_at = datetime.now(timezone.utc)
    analysis = SimpleNamespace(
        id=7,
        job_role="AI Engineer",
        created_at=created_at,
        result_json={"match_score": 82.5},
    )
    resume = SimpleNamespace(
        filename="resume.pdf",
        user_id=FakeUser.id,
    )
    query = configure_history_query(fake_db, [(analysis, resume)])

    response = authenticated_client.get("/resume/analyses")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == 7
    assert body[0]["filename"] == "resume.pdf"
    assert body[0]["job_role"] == "AI Engineer"
    assert body[0]["match_score"] == 82.5
    query.filter.assert_called_once()


def test_history_respects_limit(
    authenticated_client,
    fake_db,
):
    query = configure_history_query(fake_db, [])

    response = authenticated_client.get("/resume/analyses?limit=5")

    assert response.status_code == 200
    assert response.json() == []
    query.limit.assert_called_once_with(5)


def test_rejects_invalid_history_limit(authenticated_client):
    response = authenticated_client.get("/resume/analyses?limit=101")

    assert response.status_code == 422


def test_returns_saved_analysis_details(
    authenticated_client,
    fake_db,
):
    created_at = datetime.now(timezone.utc)
    result = {
        "job_role": "AI Engineer",
        "resume_skills": ["python"],
        "matched_skills": ["python"],
        "missing_skills": [],
        "match_score": 82.5,
        "strengths": ["Strong Python foundation."],
        "improvement_suggestions": [],
        "likely_interview_questions": [],
    }
    analysis = SimpleNamespace(
        id=7,
        created_at=created_at,
        result_json=result,
    )
    resume = SimpleNamespace(
        filename="resume.pdf",
        user_id=FakeUser.id,
    )
    query = configure_history_query(fake_db, [(analysis, resume)])

    response = authenticated_client.get("/resume/analyses/7")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == 7
    assert body["filename"] == "resume.pdf"
    assert body["result"]["job_role"] == "AI Engineer"
    assert body["result"]["match_score"] == 82.5
    query.filter.assert_called_once()


def test_returns_404_when_analysis_is_missing_or_not_owned(
    authenticated_client,
    fake_db,
):
    query = configure_history_query(fake_db, [])

    response = authenticated_client.get("/resume/analyses/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Resume analysis not found."
    query.filter.assert_called_once()


def test_history_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/resume/analyses")

    assert response.status_code == 401


def test_analysis_detail_requires_authentication():
    with TestClient(app) as client:
        response = client.get("/resume/analyses/1")

    assert response.status_code == 401
