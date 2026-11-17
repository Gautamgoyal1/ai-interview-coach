"""Reviewed invariants survive AI variation; no paid calls in this file."""

import asyncio
import copy
import json
from unittest.mock import AsyncMock

import anyio
import pytest

from app.modules.interview.problem_families import (
    FAMILIES,
    FamilyDraft,
    reviewed_families,
    select_reviewed_family,
)
from app.modules.interview.problem_spec import (
    validate_problem,
    render_question,
    ProblemSpecification,
)
from app.modules.interview.problem_construction import construct_hard_question
from app.modules.interview.question_quality import assess_family_question
from app.modules.interview.question_generator import (
    generate_interview_question,
    validate_generated_question,
    _fallback_primary_question,
)
from app.modules.interview.question_families import family_marker
from app.modules.interview.generation_errors import QuestionGenerationUnavailable


def topic_for(family):
    return {
        "oop": "Object-Oriented Programming",
        "security": "Security Fundamentals",
        "data_structures": "Data Structures",
        "rest_apis": "REST APIs",
    }.get(
        family.topic,
        (
            family.topic.upper()
            if family.topic in {"sql", "http"}
            else family.topic.title()
        ),
    )


def draft_for(family, variant="boundary"):
    return FamilyDraft(
        family_id=family.id,
        variant=variant,
        scenario="A software team is improving a service.",
        reasoning_decision="How would you "
        + family.reasoning_goal[0].lower()
        + family.reasoning_goal[1:].rstrip(".")
        + "?",
        follow_up_direction="Explain one additional failure interleaving.",
    )


@pytest.mark.parametrize(
    "family", FAMILIES, ids=lambda f: f.profile + ":" + f.topic + ":" + f.id
)
def test_reviewed_variants_have_complete_bounded_invariant_contracts(family):
    topic = topic_for(family)
    level = "fresher" if family.profile == "entry" else "experienced"
    before = copy.deepcopy(family.contract)
    for variant in ["boundary", "extension"]:
        draft = draft_for(family, variant)
        spec = family.instantiate(draft, "Software Engineer", topic, level)
        question = validate_problem(spec, "Software Engineer", topic, level)
        assert validate_generated_question(question, level, "hard", [], {}, topic)[0]
        assert question.count("?") == 1 and "\n\n" in question
        assert draft.follow_up_direction not in question
        assert all(a not in question for a in family.approaches)
        contract=spec.technical_contract.model_dump()
        visible_fields={
            'general':['input_rules','required_observation','boundary_rule'],
            'oop':['interface_guarantee','caller_workflow','failure_observation'],
            'sql':['eligibility_and_time_scope','missing_rows_and_nulls','join_and_aggregation_rule'],
            'http':['mutation','retry_identity','identity_scope','same_key_different_body','concurrent_or_lost_response_outcome','guarantee_boundary'],
            'debugging':['controlled_experiment','shared_causes_policy'],
            'security':['enforcement_boundary','freshness_rule'],
            'security_boundary':['assets','untrusted_inputs','safety_invariant','allowed_behavior','failure_case'],
        }[contract['kind']]
        assert all(contract[key] in question for key in visible_fields)
        if variant == "extension":
            assert family.extension[1] in question
        # Maximum permitted AI prose must still leave room for every fact.
        full = draft.model_copy(
            update={"scenario": "S" * 100, "reasoning_decision": "Q" * 179 + "?"}
        )
        validate_problem(
            family.instantiate(full, "Software Engineer", topic, level),
            "Software Engineer",
            topic,
            level,
        )
    assert family.contract == before


