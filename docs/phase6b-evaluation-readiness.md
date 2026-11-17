# Phase 6B: corrected content and evaluation readiness

> Subsequent execution: the single approved Approval A run is complete. See [actual semantic results](phase6b-semantic-evaluation-results.md). The embedding command below is an historical preparation record and must not be rerun under the consumed approval. Approval B remains unauthorized.

Date: 15 November 2026. **Ready for a separate isolated Gemini evaluation approval. Live rollout remains on hold.** This report supersedes the pre-correction input hashes and editorial findings. No paid requests, live ingestion, grading changes, LangGraph transitions, Azure operations, commits or pushes were performed.

## Corrections reviewed

All ten records in `knowledge_base/software_engineering/` are now revision **2**. Each had the irrelevant generic Python/OOP attribution sentence removed, so every record's revision and all 30 compiled Software Engineer hashes changed. The original metadata identities, assigned roles, taxonomy, chunk compiler and embedding recipe are unchanged. The five role-foundation records and all legacy source files are unchanged.

| Record | Correction |
| --- | --- |
| Algorithms, hard | Explicitly compares a sorted array with a balanced binary search tree, asks for balance/worst-case assumptions, and distinguishes logarithmic balanced operations from linear degeneration and array insertion. |
| OOP, easy | Allows the candidate's preferred language or a language-neutral object explanation. Shared and per-object state are the concepts; Python attribute lookup is not treated as universal. |
| OOP, hard | Defines same-key/same-amount deduplication across timeouts and eventual-outcome lookup before identifying the violating adapter. Expected concepts allow rejecting an incapable adapter or exposing a weaker workflow; a local deduplication table cannot eliminate uncertain external side effects by itself. |
| SQL, easy | Uses the string literal `WHERE orders.status = 'paid'`. The regression executes this filter and verifies that unmatched LEFT JOIN rows are removed. |
| SQL provenance | Maps joins/filter placement, isolation/retries, conditional UPDATE/row counts, aggregates, index predicates and string constants to their respective PostgreSQL 16 documentation. `sources.yaml` carries the supporting references too. |
| Other Software Engineer notes | Removes the unrelated Python/OOP sentence while retaining the applicable primary reference and original-notes licensing statement. |

The review checked the corrected prompts, expected concepts and follow-ups at easy, medium and hard levels. These changes clarify source material; they do not alter interview rubrics or scores. Python-specific examples remain valid examples where stated explicitly. The retained CC-BY-4.0 statement applies to original PrepMate notes, not third-party documentation.

## Fresh read-only database preview

The preview ran in a PostgreSQL repeatable-read, explicitly read-only transaction and rolled back. Only the existing database container was started; the interview application was not started for testing.

| Scope | Inserts | Updates | Retirements | Unique embedding inputs |
| --- | ---: | ---: | ---: | ---: |
| Full corpus | 183 | 0 | 0 | 45 |
| Software engineering folder, all assigned roles | 156 | 0 | 0 | 30 |
| **Software Engineer role only** | **30** | **0** | **0** | **30** |

The role-only plan is ten topics times three difficulties. It retains all 31 existing rows untouched; after a separately approved rollout, the expected total would be 61. The folder plan is not role-only. Exact duplicate/identity and complete-source validation passed. Shared cross-role text is intentional; no semantic near-duplicate guarantee is claimed.

The 31-row snapshot, including metadata, text, IDs and vectors, still matches the pre-correction capture:

`0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`

A before/after hash check also confirms that all **81** inspected backend module Python/taxonomy JSON files are unchanged by this correction pass. Existing uncommitted Phase 6 work was preserved.

## Final frozen input identities

