# Phase 6B Approval A: isolated Gemini semantic evaluation results

Date: 15 November 2026. **The single approved Gemini attempt completed. All frozen numeric acceptance gates passed. Approval B remains unauthorized; no live ingestion was performed.** Independent human confirmation of context support and benchmark judgments remains pending.

## Approved scope and integrity

Request identifier: `2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b`.

Before execution, the exact request bytes, each of the 91 input hashes, the 30 compiled Software Engineer records and the unchanged 32-case dataset were verified. No approved input, question, gold label, difficulty, threshold, taxonomy, rubric or retrieval implementation was changed to obtain these results.

The configured credential was present and successfully authenticated against `models/gemini-embedding-001`. Credentials were supplied in an HTTP header, never printed or saved. The metadata endpoint confirmed model version `001` and the 2,048-token input limit. The model's `countTokens` endpoint checked all 91 inputs before embedding; the largest had **804 tokens**, so no truncation was needed.

The prepared `approved_embedding_run.py` was executed once via a local audit wrapper, `execute_approval_a.py`. The wrapper did not alter payloads or the backend embedding implementation: it verified each batch against the frozen input order/task/dimension, saved responses and recorded a one-attempt lock. It used the local virtual environment and existing backend settings rather than starting Docker services. No PostgreSQL driver/session was invoked. It preserved partial response artifacts in case a later batch failed; all three batches succeeded.

Documents used **RETRIEVAL_DOCUMENT**, queries used **RETRIEVAL_QUERY**, model **gemini-embedding-001**, requested and returned dimensions **768**. All returned vectors were finite, nonzero and complete. The cache uses the existing embedding function's normalized vectors.

## Actual operations, token counts and available billing

| Operation | Actual inputs | Actual calls | Tokenizer-counted input tokens |
| --- | ---: | ---: | ---: |
| Documents | 61 | 2 embedding HTTP requests, 50 + 11 | 20,703 |
| Queries | 30 | 1 embedding HTTP request | 826 |
| **Embedding total** | **91** | **3 successful HTTP requests** | **21,529** |
| Availability preflight | Model metadata only | 1 authenticated GET | Not an embedding |
| Token-limit preflight | The same frozen 91 texts | 91 countTokens requests | Counts shown above |

All three embedding requests returned HTTP 200: **50**, **11**, then **30** vectors. No automatic retry, additional semantic experiment, generation request, Azure operation or live-data embedding replacement occurred. The 31 legacy texts were re-embedded only from their frozen local snapshot for the approved isolated comparison; live vectors were not read or overwritten by this run.

