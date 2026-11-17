"""Freeze offline Phase 6B input identities and measured cost estimates. No API/DB calls."""

import argparse
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.modules.knowledge.ingestion import load_items, parse_source


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measured(texts):
    texts = list(texts)
    characters = sum(map(len, texts))
    tokens = characters / 4
    return {
        "inputs": len(texts),
        "characters": characters,
        "estimated_tokens": tokens,
        "estimated_usd": tokens * 0.15 / 1_000_000,
        "http_requests": math.ceil(len(texts) / 50),
        "max_input_bytes": max(len(s.encode()) for s in texts),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "storage/phase6b")
    args = parser.parse_args()
    base = args.directory
    read = lambda name: json.loads((base / name).read_text(encoding="utf-8"))
    source = read("software-manifest.json")
    request = read("embedding-request-manifest.json")
    preview = read("preview-software-only.json")
    snapshot = read("legacy-snapshot.json")
    dataset = ROOT / "eval_data/phase6b_software_semantic.json"
    current = [
        asdict(i)
        for i in load_items(
            ROOT / "knowledge_base", source["model"], source["dimensions"]
        )
        if i.role == "software_engineer"
    ]
    if (
        current != source["rows"]
        or request["software_manifest_digest"] != source["digest"]
    ):
        raise ValueError("Sources differ from frozen evaluation inputs")
    if request["dataset_sha256"] != file_hash(dataset):
        raise ValueError("Dataset changed after request preparation")
    if (
        len(current),
        len(request["documents"]),
        len(request["queries"]),
        snapshot["row_count"],
    ) != (30, 61, 30, 31):
        raise ValueError("Unexpected evaluation scope")
    if len(preview["changes"]) != 30 or any(
        c["action"] != "insert" for c in preview["changes"]
    ):
        raise ValueError("Role-only plan must contain exactly 30 inserts")
    costs = {
        "semantic-documents": measured(request["documents"].values()),
        "semantic-queries": measured(request["queries"].values()),
    }
    total = measured([*request["documents"].values(), *request["queries"].values()])
    total["http_requests"] = sum(v["http_requests"] for v in costs.values())
    total["model_limit_token_reservation"] = total["inputs"] * 2048
    total["model_limit_usd_reservation"] = total["inputs"] * 2048 * 0.15 / 1_000_000
    costs.update(
        {
            "semantic-total": total,
            "provider": "Gemini Developer API",
            "rate_usd_per_million_input_tokens": 0.15,
            "pricing_checked_on": "2026-11-15",
            "pricing_url": "https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding",
            "token_method": "characters / 4 heuristic; NOT a provider token count or bill",
            "account_billing_tier": "not verified",
            "paid_calls_executed": 0,
        }
    )
    inventory = []
    for path in sorted((ROOT / "knowledge_base/software_engineering").glob("*.md")):
        meta, _ = parse_source(path)
        inventory.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "knowledge_id": meta["knowledge_id"],
                "revision": int(meta["revision"]),
                "source_sha256": file_hash(path),
            }
        )
    ready = {
        "status": "INPUTS PREPARED; separate paid evaluation approval required; live rollout not approved",
        "sources": inventory,
        "software_manifest_digest": source["digest"],
        "dataset_sha256": file_hash(dataset),
        "evaluation_request_sha256": file_hash(
            base / "embedding-request-manifest.json"
        ),
        "role_only_plan_token": preview["approval_token"],
        "legacy_snapshot_digest": snapshot["digest"],
        "roles": 12,
        "canonical_skills": 54,
        "role_only_inserts": 30,
        "role_only_updates": 0,
        "role_only_retirements": 0,
        "legacy_rows_retained": 31,
        "cost_estimate": total,
        "provider_calls": 0,
        "database_writes": 0,
    }
    for name, value in [
        ("cost-estimate.json", costs),
        ("evaluation-readiness.json", ready),
    ]:
        (base / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(ready, indent=2))


if __name__ == "__main__":
    main()
