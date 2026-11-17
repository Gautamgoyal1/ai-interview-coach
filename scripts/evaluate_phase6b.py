"""Offline scoring only. Reads snapshots/cached vectors; never contacts any provider or database."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.modules.resume.catalog import resolve_role
from app.modules.knowledge.retriever import retrieval_topics


def eligible_metadata(rows, case, topic_gate=True):
    profile = resolve_role(case["role"])
    if profile is None or case["interview_type"] == "hr":
        return []
    if case["difficulty"] == "hard" and case["experience_level"] in {
        "internship",
        "fresher",
    }:
        return []
    topics = set(retrieval_topics(case["topic_display"])) if topic_gate else None
    return [
        r
        for r in rows
        if r["role"] in profile.get("knowledge_roles", [profile["id"]])
        and r["role"] != "retired"
        and r["difficulty"] == case["difficulty"]
        and (topics is None or r["topic"] in topics or r["subtopic"] in topics)
    ]


def text_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def lexical_vector(value):
    vector = [0.0] * 768
    for token in re.findall(r"[a-z0-9]+", value.lower()):
        vector[
            int.from_bytes(hashlib.sha256(token.encode()).digest()[:4], "big") % 768
        ] += 1
    return vector


def cosine(left, right):
    denominator = math.sqrt(sum(x * x for x in left) * sum(x * x for x in right))
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0


def family(row):
    return (
        row["source_name"].split(":")[1]
        if row["source_name"].startswith("prepmate:")
        else "legacy:" + str(row["id"])
    )


def relevance(row, case):
    current = family(row)
    return (
        3
        if current == case["primary_family"]
        else 1 if current in case["secondary_families"] else 0
    )


def metrics(ranked, candidates, case):
    ranks = [
        i + 1 for i, row in enumerate(ranked) if family(row) == case["primary_family"]
    ]
    first = min(ranks) if ranks else math.inf
    gains = [2 ** relevance(row, case) - 1 for row in ranked[:3]]
    ideal = sorted([2 ** relevance(row, case) - 1 for row in candidates], reverse=True)[
        :3
    ]
    dcg = sum(value / math.log2(i + 2) for i, value in enumerate(gains))
    idcg = sum(value / math.log2(i + 2) for i, value in enumerate(ideal))
    return {
        "hit_at_1": float(first <= 1),
        "hit_at_3": float(first <= 3),
        "reciprocal_rank": 1 / first,
        "ndcg_at_3": dcg / idcg if idcg else 0.0,
    }


def legacy_metrics(ranked, candidates, case):
    grades = case.get("legacy_relevance_by_row_id", {})
    grade = lambda row: grades.get(str(row["id"]), 0)
    gains = [2 ** grade(row) - 1 for row in ranked[:3]]
    ideal = sorted([2 ** grade(row) - 1 for row in candidates], reverse=True)[:3]
    dcg = sum(value / math.log2(i + 2) for i, value in enumerate(gains))
    idcg = sum(value / math.log2(i + 2) for i, value in enumerate(ideal))
    return {
        "legacy_has_substantial_support": any(grade(row) >= 2 for row in candidates),
        "legacy_substantial_support_at_3": any(grade(row) >= 2 for row in ranked[:3]),
        "legacy_ndcg_at_3": dcg / idcg if idcg else None,
    }


def validate_vector(vector, dimensions=768):
    if (
        len(vector) != dimensions
        or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vector)
        or not any(vector)
    ):
        raise ValueError("Invalid cached embedding")
    return vector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "storage" / "phase6b")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=ROOT / "eval_data" / "phase6b_software_semantic.json",
    )
    parser.add_argument(
        "--vectors",
        type=Path,
        help="Previously approved Gemini outputs; this script cannot generate them",
    )
    parser.add_argument(
        "--surrogate",
        action="store_true",
        help="Explicitly non-semantic lexical diagnostic",
    )
    args = parser.parse_args()
    if bool(args.vectors) == args.surrogate:
        parser.error("Choose either --vectors or --surrogate")
    manifest = read(args.directory / "software-manifest.json")
    snapshot = read(args.directory / "legacy-snapshot.json")
    data = read(args.dataset)
    cases = data["cases"]
    dataset_hash = hashlib.sha256(args.dataset.read_bytes()).hexdigest()
    software = manifest["rows"]
    legacy = snapshot["rows"]
    if data.get("legacy_snapshot_digest") != snapshot["digest"]:
        raise ValueError("Legacy judgments do not match the frozen snapshot")
    # Mirror the historical legacy ingest input, including its subtopic prefix.
    docs = {text_hash(row["content"]): row["content"] for row in software}
    docs.update(
        {
            text_hash(
                f"{r['subtopic']}: {r['content']}"
            ): f"{r['subtopic']}: {r['content']}"
            for r in legacy
        }
    )
    queries = {
        text_hash(c["query"]): c["query"]
        for c in cases
        if not c["expected_runtime_abstention"]
    }
    requests = {
        "model": manifest["model"],
        "dimensions": manifest["dimensions"],
        "dataset_sha256": dataset_hash,
        "software_manifest_digest": manifest["digest"],
        "document_task_type": "RETRIEVAL_DOCUMENT",
        "query_task_type": "RETRIEVAL_QUERY",
        "documents": docs,
        "queries": queries,
        "approval_status": "NOT APPROVED; this file is an input manifest, not an API invocation",
    }
    (args.directory / "embedding-request-manifest.json").write_text(
        json.dumps(requests, indent=2) + "\n", encoding="utf-8"
    )
    if args.surrogate:
        dv = {key: lexical_vector(value) for key, value in docs.items()}
        qv = {key: lexical_vector(value) for key, value in queries.items()}
        mode = "lexical surrogate; NOT a Gemini semantic result"
    else:
        cache = read(args.vectors)
        for key in [
            "model",
            "dimensions",
            "dataset_sha256",
            "software_manifest_digest",
            "document_task_type",
            "query_task_type",
        ]:
            if cache.get(key) != requests[key]:
                raise ValueError(f"Stale or incompatible embedding cache: {key}")
        dv = {key: validate_vector(cache["documents"][key]) for key in docs}
        qv = {key: validate_vector(cache["queries"][key]) for key in queries}
        mode = "cached Gemini semantic vectors; no calls made by this scorer"
    result = []
    for case in cases:
        if case["expected_runtime_abstention"]:
            # Neither a semantic similarity threshold nor a semantic OOD detector is claimed.
            # These are explicit role/topic policy checks, not ranked negative cases.
            eligible = eligible_metadata(legacy + software, case)
            result.append(
                {
                    "id": case["id"],
                    "kind": "policy abstention",
                    "eligible": len(eligible),
                    "abstained": not eligible,
                }
            )
            continue
        query = qv[text_hash(case["query"])]
        candidates = eligible_metadata(software, case, topic_gate=False)
        if (
            len(candidates)
            != data["criteria"]["candidate_count_per_positive_semantic_query"]
        ):
            raise ValueError(
                "Unexpected candidate scope; do not compare a one-row gate as semantic ranking"
            )
        rank = sorted(
            candidates,
            key=lambda r: cosine(query, dv[text_hash(r["content"])]),
            reverse=True,
        )
        old = sorted(
            legacy,
            key=lambda r: cosine(
                query, dv[text_hash(f"{r['subtopic']}: {r['content']}")]
            ),
            reverse=True,
        )[:3]
        result.append(
            {
                "id": case["id"],
                "kind": "positive",
                "family": case["primary_family"],
                "candidate_count": len(candidates),
                "current_runtime_live_candidates": len(eligible_metadata(legacy, case)),
                "expanded_runtime_topic_candidates": len(
                    eligible_metadata(software, case)
                ),
                "baseline_legacy_wrong_role_at_3": sum(
                    r["role"] != "software_engineer" for r in old
                ),
                "ranked_top3": [family(r) for r in rank[:3]],
                **metrics(rank, candidates, case),
                **legacy_metrics(old, legacy, case),
            }
        )
    positives = [r for r in result if r["kind"] == "positive"]
    averages = {
        key: sum(r[key] for r in positives) / len(positives)
        for key in ["hit_at_1", "hit_at_3", "reciprocal_rank", "ndcg_at_3"]
    }
    counts = Counter(r["family"] for r in positives if r["hit_at_3"])
    criteria = data["criteria"]
    gates = {
        "hit_at_1": averages["hit_at_1"] >= criteria["positive_hit_at_1_min"],
        "hit_at_3": averages["hit_at_3"] >= criteria["positive_hit_at_3_min"],
        "mrr": averages["reciprocal_rank"] >= criteria["mrr_min"],
        "ndcg_at_3": averages["ndcg_at_3"] >= criteria["ndcg_at_3_min"],
        "per_family": all(
            counts[r["primary_family"]] >= criteria["min_primary_hits_per_family"]
            for r in cases
            if r["primary_family"]
        ),
        "policy_negatives": all(
            r["abstained"] for r in result if r["kind"] == "policy abstention"
        ),
    }
    report = {
        "numeric_gates": gates,
        "numeric_gates_passed": all(gates.values()),
        "mode": mode,
        "dataset_sha256": dataset_hash,
        "software_manifest_digest": manifest["digest"],
        "positive_cases": len(positives),
        "legacy_queries_with_substantial_available_support": sum(
            r["legacy_has_substantial_support"] for r in positives
        ),
        "legacy_queries_retrieving_substantial_support_at_3": sum(
            r["legacy_substantial_support_at_3"] for r in positives
        ),
        "policy_negative_cases": len(cases) - len(positives),
        "averages": averages,
        "hits_at_3_by_family": dict(counts),
        "release_decision": (
            "NOT APPROVED: surrogate scores cannot satisfy the semantic gate"
            if args.surrogate
            else "MANUAL SUPPORT/TECHNICAL REVIEW REQUIRED; metrics alone do not approve rollout"
        ),
        "provider_calls": 0,
        "database_writes": 0,
        "results": result,
    }
    filename = (
        "surrogate-diagnostic.json"
        if args.surrogate
        else "cached-semantic-results.json"
    )
    (args.directory / filename).write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in report.items() if k != "results"}, indent=2))


if __name__ == "__main__":
    main()
