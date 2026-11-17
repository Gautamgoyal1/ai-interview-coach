"""Difficulty contracts and bounded question screening; no external calls."""

import json
from unittest.mock import AsyncMock

import anyio
import pytest
from sqlalchemy.dialects import postgresql

from app.integrations.llm.base import LLMError
from app.modules.interview.difficulty_contract import (
    context_difficulty,
    difficulty_contract,
)
from app.modules.interview.hard_fallbacks import ENTRY, SENIOR
from app.modules.interview.question_generator import (
    generate_interview_question,
    validate_generated_question,
)
from app.modules.interview.question_quality import QuestionQuality
from app.modules.interview.question_quality import assess_hard_question
from app.modules.interview.question_bank import pick_curated_fallback_question
from app.modules.knowledge.retriever import _eligible_statement
from tests.problem_examples import sql_problem
from app.modules.interview.generation_errors import QuestionGenerationUnavailable


@pytest.fixture(autouse=True)
def legacy_full_spec_path(monkeypatch):
    """Keep Phase 7/7.1 full-spec regressions; hybrid has its own test module."""
    from app.modules.interview import problem_construction

    monkeypatch.setattr(
        problem_construction, "select_reviewed_family", lambda *args: None
    )


@pytest.mark.parametrize("level", ["internship", "fresher", "Entry Level"])
def test_entry_hard_context_is_medium_but_reasoning_stays_hard(level):
    assert context_difficulty("hard", level) == "medium"
    assert "ENTRY-LEVEL HARD" in difficulty_contract("hard", level)
    stmt = _eligible_statement("SQL", "Software Developer", "hard", level)
    sql = str(
        stmt.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )
    assert "chunks.difficulty = 'medium'" in sql
    assert "software_engineer" in sql


@pytest.mark.parametrize("level", ["intermediate", "experienced", None])
def test_other_hard_retrieval_remains_hard(level):
    assert context_difficulty("hard", level) == "hard"


def test_unknown_role_still_abstains_and_bad_difficulty_fails():
    assert _eligible_statement(role="Not a predefined role") is None
    with pytest.raises(ValueError):
        _eligible_statement(difficulty="impossible")


@pytest.mark.parametrize(
    "text",
    ["What is polymorphism?", "Define binary search.", "List the ACID properties."],
)
def test_direct_phrasing_is_not_a_structural_hard_rejection(text):
    # Appropriateness is semantic; definitions are not banned by their syntax.
    assert validate_generated_question(text, "experienced", "hard", [])[0]


def test_length_preserves_constraints_and_still_bounds_voice_question():
    text = (
        "A reservation has overlapping requests. "
        + "Keep the operation atomic. " * 19
        + "How would you handle a deadlock?"
    )
    assert 420 < len(text) < 900
    assert validate_generated_question(text, "experienced", "hard", [])[0]
    assert not validate_generated_question(text, "experienced", "medium", [])[0]
    assert not validate_generated_question(text * 2, "experienced", "hard", [])[0]


def test_skill_names_are_not_evidence_of_project_ownership():
    assert not validate_generated_question(
        "How did you build your project using SQL?",
        "fresher",
        "medium",
        [],
        {"resume_skills": ["SQL"]},
    )[0]


@pytest.mark.parametrize("pack", [ENTRY, SENIOR])
def test_reviewed_outage_questions_are_bounded_and_distinct(pack):
    assert len(pack) == 10
    assert len(set(pack.values())) == 10
    for question in pack.values():
        assert validate_generated_question(
            question, "fresher" if pack is ENTRY else "experienced", "hard", []
        )[0]


def quality(**overrides):
    return json.dumps(
        {
            **{k: 2 for k in "RTLHECF"},
            "minimum_solution": "Implement the invariant.",
            "observable_edge_effect": "The output changes on a tie.",
            "novelty_comparison": "No previous question.",
            "novel": True,
            "reason": "A bounded implementation decision.",
            **overrides,
        }
    )


def draft(question=None):
    spec = sql_problem().model_dump()
    if question:
        spec["scenario"] = question
    return json.dumps({"problem_spec": spec})


async def generate(provider):
    return await generate_interview_question(
        provider,
        "q_1",
        "Software Engineer",
        "SQL",
        "applied",
        "hard",
        1,
        8,
        {},
        "",
        [],
        "experienced",
    )


