"""Opt-in isolated PostgreSQL/pgvector tests, with deterministic non-paid embeddings."""

import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from dataclasses import replace
from unittest.mock import AsyncMock
import anyio
import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.chunk import Chunk
from app.modules.knowledge.ingestion import load_items, build_plan, apply_plan
from app.modules.knowledge import retriever
from app.modules.interview.difficulty_contract import context_difficulty
from app.modules.resume.catalog import resolve_role

pytestmark = pytest.mark.skipif(
    os.getenv("PREPMATE_KNOWLEDGE_POSTGRES") != "1",
    reason="opt-in disposable PostgreSQL schema",
)
ROOT = Path(__file__).resolve().parents[2]
KB = (
    ROOT / "knowledge_base"
    if (ROOT / "knowledge_base" / "software_engineering").is_dir()
    else ROOT.parent / "knowledge_base"
)
EVAL = (
    ROOT / "eval_data"
    if (ROOT / "eval_data" / "phase6_retrieval.json").exists()
    else ROOT.parent / "eval_data"
)


def lexical_vector(value):
    vector = [0.0] * 768
    for token in re.findall(r"[a-z0-9]+", value.lower()):
        index = int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % 768
        vector[index] += 1.0
    return vector


async def fake_embed(values, **kwargs):
    return [lexical_vector(value) for value in values]


@pytest.fixture
def isolated():
    schema = "test_phase6_" + uuid.uuid4().hex
    base = create_engine(settings.database_url)
    with base.begin() as c:
        c.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = base.execution_options(schema_translate_map={None: schema})
    try:
        Chunk.__table__.create(engine)
        with Session(engine) as db:
            yield db
    finally:
        assert re.fullmatch(r"test_phase6_[0-9a-f]{32}", schema)
        with base.begin() as c:
            c.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        base.dispose()


def test_idempotence_updates_retirement_and_embedding_failures(isolated):
    async def scenario():
        db = isolated
        items = load_items(KB / "software_engineering", settings.embedding_model, 768)
        plan = build_plan(db, items, settings.embedding_model, 768)
        embed = AsyncMock(side_effect=fake_embed)
        with pytest.raises(ValueError, match="Approval token"):
            await apply_plan(
                db, items, settings.embedding_model, 768, "not-approved", embed
            )
        embed.assert_not_called()
        broken = AsyncMock(return_value=[[1.0]])
        with pytest.raises(ValueError, match="Embedding result"):
            await apply_plan(
                db, items, settings.embedding_model, 768, plan["approval_token"], broken
            )
        assert db.scalar(select(text("count(*)")).select_from(Chunk)) == 0
        await apply_plan(
            db, items, settings.embedding_model, 768, plan["approval_token"], embed
        )
        db.commit()
        ids = {r.source_name: r.id for r in db.scalars(select(Chunk))}
        second = build_plan(db, items, settings.embedding_model, 768)
        assert second["changes"] == []
        assert second["embedding_inputs"] == 0
        await apply_plan(
            db, items, settings.embedding_model, 768, second["approval_token"], embed
        )
        db.commit()
        assert embed.call_count == 1
        changed = [
            (
                replace(
                    i,
                    content=i.content + "\nReviewed scenario clarification.",
                    content_hash=hashlib.sha256(
                        (i.content_hash + "new").encode()
                    ).hexdigest(),
                )
                if i.subtopic == "http"
                else i
            )
            for i in items
        ]
        update = build_plan(db, changed, settings.embedding_model, 768)
        assert update["changes"] and all(
            c["action"] == "update" for c in update["changes"]
        )
        await apply_plan(
            db, changed, settings.embedding_model, 768, update["approval_token"], embed
        )
        db.commit()
        assert {r.source_name: r.id for r in db.scalars(select(Chunk))} == ids
        retired = [
            replace(i, retired=True) if i.subtopic == "http" else i for i in changed
        ]
        retire = build_plan(db, retired, settings.embedding_model, 768)
        assert all(c["action"] == "retire" for c in retire["changes"])
        await apply_plan(
            db, retired, settings.embedding_model, 768, retire["approval_token"], embed
        )
        db.commit()
        assert not list(
            db.scalars(
                select(Chunk).where(Chunk.subtopic == "http", Chunk.role != "retired")
            )
        )
        assert list(
            db.scalars(
                select(Chunk).where(Chunk.subtopic == "http", Chunk.role == "retired")
            )
        )
        assert {r.source_name: r.id for r in db.scalars(select(Chunk))} == ids
        assert not build_plan(db, retired, settings.embedding_model, 768)["changes"]

    anyio.run(scenario)


