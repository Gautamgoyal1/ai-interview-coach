"""Actual read-only InterviewNodes/RAG audit, with frozen holdout and API ledger.

Run from the repository root after the isolated rehearsal and scoped update:
  .venv/Scripts/python.exe scripts/audit_phase7_questions.py

Never resets prior results or hides rejected drafts. Human/agent judgments belong
in a separate review file, not the generator's semantic-screen success flag.
"""

import asyncio
import hashlib
import json
import logging
import os
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
from app.modules.interview import question_generator as qg
from rollout_b_checks import state
from phase7_meter import Meter

OUT = ROOT / "storage/phase7"
read = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


async def main():
    suffix = os.getenv("PREPMATE_PHASE7_AUDIT_SUFFIX", "")
    assert suffix in {"", "-refined"}
    criteria = read(OUT / f"criteria{suffix}.json")
    assert (
        sha(ROOT / "storage/phase6b/hard-mode-quality-audit/criteria.json")
        == criteria["frozen_rubric_sha256"]
    )
    assert read(OUT / "local-update-receipt.json")["passed"]
    assert (
        settings.azure_openai_model == "gpt-5.4-mini"
        and settings.embedding_model == "gemini-embedding-001"
    )
    provider = get_llm_provider()
    assert provider.name == "azure_openai"
    assert settings.gemini_api_key and settings.embedding_dimensions == 768
    meter = Meter(OUT)
    meter.observe_azure(provider)
    meter.observe_gemini()
    files = [
        *ROOT.glob("backend/app/modules/interview/*.py"),
        ROOT / "backend/app/modules/knowledge/retriever.py",
        *ROOT.glob("knowledge_base/software_engineering/*.md"),
        OUT / f"criteria{suffix}.json",
        OUT / "vectors.json",
    ]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in files}
    freeze = OUT / f"generation-input-hashes{suffix}.json"
    if freeze.exists():
        assert read(freeze) == hashes, "Inputs changed during frozen evaluation"
    else:
        freeze.write_text(json.dumps(hashes, indent=2) + "\n")
    engine = create_engine(make_url(settings.database_url).set(host="127.0.0.1"))
    with Session(engine) as db:
        db.execute(text("SET TRANSACTION READ ONLY"))
        db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
        baseline = state(lambda sql: list(db.execute(text(sql)).scalars()))
        db.rollback()
    questions_path = OUT / f"questions{suffix}.json"
    questions = read(questions_path) if questions_path.exists() else []
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
    logger = logging.getLogger("app.modules.interview.question_generator")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    contexts = {}
    for done in questions:
        contexts[done["session"]] = done["updated_history"]
    cases = list(criteria["sample"])
    required = criteria.get("minimum_provider_questions", 30)
    replacement_base = len(cases)
    replacements = [c for c in questions if c.get("replacement_for")]
    for replacement in replacements:
        cases.append(
            {k: replacement[k] for k in criteria["sample"][0]}
            | {"replacement_for": replacement["replacement_for"]}
        )
    # Resume uncovered fallback cases without rerunning completed provider calls.
    # Keep extra sessions separate: forcing the same topic repeatedly into an
    # already full interview measures exhaustion, rather than fresh generation.
    covered = {c.get("replacement_for") for c in cases}
    for failed in questions:
        if failed["fallback_used"] and failed["id"] not in covered:
            number = len(cases) - replacement_base + 1
            if number > 10:
                break
            extra = {key: failed[key] for key in criteria["sample"][0]}
            extra.update(id=f"{suffix}R{number:02d}", replacement_for=failed["id"], session=f"extra-{suffix}-{number}")
            cases.append(extra)
    try:
        index = 0
        while index < len(cases):
            case = cases[index]
            index += 1
            if any(q["id"] == case["id"] for q in questions):
                continue
            level = case["experience_level"]
            active.clear()
            active.update(fallback_used=False, validation_log=[])
            meter.active_case = case["id"]
            history = contexts.get(
                case["session"],
                {
                    "conversation_history": [],
                    "asked_question_fingerprints": [],
                    "difficulty_history": [],
                },
            )
            skills = [
                "data structures",
                "algorithms",
                "object-oriented programming",
                "sql",
                "http",
                "rest apis",
                "git",
                "testing",
                "debugging",
                "security fundamentals",
            ]
            state_ = dict(
                **history,
                target_role="Software Engineer",
                selected_topic=case["topic"],
                experience_level=level,
                current_difficulty="hard",
                question_index=len(history["conversation_history"]) + 1,
                max_questions=15,
                interview_type="technical",
                current_question={"question_type": case["question_type"]},
                question_focus="fundamental",
                candidate_context={
                    "resume_skills": skills,
                    "matched_skills": skills,
                    "projects": [],
                    "strengths": [],
                    "improvement_suggestions": [],
                },
                topic_performance={},
            )
            first_request = len(meter.ledger["requests"])
            started = time.perf_counter()
            with Session(engine) as db:
                db.execute(text("SET TRANSACTION READ ONLY"))
                nodes = InterviewNodes(db=db, llm_provider=provider)
                retrieval = await nodes.retrieve_knowledge(state_)
                assert (
                    len(retrieval["retrieved_sources"]) == 1
                ), "RAG failed or scope changed; stop before generating"
                expected_difficulty = "medium" if level == "fresher" else "hard"
                assert retrieval["retrieved_sources"][0]["source_name"].endswith(
                    ":" + expected_difficulty
                )
                state_.update(retrieval)
                generated = await nodes.generate_question(state_)
                db.rollback()
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
            requests = meter.ledger["requests"][first_request:]
            drafts = []
            for request in requests:
                if (
                    request.get("task") != "question_generation"
                    or request["status"] != "SUCCEEDED"
                ):
                    continue
                response = read(OUT / f'response-{request["id"]:03d}.json')
                for message in response.get("output", []):
                    for part in message.get("content", []):
                        if part.get("type") == "output_text":
                            try:
                                drafts.append(
                                    json.loads(qg._strip_json_fences(part["text"]))[
                                        "question_text"
                                    ].strip()
                                )
                            except (ValueError, KeyError):
                                pass
            confirmed = (
                not active["fallback_used"] and question["question_text"] in drafts
            )
            result = dict(
                **case,
                question=question,
                sources=retrieval["retrieved_sources"],
                raw_context=retrieval["retrieved_context"],
                confirmed_provider_generated=confirmed,
                **active,
                drafts=drafts,
                request_ids=[r["id"] for r in requests],
                elapsed_seconds=time.perf_counter() - started,
                updated_history=updated,
            )
            questions.append(result)
            questions_path.write_text(json.dumps(questions, indent=2) + "\n")
            print(
                json.dumps(
                    {
                        "id": case["id"],
                        "question": question["question_text"],
                        "provider_generated": confirmed,
                        "requests": result["request_ids"],
                    }
                ),
                flush=True,
            )
            if not confirmed and len(cases) < replacement_base + 10:
                cases.append(
                    case
                    | {
                        "id": f"{suffix}R{len(cases) - replacement_base + 1:02d}",
                        "replacement_for": case["id"],
                        "session": f"extra-{suffix}-{len(cases)}",
                    }
                )
        assert sum(q["confirmed_provider_generated"] for q in questions) >= required
        with Session(engine) as db:
            db.execute(text("SET TRANSACTION READ ONLY"))
            db.execute(text("SET LOCAL TIME ZONE 'UTC'"))
            assert state(lambda sql: list(db.execute(text(sql)).scalars())) == baseline
            db.rollback()
        (OUT / f"execution-summary{suffix}.json").write_text(
            json.dumps(
                {
                    "completed": True,
                    "questions": len(questions),
                    "provider_generated": sum(
                        q["confirmed_provider_generated"] for q in questions
                    ),
                    "database_unchanged_during_audit": True,
                    "frozen_criteria_sha256": sha(OUT / f"criteria{suffix}.json"),
                    "paid_limit_usd": 2,
                },
                indent=2,
            )
            + "\n"
        )
    finally:
        meter.save()
        engine.dispose()
        qg._fallback_primary_question = original_fallback
        logger.removeHandler(handler)


if __name__ == "__main__":
    asyncio.run(main())
