"""Apply the frozen Software Engineer-only revision to LOCAL development.

No embedding client is called. Requires passing isolated rehearsal and a fresh
backup. Revalidates within the existing transaction advisory lock, commits once,
then independently verifies. Never automatically restores or deletes records.
"""

import argparse
import asyncio
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "storage/phase6b")]

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models.chunk import Chunk
from app.modules.knowledge.ingestion import load_items, build_plan, apply_plan
from app.modules.knowledge.verification import verify_stored_vector
from rollout_b_checks import canonical, check_rows, state, unchanged_other_data

OUT = ROOT / "storage/phase7"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def inputs():
    manifest = read(OUT / "source-manifest.json")
    preparation = read(OUT / "vector-preparation.json")
    assert sha(OUT / "source-manifest.json") == preparation["source_manifest_sha256"]
    assert sha(OUT / "vectors.json") == preparation["vector_cache_sha256"]
    assert all(
        sha(ROOT / path) == value for path, value in manifest["source_hashes"].items()
    )
    items = [
        i
        for i in load_items(ROOT / "knowledge_base", settings.embedding_model, 768)
        if i.role == "software_engineer"
    ]
    assert [asdict(i) for i in items] == manifest["rows"]
    assert len(items) == 30 and not any(i.retired for i in items)
    cache = read(OUT / "vectors.json")
    assert (
        cache["model"] == settings.embedding_model == "gemini-embedding-001"
        and cache["dimensions"] == 768
    )
    assert cache["document_task_type"] == "RETRIEVAL_DOCUMENT"
    return items, cache


def verify(db, items, cache):
    db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
    rows = list(db.scalars(select(Chunk).order_by(Chunk.id)))
    legacy = [r for r in rows if r.id <= 31]
    values = [
        {
            **{
                k: getattr(r, k)
                for k in (
                    "id",
                    "topic",
                    "subtopic",
                    "difficulty",
                    "role",
                    "content",
                    "source_name",
                    "source_url",
                    "license",
                    "content_hash",
                )
            },
            "embedding": list(map(float, r.embedding)),
            "created_at": str(r.created_at),
        }
        for r in legacy
    ]
    digest = read(ROOT / "storage/phase6b/legacy-snapshot.json")["digest"]
    assert len(legacy) == 31 and canonical(values) == digest
    new = [r for r in rows if r.id > 31]
    assert len(rows) == 61 and {r.id for r in new} == set(range(62, 92))
    expected = {i.source_name: i for i in items}
    assert {r.source_name for r in new} == set(expected)
    for row in new:
        item = expected[row.source_name]
        assert all(
            getattr(row, k) == v for k, v in asdict(item).items() if k != "retired"
        )
        verify_stored_vector(
            row.embedding,
            cache["documents"][hashlib.sha256(item.content.encode()).hexdigest()],
        )
    from collections import Counter

    assert Counter(r.difficulty for r in new) == {"easy": 10, "medium": 10, "hard": 10}
    plan = build_plan(db, items, settings.embedding_model, 768)
    assert not plan["changes"] and plan["embedding_inputs"] == 0
    return dict(
        total=61,
        legacy_verified=31,
        software_engineer=30,
        easy=10,
        medium=10,
        hard=10,
        vectors_verified=30,
        legacy_digest=digest,
        idempotent=True,
    )


async def main(apply_local=False):
    url = make_url(settings.database_url)
    assert url.host in {"db", "localhost", "127.0.0.1"}, "Local-only operator"
    assert read(OUT / "isolated-rehearsal.json")["passed"]
    assert (
        sha(OUT / "before-phase7.dump") == read(OUT / "preflight.json")["backup_sha256"]
    )
    items, cache = inputs()
    engine = create_engine(url.set(host="127.0.0.1"))
    receipt_path = OUT / "local-update-receipt.json"
    if not apply_local:
        with Session(engine) as db:
            db.execute(text("SET TRANSACTION READ ONLY"))
            print(json.dumps(verify(db, items, cache), indent=2))
        return
    assert (
        not receipt_path.exists()
    ), "Receipt exists: use verification mode, do not reapply"
    baseline = read(OUT / "preflight.json")["baseline"]

    async def cached_embed(texts, **kwargs):
        assert kwargs["task_type"] == "RETRIEVAL_DOCUMENT"
        return [
            cache["documents"][hashlib.sha256(t.encode()).hexdigest()] for t in texts
        ]

    with Session(engine, expire_on_commit=False) as db:
        db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        db.execute(text("SELECT pg_advisory_xact_lock(634220061)"))
        items, cache = inputs()  # Recheck files/cache inside lock.
        assert state(lambda sql: list(db.execute(text(sql)).scalars())) == baseline
        check_rows(db, True)  # Original rollout remains intact before updates.
        plan = build_plan(db, items, settings.embedding_model, 768)
        assert plan == read(OUT / "preview.json")
        assert len(plan["changes"]) == 24 and plan["unchanged"] == 6
        assert all(
            c["action"] == "update" and c["old_id"] in range(62, 92)
            for c in plan["changes"]
        )
        await apply_plan(
            db,
            items,
            settings.embedding_model,
            768,
            plan["approval_token"],
            cached_embed,
        )
        verification = verify(db, items, cache)
        unchanged_other_data(
            baseline, state(lambda sql: list(db.execute(text(sql)).scalars()))
        )
        db.commit()
        # Preserve committed IDs even if independent post-commit verification fails.
        receipt = dict(
            committed=True,
            passed=False,
            updated_ids=[c["old_id"] for c in plan["changes"]],
            plan_identifier=plan["approval_token"],
            manifest_sha256=sha(OUT / "source-manifest.json"),
            cache_sha256=sha(OUT / "vectors.json"),
            inserts=0,
            updates=24,
            deletions=0,
            retirements=0,
            provider_calls=0,
        )
        receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    with Session(engine) as db:
        db.execute(text("SET TRANSACTION READ ONLY"))
        db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        receipt["verification"] = verify(db, items, cache)
        unchanged_other_data(
            baseline, state(lambda sql: list(db.execute(text(sql)).scalars()))
        )
    receipt["passed"] = True
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply-local", action="store_true")
    asyncio.run(main(parser.parse_args().apply_local))
