
"""FastAPI endpoints for resume analysis, persistence, and history."""

import logging
from pathlib import PurePath, PureWindowsPath

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.user import User
from app.db.session import get_db
from app.modules.resume.schemas import (
    ResumeAnalysisHistoryItem,
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
    SavedResumeAnalysis,
)
from app.modules.resume.service import (
    ResumeAnalysisError,
    ResumeAnalysisService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])
service = ResumeAnalysisService()

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/analyze",
    response_model=ResumeAnalysisResult,
    status_code=status.HTTP_200_OK,
)
async def analyze_resume(
    file: UploadFile = File(...),
    job_role: str = Form(..., min_length=2, max_length=150),
    job_description: str | None = Form(
        default=None,
        max_length=15000,
    ),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ResumeAnalysisResult:
    """Analyze a PDF and save the result for the authenticated user."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Please upload a PDF file.",
        )

    try:
        # Read at most 10 MB plus one byte to detect oversized uploads.
        pdf_bytes = await file.read(MAX_PDF_SIZE + 1)

        if len(pdf_bytes) > MAX_PDF_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Resume PDF must be 10 MB or smaller.",
            )

        # Check for a PDF header near the beginning of the file.
        if b"%PDF-" not in pdf_bytes[:1024]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid PDF.",
            )

        request = ResumeAnalysisRequest(
            job_role=job_role,
            job_description=job_description,
        )

        # Analyze before writing anything to the database.
        result = await service.analyze(pdf_bytes, request)

        # Strip directory components from the uploaded filename.
        original_filename = file.filename or "resume.pdf"
        filename = (
            PureWindowsPath(original_filename).name
            if "\\" in original_filename
            else PurePath(original_filename).name
        )
        filename = filename[:255] or "resume.pdf"

        # Save the resume and analysis in one transaction.
        resume = Resume(
            user_id=current_user.id,
            filename=filename,
        )
        db.add(resume)
        db.flush()

        analysis = ResumeAnalysis(
            resume_id=resume.id,
            job_role=request.job_role,
            job_description=request.job_description,
            result_json=result.model_dump(mode="json"),
        )
        db.add(analysis)
        db.commit()

        return result

    except ResumeAnalysisError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()
        logger.exception("Failed to save resume analysis.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The resume analysis could not be saved. Please retry.",
        ) from exc

    finally:
        await file.close()


@router.get(
    "/analyses",
    response_model=list[ResumeAnalysisHistoryItem],
)
def list_resume_analyses(
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ResumeAnalysisHistoryItem]:
    """List saved resume analyses belonging to the current user."""

    records = (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(Resume.user_id == current_user.id)
        .order_by(ResumeAnalysis.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        ResumeAnalysisHistoryItem(
            id=analysis.id,
            filename=resume.filename,
            job_role=analysis.job_role,
            created_at=analysis.created_at,
            match_score=analysis.result_json.get("match_score", 0),
        )
        for analysis, resume in records
    ]


@router.get(
    "/analyses/{analysis_id}",
    response_model=SavedResumeAnalysis,
)
def get_resume_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedResumeAnalysis:
    """Retrieve an analysis only if it belongs to the current user."""

    record = (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(
            ResumeAnalysis.id == analysis_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found.",
        )

    analysis, resume = record

    return SavedResumeAnalysis(
        id=analysis.id,
        filename=resume.filename,
        created_at=analysis.created_at,
        result=ResumeAnalysisResult.model_validate(
            analysis.result_json
        ),
    )
