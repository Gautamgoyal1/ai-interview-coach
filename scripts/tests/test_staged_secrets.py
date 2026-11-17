import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "scanner", Path(__file__).parents[1] / "scan_staged_secrets.py"
)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


def test_detects_provider_shapes_and_configured_values_without_echoing_them():
    google = "AIza" + "A" * 35
    private = "-----BEGIN " + "PRIVATE KEY-----"
    findings, _ = scanner.inspect_blob(
        "src/example.py",
        (google + "\n" + private + "\n" + "local-live-value").encode(),
        ["local-live-value"],
    )
    assert {f["rule"] for f in findings} == {
        "google-api-key",
        "private-key",
        "configured-credential-value",
    }
    assert all(
        google not in str(f) and "local-live-value" not in str(f) for f in findings
    )


def test_templates_hashes_and_synthetic_fixtures_are_not_provider_keys():
    text = 'POSTGRES_PASSWORD="change-me"\nTOKEN="' + "a" * 64 + '"\n'
    findings, reviewed = scanner.inspect_blob(".env.example", text.encode())
    assert not findings and reviewed


def test_sensitive_paths_remain_findings_even_without_key_patterns():
    for name in [
        ".env.production",
        "storage/backups/database.dump",
        "frontend/node_modules/file.js",
    ]:
        findings, _ = scanner.inspect_blob(name, b"not a credential")
        assert findings


def test_ui_password_labels_are_not_credential_assignments():
    findings, _ = scanner.inspect_blob(
        "frontend/Label.tsx", b'aria-label={shown ? "Hide password" : "Show password"}'
    )
    assert not findings
