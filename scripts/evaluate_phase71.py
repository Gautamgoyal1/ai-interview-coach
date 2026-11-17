"""Read-only real-pipeline Phase 7.1 calibration and preregistered evaluation.

All stages share one persistent $2 conservative ledger. No embeddings for
documents, user sessions, grading calls or PostgreSQL writes are performed.
"""

import argparse
import asyncio
import hashlib
import json
import logging
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "backend"), str(ROOT / "storage/phase6b")]

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.llm.factory import get_llm_provider
from app.modules.interview.nodes import InterviewNodes
from app.modules.interview.generation_errors import QuestionGenerationUnavailable
from app.modules.interview.problem_spec import (
    ProblemSpecification,
    render_question,
    materialize_problem,
)
from app.modules.interview.question_quality import assess_hard_question, QuestionQuality
from app.modules.interview import question_generator as qg
from apply_phase7_local import inputs, verify
from rollout_b_checks import state
from phase7_meter import Meter

OUT = ROOT / "storage/phase71"
read = lambda p: json.loads(p.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def production_hashes():
    files = [
        *ROOT.glob("backend/app/modules/interview/*.py"),
        ROOT / "backend/app/modules/interview/quality_reference.json",
        ROOT / "backend/app/modules/knowledge/retriever.py",
        *ROOT.glob("knowledge_base/software_engineering/*.md"),
    ]
    return {str(p.relative_to(ROOT)): sha(p) for p in files}


async def main(stage):
    OUT.mkdir(exist_ok=True)
    assert all(
        sha(ROOT / p) == h for p, h in read(OUT / "frozen-prior-evidence.json").items()
    )
    assert (
        settings.azure_openai_model == "gpt-5.4-mini"
        and settings.embedding_model == "gemini-embedding-001"
        and settings.embedding_dimensions == 768
    )
    provider = get_llm_provider()
    assert provider.name == "azure_openai" and settings.gemini_api_key
    meter = Meter(
        OUT, guard_rates={"azure_input": 2.5, "azure_output": 10, "gemini_input": 1}
    )
    meter.observe_azure(provider)
    meter.observe_gemini()
    engine = create_engine(make_url(settings.database_url).set(host="127.0.0.1"))
    items, cache = inputs()
    with Session(engine) as db:
        db.execute(text("SET TRANSACTION READ ONLY"))
        db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        checks = verify(db, items, cache)
        baseline = state(lambda sql: list(db.execute(text(sql)).scalars()))
        db.rollback()
    result_file = OUT / f"{stage}-results.json"
    results = read(result_file) if result_file.exists() else []
    hashes = production_hashes()
    pin = OUT / f"{stage}-input-hashes.json"
    if pin.exists():
        if read(pin) != hashes:
            assert stage not in {
                "holdout",
                "postfix",
            }, "Never change a frozen held-out run"
            previous = OUT / f"{stage}-input-hashes-before-parser-recovery.json"
            assert (
                not previous.exists()
            ), "Use a separate development stage for further changes"
            previous.write_text(pin.read_text(), encoding="utf-8")
            pin.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    else:
        pin.write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    if stage.startswith("calibration"):
        cases = read(ROOT / "backend/app/modules/interview/quality_reference.json")[
            "cases"
        ]
    else:
        manifest = OUT / f"{stage}-manifest.json"
        cases = read(manifest)["cases"]
        if stage in {"holdout", "postfix"}:
            assert len(cases) >= (30 if stage == "holdout" else 10)
            manifest_pin = OUT / f"{stage}-manifest.sha256"
            if manifest_pin.exists():
                assert manifest_pin.read_text().strip() == sha(manifest)
            else:
                manifest_pin.write_text(sha(manifest) + "\n")
    active = {}
    original_fallback = qg._fallback_primary_question

    def fallback(*args, **kwargs):
        active["fallback_used"] = True
        return original_fallback(*args, **kwargs)

    qg._fallback_primary_question = fallback

    class Logs(logging.Handler):
        def emit(self, record):
            active.setdefault("validation_log", []).append(record.getMessage())

    handler = Logs()
    loggers = [
        logging.getLogger("app.modules.interview.problem_construction"),
        logging.getLogger("app.modules.interview.question_generator"),
    ]
    for logger in loggers:
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    contexts = {}
    for result in results:
        if result.get("updated_history"):
            contexts[result["session"]] = result["updated_history"]
    try:
        for case in cases:
            if any(r["id"] == case["id"] for r in results):
                continue
            active.clear()
            active.update(fallback_used=False, validation_log=[])
            meter.active_case = stage + ":" + case["id"]
            first = len(meter.ledger["requests"])
            started = time.perf_counter()
            if stage.startswith("calibration"):
                cached = [
                    r
                    for r in meter.ledger["requests"]
                    if r["case_id"] == meter.active_case
                    and r["status"] == "SUCCEEDED"
                    and r["task"] == "semantic_screen"
                ]
                if cached:
                    request = cached[-1]
                    response = read(OUT / f'response-{request["id"]:03d}.json')
                    raw = next(
                        p["text"]
                        for m in response["output"]
                        for p in m.get("content", [])
                        if p.get("type") == "output_text"
                    )
                    data = json.loads(raw)
                    for key in (
                        "minimum_solution",
                        "observable_edge_effect",
                        "novelty_comparison",
                        "reason",
                    ):
                        if isinstance(data.get(key), str):
                            data[key] = data[key][: 700 if key == "reason" else 350]
                    quality = QuestionQuality.model_validate(data)
                    if not case["previous_questions"]:
                        quality.novel = True
                else:
                    quality = await assess_hard_question(
                        provider,
                        case["question"],
                        case["topic"],
                        case["role"],
                        case["experience_level"],
                        case["previous_questions"],
                    )
                result = {
                    **case,
                    "screen": quality.model_dump(),
                    "screen_accept": quality.accepted,
                    "correct_verdict": quality.accepted == case["expected_accept"],
                }
            else:
                history = contexts.get(
                    case["session"],
                    case.get(
                        "seed_history",
                        {
                            "conversation_history": [],
                            "asked_question_fingerprints": [],
                            "difficulty_history": [],
                        },
                    ),
                )
                state_ = dict(
                    **history,
                    target_role=case["role"],
                    experience_level=case["experience_level"],
                    selected_topic=case["topic"],
                    current_difficulty="hard",
                    question_index=case["question_index"],
                    max_questions=15,
                    interview_type="technical",
                    current_question={"question_type": case["question_type"]},
                    question_focus="fundamental",
                    candidate_context=case["candidate_context"],
                    topic_performance={},
                )
                with Session(engine) as db:
                    db.execute(text("SET TRANSACTION READ ONLY"))
                    nodes = InterviewNodes(db=db, llm_provider=provider)
                    retrieval = await nodes.retrieve_knowledge(state_)
                    assert (
                        len(retrieval["retrieved_sources"]) == 1
                    ), "Retrieval failed; stop before generation"
                    assert retrieval["retrieved_sources"][0]["source_name"].endswith(
                        ":medium" if case["experience_level"] == "fresher" else ":hard"
                    )
                    state_.update(retrieval)
                    try:
                        generated = await nodes.generate_question(state_)
                        question = generated["current_question"]
                        updated = {
                            k: generated[k]
                            for k in (
                                "conversation_history",
                                "asked_question_fingerprints",
                                "difficulty_history",
                            )
                        }
                        contexts[case["session"]] = updated
                        result = {
                            **case,
                            "question": question,
                            "updated_history": updated,
                            "unavailable": False,
                        }
                    except QuestionGenerationUnavailable:
                        result = {**case, "question": None, "unavailable": True}
                    db.rollback()
                drafts = []
                for request in meter.ledger["requests"][first:]:
                    if (
                        request.get("task") != "question_generation"
                        or request["status"] != "SUCCEEDED"
                    ):
                        continue
                    response = read(OUT / f'response-{request["id"]:03d}.json')
                    for msg in response.get("output", []):
                        for part in msg.get("content", []):
                            if part.get("type") == "output_text":
                                try:
                                    data = json.loads(part["text"])
                                    spec = materialize_problem(
                                        data["problem_spec"],
                                        case["role"],
                                        case["topic"],
                                        case["experience_level"],
                                    )
                                    drafts.append(
                                        {
                                            "request_id": request["id"],
                                            "problem_spec": spec.model_dump(),
                                            "question_text": render_question(spec),
                                        }
                                    )
                                except (ValueError, KeyError):
                                    drafts.append(
                                        {
                                            "request_id": request["id"],
                                            "invalid_raw_text": part["text"],
                                        }
                                    )
                confirmed = bool(
                    result["question"]
                    and not active["fallback_used"]
                    and any(
                        d.get("question_text") == result["question"]["question_text"]
                        for d in drafts
                    )
                )
                if result["question"]:
                    assert (
                        result["question"]["difficulty"] == "hard"
                        and result["question"]["topic"] == case["topic"]
                    )
                result.update(
                    **active,
                    provider_generated=confirmed,
                    drafts=drafts,
                    sources=retrieval["retrieved_sources"],
                    raw_context=retrieval["retrieved_context"],
                )
            result.update(
                request_ids=[r["id"] for r in meter.ledger["requests"][first:]],
                elapsed_seconds=time.perf_counter() - started,
            )
            if stage.startswith("calibration") and cached:
                result.update(
                    request_ids=[request["id"]],
                    elapsed_seconds=request["elapsed_seconds"],
                    recovered_cached_response=True,
                )
            results.append(result)
            result_file.write_text(
                json.dumps(results, indent=2) + "\n", encoding="utf-8"
            )
            print(
                json.dumps(
                    {
                        k: result[k]
                        for k in ("id", "screen_accept", "expected_accept")
                        if k in result
                    }
                    | (
                        {
                            "provider": result["provider_generated"],
                            "unavailable": result["unavailable"],
                            "question": result["question"],
                        }
                        if "provider_generated" in result
                        else {}
                    )
                ),
                flush=True,
            )
        with Session(engine) as db:
            db.execute(text("SET TRANSACTION READ ONLY"))
            db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            assert (
                state(lambda sql: list(db.execute(text(sql)).scalars())) == baseline
            ), "Database changed during read-only stage"
            verify(db, items, cache)
            db.rollback()
        summary = {
            "completed": True,
            "cases": len(results),
            "database_unchanged": True,
            "database_checks": checks,
        }
        if stage.startswith("calibration"):
            positives = [r for r in results if r["expected_accept"]]
            negatives = [r for r in results if not r["expected_accept"]]
            summary.update(
                positive_cases=len(positives),
                negative_cases=len(negatives),
                false_rejects=sum(not r["screen_accept"] for r in positives),
                false_accepts=sum(r["screen_accept"] for r in negatives),
            )
        else:
            summary.update(
                provider_generated=sum(r["provider_generated"] for r in results),
                curated_fallbacks=sum(
                    bool(r["question"]) and r["fallback_used"] for r in results
                ),
                unavailable=sum(r["unavailable"] for r in results),
            )
        (OUT / f"{stage}-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary), flush=True)
    finally:
        meter.save()
        engine.dispose()
        qg._fallback_primary_question = original_fallback
        for logger in loggers:
            logger.removeHandler(handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "stage",
        choices=[
            "calibration",
            "calibration-v2",
            "calibration-v3",
            "pilot",
            "pilot-v2",
            "pilot-v3",
            "holdout",
            "postfix",
        ],
    )
    asyncio.run(main(parser.parse_args().stage))