def test_retrieval_evaluation_and_no_cross_role_context(isolated, monkeypatch):
    async def scenario():
        db = isolated
        items = load_items(KB, settings.embedding_model, 768)
        legacy = [i for i in items if not i.source_name.startswith("prepmate:")]
        baseline_plan = build_plan(db, legacy, settings.embedding_model, 768)
        await apply_plan(
            db,
            legacy,
            settings.embedding_model,
            768,
            baseline_plan["approval_token"],
            fake_embed,
        )
        db.commit()
        baseline_rows = retriever._query_chunks_by_embedding(
            db, lexical_vector("Software Engineer HTTP retries"), top_k=3
        )
        assert baseline_rows and all(r.role == "ml_engineer" for r in baseline_rows)
        plan = build_plan(db, items, settings.embedding_model, 768)
        await apply_plan(
            db, items, settings.embedding_model, 768, plan["approval_token"], fake_embed
        )
        db.commit()
        monkeypatch.setattr(
            retriever,
            "_embed_query",
            AsyncMock(side_effect=lambda query: lexical_vector(query)),
        )
        cases = json.loads((EVAL / "phase6_retrieval.json").read_text())
        rows = []
        for case in cases:
            embed_calls = retriever._embed_query.await_count
            got = await retriever.retrieve_chunks_async(
                db,
                case["query"],
                top_k=3,
                role=case["role"],
                topic=case["topic"],
                difficulty=case["difficulty"],
                experience_level=case["experience_level"],
            )
            expected = case["expected_subtopic"]
            # Frozen Phase 6 labels document the old exclusion. Phase 7 intentionally
            # retrieves Medium SQL facts for this entry-level Hard request; leave
            # the historical dataset untouched and make the policy delta explicit.
            if case["id"] == "no-hard-intern":
                assert expected is None
                expected = "sql"
            correct = (
                not got
                if expected is None
                else bool(got) and got[0].subtopic == expected
            )
            rows.append(
                {
                    "id": case["id"],
                    "expected": expected,
                    "retrieved": [r.subtopic for r in got],
                    "correct": correct,
                }
            )
            assert correct, rows[-1]
            if expected is None:
                assert retriever._embed_query.await_count == embed_calls
            if got:
                assert all(
                    r.role
                    in resolve_role(case["role"]).get(
                        "knowledge_roles", [resolve_role(case["role"])["id"]]
                    )
                    for r in got
                )
                assert all(
                    r.difficulty
                    == context_difficulty(case["difficulty"], case["experience_level"])
                    for r in got
                )
        # Demonstrate the previous practice bug: display role labels cannot match stored IDs.
        assert (
            list(db.scalars(select(Chunk).where(Chunk.role == "Software Developer")))
            == []
        )
        assert await retriever.retrieve_chunks_async(
            db, "binary search", role="SWE", topic="Algorithms", difficulty="medium"
        )
        report = {
            "embedding_kind": "deterministic hashed lexical surrogate, not Gemini semantic evaluation",
            "cases": len(rows),
            "passed": sum(r["correct"] for r in rows),
            "case_accuracy": sum(r["correct"] for r in rows) / len(rows),
            "positive_hit_at_1": sum(
                r["correct"] for r in rows if r["expected"] is not None
            )
            / sum(r["expected"] is not None for r in rows),
            "abstention_accuracy": sum(
                r["correct"] for r in rows if r["expected"] is None
            )
            / sum(r["expected"] is None for r in rows),
            "baseline_cross_role_fraction": sum(
                r.role != "software_engineer" for r in baseline_rows
            )
            / len(baseline_rows),
            "role_violations": 0,
            "rows": rows,
            "db_schema": db.bind.get_execution_options()["schema_translate_map"][None],
        }
        print(json.dumps(report, indent=2))
        out = Path("/app/storage/phase6")
        if out.exists():
            (out / "retrieval-evaluation.json").write_text(
                json.dumps(report, indent=2) + "\n"
            )

    anyio.run(scenario)


