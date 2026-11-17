# PrepMate knowledge sources

The existing 31 study-note files remain intact. Phase 6 adds 15 original, scenario-based source records in `software_engineering/` and `role_foundations/`; these compile into difficulty-specific chunks for explicitly assigned roles. Existing Python notes are not copied into new language tutorials. The role-neutral data-structure/OOP records add engineering scenarios and misconceptions to the earlier Python-focused coverage.

## Authorship and provenance

New notes use original explanations and scenarios with AI-assisted drafting and primary-document checks. They are not scraped interview-question banks. `sources.yaml` records primary references and review dates. CC-BY-4.0 covers the new original PrepMate notes only; it does not relicense linked documentation or legacy files. Retain record IDs, source URLs and attribution when redistributing them. Legacy files retain their original `own work` metadata, including `n/a` references; stronger legacy provenance remains a review backlog.

## Structured source format

Keep the existing Markdown front matter convention. New records add `knowledge_id`, `schema_version: 1`, positive `revision`, explicit `status: active|retired`, comma-separated canonical role IDs in `roles`, canonical `skill`, an HTTPS primary `source_url`, `reviewed_on` and the notes license. `difficulty: mixed` means the compiler emits separate easy/medium/hard rows, each containing shared concepts plus only its own question, expected answer concepts and follow-up. Sample questions ground the existing generator; they do not replace adaptive generation.

Required body sections: Definition, Core principles, Practical applications, Common misconceptions, Engineering scenario, Trade-offs and limitations, Provenance, Easy, Medium, Hard. `README.md` files are documentation and are not ingested. Every other Markdown source must validate; malformed files fail the entire preview instead of silently disappearing.

Role and skill definitions live in `backend/app/modules/resume/`. Keep `roles.json` and `skills_taxonomy.json` in their existing dictionary/list formats; `role_catalog.json` and `skill_metadata.json` add IDs, classifications, aliases, relationships and expectations. `validate_catalog()` checks consistency. A source skill must belong to every assigned role. Sharing a source across roles reuses the authored text and one embedding per difficulty, while storing explicitly scoped rows in the existing table.

## Preview and approval

From a running Compose backend:

```sh
docker compose exec -T backend python -m app.modules.knowledge.ingest_cli
```

This is read-only and does not call the embedding service. It shows insert/update/retire actions, unchanged counts, unique embedding inputs, orphaned managed source IDs and an approval token. The root `scripts/ingest_knowledge.py` remains a compatibility wrapper for local use; its default container root is `/app/knowledge_base`, so pass `--root knowledge_base` when running from the repository root.

Only after a human explicitly approves that exact preview:

```sh
docker compose exec -T backend python -m app.modules.knowledge.ingest_cli --apply --approve-plan <reviewed-token>
```

Do not run the apply command without that approval. A changed source/database plan invalidates the token. No apply command was executed during Phase 6.

## Identity, updates and retirement

New rows use `source_name = prepmate:<knowledge_id>:<role_id>:<difficulty>` as a stable managed identity. Do not rename IDs to update content. Increment `revision` when revising a record; review the generated update and embedding estimate. Approved updates retain row IDs. Explicit retirement retains the row, source text and ID, marks its role as the reserved `retired` value and excludes it from retrieval. It does not delete historical citations or any user data. Reactivating an active source is a reviewed update.

Removing a source file or role assignment does not silently retire rows: the preview reports orphaned managed identities. Retire the relevant assignments explicitly before removing their source representation. Legacy rows retain the original hash convention and remain append-only through this tool; no legacy data migration is implicit.

All embeddings are obtained and validated before row mutation. The caller owns one transaction and commits only on success. PostgreSQL advisory locking serializes this ingestion path. Re-running an unchanged import requests no embeddings. Identical shared text across role rows is embedded once per apply operation.

The model remains `gemini-embedding-001`, with 768 dimensions matching the existing pgvector column. The tool checks the actual column type before any embedding request and refuses model/dimension changes. No model change, index creation, schema migration or live regeneration is part of this release.

## Offline evaluation

`eval_data/phase6_retrieval.json` contains repeatable role/topic/difficulty cases. Run the opt-in PostgreSQL tests only against the local test environment:

```sh
docker compose exec -T -e PREPMATE_KNOWLEDGE_POSTGRES=1 backend pytest -q -s tests/integration/test_phase6_knowledge.py
```

The tests create and drop unique `test_phase6_<uuid>` schemas and use deterministic hashed lexical vectors. They exercise real pgvector SQL and ingestion lifecycle behavior; they do not measure Gemini semantic ranking quality. Live Gemini evaluation remains a separately approved quota-consuming check.
