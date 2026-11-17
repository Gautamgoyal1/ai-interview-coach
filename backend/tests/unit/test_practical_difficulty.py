"""Practical difficulty is not a quota, novelty test or architecture requirement."""

import asyncio
import json
from unittest.mock import AsyncMock

import anyio
import pytest

from app.modules.interview.difficulty_contract import opening_question_type
from app.modules.interview.generation_errors import QuestionGenerationUnavailable
from app.modules.interview.nodes import InterviewNodes
from app.modules.interview.question_bank import pick_curated_fallback_question
from app.modules.interview.question_generator import (
    generate_interview_question,
    generate_follow_up_question,
)


@pytest.mark.parametrize(
    "difficulty,direct", [("easy", 80), ("medium", 50), ("hard", 20)]
)
def test_flexible_style_schedule_over_many_positions(difficulty, direct):
    assert (
        sum(opening_question_type(difficulty, i) == "conceptual" for i in range(1, 101))
        == direct
    )


def accepted():
    return json.dumps(
        dict(
            minimum_reasoning="Explain a standard implementation choice.",
            blocking_issue="none",
            quote="",
            reason="Practical, clear and appropriate for this candidate.",
        )
    )


def test_direct_hard_uses_plain_question_without_elaborate_spec_or_repair_chain(
    monkeypatch,
):
    async def run():
        from app.modules.interview import question_generator

        async def no_spec(**kwargs):
            raise AssertionError("No specification needed for a direct question")

        monkeypatch.setattr(question_generator, "construct_hard_question", no_spec)
        p = AsyncMock()
        p.generate.side_effect = [
            json.dumps(
                dict(
                    topic="Data Structures",
                    question_text="When would you choose a hash map over a sorted array for repeated lookups?",
                    difficulty="hard",
                    question_type="conceptual",
                )
            ),
            accepted(),
        ]
        q = await generate_interview_question(
            p,
            "q",
            "Software Engineer",
            "Data Structures",
            "conceptual",
            "hard",
            1,
            8,
            {},
            "",
            [],
            "fresher",
        )
        assert (
            p.generate.await_count == 2
            and q.difficulty == "hard"
            and q.question_type == "conceptual"
        )
        assert "hash map" in q.question_text and q.reasoning_family is None
        assert "technical_contract" not in p.generate.call_args_list[0].kwargs["prompt"]

    anyio.run(run)


@pytest.mark.parametrize("difficulty", ["easy", "medium"])
def test_simple_questions_keep_one_generation_call_and_reject_changed_topic(difficulty):
    async def run():
        p = AsyncMock()
        p.generate.return_value = json.dumps(
            dict(
                topic="SQL",
                difficulty=difficulty,
                question_type="conceptual",
                question_text="What is the difference between WHERE and HAVING?",
            )
        )
        q = await generate_interview_question(
            p,
            "q",
            "Software Engineer",
            "SQL",
            "conceptual",
            difficulty,
            1,
            8,
            {},
            "",
            [],
            "fresher",
        )
        assert (
            p.generate.await_count == 1
            and q.topic == "SQL"
            and q.difficulty == difficulty
        )
        p = AsyncMock()
        p.generate.return_value = json.dumps(
            dict(
                topic="Git",
                difficulty=difficulty,
                question_type="conceptual",
                question_text="What does git rebase do?",
            )
        )
        q = await generate_interview_question(
            p,
            "q",
            "Software Engineer",
            "SQL",
            "conceptual",
            difficulty,
            1,
            8,
            {},
            "",
            [],
            "fresher",
        )
        assert (
            q.topic == "SQL"
            and q.difficulty == difficulty
            and "rebase" not in q.question_text
        )
        assert p.generate.await_count <= 2

    anyio.run(run)


def test_incorrect_direct_hard_is_rejected_and_keeps_same_topic_tier():
    async def run():
        p = AsyncMock()
        p.generate.side_effect = [
            json.dumps(
                dict(
                    topic="HTTP",
                    difficulty="hard",
                    question_type="conceptual",
                    question_text="Which local flag guarantees exactly one email after every timeout?",
                )
            ),
            json.dumps(
                dict(
                    minimum_reasoning="No local flag can prove the external effect happened once.",
                    blocking_issue="technical",
                    quote="guarantees exactly one email",
                    reason="The question demands an impossible external exactly-once guarantee.",
                )
            ),
        ]
        q = await generate_interview_question(
            p,
            "q",
            "Software Engineer",
            "HTTP",
            "conceptual",
            "hard",
            5,
            8,
            {},
            "",
            [],
            "experienced",
        )
        assert (
            q.topic == "HTTP"
            and q.difficulty == "hard"
            and "local flag" not in q.question_text
        )
        assert p.generate.await_count == 2

    anyio.run(run)