def test_selected_family_cannot_change_role_topic_profile_or_inject_contract():
    family = reviewed_families("Software Developer", "SQL", "fresher")[0]
    raw = draft_for(family).model_dump()
    raw["technical_contract"] = {"kind": "general"}
    with pytest.raises(ValueError):
        FamilyDraft.model_validate(raw)
    with pytest.raises(ValueError):
        family.instantiate(
            draft_for(family).model_copy(update={"family_id": "other"}),
            "Software Engineer",
            "SQL",
            "fresher",
        )
    assert not reviewed_families("Unlisted Role", "SQL", "fresher")
    assert not reviewed_families("Software Engineer", "Database Indexing", "fresher")
    assert not reviewed_families("Software Engineer", "HR", "experienced")


@pytest.mark.parametrize("level", ["fresher", "experienced"])
def test_variants_share_coverage_and_exhaustion_is_honest(level):
    families = reviewed_families("Software Engineer", "Security Fundamentals", level)
    assert len(families) == 2 and families[1].id == "single_use_reset"
    markers = [family_marker(f.topic, level, f.id) for f in families]
    with pytest.raises(QuestionGenerationUnavailable):
        select_reviewed_family(
            "Software Engineer", "Security Fundamentals", level, 3, markers
        )


def review(**extra):
    return json.dumps(
        dict(
            minimum_reasoning="Implement the interacting invariants and failure boundary.",
            blocking_issue="none",
            quote="",
            reason="A bounded implementation problem requiring concrete reasoning.",
            **extra
        )
    )


def test_hybrid_output_is_provider_authored_compiled_and_screened_without_regeneration():
    async def run():
        family = reviewed_families("Software Engineer", "Data Structures", "fresher")[0]
        draft = draft_for(family, "extension")
        provider = AsyncMock()
        provider.generate.side_effect = [draft.model_dump_json(), review()]
        q = await generate_interview_question(
            provider,
            "q1",
            "Software Engineer",
            "Data Structures",
            "applied",
            "hard",
            1,
            8,
            {},
            "Supporting RAG facts",
            [],
            "fresher",
        )
        assert provider.generate.await_count == 2
        assert q.question_text == render_question(
            family.instantiate(draft, "Software Engineer", "Data Structures", "fresher")
        )
        assert q.reasoning_family == family_marker(
            "data_structures", "fresher", family.id
        )
        assert (
            q.question_text
            != _fallback_primary_question(
                "q1",
                "Software Engineer",
                "Data Structures",
                "hard",
                "applied",
                [],
                "fresher",
            ).question_text
        )
        assert (
            "Supporting RAG facts"
            in provider.generate.call_args_list[0].kwargs["prompt"]
        )

    anyio.run(run)


@pytest.mark.parametrize(
    "failure", ["format", "contradiction", "wrong_family", "timeout", "bad_screen"]
)
def test_failure_is_bounded_and_same_topic_hard(failure, monkeypatch):
    from app.modules.interview import problem_construction

    async def run():
        family = reviewed_families("Software Engineer", "Data Structures", "fresher")[0]
        draft = draft_for(family)
        provider = AsyncMock()
        if failure == "format":
            provider.generate.return_value = "not json"
        elif failure == "wrong_family":
            provider.generate.return_value = draft.model_copy(
                update={"family_id": "wrong"}
            ).model_dump_json()
        elif failure == "bad_screen":
            provider.generate.side_effect = [draft.model_dump_json(), "not json"]
        elif failure == "timeout":
            monkeypatch.setattr(problem_construction, "HARD_MODEL_BUDGET_SECONDS", 0.01)

            async def stall(**kwargs):
                await asyncio.sleep(10)

            provider.generate.side_effect = stall
        else:
            provider.generate.side_effect = [
                draft.model_dump_json(),
                json.dumps(
                    dict(
                        minimum_reasoning="A genuinely contradictory requirement.",
                        blocking_issue="technical",
                        quote="Capacity K",
                        reason="A concrete blocking error in the supplied question.",
                    )
                ),
            ]
        q = await generate_interview_question(
            provider,
            "q1",
            "Software Engineer",
            "Data Structures",
            "applied",
            "hard",
            1,
            8,
            {},
            "",
            [],
            "fresher",
        )
        assert q.difficulty == "hard" and q.topic == "Data Structures"
        assert provider.generate.await_count <= 2
        assert (
            q.question_text
            == _fallback_primary_question(
                "q1",
                "Software Engineer",
                "Data Structures",
                "hard",
                "applied",
                [],
                "fresher",
            ).question_text
        )

    anyio.run(run)


