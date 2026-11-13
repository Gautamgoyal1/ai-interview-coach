"""Curated HR & Behavioral question bank, category balancing, and difficulty calibration."""

from dataclasses import dataclass
from typing import Any, Literal

from app.modules.interview.calibration import Difficulty, ExperienceLevel, normalize_experience_level
from app.modules.interview.deduplication import is_duplicate_or_paraphrase

HRCategory = Literal[
    "Behavioral Experience",
    "Situational Judgment",
    "Communication & Collaboration",
    "Critical Thinking",
    "Self-Awareness & Motivation",
]

HR_CATEGORIES: list[HRCategory] = [
    "Behavioral Experience",
    "Situational Judgment",
    "Communication & Collaboration",
    "Critical Thinking",
    "Self-Awareness & Motivation",
]

HR_CATEGORY_DESCRIPTIONS: dict[HRCategory, str] = {
    "Behavioral Experience": (
        "Past challenges, practical teamwork, leadership, taking initiative, "
        "and learning constructively from mistakes."
    ),
    "Situational Judgment": (
        "Workplace or project dilemmas, competing priorities, unexpected blockers, "
        "handling ambiguity, and responsible decision-making."
    ),
    "Communication & Collaboration": (
        "Navigating disagreements, delivering and receiving constructive feedback, "
        "articulating technical decisions to non-technical stakeholders, and diverse viewpoints."
    ),
    "Critical Thinking": (
        "Evaluating competing options, identifying engineering/process trade-offs, "
        "assessing risks, and deciding under incomplete information."
    ),
    "Self-Awareness & Motivation": (
        "Recognizing personal strengths and blind spots, career trajectory, "
        "continuous learning, and genuine alignment with the target role."
    ),
}


@dataclass(frozen=True)
class CuratedHRQuestion:
    category: HRCategory
    difficulty: Difficulty
    target_stage: Literal["fresher", "experienced", "any"]
    question_text: str
    scenario_type: Literal["past_experience", "situational_hypothetical"]


CURATED_HR_QUESTIONS: list[CuratedHRQuestion] = [
    # -------------------------------------------------------------------------
    # Behavioral Experience (Easy)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="easy",
        target_stage="fresher",
        question_text=(
            "Tell me about a challenging academic or personal project you worked on. "
            "What was the goal, what obstacle arose, and how did you overcome it?"
        ),
        scenario_type="past_experience",
    ),
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="easy",
        target_stage="experienced",
        question_text=(
            "Walk me through a project where you took initiative to improve an existing process "
            "or solve a recurring problem. What sparked your action, and what was the outcome?"
        ),
        scenario_type="past_experience",
    ),
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="easy",
        target_stage="any",
        question_text=(
            "Describe a time when you had to learn a new tool, technology, or concept under a tight deadline. "
            "How did you structure your learning and apply it effectively?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Behavioral Experience (Medium)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="medium",
        target_stage="fresher",
        question_text=(
            "Tell me about a time you worked on a team assignment where a teammate was not contributing "
            "their share or missed deadlines. How did you handle the situation to keep the project on track?"
        ),
        scenario_type="past_experience",
    ),
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="medium",
        target_stage="experienced",
        question_text=(
            "Describe a significant mistake or miscalculation you made in a past project. "
            "How and when did you realize it, what immediate corrective action did you take, and what did you change moving forward?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Behavioral Experience (Hard)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Behavioral Experience",
        difficulty="hard",
        target_stage="any",
        question_text=(
            "Describe a situation where a project you led or contributed heavily to was at serious risk of failure due to "
            "external factors beyond your direct control. How did you reassess priorities, communicate with stakeholders, and salvage value?"
        ),
        scenario_type="past_experience",
    ),

    # -------------------------------------------------------------------------
    # Situational Judgment (Easy)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Situational Judgment",
        difficulty="easy",
        target_stage="fresher",
        question_text=(
            "Imagine you are given a project task with very vague instructions and your mentor is unavailable for the day. "
            "What concrete steps would you take to make progress without going in the wrong direction?"
        ),
        scenario_type="situational_hypothetical",
    ),
    CuratedHRQuestion(
        category="Situational Judgment",
        difficulty="easy",
        target_stage="experienced",
        question_text=(
            "You discover a bug in a non-critical feature right before scheduled release. "
            "How do you evaluate whether to delay the release or deploy with a known issue and patch later?"
        ),
        scenario_type="situational_hypothetical",
    ),
    # -------------------------------------------------------------------------
    # Situational Judgment (Medium)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Situational Judgment",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "Two core team members strongly disagree about the technical direction for a critical feature, "
            "and debate is stalling progress while a milestone deadline approaches. How would you help the team reach an actionable consensus?"
        ),
        scenario_type="situational_hypothetical",
    ),
    CuratedHRQuestion(
        category="Situational Judgment",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "You are halfway through a sprint when your manager assigns you an urgent, unplanned customer issue that must be resolved today. "
            "How do you manage your existing commitments and communicate your updated capacity?"
        ),
        scenario_type="situational_hypothetical",
    ),
    # -------------------------------------------------------------------------
    # Situational Judgment (Hard)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Situational Judgment",
        difficulty="hard",
        target_stage="any",
        question_text=(
            "Suppose your leadership requests you to present performance metrics to key stakeholders in a way that technically adheres "
            "to guidelines but presents an overly optimistic, misleading picture of system reliability. How would you navigate this ethical dilemma?"
        ),
        scenario_type="situational_hypothetical",
    ),

    # -------------------------------------------------------------------------
    # Communication & Collaboration (Easy)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Communication & Collaboration",
        difficulty="easy",
        target_stage="any",
        question_text=(
            "How do you explain a complex technical concept or trade-off to a non-technical teammate, client, or stakeholder? "
            "Share an example of how you tailored your communication."
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Communication & Collaboration (Medium)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Communication & Collaboration",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "Tell me about a time you received constructive feedback or criticism that you initially disagreed with. "
            "How did you process that feedback and what did you do in response?"
        ),
        scenario_type="past_experience",
    ),
    CuratedHRQuestion(
        category="Communication & Collaboration",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "Describe a situation where you had to push back on a teammate's or stakeholder's unrealistic request. "
            "How did you frame the conversation to preserve a positive working relationship while protecting project quality?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Communication & Collaboration (Hard)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Communication & Collaboration",
        difficulty="hard",
        target_stage="any",
        question_text=(
            "You are working with a cross-functional partner whose priorities directly conflict with your engineering team's reliability objectives, "
            "leading to friction and finger-pointing. How do you step in to de-escalate tensions and establish a shared framework for decision-making?"
        ),
        scenario_type="situational_hypothetical",
    ),

    # -------------------------------------------------------------------------
    # Critical Thinking (Easy)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Critical Thinking",
        difficulty="easy",
        target_stage="any",
        question_text=(
            "When faced with multiple valid ways to solve a problem, what structured criteria do you use to evaluate options "
            "and decide which path to implement?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Critical Thinking (Medium)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Critical Thinking",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "Walk me through a decision you made where you had to choose between speed of delivery and architectural thoroughness. "
            "What trade-offs did you weigh, and how did you mitigate the resulting technical or operational debt?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Critical Thinking (Hard)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Critical Thinking",
        difficulty="hard",
        target_stage="any",
        question_text=(
            "You must make an architectural or organizational decision under significant ambiguity where data is conflicting and incomplete. "
            "How do you assess potential risks, determine acceptable thresholds of certainty, and create reversible vs irreversible decision paths?"
        ),
        scenario_type="situational_hypothetical",
    ),

    # -------------------------------------------------------------------------
    # Self-Awareness & Motivation (Easy)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Self-Awareness & Motivation",
        difficulty="easy",
        target_stage="any",
        question_text=(
            "What specific aspects of software engineering and problem-solving keep you most engaged, "
            "and what kind of team environment allows you to do your best work?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Self-Awareness & Motivation (Medium)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Self-Awareness & Motivation",
        difficulty="medium",
        target_stage="any",
        question_text=(
            "What is an area of professional or technical growth where you feel you currently have a gap or blind spot? "
            "What intentional steps have you taken recently to develop proficiency in this area?"
        ),
        scenario_type="past_experience",
    ),
    # -------------------------------------------------------------------------
    # Self-Awareness & Motivation (Hard)
    # -------------------------------------------------------------------------
    CuratedHRQuestion(
        category="Self-Awareness & Motivation",
        difficulty="hard",
        target_stage="any",
        question_text=(
            "Reflect on a situation where your initial confidence in your own assessment led to a suboptimal outcome. "
            "What did this teach you about your decision-making biases, and what guardrails do you now use to challenge your assumptions?"
        ),
        scenario_type="past_experience",
    ),
]