def test_direct_hard_timeout_never_submits_an_unreviewed_question(monkeypatch):
    from app.modules.interview import question_generator

    monkeypatch.setattr(question_generator, "HARD_MODEL_BUDGET_SECONDS", 0.02)

    async def run():
        calls = []

        async def respond(**kwargs):
            calls.append(kwargs)
            if len(calls) == 1:
                return json.dumps(
                    dict(
                        topic="SQL",
                        difficulty="hard",
                        question_type="conceptual",
                        question_text="When would an index fail to speed up a query?",
                    )
                )
            await asyncio.sleep(10)

        p = AsyncMock()
        p.generate.side_effect = respond
        q = await generate_interview_question(
            p,
            "q",
            "Software Engineer",
            "SQL",
            "conceptual",
            "hard",
            5,
            8,
            {},
            "",
            [],
            "experienced",
        )
        assert q.difficulty == "hard" and q.topic == "SQL" and len(calls) == 2
        assert q.question_text != "When would an index fail to speed up a query?"

    anyio.run(run)


@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_fallback_exhaustion_never_changes_topic_or_difficulty(difficulty):
    history = []
    for _ in range(30):
        try:
            q = pick_curated_fallback_question(
                "Software Engineer", "SQL", difficulty, "conceptual", history, "fresher"
            )
        except QuestionGenerationUnavailable:
            break
        assert q.topic == "SQL" and q.difficulty == difficulty
        history.append(q.question_text)
    else:
        pytest.fail("Repeated fallbacks must eventually become unavailable")


def test_style_selection_preserves_topic_focus_and_hr_behavior():
    async def run():
        nodes = InterviewNodes()
        base = dict(
            target_role="Software Engineer",
            candidate_context={
                "target_role": "Software Engineer",
                "matched_skills": ["SQL"],
                "resume_skills": ["SQL"],
                "missing_skills": ["Testing"],
                "projects": [],
            },
            asked_topics=[],
            question_index=5,
            max_questions=10,
            current_difficulty="hard",
            experience_level="fresher",
            topic_performance={},
            recent_scores=[],
        )
        tech = await nodes.select_topic(base)
        assert tech["current_question"]["question_type"] == "conceptual"
        assert tech["current_difficulty"] == "hard" and tech["selected_topic"]
        hr = await nodes.select_topic({**base, "interview_type": "hr"})
        assert (
            hr["question_focus"] == "behavioral"
            and hr["current_question"]["question_type"] == "conceptual"
        )

    anyio.run(run)


def test_followup_remains_answer_aware_and_does_not_escalate_a_weak_answer():
    async def run():
        p = AsyncMock()
        p.generate.return_value = json.dumps(
            dict(
                question_text="Could you show which rows your filter would keep?",
                difficulty="easy",
            )
        )
        q = await generate_follow_up_question(
            p,
            "fu",
            "Software Engineer",
            "SQL",
            "medium",
            "How do WHERE and HAVING differ?",
            "I think both run before grouping.",
            dict(
                overall_score=30,
                technical_correctness={"score": 1.5},
                missing_concepts=["group filtering"],
            ),
            "",
            "fresher",
            "understanding_check",
        )
        assert q.is_follow_up and q.difficulty == "easy"
        assert (
            "I think both run before grouping." in p.generate.call_args.kwargs["prompt"]
        )

    anyio.run(run)


def test_empty_nonessential_screen_diagnostic_does_not_force_fallback():
    from app.modules.interview.question_quality import parse_family_review

    result = parse_family_review(
        json.dumps(
            dict(
                minimum_reasoning="",
                blocking_issue="none",
                quote="",
                reason="Suitable.",
            )
        ),
        "When would you use a set?",
        [],
    )
    assert result.accepted


def test_ordinary_debugging_reuses_simple_contract_without_forcing_two_hypotheses():
    from app.modules.interview.problem_families import reviewed_families
    from app.modules.interview.problem_spec import validate_problem
    from tests.unit.test_reviewed_families import draft_for

    family = reviewed_families("Software Engineer", "Debugging", "fresher")[0]
    spec = family.instantiate(
        draft_for(family), "Software Engineer", "Debugging", "fresher"
    )
    assert spec.technical_contract.kind == "general"
    assert "hypotheses" not in spec.technical_contract.model_dump()
    assert validate_problem(spec, "Software Engineer", "Debugging", "fresher")


@pytest.mark.parametrize(
    "difficulty,direct", [("easy", 80), ("medium", 50), ("hard", 20)]
)
def test_late_adaptive_position_varies_across_sessions_without_new_state(
    difficulty, direct
):
    kinds = [opening_question_type(difficulty, 8, str(i)) for i in range(100)]
    assert kinds.count("conceptual") == direct
    assert opening_question_type(
        difficulty, 8, "saved-session"
    ) == opening_question_type(difficulty, 8, "saved-session")
