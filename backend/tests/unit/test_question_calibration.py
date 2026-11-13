"""Unit tests and quality evaluation for interview question calibration and realism."""

import json
from unittest.mock import AsyncMock

import anyio

from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    build_category_plan,
    build_difficulty_plan,
    difficulty_for_question,
    normalize_experience_level,
)
from app.modules.interview.grader import grade_interview_answer
from app.modules.interview.question_bank import (
    CURATED_QUESTION_BANK,
    get_role_fundamental_topics,
    pick_curated_fallback_question,
)
from app.modules.interview.question_generator import (
    generate_follow_up_question,
    generate_interview_question,
    validate_generated_question,
)
from app.modules.interview.rubric import RUBRIC_VERSION, RUBRIC_WEIGHTS
from app.modules.interview.topic_selector import select_topic_with_focus


def test_default_experience_level_is_fresher():
    assert DEFAULT_EXPERIENCE_LEVEL == "fresher"
    assert normalize_experience_level(None) == "fresher"
    assert normalize_experience_level("") == "fresher"
    assert normalize_experience_level("unknown") == "fresher"
    assert normalize_experience_level("Entry Level") == "fresher"
    assert normalize_experience_level("Internship") == "internship"
    assert normalize_experience_level("Intermediate") == "intermediate"
    assert normalize_experience_level("Experienced") == "experienced"


def test_difficulty_distributions_by_experience_level():
    fresher_plan = build_difficulty_plan("fresher", 8)
    assert len(fresher_plan) == 8
    assert fresher_plan[0] == "easy"
    assert fresher_plan.count("easy") == 4
    assert fresher_plan.count("medium") == 3
    assert fresher_plan.count("hard") == 1

    intern_plan = build_difficulty_plan("internship", 8)
    assert len(intern_plan) == 8
    assert intern_plan.count("easy") == 5
    assert intern_plan.count("medium") == 3
    assert intern_plan.count("hard") == 0

    exp_plan = build_difficulty_plan("experienced", 8)
    assert len(exp_plan) == 8
    assert exp_plan.count("hard") >= 3
    assert difficulty_for_question("fresher", 1, 8) == "easy"


def test_category_plan_adapts_when_evidence_is_missing():
    full_plan = build_category_plan(8, has_resume_skills=True, has_projects=True, has_gaps=True)
    assert len(full_plan) == 8
    assert full_plan.count("fundamental") == 3
    assert full_plan.count("resume_skill") == 2
    assert full_plan.count("project") == 2
    assert full_plan.count("gap_probe") == 1

    no_evidence_plan = build_category_plan(8, has_resume_skills=False, has_projects=False, has_gaps=False)
    assert all(cat == "fundamental" for cat in no_evidence_plan)


def test_role_based_topic_selection_and_personalization():
    ctx = {
        "target_role": "Backend Developer",
        "matched_skills": ["Python", "SQL"],
        "resume_skills": ["Python", "SQL", "FastAPI"],
        "missing_skills": ["Redis"],
        "projects": ["Task API"],
    }
    asked: list[str] = []
    focuses: list[str] = []
    for idx in range(1, 9):
        topic, _qtype, focus = select_topic_with_focus(ctx, asked, idx, max_questions=8)
        assert topic not in asked
        asked.append(topic)
        focuses.append(focus)

    assert len(set(asked)) == 8
    assert "fundamental" in focuses
    assert "resume_skill" in focuses
    assert "project" in focuses
    assert "gap_probe" in focuses


def test_validator_rejects_academic_bundled_repetitive_and_ungrounded_questions():
    ok, _ = validate_generated_question(
        "What is the difference between a list and a tuple in Python?",
        experience_level="fresher",
        difficulty="easy",
        previous_questions=[],
        candidate_context={},
    )
    assert ok is True

    # Overly academic for fresher
    ok_acad, reason_acad = validate_generated_question(
        "Provide a mathematical derivation of multi-head projection operators in transformers.",
        experience_level="fresher",
        difficulty="easy",
        previous_questions=[],
        candidate_context={},
    )
    assert ok_acad is False
    assert "academic" in (reason_acad or "").lower()

    # Bundled multiple questions
    ok_multi, _ = validate_generated_question(
        "What is REST? How does JWT work? What is SQL indexing? And how do you scale Redis?",
        experience_level="fresher",
        difficulty="medium",
        previous_questions=[],
    )
    assert ok_multi is False

    # Repetitive
    ok_rep, _ = validate_generated_question(
        "What is the difference between a list and a tuple in Python?",
        experience_level="fresher",
        difficulty="easy",
        previous_questions=["What is the difference between a list and a tuple in Python?"],
    )
    assert ok_rep is False

    # No invented project reference when resume has no evidence
    ok_proj, _ = validate_generated_question(
        "Can you explain the architecture of your project and how you deployed it?",
        experience_level="fresher",
        difficulty="easy",
        previous_questions=[],
        candidate_context={"resume_skills": [], "matched_skills": [], "projects": []},
    )
    assert ok_proj is False


