# Phase 6B command sheet

> Current outcome: [local autonomous completion](phase6b-autonomous-completion.md). The reviewed 30 Software Engineer rows are committed and verified (61 total). Earlier failures and approval instructions below are historical; the newer user development policy governs local work.

> Subsequent execution: the single approved Approval A run is complete. See [actual semantic results](phase6b-semantic-evaluation-results.md). The embedding command below is an historical preparation record and must not be rerun under the consumed approval. Approval B remains unauthorized.

Date: 15 November 2026. Run from `D:\ai-interview-coach` in PowerShell. **Only the preview and offline commands were executed.** Paid evaluation, live apply, retirement and restoration require separate explicit user approval under the Phase 6B request. A hash identifies the reviewed input; it does not itself grant approval.

The prepared command files live in ignored `storage/phase6b/` for review. They are not a new backend API, automatic deployment hook or committed release. Their approved write/provider paths have not been exercised. Keep the frozen files together and preserve them before deployment.

## A. Read-only preview — safe to run now

```powershell
docker compose start db
.\.venv\Scripts\python.exe scripts/prepare_phase6b.py --db-host 127.0.0.1
.\.venv\Scripts\python.exe scripts/evaluate_phase6b.py --surrogate
```

The first Python command uses PostgreSQL `REPEATABLE READ` plus `SET TRANSACTION READ ONLY`, snapshots knowledge only, and writes local files. The second performs in-memory scoring with non-semantic vectors. Run `.\.venv\Scripts\python.exe scripts/phase6b_readiness.py` afterward to regenerate the source inventory, request hash and cost estimate. Neither calls an embedding provider or updates PostgreSQL.

The baseline directory is a **pre-rollout freeze**, not a general post-deployment capture utility. Archive/protect it before applying anything. Do not overwrite `legacy-snapshot.json` with the 61-row post-rollout corpus; that would invalidate the comparison and recovery audit. Editorial changes require a new frozen directory/review before approval.

For comparison, this is the existing **full 183-row** read-only CLI, not the recommended apply scope:

```powershell
docker compose run --rm --no-deps backend python -m app.modules.knowledge.ingest_cli
```

Do not apply that full plan or use `--root /app/knowledge_base/software_engineering` as a Software Engineer-only scope: the folder includes 156 rows across roles. The role-only preview is `storage/phase6b/preview-software-only.json` and selects exactly 30 compiled items without rewriting their metadata.

## B. Paid isolated evaluation — NOT AUTHORIZED OR EXECUTED

The four content corrections and SQL provenance cleanup are complete at source revision 2; previews/manifests/costs have been refreshed. Before executing, verify input token fit and account/model availability and obtain explicit approval of the frozen request contents and spending envelope. See [final readiness review](phase6b-evaluation-readiness.md). The current request is 61 document inputs (31 isolated baseline + 30 new) and 30 query inputs. All account operations use the configured Gemini Developer API; no Azure calls are involved.

The reviewed request hash is currently:

`2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b`

After Approval A only:

```powershell
docker compose run --rm --no-deps -e PREPMATE_PHASE6B_PAID_APPROVAL=2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b backend python /app/storage/phase6b/approved_embedding_run.py
.\.venv\Scripts\python.exe scripts/evaluate_phase6b.py --vectors storage/phase6b/approved-vectors.json
```

The one-off container does not start the application server or connect to the database. It uses `RETRIEVAL_DOCUMENT` for documents, `RETRIEVAL_QUERY` for queries, model `gemini-embedding-001`, and 768 dimensions. The prepared script refuses missing/mismatched approval and changed input counts/model/hashed text. It has no automatic retry. If a provider phase fails, record any charged usage and seek approval before a new attempt; do not silently expand the scope or retry until success.

The scorer only reads cached vectors. It rejects stale model/task/dimension/dataset/source metadata and invalid vectors. Passing its numeric gates is necessary but insufficient: review required concepts, all misses, hard-level examples and any critical technical error. No cached Gemini result exists yet.

## C. Live Software Engineer rollout — NOT AUTHORIZED OR EXECUTED

Obtain separate Approval B after the semantic/manual review. Confirm that `cached-semantic-results.json` comes from real approved vectors and passes the numeric gates. Freeze the evaluated source files; confirm the role-only plan still contains exactly 30 inserts and zero updates/retirements. Retain the 31-row snapshot and original metadata hashes.

The current role-only plan token is:

`5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070`

After Approval B only:

```powershell
docker compose start db
docker compose run --rm --no-deps -e PREPMATE_PHASE6B_LIVE_APPROVAL=5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070 backend python /app/storage/phase6b/approved_apply_software.py
```

This prepared command reuses the evaluated document-vector cache through the existing `apply_plan(..., embedder=...)` extension point. It makes no new embedding request. It checks the semantic result, unchanged source manifest, embedding space, exact live plan, live corpus count and legacy digest. It acquires the existing ingestion advisory lock. In one transaction it inserts only the 30 selected rows and verifies the original 31 again before commit. Any pre-commit assertion or flush failure aborts the transaction.

The ordinary existing CLI would make new paid embedding requests for pending text. Do not substitute it casually: cached evaluation reuse and Software Engineer-only filtering are explicit parts of this prepared command.

After commit, preserve `rollout-receipt.json`, which binds all 30 new row IDs, source names and hashes. If receipt-file writing fails after a successful database commit, do not rerun apply. Run the read-only check below and review its reconstructed `postcheck-receipt.json` before using it as a recovery receipt.

## D. Post-rollout read-only verification — prepared, not executed

```powershell
docker compose run --rm --no-deps backend python /app/storage/phase6b/readonly_postcheck.py
```

Expected: 61 total rows; the original 31 rows match their snapshot including vectors; exactly 30 new active Software Engineer rows; ten per difficulty; a repeated scoped preview has no changes and no embedding inputs. This command performs no embeddings or writes to PostgreSQL. It writes a local verification receipt.

Then exercise approved read-only retrieval using the evaluated query vectors and inspect role, difficulty, source attribution and expected-concept support. Do not create real user analyses/interviews or invoke Azure Voice to test ingestion. A future real-generation smoke check is separate provider usage and requires its own approval/budget.

## E. Scoped retirement or restoration — NOT AUTHORIZED OR EXECUTED

First stop using the rollout for new retrieval if it fails the agreed checks. Before a post-commit recovery, obtain Approval C and inspect the receipt against the current rows. If any ID, source name, content hash or expected role has changed, the prepared command refuses the operation so a fresh recovery plan can be reviewed.

After explicit retirement approval only:

```powershell
docker compose run --rm --no-deps -e PREPMATE_PHASE6B_RETIRE_APPROVAL=retire:5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070 backend python /app/storage/phase6b/approved_retire_software.py
```

Only the 30 exact receipt rows have `role` changed from `software_engineer` to reserved `retired`. IDs, source text, vectors and hashes stay intact. The shared retrieval policy already excludes retired rows. The legacy 31 and all user tables are outside the mutation scope. There is no delete, truncate, model change or migration.

A role-only retirement leaves the active source hash unchanged. Therefore a plain unchanged-source ingestion preview may skip the retired row; **do not assume it reactivates it**. Restore the original role explicitly, after diagnosis and separate restoration approval:

```powershell
docker compose run --rm --no-deps -e PREPMATE_PHASE6B_RETIRE_APPROVAL=restore:5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070 backend python /app/storage/phase6b/approved_retire_software.py --restore
```

These guarded write paths are prepared for operator review; only their no-approval exit paths and Python syntax were checked in Phase 6B. No live rollback, retirement, restoration or destructive operation was performed.
