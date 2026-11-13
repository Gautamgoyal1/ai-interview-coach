"""Deterministic tests for Phase 3.5 Adaptive AI Interview Intelligence."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import anyio
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.user import User
from app.modules.interview.adaptive import (
    compute_adaptive_update,
    difficulty_for_next_topic,
    plan_follow_up,
    starting_difficulty_for_level,
)
from app.modules.interview.deduplication import (
    compute_question_fingerprint,
    is_duplicate_or_paraphrase,
)
from app.modules.interview.graph import build_interview_graph
from app.modules.interview.nodes import InterviewNodes
from app.modules.interview.repository import list_recent_user_questions
from app.modules.interview.schemas import StartInterviewRequest, SubmitAnswerRequest
from app.modules.interview.service import InterviewService
from app.modules.reports.service import ReportService


def _make_sqlite_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_starting_difficulty_by_experience_level():
    assert starting_difficulty_for_level("internship") == "easy"
    assert starting_difficulty_for_level("fresher") == "medium"
    assert starting_difficulty_for_level("intermediate") == "medium"
    assert starting_difficulty_for_level("experienced") == "medium"


def test_strong_answers_require_two_consecutive_before_increasing_and_respect_ceiling():
    # First strong answer (90): maintain medium, streak=1
    u1 = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation={"grading_status": "completed", "overall_score": 90.0},
        recent_scores=[],
        consecutive_strong_answers=0,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Python",
    )
    assert u1["next_difficulty"] == "medium"
    assert u1["consecutive_strong_answers"] == 1

    # Second consecutive strong answer (92): advance medium -> hard
    u2 = compute_adaptive_update(
        current_difficulty=u1["next_difficulty"],
        experience_level="fresher",
        evaluation={"grading_status": "completed", "overall_score": 92.0},
        recent_scores=u1["recent_scores"],
        consecutive_strong_answers=u1["consecutive_strong_answers"],
        consecutive_weak_answers=u1["consecutive_weak_answers"],
        topic_performance=u1["topic_performance"],
        topic="APIs",
    )
    assert u2["next_difficulty"] == "hard"

    # Internship ceiling caps at medium even after 2 strong answers
    intern_u1 = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="internship",
        evaluation={"grading_status": "completed", "overall_score": 95.0},
        recent_scores=[90.0],
        consecutive_strong_answers=1,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Python",
    )
    assert intern_u1["next_difficulty"] == "medium"


def test_weak_and_medium_answers_and_floor_boundary():
    # Medium score (72): maintain difficulty
    med = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation={"grading_status": "completed", "overall_score": 72.0},
        recent_scores=[],
        consecutive_strong_answers=1,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="SQL",
    )
    assert med["next_difficulty"] == "medium"
    assert med["consecutive_strong_answers"] == 0

    # Weak score (25): decrease medium -> easy
    weak = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation={"grading_status": "completed", "overall_score": 25.0},
        recent_scores=[],
        consecutive_strong_answers=0,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="SQL",
    )
    assert weak["next_difficulty"] == "easy"

    # Floor boundary: easy never drops below easy
    floor = compute_adaptive_update(
        current_difficulty="easy",
        experience_level="fresher",
        evaluation={"grading_status": "completed", "overall_score": 15.0},
        recent_scores=[25.0],
        consecutive_strong_answers=0,
        consecutive_weak_answers=1,
        topic_performance={},
        topic="SQL",
    )
    assert floor["next_difficulty"] == "easy"


def test_unavailable_grading_preserves_difficulty():
    res = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation={"grading_status": "unavailable", "overall_score": None},
        recent_scores=[80.0],
        consecutive_strong_answers=1,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Docker",
    )
    assert res["next_difficulty"] == "medium"
    assert res["recent_scores"] == [80.0]
    assert res["consecutive_strong_answers"] == 1


def test_intelligent_follow_up_decisions_and_limits():
    # Clarification for partial answer
    fu1, t1, _ = plan_follow_up(
        evaluation={
            "grading_status": "completed",
            "overall_score": 60.0,
            "technical_correctness": {"score": 3.0},
            "completeness": {"score": 2.5},
            "missing_concepts": ["B-tree lookup"],
            "follow_up_needed": True,
        },
        follow_up_count=0,
        max_follow_ups=1,
        question_type="conceptual",
        current_difficulty="medium",
    )
    assert fu1 is True
    assert t1 == "clarification"

    # Deeper exploration for strong answer
    fu2, t2, _ = plan_follow_up(
        evaluation={
            "grading_status": "completed",
            "overall_score": 90.0,
            "technical_correctness": {"score": 4.5},
            "completeness": {"score": 4.5},
            "missing_concepts": [],
            "follow_up_needed": True,
        },
        follow_up_count=0,
        max_follow_ups=1,
        question_type="conceptual",
        current_difficulty="medium",
    )
    assert fu2 is True
    assert t2 == "deeper_exploration"

    # Limit enforced
    fu_limit, _, _ = plan_follow_up(
        evaluation={"grading_status": "completed", "overall_score": 40.0},
        follow_up_count=1,
        max_follow_ups=1,
        question_type="conceptual",
        current_difficulty="medium",
    )
    assert fu_limit is False


def test_exact_and_paraphrased_question_deduplication():
    prev = ["Explain SQL joins."]
    fp = [compute_question_fingerprint("SQL", "Explain SQL joins.")]

    dup1, _ = is_duplicate_or_paraphrase("Explain SQL joins.", "SQL", prev, fp)
    dup2, _ = is_duplicate_or_paraphrase(
        "What do you understand by SQL joins?", "SQL", prev, fp
    )
    dup3, _ = is_duplicate_or_paraphrase(
        "Can you describe SQL joins?", "SQL", prev, fp
    )
    distinct, _ = is_duplicate_or_paraphrase(
        "When would you use a LEFT JOIN instead of an INNER JOIN?", "SQL", prev, fp
    )

    assert dup1 is True
    assert dup2 is True
    assert dup3 is True
    assert distinct is False


def test_cross_session_deduplication_and_user_isolation():
    SessionLocal = _make_sqlite_db()
    with SessionLocal() as db:
        u1 = User(email="u1@example.com", password_hash="x")
        u2 = User(email="u2@example.com", password_hash="x")
        db.add_all([u1, u2])
        db.flush()

        r1 = Resume(user_id=u1.id, filename="r1.pdf")
        r2 = Resume(user_id=u2.id, filename="r2.pdf")
        db.add_all([r1, r2])
        db.flush()

        a1 = ResumeAnalysis(
            resume_id=r1.id,
            job_role="Python Developer",
            result_json={
                "resume_skills": ["Python", "SQL"],
                "matched_skills": ["Python"],
                "missing_skills": ["Docker"],
                "strengths": [],
                "improvement_suggestions": [],
            },
        )
        a2 = ResumeAnalysis(
            resume_id=r2.id,
            job_role="Python Developer",
            result_json={
                "resume_skills": ["Python"],
                "matched_skills": ["Python"],
                "missing_skills": [],
                "strengths": [],
                "improvement_suggestions": [],
            },
        )
        db.add_all([a1, a2])
        db.commit()

        async def scenario():
            svc = InterviewService(llm_provider=None, checkpointer=MemorySaver())
            s1 = await svc.start_interview(
                db, u1.id, StartInterviewRequest(analysis_id=a1.id, max_questions=3, max_follow_ups=0)
            )
            q1_text = s1.current_question.question_text

            # Second session for u1 should NOT repeat s1's question
            s2 = await svc.start_interview(
                db, u1.id, StartInterviewRequest(analysis_id=a1.id, max_questions=3, max_follow_ups=0)
            )
            assert s2.current_question.question_text != q1_text

            # User isolation: u2's recent questions must not include u1's questions
            u2_recent = list_recent_user_questions(db, u2.id, target_role="Python Developer")
            assert u2_recent == []

        anyio.run(scenario)


def test_older_session_compatibility_and_restart_recovery_and_report():
    SessionLocal = _make_sqlite_db()
    with SessionLocal() as db:
        u = User(email="legacy@example.com", password_hash="x")
        db.add(u)
        db.flush()
        r = Resume(user_id=u.id, filename="r.pdf")
        db.add(r)
        db.flush()
        a = ResumeAnalysis(
            resume_id=r.id,
            job_role="Backend Developer",
            result_json={
                "resume_skills": ["Python", "REST APIs"],
                "matched_skills": ["Python"],
                "missing_skills": ["Redis"],
                "strengths": [],
                "improvement_suggestions": [],
            },
        )
        db.add(a)
        db.commit()

        async def scenario():
            # Older state missing all Phase 3.5 adaptive keys
            nodes = InterviewNodes(db=None, llm_provider=None)
            legacy_state = {
                "session_id": "legacy-1",
                "user_id": u.id,
                "analysis_id": a.id,
                "target_role": "Backend Developer",
                "candidate_context": {},
            }
            initialized = await nodes.load_candidate_context(legacy_state)  # type: ignore[arg-type]
            assert initialized["current_difficulty"] == "medium"
            assert initialized["recent_scores"] == []
            assert initialized["topic_performance"] == {}

            # Backend restart recovery with fresh MemorySaver
            svc1 = InterviewService(llm_provider=None, checkpointer=MemorySaver())
            s = await svc1.start_interview(
                db, u.id, StartInterviewRequest(analysis_id=a.id, max_questions=2, max_follow_ups=0)
            )
            svc2 = InterviewService(llm_provider=None, checkpointer=MemorySaver())
            s_after_1 = await svc2.submit_answer(
                db,
                u.id,
                s.session_id,
                SubmitAnswerRequest(
                    question_id=s.current_question.question_id,
                    answer="REST uses stateless HTTP verbs and resource URLs.",
                ),
            )
            assert s_after_1.question_index == 2
            s_done = await svc2.submit_answer(
                db,
                u.id,
                s.session_id,
                SubmitAnswerRequest(
                    question_id=s_after_1.current_question.question_id,
                    answer="Python uses reference counting and cyclic GC.",
                ),
            )
            assert s_done.status == "completed"

            # Report compatibility
            report = await ReportService(llm_provider=None).generate_report(db, u.id, s.session_id)
            assert report.session_id == s.session_id
            assert report.completion_stats.questions_answered == 2

        anyio.run(scenario)


def test_simulated_candidates_strong_weak_and_mixed():
    """Verify adaptive difficulty trajectories for Strong, Struggling, and Mixed candidates."""
    # Candidate A: Strong Performer -> medium -> medium -> hard
    d = "medium"
    scores: list[float] = []
    strong_streak = 0
    weak_streak = 0
    t_perf: dict = {}
    for topic, sc in [("Python", 90.0), ("APIs", 88.0), ("Databases", 92.0)]:
        upd = compute_adaptive_update(
            current_difficulty=d,
            experience_level="fresher",
            evaluation={"grading_status": "completed", "overall_score": sc},
            recent_scores=scores,
            consecutive_strong_answers=strong_streak,
            consecutive_weak_answers=weak_streak,
            topic_performance=t_perf,
            topic=topic,
        )
        d = upd["next_difficulty"]
        scores = upd["recent_scores"]
        strong_streak = upd["consecutive_strong_answers"]
        weak_streak = upd["consecutive_weak_answers"]
        t_perf = upd["topic_performance"]
    assert d == "hard"

    # Candidate B: Struggling Performer -> medium -> easy -> stays easy
    d_b = "medium"
    for topic, sc in [("Python", 30.0), ("APIs", 25.0)]:
        upd_b = compute_adaptive_update(
            current_difficulty=d_b,
            experience_level="fresher",
            evaluation={"grading_status": "completed", "overall_score": sc},
            recent_scores=[],
            consecutive_strong_answers=0,
            consecutive_weak_answers=0,
            topic_performance={},
            topic=topic,
        )
        d_b = upd_b["next_difficulty"]
    assert d_b == "easy"

    # Candidate C: Mixed Performer (strong Python 90, 88; weak SQL 30) -> next Python stays >= medium
    next_py_diff = difficulty_for_next_topic(
        global_difficulty="easy",
        next_topic="Python",
        last_topic="SQL",
        consecutive_weak_answers=1,
        recent_scores=[90.0, 88.0, 30.0],
        topic_performance={"python": {"avg_score": 89.0}, "sql": {"avg_score": 30.0}},
        experience_level="fresher",
    )
    assert next_py_diff in {"medium", "hard"}
