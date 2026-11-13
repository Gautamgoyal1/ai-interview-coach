"""Standalone evaluation benchmark runner for the rubric answer grader.

Run manually (outside CI) when verifying live LLM grading quality:
    python scripts/evaluate_answer_grader.py
"""

import asyncio
import json
from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.integrations.llm.factory import get_llm_provider
from app.modules.interview.grader import grade_interview_answer


async def main() -> None:
    cases_path = BACKEND_DIR / "eval_data" / "answer_evaluation_benchmark.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    provider = get_llm_provider()

    passed = 0
    for case in cases:
        result = await grade_interview_answer(
            provider=provider,
            target_role=case["target_role"],
            topic=case["topic"],
            difficulty=case["difficulty"],
            question_text=case["question_text"],
            answer_text=case["answer_text"],
            retrieved_context=case["retrieved_context"],
        )
        score = result.overall_score
        in_range = (
            score is not None
            and case["expected_min_score"] <= score <= case["expected_max_score"]
        )
        if in_range:
            passed += 1
        print(
            f"[{ 'PASS' if in_range else 'MISS' }] {case['id']} ({case['category']}): "
            f"score={score} expected=[{case['expected_min_score']}, {case['expected_max_score']}] "
            f"status={result.grading_status}"
        )

    print(f"\nBenchmark summary: {passed}/{len(cases)} cases within expected score range.")


if __name__ == "__main__":
    asyncio.run(main())
