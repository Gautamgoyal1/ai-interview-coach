"""Integration tests for the LangGraph interview API, persistence, and isolation."""

import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.models.interview_session import InterviewSession
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.integrations.llm.base import LLMError
from app.main import app
from app.modules.interview.router import service as interview_service


class ScriptedInterviewLLM:
    """Deterministic mock LLM returning structured questions and evaluations."""

    def __init__(self, follow_up_first: bool = True, fail_all: bool = False):
        self.follow_up_first = follow_up_first
        self.fail_all = fail_all
        self.q_counter = 0
        self.eval_counter = 0

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        if self.fail_all:
            raise LLMError("Simulated provider outage")

        if "Evaluate the candidate's interview answer" in prompt:
            self.eval_counter += 1
            need_fu = self.follow_up_first and self.eval_counter == 1
            return json.dumps(
                {
                    "technical_correctness": {
                        "score": 3.5 if need_fu else 4.5,
                        "explanation": "Accurate core explanation.",
                    },
                    "relevance": {
                        "score": 4.0,
                        "explanation": "Directly addresses the question.",
                    },
                    "completeness": {
                        "score": 2.5 if need_fu else 4.5,
                        "explanation": "Missing pooling details." if need_fu else "Complete.",
                    },
                    "technical_depth": {
                        "score": 3.0 if need_fu else 4.5,
                        "explanation": "Appropriate depth.",
                    },
                    "strengths": ["Clear explanation"],
                    "missing_concepts": ["Connection pooling"] if need_fu else [],
                    "improvement_suggestions": ["Discuss pooling configuration"] if need_fu else [],
                    "confidence": "medium",
                    "follow_up_needed": need_fu,
                    "follow_up_reason": "Probe connection pooling" if need_fu else None,
                }
            )

        if "Generate a targeted follow-up question" in prompt:
            return json.dumps(
                {
                    "question_text": "How would you configure connection pooling for that?",
                    "difficulty": "medium",
                }
            )

        self.q_counter += 1
        return json.dumps(
            {
                "topic": "FastAPI" if self.q_counter == 1 else "PostgreSQL",
                "difficulty": "easy" if self.q_counter == 1 else "medium",
                "question_type": "applied",
                "question_text": f"Mocked question #{self.q_counter} for the role.",
            }
        )


@pytest.fixture
def interview_env(monkeypatch):
    """Set up in-memory SQLite DB with User, Resume, Analysis, and Interview tables."""
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

    llm = ScriptedInterviewLLM(follow_up_first=True)
    monkeypatch.setattr(interview_service, "llm_provider", llm)
    monkeypatch.setattr(interview_service, "checkpointer", MemorySaver())

    try:
        with TestClient(app) as client:
            yield client, TestingSession, llm
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override
        engine.dispose()


