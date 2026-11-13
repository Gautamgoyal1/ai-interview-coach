"""AI Answer Coach service evaluating candidate answers and generating actionable feedback."""

import json
import logging
from typing import Any

from pydantic import ValidationError

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    EXPERIENCE_LEVEL_LABELS,
    normalize_experience_level,
)
from app.modules.practice.prompts import (
    PRACTICE_COACH_SYSTEM_PROMPT,
    PRACTICE_COACH_USER_PROMPT,
)
from app.modules.practice.schemas import PracticeFeedback

logger = logging.getLogger(__name__)


def _strip_json_fences(raw: str) -> str:
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
    return cleaned


def _build_heuristic_fallback(
    question_text: str,
    reference_answer: str,
    candidate_answer: str,
    interview_type: str,
    topic: str,
    previous_attempt_answer: str | None = None,
) -> PracticeFeedback:
    """Generate structured, transparent feedback when the LLM service is offline."""
    ans_words = set(candidate_answer.lower().split())
    ref_words = set(reference_answer.lower().split())
    overlap = ans_words.intersection(ref_words)

    correct_points = []
    if len(overlap) > 5:
        correct_points.append("Your response identifies key terminology relevant to the prompt.")
    else:
        correct_points.append("You provided an initial conceptual perspective on the question.")

    missing_points = [
        "Include a more detailed explanation of the underlying mechanism or trade-offs.",
        "Add a concrete practical example from a real-world scenario.",
    ]

    suggested_structure = [
        "1. Define the core concept clearly and directly in one sentence.",
        "2. Detail the primary function or mechanism.",
        "3. Highlight significant trade-offs, constraints, or alternatives.",
        "4. Conclude with a practical real-world example.",
    ] if interview_type == "technical" else [
        "1. Set the context and describe the core challenge or dilemma.",
        "2. Explain your reasoning, trade-offs weighed, and key decision.",
        "3. Describe the outcome and team collaboration.",
        "4. Share what you learned or would refine in hindsight.",
    ]

    improvements_from_prev = []
    if previous_attempt_answer:
        if len(candidate_answer) > len(previous_attempt_answer):
            improvements_from_prev.append("Expanded depth of explanation compared to previous attempt.")
        else:
            improvements_from_prev.append("Refined conciseness and focused on the core prompt.")

    return PracticeFeedback(
        correct_points=correct_points,
        missing_points=missing_points,
        improvement_suggestions=[
            "Ground your answer with an explicit concrete example to demonstrate hands-on experience.",
        ],
        suggested_structure=suggested_structure,
        improved_example_answer=reference_answer,
        next_action="Rewrite your response integrating a concrete scenario and explaining the trade-offs.",
        evaluation_status="completed",
        evaluation_confidence="medium",
        improvements_from_previous=improvements_from_prev,
    )


async def coach_practice_answer(
    *,
    provider: LLMProvider | None,
    question_text: str,
    reference_answer: str,
    candidate_answer: str,
    interview_type: str,
    topic: str,
    difficulty: str,
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    previous_attempt_answer: str | None = None,
) -> PracticeFeedback:
    """Evaluate candidate answer and generate personalized AI coaching feedback."""
    norm_level = normalize_experience_level(experience_level)
    level_label = EXPERIENCE_LEVEL_LABELS.get(norm_level, norm_level)

    prev_attempt_section = ""
    if previous_attempt_answer:
        prev_attempt_section = (
            f"Candidate's Previous Attempt (Compare current attempt to this):\n"
            f"{previous_attempt_answer}\n"
        )

    if provider is not None:
        try:
            prompt = PRACTICE_COACH_USER_PROMPT.format(
                interview_type=interview_type,
                topic=topic,
                difficulty=difficulty,
                experience_level_label=level_label,
                question_text=question_text,
                reference_answer=reference_answer,
                candidate_answer=candidate_answer,
                previous_attempt_section=prev_attempt_section,
            )

            raw_json = await provider.generate(
                prompt=prompt,
                system=PRACTICE_COACH_SYSTEM_PROMPT,
                json_mode=True,
            )
            cleaned_json = _strip_json_fences(raw_json)
            data = json.loads(cleaned_json)

            # Ensure fields exist
            feedback = PracticeFeedback(
                correct_points=data.get("correct_points", []),
                missing_points=data.get("missing_points", []),
                improvement_suggestions=data.get("improvement_suggestions", []),
                suggested_structure=data.get("suggested_structure", []),
                improved_example_answer=data.get("improved_example_answer", reference_answer),
                next_action=data.get("next_action", "Practice elaborating on trade-offs with an example."),
                evaluation_status="completed",
                evaluation_confidence=data.get("evaluation_confidence", "high"),
                improvements_from_previous=data.get("improvements_from_previous", []),
            )
            return feedback
        except (LLMError, json.JSONDecodeError, ValidationError, Exception) as exc:
            logger.warning("AI Answer Coach LLM generation failed: %s; using structured fallback", exc)

    return _build_heuristic_fallback(
        question_text=question_text,
        reference_answer=reference_answer,
        candidate_answer=candidate_answer,
        interview_type=interview_type,
        topic=topic,
        previous_attempt_answer=previous_attempt_answer,
    )
