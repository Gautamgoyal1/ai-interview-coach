"""Experience-evidence classification for resume skills.

Classifies a resume statement about a target skill into one of four
evidence categories:
- 'demonstrated': concrete personal applied work.
- 'mentioned_only': listed or mentioned without sufficient evidence of personal use.
- 'negated': explicitly denies relevant experience or use.
- 'planned_or_learning': coursework, studying, or future learning without applied experience.

Note: This is a heuristic baseline, not a full NLP parser.
"""

import re

LABELS: list[str] = [
    "demonstrated",
    "mentioned_only",
    "negated",
    "planned_or_learning",
]

EVIDENCE_PRECEDENCE: dict[str, int] = {
    "demonstrated": 4,
    "planned_or_learning": 3,
    "negated": 2,
    "mentioned_only": 1,
}


def _contains_any(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def baseline_predict(text: str, skill: str) -> str:
    """Classify evidence for a target skill using conservative heuristics."""

    text = re.sub(r"\s+", " ", text.lower().replace("\u2019", "'")).strip()
    skill = skill.lower().strip()

    if not skill or not text:
        return "mentioned_only"

    skill_pattern = re.escape(skill)

    # Split on punctuation and contrast/conjunction words. Keep the
    # original sentence available for cross-clause reasoning.
    clauses = [
        part.strip()
        for part in re.split(
            r"[;.!?]+|\bbut\b|\balthough\b|\bwhile\b",
            text,
        )
        if part.strip()
    ]

    relevant_indices = [
        index
        for index, clause in enumerate(clauses)
        if re.search(skill_pattern, clause)
    ]

    if not relevant_indices:
        return "mentioned_only"

    learning_patterns = [
        r"\bhope to learn\b",
        r"\bwant to learn\b",
        r"\bplan(?:ning)? to learn\b",
        r"\bwill learn\b",
        r"\bwill explore\b",
        r"\bwill be explored\b",
        r"\bfuture project\b",
        r"\bfuture\b",
        r"\bcurrently taking\b",
        r"\bcompleted (?:an? )?introductory\b",
        r"\bcompleted coursework\b",
        r"\bcoursework\b",
        r"\bcompleted a course\b",
        r"\blearned\b",
        r"\bstudied\b",
        r"\bcourse\b",
        r"\bbasics\b",
        r"\bintroducing\b",
        r"\bintroduced\b",
        r"\btheoretical knowledge\b",
    ]

    negation_patterns = [
        r"\bnever used\b",
        r"\bno (?:practical |hands-on )?experience with\b",
        r"\bno .*?\bexperience with\b",
        r"\bhaven't worked with\b",
        r"\bhave not worked with\b",
        r"\bhaven't used\b",
        r"\bhave not used\b",
        r"\bnot used\b",
        r"\bdid not use\b",
        r"\bdidn't use\b",
        r"\bwas not used\b",
        r"\bwasn't used\b",
        r"\bnot built\b",
        r"\bhave not built\b",
        r"\bhaven't built\b",
        r"\bno hands-on experience\b",
        r"\black hands-on experience\b",
        r"\bnot applied in practice\b",
        r"\bnot used it myself\b",
        r"\bdid not use it myself\b",
        r"\bdidn't use it myself\b",
    ]

    # These patterns indicate that an action may belong to someone else.
    third_party_patterns = [
        r"\bmy teammate\b",
        r"\bmy colleague\b",
        r"\bmy manager\b",
        r"\bmy team\b",
        r"\banother developer\b",
        r"\bmy previous employer\b",
        r"\bmy employer\b",
        r"\bmy team's technology stack\b",
    ]

    evidence_patterns = [
        r"\bbuilt\b",
        r"\bdeveloped\b",
        r"\bcreated\b",
        r"\bimplemented\b",
        r"\bused\b",
        r"\btrained\b",
        r"\bdeployed\b",
        r"\bwrote\b",
        r"\bcleaned\b",
        r"\bevaluated\b",
        r"\bjoined\b",
        r"\bquer(?:y|ied|ies)\b",
        r"\bparsed\b",
        r"\bhandled\b",
        r"\bworked with\b",
        r"\bapplied\b",
        r"\bperformed\b",
        r"\bconfigured\b",
        r"\btested\b",
        r"\banalyzed\b",
        r"\banalysed\b",
    ]

    # Find clauses that attribute the target skill to another party.
    third_party_indices = {
        index
        for index in relevant_indices
        if _contains_any(third_party_patterns, clauses[index])
    }

    # If the target skill is attributed to another party and the candidate
    # explicitly says they did not use it, do not credit the third party's
    # action to the candidate.
    self_denial_patterns = [
        r"\bi did not use it myself\b",
        r"\bi didn't use it myself\b",
        r"\bi never used it myself\b",
        r"\bi did not use\b",
        r"\bi didn't use\b",
    ]

    if (
        third_party_indices
        and _contains_any(self_denial_patterns, text)
    ):
        return "negated"

    # Search the skill-bearing clauses and the immediately following clause.
    # This allows constructions such as:
    # "No experience with scikit-learn; completed a course introducing its API."
    # It does not treat every unrelated action elsewhere in a resume as
    # evidence for this skill.
    relevant_context = set(relevant_indices)

    for index in relevant_indices:
        if index + 1 < len(clauses):
            next_clause = clauses[index + 1]

            # Only extend context when the next clause appears to continue
            # the same topic through a pronoun or learning/course reference.
            continuation_patterns = [
                r"\bits\b",
                r"\bthis\b",
                r"\bthat\b",
                r"\bthe same\b",
                r"\bcourse\b",
                r"\bcoursework\b",
                r"\bdataframes\b",
                r"\bapi\b",
            ]

            if _contains_any(continuation_patterns, next_clause):
                relevant_context.add(index + 1)

    context_clauses = [clauses[index] for index in sorted(relevant_context)]

    # First, look for explicit positive personal evidence connected to the
    # skill. Ignore third-party clauses.
    positive_evidence = False

    for index in relevant_context:
        clause = clauses[index]

        if index in third_party_indices:
            continue

        if not _contains_any(evidence_patterns, clause):
            continue

        # A denial of professional/workplace use does not cancel clear
        # personal-project evidence in the same sentence.
        professional_limited_denial = _contains_any(
            [
                r"\bnever used\b.{0,40}\bprofessionally\b",
                r"\bhaven't used\b.{0,40}\bprofessionally\b",
                r"\bhave not used\b.{0,40}\bprofessionally\b",
                r"\bnever used\b.{0,40}\bat work\b",
                r"\bnot used\b.{0,40}\bat work\b",
                r"\bhaven't used\b.{0,40}\bat work\b",
                r"\bhave not used\b.{0,40}\bat work\b",
            ],
            clause,
        )

        has_negation = _contains_any(negation_patterns, clause)

        if has_negation and not professional_limited_denial:
            continue

        # The positive action must either occur in a clause naming the
        # skill or be a clear continuation of that skill's context.
        positive_evidence = True
        break

    if positive_evidence:
        return "demonstrated"

    # Learning/course evidence takes precedence over a denial of practical
    # experience when both occur in the target skill's relevant context.
    if _contains_any(learning_patterns, " ".join(context_clauses)):
        return "planned_or_learning"

    # Negation in a skill-bearing clause means the skill is not demonstrated.
    if any(
        _contains_any(negation_patterns, clauses[index])
        for index in relevant_indices
    ):
        return "negated"

    # A third party's use without evidence of the candidate's own use
    # should not be credited to the candidate.
    if third_party_indices:
        return "mentioned_only"

    # Conservative fallback: a skill mention is not enough to establish use.
    return "mentioned_only"


def classify_skills_evidence(
    text: str,
    skills: list[str],
    taxonomy: dict[str, list[str]] | None = None,
) -> dict[str, str]:
    """Classify evidence for canonical skills in the supplied text.

    For each canonical skill, checks all associated aliases that appear in
    the text and aggregates the results to the canonical skill key.
    """
    evidence: dict[str, str] = {}
    normalized_text = text.lower()

    for canonical in skills:
        canonical_clean = canonical.strip().lower()
        if not canonical_clean:
            continue

        aliases = (
            taxonomy.get(canonical_clean, [canonical_clean])
            if taxonomy
            else [canonical_clean]
        )

        matched_aliases = [
            alias
            for alias in aliases
            if re.search(
                rf"(?<!\w){re.escape(alias.lower())}(?!\w)",
                normalized_text,
            )
        ]

        if not matched_aliases:
            # Fall back to evaluating the canonical skill name directly
            evidence[canonical_clean] = baseline_predict(text, canonical_clean)
            continue

        # Evaluate evidence for each alias present in the resume
        best_label = "mentioned_only"
        best_rank = 0

        for alias in matched_aliases:
            label = baseline_predict(text, alias)
            rank = EVIDENCE_PRECEDENCE.get(label, 0)
            if rank > best_rank:
                best_rank = rank
                best_label = label

        evidence[canonical_clean] = best_label

    return evidence
