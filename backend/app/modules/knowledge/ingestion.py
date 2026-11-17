"""Validated, preview-first compilation into the existing 768-dimensional chunks table."""

from dataclasses import dataclass, asdict
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re
from urllib.parse import urlparse

from sqlalchemy import select
from app.db.models.chunk import Chunk, EMBEDDING_DIM
from app.modules.resume.catalog import load_catalog, read_json
from app.modules.knowledge.embeddings import embed_texts

PREFIX = "prepmate:"
SUPPORTED_MODEL = "gemini-embedding-001"
SECTIONS = (
    "Definition",
    "Core principles",
    "Practical applications",
    "Common misconceptions",
    "Engineering scenario",
    "Trade-offs and limitations",
    "Provenance",
)


@dataclass(frozen=True)
class KnowledgeItem:
    source_name: str
    topic: str
    subtopic: str
    difficulty: str
    role: str
    content: str
    source_url: str
    license: str
    content_hash: str
    retired: bool = False


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_source(path):
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if not raw.startswith("---\n") or "\n---\n" not in raw[4:]:
        raise ValueError(f"{path}: missing front matter")
    header, body = raw[4:].split("\n---\n", 1)
    meta = {}
    for line in header.splitlines():
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        key = key.strip()
        if not separator or not key or key in meta:
            raise ValueError(f"{path}: malformed or duplicate metadata")
        meta[key.strip()] = value.strip()
    for name in (
        "topic",
        "subtopic",
        "difficulty",
        "source_name",
        "source_url",
        "license",
    ):
        if not meta.get(name):
            raise ValueError(f"{path}: missing {name}")
    if len(body.strip()) < 100:
        raise ValueError(f"{path}: body too short")
    return meta, body.strip()


def load_items(root: Path, model: str, dimensions: int):
    if dimensions != EMBEDDING_DIM:
        raise ValueError("Embedding dimensions do not match existing chunks schema")
    if model != SUPPORTED_MODEL:
        raise ValueError(
            "Embedding model changes require a separately approved regeneration plan"
        )
    profiles = {r["id"]: r for r in load_catalog()["roles"]}
    roles = set(profiles)
    taxonomy = read_json(Path(__file__).parents[1] / "resume" / "skills_taxonomy.json")
    items, ids, bodies = [], set(), set()
    for path in sorted(root.rglob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        meta, body = parse_source(path)
        if "knowledge_id" not in meta:
            # Preserve the exact legacy hash and content; never silently replace it.
            role = meta.get("role", "ml_engineer")
            h = digest(f"{role}|{meta['topic']}|{body}")
            items.append(
                KnowledgeItem(
                    meta["source_name"],
                    meta["topic"],
                    meta["subtopic"],
                    meta["difficulty"],
                    role,
                    body,
                    meta["source_url"],
                    meta["license"],
                    h,
                )
            )
            continue
        kid = meta["knowledge_id"]
        if kid in ids or not re.fullmatch(r"[a-z][a-z0-9_.-]{2,60}", kid):
            raise ValueError(f"Duplicate or invalid knowledge identifier: {kid}")
        ids.add(kid)
        if (
            meta.get("schema_version") != "1"
            or not meta.get("revision", "").isdigit()
            or int(meta["revision"]) < 1
        ):
            raise ValueError(f"{kid}: invalid schema/revision")
        if meta.get("status") not in {"active", "retired"}:
            raise ValueError(f"{kid}: explicit status required")
        assigned = [r.strip() for r in meta.get("roles", "").split(",")]
        if not assigned or len(assigned) != len(set(assigned)) or set(assigned) - roles:
            raise ValueError(f"{kid}: unknown/duplicate roles")
        if meta.get("skill") not in taxonomy:
            raise ValueError(f"{kid}: unknown canonical skill")
        if any(
            meta["skill"]
            not in profiles[r]["required"]
            + profiles[r]["recommended"]
            + profiles[r]["advanced"]
            for r in assigned
        ):
            raise ValueError(f"{kid}: skill is not relevant to an assigned role")
        if (
            urlparse(meta["source_url"]).scheme != "https"
            or not urlparse(meta["source_url"]).netloc
        ):
            raise ValueError(f"{kid}: HTTPS provenance required")
        if meta["license"] != "CC-BY-4.0 (original PrepMate notes)":
            raise ValueError(f"{kid}: reviewed original-content license required")
        if meta.get("reviewed_on") is None or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}", meta["reviewed_on"]
        ):
            raise ValueError(f"{kid}: review date required")
        date.fromisoformat(meta["reviewed_on"])
        body_hash = digest(body)
        if body_hash in bodies:
            raise ValueError(f"{kid}: duplicate knowledge body")
        bodies.add(body_hash)
        for section in SECTIONS:
            if f"## {section}\n" not in body:
                raise ValueError(f"{kid}: missing {section}")
        shared = body.split("## Easy\n", 1)[0]
        if meta["source_url"] not in shared:
            raise ValueError(f"{kid}: source link must appear in provenance")
        for difficulty in ("easy", "medium", "hard"):
            match = re.search(
                rf"^## {difficulty.title()}\n(.*?)(?=^## |\Z)", body, re.M | re.S
            )
            if not match or any(
                f"{field}:" not in match[1]
                for field in ("Question", "Expected concepts", "Follow-up")
            ):
                raise ValueError(f"{kid}: incomplete {difficulty} question")
            content = f"{shared.strip()}\n\n## {difficulty.title()}\n{match[1].strip()}"
            for role in assigned:
                name = f"{PREFIX}{kid}:{role}:{difficulty}"
                if (
                    len(name) > 128
                    or len(meta["topic"]) > 64
                    or len(meta["subtopic"]) > 128
                    or len(meta["source_url"]) > 512
                ):
                    raise ValueError(f"{kid}: metadata exceeds existing column limits")
                payload = json.dumps(
                    [meta, role, difficulty, content, model, dimensions], sort_keys=True
                )
                items.append(
                    KnowledgeItem(
                        name,
                        meta["topic"],
                        meta["subtopic"],
                        difficulty,
                        role,
                        content,
                        meta["source_url"],
                        meta["license"],
                        digest(payload),
                        meta["status"] == "retired",
                    )
                )
    return items


