"""Integration tests for evidence-aware resume analysis workflow."""

import json
from unittest.mock import AsyncMock, patch

import anyio
import pytest

from app.modules.resume.evidence import (
    classify_skills_evidence,
    baseline_predict,
)
from app.modules.resume.prompts import build_resume_analysis_prompt
from app.modules.resume.schemas import (
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
)
from app.modules.resume.scoring import load_skill_taxonomy
from app.modules.resume.service import (
    ResumeAnalysisError,
    ResumeAnalysisService,
)

VALID_FEEDBACK = {
    "strengths": ["Evidence-supported strength in Python"],
    "improvement_suggestions": ["Demonstrate Docker in an applied project"],
    "likely_interview_questions": [
        "Explain how you built your Python data pipeline."
    ],
}


def create_mock_llm():
    mock = AsyncMock()
    mock.generate.return_value = json.dumps(VALID_FEEDBACK)
    return mock


def extract_prompt_skill_analysis(prompt: str) -> dict:
    start_tag = "<skill_match_analysis>\n"
    end_tag = "\n</skill_match_analysis>"
    start_idx = prompt.index(start_tag) + len(start_tag)
    end_idx = prompt.index(end_tag)
    return json.loads(prompt[start_idx:end_idx])


def test_service_invokes_classifier_and_populates_prompt_evidence():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "Built data transformation pipelines in Python. "
            "Docker is also listed in my technical competencies."
        )
        request = ResumeAnalysisRequest(
            job_role="Data Engineer",
            job_description="Requirements: Python, Docker, and SQL.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            result = await service.analyze(b"%PDF-test", request)

        assert isinstance(result, ResumeAnalysisResult)
        assert result.matched_skills == ["docker", "python"]
        assert result.missing_skills == ["sql"]
        assert result.match_score == pytest.approx(66.67)

        # Inspect the prompt passed to the LLM
        mock_llm.generate.assert_awaited_once()
        call_kwargs = mock_llm.generate.await_args.kwargs
        prompt = call_kwargs["prompt"]
        analysis_data = extract_prompt_skill_analysis(prompt)

        assert "skill_evidence" in analysis_data
        evidence = analysis_data["skill_evidence"]
        assert evidence["python"] == "demonstrated"
        assert evidence["docker"] == "mentioned_only"

    anyio.run(scenario)


def test_demonstrated_skill_alongside_mentioned_only_skill():
    """Verify distinct evidence classifications when one skill is demonstrated and another is only mentioned."""
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "Implemented REST APIs in Python. "
            "Skills: SQL, Docker."
        )
        request = ResumeAnalysisRequest(
            job_role="Software Engineer",
            job_description="Requirements: Python, Docker, and SQL.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            await service.analyze(b"%PDF-test", request)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        assert evidence["python"] == "demonstrated"
        assert evidence["docker"] == "mentioned_only"
        assert evidence["sql"] == "mentioned_only"

    anyio.run(scenario)


def test_skill_alias_does_not_create_duplicate_evidence_entries():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "Trained regression and classification models using sklearn."
        )
        request = ResumeAnalysisRequest(
            job_role="Machine Learning Engineer",
            job_description="Required skill: scikit-learn.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            result = await service.analyze(b"%PDF-test", request)

        assert result.matched_skills == ["scikit-learn"]
        assert result.missing_skills == []

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        # Canonical skill is mapped to demonstrated via its alias
        assert evidence.get("scikit-learn") == "demonstrated"
        # Alias 'sklearn' must not create a duplicate key
        assert "sklearn" not in evidence

    anyio.run(scenario)


def test_unrelated_positive_action_does_not_leak_evidence_to_target_skill():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "Built distributed stream processing systems in Python; "
            "Docker is also mentioned in my toolkit."
        )
        request = ResumeAnalysisRequest(
            job_role="DevOps Engineer",
            job_description="Required skills: Python and Docker.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            await service.analyze(b"%PDF-test", request)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        assert evidence["python"] == "demonstrated"
        assert evidence["docker"] == "mentioned_only"

    anyio.run(scenario)


def test_third_party_use_is_not_credited_to_candidate():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "My teammate built the Docker container deployment pipeline. "
            "I developed Python backend models."
        )
        request = ResumeAnalysisRequest(
            job_role="Backend Developer",
            job_description="Required skills: Python and Docker.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            await service.analyze(b"%PDF-test", request)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        assert evidence["python"] == "demonstrated"
        assert evidence["docker"] == "mentioned_only"

    anyio.run(scenario)


def test_third_party_mention_with_self_denial_is_negated():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "My team used Docker for containerization, but I did not use it myself."
        )
        request = ResumeAnalysisRequest(
            job_role="Engineer",
            job_description="Required skill: Docker.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            await service.analyze(b"%PDF-test", request)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        assert evidence["docker"] == "negated"

    anyio.run(scenario)


def test_coursework_is_labeled_planned_or_learning():
    """Verify coursework is classified as planned_or_learning, preventing false practical claims."""
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = (
            "Completed university coursework introducing machine learning algorithms. "
            "Built data cleaning scripts in pandas."
        )
        request = ResumeAnalysisRequest(
            job_role="ML Intern",
            job_description="Required skills: Machine Learning and Pandas.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            await service.analyze(b"%PDF-test", request)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]

        assert evidence["machine learning"] == "planned_or_learning"
        assert evidence["pandas"] == "demonstrated"

    anyio.run(scenario)


def test_prompt_forbids_praising_negated_or_mentioned_skills_as_strengths():
    """Verify prompt instructions explicitly prevent treating negated or mentioned skills as demonstrated strengths."""
    prompt = build_resume_analysis_prompt(
        resume_text="Some resume",
        job_role="Engineer",
        matched_skills=["docker", "python"],
        skill_evidence={"docker": "negated", "python": "demonstrated"},
    )

    normalized = " ".join(prompt.lower().split())
    assert "heuristic indicator" in normalized
    assert "do not praise skills labeled 'negated', 'mentioned_only', or 'planned_or_learning' as applied practical strengths" in normalized
    assert "do not claim that the candidate has never used a tool outside this resume" in normalized


def test_prompt_instructs_recommendation_to_provide_evidence_not_incompetence():
    """Verify prompt instructs distinguishing missing evidence from claims of candidate incompetence."""
    prompt = build_resume_analysis_prompt(
        resume_text="Skills: Python",
        job_role="Engineer",
        matched_skills=["python"],
        missing_skills=["docker"],
    )

    normalized = " ".join(prompt.lower().split())
    assert "a missing skill means the matching process did not find evidence for it" in normalized
    assert "it does not prove that the candidate lacks the skill" in normalized


def test_existing_matched_and_missing_skills_and_score_remain_unchanged():
    """Verify deterministic scores and matched/missing calculations remain identical."""
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        resume_text = "I have never used Docker. Built personal Python tools."
        request = ResumeAnalysisRequest(
            job_role="Software Engineer",
            job_description="Requirements: Python, Docker, and SQL.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value=resume_text,
        ):
            result = await service.analyze(b"%PDF-test", request)

        # Baseline matching logic detects Docker mention and Python mention
        assert result.matched_skills == ["docker", "python"]
        assert result.missing_skills == ["sql"]
        assert result.match_score == pytest.approx(66.67)

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        evidence = extract_prompt_skill_analysis(prompt)["skill_evidence"]
        assert evidence["docker"] == "negated"
        assert evidence["python"] == "demonstrated"

    anyio.run(scenario)


def test_response_schema_compatibility():
    """Ensure the returned model strictly conforms to existing ResumeAnalysisResult schema."""
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        request = ResumeAnalysisRequest(
            job_role="Machine Learning Engineer",
            job_description="Python and Docker required.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value="Built Python services.",
        ):
            result = await service.analyze(b"%PDF-test", request)

        dumped = result.model_dump()
        expected_keys = {
            "job_role",
            "resume_skills",
            "matched_skills",
            "missing_skills",
            "match_score",
            "strengths",
            "improvement_suggestions",
            "likely_interview_questions",
        }
        assert set(dumped.keys()) == expected_keys

    anyio.run(scenario)


def test_empty_or_non_technical_resume_handled_cleanly():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)

        request = ResumeAnalysisRequest(
            job_role="Software Engineer",
            job_description="Python required.",
        )

        with patch(
            "app.modules.resume.service.extract_resume_text",
            return_value="General project management without any tech keywords.",
        ):
            result = await service.analyze(b"%PDF-test", request)

        assert result.matched_skills == []
        assert result.missing_skills == ["python"]
        assert result.match_score == 0.0

        prompt = mock_llm.generate.await_args.kwargs["prompt"]
        analysis_data = extract_prompt_skill_analysis(prompt)
        assert analysis_data["skill_evidence"] == {}

    anyio.run(scenario)


def test_empty_resume_text_raises_analysis_error():
    async def scenario():
        mock_llm = create_mock_llm()
        service = ResumeAnalysisService(llm=mock_llm)
        request = ResumeAnalysisRequest(job_role="Engineer")

        with patch(
            "app.modules.resume.service.extract_resume_text",
            side_effect=ValueError("The uploaded PDF contains no readable text."),
        ):
            with pytest.raises(ResumeAnalysisError, match="no readable text"):
                await service.analyze(b"%PDF-test", request)

    anyio.run(scenario)


# ---------------------------------------------------------------------------
# Precedence & Aggregation Unit Tests
# ---------------------------------------------------------------------------


def test_precedence_demonstrated_over_mentioned_only_for_multiple_aliases():
    """When a resume lists a skill in a skills section but demonstrates an alias in a project, demonstrated wins."""
    taxonomy = load_skill_taxonomy()
    text = (
        "Technical Skills: Scikit-learn, Python.\n"
        "Projects: Trained random forest models using sklearn for customer analytics."
    )
    evidence = classify_skills_evidence(
        text=text,
        skills=["scikit-learn"],
        taxonomy=taxonomy,
    )
    assert evidence["scikit-learn"] == "demonstrated"
    assert "sklearn" not in evidence


def test_precedence_personal_project_over_professional_denial():
    """Denial of professional use does not cancel demonstrated personal project experience."""
    taxonomy = load_skill_taxonomy()
    text = "Never used Python at work, but built personal scripts and tools."
    evidence = classify_skills_evidence(
        text=text,
        skills=["python"],
        taxonomy=taxonomy,
    )
    assert evidence["python"] == "demonstrated"


def test_precedence_coursework_over_practical_denial():
    """Coursework takes precedence over denial of practical experience."""
    taxonomy = load_skill_taxonomy()
    text = "No practical experience with scikit-learn; completed a course introducing its API."
    evidence = classify_skills_evidence(
        text=text,
        skills=["scikit-learn"],
        taxonomy=taxonomy,
    )
    assert evidence["scikit-learn"] == "planned_or_learning"


def test_classify_skills_evidence_empty_and_unknown_skills():
    """Handle empty skill list and unknown skill gracefully."""
    taxonomy = load_skill_taxonomy()
    # Empty skills list
    assert classify_skills_evidence("Some text", [], taxonomy) == {}
    # Skill not present in text falls back to mentioned_only
    assert classify_skills_evidence("Some text", ["rust"], taxonomy) == {
        "rust": "mentioned_only"
    }
    # Empty text
    assert classify_skills_evidence("", ["python"], taxonomy) == {
        "python": "mentioned_only"
    }
