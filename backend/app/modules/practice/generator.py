"""Practice question, progressive hints, and reference answer generator."""

from dataclasses import dataclass
import json
import logging
import re
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError
from sqlalchemy.orm import Session

from app.integrations.llm.base import LLMError, LLMProvider
from app.modules.interview.calibration import (
    DEFAULT_EXPERIENCE_LEVEL,
    EXPERIENCE_LEVEL_LABELS,
    normalize_experience_level,
)
from app.modules.interview.deduplication import is_duplicate_or_paraphrase
from app.modules.knowledge.retriever import retrieve_chunks_async
from app.modules.practice.prompts import (
    PRACTICE_QUESTION_SYSTEM_PROMPT,
    PRACTICE_QUESTION_USER_PROMPT,
)

logger = logging.getLogger(__name__)


class _GeneratedPracticePayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    question_text: str
    hint_1: str
    hint_2: str
    reference_answer: str
    reference_explanation: str | None = None


@dataclass
class PracticeQuestionData:
    question_text: str
    topic: str
    difficulty: str
    hints: dict[str, str]
    reference_answer: str
    reference_explanation: str | None


# Curated question packs for deterministic offline testing and resilient fallback
_CURATED_PRACTICE_PACKS: dict[str, PracticeQuestionData] = {
    "authentication": PracticeQuestionData(
        question_text="What is the difference between authentication and authorization in web applications, and how do they work together?",
        topic="Authentication & Authorization",
        difficulty="medium",
        hints={
            "hint_1": "Think about the difference between verifying who someone is versus checking what permissions they hold.",
            "hint_2": "Frame your answer by defining authentication (identity verification like login), defining authorization (access control like role checks), and giving an example of a logged-in user trying to access an admin route.",
        },
        reference_answer=(
            "Authentication verifies a user's identity — proving who they are, typically via credentials like a password, OTP, or SSO token. "
            "Authorization determines what actions or resources an authenticated user is permitted to access, based on roles or policies. "
            "For example, logging into a system verifies identity (authentication). Checking whether that logged-in user has permission to access the billing admin dashboard is authorization."
        ),
        reference_explanation="Distinguishes identity verification from permission management and grounds both in a clear concrete web workflow.",
    ),
    "sql": PracticeQuestionData(
        question_text="Explain the difference between an INNER JOIN and a LEFT JOIN in SQL, and provide a scenario where you would choose one over the other.",
        topic="SQL Joins",
        difficulty="medium",
        hints={
            "hint_1": "Consider what happens to rows in the left table when there is no corresponding match in the right table.",
            "hint_2": "Contrast how INNER JOIN discards non-matching rows from both tables, while LEFT JOIN preserves all rows from the left table with NULL placeholders for unmatched right columns.",
        },
        reference_answer=(
            "An INNER JOIN returns only records where there is a matching key in both tables. A LEFT JOIN returns all records from the left table, plus matched records from the right table; if no match exists, NULL values are returned for the right table's columns. "
            "For example, if you want a list of all registered users and their orders, use LEFT JOIN so users who haven't placed an order yet are still included. If you only want users with active orders, use INNER JOIN."
        ),
        reference_explanation="Accurately defines row inclusion semantics and provides a practical business domain example.",
    ),
    "overfitting": PracticeQuestionData(
        question_text="Your machine learning model achieves 98% training accuracy but only 70% validation accuracy. What is happening, and how would you diagnose and address it?",
        topic="Overfitting & Generalization",
        difficulty="medium",
        hints={
            "hint_1": "Focus on the gap between performance on seen training data versus unseen validation data.",
            "hint_2": "Identify overfitting where the model memorizes training noise. Outline techniques to resolve it: regularization (L1/L2, dropout), data augmentation, early stopping, or simplifying model architecture.",
        },
        reference_answer=(
            "The model is suffering from overfitting — it has memorized specific noise and patterns in the training set rather than learning generalizable features. "
            "To address this, I would: 1) Apply regularization such as L1/L2 penalty or Dropout; 2) Increase data diversity through data augmentation or collecting more training samples; "
            "3) Simplify the model architecture or reduce capacity; and 4) Implement early stopping based on validation loss."
        ),
        reference_explanation="Explains generalization failure clearly and lists actionable, standard remediation strategies.",
    ),
    "conflict": PracticeQuestionData(
        question_text="Tell me about a time when you and a teammate or stakeholder had a strong disagreement on a project's direction. How did you handle the situation and reach alignment?",
        topic="Conflict Resolution",
        difficulty="medium",
        hints={
            "hint_1": "Focus on how you sought to understand their perspective and kept the focus on project objectives rather than personal conflict.",
            "hint_2": "Structure your response around: 1) The conflicting perspectives and context; 2) How you facilitated an objective evaluation (data, constraints, user impact); 3) The agreed solution and trade-offs; 4) The resulting outcome and team relationship.",
        },
        reference_answer=(
            "In a previous project, a teammate wanted to build a custom caching layer while I advocated using Redis to save development time before our sprint deadline. "
            "Instead of arguing preferences, I scheduled a brief technical sync where we listed our constraints: time-to-market, maintenance burden, and traffic estimates. "
            "Seeing that our expected traffic was modest and the deadline was tight, we agreed to start with Redis for MVP and document custom caching as a future optimization. "
            "This preserved team trust and allowed us to deliver the feature on schedule."
        ),
        reference_explanation="Demonstrates objective problem-solving, stakeholder empathy, pragmatic trade-offs, and constructive team alignment.",
    ),
}


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