def select_hr_category(
    question_index: int,
    asked_categories: list[str],
    max_questions: int = 8,
) -> HRCategory:
    """Select the next HR category ensuring round-robin coverage before repeating."""
    asked_counts: dict[str, int] = {cat: 0 for cat in HR_CATEGORIES}
    for c in asked_categories:
        if c in asked_counts:
            asked_counts[c] += 1

    # First, prioritize any category that has not been asked yet in order of HR_CATEGORIES.
    for cat in HR_CATEGORIES:
        if asked_counts[cat] == 0:
            return cat

    # If all categories have been sampled at least once, choose the least frequently asked category
    # that is different from the immediately preceding category.
    last_cat = asked_categories[-1] if asked_categories else None
    sorted_cats = sorted(
        HR_CATEGORIES,
        key=lambda c: (asked_counts[c], 1 if c == last_cat else 0),
    )
    return sorted_cats[0]


def pick_curated_hr_question(
    category: HRCategory,
    difficulty: Difficulty,
    experience_level: str | None,
    previous_questions: list[str],
) -> CuratedHRQuestion:
    """Pick an unasked curated fallback question matching category, difficulty, and stage."""
    norm_level = normalize_experience_level(experience_level)
    is_fresher_stage = norm_level in {"internship", "fresher"}

    # Filter candidates by category and difficulty
    pool = [
        q for q in CURATED_HR_QUESTIONS
        if q.category == category and q.difficulty == difficulty
    ]

    # If pool is empty, relax difficulty
    if not pool:
        pool = [q for q in CURATED_HR_QUESTIONS if q.category == category]

    # Prioritize stage-appropriate questions
    ranked = sorted(
        pool,
        key=lambda q: (
            0 if (is_fresher_stage and q.target_stage == "fresher")
            or (not is_fresher_stage and q.target_stage == "experienced")
            else (1 if q.target_stage == "any" else 2)
        ),
    )

    for candidate in ranked:
        if previous_questions:
            is_dup, _ = is_duplicate_or_paraphrase(
                candidate_text=candidate.question_text,
                candidate_topic=category,
                previous_questions=previous_questions,
            )
            if is_dup:
                continue
        return candidate

    return ranked[0]
