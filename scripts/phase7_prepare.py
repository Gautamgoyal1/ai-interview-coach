"""Prepare frozen Phase 7 vectors; no PostgreSQL writes.

Run from the repository root: .venv/Scripts/python.exe scripts/phase7_prepare.py
The local meter stops before $2 estimated usage; existing vectors are reused.
"""

import asyncio
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.core.config import settings
from app.modules.knowledge.embeddings import embed_texts
from app.modules.knowledge.ingestion import load_items
from phase7_meter import Meter

OUT = ROOT / "storage/phase7"
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()


async def main():
    assert (
        settings.embedding_model == "gemini-embedding-001"
        and settings.embedding_dimensions == 768
    )
    assert settings.gemini_api_key
    assert json.loads((OUT / "isolated-rehearsal.json").read_text())["passed"]
    manifest = json.loads((OUT / "source-manifest.json").read_text())
    items = [
        i
        for i in load_items(ROOT / "knowledge_base", settings.embedding_model, 768)
        if i.role == "software_engineer"
    ]
    assert [asdict(i) for i in items] == manifest["rows"]
    old = json.loads((ROOT / "storage/phase6b/approved-vectors.json").read_text())
    cache_path = OUT / "vectors.json"
    cache = (
        json.loads(cache_path.read_text())
        if cache_path.exists()
        else {
            "model": settings.embedding_model,
            "dimensions": 768,
            "document_task_type": "RETRIEVAL_DOCUMENT",
            "documents": {},
        }
    )
    texts = list(dict.fromkeys(i.content for i in items))
    for t in texts:
        if sha(t) in old["documents"]:
            cache["documents"][sha(t)] = old["documents"][sha(t)]
    pending = [t for t in texts if sha(t) not in cache["documents"]]
    # Reviewed English prose, max 3865 chars. Record estimates instead of claiming
    # exact Gemini token usage (the embedding response supplies no usage).
    assert all(len(t) <= 4000 and len(t.encode()) <= 4100 for t in pending)
    meter = Meter(OUT)
    meter.active_case = "knowledge-revision-3"
    meter.observe_gemini()
    if pending:
        vectors = await embed_texts(pending, task_type="RETRIEVAL_DOCUMENT")
        assert len(vectors) == len(pending)
        cache["documents"].update({sha(t): v for t, v in zip(pending, vectors)})
    cache_path.write_text(json.dumps(cache) + "\n")
    summary = dict(
        new_embedding_inputs=len(pending),
        reused_inputs=len(texts) - len(pending),
        source_manifest_sha256=hashlib.sha256(
            (OUT / "source-manifest.json").read_bytes()
        ).hexdigest(),
        vector_cache_sha256=hashlib.sha256(cache_path.read_bytes()).hexdigest(),
        max_estimated_input_tokens_chars_div_4=max(map(len, texts)) / 4,
        exact_embedding_usage_available=False,
        database_writes=0,
    )
    (OUT / "vector-preparation.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
