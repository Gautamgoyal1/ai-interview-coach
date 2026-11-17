# Phase 6B: local rollout completed and question realism tested

Date: 15 November 2026. **COMPLETE in the local development database.** PostgreSQL now contains **61 knowledge rows**: the original 31 unchanged rows plus exactly 30 reviewed Software Engineer records. The user?s autonomous development policy superseded the previous per-attempt Approval B stop/reapproval workflow for work within this local scope and budget. No production deployment, commit or push occurred.

## Vector verification defect and durable fix

The previous failure was caused by comparing Python float64 values parsed from pgvector decimal text with exact float32 numeric values. Those numbers can differ while representing identical PostgreSQL storage bits.

`app.modules.knowledge.verification` now canonicalizes values to IEEE float32 bytes and compares those bytes. It validates dimensions, finite values and float32 range. It rejects a one-ULP change rather than using a broad numerical tolerance. Local deployment checks import this tested helper instead of maintaining a separate comparison implementation.

An actual PostgreSQL/pgvector reproduction in a disposable restored database demonstrated the old equality failure. The fixed checker then passed real INSERT/commit/fresh-connection reads, and rejected a deliberately corrupted stored component. Unit tests cover decimal round-trips, exact float32 values, one-ULP changes, sign changes, dimensions, NaN, infinity, range overflow and invalid expected data.

## Isolated rehearsal and regression results

- Fresh full database backup: `storage/phase6b/autonomous-rollout/backup-used.dump`, SHA-256 `d34946dc829af870cbd6f6d60fcb1ae0c503cc9c696a6960637d1bcccfd32c39`.
- An isolated restore verified all 11 tables, six sequences, column/constraint metadata, 36 indexes and the narrowly documented cast equivalence. A new backup was required because the earlier rollback had advanced the chunk sequence.
- The full 31-to-61 ingestion was rehearsed and committed in a separate disposable PostgreSQL container. A fresh connection verified all new metadata/vectors, preserved legacy/user data and an idempotent preview. All 32 cached retrieval cases were exercised there.
- **Final full backend suite: 306 passed, zero skipped**, including opt-in PostgreSQL ingestion/retrieval and vector-storage tests. Two existing deprecation warnings remain (`crypt` and the HTTP-422 constant).
- **13 new regression cases** in this task: eight vector unit cases, two persisted-vector integration cases and three Hard-context projection cases.
- Nine existing offline Phase 6B preparation tests passed in the focused regression run. Frontend tests/build were not rerun; this task makes no frontend changes.
- Every disposable restore/rehearsal container was removed after use. Tests did not write to existing user tables in the local development database.

## Actual local database changes

The reviewed Software Engineer-only apply procedure ran under advisory lock `634220061`, with frozen files and the exact plan rechecked inside the lock. It reused evaluated Gemini document vectors and committed one 30-row INSERT transaction. Provider HTTP calls were blocked during ingestion.

| Item | Verified final result |
| --- | --- |
| `public.chunks` total | **61** |
| Original legacy records | **31, exact original digest preserved** |
| New active Software Engineer records | **30** |
| Difficulty distribution | **10 Easy, 10 Medium, 10 Hard** |
| Allocated new database IDs | **62?91**, every ID saved in receipt |
| Updates / retirements / deletions | **0 / 0 / 0** |
| Other application table contents | **Unchanged, complete data digests compared** |
| Live schema and other sequence values | **Unchanged** |
| Chunk sequence | **61 ? 91**, earlier rolled-back ID gap retained |
| Repeat role-only preview | **Zero changes, zero embedding inputs** |
| New embedding / Azure Speech calls | **0 / 0** |

All 30 new source names, roles, topics, difficulties, content, source URLs, licenses, content hashes and float32 vector bits were compared with the reviewed manifest/cache from a new read-only connection. The original legacy metadata/content/vector digest remains `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`.

No user analysis, resume, interview, report, practice record, grading weight or historical score was changed. The 156-row folder and 183-row full-corpus plans were not applied. Source revisions, taxonomy and approved embedding inputs were not changed.