def test_entry_hard_retrieves_medium_facts_for_all_software_topics(
    isolated, monkeypatch
):
    """New policy test; frozen historical abstention labels stay unchanged."""

    async def scenario():
        items = [
            i
            for i in load_items(KB, settings.embedding_model, 768)
            if i.role == "software_engineer"
        ]
        plan = build_plan(isolated, items, settings.embedding_model, 768)
        await apply_plan(
            isolated,
            items,
            settings.embedding_model,
            768,
            plan["approval_token"],
            fake_embed,
        )
        isolated.commit()
        monkeypatch.setattr(
            retriever,
            "_embed_query",
            AsyncMock(side_effect=lambda q: lexical_vector(q)),
        )
        for topic in {i.topic for i in items}:
            for level in ("fresher", "Internship"):
                rows = await retriever.retrieve_chunks_async(
                    isolated,
                    f"Practical reasoning about {topic}",
                    role="Software Developer",
                    topic=topic,
                    difficulty="hard",
                    experience_level=level,
                )
                assert rows and all(
                    r.role == "software_engineer"
                    and r.difficulty == "medium"
                    and r.topic == topic
                    for r in rows
                )
            senior = await retriever.retrieve_chunks_async(
                isolated,
                topic,
                role="SWE",
                topic=topic,
                difficulty="hard",
                experience_level="experienced",
            )
            assert senior and all(r.difficulty == "hard" for r in senior)

    anyio.run(scenario)


def test_scoped_version_updates_keep_ids_legacy_vectors_and_other_roles(isolated):
    async def scenario():
        items = load_items(KB, settings.embedding_model, 768)
        initial = build_plan(isolated, items, settings.embedding_model, 768)
        await apply_plan(
            isolated,
            items,
            settings.embedding_model,
            768,
            initial["approval_token"],
            fake_embed,
        )
        isolated.commit()

        def snapshot():
            return {
                r.id: (
                    r.source_name,
                    r.role,
                    r.content_hash,
                    r.content,
                    list(map(float, r.embedding)),
                )
                for r in isolated.scalars(select(Chunk))
            }

        before = snapshot()
        scoped = [
            replace(
                i,
                content=i.content + "\nVersioned scenario.",
                content_hash=hashlib.sha256(
                    (i.content_hash + "v4").encode()
                ).hexdigest(),
            )
            for i in items
            if i.role == "software_engineer"
        ]
        plan = build_plan(isolated, scoped, settings.embedding_model, 768)
        assert len(plan["changes"]) == 30 and all(
            c["action"] == "update" for c in plan["changes"]
        )
        await apply_plan(
            isolated,
            scoped,
            settings.embedding_model,
            768,
            plan["approval_token"],
            fake_embed,
        )
        isolated.commit()
        isolated.expire_all()
        after = snapshot()
        assert before.keys() == after.keys()
        assert all(
            before[key] == after[key]
            for key in before
            if before[key][1] != "software_engineer"
        )
        assert not build_plan(isolated, scoped, settings.embedding_model, 768)[
            "changes"
        ]

    anyio.run(scenario)
