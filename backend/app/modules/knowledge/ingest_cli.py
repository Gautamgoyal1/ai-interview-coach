"""Preview by default. Apply only an explicitly reviewed approval token."""

import argparse
import asyncio
import json
from pathlib import Path
from sqlalchemy import text
from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.knowledge.ingestion import load_items, build_plan, apply_plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("/app/knowledge_base"))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approve-plan")
    args = parser.parse_args()
    if args.apply and not args.approve_plan:
        parser.error("--apply requires an explicitly approved preview token")
    if settings.embedding_model != "gemini-embedding-001":
        parser.error(
            "Embedding model changes need a separately reviewed full-corpus regeneration plan"
        )
    items = load_items(
        args.root, settings.embedding_model, settings.embedding_dimensions
    )
    if not items:
        parser.error("Knowledge root has no source files; refusing an empty preview")
    with SessionLocal() as db:
        if not args.apply:
            db.execute(text("SET TRANSACTION READ ONLY"))
        plan = build_plan(
            db, items, settings.embedding_model, settings.embedding_dimensions
        )
        print(json.dumps(plan, indent=2))
        if args.apply:
            asyncio.run(
                apply_plan(
                    db,
                    items,
                    settings.embedding_model,
                    settings.embedding_dimensions,
                    args.approve_plan,
                )
            )
            db.commit()
        else:
            db.rollback()


if __name__ == "__main__":
    main()
