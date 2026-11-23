"""Run offline regressions on a fresh disposable pgvector DB, never the local DB.

Prerequisite: docker compose build backend. No private snapshots are required.
"""

import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]


def run(args, *, env=None, capture=False, check=True):
    return subprocess.run(
        args,
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        check=check,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "storage/repository-sync/backend-tests"
    )
    parser.add_argument("--image", help="Explicit built image/tag; avoids testing a stale running Compose container image")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    image = [args.image] if args.image else (
        run(["docker", "compose", "images", "-q", "backend"], capture=True)
        .stdout.strip()
        .splitlines()
    )
    if not image:
        parser.error("Build the backend first: docker compose build backend")
    image = image[0]
    suffix = uuid.uuid4().hex[:12]
    name = "prepmate-test-" + suffix
    network = name + "-network"
    env = os.environ.copy()
    env.update(
        POSTGRES_USER="prepmate_test",
        POSTGRES_DB="prepmate_test",
        POSTGRES_PASSWORD=secrets.token_urlsafe(24),
        JWT_SECRET_KEY=secrets.token_urlsafe(48),
        LLM_PROVIDER="azure_openai",
        AZURE_OPENAI_API_KEY="synthetic-offline-test",
        AZURE_OPENAI_ENDPOINT="https://example.invalid",
        GEMINI_API_KEY="synthetic-offline-test",
        AZURE_SPEECH_KEY="synthetic-offline-test",
        AZURE_SPEECH_REGION="eastasia",
    )
    env["DATABASE_URL"] = (
        f"postgresql+psycopg://prepmate_test:{env['POSTGRES_PASSWORD']}@{name}:5432/prepmate_test"
    )
    network_id = run(
        [
            "docker",
            "network",
            "create",
            "--label",
            "prepmate.purpose=offline-tests",
            network,
        ],
        capture=True,
    ).stdout.strip()
    container_id = None
    try:
        container_id = run(
            [
                "docker",
                "run",
                "--detach",
                "--name",
                name,
                "--network",
                network,
                "--label",
                "prepmate.purpose=offline-tests",
                "--mount",
                "type=tmpfs,destination=/var/lib/postgresql/data",
                "--env",
                "POSTGRES_USER",
                "--env",
                "POSTGRES_DB",
                "--env",
                "POSTGRES_PASSWORD",
                "pgvector/pgvector:pg16",
            ],
            env=env,
            capture=True,
        ).stdout.strip()
        for _ in range(50):
            ready = run(
                [
                    "docker",
                    "exec",
                    name,
                    "pg_isready",
                    "-U",
                    "prepmate_test",
                    "-d",
                    "prepmate_test",
                ],
                capture=True,
                check=False,
            )
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            raise RuntimeError("Disposable test PostgreSQL did not become ready")
        command = [
            "docker",
            "run",
            "--rm",
            "--network",
            network,
            "--mount",
            f'type=bind,source={(ROOT/"backend").as_posix()},destination=/app,readonly',
            "--mount",
            f'type=bind,source={(ROOT/"knowledge_base").as_posix()},destination=/app/knowledge_base,readonly',
            "--mount",
            f'type=bind,source={(ROOT/"eval_data").as_posix()},destination=/app/eval_data,readonly',
            "--mount",
            f"type=bind,source={output.as_posix()},destination=/app/storage",
            "--workdir",
            "/app",
            "--env",
            "PYTHONDONTWRITEBYTECODE=1",
        ]
        for key in [
            "DATABASE_URL",
            "POSTGRES_PASSWORD",
            "JWT_SECRET_KEY",
            "LLM_PROVIDER",
            "AZURE_OPENAI_API_KEY",
            "AZURE_OPENAI_ENDPOINT",
            "GEMINI_API_KEY",
            "AZURE_SPEECH_KEY",
            "AZURE_SPEECH_REGION",
        ]:
            command += ["--env", key]
        result = run(
            command + [image, "python", "scripts/run_offline_tests.py"],
            env=env,
            check=False,
        )
        if result.returncode:
            raise SystemExit(result.returncode)
        print(
            "Offline suite passed; original PostgreSQL and user data were not accessed."
        )
    finally:
        if container_id:
            actual = run(
                ["docker", "inspect", "--format", "{{.Id}}", name], capture=True
            ).stdout.strip()
            if actual != container_id or not name.startswith("prepmate-test-"):
                raise RuntimeError("Refusing cleanup: test container identity changed")
            run(["docker", "rm", "--force", container_id], capture=True)
        actual = run(
            ["docker", "network", "inspect", "--format", "{{.Id}}", network],
            capture=True,
        ).stdout.strip()
        if actual != network_id:
            raise RuntimeError("Refusing cleanup: test network identity changed")
        run(["docker", "network", "rm", network_id], capture=True)


if __name__ == "__main__":
    main()
