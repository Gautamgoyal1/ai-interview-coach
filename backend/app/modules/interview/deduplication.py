"""Multi-level question deduplication and concept fingerprinting."""

import re

_BOILERPLATE_PREFIXES = (
    r"^can you explain\s+",
    r"^could you explain\s+",
    r"^please explain\s+",
    r"^explain\s+",
    r"^what do you understand by\s+",
    r"^can you describe\s+",
    r"^could you describe\s+",
    r"^describe\s+",
    r"^tell me about\s+",
    r"^what is\s+",
    r"^what are\s+",
)

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "between", "by", "can", "could",
    "do", "does", "explain", "for", "from", "how", "in", "into", "is", "it",
    "of", "on", "or", "please", "should", "that", "the", "their", "them",
    "this", "to", "understand", "use", "used", "using", "what", "when",
    "where", "which", "why", "with", "would", "you", "your",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def normalize_question_text(text: str) -> str:
    """Normalize question text by stripping boilerplate stems and punctuation."""
    cleaned = text.strip().lower()
    for pattern in _BOILERPLATE_PREFIXES:
        cleaned = re.sub(pattern, "", cleaned)
    tokens = [t for t in _TOKEN_RE.findall(cleaned) if t not in _STOPWORDS]
    return " ".join(tokens)


def core_tokens(text: str) -> set[str]:
    """Extract non-stopword stem tokens from a question."""
    norm = normalize_question_text(text)
    return set(norm.split()) if norm else set()


def compute_question_fingerprint(topic: str, question_text: str) -> str:
    """Build a deterministic topic + concept fingerprint for deduplication."""
    norm_topic = re.sub(r"\s+", "_", topic.strip().lower()) or "general"
    tokens = sorted(core_tokens(question_text))
    stem = "_".join(tokens[:6]) if tokens else "empty"
    return f"{norm_topic}::{stem}"


def is_duplicate_or_paraphrase(
    candidate_text: str,
    candidate_topic: str,
    previous_questions: list[str],
    asked_fingerprints: list[str] | None = None,
) -> tuple[bool, str | None]:
    """Detect exact duplicates, concept fingerprint matches, and close paraphrases."""
    cand_raw = candidate_text.strip().lower()
    cand_norm = normalize_question_text(candidate_text)
    cand_tokens = core_tokens(candidate_text)
    cand_fp = compute_question_fingerprint(candidate_topic, candidate_text)

    if asked_fingerprints and cand_fp in set(asked_fingerprints):
        return True, "Matches a previously asked concept fingerprint."

    for prev in previous_questions:
        if not prev:
            continue
        prev_raw = prev.strip().lower()
        if prev_raw == cand_raw:
            return True, "Exact duplicate of a previous question."

        prev_norm = normalize_question_text(prev)
        if cand_norm and prev_norm and cand_norm == prev_norm:
            return True, "Paraphrase of a previous question."

        prev_tokens = core_tokens(prev)
        if cand_tokens and prev_tokens:
            jaccard = len(cand_tokens & prev_tokens) / len(cand_tokens | prev_tokens)
            if jaccard >= 0.60:
                return True, "High concept overlap with a previous question."

    return False, None
