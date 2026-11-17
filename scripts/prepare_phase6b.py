"""Read-only Phase 6B snapshots. Never embeds, applies, retires or alters schemas."""

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.models.chunk import Chunk
from app.modules.knowledge.ingestion import load_items, build_plan
from app.modules.resume.catalog import validate_catalog


def sha(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db-host",
        help="Optional local database hostname override; credentials are never printed",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "storage" / "phase6b")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    catalog = validate_catalog()
    all_items = load_items(
        ROOT / "knowledge_base", settings.embedding_model, settings.embedding_dimensions
    )
    software_items = [
        i
        for i in all_items
        if i.role == "software_engineer" and i.source_name.startswith("prepmate:")
    ]
    folder_items = load_items(
        ROOT / "knowledge_base" / "software_engineering",
        settings.embedding_model,
        settings.embedding_dimensions,
    )
    managed = [i for i in all_items if i.source_name.startswith("prepmate:")]
    url = make_url(settings.database_url)
    if args.db_host:
        url = url.set(host=args.db_host)
    engine = create_engine(url, pool_pre_ping=True)
    plans = {}
    with engine.connect().execution_options(isolation_level="REPEATABLE READ") as conn:
        transaction = conn.begin()
        try:
            conn.execute(text("SET TRANSACTION READ ONLY"))
            assert conn.scalar(text("SHOW transaction_read_only")) == "on"
            with Session(bind=conn) as db:
                rows = list(db.scalars(select(Chunk).order_by(Chunk.id)))
                baseline = [
                    {
                        **{
                            key: getattr(row, key)
                            for key in (
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
                        "embedding": [float(x) for x in row.embedding],
                        "created_at": str(row.created_at),
                    }
                    for row in rows
                ]
                before = sha(baseline)
                for name, items in [
                    ("all", all_items),
                    ("software-folder", folder_items),
                    ("software-only", software_items),
                ]:
                    plans[name] = build_plan(
                        db,
                        items,
                        settings.embedding_model,
                        settings.embedding_dimensions,
                    )
                assert len(rows) == db.scalar(
                    select(text("count(*)")).select_from(Chunk)
                )
                after = sha(
                    [
                        {
                            **{
                                key: getattr(row, key)
                                for key in (
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
                            "embedding": [float(x) for x in row.embedding],
                            "created_at": str(row.created_at),
                        }
                        for row in db.scalars(select(Chunk).order_by(Chunk.id))
                    ]
                )
                assert before == after
                snapshot = {
                    "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                    "read_only": True,
                    "row_count": len(rows),
                    "digest": before,
                    "model_identity": "not stored per legacy row; configured model is not proof of historical model identity",
                    "rows": baseline,
                }
        finally:
            transaction.rollback()
    engine.dispose()
    for name, plan in plans.items():
        (args.output / f"preview-{name}.json").write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8"
        )
    (args.output / "legacy-snapshot.json").write_text(
        json.dumps(snapshot, indent=2) + "\n", encoding="utf-8"
    )
    manifest = {
        "model": settings.embedding_model,
        "dimensions": settings.embedding_dimensions,
        "scope": "software_engineer only; original source metadata preserved",
        "rows": [asdict(i) for i in software_items],
    }
    manifest["digest"] = sha(manifest)
    (args.output / "software-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    measured = {}
    for name, items in [("software-only", software_items), ("all-managed", managed)]:
        inputs = set(i.content for i in items)
        characters = sum(map(len, inputs))
        measured[name] = {
            "rows": len(items),
            "unique_inputs": len(inputs),
            "characters": characters,
            "utf8_bytes": sum(len(s.encode()) for s in inputs),
            "max_input_bytes": max(len(s.encode()) for s in inputs),
            "heuristic_tokens_chars_div_4": characters / 4,
            "heuristic_cost_usd_at_0_15_per_million": characters / 4 * 0.15 / 1_000_000,
        }
    summaries = {
        name: {
            "actions": dict(Counter(c["action"] for c in plan["changes"])),
            "unchanged_in_selected_sources": plan["unchanged"],
            "embedding_inputs": plan["embedding_inputs"],
            "approval_token": plan["approval_token"],
            "orphaned_managed_sources": plan["orphaned_managed_sources"],
        }
        for name, plan in plans.items()
    }
    result = {
        "catalog": catalog,
        "configured_provider": "Gemini Developer API (not Azure)",
        "model": settings.embedding_model,
        "dimensions": settings.embedding_dimensions,
        "gemini_key_present": bool(settings.gemini_api_key),
        "legacy_rows": len(baseline),
        "legacy_snapshot_digest": before,
        "read_only": True,
        "plans": summaries,
        "measured_inputs": measured,
        "paid_requests": 0,
        "live_writes": 0,
    }
    (args.output / "review-summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
