"""Evidence-based strength, weakness, and missing-concept analysis."""

from collections import Counter
from dataclasses import dataclass

from app.modules.reports.schemas import QuestionFeedbackItem, TopicPerformance


@dataclass
class AnalysisInsights:
    strengths: list[str]
    weaknesses: list[str]
    missing_concepts: list[str]


def _dedupe(items: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for raw in items:
        cleaned = raw.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)
            if len(result) >= limit:
                break
    return result


def analyze_interview_performance(
    question_feedback: list[QuestionFeedbackItem],
    topic_scores: list[TopicPerformance],
) -> AnalysisInsights:
    """Identify evidence-supported strengths and weaknesses from evaluations."""
    strengths: list[str] = []
    weaknesses: list[str] = []
    missing_concepts: list[str] = []

    for topic_perf in topic_scores:
        if topic_perf.score is None:
            continue
        if topic_perf.score >= 75.0:
            strengths.append(
                f"Strong performance in {topic_perf.topic} "
                f"({topic_perf.score:.0f}/100 across {topic_perf.evaluated_questions} evaluated answer(s))."
            )

    low_topic_counts: Counter[str] = Counter()
    low_topic_first_reason: dict[str, str] = {}

    for item in question_feedback:
        if item.grading_status == "completed":
            if item.overall_score is not None and item.overall_score >= 70.0:
                strengths.extend(item.strengths)

            if item.overall_score is not None and item.overall_score < 60.0:
                low_topic_counts[item.topic] += 1
                if item.topic not in low_topic_first_reason:
                    gap_note = (
                        item.missing_concepts[0]
                        if item.missing_concepts
                        else "incomplete technical explanation"
                    )
                    low_topic_first_reason[item.topic] = gap_note

            missing_concepts.extend(item.missing_concepts)

    # Distinguish repeated weaknesses from a single weak answer.
    for topic_name, count in low_topic_counts.items():
        gap_note = low_topic_first_reason[topic_name]
        if count >= 2:
            weaknesses.append(
                f"Recurring gap in {topic_name} ({count} answers below target, e.g., {gap_note})."
            )
        else:
            weaknesses.append(
                f"Single-question gap in {topic_name}: {gap_note}."
            )

    return AnalysisInsights(
        strengths=_dedupe(strengths, limit=6),
        weaknesses=_dedupe(weaknesses, limit=6),
        missing_concepts=_dedupe(missing_concepts, limit=10),
    )