def _pick_curated_fallback(
    topic: str,
    interview_type: str,
    difficulty: str,
) -> PracticeQuestionData:
    norm_topic = topic.lower()
    for key, pack in _CURATED_PRACTICE_PACKS.items():
        if key in norm_topic:
            return pack

    if interview_type == "hr":
        return PracticeQuestionData(
            question_text=f"How would you approach a situation where you encountered competing priorities or ambiguity regarding '{topic}'?",
            topic=topic,
            difficulty=difficulty,
            hints={
                "hint_1": "Reflect on how you prioritize tasks, gather clarification, and communicate expectations.",
                "hint_2": "Describe how you assess urgency vs impact, align with stakeholders or mentors, and reflect on the outcome.",
            },
            reference_answer=(
                f"When dealing with ambiguous requirements or competing priorities in {topic}, I first map out core constraints, deadlines, and stakeholder expectations. "
                "I consult with project leads to align on what success looks like, prioritize the highest-impact components first, and maintain proactive updates to prevent misaligned work."
            ),
            reference_explanation="Highlights proactive communication, systematic prioritization, and adaptability in ambiguous settings.",
        )

    return PracticeQuestionData(
        question_text=f"Explain the core fundamentals and common trade-offs associated with '{topic}' in modern software systems.",
        topic=topic,
        difficulty=difficulty,
        hints={
            "hint_1": "Define the primary purpose of this concept and where it is typically used in the tech stack.",
            "hint_2": "Explain both the benefits and potential limitations or trade-offs (e.g. performance, complexity, memory overhead) with an example.",
        },
        reference_answer=(
            f"{topic} provides a structured mechanism for solving engineering challenges by establishing clear boundaries and efficient operations. "
            "The key trade-off is balancing implementation complexity and resource overhead against maintainability and performance gains."
        ),
        reference_explanation="Gives a balanced fundamental overview and highlights practical engineering trade-offs.",
    )


async def generate_practice_question(
    *,
    provider: LLMProvider | None,
    interview_type: str,
    target_role: str,
    topic: str,
    experience_level: str = DEFAULT_EXPERIENCE_LEVEL,
    difficulty: str = "medium",
    weakness_context: str | None = None,
    previous_questions: list[str] | None = None,
    db: Session | None = None,
) -> PracticeQuestionData:
    """Generate a targeted practice question with progressive hints and a reference answer."""
    prev_q_list = previous_questions or []
    norm_level = normalize_experience_level(experience_level)
    level_label = EXPERIENCE_LEVEL_LABELS.get(norm_level, norm_level)

    # Optional RAG context for technical questions
    rag_context_text = ""
    if interview_type == "technical" and db is not None:
        try:
            chunks = await retrieve_chunks_async(
                db=db,
                query=f"{topic} {weakness_context or ''}".strip(),
                top_k=2,
                topic=topic if len(topic.split()) <= 3 else None,
                role=target_role,
            )
            if chunks:
                rag_context_text = "Knowledge base context:\n" + "\n".join(
                    f"- {c.content}" for c in chunks
                )
        except Exception as exc:
            logger.debug("Optional RAG retrieval for practice question failed: %s", exc)

    if provider is not None:
        for attempt in range(2):
            try:
                user_prompt = PRACTICE_QUESTION_USER_PROMPT.format(
                    target_role=target_role,
                    interview_type=interview_type,
                    topic=topic,
                    experience_level_label=level_label,
                    difficulty=difficulty,
                    weakness_context=weakness_context or "General topic practice and core concept reinforcement.",
                    previous_questions=json.dumps(prev_q_list),
                    optional_rag_context=rag_context_text,
                )

                raw_json = await provider.generate(
                    prompt=user_prompt,
                    system=PRACTICE_QUESTION_SYSTEM_PROMPT,
                    json_mode=True,
                )
                cleaned_json = _strip_json_fences(raw_json)
                data = json.loads(cleaned_json)
                parsed = _GeneratedPracticePayload.model_validate(data)

                # Validate question text
                cleaned_q = parsed.question_text.strip()
                if len(cleaned_q.split()) < 6:
                    continue

                # Deduplication check
                if prev_q_list:
                    is_dup, _ = is_duplicate_or_paraphrase(
                        candidate_text=cleaned_q,
                        candidate_topic=topic,
                        previous_questions=prev_q_list,
                    )
                    if is_dup:
                        continue

                hints = {
                    "hint_1": parsed.hint_1.strip(),
                    "hint_2": parsed.hint_2.strip(),
                }

                return PracticeQuestionData(
                    question_text=cleaned_q,
                    topic=topic,
                    difficulty=difficulty,
                    hints=hints,
                    reference_answer=parsed.reference_answer.strip(),
                    reference_explanation=parsed.reference_explanation.strip() if parsed.reference_explanation else None,
                )
            except (LLMError, json.JSONDecodeError, ValidationError) as exc:
                logger.warning("Practice question generation attempt %d failed: %s", attempt + 1, exc)

    # Curated fallback
    fallback = _pick_curated_fallback(topic, interview_type, difficulty)
    return fallback
