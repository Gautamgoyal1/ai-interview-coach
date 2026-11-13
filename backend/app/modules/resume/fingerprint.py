"""Deterministic content hashing and analysis fingerprinting for resume deduplication."""

from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re

from app.core.config import settings

SCORING_VERSION = "1.0"
EVIDENCE_VERSION = "1.0"
PROMPT_VERSION = "1.0"
FINGERPRINT_VERSION = "1.0"

_RESUME_DIR = Path(__file__).resolve().parent
_TAXONOMY_PATH = _RESUME_DIR / "skills_taxonomy.json"
_ROLES_PATH = _RESUME_DIR / "roles.json"


def normalize_text(text: str | None) -> str:
    """Normalize line endings and trailing/excess blank lines without altering meaning."""
    if not text:
        return ""
    unified = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in unified.split("\n")]
    collapsed = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return collapsed.strip()


def normalize_role(role: str) -> str:
    """Normalize target job role casing and surrounding/internal whitespace."""
    return " ".join(role.strip().lower().split())


@lru_cache(maxsize=1)
def get_taxonomy_digest() -> str:
    """Return a SHA-256 digest of the skill taxonomy and role profile definitions."""
    h = hashlib.sha256()
    for path in (_TAXONOMY_PATH, _ROLES_PATH):
        if path.exists():
            h.update(path.read_bytes())
    return h.hexdigest()


def compute_sha256(value: str) -> str:
    """Return the hex SHA-256 digest of a UTF-8 string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_resume_hash(resume_text: str) -> str:
    """Compute a stable SHA-256 digest of normalized resume text."""
    return compute_sha256(normalize_text(resume_text))


def compute_job_description_hash(job_description: str | None) -> str:
    """Compute a stable SHA-256 digest of normalized job description text."""
    normalized = normalize_text(job_description)
    return compute_sha256(normalized) if normalized else ""


def compute_analysis_fingerprint(
    *,
    resume_text: str,
    job_role: str,
    job_description: str | None = None,
    taxonomy_digest: str | None = None,
    scoring_version: str = SCORING_VERSION,
    evidence_version: str = EVIDENCE_VERSION,
    prompt_version: str = PROMPT_VERSION,
    model_identifier: str | None = None,
) -> tuple[str, str]:
    """Compute (resume_hash, analysis_fingerprint) from all material inputs."""
    resume_hash = compute_resume_hash(resume_text)
    jd_hash = compute_job_description_hash(job_description)
    model_id = model_identifier if model_identifier is not None else (
        settings.gemini_model or settings.azure_openai_model or "default"
    )

    payload = {
        "fingerprint_version": FINGERPRINT_VERSION,
        "resume_hash": resume_hash,
        "role": normalize_role(job_role),
        "job_description_hash": jd_hash,
        "taxonomy_digest": taxonomy_digest or get_taxonomy_digest(),
        "scoring_version": scoring_version,
        "evidence_version": evidence_version,
        "prompt_version": prompt_version,
        "model": model_id,
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return resume_hash, compute_sha256(canonical)
