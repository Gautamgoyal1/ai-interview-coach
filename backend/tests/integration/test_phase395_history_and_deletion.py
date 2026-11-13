"""Phase 3.95 tests: resume deduplication, fingerprinting, forced reanalysis, and safe deletion."""

import asyncio
import json
from unittest.mock import patch

import httpx
import pytest
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user
from app.db.models.interview_session import InterviewSession
from app.db.models.report import InterviewReport
from app.db.models.resume import Resume, ResumeAnalysis
from app.db.models.turn import InterviewTurn
from app.db.models.user import User
from app.db.session import get_db
from app.main import app
from app.modules.interview.router import service as interview_service
from app.modules.resume import router as resume_router_mod
from app.modules.resume.schemas import ResumeAnalysisResult


def _make_pdf(marker: str) -> bytes:
    return f"%PDF-1.4\n% {marker}\n".encode("utf-8")


@pytest.fixture()
def phase395_env():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    tables = [
        User.__table__,
        Resume.__table__,
        ResumeAnalysis.__table__,
        InterviewSession.__table__,
        InterviewTurn.__table__,
        InterviewReport.__table__,
    ]
    for t in tables:
        t.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    db = SessionLocal()
    user_a = User(email="alice395@example.com", password_hash="h1")
    user_b = User(email="bob395@example.com", password_hash="h2")
    db.add_all([user_a, user_b])
    db.commit()
    db.refresh(user_a)
    db.refresh(user_b)
    uid_a, uid_b = user_a.id, user_b.id
    db.close()

    active_uid = {"id": uid_a}

    def override_db():
        s = SessionLocal()
        try:
            yield s
        finally:
            s.close()

    def override_user():
        s = SessionLocal()
        u = s.get(User, active_uid["id"])
        s.close()
        return u

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    yield SessionLocal, uid_a, uid_b, active_uid

    app.dependency_overrides.clear()
    for t in reversed(tables):
        t.drop(bind=engine)


def test_dedup_reuse_different_filename_role_jd_content_and_user_isolation(phase395_env):
    SessionLocal, uid_a, uid_b, active_uid = phase395_env
    llm_calls = {"count": 0}

    async def fake_analyze(pdf_bytes, request):
        await asyncio.sleep(0.02)
        llm_calls["count"] += 1
        return ResumeAnalysisResult(
            job_role=request.job_role,
            resume_skills=["python", "sql"],
            matched_skills=["python"],
            missing_skills=["docker"],
            match_score=75.0,
            strengths=["You demonstrated Python in your projects."],
            improvement_suggestions=["Add Docker containerization details."],
            likely_interview_questions=["How do you structure a FastAPI app?"],
        )

    def fake_extract(pdf_bytes: bytes) -> str:
        return pdf_bytes.decode("utf-8", errors="ignore")

    async def _run():
        with (
            patch.object(resume_router_mod.service, "analyze", side_effect=fake_analyze),
            patch.object(resume_router_mod, "extract_resume_text", side_effect=fake_extract),
        ):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 1. Initial upload
                r1 = await client.post(
                    "/resume/analyze",
                    files={"file": ("resume_v1.pdf", _make_pdf("Python SQL API"), "application/pdf")},
                    data={"job_role": "Backend Developer", "job_description": "Python FastAPI"},
                )
                assert r1.status_code == 200
                d1 = r1.json()
                assert d1["reused"] is False
                assert d1["version"] == 1
                assert llm_calls["count"] == 1

                # 2. Identical resume + different filename -> reused!
                r2 = await client.post(
                    "/resume/analyze",
                    files={"file": ("renamed_copy.pdf", _make_pdf("Python SQL API"), "application/pdf")},
                    data={"job_role": "Backend Developer", "job_description": "Python FastAPI"},
                )
                assert r2.status_code == 200
                d2 = r2.json()
                assert d2["reused"] is True
                assert d2["analysis_id"] == d1["analysis_id"]
                assert llm_calls["count"] == 1

                # 3. Same resume + different role -> distinct record
                r3 = await client.post(
                    "/resume/analyze",
                    files={"file": ("resume_v1.pdf", _make_pdf("Python SQL API"), "application/pdf")},
                    data={"job_role": "Data Engineer", "job_description": "Python FastAPI"},
                )
                assert r3.status_code == 200
                assert r3.json()["reused"] is False
                assert r3.json()["analysis_id"] != d1["analysis_id"]
                assert llm_calls["count"] == 2

                # 4. Same resume + same role + different JD -> distinct record
                r4 = await client.post(
                    "/resume/analyze",
                    files={"file": ("resume_v1.pdf", _make_pdf("Python SQL API"), "application/pdf")},
                    data={"job_role": "Backend Developer", "job_description": "Python Django Kubernetes"},
                )
                assert r4.status_code == 200
                assert r4.json()["reused"] is False
                assert llm_calls["count"] == 3

                # 5. Modified resume content -> distinct record
                r5 = await client.post(
                    "/resume/analyze",
                    files={"file": ("resume_v1.pdf", _make_pdf("Python SQL API Docker"), "application/pdf")},
                    data={"job_role": "Backend Developer", "job_description": "Python FastAPI"},
                )
                assert r5.status_code == 200
                assert r5.json()["reused"] is False
                assert llm_calls["count"] == 4

                # 6. Cross-user isolation: Bob uploading identical resume gets private record
                active_uid["id"] = uid_b
                r6 = await client.post(
                    "/resume/analyze",
                    files={"file": ("resume_v1.pdf", _make_pdf("Python SQL API"), "application/pdf")},
                    data={"job_role": "Backend Developer", "job_description": "Python FastAPI"},
                )
                assert r6.status_code == 200
                assert r6.json()["reused"] is False
                assert r6.json()["analysis_id"] != d1["analysis_id"]
                assert llm_calls["count"] == 5

                # Bob cannot delete Alice's analysis
                del_bob = await client.delete(f"/resume/analyses/{d1['analysis_id']}")
                assert del_bob.status_code == 404

    asyncio.run(_run())


