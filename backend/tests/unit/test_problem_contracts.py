import copy
import json
from unittest.mock import AsyncMock

import anyio
import pytest

from app.modules.interview.problem_spec import (
    ProblemSpecification,
    render_question,
    validate_problem,
)
from app.modules.interview.problem_construction import response_schema
from app.modules.interview.generation_errors import QuestionGenerationUnavailable
from app.modules.interview.question_bank import pick_curated_fallback_question
from app.modules.interview.hard_fallbacks import hard_fallback_candidates
from app.modules.interview.question_generator import prepare_question_context
from app.modules.interview.question_quality import QuestionQuality
from tests.problem_examples import sql_problem, general_problem


@pytest.mark.parametrize(
    "mutation",
    [
        "undefined_ref",
        "undefined_prose",
        "unobservable_tie",
        "missing_key",
        "nonunique_identity",
        "missing_output_grain",
    ],
)
def test_sql_contract_rejects_invalid_relationships(mutation):
    data = sql_problem().model_dump()
    c = data["technical_contract"]
    if mutation == "undefined_ref":
        c["references"][0]["column"] = "access_type"
    if mutation == "undefined_prose":
        data["edge_case"] = "Filter by events.access_type."
    if mutation == "unobservable_tie":
        c["outputs"][1]["sources"][0]["column"] = "created_at"
    if mutation == "missing_key":
        c["tables"][1]["primary_key"] = ["unknown"]
    if mutation == "nonunique_identity":
        c["ranking"]["selected_row_identity"]["column"] = "user_id"
    if mutation == "missing_output_grain":
        c["outputs"] = c["outputs"][1:]
    with pytest.raises(ValueError):
        ProblemSpecification.model_validate(data)


def test_projection_keeps_contracts_hides_answers_and_accepts_alternatives():
    spec = sql_problem()
    text = validate_problem(spec, "Software Engineer", "SQL", "experienced")
    assert "event_id" in text and "events.id" in text and "NULL" in text
    assert "Window rank" not in text and "Index choice" not in text
    assert len(text) <= 900
    assert "LEFT JOIN LATERAL" in spec.valid_alternative_approaches[0]


def test_sql_prose_does_not_misclassify_domains_or_namespaced_functions_as_columns():
    data = sql_problem().model_dump()
    data["scenario"] = (
        "An analytics service at shop.example.com uses pg_catalog functions."
    )
    assert ProblemSpecification.model_validate(data)
    data["edge_case"] = "Filter by `unknown_table.status`."
    with pytest.raises(ValueError):
        ProblemSpecification.model_validate(data)


@pytest.mark.parametrize("kind", ["identity", "tier", "topic_contract", "alternatives"])
def test_no_identity_or_contract_type_substitution(kind):
    spec = sql_problem()
    if kind == "identity":
        with pytest.raises(ValueError):
            validate_problem(spec, "Backend Developer", "SQL", "experienced")
    elif kind == "tier":
        d = spec.model_dump()
        d["requested_difficulty"] = "medium"
        with pytest.raises(ValueError):
            ProblemSpecification.model_validate(d)
    elif kind == "topic_contract":
        d = spec.model_dump()
        d["technical_contract"] = general_problem().technical_contract.model_dump()
        with pytest.raises(ValueError):
            validate_problem(
                ProblemSpecification.model_validate(d),
                "Software Engineer",
                "SQL",
                "experienced",
            )
    else:
        d = spec.model_dump()
        d["valid_alternative_approaches"] = ["One approach", "One approach"]
        with pytest.raises(ValueError):
            ProblemSpecification.model_validate(d)


@pytest.mark.parametrize(
    "before,after",
    [("denied", "denied"), ("allowed", "allowed"), ("denied", "allowed")],
)
def test_revocation_exercises_previously_held_permission(before, after):
    d = general_problem().model_dump()
    d.update(
        topic="Security Fundamentals",
        technical_contract={
            "kind": "security",
            "tested_permission": {
                "principal": "reader",
                "resource": "note",
                "action": "write",
                "before": before,
                "after": after,
                "transition": "The sharing grant is revoked.",
            },
            "enforcement_boundary": "At the server.",
            "freshness_rule": "Check current policy.",
        },
    )
    with pytest.raises(ValueError):
        ProblemSpecification.model_validate(d)


def test_oop_unavailable_capability_cannot_be_promised_achievable():
    d = general_problem().model_dump()
    d.update(
        topic="Object-Oriented Programming",
        technical_contract={
            "kind": "oop",
            "interface_guarantee": "Publish only complete results.",
            "caller_workflow": "Stage, then publish.",
            "failure_observation": "A failed stage remains private.",
            "capability": "achievable",
            "unavailable_capability": "No atomic publication is available.",
            "caller_steps": ["Stage content.", "Publish content."],
        },
    )
    with pytest.raises(ValueError):
        ProblemSpecification.model_validate(d)


def test_oop_projection_marks_unavailable_capability_as_unavailable():
    d = general_problem().model_dump()
    d.update(
        topic="Object-Oriented Programming",
        technical_contract={
            "kind": "oop",
            "interface_guarantee": "Partial results stay private.",
            "caller_workflow": "Start, stage and publish or cancel.",
            "failure_observation": "Failure leaves the previous result visible.",
            "capability": "capability_split_required",
            "unavailable_capability": "An always-successful publish method.",
            "caller_steps": [
                "Stage content privately.",
                "Publish the complete result.",
            ],
        },
    )
    question = render_question(ProblemSpecification.model_validate(d))
    assert "Unavailable capability: An always-successful publish method." in question


