"""Practical question guidance; adaptive plans and answer grading are unchanged."""

from app.modules.interview.calibration import normalize_experience_level


def context_difficulty(difficulty: str, experience_level: str | None) -> str:
    # Entry-level Hard still benefits from fundamental factual grounding.
    if difficulty == "hard" and experience_level is not None:
        if normalize_experience_level(experience_level) in {"internship", "fresher"}:
            return "medium"
    return difficulty


def opening_question_type(
    difficulty: str, question_index: int, session_key: str = ""
) -> str:
    """A flexible style schedule, not a validation quota or difficulty plan.

    Over ten positions: Easy 8 direct / 2 applied, Medium 5 / 5, Hard 2 / 8.
    Short/adaptive interviews and safe fallbacks can deviate. Focus (resume,
    project, gap) is independent of whether its question is direct or applied.
    """
    # Existing session IDs rotate late adaptive questions across styles, while
    # keeping refresh/restart deterministic. No new persisted state or quota.
    position = (max(1, question_index) - 1 + sum(session_key.encode("utf-8"))) % 10
    direct = {
        "easy": {0, 1, 2, 4, 5, 6, 7, 9},
        "medium": {0, 2, 4, 6, 8},
        "hard": {4, 9},
    }
    return (
        "conceptual"
        if position in direct.get(difficulty, direct["medium"])
        else "applied"
    )


def difficulty_contract(difficulty: str, experience_level: str) -> str:
    level = normalize_experience_level(experience_level)
    definitions = {
        "easy": "EASY: mostly direct fundamentals (about 80% direct / 20% simple applied across interviews). Short, clear and beginner-friendly.",
        "medium": "MEDIUM: roughly half direct comparisons/concepts and half common implementation or everyday development scenarios. Moderate practical reasoning.",
        "hard": "HARD: roughly 20% direct but challenging and 80% realistic applied/scenario questions across interviews. A concise, familiar coding, SQL, debugging or design problem can be Hard. Standard techniques are welcome.",
    }
    profile = (
        "ENTRY-LEVEL HARD remains basic-to-intermediate applied fundamentals; do not assume senior production responsibility."
        if level in {"internship", "fresher"} and difficulty == "hard"
        else (
            "For internship/fresher candidates use basic-to-intermediate programming and applied fundamentals."
            if level in {"internship", "fresher"}
            else "For experienced candidates ask for independent reasoning, implementation choices, optimization or a relevant trade-off; architecture is optional."
        )
    )
    return (
        definitions.get(difficulty, definitions["medium"])
        + " "
        + profile
        + (
            " These are flexible interview-wide targets, never per-question rejection rules. "
            "Ask one natural question a human interviewer would plausibly ask. Do not add concurrency, distributed systems, "
            "multiple failures or several constraints just to manufacture difficulty. State only assumptions needed to answer. "
            "Do not reveal a solution. Save independent deeper challenges for an answer-aware follow-up."
        )
    )


DOMAINS = (
    "search",
    "collaboration",
    "file storage",
    "analytics",
    "messaging",
    "scheduling",
    "caching",
    "authentication",
    "deployment",
    "e-commerce",
)


def scenario_guidance(question_index: int) -> str:
    domain = DOMAINS[(max(question_index, 1) - 1) % len(DOMAINS)]
    return (
        f"If an applied question is selected, {domain} is an optional setting, not a requirement. "
        "For a direct question omit decorative scenarios. Vary the task, not just the nouns. "
        "Never claim hypothetical work is candidate experience."
    )


def topic_reasoning_guidance(topic: str, experience_level: str, difficulty: str) -> str:
    from app.modules.knowledge.retriever import retrieval_topics

    facts = {
        "data_structures": "Ask about choosing or implementing useful collections, lookup, ordering or traversal; standard algorithms are valid.",
        "algorithms": "Use common coding and problem-solving tasks. State input and desired output; include complexity discussion when useful.",
        "object_oriented_programming": "Use ordinary object responsibilities, composition, interfaces and implementation choices. Do not invent an impossible interface guarantee.",
        "sql": "For query problems define referenced tables/columns and desired rows. Clarify ties, NULLs or missing rows only when they affect the requested output.",
        "http": "Ask about ordinary requests, responses, errors, updates or retries. Do not imply a header alone guarantees exactly-once execution.",
        "rest_apis": "Use realistic API behavior and design decisions; specify the client-visible behavior that matters without adding unrelated races.",
        "git": "Use everyday branch, commit, merge and recovery decisions. Give enough context to choose a safe action, not a mandatory migration incident.",
        "testing": "Ask how to test an observable behavior with useful inputs and assertions; mocks and standard techniques are legitimate answers.",
        "debugging": "Give a symptom or useful evidence and ask how to investigate. Multiple competing hypotheses are optional; do not force overlapping causes to be mutually exclusive.",
        "security_fundamentals": "Use practical validation, authentication or authorization decisions. A revocation question must exercise a permission the user previously held.",
    }
    return (
        " ".join(facts[t] for t in retrieval_topics(topic) if t in facts)
        or "Keep the selected skill and requested experience level central."
    )
