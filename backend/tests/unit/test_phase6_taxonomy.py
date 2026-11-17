import json
from pathlib import Path
from unittest.mock import AsyncMock
import anyio
import pytest
from app.modules.resume.catalog import (
    validate_catalog,
    canonical_role_name,
    resolve_role,
    read_json,
)
from app.modules.resume.scoring import (
    load_role_skills,
    load_skill_taxonomy,
    normalize_skill,
    extract_skills,
    calculate_match,
    calculate_match_against_skills,
)
from app.modules.resume.evidence import classify_skills_evidence
from app.modules.resume.fingerprint import compute_analysis_fingerprint, SCORING_VERSION
from app.modules.resume.service import ResumeAnalysisService
from app.modules.resume.schemas import ResumeAnalysisRequest
from app.modules.knowledge.ingestion import load_items, parse_source
from app.modules.knowledge.retriever import retrieval_topics

ROOT = Path(__file__).resolve().parents[2]
KB = (
    (ROOT / "knowledge_base")
    if (ROOT / "knowledge_base" / "software_engineering").is_dir()
    else ROOT.parent / "knowledge_base"
)


def test_catalog_consistency():
    report = validate_catalog()
    assert report["skills"] >= 23 and report["roles"] >= 5
    assert SCORING_VERSION == "1.1"


@pytest.mark.parametrize(
    "alias",
    [
        "Software Developer",
        "Software Engineer",
        "SWE",
        "SDE",
        " software   developer ",
        "software engineer intern",
    ],
)
def test_software_role_aliases(alias):
    assert canonical_role_name(alias) == "software engineer"
    assert resolve_role(alias)["id"] == "software_engineer"


@pytest.mark.parametrize(
    "alias,expected",
    [
        ("OOP", "object-oriented programming"),
        ("JS", "javascript"),
        ("RESTful API", "rest apis"),
        ("Python3", "python"),
        ("sklearn", "scikit-learn"),
    ],
)
def test_skill_aliases(alias, expected):
    assert normalize_skill(alias) == expected
    assert extract_skills(alias) == [expected]