def test_debugging_identical_predictions_do_not_distinguish_hypotheses():
    d = general_problem().model_dump()
    d.update(
        topic="Debugging",
        technical_contract={
            "kind": "debugging",
            "hypotheses": [
                {
                    "cause": "A cache key collision.",
                    "predicted_observation": "Both requests return the same value.",
                },
                {
                    "cause": "Shared mutable request state.",
                    "predicted_observation": "Both requests return the same value.",
                },
            ],
            "controlled_experiment": "Control overlap and disable cache.",
            "shared_causes_policy": "Both causes may coexist.",
        },
    )
    with pytest.raises(ValueError):
        ProblemSpecification.model_validate(d)


def test_schema_contains_only_the_selected_contract_and_its_dependencies():
    schema = response_schema("SQL")["properties"]["problem_spec"]
    assert "SQLContract" in schema["$defs"] and "HTTPContract" not in schema["$defs"]


@pytest.mark.parametrize("level", ["fresher", "experienced"])
def test_hard_fallback_exhaustion_is_explicit_not_a_downgrade(level):
    candidates = hard_fallback_candidates("Algorithms", level)
    assert len(candidates) >= 2
    with pytest.raises(QuestionGenerationUnavailable):
        pick_curated_fallback_question(
            "Software Engineer", "Algorithms", "hard", "applied", candidates, level
        )
    with pytest.raises(QuestionGenerationUnavailable):
        pick_curated_fallback_question(
            "Software Engineer", "Unlisted Topic", "hard", "applied", [], level
        )


def test_entry_hard_projection_keeps_facts_not_medium_question_anchor():
    context = "[algorithms] # Notes\n\n## Definition\nBinary search uses sorted input.\n\n## Engineering scenario\nA routine loop bug.\n\n## Medium\nQuestion: Find one lower bound.\nExpected concepts: progress\nFollow-up: Why?"
    result = prepare_question_context(context, "hard", "fresher")
    assert (
        "sorted input" in result
        and "lower bound" not in result
        and "routine loop bug" not in result
    )


def test_seven_axis_screen_never_averages_away_a_critical_failure():
    positive = {
        **{k: 2 for k in "RTLHECF"},
        "novel": True,
        "reason": "A valid bounded implementation task.",
        "minimum_solution": "Preserve the invariant.",
        "observable_edge_effect": "A different output is observed.",
        "novelty_comparison": "No previous question.",
    }
    assert QuestionQuality.model_validate(positive).accepted
    for key in "RTHEC":
        assert not QuestionQuality.model_validate({**positive, key: 1}).accepted
    with pytest.raises(ValueError):
        QuestionQuality.model_validate({**positive, "T": "2"})


def test_compact_provider_draft_builds_a_complete_private_spec_without_repeating_facts():
    from app.modules.interview.problem_spec import materialize_problem

    full = general_problem().model_dump()
    omitted = {
        "role",
        "topic",
        "experience_level",
        "requested_difficulty",
        "assumptions",
        "constraints",
        "observable_goal",
        "edge_case",
    }
    draft = {k: v for k, v in full.items() if k not in omitted}
    spec = materialize_problem(draft, "Software Engineer", "Algorithms", "fresher")
    assert (
        spec.constraints
        and spec.assumptions
        and spec.observable_goal
        and spec.edge_case
    )
    assert len(render_question(spec)) < len(render_question(general_problem()))
    assert "Sorting" not in render_question(spec)


def test_fallback_respects_provider_reasoning_family_not_just_paraphrase_hash():
    from app.modules.interview.question_families import family_marker

    marker = family_marker("data_structures", "fresher", "recency_eviction")
    q = pick_curated_fallback_question(
        "Software Engineer",
        "Data Structures",
        "hard",
        "applied",
        ["Keep recently accessed items in constant time under a bounded capacity."],
        "fresher",
        asked_fingerprints=[marker],
    )
    assert q.difficulty == "hard" and q.topic == "Data Structures"
    assert q.reasoning_family != marker and "stack" in q.question_text


def test_broad_retrieval_alias_does_not_authorize_off_topic_curated_fallback():
    for topic in ("Hash Maps", "Database Indexing", "Authentication & Authorization"):
        with pytest.raises(QuestionGenerationUnavailable):
            pick_curated_fallback_question(
                "Software Engineer", topic, "hard", "applied", [], "fresher"
            )


def test_shared_family_exhaustion_never_rephrases_reservations_or_revocation():
    from app.modules.interview.question_families import family_marker
    from app.modules.interview.problem_construction import select_construction_family

    marker = family_marker("sql", "experienced", "reservation_outbox")
    new = pick_curated_fallback_question(
        "Software Engineer",
        "SQL",
        "hard",
        "applied",
        [],
        "experienced",
        asked_fingerprints=[marker],
    )
    assert new.reasoning_family == family_marker(
        "sql", "experienced", "snapshot_aggregates"
    )
    with pytest.raises(QuestionGenerationUnavailable):
        pick_curated_fallback_question(
            "Software Engineer",
            "SQL",
            "hard",
            "applied",
            [],
            "experienced",
            asked_fingerprints=[marker, new.reasoning_family],
        )
    sec = family_marker("security", "fresher", "authorization_transition")
    with pytest.raises(QuestionGenerationUnavailable) as unavailable:
        select_construction_family("Security Fundamentals", "fresher", 2, [sec])
    assert unavailable.value.reason == "coverage_exhausted"


def test_reasoning_family_is_private_and_stable_across_question_serialization():
    from app.modules.interview.schemas import InterviewQuestion

    q = InterviewQuestion(
        question_id="q1",
        topic="SQL",
        difficulty="hard",
        question_text="A valid question?",
        reasoning_family="private-family",
    )
    assert (
        q.reasoning_family == "private-family"
        and "reasoning_family" not in q.model_dump()
    )
