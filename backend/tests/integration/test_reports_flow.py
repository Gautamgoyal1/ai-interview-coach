"""Integration tests for interview report generation, persistence, and isolation."""

import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.models.interview_session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.integrations.llm.base import LLMError
from app.main import app
from app.modules.interview.grader import grade_interview_answer
from app.modules.reports.router import service as report_service


class MockReportLLM:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.calls = 0

    async def generate(
        self, prompt: str, system: str | None = None, json_mode: bool = False
    ) -> str:
        self.calls += 1
        if self.fail:
            raise LLMError("Simulated report LLM failure")
        return json.dumps(
            {
                "recommendations": [
                    {
                        "area": "PostgreSQL Indexing",
                        "observed_gap": "Missed EXPLAIN ANALYZE details.",
                        "action": "Practice reading EXPLAIN ANALYZE plans on composite indexes.",
                        "priority": "high",
                    }
                ]
            }
        )


@pytest.fixture
def report_env(monkeypatch):
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
    InterviewSession.__table__.create(bind=engine)
    InterviewTurn.__table__.create(bind=engine)
    InterviewReport.__table__.create(bind=engine)

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

    llm = MockReportLLM()
    monkeypatch.setattr(report_service, "llm_provider", llm)

    try:
        with TestClient(app) as client:
            yield client, TestingSession, llm
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def _seed_user_and_session(
    client: TestClient,
    SessionLocal,
    email: str,
    status: str = "completed",
    partial_eval: bool = False,
):
    reg = client.post(
        "/auth/register",
        json={"email": email, "password": "strongpassword123"},
    )
    user_id = reg.json()["id"]
    login = client.post(
        "/auth/login",
        json={"email": email, "password": "strongpassword123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    db = SessionLocal()
    try:
        resume = Resume(user_id=user_id, filename="cv.pdf")
        db.add(resume)
        db.flush()
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            job_role="Backend Developer",
            result_json={"job_role": "Backend Developer"},
        )
        db.add(analysis)
        db.flush()
        sess = InterviewSession(
            id=f"sess-{user_id}-{status}",
            user_id=user_id,
            resume_analysis_id=analysis.id,
            target_role="Backend Developer",
            status=status,
            question_index=2,
            max_questions=2,
            follow_up_count=0,
            max_follow_ups=1,
            configuration={},
            graph_state={},
            completed_at=datetime.now(timezone.utc) if status == "completed" else None,
        )
        db.add(sess)
        db.flush()

        db.add(
            InterviewTurn(
                session_id=sess.id,
                question_id="q_001",
                question_index=1,
                is_follow_up=False,
                topic="PostgreSQL",
                difficulty="medium",
                question_type="applied",
                question_text="How do you optimize slow PostgreSQL queries?",
                rag_sources=[],
                answer_text="Add an index.",
                evaluation={
                    "technical_correctness": {"score": 2.0, "explanation": "Basic."},
                    "relevance": {"score": 4.0, "explanation": "On topic."},
                    "completeness": {"score": 2.0, "explanation": "Missed EXPLAIN ANALYZE."},
                    "technical_depth": {"score": 2.0, "explanation": "Shallow."},
                    "strengths": ["Mentioned indexes"],
                    "missing_concepts": ["EXPLAIN ANALYZE"],
                    "improvement_suggestions": ["Inspect execution plans."],
                    "grading_status": "completed",
                },
                answered_at=datetime.now(timezone.utc),
            )
        )
        db.add(
            InterviewTurn(
                session_id=sess.id,
                question_id="q_002",
                question_index=2,
                is_follow_up=False,
                topic="FastAPI",
                difficulty="easy",
                question_type="conceptual",
                question_text="Explain Depends() in FastAPI.",
                rag_sources=[],
                answer_text="Depends() injects shared dependencies per request.",
                evaluation=(
                    {"grading_status": "unavailable", "overall_score": None}
                    if partial_eval
                    else {
                        "technical_correctness": {"score": 5.0, "explanation": "Exact."},
                        "relevance": {"score": 5.0, "explanation": "Direct."},
                        "completeness": {"score": 4.0, "explanation": "Solid."},
                        "technical_depth": {"score": 4.0, "explanation": "Good."},
                        "strengths": ["Clear dependency injection explanation"],
                        "missing_concepts": [],
                        "improvement_suggestions": [],
                        "grading_status": "completed",
                    }
                ),
                answered_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        return headers, sess.id
    finally:
        db.close()


def test_report_generation_idempotency_and_user_isolation(report_env):
    client, SessionLocal, llm = report_env
    headers_a, sess_completed = _seed_user_and_session(
        client, SessionLocal, "rep_a@example.com", status="completed"
    )
    _, sess_active = _seed_user_and_session(
        client, SessionLocal, "rep_active@example.com", status="in_progress"
    )
    headers_b, _ = _seed_user_and_session(
        client, SessionLocal, "rep_b@example.com", status="completed"
    )

    # Reject generation for active interview.
    active_headers, _ = _seed_user_and_session(
        client, SessionLocal, "rep_active2@example.com", status="in_progress"
    )
    assert active_headers
    # Use user_a's own active session instead:
    db = SessionLocal()
    try:
        db.query(InterviewSession).filter(
            InterviewSession.id == sess_active
        ).update({"user_id": 1})
        db.commit()
    finally:
        db.close()

    assert (
        client.post(
            f"/reports/interviews/{sess_active}/generate",
            headers=headers_a,
        ).status_code
        == 400
    )

    # Generate report for completed interview.
    gen_res = client.post(
        f"/reports/interviews/{sess_completed}/generate",
        headers=headers_a,
    )
    assert gen_res.status_code == 200
    rep = gen_res.json()
    assert rep["status"] == "completed"
    assert rep["rubric_version"] == "v1.0"
    assert rep["overall_score"] is not None
    assert len(rep["topic_scores"]) == 2
    assert len(rep["recommendations"]) == 1
    assert llm.calls == 1

    # Idempotent retry does not invoke LLM again.
    gen_res_2 = client.post(
        f"/reports/interviews/{sess_completed}/generate",
        headers=headers_a,
    )
    assert gen_res_2.status_code == 200
    assert gen_res_2.json()["id"] == rep["id"]
    assert llm.calls == 1

    # GET & list reports work for User A.
    assert (
        client.get(
            f"/reports/interviews/{sess_completed}", headers=headers_a
        ).status_code
        == 200
    )
    list_a = client.get("/reports", headers=headers_a).json()
    assert len(list_a) == 1
    assert list_a[0]["session_id"] == sess_completed

    # Cross-user isolation & missing session -> 404.
    assert (
        client.get(
            f"/reports/interviews/{sess_completed}", headers=headers_b
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/reports/interviews/{sess_completed}/generate", headers=headers_b
        ).status_code
        == 404
    )
    assert (
        client.get("/reports/interviews/missing-id", headers=headers_a).status_code
        == 404
    )


def test_partial_report_and_recommendation_fallback_on_llm_failure(report_env):
    client, SessionLocal, llm = report_env
    llm.fail = True

    headers, sess_partial = _seed_user_and_session(
        client,
        SessionLocal,
        "partial@example.com",
        status="completed",
        partial_eval=True,
    )

    res = client.post(
        f"/reports/interviews/{sess_partial}/generate",
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "partial"
    assert data["evaluation_coverage"]["is_partial"] is True
    assert data["evaluation_coverage"]["unavailable_count"] == 1
    assert len(data["recommendations"]) >= 1


def test_grader_failure_never_fabricates_positive_score():
    import anyio

    class BrokenLLM:
        async def generate(self, prompt, system=None, json_mode=False):
            raise LLMError("outage")

    async def scenario():
        ev = await grade_interview_answer(
            provider=BrokenLLM(),
            target_role="Backend Developer",
            topic="PostgreSQL",
            difficulty="medium",
            question_text="Explain MVCC.",
            answer_text="MVCC keeps multiple row versions so readers do not block writers.",
            retrieved_context="",
        )
        assert ev.grading_status == "unavailable"
        assert ev.overall_score is None
        assert ev.technical_correctness is None

    anyio.run(scenario)