def test_duplicate_keys_rejected(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text('{"python":[],"python":[]}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON key"):
        read_json(path)


def test_taxonomy_does_not_infer_prerequisites_or_award_proficiency():
    assert extract_skills("I plan to learn OOP.") == ["object-oriented programming"]
    evidence = classify_skills_evidence(
        "I plan to learn OOP.", ["object-oriented programming"], load_skill_taxonomy()
    )
    assert evidence["object-oriented programming"] == "planned_or_learning"
    assert (
        calculate_match_against_skills(
            "Python", load_role_skills()["software engineer"]
        )["match_score"]
        == 0
    )
    assert "java" not in extract_skills("JavaScript")


def test_legacy_role_denominator_and_score_unchanged():
    roles = load_role_skills()
    assert roles["python developer"] == ["python", "sql", "docker"]
    assert len(roles["machine learning engineer"]) == 9
    assert calculate_match("Python", "Python and Docker")["match_score"] == 50
    assert calculate_match("Python and Git", "Python and Docker")["match_score"] == 50
    assert (
        calculate_match("Python and Docker", "Python and Docker")["match_score"] == 100
    )


def test_software_role_is_used_by_service_without_jd():
    async def scenario():
        llm = AsyncMock()
        llm.generate.return_value = json.dumps(
            {
                "strengths": ["Your resume lists SQL."],
                "improvement_suggestions": ["Add a concrete test example."],
                "likely_interview_questions": ["How would you test a failed query?"],
            }
        )
        result = await ResumeAnalysisService(llm).analyze(
            b"", ResumeAnalysisRequest(job_role="SWE"), resume_text="SQL and Git"
        )
        assert result.matched_skills == ["git", "sql"]
        assert len(result.missing_skills) == 5
        assert result.match_score == 28.57

    anyio.run(scenario)


def test_catalog_changes_invalidate_fingerprint_not_historical_data():
    _, old = compute_analysis_fingerprint(
        resume_text="SQL", job_role="SWE", taxonomy_digest="old", scoring_version="1.0"
    )
    _, new = compute_analysis_fingerprint(
        resume_text="SQL", job_role="SWE", taxonomy_digest="new"
    )
    assert old != new


def test_source_validation_and_difficulty_sections(tmp_path):
    items = load_items(KB, "gemini-embedding-001", 768)
    swe = [i for i in items if i.role == "software_engineer"]
    assert len(swe) >= 30
    assert {i.difficulty for i in swe} == {"easy", "medium", "hard"}
    assert all(
        "Expected concepts:" in i.content and "https://" in i.content for i in swe
    )
    assert len({i.source_name for i in swe}) == len(swe)
    with pytest.raises(ValueError, match="dimensions"):
        load_items(KB, "other", 1536)
    source = KB / "software_engineering" / "http.md"
    (tmp_path / "first.md").write_text(
        source.read_text(encoding="utf-8"), encoding="utf-8"
    )
    (tmp_path / "duplicate.md").write_text(
        source.read_text(encoding="utf-8"), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="Duplicate or invalid"):
        load_items(tmp_path, "gemini-embedding-001", 768)


def test_representative_answer_concepts_are_accurate():
    items = load_items(KB, "gemini-embedding-001", 768)
    by_sub = {i.subtopic: i.content for i in items if i.role == "software_engineer"}
    assert "not necessarily the same status" in by_sub["http"]
    assert "shifting elements remains linear" in by_sub["algorithms"]
    assert "every contained element must also be hashable" in by_sub["data_structures"]
    assert "not automatically serializable" in by_sub["sql"]
    assert "does not replace authorization" in by_sub["security"]


def test_display_topics_are_separate_from_resume_aliases():
    assert "data_structures" in retrieval_topics("Arrays & Linked Lists")
    assert "security_fundamentals" in retrieval_topics("Authentication & Authorization")
    assert extract_skills("Authentication & Authorization") == []


@pytest.mark.parametrize(
    "alias,expected",
    [
        ("Front-end Engineer", "frontend developer"),
        ("Backend Engineer", "backend developer"),
        ("Full-Stack Engineer", "full stack developer"),
        ("SOC Analyst", "cybersecurity analyst"),
        ("Cloud Engineer", "devops engineer"),
        ("QA Automation Engineer", "qa engineer"),
    ],
)
def test_expanded_role_aliases(alias, expected):
    assert canonical_role_name(alias) == expected


def test_new_role_questions_use_own_fundamentals():
    from app.modules.interview.question_bank import get_role_fundamental_topics

    assert get_role_fundamental_topics("Frontend Developer")[0] == "Html"
    assert "Statistics" in get_role_fundamental_topics("Data Analyst")
    assert "Incident Response" in get_role_fundamental_topics("SOC Analyst")


def test_nested_aliases_do_not_inflate_skill_coverage():
    assert extract_skills("React.js") == ["react"]
    assert extract_skills("Automated testing") == ["test automation"]
    assert extract_skills("Testing and automated testing") == [
        "test automation",
        "testing",
    ]
    assert calculate_match("Automated testing", "Testing")["match_score"] == 0


def test_representative_data_structure_and_sql_semantics():
    import sqlite3

    assert list(dict.fromkeys([3, 1, 3, 2, 1])) == [3, 1, 2]
    with pytest.raises(TypeError):
        hash(([],))
    db = sqlite3.connect(":memory:")
    try:
        db.executescript(
            'CREATE TABLE customers(id INTEGER); CREATE TABLE orders(customer_id INTEGER,status TEXT); INSERT INTO customers VALUES(1),(2); INSERT INTO orders VALUES(1,"paid");'
        )
        assert (
            len(
                db.execute(
                    "SELECT customers.id FROM customers LEFT JOIN orders ON customers.id=orders.customer_id"
                ).fetchall()
            )
            == 2
        )
        assert (
            len(
                db.execute(
                    'SELECT customers.id FROM customers LEFT JOIN orders ON customers.id=orders.customer_id WHERE orders.status="paid"'
                ).fetchall()
            )
            == 1
        )
    finally:
        db.close()


def test_retrieval_query_carries_role_level_type_and_previous_answer(monkeypatch):
    from app.modules.interview.nodes import InterviewNodes

    retrieve = AsyncMock(return_value=[])
    monkeypatch.setattr("app.modules.interview.nodes.retrieve_chunks_async", retrieve)

    async def scenario():
        result = await InterviewNodes(db=object()).retrieve_knowledge(
            {
                "target_role": "Software Developer",
                "selected_topic": "HTTP",
                "experience_level": "intermediate",
                "current_difficulty": "medium",
                "current_question": {"question_type": "applied"},
                "conversation_history": [
                    {
                        "question_text": "What happens on a timeout?",
                        "answer_text": "The POST might already have committed.",
                    }
                ],
            }
        )
        assert result["retrieved_context"] == ""
        args = retrieve.await_args.kwargs
        assert args["role"] == "Software Developer" and args["topic"] == "HTTP"
        assert (
            args["difficulty"] == "medium"
            and args["experience_level"] == "intermediate"
        )
        assert "applied" in args["query"] and "already have committed" in args["query"]

    anyio.run(scenario)


def test_digest_changes_without_a_process_restart(tmp_path, monkeypatch):
    from app.modules.resume import fingerprint

    monkeypatch.setattr(fingerprint, "_RESUME_DIR", tmp_path)
    monkeypatch.setattr(fingerprint, "_ROLES_PATH", tmp_path / "roles.json")
    monkeypatch.setattr(
        fingerprint, "_TAXONOMY_PATH", tmp_path / "skills_taxonomy.json"
    )
    path = tmp_path / "role_catalog.json"
    path.write_text('{"version":1}', encoding="utf-8")
    old = fingerprint.get_taxonomy_digest()
    path.write_text('{"version":2}', encoding="utf-8")
    assert fingerprint.get_taxonomy_digest() != old


def test_ingestion_cli_requires_approval_before_database_or_network(monkeypatch):
    from app.modules.knowledge import ingest_cli

    monkeypatch.setattr("sys.argv", ["ingest_knowledge", "--apply"])
    database = AsyncMock()
    monkeypatch.setattr(ingest_cli, "SessionLocal", database)
    with pytest.raises(SystemExit) as error:
        ingest_cli.main()
    assert error.value.code == 2
    database.assert_not_called()