def test_question_generator_retries_once_then_falls_back_to_curated_bank():
    async def scenario():
        provider = AsyncMock()
        # Both attempts return overly academic text -> bounded retry (2 calls) then curated fallback
        provider.generate.return_value = json.dumps(
            {
                "topic": "Transformers",
                "difficulty": "hard",
                "question_type": "conceptual",
                "question_text": "Provide a mathematical derivation of multi-head projection operators.",
            }
        )
        q = await generate_interview_question(
            provider=provider,
            question_id="q_001",
            target_role="AI Engineer",
            topic="Transformers & Attention",
            question_type="conceptual",
            difficulty="easy",
            question_index=1,
            max_questions=8,
            candidate_context={"matched_skills": ["Python"]},
            retrieved_context="",
            previous_questions=[],
            experience_level="fresher",
            question_focus="fundamental",
        )
        assert provider.generate.await_count == 2
        assert q.difficulty == "easy"  # Enforces planned difficulty
        assert "mathematical derivation" not in q.question_text.lower()
        assert len(q.question_text) > 15

    anyio.run(scenario)


def test_follow_up_does_not_escalate_difficulty_when_candidate_struggles():
    async def scenario():
        provider = AsyncMock()
        provider.generate.return_value = json.dumps(
            {
                "question_text": "No problem—can you give one simple example of when overfitting happens?",
                "difficulty": "hard",
            }
        )
        fu = await generate_follow_up_question(
            provider=provider,
            question_id="q_001_fu_1",
            target_role="Data Scientist",
            topic="Overfitting & Underfitting",
            difficulty="medium",
            previous_question="What is overfitting?",
            candidate_answer="I am not sure, maybe too much data.",
            evaluation={
                "overall_score": 30.0,
                "technical_correctness": {"score": 1.5, "explanation": "Unclear."},
                "missing_concepts": ["memorizing training noise"],
            },
            retrieved_context="",
            experience_level="fresher",
        )
        assert fu.is_follow_up is True
        assert fu.difficulty == "easy"  # Stepped down from medium -> easy

    anyio.run(scenario)


def test_grader_passes_experience_level_and_preserves_rubric_contract():
    async def scenario():
        provider = AsyncMock()
        provider.generate.return_value = json.dumps(
            {
                "technical_correctness": {"score": 4, "explanation": "Accurate for entry level."},
                "relevance": {"score": 5, "explanation": "Directly answered."},
                "completeness": {"score": 4, "explanation": "Covers core points."},
                "technical_depth": {"score": 4, "explanation": "Good depth for fresher."},
                "strengths": ["Clear distinction between lists and tuples"],
                "missing_concepts": [],
                "improvement_suggestions": [],
                "confidence": "high",
                "follow_up_needed": False,
                "follow_up_reason": None,
            }
        )
        res = await grade_interview_answer(
            provider=provider,
            target_role="Python Developer",
            topic="Lists vs Tuples",
            difficulty="easy",
            question_text="What is the difference between a list and a tuple?",
            answer_text="Lists are mutable and use square brackets; tuples are immutable.",
            retrieved_context="",
            experience_level="internship",
        )
        assert res.grading_status == "completed"
        assert res.rubric_version == RUBRIC_VERSION
        assert res.rubric_weights == RUBRIC_WEIGHTS
        sent_prompt = provider.generate.call_args.kwargs["prompt"]
        assert "Internship" in sent_prompt

    anyio.run(scenario)


def test_curated_evaluation_dataset_quality_across_roles():
    """Verify curated fallback questions across all major roles meet realism & quality criteria."""
    roles = [
        "Software Engineer",
        "Backend Developer",
        "Python Developer",
        "Data Scientist",
        "Machine Learning Engineer",
        "AI Engineer",
    ]
    for role in roles:
        topics = get_role_fundamental_topics(role)
        assert len(topics) >= 6
        asked: list[str] = []
        for idx, diff in enumerate(build_difficulty_plan("fresher", 8), start=1):
            q = pick_curated_fallback_question(
                target_role=role,
                topic=topics[(idx - 1) % len(topics)],
                difficulty=diff,
                question_type="conceptual",
                previous_questions=asked,
                experience_level="fresher",
                has_resume_evidence=True,
            )
            ok, reason = validate_generated_question(
                q.question_text,
                experience_level="fresher",
                difficulty=diff,
                previous_questions=asked,
                candidate_context={"resume_skills": ["Python"]},
            )
            assert ok, f"{role} Q{idx} failed validation: {reason}"
            asked.append(q.question_text)
        assert len(set(asked)) == 8
        assert len(CURATED_QUESTION_BANK) >= 6
