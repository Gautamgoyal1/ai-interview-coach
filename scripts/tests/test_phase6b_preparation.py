"""Tests for offline benchmark scoring and rollout-scope validation."""

import importlib.util
from pathlib import Path
import math
import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "phase6b_evaluation", ROOT / "scripts" / "evaluate_phase6b.py"
)
evaluation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def row(name):
    return {"source_name": "prepmate:" + name + ":software_engineer:medium"}


def test_ideal_rank_and_discounted_relevance_metrics():
    primary, secondary = row("swe.http"), row("swe.rest")
    case = {"primary_family": "swe.http", "secondary_families": ["swe.rest"]}
    ideal = evaluation.metrics([primary, secondary], [primary, secondary], case)
    assert ideal == {
        "hit_at_1": 1.0,
        "hit_at_3": 1.0,
        "reciprocal_rank": 1.0,
        "ndcg_at_3": 1.0,
    }
    swapped = evaluation.metrics([secondary, primary], [primary, secondary], case)
    assert swapped["hit_at_1"] == 0 and swapped["reciprocal_rank"] == 0.5
    assert swapped["ndcg_at_3"] == pytest.approx(
        (1 + 7 / math.log2(3)) / (7 + 1 / math.log2(3))
    )


def test_policy_scope_does_not_follow_the_gold_answer():
    candidate = {
        "role": "software_engineer",
        "difficulty": "medium",
        "topic": "sql",
        "subtopic": "sql",
    }
    case = {
        "role": "SWE",
        "interview_type": "technical",
        "difficulty": "medium",
        "experience_level": "intermediate",
        "topic_display": "SQL",
        "primary_family": None,
        "expected_runtime_abstention": True,
    }
    assert evaluation.eligible_metadata([candidate], case) == [candidate]
    assert (
        evaluation.eligible_metadata([candidate], {**case, "role": "Quantum Pilot"})
        == []
    )
    assert (
        evaluation.eligible_metadata([candidate], {**case, "interview_type": "hr"})
        == []
    )


def test_bad_cached_vectors_are_rejected():
    for vector in [[1.0] * 767, [0.0] * 768, [float("nan")] + [0.0] * 767]:
        with pytest.raises(ValueError, match="Invalid cached"):
            evaluation.validate_vector(vector)
    assert evaluation.validate_vector([1.0] + [0.0] * 767)[0] == 1.0


def test_software_only_scope_preserves_source_hashes():
    from app.modules.knowledge.ingestion import load_items

    all_items = load_items(ROOT / "knowledge_base", "gemini-embedding-001", 768)
    selected = [i for i in all_items if i.role == "software_engineer"]
    assert len(selected) == 30
    for level in ["easy", "medium", "hard"]:
        assert sum(i.difficulty == level for i in selected) == 10
    assert all(i in all_items for i in selected)
    assert len({i.content_hash for i in selected}) == 30


def test_legacy_relevance_is_not_zeroed_by_its_role_tag():
    old = {"id": 27, "role": "ml_engineer"}
    score = evaluation.legacy_metrics(
        [old], [old], {"legacy_relevance_by_row_id": {"27": 3}}
    )
    assert score["legacy_has_substantial_support"]
    assert score["legacy_ndcg_at_3"] == 1.0
    assert (
        evaluation.legacy_metrics([old], [old], {"legacy_relevance_by_row_id": {}})[
            "legacy_ndcg_at_3"
        ]
        is None
    )


def test_reviewed_sources_have_revisioned_relevant_provenance():
    from app.modules.knowledge.ingestion import parse_source

    for path in (ROOT / "knowledge_base/software_engineering").glob("*.md"):
        meta, body = parse_source(path)
        # Source revisions advanced in Phase 7; preserve the editorial floor.
        assert int(meta["revision"]) >= 2
        assert "Existing Python data-structure and OOP notes" not in body
        assert meta["source_url"] in body.split("## Easy")[0]
    sql = (ROOT / "knowledge_base/software_engineering/sql.md").read_text()
    for reference in [
        "queries-table-expressions.html",
        "transaction-iso.html",
        "sql-update.html",
        "functions-aggregate.html",
        "indexes-types.html",
        "sql-syntax-lexical.html",
    ]:
        assert reference in sql


def test_algorithm_prompt_states_balance_and_worst_case_assumptions():
    from app.modules.knowledge.ingestion import load_items

    items = load_items(
        ROOT / "knowledge_base/software_engineering", "gemini-embedding-001", 768
    )
    hard = next(
        i.content
        for i in items
        if i.source_name == "prepmate:swe.algorithms:software_engineer:hard"
    )
    assert "balanced search tree" in hard
    assert "O(log n + k)" in hard
    assert "Balanced-tree bounds require actual balancing" in hard


def test_oop_prompts_allow_language_choice_and_define_capability_limits():
    from app.modules.knowledge.ingestion import load_items

    items = load_items(
        ROOT / "knowledge_base/software_engineering", "gemini-embedding-001", 768
    )
    prompts = {
        i.difficulty: i.content
        for i in items
        if i.role == "software_engineer" and i.topic == "object_oriented_programming"
    }
    assert "language of your choice" in prompts["easy"]
    assert "language-neutral object example" in prompts["easy"]
    assert "atomic create-if-absent" in prompts["hard"]
    assert "ambiguous timeout outcomes" in prompts["hard"]
    assert "read-then-write adapter does not make B atomic" in prompts["hard"]
    assert "created/already-exists/unknown outcomes" in prompts["hard"]


def test_sql_followup_executes_with_a_quoted_string_literal():
    import sqlite3

    body = (ROOT / "knowledge_base/software_engineering/sql.md").read_text()
    predicate = "WHERE orders.status = 'paid'"
    assert predicate in body
    with sqlite3.connect(":memory:") as db:
        db.executescript(
            "CREATE TABLE customers(id INTEGER); CREATE TABLE orders(customer_id INTEGER, status TEXT); INSERT INTO customers VALUES (1),(2); INSERT INTO orders VALUES (1,'paid');"
        )
        join = "SELECT customers.id FROM customers LEFT JOIN orders ON customers.id = orders.customer_id"
        assert db.execute(join).fetchall() == [(1,), (2,)]
        assert db.execute(join + " " + predicate).fetchall() == [(1,)]
