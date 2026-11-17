from app.modules.interview.question_generator import prepare_question_context


def record(topic, contract):
    return (
        f"[{topic}] # Source title\n\n## Definition\nUseful facts.\n\n"
        "## Engineering scenario\nA shared_cart_example intended for beginners.\n\n"
        "## Trade-offs and limitations\nExplicit limitations.\n\n"
        "## Provenance\nhttps://example.org/primary\n\n"
        f"## Hard\nQuestion: {contract}\nExpected concepts: unknown outcomes.\nFollow-up: Why?"
    )


def test_hard_context_keeps_facts_and_provenance_without_worked_templates():
    original = record("oop", "Choose a safe provider capability contract.")
    focused = prepare_question_context(original, "hard")
    assert "Choose a safe provider capability contract." not in focused
    assert "shared_cart_example" not in focused
    assert "Explicit limitations." in focused
    assert "https://example.org/primary" in focused
    assert "## Hard" not in focused and "Useful facts." in focused
    assert "shared_cart_example" in original


def test_multiple_sources_retain_their_own_facts_and_provenance():
    focused = prepare_question_context(
        record("oop", "Provider contract?")
        + "\n\n"
        + record("sql", "Transaction boundary?"),
        "hard",
    )
    assert focused.count("## Definition") == 2
    assert (
        "Provider contract?" not in focused and "Transaction boundary?" not in focused
    )
    assert "shared_cart_example" not in focused


def test_other_levels_and_unstructured_legacy_notes_are_preserved():
    original = record("oop", "Contract?")
    assert prepare_question_context(original, "easy") == original
    assert prepare_question_context(original, "medium") == original
    legacy = "## Hard\nA legacy note without structured question fields."
    assert prepare_question_context(legacy, "hard") == legacy
