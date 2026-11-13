"""Integration tests for Phase 4A: Interview Personalization & HR/Behavioral Interview Engine."""

import asyncio
import json
import uuid

import pytest
from fastapi.testclient import TestClient
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.models.interview_session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.integrations.llm.base import LLMError
from app.main import app
from app.modules.interview.adaptive import compute_adaptive_update
from app.modules.interview.deduplication import compute_question_fingerprint
from app.modules.interview.hr_generator import generate_hr_follow_up, generate_hr_question
from app.modules.interview.hr_grader import grade_hr_interview_answer
from app.modules.interview.hr_question_bank import (
    HR_CATEGORIES,
    pick_curated_hr_question,
    select_hr_category,
)
from app.modules.interview.router import service as interview_service
from app.modules.interview.rubric import (
    HR_DIMENSION_LABELS,
    HR_RUBRIC_DIMENSIONS,
    HR_RUBRIC_VERSION,
    HR_RUBRIC_WEIGHTS,
    calculate_hr_answer_score,
)
from app.modules.reports.router import service as report_service


class ScriptedHRLLM:
    """Mock LLM returning deterministic HR questions, contextual follow-ups, and grading."""

    def __init__(self, need_follow_up: bool = True, fail_all: bool = False):
        self.need_follow_up = need_follow_up
        self.fail_all = fail_all
        self.eval_count = 0

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        if self.fail_all:
            raise LLMError("Simulated LLM service unavailable")

        # 1. HR Evaluation
        if "Evaluate the candidate's answer thoroughly" in prompt or "reasoning_critical_thinking" in (system or ""):
            self.eval_count += 1
            is_fu = self.need_follow_up and self.eval_count == 1
            return json.dumps(
                {
                    "reasoning_critical_thinking": {
                        "score": 4.5 if not is_fu else 3.5,
                        "explanation": "Clear logical framework and context awareness.",
                    },
                    "decision_making_tradeoffs": {
                        "score": 4.0 if not is_fu else 3.0,
                        "explanation": "Evaluated constraints and practical alternatives.",
                    },
                    "communication_clarity": {
                        "score": 4.5,
                        "explanation": "Concise, structured, and easy to follow.",
                    },
                    "relevance_completeness": {
                        "score": 4.0 if not is_fu else 3.5,
                        "explanation": "Addressed the primary scenario directly.",
                    },
                    "reflection_adaptability": {
                        "score": 4.0,
                        "explanation": "Demonstrated openness to feedback and growth.",
                    },
                    "strengths": ["Structured problem analysis", "Clear communication"],
                    "missing_concepts": [] if not is_fu else ["Exploration of stakeholder disagreement"],
                    "improvement_suggestions": ["Mention retrospective metrics for measuring success."],
                    "confidence": "high",
                    "follow_up_needed": is_fu,
                    "follow_up_reason": "Explore stakeholder trade-offs." if is_fu else None,
                    "follow_up_type": "trade_off_exploration" if is_fu else None,
                }
            )

        # 2. HR Follow-up generation
        if "Generate a concise, insightful follow-up question" in prompt or "context-aware follow-up" in (system or ""):
            return json.dumps(
                {
                    "question_text": "What alternative options did you consider before deciding on that approach?",
                    "follow_up_type": "trade_off_exploration",
                }
            )

        # 3. Primary HR Question generation
        if "Generate one distinct, engaging HR/behavioral question" in prompt:
            return json.dumps(
                {
                    "category": "Behavioral Experience",
                    "difficulty": "medium",
                    "question_text": (
                        "Tell me about a challenging academic or project deadline where requirements changed unexpectedly. "
                        "How did you reprioritize your work and communicate with your team?"
                    ),
                    "scenario_type": "past_experience",
                }
            )

        # 4. Report Recommendations
        if "preparation recommendations" in prompt or "study plan" in (system or ""):
            return json.dumps(
                {
                    "recommendations": [
                        {
                            "area": "Communication & Clarity",
                            "observed_gap": "Responses could incorporate clearer structure when articulating trade-offs.",
                            "action": "Practice concise executive summaries before explaining technical details.",
                            "priority": "medium",
                        }
                    ]
                }
            )

        return "{}"