def test_concurrent_duplicate_analysis_and_forced_reanalysis_and_processing(phase395_env):
    SessionLocal, uid_a, _uid_b, active_uid = phase395_env
    active_uid["id"] = uid_a
    llm_calls = {"count": 0}

    async def fake_analyze(pdf_bytes, request):
        await asyncio.sleep(0.05)
        llm_calls["count"] += 1
        return ResumeAnalysisResult(
            job_role=request.job_role,
            resume_skills=["python"],
            matched_skills=["python"],
            missing_skills=[],
            match_score=90.0,
            strengths=[f"Run {llm_calls['count']}"],
            improvement_suggestions=["Keep practicing."],
            likely_interview_questions=["Explain GIL."],
        )

    def fake_extract(pdf_bytes: bytes) -> str:
        return pdf_bytes.decode("utf-8", errors="ignore")

    async def _run():
        with (
            patch.object(resume_router_mod.service, "analyze", side_effect=fake_analyze),
            patch.object(resume_router_mod, "extract_resume_text", side_effect=fake_extract),
        ):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                # 7. Concurrent identical requests -> LLM called once, 1 reused
                p1, p2 = await asyncio.gather(
                    client.post(
                        "/resume/analyze",
                        files={"file": ("cv.pdf", _make_pdf("Concurrent Resume"), "application/pdf")},
                        data={"job_role": "Python Developer"},
                    ),
                    client.post(
                        "/resume/analyze",
                        files={"file": ("cv.pdf", _make_pdf("Concurrent Resume"), "application/pdf")},
                        data={"job_role": "Python Developer"},
                    ),
                )
                assert p1.status_code == 200 and p2.status_code == 200
                assert llm_calls["count"] == 1
                reused_flags = sorted([p1.json()["reused"], p2.json()["reused"]])
                assert reused_flags == [False, True]
                aid = p1.json()["analysis_id"]

                # 8. Force reanalysis with 0 interviews -> updates in place, version=2
                rf = await client.post(
                    "/resume/analyze",
                    files={"file": ("cv.pdf", _make_pdf("Concurrent Resume"), "application/pdf")},
                    data={"job_role": "Python Developer", "force_reanalyze": "true"},
                )
                assert rf.status_code == 200
                assert rf.json()["reused"] is False
                assert rf.json()["version"] == 2
                assert rf.json()["analysis_id"] == aid
                assert llm_calls["count"] == 2

                # 9. Processing status returns 409 Conflict
                db = SessionLocal()
                row = db.get(ResumeAnalysis, aid)
                row.status = "processing"
                db.commit()
                db.close()

                r_proc = await client.post(
                    "/resume/analyze",
                    files={"file": ("cv.pdf", _make_pdf("Concurrent Resume"), "application/pdf")},
                    data={"job_role": "Python Developer"},
                )
                assert r_proc.status_code == 409

                # 10. Failed status allows retry and completes
                db = SessionLocal()
                row = db.get(ResumeAnalysis, aid)
                row.status = "failed"
                db.commit()
                db.close()

                r_retry = await client.post(
                    "/resume/analyze",
                    files={"file": ("cv.pdf", _make_pdf("Concurrent Resume"), "application/pdf")},
                    data={"job_role": "Python Developer"},
                )
                assert r_retry.status_code == 200
                assert r_retry.json()["status"] == "completed"
                assert llm_calls["count"] == 3

    asyncio.run(_run())