| Artifact | SHA-256 / plan identifier |
| --- | --- |
| Software manifest digest | `02f5660e48757787b255e38b0151e333dfdaaffc745c44642e572590005c9f44` |
| Evaluation dataset, unchanged | `6f4f43b0734bafb783209c1735e046c3c4a7293f0e3160ed0a22cc7fe473d424` |
| **Gemini request manifest / evaluation approval identifier** | **`2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b`** |
| Role-only ingestion plan, separate future approval | `5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070` |
| Full-corpus preview, outside proposed rollout | `a194aef552fa8274da2c1f243e94a80a41886ab1df19bee6ac9b8fddb1482696` |
| Folder preview, outside proposed rollout | `dca782068d73efb91bde7a2f76e5d00e933aa954dd6f94281749683bdb5ba08b` |

The previous evaluation hash and rollout token are superseded. The old evaluation hash was tested and refused before importing provider code. A hash binds approval to reviewed inputs; it is not authorization.

The final [request manifest](../storage/phase6b/embedding-request-manifest.json) contains the exact text and SHA-256 for each of **61 documents and 30 queries**. Documents comprise 31 isolated legacy inputs (historical subtopic prefix retained) and 30 revised Software Engineer inputs. No legacy vector will be overwritten. The [software manifest](../storage/phase6b/software-manifest.json) enumerates all 30 compiled rows, their original role metadata and ingestion content hashes. The [readiness inventory](../storage/phase6b/evaluation-readiness.json) records each of the ten source-file hashes and revision numbers. Pre-correction artifacts remain archived in `storage/phase6b/before-content-corrections/`.

## Usage and expected cost

Configured provider: **Gemini Developer API**, model `gemini-embedding-001`, dimensions **768**. Documents use `RETRIEVAL_DOCUMENT`; queries use `RETRIEVAL_QUERY`. No Azure usage is involved.

The [official standard price](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding), checked 15 November 2026, is **$0.15 per million input tokens**. The synchronous `batchEmbedContents` calls do not qualify for the asynchronous Batch API discount. The account's free/paid tier is unverified.

| Scope | Inputs | Characters | Estimated tokens, characters / 4 | Estimated USD |
| --- | ---: | ---: | ---: | ---: |
| Isolated evaluation documents | 61 | 109,626 | 27,406.5 | $0.004111 |
| Isolated evaluation queries | 30 | 4,663 | 1,165.75 | $0.000175 |
| **Isolated evaluation total** | **91** | **114,289** | **28,572.25** | **$0.004286** |
| Software-only documents, if separately re-embedded | 30 | 61,230 | 15,307.5 | $0.002296 |
| Full prepared curriculum, outside proposed rollout | 45 unique | 91,700 | 22,925 | $0.003439 |

Evaluation requires three HTTP requests: 50 + 11 documents, then 30 queries. These are measured text counts with heuristic token estimates, not provider token counts or actual charges. The largest input is 4,464 UTF-8 bytes; the largest new input is 2,687 bytes. Byte length does not establish compliance with the 2,048-token input limit. Confirm token fit and model/account availability as part of the separately approved provider preflight; never silently truncate frozen inputs or switch models. Any resulting input change requires a refreshed manifest and approval.

A suggested spending envelope is **$0.05 for one attempt**, including reasonable token-estimation headroom; this is not an API-enforced billing cap. At 2,048 tokens per input the model-limit reservation is $0.0279552. Retries, generation and infrastructure are not included. The prepared runner has no automatic retry. A future rollout can reuse evaluated document vectors with no further embedding charge; ordinary ingestion would embed pending text again. [Machine-readable cost estimate](../storage/phase6b/cost-estimate.json).

## Frozen evaluation criteria

The unchanged [32-case dataset](../eval_data/phase6b_software_semantic.json) has 30 positives (one per topic/difficulty) and two policy-abstention cases. The semantic arm uses role/difficulty filtering, **ten eligible topics per positive**, no topic predicate and no gold topic label prepended to the query. Exact-topic filtering is checked separately and is not evidence of semantic ranking quality. The comparison includes unfiltered legacy ranking and current-runtime empty Software Engineer scope. Legacy relevance is graded from text, including useful Python/OOP content, rather than zeroed because of its role tag.

Required gates remain frozen:

- Primary hit@1 at least **24/30 (80%)**.
- Primary hit@3 at least **27/30 (90%)**.
- MRR at least **0.85**; graded nDCG@3 at least **0.80**.
- At least **2/3** primary hit@3 for every topic.
- **Zero** runtime role/difficulty violations; both policy negatives abstain.
- Manual support review of required concepts, all misses and all hard-level results; no critical unsupported technical conclusion. Numeric metrics alone do not authorize rollout.

The dataset is author-curated rather than an independent holdout. Gold relevance/support judgments need human confirmation. There is no tuned semantic out-of-domain threshold. Shared advanced scenario text in easy chunks still requires eventual generated-question difficulty review; field labels alone cannot prove cognitive difficulty.

## Offline validation and regression results

- Targeted source/taxonomy/preparation checks: **41 passed** (32 taxonomy/source tests plus nine preparation tests).
- Full backend plus preparation suite: **300 passed, two skipped**, one existing Starlette HTTP-422 deprecation warning. The skipped cases are opt-in disposable-PostgreSQL ingestion tests; no PostgreSQL ingestion test was enabled in this pass.
- New regressions cover revision/provenance, balanced-tree assumptions, language choice and explicit retry guarantees, and executable quoted SQL behavior. Existing tests cover metadata policy, scoped source selection, metric arithmetic, legacy relevance and cache validation.
- Compiler validation and regenerated manifests: passed. Exactly 30 selected identities remain; all 30 hashes changed as expected; no source/row identity was added or removed.
- Three prepared provider/write commands refused missing approval; the embedding runner also refused the superseded request hash before any provider access. Approved execution paths remain untested.
- Revised lexical surrogate: hit@1 **19/30**, hit@3 **23/30**, MRR **0.7220**, nDCG@3 **0.6960**; policy negatives **2/2**. This deliberately non-semantic diagnostic fails the semantic gates and **does not predict Gemini quality**. The acceptance thresholds were not changed.
- **Real Gemini evaluation: NOT RUN. Live PostgreSQL ingestion: NOT RUN.** Frontend tests/build were not rerun because this pass changes no frontend code.

## Exact next steps after separate approval

Reproduce the safe preparation from PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_phase6b.py --db-host 127.0.0.1
.\.venv\Scripts\python.exe scripts/evaluate_phase6b.py --surrogate
.\.venv\Scripts\python.exe scripts/phase6b_readiness.py
```

The following is prepared **only for explicit approval of the frozen paid evaluation**, and has not been executed:

```powershell
docker compose run --rm --no-deps -e PREPMATE_PHASE6B_PAID_APPROVAL=2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b backend python /app/storage/phase6b/approved_embedding_run.py
.\.venv\Scripts\python.exe scripts/evaluate_phase6b.py --vectors storage/phase6b/approved-vectors.json
```

The one-off container neither starts the backend server nor connects to PostgreSQL. Its input guard binds the exact request manifest. Save the cache, actual provider usage, numeric report and manual findings before deciding on the separate live-rollout request. A failed/partial paid run needs a reviewed retry request, not an automatic rerun.

[Updated command sheet](phase6b-rollout-commands.md) contains the separate rollout/postcheck/receipt-scoped recovery commands. They remain unauthorized. Do not substitute the full-corpus ingestion CLI. The live database must remain at its original 31 rows until rollout is explicitly approved.

## Files changed in this correction pass

- Ten revision-2 Markdown notes in `knowledge_base/software_engineering/` and SQL reference entries in `knowledge_base/sources.yaml`.
- `scripts/tests/test_phase6b_preparation.py`: four additional content regressions; nine total tests.
- `scripts/phase6b_readiness.py`: offline source inventory, request identity and reproducible cost measurements.
- This report, refreshed `docs/phase6b-live-knowledge-validation.md` and `docs/phase6b-rollout-commands.md`.
- Regenerated ignored local previews, manifests, cost estimates, diagnostics and approval-guard checks in `storage/phase6b/`; the reviewed future-run scripts stay there too.

No new dependency, schema, taxonomy, RAG architecture, rubric, historical score, user-data record or voice implementation change is included.