@pytest.fixture(name="client_and_session")
def fixture_client_and_session(monkeypatch):
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

    prev_get_db = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    llm = ScriptedHRLLM(need_follow_up=True)
    monkeypatch.setattr(interview_service, "llm_provider", llm)
    monkeypatch.setattr(interview_service, "checkpointer", MemorySaver())
    monkeypatch.setattr(report_service, "llm_provider", llm)

    with TestClient(app) as client:
        yield client, TestingSession, llm

    if prev_get_db is None:
        app.dependency_overrides.pop(get_db, None)
    else:
        app.dependency_overrides[get_db] = prev_get_db
    engine.dispose()


def _create_user_and_analysis(client: TestClient, SessionLocal, email: str, role: str = "Software Engineer"):
    reg = client.post(
        "/auth/register",
        json={"email": email, "password": "TestPassword123!"},
    )
    assert reg.status_code == 201
    user_id = reg.json()["id"]

    login = client.post(
        "/auth/login",
        json={"email": email, "password": "TestPassword123!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    db = SessionLocal()
    try:
        resume = Resume(user_id=user_id, filename="resume.pdf")
        db.add(resume)
        db.flush()
        analysis = ResumeAnalysis(
            user_id=user_id,
            resume_id=resume.id,
            job_role=role,
            resume_hash="hash_123",
            analysis_fingerprint=f"fp_{uuid.uuid4().hex}",
            status="completed",
            version=1,
            result_json={
                "job_role": role,
                "resume_skills": ["Python", "FastAPI", "React", "Docker"],
                "matched_skills": ["Python", "FastAPI"],
                "missing_skills": ["Kubernetes"],
                "match_score": 85.0,
                "strengths": ["Strong project execution", "Collaborative team member"],
                "improvement_suggestions": ["Practice trade-off articulation"],
                "likely_interview_questions": [],
                "projects": ["Distributed task queue", "Fullstack dashboard"],
            },
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        analysis_id = analysis.id
    finally:
        db.close()

    return user_id, headers, analysis_id


# ============================================================================
# 1. HR Rubric Deterministic Calculation & Benchmark Evaluation Set
# ============================================================================

def test_hr_rubric_deterministic_calculation():
    # Verify weights sum exactly to 1.0
    assert sum(HR_RUBRIC_WEIGHTS.values()) == pytest.approx(1.0)
    assert len(HR_RUBRIC_DIMENSIONS) == 5

    # Benchmark reviewed evaluation set:
    # A. Strong answer (all 4.5/5.0) -> expected (4.5 / 5.0) * 100 = 90.0
    strong_scores = {dim: 4.5 for dim in HR_RUBRIC_DIMENSIONS}
    assert calculate_hr_answer_score(strong_scores) == 90.0

    # B. Moderate answer:
    # reasoning=3.5 (0.30*3.5 = 1.05), decision=3.0 (0.25*3.0 = 0.75), comm=4.0 (0.20*4.0 = 0.80),
    # relevance=3.5 (0.15*3.5 = 0.525), reflection=3.0 (0.10*3.0 = 0.30)
    # Sum = 3.425 / 5.0 * 100 = 68.5
    mod_scores = {
        "reasoning_critical_thinking": 3.5,
        "decision_making_tradeoffs": 3.0,
        "communication_clarity": 4.0,
        "relevance_completeness": 3.5,
        "reflection_adaptability": 3.0,
    }
    assert calculate_hr_answer_score(mod_scores) == 68.5

    # C. Weak answer (all 1.5/5.0) -> (1.5 / 5.0) * 100 = 30.0
    weak_scores = {dim: 1.5 for dim in HR_RUBRIC_DIMENSIONS}
    assert calculate_hr_answer_score(weak_scores) == 30.0

    # Validation errors on invalid inputs
    with pytest.raises(ValueError, match="Missing dimension scores"):
        calculate_hr_answer_score({"reasoning_critical_thinking": 4.0})

    with pytest.raises(ValueError, match="must be between 0 and 5"):
        calculate_hr_answer_score({**strong_scores, "communication_clarity": 6.0})


# ============================================================================
# 2. HR Category Rotation & Balance
# ============================================================================

def test_hr_category_balance():
    asked: list[str] = []
    # Across first 5 questions, all 5 categories must be sampled
    for q_idx in range(1, 6):
        cat = select_hr_category(q_idx, asked, max_questions=8)
        assert cat in HR_CATEGORIES
        assert cat not in asked  # No repeats before all sampled
        asked.append(cat)

    assert set(asked) == set(HR_CATEGORIES)

    # Next question (6th) selects cleanly without immediate duplicate
    next_cat = select_hr_category(6, asked, max_questions=8)
    assert next_cat in HR_CATEGORIES
    assert next_cat != asked[-1]


# ============================================================================
# 3. Question Personalization & Deduplication
# ============================================================================

def test_hr_question_personalization_and_deduplication():
    llm = ScriptedHRLLM()

    async def _run():
        q1 = await generate_hr_question(
            provider=llm,
            question_id="q_001",
            target_role="Software Engineer",
            category="Behavioral Experience",
            difficulty="medium",
            question_index=1,
            max_questions=8,
            candidate_context={"projects": ["E-commerce cart"], "resume_skills": ["Python"]},
            previous_questions=[],
            experience_level="fresher",
        )
        assert q1.question_id == "q_001"
        assert q1.topic == "Behavioral Experience"
        assert len(q1.question_text) > 10

        # Deduplication check: if the same question text is in previous_questions, fallback picks an unasked curated question
        fp = compute_question_fingerprint(q1.topic, q1.question_text)
        q2 = await generate_hr_question(
            provider=llm,
            question_id="q_002",
            target_role="Software Engineer",
            category="Behavioral Experience",
            difficulty="medium",
            question_index=2,
            max_questions=8,
            candidate_context={},
            previous_questions=[q1.question_text],
            asked_fingerprints=[fp],
            experience_level="fresher",
        )
        assert q2.question_text != q1.question_text

    asyncio.run(_run())


# ============================================================================
# 4. HR Grader & Defensible Open-Ended Answers
# ============================================================================

def test_hr_grader_defensible_answers_and_fallback():
    llm = ScriptedHRLLM()

    async def _run():
        eval_res = await grade_hr_interview_answer(
            provider=llm,
            target_role="Backend Developer",
            category="Situational Judgment",
            difficulty="medium",
            question_text="Two teammates disagree on technical approach. How do you resolve it?",
            answer_text=(
                "I would schedule a short discussion to understand the core trade-offs of both options, "
                "evaluate them against our project requirements and deadlines, and prototype a minimal test if needed. "
                "If disagreement persists, we would escalate to the tech lead with a summary of pros and cons."
            ),
            experience_level="fresher",
        )
        assert eval_res.grading_status == "completed"
        assert eval_res.overall_score is not None
        assert eval_res.overall_score >= 70.0
        assert eval_res.reasoning_critical_thinking is not None
        assert eval_res.decision_making_tradeoffs is not None

        # Empty answer test
        empty_eval = await grade_hr_interview_answer(
            provider=llm,
            target_role="Backend Developer",
            category="Situational Judgment",
            difficulty="medium",
            question_text="Tell me about a challenge.",
            answer_text="",
        )
        assert empty_eval.overall_score == 0.0
        assert empty_eval.follow_up_needed is True

        # Unavailable LLM test
        offline_eval = await grade_hr_interview_answer(
            provider=None,
            target_role="Backend Developer",
            category="Situational Judgment",
            difficulty="medium",
            question_text="Tell me about a challenge.",
            answer_text="Short answer provided.",
        )
        assert offline_eval.grading_status == "unavailable"
        assert offline_eval.overall_score is None

    asyncio.run(_run())


# ============================================================================
# 5. Adaptive Practice vs Mock Assessment
# ============================================================================

def test_adaptive_vs_mock_progression():
    # Adaptive mode: strong answers advance difficulty
    eval_high = {
        "overall_score": 90.0,
        "reasoning_critical_thinking": {"score": 4.5},
        "grading_status": "completed",
    }
    update1 = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation=eval_high,
        recent_scores=[85.0],
        consecutive_strong_answers=1,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Behavioral Experience",
        progression_mode="adaptive",
        starting_difficulty="medium",
    )
    assert update1["next_difficulty"] == "hard"

    # Mock assessment mode: stays stable at starting/planned difficulty
    update_mock = compute_adaptive_update(
        current_difficulty="medium",
        experience_level="fresher",
        evaluation=eval_high,
        recent_scores=[85.0],
        consecutive_strong_answers=1,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Behavioral Experience",
        progression_mode="mock",
        starting_difficulty="medium",
    )
    assert update_mock["next_difficulty"] == "medium"

    # Explicit starting difficulty choice (e.g. "hard" chosen by an internship candidate)
    update_explicit = compute_adaptive_update(
        current_difficulty="hard",
        experience_level="internship",
        evaluation=eval_high,
        recent_scores=[],
        consecutive_strong_answers=0,
        consecutive_weak_answers=0,
        topic_performance={},
        topic="Behavioral Experience",
        progression_mode="mock",
        starting_difficulty="hard",
    )
    assert update_explicit["next_difficulty"] == "hard"


# ============================================================================
# 6. Full HR Interview Lifecycle, Follow-up, and Report Generation
# ============================================================================

def test_full_hr_interview_lifecycle_and_report(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers, analysis_id = _create_user_and_analysis(
        client, SessionLocal, "hr_flow_user@example.com"
    )

    # Start HR interview
    start_payload = {
        "analysis_id": analysis_id,
        "interview_type": "hr",
        "experience_level": "fresher",
        "starting_difficulty": "medium",
        "progression_mode": "adaptive",
        "max_questions": 2,
        "max_follow_ups": 1,
    }

    start_res = client.post("/interview/start", json=start_payload, headers=headers)
    assert start_res.status_code == 201, start_res.text
    data = start_res.json()
    session_id = data["session_id"]
    assert data["interview_type"] == "hr"
    assert data["starting_difficulty"] == "medium"
    assert data["progression_mode"] == "adaptive"
    assert data["current_question"] is not None
    assert data["current_question"]["topic"] in HR_CATEGORIES

    q1_id = data["current_question"]["question_id"]

    # Submit Q1 answer -> triggers contextual follow-up
    ans1_payload = {
        "question_id": q1_id,
        "answer": "In my academic capstone project, we faced a tight deadline so I prioritized core user authentication first.",
    }
    ans1_res = client.post(f"/interview/{session_id}/answer", json=ans1_payload, headers=headers)
    assert ans1_res.status_code == 200, ans1_res.text
    data1 = ans1_res.json()
    assert data1["current_question"] is not None
    assert data1["current_question"]["is_follow_up"] is True
    assert data1["follow_up_count"] == 1

    fu_id = data1["current_question"]["question_id"]

    # Submit Follow-up answer -> advances to Q2
    fu_payload = {
        "question_id": fu_id,
        "answer": "We weighed building a custom OAuth provider vs standard JWT and chose JWT for delivery speed.",
    }
    ans2_res = client.post(f"/interview/{session_id}/answer", json=fu_payload, headers=headers)
    assert ans2_res.status_code == 200, ans2_res.text
    data2 = ans2_res.json()
    assert data2["question_index"] == 2
    assert data2["current_question"]["is_follow_up"] is False

    # End the interview
    end_res = client.post(f"/interview/{session_id}/end", headers=headers)
    assert end_res.status_code == 200
    assert end_res.json()["status"] == "completed"

    # Generate HR Report
    rep_res = client.post(f"/reports/interviews/{session_id}/generate", headers=headers)
    assert rep_res.status_code == 200, rep_res.text
    report_data = rep_res.json()
    assert report_data["interview_type"] == "hr"
    assert report_data["rubric_version"] == HR_RUBRIC_VERSION
    assert report_data["overall_score"] is not None

    # Verify HR dimensions are present and technical dimensions are absent
    for hr_dim in HR_RUBRIC_DIMENSIONS:
        assert hr_dim in report_data["dimension_scores"]
        assert report_data["dimension_scores"][hr_dim]["label"] == HR_DIMENSION_LABELS[hr_dim]

    assert "technical_correctness" not in report_data["dimension_scores"]

    # Verify Report Summary in list endpoint
    list_res = client.get("/reports", headers=headers)
    assert list_res.status_code == 200
    summaries = list_res.json()
    assert len(summaries) >= 1
    assert summaries[0]["interview_type"] == "hr"
    assert summaries[0]["rubric_version"] == HR_RUBRIC_VERSION


# ============================================================================
# 7. Cross-User Isolation
# ============================================================================

def test_cross_user_isolation(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_a_id, headers_a, analysis_a_id = _create_user_and_analysis(
        client, SessionLocal, "user_a@example.com"
    )
    _user_b_id, headers_b, _analysis_b_id = _create_user_and_analysis(
        client, SessionLocal, "user_b@example.com"
    )

    # User B cannot start interview using User A's resume analysis
    res = client.post(
        "/interview/start",
        json={"analysis_id": analysis_a_id, "interview_type": "hr"},
        headers=headers_b,
    )
    assert res.status_code == 404

    # Create session for User A
    sess_res = client.post(
        "/interview/start",
        json={"analysis_id": analysis_a_id, "interview_type": "hr"},
        headers=headers_a,
    )
    assert sess_res.status_code == 201
    sid = sess_res.json()["session_id"]

    # User B cannot read User A's interview session
    get_res = client.get(f"/interview/{sid}", headers=headers_b)
    assert get_res.status_code == 404
