"""Phase 3.9 reliability, concurrency, and topic-quality regression tests."""

import asyncio
import json
from unittest.mock import patch

import httpx
import pytest
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.db.models.interview_session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.integrations.llm.base import LLMProvider
from app.main import app
from app.modules.interview.router import service as interview_service
from app.modules.interview.topic_selector import select_topic_with_focus
from app.modules.reports.service import ReportService


class _CountingMockLLM(LLMProvider):
    def __init__(self, delay_s: float = 0.05) -> None:
        self.delay_s = delay_s
        self.eval_calls = 0

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        await asyncio.sleep(self.delay_s)
        if "Evaluate the candidate's interview answer" in prompt:
            self.eval_calls += 1
            return json.dumps({
                "score": 8.0,
                "relevance": 8.0,
                "clarity": 8.0,
                "technical_depth": 8.0,
                "strengths": ["Clear answer"],
                "weaknesses": [],
                "missing_concepts": [],
                "feedback": "Good explanation.",
                "needs_follow_up": False,
            })
        return json.dumps({
            "question_text": "What is the difference between a process and a thread?",
            "expected_concepts": ["memory space", "concurrency"],
            "follow_up_hint": "Ask about context switching.",
        })


@pytest.fixture()
def isolated_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        User.__table__,
        Resume.__table__,
        ResumeAnalysis.__table__,
        InterviewSession.__table__,
        InterviewTurn.__table__,
        InterviewReport.__table__,
    ]
    for t in tables:
        t.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    db = SessionLocal()
    user = User(email="race@example.com", password_hash="hashed")
    db.add(user)
    db.commit()
    db.refresh(user)

    resume = Resume(
        user_id=user.id,
        filename="resume.pdf",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    analysis = ResumeAnalysis(
        resume_id=resume.id,
        job_role="Backend Developer",
        job_description="FastAPI SQL",
        result_json={
            "match_score": 82.0,
            "resume_skills": ["Python", "FastAPI", "SQL"],
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Redis"],
            "strengths": ["Good Python skills"],
            "improvement_suggestions": ["Practice caching"],
        },
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    yield SessionLocal, user.id, analysis.id

    for t in reversed(tables):
        t.drop(bind=engine)


def test_concurrent_submit_answer_returns_409_and_runs_llm_once(isolated_db):
    async def _run():
        SessionLocal, user_id, analysis_id = isolated_db
        mock_llm = _CountingMockLLM(delay_s=0.05)

        orig_llm = interview_service.llm_provider
        orig_cp = interview_service.checkpointer
        interview_service.llm_provider = mock_llm
        interview_service.checkpointer = MemorySaver()

        def override_db():
            s = SessionLocal()
            try:
                yield s
            finally:
                s.close()

        def override_user():
            s = SessionLocal()
            u = s.get(User, user_id)
            s.close()
            return u

        app.dependency_overrides[get_db] = override_db
        app.dependency_overrides[get_current_user] = override_user

        try:
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                start_resp = await client.post(
                    "/interview/start",
                    json={
                        "analysis_id": analysis_id,
                        "max_questions": 2,
                        "experience_level": "fresher",
                    },
                )
                assert start_resp.status_code == 201
                session_data = start_resp.json()
                session_id = session_data["session_id"]
                question_id = session_data["current_question"]["question_id"]

                r1, r2 = await asyncio.gather(
                    client.post(
                        f"/interview/{session_id}/answer",
                        json={"question_id": question_id, "answer": "Processes have isolated memory while threads share memory."},
                    ),
                    client.post(
                        f"/interview/{session_id}/answer",
                        json={"question_id": question_id, "answer": "Processes have isolated memory while threads share memory."},
                    ),
                )
                statuses = sorted([r1.status_code, r2.status_code])
                assert statuses == [200, 409]
                assert mock_llm.eval_calls == 1
        finally:
            app.dependency_overrides.clear()
            interview_service.llm_provider = orig_llm
            interview_service.checkpointer = orig_cp

    asyncio.run(_run())


def test_topic_selector_never_emits_literal_resume_project():
    topic, qtype, focus = select_topic_with_focus(
        candidate_context={
            "target_role": "Backend Developer",
            "resume_skills": ["Python", "FastAPI"],
            "matched_skills": ["Python"],
            "missing_skills": ["Redis"],
            "projects": [],
        },
        asked_topics=[],
        question_index=10,
        max_questions=10,
    )
    assert topic != "Resume Project"
    assert "resume project" not in topic.lower()


def test_concurrent_report_generation_handles_integrity_error(isolated_db):
    SessionLocal, user_id, analysis_id = isolated_db
    db = SessionLocal()
    session = InterviewSession(
        id="report-race-session-1",
        user_id=user_id,
        resume_analysis_id=analysis_id,
        target_role="Backend Developer",
        status="completed",
        max_questions=1,
        question_index=1,
        configuration={"experience_level": "fresher"},
        graph_state={},
    )
    db.add(session)
    db.add(
        InterviewTurn(
            session_id="report-race-session-1",
            question_index=1,
            question_id="q1",
            topic="REST APIs",
            difficulty="easy",
            question_type="conceptual",
            question_text="What is REST?",
            answer_text="REST is an architectural style using stateless HTTP requests.",
            evaluation={
                "score": 8.0,
                "relevance": 8.0,
                "clarity": 8.0,
                "technical_depth": 8.0,
                "strengths": ["Clear"],
                "weaknesses": [],
                "missing_concepts": [],
                "feedback": "Good.",
            },
        )
    )
    db.commit()

    # Pre-insert report in a separate session on IntegrityError simulation
    def insert_competing_report():
        s2 = SessionLocal()
        s2.add(
            InterviewReport(
                session_id="report-race-session-1",
                user_id=user_id,
                target_role="Backend Developer",
                overall_score=8.0,
                dimension_scores={
                    "relevance": {"dimension": "relevance", "label": "Relevance", "score": 8.0, "weight": 0.3, "evaluated_count": 1},
                    "clarity": {"dimension": "clarity", "label": "Clarity", "score": 8.0, "weight": 0.25, "evaluated_count": 1},
                    "technical_depth": {"dimension": "technical_depth", "label": "Technical Depth", "score": 8.0, "weight": 0.45, "evaluated_count": 1},
                },
                topic_scores=[{"topic": "REST APIs", "average_score": 8.0, "questions_asked": 1, "evaluated_questions": 1}],
                strengths=["Clear"],
                weaknesses=[],
                missing_concepts=[],
                recommendations=[],
                question_feedback=[],
                completion_stats={
                    "questions_answered": 1,
                    "primary_questions_completed": 1,
                    "follow_ups_answered": 0,
                    "total_primary_questions": 1,
                },
                evaluation_coverage={
                    "evaluated_count": 1,
                    "unavailable_count": 0,
                    "total_answered": 1,
                    "coverage_ratio": 1.0,
                    "is_partial": False,
                },
                rubric_version="1.0",
                rubric_weights={"relevance": 0.3, "clarity": 0.25, "technical_depth": 0.45},
                status="completed",
            )
        )
        s2.commit()
        s2.close()

    orig_commit = db.commit

    def flaky_commit():
        insert_competing_report()
        raise IntegrityError("UNIQUE constraint failed", params=None, orig=Exception("dup"))

    report_svc = ReportService(llm_provider=_CountingMockLLM(delay_s=0.0))
    with patch.object(db, "commit", side_effect=flaky_commit):
        resp = asyncio.run(report_svc.generate_report(db=db, user_id=user_id, session_id="report-race-session-1"))

    assert resp.session_id == "report-race-session-1"
    assert resp.overall_score == 8.0
    db.commit = orig_commit
    db.close()
