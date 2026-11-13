"""Deterministic session-level, dimension-level, and topic-level scoring.

Supports both Technical and HR rubric aggregations.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from app.db.models.turn import InterviewTurn
from app.modules.interview.rubric import (
    DIMENSION_LABELS,
    HR_DIMENSION_LABELS,
    HR_RUBRIC_DIMENSIONS,
    HR_RUBRIC_WEIGHTS,
    RUBRIC_DIMENSIONS,
    RUBRIC_WEIGHTS,
    calculate_answer_score_unrounded,
    calculate_hr_answer_score_unrounded,
)
from app.modules.reports.schemas import (
    CompletionStats,
    DimensionSummary,
    EvaluationCoverage,
    QuestionFeedbackItem,
    TopicPerformance,
)

PRIMARY_GROUP_WEIGHT = 0.70
FOLLOW_UP_GROUP_WEIGHT = 0.30


@dataclass
class ScoringBundle:
    overall_score: float | None
    dimension_scores: dict[str, DimensionSummary]
    topic_scores: list[TopicPerformance]
    question_feedback: list[QuestionFeedbackItem]
    completion_stats: CompletionStats
    evaluation_coverage: EvaluationCoverage


def _extract_valid_dimension_scores(
    evaluation: dict[str, Any] | None,
    dimensions: tuple[str, ...],
) -> dict[str, float] | None:
    if not evaluation or evaluation.get("grading_status") == "unavailable":
        return None

    extracted: dict[str, float] = {}
    for dim in dimensions:
        entry = evaluation.get(dim)
        if not isinstance(entry, dict) or "score" not in entry:
            return None
        try:
            score = float(entry["score"])
        except (TypeError, ValueError):
            return None
        if score < 0.0 or score > 5.0:
            return None
        extracted[dim] = score
    return extracted


def aggregate_interview_scores(
    turns: list[InterviewTurn],
    total_primary_questions: int,
    interview_type: str = "technical",
    rubric_version: str | None = None,
) -> ScoringBundle:
    """Deterministically aggregate turn evaluations into session & topic scores."""
    is_hr = (
        str(interview_type).strip().lower() == "hr"
        or (rubric_version and "hr" in str(rubric_version).lower())
    )

    dimensions = HR_RUBRIC_DIMENSIONS if is_hr else RUBRIC_DIMENSIONS
    weights = HR_RUBRIC_WEIGHTS if is_hr else RUBRIC_WEIGHTS
    labels = HR_DIMENSION_LABELS if is_hr else DIMENSION_LABELS
    unrounded_fn = (
        calculate_hr_answer_score_unrounded
        if is_hr
        else calculate_answer_score_unrounded
    )

    answered_turns = [t for t in turns if t.answer_text is not None]
    primary_answered = [t for t in answered_turns if not t.is_follow_up]
    follow_up_answered = [t for t in answered_turns if t.is_follow_up]

    dim_totals: dict[str, list[float]] = {dim: [] for dim in dimensions}
    turn_unrounded_scores: dict[str, float | None] = {}
    evaluated_count = 0
    unavailable_count = 0

    question_feedback: list[QuestionFeedbackItem] = []

    for turn in answered_turns:
        ev = turn.evaluation or {}
        dim_map = _extract_valid_dimension_scores(ev, dimensions)

        if dim_map is not None:
            unrounded = unrounded_fn(dim_map, weights)
            turn_unrounded_scores[turn.question_id] = unrounded
            evaluated_count += 1
            for dim, val in dim_map.items():
                dim_totals[dim].append(val)
            grading_status = "completed"
            display_score = round(unrounded, 2)
        else:
            turn_unrounded_scores[turn.question_id] = None
            unavailable_count += 1
            grading_status = "unavailable"
            display_score = None

        dim_details = {
            dim: ev[dim]
            for dim in dimensions
            if isinstance(ev.get(dim), dict)
        }

        question_feedback.append(
            QuestionFeedbackItem(
                question_id=turn.question_id,
                question_index=turn.question_index,
                is_follow_up=turn.is_follow_up,
                parent_question_id=turn.parent_question_id,
                topic=turn.topic,
                difficulty=turn.difficulty,
                question_text=turn.question_text,
                answer_text=turn.answer_text,
                overall_score=display_score,
                grading_status=grading_status,
                dimension_scores=dim_details,
                strengths=list(ev.get("strengths") or []),
                missing_concepts=list(ev.get("missing_concepts") or []),
                improvement_suggestions=list(
                    ev.get("improvement_suggestions") or []
                ),
            )
        )

    # Group by primary question_index so follow-ups refine the same primary topic
    # without double-counting or inflating the session mean.
    primary_groups: dict[int, list[InterviewTurn]] = defaultdict(list)
    for turn in answered_turns:
        primary_groups[turn.question_index].append(turn)

    group_scores: list[float] = []
    topic_group_scores: dict[str, list[float]] = defaultdict(list)
    topic_question_counts: dict[str, int] = defaultdict(int)
    topic_eval_counts: dict[str, int] = defaultdict(int)

    for _q_idx, group_turns in sorted(primary_groups.items()):
        primaries = [t for t in group_turns if not t.is_follow_up]
        follow_ups = [t for t in group_turns if t.is_follow_up]
        topic_name = (primaries[0] if primaries else group_turns[0]).topic
        topic_question_counts[topic_name] += len(group_turns)

        primary_score = (
            turn_unrounded_scores.get(primaries[0].question_id)
            if primaries
            else None
        )
        fu_scores = [
            s
            for t in follow_ups
            if (s := turn_unrounded_scores.get(t.question_id)) is not None
        ]

        for t in group_turns:
            if turn_unrounded_scores.get(t.question_id) is not None:
                topic_eval_counts[topic_name] += 1

        group_score: float | None = None
        if primary_score is not None and fu_scores:
            fu_mean = sum(fu_scores) / len(fu_scores)
            group_score = (
                PRIMARY_GROUP_WEIGHT * primary_score
                + FOLLOW_UP_GROUP_WEIGHT * fu_mean
            )
        elif primary_score is not None:
            group_score = primary_score
        elif fu_scores:
            group_score = sum(fu_scores) / len(fu_scores)

        if group_score is not None:
            group_scores.append(group_score)
            topic_group_scores[topic_name].append(group_score)

    overall_score = (
        round(sum(group_scores) / len(group_scores), 2)
        if group_scores
        else None
    )

    dimension_scores: dict[str, DimensionSummary] = {}
    for dim in dimensions:
        vals = dim_totals[dim]
        avg = sum(vals) / len(vals) if vals else None
        dimension_scores[dim] = DimensionSummary(
            dimension=dim,
            label=labels[dim],
            weight=weights[dim],
            average_score=round(avg, 2) if avg is not None else None,
            percentage=round((avg / 5.0) * 100.0, 2) if avg is not None else None,
            evaluated_count=len(vals),
        )

    topic_scores: list[TopicPerformance] = []
    for topic_name, q_count in topic_question_counts.items():
        scores_for_topic = topic_group_scores.get(topic_name, [])
        topic_avg = (
            round(sum(scores_for_topic) / len(scores_for_topic), 2)
            if scores_for_topic
            else None
        )
        topic_scores.append(
            TopicPerformance(
                topic=topic_name,
                score=topic_avg,
                questions_asked=q_count,
                evaluated_questions=topic_eval_counts.get(topic_name, 0),
            )
        )

    total_answered = len(answered_turns)
    coverage_ratio = (
        round(evaluated_count / total_answered, 4) if total_answered > 0 else 0.0
    )

    return ScoringBundle(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        topic_scores=topic_scores,
        question_feedback=question_feedback,
        completion_stats=CompletionStats(
            questions_answered=total_answered,
            primary_questions_completed=len(primary_answered),
            follow_ups_answered=len(follow_up_answered),
            total_primary_questions=total_primary_questions,
        ),
        evaluation_coverage=EvaluationCoverage(
            evaluated_count=evaluated_count,
            unavailable_count=unavailable_count,
            total_answered=total_answered,
            coverage_ratio=coverage_ratio,
            is_partial=total_answered == 0 or unavailable_count > 0,
        ),
    )
