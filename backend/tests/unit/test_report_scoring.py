"""Unit tests for deterministic rubric scoring, aggregation, and analysis."""

from datetime import datetime, timezone

import pytest

from app.db.models.turn import InterviewTurn
from app.modules.interview.rubric import (
    RUBRIC_WEIGHTS,
    calculate_answer_score,
    validate_weights,
)
from app.modules.reports.analyzer import analyze_interview_performance
from app.modules.reports.scoring import aggregate_interview_scores


def test_weighted_score_arithmetic_and_boundaries():
    assert (
        calculate_answer_score(
            {
                "technical_correctness": 5.0,
                "relevance": 5.0,
                "completeness": 5.0,
                "technical_depth": 5.0,
            }
        )
        == 100.0
    )
    assert (
        calculate_answer_score(
            {
                "technical_correctness": 0.0,
                "relevance": 0.0,
                "completeness": 0.0,
                "technical_depth": 0.0,
            }
        )
        == 0.0
    )
    # 4*0.4 + 3*0.2 + 2*0.25 + 1*0.15 = 1.6 + 0.6 + 0.5 + 0.15 = 2.85 -> 57.0%
    assert (
        calculate_answer_score(
            {
                "technical_correctness": 4.0,
                "relevance": 3.0,
                "completeness": 2.0,
                "technical_depth": 1.0,
            }
        )
        == 57.0
    )


def test_invalid_weights_and_missing_or_out_of_range_dimensions():
    with pytest.raises(ValueError):
        validate_weights(
            {
                "technical_correctness": 0.5,
                "relevance": 0.5,
                "completeness": 0.5,
                "technical_depth": 0.5,
            }
        )

    with pytest.raises(ValueError):
        calculate_answer_score({"technical_correctness": 4.0})

    with pytest.raises(ValueError):
        calculate_answer_score(
            {
                "technical_correctness": 6.0,
                "relevance": 4.0,
                "completeness": 4.0,
                "technical_depth": 4.0,
            }
        )


def _make_turn(
    qid: str,
    idx: int,
    topic: str,
    is_fu: bool = False,
    parent_id: str | None = None,
    scores: dict[str, float] | None = None,
    unavailable: bool = False,
) -> InterviewTurn:
    ev = None
    if unavailable:
        ev = {"grading_status": "unavailable", "overall_score": None}
    elif scores is not None:
        ev = {
            dim: {"score": val, "explanation": f"{dim} explanation"}
            for dim, val in scores.items()
        }
        ev["grading_status"] = "completed"
        ev["strengths"] = ["Accurate core points"]
        ev["missing_concepts"] = ["Edge cases"] if scores["completeness"] < 3 else []
        ev["improvement_suggestions"] = []

    return InterviewTurn(
        session_id="sess-1",
        question_id=qid,
        question_index=idx,
        is_follow_up=is_fu,
        parent_question_id=parent_id,
        topic=topic,
        difficulty="medium",
        question_type="follow_up" if is_fu else "applied",
        question_text=f"Question {qid}",
        rag_sources=[],
        answer_text="Candidate answer",
        evaluation=ev,
        created_at=datetime.now(timezone.utc),
        answered_at=datetime.now(timezone.utc),
    )


def test_follow_up_aggregation_and_partial_coverage():
    # Q1 primary (all 4s -> 80.0) + Q1 follow-up (all 5s -> 100.0)
    # Group 1 = 0.7 * 80 + 0.3 * 100 = 86.0 (not double-counted as 2 topics!)
    # Q2 primary unavailable
    turns = [
        _make_turn(
            "q_001",
            1,
            "FastAPI",
            scores={
                "technical_correctness": 4,
                "relevance": 4,
                "completeness": 4,
                "technical_depth": 4,
            },
        ),
        _make_turn(
            "q_001_fu_1",
            1,
            "FastAPI",
            is_fu=True,
            parent_id="q_001",
            scores={
                "technical_correctness": 5,
                "relevance": 5,
                "completeness": 5,
                "technical_depth": 5,
            },
        ),
        _make_turn("q_002", 2, "PostgreSQL", unavailable=True),
    ]

    bundle = aggregate_interview_scores(turns, total_primary_questions=2)
    assert bundle.overall_score == 86.0
    assert bundle.evaluation_coverage.evaluated_count == 2
    assert bundle.evaluation_coverage.unavailable_count == 1
    assert bundle.evaluation_coverage.is_partial is True
    assert len(bundle.topic_scores) == 2
    assert bundle.topic_scores[0].topic == "FastAPI"
    assert bundle.topic_scores[0].score == 86.0
    assert bundle.topic_scores[1].topic == "PostgreSQL"
    assert bundle.topic_scores[1].score is None

    insights = analyze_interview_performance(
        bundle.question_feedback, bundle.topic_scores
    )
    assert any("FastAPI" in s for s in insights.strengths)
    assert bundle.dimension_scores["technical_correctness"].weight == RUBRIC_WEIGHTS["technical_correctness"]