def test_deletion_semantics_for_analysis_interview_and_report(phase395_env):
    SessionLocal, uid_a, uid_b, active_uid = phase395_env
    active_uid["id"] = uid_a

    # Seed analysis -> interview -> turn -> report
    db = SessionLocal()
    res = Resume(user_id=uid_a, filename="seed.pdf")
    db.add(res)
    db.flush()
    analysis = ResumeAnalysis(
        user_id=uid_a,
        resume_id=res.id,
        job_role="Backend Developer",
        resume_hash="hash_del_1",
        analysis_fingerprint="fp_del_1",
        status="completed",
        version=1,
        result_json={
            "job_role": "Backend Developer",
            "resume_skills": ["python"],
            "matched_skills": ["python"],
            "missing_skills": [],
            "match_score": 88.0,
            "strengths": ["Strong Python"],
            "improvement_suggestions": ["Add Redis"],
            "likely_interview_questions": ["Explain async IO."],
        },
    )
    db.add(analysis)
    db.flush()

    sess = InterviewSession(
        id="sess-del-1",
        user_id=uid_a,
        resume_analysis_id=analysis.id,
        target_role="Backend Developer",
        status="completed",
        max_questions=1,
        question_index=1,
        configuration={"experience_level": "fresher"},
        graph_state={},
    )
    db.add(sess)
    db.add(
        InterviewTurn(
            session_id="sess-del-1",
            question_index=1,
            question_id="q1",
            topic="Python",
            difficulty="easy",
            question_type="conceptual",
            question_text="What is async?",
            answer_text="Cooperative multitasking.",
            evaluation={"score": 8.0, "relevance": 8.0, "clarity": 8.0, "technical_depth": 8.0},
        )
    )
    db.add(
        InterviewReport(
            session_id="sess-del-1",
            user_id=uid_a,
            target_role="Backend Developer",
            overall_score=80.0,
            dimension_scores={},
            topic_scores=[],
            strengths=["Good"],
            weaknesses=[],
            missing_concepts=[],
            recommendations=[],
            question_feedback=[],
            completion_stats={},
            evaluation_coverage={},
            rubric_version="1.0",
            rubric_weights={},
            status="completed",
        )
    )
    db.commit()
    aid = analysis.id
    db.close()

    async def _run():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            # Cross-user delete attempts must 404
            active_uid["id"] = uid_b
            assert (await client.delete(f"/reports/interviews/sess-del-1")).status_code == 404
            assert (await client.delete("/interview/sess-del-1")).status_code == 404
            assert (await client.delete(f"/resume/analyses/{aid}")).status_code == 404

            # Alice deletes ONLY the report -> session & turns remain!
            active_uid["id"] = uid_a
            del_rep = await client.delete("/reports/interviews/sess-del-1")
            assert del_rep.status_code == 200
            assert del_rep.json()["deleted"] is True

            # Report GET is 404 (not auto-recreated), while interview GET still works
            assert (await client.get("/reports/interviews/sess-del-1")).status_code == 404
            assert (await client.get("/interview/sess-del-1")).status_code == 200
            # Duplicate delete report -> 404
            assert (await client.delete("/reports/interviews/sess-del-1")).status_code == 404

            # Delete analysis with dependent interview (cascade=False) -> archived!
            del_arch = await client.delete(f"/resume/analyses/{aid}?cascade=false")
            assert del_arch.status_code == 200
            assert del_arch.json()["mode"] == "archived"
            assert del_arch.json()["dependent_interviews"] == 1
            # Hidden from history & detail, duplicate delete -> 404
            assert (await client.get("/resume/analyses")).json() == []
            assert (await client.get(f"/resume/analyses/{aid}")).status_code == 404
            assert (await client.delete(f"/resume/analyses/{aid}")).status_code == 404
            # Underlying interview still accessible
            assert (await client.get("/interview/sess-del-1")).status_code == 200

            # Delete interview -> permanently removes session & turns
            del_int = await client.delete("/interview/sess-del-1")
            assert del_int.status_code == 200
            assert (await client.get("/interview/sess-del-1")).status_code == 404
            assert (await client.delete("/interview/sess-del-1")).status_code == 404

    asyncio.run(_run())