def test_screen_requires_real_quote_but_never_treats_its_judgment_as_ground_truth():
    async def run():
        p = AsyncMock()
        p.generate.return_value = json.dumps(
            dict(
                minimum_reasoning="Reason about state transitions.",
                blocking_issue="clarity",
                quote="invented text",
                reason="A supposed defect requiring a quote.",
            )
        )
        with pytest.raises(ValueError):
            await assess_family_question(
                p,
                "A real candidate question?",
                "SQL",
                "Software Engineer",
                "experienced",
                [],
            )

    anyio.run(run)


def test_long_screen_diagnostics_do_not_discard_a_valid_decision():
    from app.modules.interview.question_quality import parse_family_review

    raw = json.dumps(
        dict(
            minimum_reasoning="Reasoning " * 100,
            blocking_issue="none",
            quote="",
            reason="Evidence " * 100,
        )
    )
    result = parse_family_review(raw, "A real question?", [])
    assert (
        result.accepted
        and 490 <= len(result.minimum_reasoning) <= 500
        and 690 <= len(result.reason) <= 700
    )


def test_older_curated_history_without_family_markers_is_not_recycled_by_ai():
    from app.modules.interview.hard_fallbacks import ENTRY

    selected, marker = select_reviewed_family(
        "Software Engineer",
        "Data Structures",
        "fresher",
        1,
        [],
        [ENTRY["data_structures"]],
    )
    assert selected.id != "recency_eviction"


@pytest.mark.parametrize("topic", ["SQL", "Security Fundamentals"])
def test_outage_fallback_uses_new_distinct_family_after_old_coverage_exhaustion(topic):
    level = "experienced"
    old = (
        [family_marker("sql", level, "reservation_outbox")]
        if topic == "SQL"
        else [family_marker("security", level, "revoked_export_principal")]
    )
    q = _fallback_primary_question(
        "q",
        "Software Engineer",
        topic,
        "hard",
        "applied",
        [],
        level,
        asked_fingerprints=old,
    )
    expected = "snapshot_aggregates" if topic == "SQL" else "single_use_reset"
    assert q.reasoning_family == family_marker(
        "sql" if topic == "SQL" else "security", level, expected
    )


@pytest.mark.parametrize(
    "unavailable",
    [
        "An always-successful publish method.",
        "Universal rewind beyond a retained prefix.",
        "No universal atomic publish operation exists.",
    ],
)
def test_oop_compiler_keeps_the_capability_qualifier_even_with_negative_wording(
    unavailable,
):
    family = reviewed_families(
        "Software Engineer", "Object-Oriented Programming", "experienced"
    )[0]
    spec = family.instantiate(
        draft_for(family),
        "Software Engineer",
        "Object-Oriented Programming",
        "experienced",
    )
    raw = spec.model_dump()
    raw["technical_contract"]["unavailable_capability"] = unavailable
    text = render_question(ProblemSpecification.model_validate(raw))
    assert "Unavailable capability: " + unavailable in text
    assert "Peeked" not in text and spec.reasoning_decision in text


def test_ranked_output_keeps_full_meaning_instead_of_replacing_it_with_only_identity():
    from tests.problem_examples import sql_problem

    raw = sql_problem().model_dump()
    raw["technical_contract"]["outputs"][1][
        "meaning"
    ] = "selected event ID eligible in the reporting window"
    assert raw["technical_contract"]["outputs"][1]["meaning"] in render_question(
        ProblemSpecification.model_validate(raw)
    )