[Google's standard embedding rate](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) is $0.15 per million input tokens. Applying it to the measured tokenizer counts gives an **estimated standard charge of $0.00322935**, comfortably below the approved **$0.05** allowance. This is not a verified bill: the embedding responses contained only `embeddings`, with no `usageMetadata`, billable-token total, invoice or account-tier information. Actual billed charge is **unavailable**; free-tier eligibility is unverified. The countTokens results are actual provider tokenizer measurements, not proof of billing consumption.

Measured embedding HTTP durations were **2.833 s**, **1.833 s** and **2.461 s**, totaling **7.127 s**; these exclude preflight, local setup and scoring. No application STT, TTS or interview-generation latency was measured.

## Frozen acceptance thresholds

Scoring used the original 32-case dataset: 30 positive questions, one per ten topics and three difficulties, plus two explicit policy abstentions. Primary-family relevance is 3; frozen related families are 1; other candidates are 0. Cosine ranking uses ten role/difficulty-eligible topic records per positive, without a topic predicate or gold label prepended to queries. The exact-topic arm is a separate functional check.

| Criterion | Frozen threshold | Measured result | Outcome |
| --- | --- | --- | --- |
| Primary Hit@1 | At least 24/30, 80% | **29/30, 96.67%** | PASS |
| Primary Hit@3 | At least 27/30, 90% | **30/30, 100%** | PASS |
| MRR | At least 0.85 | **0.9833** | PASS |
| Graded nDCG@3 | At least 0.80 | **0.9404** | PASS |
| Per-topic primary Hit@3 | At least 2/3 each | **3/3 for all ten** | PASS |
| Runtime role violations | Zero | **0** | PASS |
| Runtime difficulty violations | Zero | **0** | PASS |
| Explicit policy abstentions | Both abstain | **2/2** | PASS |
| Context technical support | Review required concepts, all misses and hard examples | Agent inspection complete; no critical contradiction observed | Independent human confirmation pending |

The two abstentions were `out-of-scope-ml` and `unknown-role`. Neither required a query embedding. They exercise explicit policy, not a learned semantic out-of-domain detector. Metadata checks here run over the frozen local copy; PostgreSQL ingestion and production SQL execution were not exercised.

## Performance by topic

| Topic | Cases | Hit@1 | Hit@3 | MRR | nDCG@3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Data Structures | 3 | 3/3 | 3/3 | 1.0000 | 0.9610 |
| Algorithms | 3 | 3/3 | 3/3 | 1.0000 | 0.9943 |
| Object-Oriented Programming | 3 | 2/3 | 3/3 | 0.8333 | 0.8045 |
| SQL | 3 | 3/3 | 3/3 | 1.0000 | 0.9173 |
| HTTP | 3 | 3/3 | 3/3 | 1.0000 | 0.9724 |
| REST APIs | 3 | 3/3 | 3/3 | 1.0000 | 0.9590 |
| Git | 3 | 3/3 | 3/3 | 1.0000 | 0.9392 |
| Testing | 3 | 3/3 | 3/3 | 1.0000 | 0.9173 |
| Debugging | 3 | 3/3 | 3/3 | 1.0000 | 0.9449 |
| Security Fundamentals | 3 | 3/3 | 3/3 | 1.0000 | 0.9943 |

## Performance by difficulty

| Difficulty | Cases | Hit@1 | Hit@3 | MRR | nDCG@3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Easy | 10 | 10/10 | 10/10 | 1.0000 | 0.9652 |
| Medium | 10 | 9/10 | 10/10 | 0.9500 | 0.9218 |
| Hard | 10 | 10/10 | 10/10 | 1.0000 | 0.9343 |

## Every primary retrieval failure

There is **one first-place miss and zero top-three misses**.

**`oop-medium`**: ?Checkout must support two payment providers with different error types. Where would you put the boundary so orchestration stays testable??

| Rank | Retrieved family | Cosine | Frozen relevance |
| --- | --- | ---: | ---: |
| 1 | Testing | 0.674668 | 0 |
| 2 | OOP, intended primary | 0.670335 | 3 |
| 3 | REST APIs | 0.627687 | 0 |

The top-two similarity gap is only **0.004333**. The testing note shares checkout, gateway, dependency-boundary and testability language, which plausibly explains the ordering; this is an interpretation, not a proven account of model internals. It offers useful testing context but does not establish composition/error translation. The second-ranked OOP record directly supplies the interface contract, composition and adapter-error concepts. Thus the primary is available to a top-three consumer, while a top-one consumer would receive incomplete design grounding. The frozen labels were not revised to credit the testing result after seeing it.

Recommended follow-up, not implemented: review whether OOP's shared scenario can state provider adapters, stable interface guarantees and error normalization more explicitly. Evaluate such a source revision on a fresh, independently authored holdout after separate approval. Preserve the existing correct role/topic/difficulty filtering; its explicit OOP topic path already narrows this scenario to the OOP record. Do not weaken thresholds or add a broad retry/budget expansion.

## Secondary-context omissions

For completeness, 17 cases omit a frozen grade-1 related family from their top three. These are **not primary Hit@3 failures**; they contribute to the graded nDCG result. Other grade-0 families also appear in lower positions. Full ranks, scores and contexts are retained in the detailed JSON.

| Case | Related family absent from top three |
| --- | --- |
| ds-hard | swe.algorithms |
| oop-easy | swe.debugging |
| oop-medium | swe.debugging |
| oop-hard | swe.debugging |
| sql-easy | swe.debugging |
| sql-medium | swe.debugging |
| sql-hard | swe.debugging |
| http-hard | swe.rest |
| rest-medium | swe.security |
| rest-hard | swe.security |
| git-easy | swe.testing |
| git-hard | swe.testing |
| testing-easy | swe.debugging |
| testing-medium | swe.debugging |
| testing-hard | swe.debugging |
| debug-medium | swe.testing |
| debug-hard | swe.testing |

The primary context still supports the case in each instance. Before investing in secondary recall, independently review whether these broad related-family labels represent necessary context, then freeze any new judgments in a new benchmark version. Do not rewrite this run's labels or claim all three returned records are equally relevant. If genuine multi-topic gaps remain, consider more specific source explanations or topic-aware reranking in a separately scoped change; this evaluation does not authorize an architecture change.

## Technical support quality

All 30 positives include the intended primary in the retrieved top three, and the agent inspected the required-support concepts against the actual retrieved text. No critical false guarantee or technical contradiction was observed. The corrected tree assumptions, SQL literal/transaction boundaries and retry/substitutability constraints appear in the evaluated texts.

These are short interview-grounding notes, not complete worked solutions. Several hard-level concepts appear as expected-concept prompts rather than implementations: deduplication recovery sizing, locking SQL, cross-system reconciliation, cursor mechanics, cache revocation and merge-mainline selection still require candidate reasoning or further reference material. This is adequate framing under the frozen retrieval criteria, not proof that the context alone teaches or verifies every implementation.

| Case | Primary rank | Support observations |
| --- | ---: | --- |
| ds-easy | 1 | Membership, expected hash lookup and ordering are explicit in the retrieved primary text. No worst-case constant-time claim is made. |
| ds-medium | 1 | Identity/normalization, first-record retention, seen-set memory and conflicting values are present. A full CSV validation policy is outside this note. |
| ds-hard | 1 | Durable identity, bounded retention, recovery and post-expiry duplicate behavior are explicit. Storage sizing and an actual seven-day recovery design remain candidate reasoning. |
| algo-easy | 1 | Sorted input, consistent comparison and shrinking interval are explicit. |
| algo-medium | 1 | Minimal two-element non-progress, interval conventions, midpoint progress and duplicate tests are explicit; executable corrected search code is not supplied. |
| algo-hard | 1 | Balanced-tree assumptions, logarithmic balanced operations, linear insertion/movement, locality and workload are explicit. Range-output cost is also named. |
| oop-easy | 1 | Shared mutable class state, per-instance initialization and a two-cart isolation test directly support the scenario; preferred-language explanation is permitted. |
| oop-medium | 2 | Rank 1 Testing supports fakes, dependency boundaries and integration contracts, but does not directly establish composition or error translation. Rank 2 OOP explicitly supplies the interface/composition/error-behavior concepts, so the top-3 context supports the full interview framing. |
| oop-hard | 1 | The primary hard example states retry guarantees and failure ambiguity, substitutability, weaker capabilities and external-side-effect limitations. It correctly permits rejecting an impossible universal guarantee. |
| sql-easy | 1 | LEFT JOIN preservation, null right-hand values and WHERE elimination are explicit; the paid string literal is correctly quoted. |
| sql-medium | 1 | Conditional UPDATE with stock>0, affected rows and transaction scope directly address the race. The note is conceptual rather than a complete production inventory implementation. |
| sql-hard | 1 | Lock ordering, serializable abort/retry safety, transaction boundaries and external effects are named; full locking SQL and distributed payment orchestration are not provided. |
| http-easy | 1 | The intended-effect definition and different DELETE response statuses are explicit and technically consistent. |
| http-medium | 1 | Unknown outcomes, durable idempotency storage, payload validation and lookup/reconciliation are explicit. Authorization is not replaced by method semantics. |
| http-hard | 1 | Durable state machine, provider idempotency, reconciliation and no naive exactly-once promise are explicit concepts; recovery implementation must still be reasoned through. |
| rest-easy | 1 | Stable resource identity, GET, documented missing-resource behavior and per-operation authorization are present. |
| rest-medium | 1 | Representation validators, conditional writes and conflict recovery support optimistic concurrency. Exact ETag/If-Match response examples are not provided. |
| rest-hard | 1 | Stable ordering, cursor contracts, concurrent mutation and client compatibility are explicit. Snapshot/cursor token mechanics remain design choices. |
| git-easy | 1 | New inverse commits, preserved shared ancestry and auditability are directly supported. |
| git-medium | 1 | Conflict intent, dependencies, deliberate resolution and forward-fix alternatives are directly supported. |
| git-hard | 1 | Merge-parent interpretation and code/data compatibility are explicit; selecting a concrete mainline and staging migration recovery require repository-specific facts. |
| testing-easy | 1 | Fixtures, controlled setup/teardown, shared mutable state and cleanup are explicit. |
| testing-medium | 1 | Fake failures, deterministic time, observable retry behavior and separately checked integration/mock contracts are directly supported. |
| testing-hard | 1 | Failure injection, idempotency assertions, integration boundaries and limited end-to-end tests support layered testing; test bodies are not supplied. |
| debug-easy | 1 | Inputs/environment, expected versus observed behavior, minimal reproduction and secret minimization are supported. |
| debug-medium | 1 | Request IDs, controlled two-request concurrency, shared state and a regression test directly match the query. |
| debug-hard | 1 | Scope, traces, falsifiable hypotheses and safe mitigation are explicit. The note avoids inferring root cause from recent changes alone. |
| security-easy | 1 | Identity versus permission, object ownership and server-side enforcement directly match the report-access example. |
| security-medium | 1 | Owner/policy-scoped lookup and two-user checks for reads and mutations directly support the scenario. |
| security-hard | 1 | Consistent policy, background principal, revocation and cache checks are explicit prompts. Concrete cache invalidation and share-token designs remain to be supplied by the candidate. |

This is agent technical inspection, not independent subject-matter-expert sign-off. An independent reviewer should confirm the benchmark relevance annotations and the OOP miss, and inspect the ten hard examples. No additional paid answer-generation or interview test was run, so question quality and final interview behavior are not established by these retrieval metrics.

## Isolated baseline comparison

Current live-corpus metadata policy yields **zero** eligible Software Engineer rows for all 30 positive cases. This was calculated from the frozen 31-row snapshot, not by writing or querying user records.

In the unfiltered legacy comparison, five queries have frozen grade-2-or-higher available support; **four of those five** retrieved substantial support in the top three with Gemini. Legacy partial support was not zeroed because the records carry an `ml_engineer` tag. Graded baseline nDCG@3 is approximately **0.6481 across 19 queries with nonempty relevance ideals**; the remaining 11 have no relevant ideal and are reported as unavailable rather than ranking failures. The expanded and legacy arms have different candidate sets/judgments, so their nDCG values are not a controlled causal improvement percentage. Per-query baseline row IDs, similarity and grades are saved.

## Saved evidence and reproduction without spending

- [Approved vectors](../storage/phase6b/approved-vectors.json), cache SHA-256 `fbf87e80d48c2c0f2926316aa451760791a5994ecf47a75e4cf854d89cde40c9`.
- [Frozen scorer results](../storage/phase6b/cached-semantic-results.json).
- [Detailed ranks, contexts, topic/difficulty aggregates and support review](../storage/phase6b/semantic-review-details.json).
- [Actual attempt/batch audit](../storage/phase6b/approval-a-execution.json).
- [Model availability](../storage/phase6b/live-model-preflight.json) and [all 91 token counts](../storage/phase6b/live-token-preflight.json).
- Raw successful response files `storage/phase6b/live-embedding-response-01.json` through `03.json`.
- Frozen request and source manifests remain unchanged. Their historical `approval_status` text remains untouched to preserve the approved byte hash; authorization and execution are recorded separately in the attempt audit.

These vector/audit artifacts are local ignored files. Preserve them together; they have not been committed or uploaded. Only cached scoring can be rerun without spending:

```powershell
.\.venv\Scripts\python.exe scripts/evaluate_phase6b.py --vectors storage/phase6b/approved-vectors.json
.\.venv\Scripts\python.exe storage/phase6b/analyze_approved_results.py
```

**Do not rerun the embedding command: the approved one attempt is consumed.** `approval-a-attempt.lock` protects the audit wrapper against accidental reruns. Any further provider attempt needs separate approval. Passing numeric gates does not grant Approval B.

## Decision and remaining work

**Numeric semantic acceptance: PASS. Independent human content/annotation confirmation: PENDING. Live rollout: NOT AUTHORIZED.**

Keep the reviewed source revision, dataset, request, vectors and reports frozen. The strongest next steps are independent support review, an unseen holdout with more provider-adapter and multi-topic scenarios, and future generated-question difficulty checks. Any new paid holdout or generation test needs its own approved scope. No source tuning, data ingestion, live re-embedding, grading change, schema change, LangGraph transition, Azure call, commit or push followed the evaluation.
