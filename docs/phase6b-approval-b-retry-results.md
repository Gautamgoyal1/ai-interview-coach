# Phase 6B Approval B retry: pre-commit rollback

> Current outcome: [local autonomous completion](phase6b-autonomous-completion.md). The reviewed 30 Software Engineer rows are committed and verified (61 total). Earlier failures and approval instructions below are historical; the newer user development policy governs local work.

Date: 15 November 2026. **The single approved retry did not complete. A pre-commit vector check failed and the transaction rolled back. No new knowledge records remain. No automatic retry or recovery was performed.**

## Fresh preflight passed

The revision-2 sources, manifest, evaluated cache and 30-row role-only plan matched all frozen identities. PostgreSQL contained exactly 31 original knowledge rows with the expected metadata/content/vector digest. The fresh plan proposed exactly 30 inserts, zero updates, zero retirements and zero deletions.

All application data, schema metadata and sequences matched the existing backup snapshot. The original backup was preserved and copied to `storage/phase6b/rollout-b-retry/backup-used.dump` for this attempt.

Backup SHA-256: `122c76e897434e97c15c57892c428e152016ef5e9193c824ad4495808955b688`. Size: **320,512 bytes**.

A fresh network-isolated PostgreSQL restore passed the corrected verifier:

- All **11 tables**: row counts and complete data digests matched.
- All **six sequences**, columns and constraints matched.
- All **36 indexes** matched, permitting only the documented fixed array-cast equivalence.
- **14 predicate-semantic checks** passed in both live and restored databases, including NULL cases.
- The temporary restore container was removed. No restore touched the live database.

## Guarded transaction and failure

The unchanged reviewed `approved_apply_software.py` was invoked once through an audit wrapper. Its file SHA-256 remained `4ec35a378a7a58957f6ea8d00abdafd7c9c6e725dc9acd82a2dd3142bc98e041`.

The wrapper rechecked frozen source/cache identities and the complete database baseline inside advisory lock `634220061`. It restricted SQL writes to `public.chunks` INSERTs and blocked provider HTTP requests. The prepared apply reused cached vectors and flushed the 30 rows in one INSERT statement within one transaction.

Before commit, my added vector verifier raised:

```text
AssertionError: Stored vector differs from evaluated float32 vector
```

The transaction never committed. Session cleanup rolled back its inserted rows, and no receipt was created. The attempt lock and error audit were retained. This was a verifier representation error, not demonstrated cache corruption.

## Read-only diagnosis and offline correction

The verifier required a decoded Python float to equal an exact float32 numeric value. The container's pgvector Python client, version **0.5.1**, decodes decimal vector text into Python floats. These can differ numerically from the exact float32 value while representing identical float32 storage bits.

All 30 approved vectors were tested through explicit PostgreSQL `vector(768)` casts in a read-only transaction, with no INSERT. This reproduced strict numeric inequality, but **all 30 matched the evaluated cache's float32 storage bits exactly**. The largest decoded difference from an exact float32 value was approximately **1.49e-08**.

The local deployment helper now compares IEEE float32 bit sequences rather than Python numeric equality. It does not loosen verification to a broad epsilon. Six offline checks passed: exact float32 and correct decimal decoding accepted; a one-ULP change, sign change, wrong dimension and NaN rejected.

The corrected helper was **not used for another ingestion attempt**. This diagnosis concerns read-only casts; it is not a post-commit verification of new rows, since none remain committed. No production dependency, application file, source record, frozen label/threshold or evaluated vector was changed.

## Actual final database state

Read-only verification after rollback confirmed:

| Item | Actual result |
| --- | ---: |
| Total knowledge rows | **31** |
| Committed new Software Engineer rows | **0** |
| Committed inserts / updates / retirements / deletions | **0 / 0 / 0 / 0** |
| Legacy rows matching frozen snapshot | **31** |
| Application table data digests | **All unchanged** |
| Live schema metadata | **Unchanged** |
| Other sequence values | **Unchanged** |
| `public.chunks_id_seq` | **31 ? 61** |
| Rollout receipt | **Not created** |
| Post-commit 61-row / retrieval verification | **Not run; no commit occurred** |
| New provider or Azure calls | **0** |
| Automatic ingestion retries | **0** |

Sequence allocation survives transaction rollback. The counter advance is therefore a real state change despite all table contents being unchanged. **It was not reset.** No retirement, deletion, restoration or other recovery write occurred. No inserted IDs are represented as a successful rollout receipt.

The legacy digest remains `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`. Source and cache hashes remain frozen. The broader folder/corpus ingestion and Approval A were not executed. No Git commit or push occurred.

## Remaining work and stopping boundary

**The approved one retry is consumed; activation remains incomplete.** The user required stopping after any failed check and prohibited automatic retries. No further apply was attempted after the verifier correction.

Before a separately authorized live attempt, rehearse the complete apply and corrected verifier against an isolated restored database. Fresh preflight must account for the advanced chunk sequence and create a current-state backup; the preserved backup accurately represents the earlier sequence value. Preserve it and all failure evidence. Do not reset the counter or restore the backup into live PostgreSQL automatically.

## Evidence

- [Retry summary](../storage/phase6b/rollout-b-retry/retry-result-summary.json).
- [Successful preflight and restore verification](../storage/phase6b/rollout-b-retry/preflight.json).
- [Apply error and locked identity checks](../storage/phase6b/rollout-b-retry/apply-audit.json).
- [Rollback integrity and sequence checks](../storage/phase6b/rollout-b-retry/failure-readonly-verification.json).
- [Explicit vector-cast storage-bit diagnosis](../storage/phase6b/rollout-b-retry/vector-explicit-cast-bit-verification.json).
- [Six offline comparison checks](../storage/phase6b/rollout-b-retry/vector-checker-offline-tests.json).

Evidence and private database backups remain local ignored files and have not been committed or uploaded.
