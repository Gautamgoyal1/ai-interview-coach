"""Scan exact staged blobs; report paths/rules only, never credential values.

Pattern and configured-value checks are defense in depth, not a history audit or
a guarantee that every possible secret/PII format is detectable.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "google-api-key": re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),
    "provider-key": re.compile(r"\bsk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}"),
    "github-token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"),
    "aws-access-key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
}
KEY = r"(?:[a-z_]*(?:api_key|secret_key|jwt_secret|client_secret|access_token|refresh_token)|[a-z_]*password|[a-z_]*passwd)"
ASSIGNMENT = re.compile(
    r"""(?im)(?:["']"""
    + KEY
    + r"""["']|\b"""
    + KEY
    + r"""\b)\s*[:=]\s*["']([^"'\r\n]{8,})["']"""
)
PLACEHOLDER = re.compile(
    r"(?i)(change.?me|replace|example|placeholder|synthetic|dummy|not[-_ ](?:a[-_ ])?(?:real|login)|test|your[_ -]|<|\{|\*|\\|\.join\()"
)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def inspect_blob(path, blob, configured=()):
    findings = []
    reviewed = []

    def add(rule, offset=0):
        findings.append(dict(path=path, line=blob[:offset].count(b"\n") + 1, rule=rule))

    name = Path(path).name
    if (name == ".env" or name.startswith(".env.")) and not name.endswith(".example"):
        add("environment-file")
    if re.search(
        r"(^|/)(node_modules|\.venv|__pycache__|uploads|candidate-data|backups)/", path
    ) or name.endswith(
        (
            ".dump",
            ".backup",
            ".sqlite",
            ".sqlite3",
            ".db",
            ".pem",
            ".p12",
            ".pfx",
            ".key",
        )
    ):
        add("private-or-generated-artifact")
    if len(blob) > 5 * 1024 * 1024:
        add("large-file-over-5MiB")
    for value in configured:
        at = blob.find(value.encode())
        if at >= 0:
            add("configured-credential-value", at)
    if b"\0" in blob:
        return findings, reviewed
    text = blob.decode("utf-8", errors="replace")
    for rule, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            add(rule, len(text[: m.start()].encode()))
    for m in ASSIGNMENT.finditer(text):
        record = dict(
            path=path, line=text[: m.start()].count("\n") + 1, rule="credential-literal"
        )
        if PLACEHOLDER.search(m[1]) or len(set(m[1])) <= 2:
            reviewed.append(
                {**record, "classification": "placeholder/synthetic literal"}
            )
        else:
            findings.append(record)
    return findings, reviewed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Preflight candidates; default scans exact staged content",
    )
    args = parser.parse_args()
    if args.worktree:
        paths = sorted(
            set(
                git("ls-files", "-z").decode().split("\0")
                + git("ls-files", "--others", "--exclude-standard", "-z")
                .decode()
                .split("\0")
            )
            - {""}
        )
    else:
        paths = [
            p
            for p in git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
            .decode()
            .split("\0")
            if p
        ]
    if not paths:
        parser.error("No files to scan; refusing to report an empty scan as PASS")
    # Read current backend credentials locally without printing values or importing app settings.
    from dotenv import dotenv_values

    configured = sorted(
        {
            variant
            for k, v in dotenv_values(ROOT / ".env").items()
            if v
            and len(v) >= 8
            and re.search(r"(API_KEY|SECRET|PASSWORD|TOKEN)", k)
            and v not in {"change-me", "changeme", "replace-me", "your-api-key"}
            for variant in (v, quote(v, safe=""))
        }
    )
    findings = []
    reviewed = []
    bytes_read = 0
    for path in paths:
        blob = (ROOT / path).read_bytes() if args.worktree else git("show", ":" + path)
        bytes_read += len(blob)
        bad, ok = inspect_blob(path, blob, configured)
        findings += bad
        reviewed += ok
    report = dict(
        mode="working-tree preflight" if args.worktree else "exact Git index blobs",
        files=len(paths),
        bytes=bytes_read,
        configured_values_checked=len(configured),
        findings=findings,
        reviewed_placeholders=reviewed,
        passed=not findings,
        scope="Pattern + current configured credential checks; not full history/PII certification",
    )
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: v for k, v in report.items() if k != "reviewed_placeholders"}, indent=2
        )
    )
    raise SystemExit(1 if findings else 0)


if __name__ == "__main__":
    main()
