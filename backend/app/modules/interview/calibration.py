"""Experience-level calibration, deterministic difficulty plans, and question mix."""

from typing import Any, Literal

ExperienceLevel = Literal["internship", "fresher", "intermediate", "experienced"]
Difficulty = Literal["easy", "medium", "hard"]
QuestionFocus = Literal["fundamental", "resume_skill", "project", "gap_probe"]

DEFAULT_EXPERIENCE_LEVEL: ExperienceLevel = "fresher"

EXPERIENCE_LEVEL_LABELS: dict[ExperienceLevel, str] = {
    "internship": "Internship",
    "fresher": "Fresher / Entry Level",
    "intermediate": "Intermediate",
    "experienced": "Experienced",
}

EXPERIENCE_GUIDANCE: dict[ExperienceLevel, str] = {
    "internship": (
        "Candidate is an internship applicant (college student). Ask foundational, "
        "practical, approachable questions. Avoid senior architecture, distributed "
        "consensus, or obscure edge-case trivia."
    ),
    "fresher": (
        "Candidate is a fresher / entry-level graduate. Focus on core CS and "
        "role fundamentals, practical understanding, and resume projects. "
        "Avoid senior system-design complexity or academic derivations."
    ),
    "intermediate": (
        "Candidate has intermediate hands-on experience. Ask practical applied "
        "questions, real-world trade-offs, debugging, and moderate design choices."
    ),
    "experienced": (
        "Candidate is experienced. Include deeper architectural trade-offs, "
        "scalability, reliability, and production debugging where appropriate."
    ),
}

# Target difficulty weights: (easy, medium, hard)
DIFFICULTY_DISTRIBUTIONS: dict[ExperienceLevel, dict[Difficulty, float]] = {
    "internship": {"easy": 0.60, "medium": 0.35, "hard": 0.05},
    "fresher": {"easy": 0.45, "medium": 0.45, "hard": 0.10},
    "intermediate": {"easy": 0.25, "medium": 0.55, "hard": 0.20},
    "experienced": {"easy": 0.15, "medium": 0.50, "hard": 0.35},
}

# Target question category weights: 40% fundamentals, 30% resume skills, 20% project, 10% gaps
CATEGORY_DISTRIBUTION: dict[QuestionFocus, float] = {
    "fundamental": 0.40,
    "resume_skill": 0.30,
    "project": 0.20,
    "gap_probe": 0.10,
}

_LEVEL_ALIASES: dict[str, ExperienceLevel] = {
    "intern": "internship",
    "internship": "internship",
    "student": "internship",
    "student / internship": "internship",
    "fresher": "fresher",
    "entry": "fresher",
    "entry_level": "fresher",
    "entry-level": "fresher",
    "fresher / entry level": "fresher",
    "junior": "fresher",
    "graduate": "fresher",
    "intermediate": "intermediate",
    "mid": "intermediate",
    "mid_level": "intermediate",
    "mid-level": "intermediate",
    "experienced: 1–3 years": "intermediate",
    "experienced: 1-3 years": "intermediate",
    "1-3 years": "intermediate",
    "1-3": "intermediate",
    "experienced": "experienced",
    "experienced: 3+ years": "experienced",
    "3+ years": "experienced",
    "3+": "experienced",
    "senior": "experienced",
}


def normalize_experience_level(value: str | None) -> ExperienceLevel:
    """Normalize arbitrary experience-level input, defaulting to fresher."""
    if not value:
        return DEFAULT_EXPERIENCE_LEVEL
    cleaned = str(value).strip().lower()
    return _LEVEL_ALIASES.get(cleaned, DEFAULT_EXPERIENCE_LEVEL)


def _allocate_counts(total: int, weights: dict[Any, float]) -> dict[Any, int]:
    """Deterministically allocate `total` slots using Hamilton largest-remainder."""
    safe_total = max(1, total)
    raw = {key: safe_total * weight for key, weight in weights.items()}
    counts = {key: int(val) for key, val in raw.items()}
    remainder = safe_total - sum(counts.values())
    if remainder > 0:
        ranked = sorted(
            weights.keys(),
            key=lambda k: (raw[k] - counts[k], weights[k]),
            reverse=True,
        )
        for key in ranked[:remainder]:
            counts[key] += 1
    return counts


def build_difficulty_plan(
    experience_level: str | None,
    max_questions: int,
) -> list[Difficulty]:
    """Build a deterministic per-question difficulty sequence for an interview."""
    level = normalize_experience_level(experience_level)
    weights = DIFFICULTY_DISTRIBUTIONS[level]
    counts = _allocate_counts(max_questions, weights)

    easy_n = counts["easy"]
    med_n = counts["medium"]
    hard_n = counts["hard"]

    # Order smoothly: start with easy warm-ups, interleave easy/medium, place hard late.
    plan: list[Difficulty] = []
    if easy_n > 0:
        plan.append("easy")
        easy_n -= 1

    while easy_n > 0 or med_n > 0:
        if med_n > 0 and (len(plan) % 2 == 1 or easy_n == 0):
            plan.append("medium")
            med_n -= 1
        elif easy_n > 0:
            plan.append("easy")
            easy_n -= 1

    plan.extend(["hard"] * hard_n)
    return plan


def difficulty_for_question(
    experience_level: str | None,
    question_index: int,
    max_questions: int,
) -> Difficulty:
    """Return the calibrated difficulty for a 1-based question_index."""
    plan = build_difficulty_plan(experience_level, max_questions)
    idx = max(0, min(len(plan) - 1, question_index - 1))
    return plan[idx]


def build_category_plan(
    max_questions: int,
    has_resume_skills: bool = True,
    has_projects: bool = True,
    has_gaps: bool = True,
) -> list[QuestionFocus]:
    """Build a balanced category plan adapting cleanly when evidence is missing."""
    weights = dict(CATEGORY_DISTRIBUTION)
    if not has_gaps:
        weights["fundamental"] += weights.pop("gap_probe")
    if not has_projects:
        weights["fundamental"] += weights.pop("project")
    if not has_resume_skills:
        weights["fundamental"] += weights.pop("resume_skill")

    counts = _allocate_counts(max_questions, weights)
    # Interleave deterministically: fundamental, resume_skill, project, gap_probe
    order: list[QuestionFocus] = [
        "fundamental",
        "resume_skill",
        "project",
        "gap_probe",
    ]
    plan: list[QuestionFocus] = []
    remaining = {k: counts.get(k, 0) for k in order}
    while len(plan) < max(1, max_questions):
        added = False
        for key in order:
            if remaining[key] > 0:
                plan.append(key)
                remaining[key] -= 1
                added = True
        if not added:
            break
    return plan


def category_for_question(
    question_index: int,
    max_questions: int,
    candidate_context: dict[str, Any],
) -> QuestionFocus:
    """Return the planned question focus for a 1-based question_index."""
    has_resume = bool(
        (candidate_context.get("matched_skills") or [])
        or (candidate_context.get("resume_skills") or [])
    )
    # Project questions are grounded if candidate has project snippets or demonstrated skills.
    has_projects = bool(
        (candidate_context.get("projects") or [])
        or (candidate_context.get("resume_skills") or [])
        or (candidate_context.get("matched_skills") or [])
    )
    has_gaps = bool(candidate_context.get("missing_skills") or [])

    plan = build_category_plan(
        max_questions=max_questions,
        has_resume_skills=has_resume,
        has_projects=has_projects,
        has_gaps=has_gaps,
    )
    idx = max(0, min(len(plan) - 1, question_index - 1))
    return plan[idx]
