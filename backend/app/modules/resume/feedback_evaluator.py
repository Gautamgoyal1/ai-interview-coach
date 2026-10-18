
from collections.abc import Mapping
from typing import Any


ISSUE_UNSUPPORTED_TOPIC = "unsupported_topic_needs_review"
ISSUE_EMPTY_SECTION = "empty_required_section"
ISSUE_DUPLICATE_ITEM = "duplicate_feedback_item"

UNESTABLISHED_TOPIC_ALIASES = {
    "Model accuracy or other numerical performance results": (
        "model accuracy",
        "accuracy",
        "precision",
        "recall",
        "f1 score",
        "95%",
        "performance metric",
    ),
    "Model deployment or production experience": (
        "deployment",
        "deployed",
        "production experience",
        "production environment",
    ),
    "Docker experience": ("docker",),
    "Cloud platform experience": (
        "cloud platform",
        "aws",
        "azure",
        "gcp",
    ),
    "Specific feature engineering techniques": (
        "feature engineering",
    ),
    "Specific missing-value or outlier handling techniques": (
        "missing value",
        "missing values",
        "outlier",
    ),
}

# Phrases that usually indicate a recommendation or conditional suggestion,
# rather than a claim that the candidate already has the experience.
RECOMMENDATION_MARKERS = (
    "if applicable",
    "if you have",
    "if you have measured",
    "if measured",
    "if available",
    "consider adding",
    "consider including",
    "add details",
    "add specific",
    "include details",
    "include any",
    "describe how",
    "explain how",
    "provide evidence",
    "where applicable",
    "if you used",
    "if you have used",
    "if you have experience",
)

QUESTION_STARTERS = (
    "how ",
    "what ",
    "why ",
    "when ",
    "where ",
    "which ",
    "who ",
    "can you ",
    "could you ",
    "would you ",
    "have you ",
    "did you ",
    "describe ",
    "explain ",
    "walk me through ",
)


def _normalise(value: Any) -> str:
    """Convert a value to normalised text for comparison."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.casefold().split())


def _is_conditional_recommendation(text: str) -> bool:
    """Identify recommendations that condition advice on existing experience."""
    normalised = _normalise(text)

    conditional_markers = (
        "if you ",
        "if applicable",
        "if available",
        "where applicable",
        "consider adding",
        "consider including",
        "add details",
        "add specific",
        "include details",
        "include any",
        "provide evidence",
    )

    return any(
        marker in normalised
        for marker in conditional_markers
    )

def _is_question(text: str, section: str) -> bool:
    """Identify interview questions that should not be treated as claims."""
    normalised = _normalise(text)

    if section == "likely_interview_questions":
        return True

    return normalised.endswith("?") or normalised.startswith(
        QUESTION_STARTERS
    )


def _add_issue(
    issues: list[dict[str, str]],
    *,
    section: str,
    item: str,
    issue: str,
    detail: str,
) -> None:
    issues.append(
        {
            "section": section,
            "item": item,
            "issue": issue,
            "detail": detail,
        }
    )


def evaluate_feedback(
    feedback: Mapping[str, Any],
    expectations: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Evaluate feedback structure and flag potentially unsupported claims.

    This is a deterministic heuristic evaluator. It does not prove that
    a statement is factually correct or incorrect.
    """
    issues: list[dict[str, str]] = []

    section_expectations = expectations.get(
        "section_expectations", {}
    )

    # 1. Validate required feedback sections.
    for section, section_rules in section_expectations.items():
        if not isinstance(section_rules, Mapping):
            continue

        must_be_nonempty = section_rules.get(
            "must_be_nonempty", False
        )

        if not must_be_nonempty:
            continue

        items = feedback.get(section)

        if not isinstance(items, list) or not any(
            isinstance(item, str) and item.strip()
            for item in items
        ):
            _add_issue(
                issues,
                section=section,
                item="",
                issue=ISSUE_EMPTY_SECTION,
                detail=(
                    f"Section '{section}' must contain at least "
                    "one non-empty feedback item."
                ),
            )

    # 2. Check for duplicate feedback items.
    for section in section_expectations:
        items = feedback.get(section, [])

        if not isinstance(items, list):
            continue

        seen: set[str] = set()

        for item in items:
            if not isinstance(item, str) or not item.strip():
                continue

            normalised = _normalise(item)

            if normalised in seen:
                _add_issue(
                    issues,
                    section=section,
                    item=item,
                    issue=ISSUE_DUPLICATE_ITEM,
                    detail=(
                        "This feedback item duplicates another item "
                        "in the same section."
                    ),
                )
            else:
                seen.add(normalised)

    # 3. Flag mentions of experience or results that the resume
    # does not establish. Recommendations and questions are exempt.
    unestablished_topics = expectations.get(
        "not_established_by_resume", []
    )

    for section in section_expectations:
        items = feedback.get(section, [])

        if not isinstance(items, list):
            continue

        for item in items:
            if not isinstance(item, str) or not item.strip():
                continue

            normalised_item = _normalise(item)

            if _is_question(item, section):
                continue

            if _is_conditional_recommendation(item):
                continue

            for topic in unestablished_topics:
                if not isinstance(topic, str):
                    continue

                aliases = UNESTABLISHED_TOPIC_ALIASES.get(
                    topic, (topic,)
                )

                matched_alias = next(
                    (
                        alias
                        for alias in aliases
                        if _normalise(alias) in normalised_item
                    ),
                    None,
                )

                if matched_alias is None:
                    continue

                _add_issue(
                    issues,
                    section=section,
                    item=item,
                    issue=ISSUE_UNSUPPORTED_TOPIC,
                    detail=(
                        f"Potential unsupported claim about "
                        f"'{topic}'. The feedback mentions "
                        f"'{matched_alias}', which the resume "
                        "does not establish. Check whether the "
                        "statement is presented as an existing fact."
                    ),
                )
                # One issue per topic per feedback item.
                # Continue checking other topics in this item.
    structure_issues = {
        ISSUE_EMPTY_SECTION,
        ISSUE_DUPLICATE_ITEM,
    }

    structure_checks_passed = not any(
        issue["issue"] in structure_issues
        for issue in issues
    )

    return {
        "evaluation_id": expectations.get(
            "evaluation_id", "unspecified"
        ),
        "structure_checks_passed": structure_checks_passed,
        "issue_count": len(issues),
        "issues": issues,
    }
