# Local storage policy

This directory holds runtime files and local development evidence, not a portable
database snapshot. Do not commit candidate uploads, transcripts, credentials,
database exports, generated embedding caches, audio, or raw provider receipts.

The named experiment directories in `.gitignore` were reviewed as local artifacts.
They remain on disk. New directories are not automatically hidden: review them
before staging. Keep reusable code under `scripts/`, application code under
`backend/` or `frontend/`, and synthetic fixtures under `eval_data/` or
`backend/tests/fixtures/`.

`phase6b/rollout_b_checks.py` is an explicitly reviewed source exception because
historical operators import it. Its companion manifests, database snapshots,
vectors and receipts stay local. Those operators require their original private
inputs; they are not fresh-install bootstrap commands.
