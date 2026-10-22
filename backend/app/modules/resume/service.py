
"""Orchestrates resume parsing, skill matching, and AI feedback."""

import json
import logging

from pydantic import ValidationError

from app.integrations.llm.base import LLMError
from app.integrations.llm.factory import get_llm_provider
from app.modules.resume.feedback_evaluator import evaluate_feedback
from app.modules.resume.parser import extract_resume_text
from app.modules.resume.prompts import (
    RESUME_ANALYSIS_SYSTEM_PROMPT,
    build_resume_analysis_prompt,
)
from app.modules.resume.schemas import (
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
)
from app.modules.resume.scoring import (
    calculate_match,
    calculate_match_against_skills,
    load_role_skills,
)


logger = logging.getLogger(__name__)


class ResumeAnalysisError(Exception):
    """Raised when resume analysis cannot be completed."""


class ResumeAnalysisService:
    def __init__(self, llm=None):
        self.llm = llm if llm is not None else get_llm_provider()

    async def analyze(
        self,
        pdf_bytes: bytes,
        request: ResumeAnalysisRequest,
    ) -> ResumeAnalysisResult:
        # 1. Extract text from the uploaded PDF.
        try:
            resume_text = extract_resume_text(pdf_bytes)
        except ValueError as exc:
            raise ResumeAnalysisError(str(exc)) from exc

        # 2. Calculate deterministic skill coverage.
        if request.job_description and request.job_description.strip():
            match = calculate_match(
                resume_text,
                request.job_description,
            )
        else:
            role_skills = load_role_skills()
            required_skills = role_skills.get(
                request.job_role.strip().lower()
            )

            if required_skills is None:
                raise ResumeAnalysisError(
                    "This job role has no default skill profile. "
                    "Please provide a job description for accurate "
                    "skill matching."
                )

            match = calculate_match_against_skills(
                resume_text,
                required_skills,
            )

        # 3. Build the prompt using deterministic skill analysis.
        prompt = build_resume_analysis_prompt(
            resume_text=resume_text,
            job_role=request.job_role,
            job_description=request.job_description,
            matched_skills=match["matched_skills"],
            missing_skills=match["missing_skills"],
            match_score=match["match_score"],
        )

        # 4. Request AI feedback.
        try:
            raw_response = await self.llm.generate(
                prompt=prompt,
                system=RESUME_ANALYSIS_SYSTEM_PROMPT,
                json_mode=True,
            )
        except LLMError as exc:
            logger.error(
                "Resume analysis provider failed: %s",
                exc,
            )
            raise ResumeAnalysisError(
                "The AI provider could not complete resume analysis."
            ) from exc

        # 5. Parse the response and validate its schema.
        try:
            feedback = json.loads(raw_response)

            if not isinstance(feedback, dict):
                raise ValueError("Expected a JSON object.")

            result_data = {
                "job_role": request.job_role,
                "resume_skills": match["resume_skills"],
                "matched_skills": match["matched_skills"],
                "missing_skills": match["missing_skills"],
                "match_score": match["match_score"],
                "strengths": feedback["strengths"],
                "improvement_suggestions": feedback[
                    "improvement_suggestions"
                ],
                "likely_interview_questions": feedback[
                    "likely_interview_questions"
                ],
            }

            result = ResumeAnalysisResult.model_validate(result_data)

        except (
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            ValidationError,
        ) as exc:
            logger.error(
                "Invalid resume analysis response: %s",
                exc,
            )
            raise ResumeAnalysisError(
                "The AI returned an invalid resume analysis. Please retry."
            ) from exc

        # 6. Run deterministic quality checks.
        # These generic expectations deliberately avoid using the
        # synthetic benchmark's candidate-specific assumptions.
        quality_expectations = {
            "evaluation_id": "live_resume_feedback",
            "section_expectations": {
                "strengths": {"must_be_nonempty": True},
                "improvement_suggestions": {"must_be_nonempty": True},
                "likely_interview_questions": {"must_be_nonempty": True},
            },
            "not_established_by_resume": [],
        }

        quality_report = evaluate_feedback(
            {
                "strengths": result.strengths,
                "improvement_suggestions": result.improvement_suggestions,
                "likely_interview_questions": (
                    result.likely_interview_questions
                ),
            },
            quality_expectations,
        )

        # Structural failures are not suitable to return to the frontend.
        if not quality_report["structure_checks_passed"]:
            logger.warning(
                "Resume feedback failed structural quality checks: %s",
                quality_report["issues"],
            )
            raise ResumeAnalysisError(
                "The AI returned feedback that failed quality checks. "
                "Please retry."
            )

        # Record other quality warnings without automatically rejecting
        # potentially useful feedback.
        if quality_report["issues"]:
            logger.warning(
                "Resume feedback quality warnings: %s",
                quality_report["issues"],
            )

        return result
