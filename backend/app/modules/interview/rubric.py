"""Formal, versioned rubrics and deterministic scoring for interview answers.

Supports both Technical (v1.0) and HR/Behavioral (v1.0-hr) assessment tracks.
"""

import math
from typing import Mapping

# ============================================================================
# Technical Interview Rubric (v1.0)
# ============================================================================
RUBRIC_VERSION = "v1.0"

RUBRIC_DIMENSIONS: tuple[str, ...] = (
    "technical_correctness",
    "relevance",
    "completeness",
    "technical_depth",
)

RUBRIC_WEIGHTS: dict[str, float] = {
    "technical_correctness": 0.40,
    "relevance": 0.20,
    "completeness": 0.25,
    "technical_depth": 0.15,
}

DIMENSION_LABELS: dict[str, str] = {
    "technical_correctness": "Technical Correctness",
    "relevance": "Relevance",
    "completeness": "Completeness",
    "technical_depth": "Technical Depth",
}

# ============================================================================
# HR / Behavioral Interview Rubric (v1.0-hr)
# ============================================================================
HR_RUBRIC_VERSION = "v1.0-hr"

HR_RUBRIC_DIMENSIONS: tuple[str, ...] = (
    "reasoning_critical_thinking",
    "decision_making_tradeoffs",
    "communication_clarity",
    "relevance_completeness",
    "reflection_adaptability",
)

HR_RUBRIC_WEIGHTS: dict[str, float] = {
    "reasoning_critical_thinking": 0.30,
    "decision_making_tradeoffs": 0.25,
    "communication_clarity": 0.20,
    "relevance_completeness": 0.15,
    "reflection_adaptability": 0.10,
}

HR_DIMENSION_LABELS: dict[str, str] = {
    "reasoning_critical_thinking": "Reasoning & Critical Thinking",
    "decision_making_tradeoffs": "Decision-Making & Trade-offs",
    "communication_clarity": "Communication & Clarity",
    "relevance_completeness": "Relevance & Completeness",
    "reflection_adaptability": "Reflection & Adaptability",
}


def validate_weights_for_dimensions(
    weights: Mapping[str, float],
    dimensions: tuple[str, ...],
) -> dict[str, float]:
    """Ensure all expected rubric dimensions exist and weights sum to 1.0."""
    missing = [dim for dim in dimensions if dim not in weights]
    if missing:
        raise ValueError(f"Missing rubric weights for: {', '.join(missing)}")

    cleaned: dict[str, float] = {}
    for dim in dimensions:
        val = float(weights[dim])
        if not math.isfinite(val) or val < 0.0 or val > 1.0:
            raise ValueError(f"Invalid weight for {dim}: {val}")
        cleaned[dim] = val

    total = sum(cleaned.values())
    if not math.isclose(total, 1.0, rel_tol=1e-6, abs_tol=1e-6):
        raise ValueError(f"Rubric weights must sum to 1.0 (got {total:.4f}).")

    return cleaned


def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
    """Ensure technical rubric dimensions exist and weights sum to 1.0."""
    return validate_weights_for_dimensions(weights, RUBRIC_DIMENSIONS)


def validate_hr_weights(
    weights: Mapping[str, float] = HR_RUBRIC_WEIGHTS,
) -> dict[str, float]:
    """Ensure HR rubric dimensions exist and weights sum to 1.0."""
    return validate_weights_for_dimensions(weights, HR_RUBRIC_DIMENSIONS)


def calculate_score_for_dimensions_unrounded(
    scores: Mapping[str, float],
    dimensions: tuple[str, ...],
    weights: Mapping[str, float],
) -> float:
    """Deterministically compute unrounded 0-100 score from 0-5 dimensions."""
    validated = validate_weights_for_dimensions(weights, dimensions)

    missing = [dim for dim in dimensions if dim not in scores]
    if missing:
        raise ValueError(f"Missing dimension scores: {', '.join(missing)}")

    weighted_sum = 0.0
    for dim, weight in validated.items():
        val = float(scores[dim])
        if not math.isfinite(val) or val < 0.0 or val > 5.0:
            raise ValueError(
                f"Dimension '{dim}' score must be between 0 and 5 (got {val})."
            )
        weighted_sum += val * weight

    return (weighted_sum / 5.0) * 100.0


def calculate_answer_score_unrounded(
    scores: Mapping[str, float],
    weights: Mapping[str, float] = RUBRIC_WEIGHTS,
) -> float:
    """Deterministically compute an unrounded 0-100 score for technical answers."""
    return calculate_score_for_dimensions_unrounded(
        scores, RUBRIC_DIMENSIONS, weights
    )


def calculate_answer_score(
    scores: Mapping[str, float],
    weights: Mapping[str, float] = RUBRIC_WEIGHTS,
) -> float:
    """Compute a reproducible, 2-decimal rounded 0-100 score for technical answers."""
    return round(calculate_answer_score_unrounded(scores, weights), 2)


def calculate_hr_answer_score_unrounded(
    scores: Mapping[str, float],
    weights: Mapping[str, float] = HR_RUBRIC_WEIGHTS,
) -> float:
    """Deterministically compute an unrounded 0-100 score for HR answers."""
    return calculate_score_for_dimensions_unrounded(
        scores, HR_RUBRIC_DIMENSIONS, weights
    )


def calculate_hr_answer_score(
    scores: Mapping[str, float],
    weights: Mapping[str, float] = HR_RUBRIC_WEIGHTS,
) -> float:
    """Compute a reproducible, 2-decimal rounded 0-100 score for HR answers."""
    return round(calculate_hr_answer_score_unrounded(scores, weights), 2)


def get_rubric_dimensions(
    rubric_version: str | None = None,
    interview_type: str = "technical",
) -> tuple[str, ...]:
    if (
        rubric_version == HR_RUBRIC_VERSION
        or (rubric_version and "hr" in rubric_version.lower())
        or interview_type.lower() == "hr"
    ):
        return HR_RUBRIC_DIMENSIONS
    return RUBRIC_DIMENSIONS


def get_rubric_weights(
    rubric_version: str | None = None,
    interview_type: str = "technical",
) -> dict[str, float]:
    if (
        rubric_version == HR_RUBRIC_VERSION
        or (rubric_version and "hr" in rubric_version.lower())
        or interview_type.lower() == "hr"
    ):
        return dict(HR_RUBRIC_WEIGHTS)
    return dict(RUBRIC_WEIGHTS)


def get_dimension_labels(
    rubric_version: str | None = None,
    interview_type: str = "technical",
) -> dict[str, str]:
    if (
        rubric_version == HR_RUBRIC_VERSION
        or (rubric_version and "hr" in rubric_version.lower())
        or interview_type.lower() == "hr"
    ):
        return dict(HR_DIMENSION_LABELS)
    return dict(DIMENSION_LABELS)