Receipt SHA-256: `444dd173ce143a96121a9acd8d84b8d9bd49349fc34d4a8bef4b8588f0f2e6d0`. The receipt is preserved at both `storage/phase6b/rollout-receipt.json` and `storage/phase6b/autonomous-rollout/rollout-receipt.json`. Evaluated cache SHA-256 remains `fbf87e80d48c2c0f2926316aa451760791a5994ecf47a75e4cf854d89cde40c9`.

## Actual PostgreSQL retrieval

These are real database cosine queries using cached query vectors, not mocked rankings or new embeddings:

| Measurement | Result |
| --- | ---: |
| Broad role/difficulty primary Hit@1 | **29/30, 96.67%** |
| Broad role/difficulty primary Hit@3 | **30/30, 100%** |
| MRR | **0.9833** |
| Graded nDCG@3 | **0.9404** |
| Strict topic-scoped primary checks | **30/30** |
| Explicit abstentions | **2/2** |
| Role/difficulty violations | **0** |

The previously reviewed OOP Medium first-place miss remains in broad semantic ranking; its primary context is second. No frozen label or threshold was changed to improve these results. Actual topic-scoped retrieval selects the intended OOP context.

## Question-generation experiments and improvements

Question tests used the actual newly stored rows and synthetic candidate context only. They called the configured Azure OpenAI provider, `gpt-5.4-mini`, through the existing generation pipeline. They did not create interview/user records or call grading.

Measured defects were addressed rather than just relabelling output:

1. The first test?s HTTP-level observer did not observe SDK requests. Its nine generation operations are retained but are not labelled free, mocked or fully metered. Metering moved to `responses.create`, recording returned token usage and preserving the ledger across experiments.
2. A Hard Algorithms sample asked a routine binary-search boundary-debugging question. Prompt guidance now requires an experienced Hard decision with concrete constraints and trade-offs, and states needed contract assumptions.
3. Prompt wording alone did not prevent Hard OOP from drifting to the shared beginner cart scenario. Structured Hard generation context now prioritizes the selected Hard question/expected concepts plus definition, trade-offs and provenance. It omits competing shared beginner scenarios for question generation only. Raw stored context, retrieval, grading context, Easy/Medium and unstructured legacy notes remain unchanged.
4. OOP iterations included an obvious yes/no violation and a cart-state regression. These remain preserved as unsuccessful depth experiments. The final focused example states the actual retry and outcome contract and asks for the adapter/capability decision.

### Final Easy / Medium / Hard smoke test

Each final result was matched against its metered SDK response, so curated fallbacks were not counted as successful AI generation:

**Easy ? SQL**

How does a LEFT JOIN differ from an INNER JOIN?

**Medium ? Object-Oriented Programming**

Imagine your checkout flow currently calls one payment provider directly, but next month the business may switch to a different provider without changing the checkout logic. How would you structure that using OOP?

**Hard ? Algorithms**

Suppose you need to support a workload with frequent inserts and frequent range queries over numeric keys. One design keeps the keys in a sorted array; another uses a balanced binary search tree. How would you decide between them, and what are the worst-case time costs of insert and range query for each under the usual balance assumptions?

### Additional final Hard OOP check

Consider a `PaymentGateway` interface that promises: if `charge(amount, idempotency_key)` is called again with the same key and amount, it will not create a second charge, even after a timeout, and callers can later ask for the final outcome. If one adapter cannot honor that because its provider ignores idempotency keys and offers no outcome lookup, what should you do with that adapter and why?

The final Hard Algorithms question requires workload reasoning and explicit balance/cost assumptions; the Hard OOP question makes the observable contract and provider limitation explicit. These are agent quality observations on a small sample, not proof of general difficulty calibration or grading accuracy.

## API usage, budget, failures and retries

