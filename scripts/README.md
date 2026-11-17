# Developer tools

Run commands from the repository root unless noted otherwise. Ordinary tests are
offline; model evaluations and ingestion apply operations can spend API quota.

## Fresh-clone tools

| Tool | Purpose |
|---|---|
| `test_backend_isolated.py` | Builds on an existing Compose backend image; fresh disposable pgvector database, migrations, offline regressions and local JUnit output |
| `scan_staged_secrets.py` | Scans exact Git index blobs; `--worktree` is a separate preflight, never a substitute for the staged scan |
| `ingest_knowledge.py` | Compatibility wrapper for the backend ingestion CLI; defaults to preview, requires an explicit token for apply |
| `phase7_meter.py` | Local request/cost guard used by historical evaluation operators; estimates, not provider billing |
| `tests/` | Offline tooling tests using synthetic data and checked-in knowledge sources |

The backend suite's PostgreSQL tests use synthetic embeddings and disposable
schemas. The public isolated runner does not need any `storage/phase*` backup,
candidate record, embedding cache or provider credential.

## Historical experiments

`prepare_phase6b.py`, `phase6b_readiness.py`, `evaluate_phase6b.py`,
`phase7_prepare.py`, `apply_phase7_local.py`, `audit_phase7_questions.py`,
`evaluate_phase71.py`, `evaluate_phase72.py` and
`evaluate_practical_interviews.py` preserve the development procedure and its
approval/hash/budget guards. Their default manifests, snapshots, vector caches
and receipts are private local inputs, deliberately absent from Git.

These operators are **not** bootstrap scripts for a new install. Some bind exact
historical row counts, source revisions or plan hashes. A missing/mismatched input
must abort, not be replaced with a fabricated file. Apply tools can write to the
configured database; do not execute them as a documentation smoke test.

Earlier root `evaluate_grader.py`, `evaluate_retrieval.py` and related tools also
have their own model/data assumptions. Review each entrypoint before running it.

Browser verification scripts require a running app, the appropriate synthetic
account/fixtures and Playwright. Some still reference the original local
`storage/voice-acceptance/node_modules` installation. They are preserved historical
helpers, not a clean-clone browser test command. No Playwright dependency is added
to the application by this repository-maintenance change.

`storage/phase6b/rollout_b_checks.py` is intentionally versioned source: historical
operators import it. Its private data companions remain ignored. Public evaluation
fixtures under `eval_data/` and `backend/eval_data/` are tracked independently of
runtime result caches.
