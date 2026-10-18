import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.modules.resume.schemas import ResumeAnalysisRequest
from app.modules.resume.service import ResumeAnalysisService


async def main():
    base = Path(__file__).resolve().parent.parent
    fixture_dir = base / "tests" / "fixtures"
    output_dir = base / "eval_results"
    output_dir.mkdir(exist_ok=True)

    pdf_path = fixture_dir / "sample_resume.pdf"
    job_path = fixture_dir / "sample_job_description.txt"

    request = ResumeAnalysisRequest(
        job_role="Junior Machine Learning Engineer",
        job_description=job_path.read_text(encoding="utf-8"),
    )

    service = ResumeAnalysisService()
    result = await service.analyze(pdf_path.read_bytes(), request)

    report = result.model_dump()
    output_path = output_dir / "resume_grounding_baseline.json"
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())