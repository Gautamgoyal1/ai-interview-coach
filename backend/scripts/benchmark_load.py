"""Repeatable, non-destructive latency and concurrency benchmark for PrepMate.

Usage:
  python scripts/benchmark_load.py --base-url http://127.0.0.1:8000
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import statistics
import sys
import time
from pathlib import Path
from typing import Any

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def percentile(sorted_values: list[float], pct: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_values[low]
    weight = rank - low
    return sorted_values[low] * (1.0 - weight) + sorted_values[high] * weight


def summarize(name: str, concurrency: int, latencies_ms: list[float], errors: int, wall_s: float) -> dict[str, Any]:
    ordered = sorted(latencies_ms)
    total = len(latencies_ms) + errors
    rps = total / wall_s if wall_s > 0 else 0.0
    return {
        "workload": name,
        "concurrency": concurrency,
        "requests": total,
        "errors": errors,
        "error_rate_pct": round((errors / total) * 100, 2) if total else 0.0,
        "rps": round(rps, 2),
        "min_ms": round(ordered[0], 2) if ordered else 0.0,
        "p50_ms": round(percentile(ordered, 50), 2),
        "p95_ms": round(percentile(ordered, 95), 2),
        "max_ms": round(ordered[-1], 2) if ordered else 0.0,
        "mean_ms": round(statistics.mean(ordered), 2) if ordered else 0.0,
    }


async def run_concurrent_requests(
    client: httpx.AsyncClient,
    concurrency: int,
    total_requests: int,
    request_factory,
) -> tuple[list[float], int, float]:
    sem = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    errors = 0

    async def one(idx: int) -> None:
        nonlocal errors
        async with sem:
            t0 = time.perf_counter()
            try:
                resp = await request_factory(client, idx)
                elapsed = (time.perf_counter() - t0) * 1000.0
                if resp.status_code >= 400:
                    errors += 1
                else:
                    latencies.append(elapsed)
            except Exception:
                errors += 1

    wall_start = time.perf_counter()
    await asyncio.gather(*(one(i) for i in range(total_requests)))
    wall_s = time.perf_counter() - wall_start
    return latencies, errors, wall_s


async def benchmark_http_workload_a(base_url: str, email: str, password: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        login_resp = await client.post("/auth/login", json={"email": email, "password": password})
        if login_resp.status_code != 200:
            raise RuntimeError(f"Benchmark login failed ({login_resp.status_code}): {login_resp.text}")
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        history_resp = await client.get("/resume/analyses", headers=headers)
        history_items = history_resp.json() if history_resp.status_code == 200 else []
        reports_resp = await client.get("/reports", headers=headers)
        report_items = reports_resp.json() if reports_resp.status_code == 200 else []
        sample_session_id = report_items[0]["session_id"] if report_items else None

        for conc in (1, 5, 10, 25):
            total = max(conc * 3, 15)
            lats, errs, wall = await run_concurrent_requests(
                client,
                conc,
                total,
                lambda c, _: c.get("/health"),
            )
            results.append(summarize("GET /health", conc, lats, errs, wall))

            lats, errs, wall = await run_concurrent_requests(
                client,
                conc,
                total,
                lambda c, _: c.get("/resume/analyses", headers=headers),
            )
            results.append(summarize("GET /resume/analyses", conc, lats, errs, wall))

            lats, errs, wall = await run_concurrent_requests(
                client,
                conc,
                total,
                lambda c, _: c.get("/reports", headers=headers),
            )
            results.append(summarize("GET /reports", conc, lats, errs, wall))

            if sample_session_id:
                lats, errs, wall = await run_concurrent_requests(
                    client,
                    conc,
                    total,
                    lambda c, _: c.get(f"/interview/{sample_session_id}", headers=headers),
                )
                results.append(summarize("GET /interview/{id}", conc, lats, errs, wall))

        # Auth login benchmark (kept at moderate volume to respect rate limiter on failures)
        for conc in (1, 5, 10):
            total = max(conc * 2, 6)
            lats, errs, wall = await run_concurrent_requests(
                client,
                conc,
                total,
                lambda c, _: c.post("/auth/login", json={"email": email, "password": password}),
            )
            results.append(summarize("POST /auth/login", conc, lats, errs, wall))

    return results


async def benchmark_mocked_interview_workload_b() -> list[dict[str, Any]]:
    """Measure interview start + answer submission concurrency with mocked LLM in-process."""
    from unittest.mock import patch
    import tempfile
    from fastapi import FastAPI
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.api.dependencies import get_current_user
    from app.db.base import Base
    from app.db.models.resume import Resume, ResumeAnalysis
    from app.db.models.user import User
    from app.db.session import get_db
    from app.integrations.llm.base import LLMProvider
    from app.modules.interview import router as interview_router_mod
    from app.modules.interview.service import InterviewService

    class _FastMockLLM(LLMProvider):
        async def generate(
            self,
            prompt: str,
            system: str | None = None,
            json_mode: bool = False,
        ) -> str:
            if "evaluate" in prompt.lower() or "score" in prompt.lower():
                return json.dumps({
                    "score": 8.0,
                    "relevance": 8.0,
                    "clarity": 8.0,
                    "technical_depth": 8.0,
                    "strengths": ["Clear explanation"],
                    "weaknesses": [],
                    "missing_concepts": [],
                    "feedback": "Good answer.",
                    "needs_follow_up": False,
                })
            return json.dumps({
                "question": "Explain how hash tables handle collisions and their average lookup complexity.",
                "topic": "Hash Maps",
                "difficulty": "easy",
                "question_type": "conceptual",
                "expected_concepts": ["hash function", "collisions", "O(1)"],
                "follow_up_hint": "Compare chaining and open addressing.",
            })

    tmp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp_db.close()
    engine = create_engine(
        f"sqlite:///{tmp_db.name}",
        connect_args={"check_same_thread": False, "timeout": 30},
    )
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    db = TestSession()
    user = User(email="bench@example.com", password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    resume = Resume(user_id=user.id, filename="bench.pdf")
    db.add(resume)
    db.commit()
    db.refresh(resume)
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        job_role="Backend Developer",
        job_description="FastAPI PostgreSQL",
        result_json={
            "match_score": 85.0,
            "resume_skills": ["Python", "FastAPI", "SQL"],
            "matched_skills": ["Python", "FastAPI"],
            "missing_skills": ["Redis"],
            "strengths": ["Strong backend fundamentals"],
            "improvement_suggestions": ["Add caching"],
        },
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id
    user_id = user.id
    db.close()

    app = FastAPI()
    app.include_router(interview_router_mod.router)
    orig_service = interview_router_mod.service
    interview_router_mod.service = InterviewService(llm_provider=_FastMockLLM())

    def override_db():
        s = TestSession()
        try:
            yield s
        finally:
            s.close()

    def override_user():
        s = TestSession()
        u = s.get(User, user_id)
        s.close()
        return u

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = override_user

    results: list[dict[str, Any]] = []
    try:
        async def _empty_chunks(*args: Any, **kwargs: Any) -> list[Any]:
            return []

        transport = httpx.ASGITransport(app=app)
        with patch("app.modules.interview.nodes.retrieve_chunks_async", side_effect=_empty_chunks):
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                for conc in (1, 5, 10, 25):
                    total = conc * 2
                    sessions: list[tuple[str, str]] = []

                    async def start_one(c: httpx.AsyncClient, _: int):
                        resp = await c.post(
                            "/interview/start",
                            json={"analysis_id": analysis_id, "max_questions": 2, "experience_level": "fresher"},
                        )
                        if resp.status_code == 201:
                            data = resp.json()
                            sessions.append((data["session_id"], data["current_question"]["question_id"]))
                        return resp

                    lats, errs, wall = await run_concurrent_requests(client, conc, total, start_one)
                    results.append(summarize("POST /interview/start (mock LLM)", conc, lats, errs, wall))

                    if sessions:
                        lats, errs, wall = await run_concurrent_requests(
                            client,
                            conc,
                            len(sessions),
                            lambda c, idx: c.post(
                                f"/interview/{sessions[idx][0]}/answer",
                                json={
                                    "question_id": sessions[idx][1],
                                    "answer": "Hash tables use a hash function to map keys to buckets, achieving O(1) average lookup and handling collisions via chaining or open addressing.",
                                },
                            ),
                        )
                        results.append(summarize("POST /interview/{id}/answer (mock LLM)", conc, lats, errs, wall))
    finally:
        interview_router_mod.service = orig_service
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        Path(tmp_db.name).unlink(missing_ok=True)

    return results


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--email", default="calibrated_verify_1794491251025@example.com")
    parser.add_argument("--password", default="TestPassword123!")
    parser.add_argument("--workload-a-only", action="store_true")
    args = parser.parse_args()

    all_results: list[dict[str, Any]] = []
    print("Running Workload A against live server:", args.base_url)
    all_results.extend(await benchmark_http_workload_a(args.base_url, args.email, args.password))
    if not args.workload_a_only:
        print("Running Workload B (mocked LLM interview concurrency)...")
        all_results.extend(await benchmark_mocked_interview_workload_b())
    print(json.dumps(all_results, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
