"""Integration tests for Phase 4B: Personalized Practice Mode & AI Answer Coaching System."""

import json
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, hash_password
from app.db.models.interview_session import InterviewSession
from app.db.models.practice import PracticeAttempt, PracticeQuestion, PracticeSession
from app.db.models.report import InterviewReport
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.integrations.llm.base import LLMError
from app.main import app
from app.modules.practice.router import service as practice_service


class ScriptedPracticeLLM:
    """Deterministic LLM mock for practice question generation and AI Answer Coaching."""

    def __init__(self, fail_all: bool = False):
        self.fail_all = fail_all
        self.question_count = 0
        self.eval_count = 0

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        if self.fail_all:
            raise LLMError("Simulated LLM service unavailable")

        # 1. Practice Question Generation
        if "generate a realistic, targeted practice question" in (system or "") or "Generate a targeted practice question" in prompt:
            self.question_count += 1
            if "Conflict" in prompt or "hr" in prompt.lower():
                return json.dumps(
                    {
                        "question_text": f"Tell me about a challenging team conflict you navigated during a high-stakes project (Variation {self.question_count}).",
                        "hint_1": "Focus on understanding the other person's perspective objectively.",
                        "hint_2": "Describe how you facilitated alignment using constraints and project objectives.",
                        "reference_answer": "In our project, we resolved a design dispute by testing both approaches on a subset of users and picking the higher-converting layout.",
                        "reference_explanation": "Highlights data-driven resolution, empathy, and collaborative alignment.",
                    }
                )

            return json.dumps(
                {
                    "question_text": f"What is the difference between an INNER JOIN and a LEFT JOIN in SQL? (Variation {self.question_count})",
                    "hint_1": "Consider what happens to rows in the left table when no match exists in the right table.",
                    "hint_2": "Explain that INNER JOIN discards non-matching rows, while LEFT JOIN retains all left rows with NULL placeholders.",
                    "reference_answer": "An INNER JOIN returns only records where there is a match in both tables. A LEFT JOIN returns all rows from the left table and matched rows from the right table, filling unmatched right columns with NULL.",
                    "reference_explanation": "Explains row inclusion semantics and NULL handling clearly.",
                }
            )

        # 2. AI Answer Coach
        if "PrepMate's AI Answer Coach" in (system or "") or "Analyze and coach the candidate's interview answer" in prompt:
            self.eval_count += 1
            has_prev = "Candidate's Previous Attempt" in prompt

            return json.dumps(
                {
                    "correct_points": [
                        "Correctly identified that INNER JOIN only includes rows where keys match in both tables."
                    ],
                    "missing_points": [
                        "Did not explain how LEFT JOIN handles unmatched rows with NULL values."
                    ] if not has_prev else [],
                    "improvement_suggestions": [
                        "Include a practical example such as users and orders to make your explanation concrete."
                    ],
                    "suggested_structure": [
                        "1. Define INNER JOIN row inclusion criteria.",
                        "2. Define LEFT JOIN and NULL behavior for unmatched records.",
                        "3. Provide a clear real-world example.",
                    ],
                    "improved_example_answer": "An INNER JOIN returns rows with matches in both tables. A LEFT JOIN preserves all left rows, using NULLs for missing right data. For example, listing all users whether or not they have placed orders requires a LEFT JOIN.",
                    "next_action": "Add an example showing when you would specifically choose LEFT JOIN over INNER JOIN.",
                    "evaluation_confidence": "high",
                    "improvements_from_previous": [
                        "Added explicit mention of NULL values for unmatched records, significantly improving technical accuracy."
                    ] if has_prev else [],
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
    PracticeSession.__table__.create(bind=engine)
    PracticeQuestion.__table__.create(bind=engine)
    PracticeAttempt.__table__.create(bind=engine)

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

    app.dependency_overrides[get_db] = override_get_db

    llm = ScriptedPracticeLLM()
    monkeypatch.setattr(practice_service, "_llm_provider", llm)

    with TestClient(app) as test_client:
        yield test_client, TestingSession, llm

    app.dependency_overrides.clear()


def _create_user_and_auth(client: TestClient, SessionLocal, email: str = "practice_user@example.com"):
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
    return user_id, headers


# ============================================================================
# 1. Practice Session Creation (Technical & HR)
# ============================================================================

def test_practice_session_creation_technical_and_hr(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers = _create_user_and_auth(client, SessionLocal, "session_test@example.com")

    # Technical session
    tech_payload = {
        "topic": "SQL Joins",
        "interview_type": "technical",
        "target_role": "Software Engineer",
        "experience_level": "fresher",
        "weakness_context": "Candidate confused INNER vs LEFT JOIN in recent interview.",
        "difficulty": "medium",
    }
    res_tech = client.post("/practice/sessions", json=tech_payload, headers=headers)
    assert res_tech.status_code == 201, res_tech.text
    tech_data = res_tech.json()
    assert tech_data["topic"] == "SQL Joins"
    assert tech_data["interview_type"] == "technical"
    assert len(tech_data["questions"]) == 1

    q1 = tech_data["questions"][0]
    assert "JOIN" in q1["question_text"]
    assert q1["reference_revealed"] is False
    assert q1["reference_answer"] is None  # Hidden by default!
    assert q1["hints_revealed"] == []
    assert q1["revealed_hints"] == {}  # Hidden by default!

    # HR session
    hr_payload = {
        "topic": "Conflict Resolution",
        "interview_type": "hr",
        "target_role": "Product Engineer",
        "experience_level": "experienced_1_3",
        "weakness_context": "Struggled with stakeholder disagreement.",
        "difficulty": "medium",
    }
    res_hr = client.post("/practice/sessions", json=hr_payload, headers=headers)
    assert res_hr.status_code == 201, res_hr.text
    hr_data = res_hr.json()
    assert hr_data["interview_type"] == "hr"
    assert len(hr_data["questions"]) == 1


# ============================================================================
# 2. Progressive Hint System (Hint 1 -> Hint 2)
# ============================================================================

def test_progressive_hints_system(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers = _create_user_and_auth(client, SessionLocal, "hint_test@example.com")

    res = client.post(
        "/practice/sessions",
        json={"topic": "SQL Joins", "interview_type": "technical"},
        headers=headers,
    )
    session_data = res.json()
    q_id = session_data["questions"][0]["id"]

    # Reveal Hint 1
    h1_res = client.post(f"/practice/questions/{q_id}/hints/1/reveal", headers=headers)
    assert h1_res.status_code == 200, h1_res.text
    h1_data = h1_res.json()
    assert h1_data["level"] == 1
    assert len(h1_data["hint_text"]) > 10
    assert h1_data["hints_revealed"] == [1]
    assert h1_data["assistance_level"] == "hint_assisted"

    # Fetch question to confirm hint 1 is now visible in question response
    q_fetch = client.get(f"/practice/sessions/{session_data['id']}", headers=headers)
    q_data = q_fetch.json()["questions"][0]
    assert "1" in q_data["revealed_hints"]
    assert "2" not in q_data["revealed_hints"]
    assert q_data["reference_answer"] is None

    # Reveal Hint 2
    h2_res = client.post(f"/practice/questions/{q_id}/hints/2/reveal", headers=headers)
    assert h2_res.status_code == 200, h2_res.text
    h2_data = h2_res.json()
    assert h2_data["level"] == 2
    assert h2_data["hints_revealed"] == [1, 2]
    assert h2_data["assistance_level"] == "hint_assisted"


# ============================================================================
# 3. Reference Answer Reveal & Assistance Tracking
# ============================================================================

def test_reference_answer_reveal_and_assistance_tracking(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers = _create_user_and_auth(client, SessionLocal, "ref_test@example.com")

    res = client.post(
        "/practice/sessions",
        json={"topic": "SQL Joins", "interview_type": "technical"},
        headers=headers,
    )
    session_data = res.json()
    q_id = session_data["questions"][0]["id"]

    # Before reveal: reference is hidden
    assert session_data["questions"][0]["reference_revealed"] is False
    assert session_data["questions"][0]["reference_answer"] is None

    # Reveal reference answer
    ref_res = client.post(f"/practice/questions/{q_id}/reference/reveal", headers=headers)
    assert ref_res.status_code == 200, ref_res.text
    ref_data = ref_res.json()
    assert ref_data["reference_revealed"] is True
    assert len(ref_data["reference_answer"]) > 20
    assert ref_data["assistance_level"] == "reference_assisted"

    # Fetch question: reference is now visible and marked reference_assisted
    q_fetch = client.get(f"/practice/sessions/{session_data['id']}", headers=headers)
    q_data = q_fetch.json()["questions"][0]
    assert q_data["reference_revealed"] is True
    assert q_data["reference_answer"] is not None


# ============================================================================
# 4. AI Answer Coach, Submission & Retry Comparison
# ============================================================================

def test_ai_answer_coach_and_retry_comparison(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers = _create_user_and_auth(client, SessionLocal, "coach_test@example.com")

    res = client.post(
        "/practice/sessions",
        json={"topic": "SQL Joins", "interview_type": "technical"},
        headers=headers,
    )
    session_data = res.json()
    q_id = session_data["questions"][0]["id"]

    # 1. Independent first attempt
    att1_res = client.post(
        f"/practice/questions/{q_id}/attempts",
        json={"answer_text": "INNER JOIN joins two tables where keys match."},
        headers=headers,
    )
    assert att1_res.status_code == 201, att1_res.text
    att1 = att1_res.json()
    assert att1["attempt_number"] == 1
    assert att1["assistance_level"] == "independent"
    assert att1["reference_revealed"] is False
    assert len(att1["feedback"]["correct_points"]) >= 1
    assert len(att1["feedback"]["suggested_structure"]) >= 1
    assert len(att1["feedback"]["next_action"]) > 0
    assert att1["feedback"]["improvements_from_previous"] == []

    # 2. Retry attempt (Improve My Answer)
    att2_res = client.post(
        f"/practice/questions/{q_id}/attempts",
        json={
            "answer_text": (
                "An INNER JOIN returns only records where keys match in both tables. "
                "A LEFT JOIN returns all rows from the left table, and if there is no matching right record, it populates those columns with NULL."
            )
        },
        headers=headers,
    )
    assert att2_res.status_code == 201, att2_res.text
    att2 = att2_res.json()
    assert att2["attempt_number"] == 2
    assert att2["assistance_level"] == "independent"
    assert len(att2["feedback"]["improvements_from_previous"]) >= 1
    assert "NULL" in att2["feedback"]["improvements_from_previous"][0]

    # Verify attempt history endpoint
    history_res = client.get(f"/practice/questions/{q_id}/attempts", headers=headers)
    assert history_res.status_code == 200
    attempts = history_res.json()
    assert len(attempts) == 2
    assert attempts[0]["attempt_number"] == 1
    assert attempts[1]["attempt_number"] == 2


# ============================================================================
# 5. Generate Similar Question (Transfer of Understanding)
# ============================================================================

def test_generate_similar_question(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_id, headers = _create_user_and_auth(client, SessionLocal, "similar_test@example.com")

    res = client.post(
        "/practice/sessions",
        json={"topic": "SQL Joins", "interview_type": "technical"},
        headers=headers,
    )
    session_id = res.json()["id"]

    # Generate a variation / similar question
    gen_res = client.post(
        f"/practice/sessions/{session_id}/questions",
        json={"difficulty": "medium", "focus_concept": "SQL Joins with multiple tables"},
        headers=headers,
    )
    assert gen_res.status_code == 201, gen_res.text
    new_q = gen_res.json()
    assert new_q["session_id"] == session_id
    assert new_q["reference_revealed"] is False

    # Check that session now has 2 questions
    sess_res = client.get(f"/practice/sessions/{session_id}", headers=headers)
    sess_data = sess_res.json()
    assert len(sess_data["questions"]) == 2


# ============================================================================
# 6. Practice Recommendations from Interview Reports
# ============================================================================

def test_practice_recommendations_from_reports(client_and_session):
    client, SessionLocal, _llm = client_and_session
    user_id, headers = _create_user_and_auth(client, SessionLocal, "rec_test@example.com")

    # Create an interview session and report with weaknesses
    db = SessionLocal()
    int_session = InterviewSession(
        id=str(uuid.uuid4()),
        user_id=user_id,
        resume_analysis_id=1,
        target_role="Backend Engineer",
        interview_type="technical",
        status="completed",
        configuration={},
    )
    db.add(int_session)
    db.commit()

    report = InterviewReport(
        session_id=int_session.id,
        user_id=user_id,
        target_role="Backend Engineer",
        interview_type="technical",
        overall_score=68.0,
        dimension_scores={},
        topic_scores=[{"topic": "Database Indexing", "score": 45.0, "questions_asked": 2}],
        strengths=["Basic SQL queries"],
        weaknesses=["Database Indexing: missed B-Tree query mechanics"],
        missing_concepts=["B-Tree index structure"],
        recommendations=[
            {
                "area": "Database Indexing",
                "observed_gap": "Candidate did not explain B-tree traversal.",
                "action": "Practice explaining clustered vs non-clustered indexes.",
                "priority": "high",
            }
        ],
        question_feedback=[],
        completion_stats={},
        evaluation_coverage={},
        rubric_version="v1.0",
        rubric_weights={},
        status="completed",
    )
    db.add(report)
    db.commit()
    db.close()

    # Query recommendations endpoint
    rec_res = client.get("/practice/recommendations", headers=headers)
    assert rec_res.status_code == 200, rec_res.text
    recs = rec_res.json()
    assert len(recs) >= 1
    assert any("Indexing" in r["topic"] for r in recs)


# ============================================================================
# 7. Ownership Protection, Cross-User Isolation & Safe Deletion
# ============================================================================

def test_ownership_and_safe_deletion(client_and_session):
    client, SessionLocal, _llm = client_and_session
    _user_a, headers_a = _create_user_and_auth(client, SessionLocal, "owner_a@example.com")
    _user_b, headers_b = _create_user_and_auth(client, SessionLocal, "owner_b@example.com")

    # User A creates a session
    res_a = client.post(
        "/practice/sessions",
        json={"topic": "SQL Joins", "interview_type": "technical"},
        headers=headers_a,
    )
    session_id_a = res_a.json()["id"]
    q_id_a = res_a.json()["questions"][0]["id"]

    # User B cannot get User A's session -> 404
    get_b = client.get(f"/practice/sessions/{session_id_a}", headers=headers_b)
    assert get_b.status_code == 404

    # User B cannot reveal User A's hints -> 404
    hint_b = client.post(f"/practice/questions/{q_id_a}/hints/1/reveal", headers=headers_b)
    assert hint_b.status_code == 404

    # User B cannot submit attempts to User A's question -> 404
    att_b = client.post(
        f"/practice/questions/{q_id_a}/attempts",
        json={"answer_text": "Malicious attempt"},
        headers=headers_b,
    )
    assert att_b.status_code == 404

    # User B cannot delete User A's session -> 404
    del_b = client.delete(f"/practice/sessions/{session_id_a}", headers=headers_b)
    assert del_b.status_code == 404

    # User A deletes their session -> 200
    del_a = client.delete(f"/practice/sessions/{session_id_a}", headers=headers_a)
    assert del_a.status_code == 200

    # User A can no longer get the deleted session -> 404
    get_deleted = client.get(f"/practice/sessions/{session_id_a}", headers=headers_a)
    assert get_deleted.status_code == 404