def test_hard_review_rejection_is_bounded_and_uses_reviewed_fallback():
    async def run():
        provider = AsyncMock()
        rejected = json.loads(quality())
        rejected.update(H=1, reason="Routine single-row lock example.")
        provider.generate.side_effect = [
            draft(),
            json.dumps(rejected),
            draft(),
            quality(),
        ]
        result = await generate(provider)
        assert provider.generate.await_count == 2
        assert result.topic == "SQL" and result.difficulty == "hard"
        assert result.question_text == SENIOR["sql"]

    anyio.run(run)


def test_review_failure_never_accepts_unreviewed_draft():
    async def run():
        provider = AsyncMock()
        provider.generate.side_effect = [
            draft("A worker has concurrent jobs and can crash. How would you recover?"),
            LLMError("unavailable"),
        ]
        result = await generate(provider)
        assert provider.generate.await_count == 2
        assert result.question_text == SENIOR["sql"]

    anyio.run(run)


def test_repeated_semantic_rejections_are_bounded_and_fall_back():
    async def run():
        provider = AsyncMock()
        rejected = json.loads(quality())
        rejected.update(C=1)
        provider.generate.side_effect = [draft(), json.dumps(rejected)] * 2
        assert (await generate(provider)).question_text == SENIOR["sql"]
        assert provider.generate.await_count == 2

    anyio.run(run)


def test_review_does_not_coerce_untrusted_boolean_strings():
    data = json.loads(quality())
    data["H"] = "true"
    with pytest.raises(ValueError):
        QuestionQuality.model_validate(data)


@pytest.mark.parametrize("stall_at", ["construction", "screen"])
def test_shared_hard_model_deadline_cancels_stalled_call_without_retry(
    monkeypatch, stall_at
):
    import asyncio
    from app.modules.interview import problem_construction

    monkeypatch.setattr(problem_construction, "HARD_MODEL_BUDGET_SECONDS", 0.02)

    async def run():
        canceled = []
        calls = []

        async def respond(**kwargs):
            calls.append(kwargs)
            if stall_at == "screen" and len(calls) == 1:
                return draft()
            try:
                await asyncio.sleep(10)
            except asyncio.CancelledError:
                canceled.append(True)
                raise

        provider = AsyncMock()
        provider.generate.side_effect = respond
        result = await generate(provider)
        assert result.question_text == SENIOR["sql"]
        assert result.difficulty == "hard" and result.topic == "SQL"
        assert len(calls) == (1 if stall_at == "construction" else 2)
        assert canceled == [True]

    anyio.run(run)


def test_easy_generation_has_no_semantic_review_call():
    async def run():
        provider = AsyncMock()
        provider.generate.return_value = json.dumps(
            {
                "topic": "SQL",
                "difficulty": "easy",
                "question_type": "conceptual",
                "question_text": "What is a database transaction?",
            }
        )
        result = await generate_interview_question(
            provider,
            "q_1",
            "Software Engineer",
            "SQL",
            "conceptual",
            "easy",
            1,
            8,
            {},
            "",
            [],
            "fresher",
        )
        assert result.difficulty == "easy"
        assert provider.generate.await_count == 1

    anyio.run(run)


def test_familiarity_is_not_repetition_with_an_empty_history():
    async def run():
        provider = AsyncMock()
        data = json.loads(quality())
        data["novel"] = False
        provider.generate.return_value = json.dumps(data)
        result = await assess_hard_question(
            provider, SENIOR["sql"], "SQL", "Software Engineer", "experienced", []
        )
        assert result.accepted
        prompt = provider.generate.call_args.kwargs["prompt"]
        assert SENIOR["sql"] in prompt
        result = await assess_hard_question(
            provider,
            SENIOR["sql"],
            "SQL",
            "Software Engineer",
            "experienced",
            [SENIOR["sql"]],
        )
        assert not result.accepted

    anyio.run(run)


def test_outage_does_not_invent_work_or_relabel_an_easy_question_hard():
    q = pick_curated_fallback_question(
        "Software Engineer",
        "Unlisted Skill",
        "medium",
        "applied",
        [],
        has_resume_evidence=True,
    )
    assert "your work" not in q.question_text
    assert "How would" in q.question_text
    with pytest.raises(QuestionGenerationUnavailable):
        pick_curated_fallback_question(
            "Software Engineer", "Unlisted Skill", "hard", "conceptual", []
        )