def _create_user_and_analysis(client: TestClient, SessionLocal, email: str):
    reg = client.post(
        "/auth/register",
        json={"email": email, "password": "strongpassword123"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "strongpassword123"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    db = SessionLocal()
    try:
        resume = Resume(user_id=user_id, filename="candidate.pdf")
        db.add(resume)
        db.flush()
        analysis = ResumeAnalysis(
            resume_id=resume.id,
            job_role="Backend Developer",
            result_json={
                "job_role": "Backend Developer",
                "resume_skills": ["Python", "FastAPI", "PostgreSQL"],
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Redis"],
                "match_score": 78.0,
                "strengths": ["Built REST APIs with FastAPI."],
                "improvement_suggestions": ["Add caching with Redis."],
                "likely_interview_questions": [],
            },
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        analysis_id = analysis.id
    finally:
        db.close()

    return headers, analysis_id


def test_full_interview_lifecycle_follow_ups_and_completion(interview_env):
    client, SessionLocal, _llm = interview_env
    headers_a, analysis_a = _create_user_and_analysis(
        client, SessionLocal, "cand_a@example.com"
    )
    headers_b, _ = _create_user_and_analysis(
        client, SessionLocal, "cand_b@example.com"
    )

    # Cross-user analysis access is blocked (404).
    unauth_start = client.post(
        "/interview/start",
        headers=headers_b,
        json={"analysis_id": analysis_a, "max_questions": 2, "max_follow_ups": 1},
    )
    assert unauth_start.status_code == 404

    # Start interview for User A.
    start_res = client.post(
        "/interview/start",
        headers=headers_a,
        json={"analysis_id": analysis_a, "max_questions": 2, "max_follow_ups": 1},
    )
    assert start_res.status_code == 201
    s1 = start_res.json()
    session_id = s1["session_id"]
    assert s1["status"] == "in_progress"
    assert s1["question_index"] == 1
    assert s1["current_question"]["question_id"] == "q_001"
    assert s1["current_question"]["is_follow_up"] is False

    # Empty answer rejected.
    empty_res = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={"question_id": "q_001", "answer": "   "},
    )
    assert empty_res.status_code == 422

    # Submit A1 -> triggers follow-up q_001_fu_1.
    a1_res = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={
            "question_id": "q_001",
            "answer": "FastAPI uses Depends() for dependency injection.",
        },
    )
    assert a1_res.status_code == 200
    s2 = a1_res.json()
    assert s2["status"] == "in_progress"
    assert s2["question_index"] == 1
    assert s2["follow_up_count"] == 1
    assert s2["current_question"]["question_id"] == "q_001_fu_1"
    assert s2["current_question"]["is_follow_up"] is True

    # Duplicate answer to q_001 rejected with 409 Conflict.
    dup_res = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={"question_id": "q_001", "answer": "Retry"},
    )
    assert dup_res.status_code == 409

    # Cross-user session access blocked (404) & unknown session returns 404.
    assert client.get(f"/interview/{session_id}", headers=headers_b).status_code == 404
    assert client.get("/interview/does-not-exist", headers=headers_a).status_code == 404

    # Simulate backend restart by replacing MemorySaver before follow-up answer!
    interview_service.checkpointer = MemorySaver()

    # Refresh / GET session restores exact state.
    get_res = client.get(f"/interview/{session_id}", headers=headers_a)
    assert get_res.status_code == 200
    assert get_res.json()["current_question"]["question_id"] == "q_001_fu_1"

    # Submit follow-up answer -> advances to q_002.
    fu_res = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={
            "question_id": "q_001_fu_1",
            "answer": "Use SQLAlchemy QueuePool with pool_size and max_overflow.",
        },
    )
    assert fu_res.status_code == 200
    s3 = fu_res.json()
    assert s3["status"] == "in_progress"
    assert s3["question_index"] == 2
    assert s3["follow_up_count"] == 0
    assert s3["current_question"]["question_id"] == "q_002"

    # Submit A2 -> reaches max_questions=2 -> completes interview.
    a2_res = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={
            "question_id": "q_002",
            "answer": "Inspect EXPLAIN ANALYZE and add composite B-tree indexes.",
        },
    )
    assert a2_res.status_code == 200
    s4 = a2_res.json()
    assert s4["status"] == "completed"
    assert s4["current_question"] is None
    assert len(s4["conversation_history"]) == 3
    assert all(turn["answer_text"] for turn in s4["conversation_history"])

    # Submitting to completed session returns 400.
    after_done = client.post(
        f"/interview/{session_id}/answer",
        headers=headers_a,
        json={"question_id": "q_002", "answer": "Extra"},
    )
    assert after_done.status_code == 400


def test_end_interview_and_llm_failure_fallback(interview_env):
    client, SessionLocal, llm = interview_env
    llm.fail_all = True

    headers, analysis_id = _create_user_and_analysis(
        client, SessionLocal, "fallback@example.com"
    )

    start_res = client.post(
        "/interview/start",
        headers=headers,
        json={"analysis_id": analysis_id, "max_questions": 3, "max_follow_ups": 1},
    )
    assert start_res.status_code == 201
    session_id = start_res.json()["session_id"]
    assert start_res.json()["current_question"]["question_text"]

    end_res = client.post(f"/interview/{session_id}/end", headers=headers)
    assert end_res.status_code == 200
    assert end_res.json()["status"] == "completed"
    assert end_res.json()["current_question"] is None
