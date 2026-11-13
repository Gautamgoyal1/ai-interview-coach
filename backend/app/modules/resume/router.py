"""FastAPI endpoints for resume analysis, deduplication, persistence, and history."""

import asyncio
from datetime import datetime, timezone
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
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.models.interview_session import InterviewSession
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.user import User
from app.db.session import get_db
from app.modules.interview.graph import clear_session_checkpoints
from app.modules.resume.evidence import classify_skills_evidence
from app.modules.resume.fingerprint import compute_analysis_fingerprint
from app.modules.resume.parser import extract_resume_text
from app.modules.resume.schemas import (
    AnalyzeResumeResponse,
    DeleteAnalysisResponse,
    ResumeAnalysisHistoryItem,
    ResumeAnalysisRequest,
    ResumeAnalysisResult,
    SavedResumeAnalysis,
)
from app.modules.resume.scoring import load_skill_taxonomy
from app.modules.resume.service import (
    ResumeAnalysisError,
    ResumeAnalysisService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/resume", tags=["Resume"])
service = ResumeAnalysisService()

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
_analysis_locks: dict[tuple[int, str], asyncio.Lock] = {}


def _get_analysis_lock(user_id: int, fingerprint: str) -> asyncio.Lock:
    key = (user_id, fingerprint)
    lock = _analysis_locks.get(key)
    if lock is None:
        if len(_analysis_locks) > 1000:
            stale = [k for k, v in _analysis_locks.items() if not v.locked()]
            for k in stale[:500]:
                _analysis_locks.pop(k, None)
        lock = asyncio.Lock()
        _analysis_locks[key] = lock
    return lock


def _sanitize_filename(original: str | None) -> str:
    raw = original or "resume.pdf"
    name = (
        PureWindowsPath(raw).name
        if "\\" in raw
        else PurePath(raw).name
    )
    return name[:255] or "resume.pdf"


def _hydrating_analyze_response(
    analysis: ResumeAnalysis,
    *,
    reused: bool,
) -> AnalyzeResumeResponse:
    payload = dict(analysis.result_json or {})
    payload["analysis_id"] = getattr(analysis, "id", None)
    payload["reused"] = reused
    payload["version"] = getattr(analysis, "version", 1)
    payload["status"] = getattr(analysis, "status", "completed")
    payload.setdefault("skill_evidence", {})
    return AnalyzeResumeResponse.model_validate(payload)


def _find_active_analysis(
    db: Session,
    user_id: int,
    fingerprint: str,
) -> ResumeAnalysis | None:
    if not hasattr(db, "query"):
        return None
    return (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.user_id == user_id,
            ResumeAnalysis.analysis_fingerprint == fingerprint,
            ResumeAnalysis.deleted_at.is_(None),
        )
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResumeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_resume(
    file: UploadFile = File(...),
    job_role: str = Form(..., min_length=2, max_length=150),
    job_description: str | None = Form(
        default=None,
        max_length=15000,
    ),
    force_reanalyze: bool = Form(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AnalyzeResumeResponse:
    """Analyze a PDF, reusing an identical active analysis unless forced."""

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Please upload a PDF file.",
        )

    try:
        pdf_bytes = await file.read(MAX_PDF_SIZE + 1)

        if len(pdf_bytes) > MAX_PDF_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail="Resume PDF must be 10 MB or smaller.",
            )

        if b"%PDF-" not in pdf_bytes[:1024]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is not a valid PDF.",
            )

        request = ResumeAnalysisRequest(
            job_role=job_role,
            job_description=job_description,
        )

        try:
            resume_text: str | None = extract_resume_text(pdf_bytes)
        except ValueError:
            resume_text = None

        fingerprint_source = (
            resume_text
            if resume_text is not None
            else pdf_bytes.decode("latin-1", errors="ignore")
        )
        resume_hash, fingerprint = compute_analysis_fingerprint(
            resume_text=fingerprint_source,
            job_role=request.job_role,
            job_description=request.job_description,
        )

        lock = _get_analysis_lock(current_user.id, fingerprint)
        async with lock:
            if hasattr(db, "expire_all"):
                db.expire_all()
            existing = _find_active_analysis(db, current_user.id, fingerprint)

            if existing is not None:
                if existing.status == "processing":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="An identical resume analysis is already in progress. Please retry shortly.",
                    )
                if existing.status == "completed" and not force_reanalyze:
                    return _hydrating_analyze_response(existing, reused=True)

            # Run AI/scoring before mutating DB so we never hold DB write locks during LLM calls.
            result = await service.analyze(pdf_bytes, request)
            filename = _sanitize_filename(file.filename)

            result_payload = result.model_dump(mode="json")
            if resume_text:
                try:
                    taxonomy = load_skill_taxonomy()
                except Exception:
                    taxonomy = None
                result_payload["skill_evidence"] = classify_skills_evidence(
                    text=resume_text,
                    skills=result.matched_skills,
                    taxonomy=taxonomy,
                )

            if existing is not None and existing.status in {"completed", "failed"}:
                dep_count = (
                    db.query(func.count(InterviewSession.id))
                    .filter(InterviewSession.resume_analysis_id == existing.id)
                    .scalar()
                    or 0
                )
                next_version = existing.version + (1 if existing.status == "completed" else 0)

                if dep_count == 0:
                    existing.job_role = request.job_role
                    existing.job_description = request.job_description
                    existing.status = "completed"
                    existing.version = next_version
                    existing.result_json = result_payload
                    existing.created_at = datetime.now(timezone.utc)
                    db.commit()
                    if hasattr(db, "refresh"):
                        db.refresh(existing)
                    return _hydrating_analyze_response(existing, reused=False)

                # Archive previous version so existing interviews/reports keep their reference.
                existing.deleted_at = datetime.now(timezone.utc)
                db.flush()
            else:
                next_version = 1

            resume = Resume(
                user_id=current_user.id,
                filename=filename,
            )
            db.add(resume)
            db.flush()

            analysis = ResumeAnalysis(
                user_id=current_user.id,
                resume_id=resume.id,
                job_role=request.job_role,
                job_description=request.job_description,
                resume_hash=resume_hash,
                analysis_fingerprint=fingerprint,
                status="completed",
                version=next_version,
                result_json=result_payload,
            )
            db.add(analysis)

            try:
                db.commit()
                if hasattr(db, "refresh"):
                    db.refresh(analysis)
            except IntegrityError:
                db.rollback()
                concurrent = _find_active_analysis(db, current_user.id, fingerprint)
                if concurrent is not None and concurrent.status == "completed":
                    return _hydrating_analyze_response(concurrent, reused=True)
                raise

            return _hydrating_analyze_response(analysis, reused=False)

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
    """List active saved resume analyses belonging to the current user."""

    records = (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(
            Resume.user_id == current_user.id,
            ResumeAnalysis.deleted_at.is_(None),
            ResumeAnalysis.status == "completed",
        )
        .order_by(ResumeAnalysis.created_at.desc(), ResumeAnalysis.id.desc())
        .limit(limit)
        .all()
    )

    interview_counts: dict[int, int] = {}
    if records and isinstance(db, Session):
        analysis_ids = [analysis.id for analysis, _resume in records]
        try:
            count_rows = (
                db.query(
                    InterviewSession.resume_analysis_id,
                    func.count(InterviewSession.id),
                )
                .filter(
                    InterviewSession.user_id == current_user.id,
                    InterviewSession.resume_analysis_id.in_(analysis_ids),
                )
                .group_by(InterviewSession.resume_analysis_id)
                .all()
            )
            interview_counts = {int(aid): int(cnt) for aid, cnt in count_rows}
        except SQLAlchemyError:
            interview_counts = {}

    return [
        ResumeAnalysisHistoryItem(
            id=analysis.id,
            filename=resume.filename,
            job_role=analysis.job_role,
            created_at=analysis.created_at,
            match_score=analysis.result_json.get("match_score", 0),
            version=getattr(analysis, "version", 1),
            interview_count=interview_counts.get(analysis.id, 0),
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
    """Retrieve an active analysis only if it belongs to the current user."""

    record = (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(
            ResumeAnalysis.id == analysis_id,
            Resume.user_id == current_user.id,
            ResumeAnalysis.deleted_at.is_(None),
            ResumeAnalysis.status == "completed",
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found.",
        )

    analysis, resume = record
    interview_count = 0
    if isinstance(db, Session):
        try:
            interview_count = int(
                db.query(func.count(InterviewSession.id))
                .filter(
                    InterviewSession.resume_analysis_id == analysis.id,
                    InterviewSession.user_id == current_user.id,
                )
                .scalar()
                or 0
            )
        except SQLAlchemyError:
            interview_count = 0

    return SavedResumeAnalysis(
        id=analysis.id,
        filename=resume.filename,
        created_at=analysis.created_at,
        version=getattr(analysis, "version", 1),
        interview_count=interview_count,
        skill_evidence=dict((analysis.result_json or {}).get("skill_evidence") or {}),
        result=ResumeAnalysisResult.model_validate(analysis.result_json),
    )


@router.delete(
    "/analyses/{analysis_id}",
    response_model=DeleteAnalysisResponse,
)
def delete_resume_analysis(
    analysis_id: int,
    cascade: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DeleteAnalysisResponse:
    """Delete or archive an owned resume analysis with explicit dependent-data handling."""

    record = (
        db.query(ResumeAnalysis, Resume)
        .join(Resume, Resume.id == ResumeAnalysis.resume_id)
        .filter(
            ResumeAnalysis.id == analysis_id,
            Resume.user_id == current_user.id,
            ResumeAnalysis.deleted_at.is_(None),
        )
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume analysis not found.",
        )

    analysis, _resume = record
    dependent_session_ids = [
        row[0]
        for row in db.query(InterviewSession.id)
        .filter(
            InterviewSession.resume_analysis_id == analysis.id,
            InterviewSession.user_id == current_user.id,
        )
        .all()
    ]
    dep_count = len(dependent_session_ids)

    if dep_count > 0 and not cascade:
        # Soft-delete from history & deduplication while keeping historical interview references intact.
        analysis.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return DeleteAnalysisResponse(
            deleted=True,
            analysis_id=analysis_id,
            mode="archived",
            dependent_interviews=dep_count,
        )

    # Permanent deletion (also cascades owned dependent interviews/turns/reports if cascade=True).
    db.delete(analysis)
    db.commit()
    if dependent_session_ids:
        clear_session_checkpoints(dependent_session_ids)

    return DeleteAnalysisResponse(
        deleted=True,
        analysis_id=analysis_id,
        mode="permanent",
        dependent_interviews=dep_count,
    )