Provider: **Azure OpenAI**. Requested and returned model: **gpt-5.4-mini**. Gemini embeddings were reused, so Gemini requests in this task were **zero**. Azure Speech calls were **zero**.

| Usage | Measured / estimated result |
| --- | --- |
| Metered SDK requests | **14 successful, 0 provider failures** |
| Metered input tokens | **15,525** |
| Metered output tokens | **1,206** |
| Metered generation operations | **11**, with **3 validator-driven extra attempts** |
| Initial unmetered operations | **9**, actual raw request count unavailable; **9?18 possible attempts** |
| Total possible provider-request count | **23?32**, not an exact billing count |
| Metered public-list-price comparison | **$0.01707075** |
| Allowance for initial unknown usage | **$0.871263** |
| Final conservative estimated exposure | **$1.074753 of $2** |
| Actual Azure account bill | **Unavailable** |

The reference estimate uses [OpenAI?s published gpt-5.4-mini rate](https://developers.openai.com/api/docs/models/gpt-5.4-mini), $0.75/M input and $4.50/M output tokens. It is **not verified Azure account pricing**. The budget guard reserves future requests using much higher $10/M input and $40/M output assumptions, text-byte input bounds and the existing 4,000 output-token cap. The initial unmetered batch is conservatively allowed up to 18 attempts, bounded input text, 4,000 output tokens each and twice the public reference rate. This is an estimated accounting limit, not a provider-enforced cap or actual bill.

SDK transport retries remain disabled. The three metered extra attempts were the existing question-quality validator?s regeneration behavior. The initial observer assertion failure and unsuccessful Hard-depth examples were retained, fixed and retested within the same scope; development did not stop for another approval. No additional embedding experiment was needed.

## Files changed in this task

- `backend/app/modules/knowledge/verification.py`
- `backend/app/modules/interview/question_generator.py`
- `backend/app/modules/interview/prompts.py`
- `backend/tests/unit/test_vector_verification.py`
- `backend/tests/integration/test_vector_storage.py`
- `backend/tests/unit/test_question_context.py`

Also added this completion report and `docs/development-testing-policy.md`. Historical status reports link here while retaining prior failure evidence. Ignored local operator scripts, backups, XML test results, database receipts, model outputs and usage logs are retained under `storage/phase6b/`. Existing uncommitted Phase 6 work was preserved. No dependency or schema migration was added.

## Remaining limitations

- The original unmetered batch?s exact request/token usage cannot be reconstructed from retained responses; the budget ledger records that uncertainty rather than inventing measurements.
- The sources remain short interview-grounding notes, with the previously documented Hard implementation-depth gaps. This task did not expand to other roles or the full curriculum.
- Difficulty quality remains probabilistic. A small live question sample improved after measured fixes; broader independent holdouts, generated-answer review and interview-level grading checks remain future work.
- No browser interview or human microphone acceptance was performed here. Azure Speech behavior was not changed.
- The application server was not deployed or started as part of this data rollout. No production environment, credential, Git commit or push was changed.

## Evidence

- [Completion summary](../storage/phase6b/autonomous-rollout/completion-summary.json).
- [Inserted-ID rollout receipt](../storage/phase6b/autonomous-rollout/rollout-receipt.json).
- [Final row/vector/retrieval verification](../storage/phase6b/autonomous-rollout/postcommit-verification.json).
- [Zero-change preview](../storage/phase6b/autonomous-rollout/postcommit-idempotent-preview.json).
- [Final isolated rehearsal](../storage/phase6b/autonomous-rollout/isolated-rehearsal.json) and [full test XML](../storage/phase6b/autonomous-rollout/backend-tests.xml).
- [SDK usage and budget ledger](../storage/phase6b/autonomous-rollout/api-usage.json).
- [Final representative questions](../storage/phase6b/autonomous-rollout/generated-questions-final.json) and [focused Hard OOP question](../storage/phase6b/autonomous-rollout/generated-questions-oop-focused.json).

Backups contain private application data; all backups and model/audit artifacts remain local ignored files and were not uploaded or committed.
