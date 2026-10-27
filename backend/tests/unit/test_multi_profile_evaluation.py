"""Unit tests for synthetic profile fixtures and multi-profile evaluation runner."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import anyio
import pytest

from app.modules.resume.evidence import classify_skills_evidence
from app.modules.resume.parser import extract_resume_text
from app.modules.resume.scoring import calculate_match, load_skill_taxonomy
from scripts.evaluate_generated_resume_feedback import (
    check_evidence_alignment_violations,
    evaluate_single_profile,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "synthetic_profiles"
MANIFEST_PATH = FIXTURES_DIR / "synthetic_profiles_manifest.json"


def test_manifest_and_fixtures_exist():
    assert MANIFEST_PATH.exists(), f"Missing manifest at {MANIFEST_PATH}"
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    profiles = manifest.get("profiles", [])
    assert len(profiles) == 4, f"Expected 4 profiles, found {len(profiles)}"

    for profile in profiles:
        base_name = profile["file_base"]
        txt_path = FIXTURES_DIR / f"{base_name}.txt"
        pdf_path = FIXTURES_DIR / f"{base_name}.pdf"
        assert txt_path.exists(), f"Missing {txt_path}"
        assert pdf_path.exists(), f"Missing {pdf_path}"

        # Verify PDF contains readable text
        text = extract_resume_text(pdf_path.read_bytes())
        assert len(text.strip()) > 50, f"PDF text empty in {pdf_path}"


def test_deterministic_evidence_per_profile():
    taxonomy = load_skill_taxonomy()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    for profile in manifest["profiles"]:
        base_name = profile["file_base"]
        txt_path = FIXTURES_DIR / f"{base_name}.txt"
        resume_text = txt_path.read_text(encoding="utf-8")

        expected_evidence = profile.get("expected_evidence", {})
        skills_to_check = list(expected_evidence.keys())

        if skills_to_check:
            evidence = classify_skills_evidence(
                text=resume_text,
                skills=skills_to_check,
                taxonomy=taxonomy,
            )
            for skill, expected_label in expected_evidence.items():
                assert (
                    evidence.get(skill) == expected_label
                ), f"Mismatch in {base_name} for skill '{skill}': got {evidence.get(skill)}, expected {expected_label}"


def test_evidence_alignment_violation_detector():
    prohibited = ["docker", "kubernetes"]

    # Violation case: strength praises prohibited skill
    strengths_with_violation = [
        "Strong fundamentals in Python.",
        "Demonstrated hands-on experience deploying with Docker.",
    ]
    violations = check_evidence_alignment_violations(
        strengths_with_violation, prohibited
    )
    assert len(violations) == 1
    assert violations[0]["prohibited_keyword"] == "docker"

    # Clean case: no prohibited skills in strengths
    clean_strengths = [
        "Strong fundamentals in Python.",
        "Querying relational databases with SQL.",
    ]
    clean_violations = check_evidence_alignment_violations(
        clean_strengths, prohibited
    )
    assert len(clean_violations) == 0


def test_evaluate_single_profile_deterministic_flow():
    async def scenario():
        mock_llm = AsyncMock()
        mock_llm.generate.return_value = json.dumps({
            "strengths": ["Demonstrated Python proficiency."],
            "improvement_suggestions": ["Gain Docker experience."],
            "likely_interview_questions": ["Explain your Python scripts."],
        })

        mock_service = AsyncMock()
        mock_analysis = MagicMock()
        mock_analysis.matched_skills = ["docker", "python", "sql"]
        mock_analysis.missing_skills = []
        mock_analysis.match_score = 60.0
        mock_analysis.strengths = ["Demonstrated Python proficiency."]
        mock_analysis.improvement_suggestions = ["Gain Docker experience."]
        mock_analysis.likely_interview_questions = ["Explain your Python scripts."]
        mock_analysis.job_role = "Junior Machine Learning Engineer"
        mock_analysis.model_dump.return_value = {
            "job_role": "Junior Machine Learning Engineer",
            "matched_skills": ["docker", "python", "sql"],
            "missing_skills": [],
            "match_score": 60.0,
            "strengths": ["Demonstrated Python proficiency."],
            "improvement_suggestions": ["Gain Docker experience."],
            "likely_interview_questions": ["Explain your Python scripts."],
        }
        mock_service.analyze.return_value = mock_analysis

        res = await evaluate_single_profile(
            profile_id="profile_1_negated",
            pdf_bytes=b"%PDF-test",
            resume_text="I have never used Docker. Built Python tools.",
            job_role="Junior Machine Learning Engineer",
            job_description="Requirements: Python, Docker, SQL.",
            service=mock_service,
            judge=None,
            expected_matched_skills=["docker", "python", "sql"],
            prohibited_keywords=["docker"],
        )

        assert res["profile_id"] == "profile_1_negated"
        assert res["item_count"] == 3
        assert res["deterministic_checks"]["matched_skills_match_expected"] is True
        assert len(res["deterministic_checks"]["evidence_alignment_violations"]) == 0
        assert res["section_metrics"]["strengths"]["total_items"] == 1
        assert res["section_metrics"]["improvement_suggestions"]["total_items"] == 1
        assert res["section_metrics"]["likely_interview_questions"]["total_items"] == 1

    anyio.run(scenario)
