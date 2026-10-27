
"""Skill extraction and deterministic resume-to-job matching."""

import json
import math
import re
from pathlib import Path


TAXONOMY_PATH = Path(__file__).with_name("skills_taxonomy.json")
ROLES_PATH = Path(__file__).with_name("roles.json")


def load_skill_taxonomy() -> dict[str, list[str]]:
    """Load canonical skills and their aliases."""
    with TAXONOMY_PATH.open("r", encoding="utf-8") as file:
        taxonomy = json.load(file)

    return {
        canonical.lower(): [
            canonical.lower(),
            *(alias.lower() for alias in aliases),
        ]
        for canonical, aliases in taxonomy.items()
    }


def extract_skills(
    text: str,
    taxonomy: dict[str, list[str]] | None = None,
) -> list[str]:
    """Return canonical skills found in text using whole-word matching."""
    if taxonomy is None:
        taxonomy = load_skill_taxonomy()

    normalized_text = text.lower()
    found = []

    for canonical, aliases in taxonomy.items():
        for alias in aliases:
            pattern = rf"(?<!\w){re.escape(alias.lower())}(?!\w)"

            if re.search(pattern, normalized_text):
                found.append(canonical)
                break

    return sorted(set(found))


def calculate_match(
    resume_text: str,
    job_text: str,
    taxonomy: dict[str, list[str]] | None = None,
) -> dict:
    """Compare detected resume skills against skills in a job description."""
    resume_skills = set(extract_skills(resume_text, taxonomy))
    required_skills = set(extract_skills(job_text, taxonomy))

    matched = sorted(resume_skills & required_skills)
    missing = sorted(required_skills - resume_skills)

    score = (
        round(len(matched) / len(required_skills) * 100, 2)
        if required_skills
        else 0.0
    )

    return {
        "resume_skills": sorted(resume_skills),
        "required_skills": sorted(required_skills),
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score,
    }


def load_role_skills() -> dict[str, list[str]]:
    """Load default required skills for supported job roles."""
    with ROLES_PATH.open("r", encoding="utf-8") as file:
        roles = json.load(file)

    return {
        role.strip().lower(): [
            skill.strip().lower() for skill in skills
        ]
        for role, skills in roles.items()
    }


def calculate_match_against_skills(
    resume_text: str,
    required_skills: list[str],
    taxonomy: dict[str, list[str]] | None = None,
) -> dict:
    """Compare detected resume skills against an explicit skill list."""
    if taxonomy is None:
        taxonomy = load_skill_taxonomy()

    resume_skills = set(extract_skills(resume_text, taxonomy))
    required = {skill.strip().lower() for skill in required_skills}

    # Reject skills that are not defined in the canonical taxonomy.
    unknown_skills = required - set(taxonomy)

    if unknown_skills:
        raise ValueError(
            f"Unknown canonical skills: {sorted(unknown_skills)}"
        )

    matched = sorted(resume_skills & required)
    missing = sorted(required - resume_skills)

    score = (
        round(len(matched) / len(required) * 100, 2)
        if required
        else 0.0
    )

    return {
        "resume_skills": sorted(resume_skills),
        "required_skills": sorted(required),
        "matched_skills": matched,
        "missing_skills": missing,
        "match_score": score,
    }


def calculate_weighted_match(
    matched_skills: list[str],
    required_skills: list[str],
    skill_weights: dict[str, float],
) -> dict:
    """Calculate an experimental weighted score without changing match_score."""
    required = {skill.strip().lower() for skill in required_skills}
    matched = {skill.strip().lower() for skill in matched_skills}

    unknown_matches = matched - required
    if unknown_matches:
        raise ValueError(
            "Matched skills must be required skills: "
            f"{sorted(unknown_matches)}"
        )

    normalized_weights = {
        skill.strip().lower(): weight
        for skill, weight in skill_weights.items()
    }

    missing_weights = required - set(normalized_weights)
    if missing_weights:
        raise ValueError(
            f"Missing weights for required skills: {sorted(missing_weights)}"
        )

    for skill in required:
        weight = normalized_weights[skill]

        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError(
                f"Weight for '{skill}' must be a finite positive number."
            )

    total_weight = sum(normalized_weights[skill] for skill in required)
    matched_weight = sum(
        normalized_weights[skill] for skill in matched
    )

    score = (
        round(matched_weight / total_weight * 100, 2)
        if total_weight
        else 0.0
    )

    return {
        "weighted_match_score": score,
        "matched_weight": round(matched_weight, 4),
        "total_weight": round(total_weight, 4),
    }



def adjust_skill_weights_from_job_description(
    skill_weights: dict[str, float],
    job_description: str,
) -> dict[str, float]:
    """Adjust baseline weights using explicit requirement labels.

    This is a conservative heuristic, not a complete natural-language parser.
    """
    required_pattern = re.compile(
        r"\b(?:required|must[- ]have|must|required skill)\b",
        re.IGNORECASE,
    )
    preferred_pattern = re.compile(
        r"\b(?:preferred|nice[- ]to[- ]have|bonus|desirable)\b",
        re.IGNORECASE,
    )
    negated_required_pattern = re.compile(
        r"\b(?:not|never)\s+(?:(?:strictly|necessarily)\s+)?required\b"
        r"|\bnot\s+(?:a\s+)?requirement\b"
        r"|\bnot\s+mandatory\b"
        r"|\bno\s+requirement\s+for\b",
        re.IGNORECASE,
    )

    # Split sentences and contrasting clauses so a negation for one
    # skill does not suppress a requirement signal for another.
    clauses = re.split(
        r"(?<=[.!?])\s+|\n+|;\s*|,\s*(?=(?:but|however|whereas|while)\b)",
        job_description,
        flags=re.IGNORECASE,
    )

    adjusted: dict[str, float] = {}

    for skill, weight in skill_weights.items():
        canonical = skill.strip().lower()

        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not math.isfinite(weight)
            or weight <= 0
        ):
            raise ValueError(
                f"Weight for '{canonical}' must be a finite positive number."
            )

        skill_pattern = re.compile(
            rf"(?<!\w){re.escape(canonical)}(?!\w)",
            re.IGNORECASE,
        )

        required_signal = False
        preferred_signal = False

        for clause in clauses:
            if not skill_pattern.search(clause):
                continue

            # Ignore requirement signals in a negated clause.
            if negated_required_pattern.search(clause):
                continue

            if required_pattern.search(clause):
                required_signal = True
            elif preferred_pattern.search(clause):
                preferred_signal = True

        if required_signal:
            adjusted[canonical] = round(weight * 1.25, 4)
        elif preferred_signal:
            adjusted[canonical] = round(weight * 0.75, 4)
        else:
            adjusted[canonical] = float(weight)

    return adjusted
