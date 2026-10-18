
"""Tests for the resume analysis service flow."""

import json
from unittest.mock import AsyncMock, patch

import anyio
import pytest

from app.modules.resume.prompts import (
    RESUME_ANALYSIS_SYSTEM_PROMPT,
    build_resume_analysis_prompt,
)
from app.modules.resume.schemas import (
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
)
from app.modules.resume.service import (
    ResumeAnalysisError,
    ResumeAnalysisService,
)


VALID_FEEDBACK = {
    "strengths": ["Strong Python fundamentals"],
    "improvement_suggestions": [
        "Add more ML project details",
    ],
    "likely_interview_questions": [
        "Explain a machine learning project you built.",
    ],
}


def create_mock_llm(response=None):
    """Create a mock LLM without making real API calls."""
    llm = AsyncMock()
    llm.generate.return_value = (
        json.dumps(VALID_FEEDBACK)
        if response is None
        else response
    )
    return llm


def test_role_defaults_are_used_when_description_is_missing():
    async def scenario():
        mock_llm = create_mock_llm()
        request = ResumeAnalysisRequest(
            job_role="Machine Learning Engineer",
        )
        service = ResumeAnalysisService(llm=mock_llm)

        with (
            patch(
                "app.modules.resume.service.extract_resume_text",
                return_value="Python and machine learning experience",
            ),
            patch(
                "app.modules.resume.service.load_role_skills",
                return_value={
                    "machine learning engineer": [
                        "python",
                        "machine learning",
                        "docker",
                    ]
                },
            ),
        ):
            result = await service.analyze(b"%PDF-test", request)

        assert isinstance(result, ResumeAnalysisResult)
        assert result.match_score == pytest.approx(66.67)
        assert result.matched_skills == [
            "machine learning",
            "python",
        ]
        assert result.missing_skills == ["docker"]
        mock_llm.generate.assert_awaited_once()

    anyio.run(scenario)


def test_job_description_takes_priority():
    async def scenario():
        mock_llm = create_mock_llm()
        request = ResumeAnalysisRequest(
            job_role="Machine Learning Engineer",
            job_description="Python and Docker experience required",
        )
        service = ResumeAnalysisService(llm=mock_llm)

        with (
            patch(
                "app.modules.resume.service.extract_resume_text",
                return_value="Python experience",
            ),
            patch(
                "app.modules.resume.service.load_role_skills",
            ) as mock_load_roles,
        ):
            result = await service.analyze(b"%PDF-test", request)

        assert result.match_score == pytest.approx(50.0)
        assert result.matched_skills == ["python"]
        assert result.missing_skills == ["docker"]
        mock_load_roles.assert_not_called()
        mock_llm.generate.assert_awaited_once()

    anyio.run(scenario)


def test_unknown_role_without_description_raises_error():
    async def scenario():
        mock_llm = create_mock_llm()
        request = ResumeAnalysisRequest(
            job_role="Quantum Engineer",
        )
        service = ResumeAnalysisService(llm=mock_llm)

        with (
            patch(
                "app.modules.resume.service.extract_resume_text",
                return_value="Python experience",
            ),
            patch(
                "app.modules.resume.service.load_role_skills",
                return_value={
                    "python developer": ["python"],
                },
            ),
        ):
            with pytest.raises(
                ResumeAnalysisError,
                match="no default skill profile",
            ):
                await service.analyze(b"%PDF-test", request)

        mock_llm.generate.assert_not_awaited()

    anyio.run(scenario)


def test_invalid_gemini_json_raises_analysis_error():
    async def scenario():
        mock_llm = create_mock_llm("not valid JSON")
        request = ResumeAnalysisRequest(
            job_role="Machine Learning Engineer",
        )
        service = ResumeAnalysisService(llm=mock_llm)

        with (
            patch(
                "app.modules.resume.service.extract_resume_text",
                return_value="Python and machine learning",
            ),
            patch(
                "app.modules.resume.service.load_role_skills",
                return_value={
                    "machine learning engineer": [
                        "python",
                        "machine learning",
                    ]
                },
            ),
        ):
            with pytest.raises(
                ResumeAnalysisError,
                match="invalid resume analysis",
            ):
                await service.analyze(b"%PDF-test", request)

        mock_llm.generate.assert_awaited_once()

    anyio.run(scenario)


def test_system_prompt_requires_evidence_grounding():
    prompt = RESUME_ANALYSIS_SYSTEM_PROMPT.lower()

    assert "never invent skills" in prompt
    assert "do not invent project details" in prompt
    assert "directly supported by the resume" in prompt
    assert "untrusted data" in prompt
    assert "valid json" in prompt


def test_analysis_prompt_includes_resume_and_role():
    prompt = build_resume_analysis_prompt(
        resume_text="Python developer with a machine learning project.",
        job_role="Machine Learning Engineer",
        job_description="Python experience required.",
    )

    assert "Machine Learning Engineer" in prompt
    assert "Python developer with a machine learning project." in prompt
    assert "Python experience required." in prompt
    assert "untrusted data" in prompt.lower()


def test_analysis_prompt_handles_empty_job_description():
    prompt = build_resume_analysis_prompt(
        resume_text="Python developer",
        job_role="Python Developer",
        job_description="   ",
    )

    assert "No job description was provided." in prompt
    assert "Python Developer" in prompt

def test_schema_accepts_unsupported_claims_as_strings():
    """Document that schema validation does not verify factual grounding."""
    result = ResumeAnalysisResult.model_validate(
        {
            "job_role": "Machine Learning Engineer",
            "resume_skills": ["python"],
            "matched_skills": ["python"],
            "missing_skills": ["docker"],
            "match_score": 50.0,
            "strengths": [
                "Deployed a machine learning model achieving 99% accuracy"
            ],
            "improvement_suggestions": [
                "Add more details about deployment"
            ],
            "likely_interview_questions": [
                "Explain how you deployed the model achieving 99% accuracy"
            ],
        }
    )

    assert "99% accuracy" in result.strengths[0]
