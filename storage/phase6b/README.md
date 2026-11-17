# Historical rollout verification source

`rollout_b_checks.py` contains reusable verification functions imported by the
versioned historical Phase 6B/7 operators. It is source code, not a database dump.
Its constants identify frozen approval plans and caches; they are not API tokens.

The private companion data is deliberately not shipped. Functions that verify a
specific historical rollout require the original local manifests and snapshots.
Do not replace missing evidence with fabricated files or run old apply commands
as a new installation step. Use the public ingestion preview and the standalone
isolated regression runner documented in the repository README instead.
