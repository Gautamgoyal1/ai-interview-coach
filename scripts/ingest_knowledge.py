"""Compatibility entrypoint; previews only unless an approved plan is applied."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
from app.modules.knowledge.ingest_cli import main

if __name__ == "__main__":
    main()