def build_plan(db, items, model, dimensions):
    if dimensions != EMBEDDING_DIM:
        raise ValueError("Embedding dimension/schema mismatch")
    if model != SUPPORTED_MODEL:
        raise ValueError("Embedding model change is not approved")
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy import text

        schema = (
            db.bind.get_execution_options()
            .get("schema_translate_map", {})
            .get(None, "public")
        )
        vector_type = db.scalar(
            text(
                "SELECT format_type(atttypid,atttypmod) FROM pg_attribute WHERE attrelid=to_regclass(:table) AND attname='embedding' AND NOT attisdropped"
            ),
            {"table": f"{schema}.chunks"},
        )
        if vector_type != f"vector({dimensions})":
            raise ValueError(
                "Database vector column is incompatible; no embeddings requested"
            )
    existing = list(db.scalars(select(Chunk)).all())
    hashes = {r.content_hash for r in existing}
    managed = {}
    for row in existing:
        if row.source_name.startswith(PREFIX):
            if row.source_name in managed:
                raise ValueError("Duplicate managed knowledge identity in database")
            managed[row.source_name] = row
    changes, unchanged = [], 0
    for item in items:
        old = (
            managed.get(item.source_name)
            if item.source_name.startswith(PREFIX)
            else None
        )
        action = (
            "retire"
            if item.retired and old and old.role != "retired"
            else (
                "skip"
                if item.retired
                else (
                    "update"
                    if old and old.content_hash != item.content_hash
                    else "skip" if item.content_hash in hashes else "insert"
                )
            )
        )
        if action == "skip":
            unchanged += 1
        else:
            changes.append(
                {
                    "action": action,
                    "source_name": item.source_name,
                    "old_id": old.id if old else None,
                    "old_hash": old.content_hash if old else None,
                    "new_hash": item.content_hash,
                }
            )
    missing = sorted(set(managed) - {i.source_name for i in items})
    payload = {
        "model": model,
        "dimensions": dimensions,
        "changes": changes,
        "unchanged": unchanged,
        "orphaned_managed_sources": missing,
    }
    payload["approval_token"] = digest(json.dumps(payload, sort_keys=True))
    payload["embedding_inputs"] = len(
        {
            i.content
            for i in items
            if any(
                c["new_hash"] == i.content_hash and c["action"] != "retire"
                for c in changes
            )
        }
    )
    return payload


async def apply_plan(
    db, items, model, dimensions, approval_token, embedder=embed_texts
):
    # Serialize managed ingestion only; no user tables are locked or altered.
    if db.bind.dialect.name == "postgresql":
        from sqlalchemy import text

        db.execute(text("SELECT pg_advisory_xact_lock(634220061)"))
    plan = build_plan(db, items, model, dimensions)
    if approval_token != plan["approval_token"]:
        raise ValueError(
            "Approval token does not match current preview; review a fresh plan"
        )
    by_hash = {i.content_hash: i for i in items}
    pending = [
        by_hash[c["new_hash"]] for c in plan["changes"] if c["action"] != "retire"
    ]
    texts = list(dict.fromkeys(i.content for i in pending))
    vectors = await embedder(texts, task_type="RETRIEVAL_DOCUMENT") if texts else []
    if len(vectors) != len(texts) or any(
        len(v) != dimensions or not all(math.isfinite(x) for x in v) or not any(v)
        for v in vectors
    ):
        raise ValueError(
            "Embedding result count/dimension/values invalid; no chunks written"
        )
    mapped = dict(zip(texts, vectors))
    for change in plan["changes"]:
        row = db.get(Chunk, change["old_id"]) if change["old_id"] else None
        if change["action"] == "retire":
            # Preserve row IDs, source text and historical citations; hide from retrieval.
            row.role = "retired"
            row.content_hash = by_hash[change["new_hash"]].content_hash
            continue
        item = by_hash[change["new_hash"]]
        fields = asdict(item)
        fields.pop("retired")
        fields["embedding"] = mapped[item.content]
        if row:
            for key, value in fields.items():
                setattr(row, key, value)
        else:
            db.add(Chunk(**fields))
    db.flush()
    return plan
