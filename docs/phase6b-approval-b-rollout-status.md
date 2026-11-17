# Phase 6B Approval B: rollout aborted during preflight

> Current outcome: [local autonomous completion](phase6b-autonomous-completion.md). The reviewed 30 Software Engineer rows are committed and verified (61 total). Earlier failures and approval instructions below are historical; the newer user development policy governs local work.

> Subsequent retry: fresh preflight passed, but the retry rolled back before commit on a vector representation check. See [retry results and current state](phase6b-approval-b-retry-results.md). No knowledge rows were added; the chunk sequence advanced.

Date: 15 November 2026. **Status: ABORTED BEFORE LIVE WRITES. No knowledge records were inserted.** The existing approval-guarded apply procedure was never invoked. This is an unsuccessful deployment attempt, not a completed rollout.

## Passed preflight checks

- Frozen Software Engineer source manifest, ten revision-2 source files, evaluation dataset/results, request artifact and evaluated cache matched the final review hashes.
- Role-only plan identifier remained `5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070`.
- The fresh explicitly read-only plan proposed exactly 30 inserts, zero updates and zero retirements. There was no delete operation. All required vectors were present in the existing cache; no provider call was needed.
- PostgreSQL held exactly 31 legacy knowledge records. Their full frozen content/vector digest remained `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`.
- Frozen artifacts and reviewed source files were copied into local ignored `storage/phase6b/rollout-b/frozen/` with matching byte hashes. No environment file or API key was copied into this preservation set.

## Backup and failed verification

A full PostgreSQL custom-format backup was produced from an exported repeatable-read snapshot while holding the existing managed-ingestion advisory lock. The connection was explicitly read-only. Backup location: `storage/phase6b/rollout-b/before-rollout.dump`.

- Size: **320,512 bytes**.
- SHA-256: `122c76e897434e97c15c57892c428e152016ef5e9193c824ad4495808955b688`.
- Backup archive listing was readable.
- The backup restored successfully into a temporary PostgreSQL/pgvector container using the same local image, no network and temporary storage.

The initial verifier compared `pg_get_indexdef` text exactly and failed on an equivalent cast representation in the pre-existing `uq_resume_analyses_active_fingerprint` index. This comparison was too strict. It did not establish lost data or an unsafe change to the live database.

Live index predicate:

```sql
(deleted_at IS NULL)
AND status::text = ANY (
  (ARRAY['processing'::varchar, 'completed'::varchar])::text[]
)
```

Restored predicate:

```sql
(deleted_at IS NULL)
AND status::text = ANY (
  ARRAY[('processing'::varchar)::text, ('completed'::varchar)::text]
)
```

The same two fixed string elements are converted to text either as an array or individually. Subsequent isolated-restore diagnosis confirmed:

- **All 11 tables** had identical row counts and data digests.
- All sequence values/called flags, column definitions and constraints matched.
- All other index definitions matched exactly; the sole difference was this array-cast formatting.
- A narrow normalization of only these two equivalent cast forms made the complete index-definition sets match. It does not ignore uniqueness, indexed columns, predicate literals or other index changes.
- Fourteen read-only PostgreSQL predicate checks, including NULL status and NULL/non-NULL deletion timestamps, agreed.
- Every temporary verification container was removed after use; the live database was never restored into or modified.

The saved backup is consequently **logically verified after diagnosis**, while the original strict verification failure is retained in the audit. The archive contains private application data and remains local/ignored; it has not been committed or uploaded.

## Why ingestion did not resume

The user's condition was: **?Abort if any verification fails or the reviewed source/database state has changed.?** The initial strict restore comparison failed, and the write was aborted before invoking apply. After diagnosing the false-positive metadata mismatch, this attempt was not automatically resumed or treated as a successful preflight.

The local backup comparison helper has now been corrected to accept only this exact equivalent cast representation while retaining all data, sequence, other-schema and index checks. Five offline checks passed: the equivalent cast was accepted; changed uniqueness, predicate values, table data and sequence state were rejected. The corrected preflight was not used to resume this aborted rollout. A subsequent attempt must recheck fresh database/source/cache state before proceeding. It must not reuse the initial raw index-text hash as proof of a substantive schema difference, nor broadly ignore index mismatches. The frozen knowledge sources, vector cache and approval-plan identifier do not need changing for this verifier issue.

## Final database state and actual changes

A final explicitly read-only transaction confirmed the entire live application state still matches its preflight snapshot: all table data digests, schema metadata and sequence state are unchanged.

| Item | Actual result |
| --- | ---: |
| Total knowledge records | **31** |
| New Software Engineer records | **0** |
| Inserts / updates / retirements / deletions | **0 / 0 / 0 / 0** |
| Verified legacy records | **31** |
| Apply procedure invoked | **No** |
| Post-commit verification | **Not applicable; no commit occurred** |
| Rollout receipt with inserted IDs | **Not created; no IDs were allocated** |
| Paid embedding/generation calls | **0** |
| Azure calls | **0** |
| Source/vector/evaluation changes | **0** |
| Commits / pushes | **0 / 0** |

The 156-row folder and 183-row full-corpus ingestion were not executed. Approval A was not rerun. User analyses, interviews, reports, practice data, scoring, other roles and live schemas remain unchanged. No automatic retirement, deletion or recovery action occurred.

## Evidence

- [Final aborted-attempt summary](../storage/phase6b/rollout-b/aborted-rollout-summary.json).
- [Original backup verification failure](../storage/phase6b/rollout-b/backup-verification.json).
- [Isolated restore diagnosis](../storage/phase6b/rollout-b/backup-diagnosis.json).
- [Exact index-definition difference](../storage/phase6b/rollout-b/index-definition-differences.json).
- [Fresh role-only preview](../storage/phase6b/rollout-b/preflight-preview/preview-software-only.json).
- [Preserved artifact hashes](../storage/phase6b/rollout-b/preserved-artifacts.json).

No production code or database schema was changed to perform this diagnosis. The local preflight/diagnostic helpers and this report are the only new tooling/documentation for the aborted attempt.
