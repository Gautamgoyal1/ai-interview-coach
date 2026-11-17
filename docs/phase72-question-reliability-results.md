# Phase 7.2 — question reliability implementation and results

Date: 2026-11-16. **The constrained AI path improved on this fresh evaluation; the semantic screen remains unreliable.** Agent review passed **26/28 delivered hybrid AI questions**, versus 5/8 provider questions in Phase 7.1. Only two new-run deliveries used fixed fallbacks. This improvement therefore does not come from increasing the fallback share.

These are **provisional agent judgments**, without independent human or blinded review. The new architecture constrains technical content more tightly than the earlier freeform specification generator, and the cohorts differ. These results do not establish general reliability outside the reviewed families or a production release approval.

[All 32 evaluation outcomes, actual questions, per-question scores, rejected drafts and development failures](phase72-question-results.md) are preserved. No production code changed after the final holdout began. Original Phase 6B/7/7.1 evidence and labels remain frozen.

## Diagnosis and OOP verification

The 30-case Phase 7.1 holdout contained:

| Construction outcome | Count | Finding |
|---|---:|---|
| Provider question delivered | 8 | Five passed agent review; three did not |
| Valid draft rejected by semantic screen | 8 | False rejections, often demanding that the question prescribe its implementation |
| Negative draft correctly rejected by screen | 11 | Genuine clarity, correctness or depth problems |
| Deterministic contract rejection | 2 | Contradictory OOP capability and SQL output missing its declared row identity |
| Provider timeout | 1 | 60-second failure followed by fallback |

There were no demonstrated malformed-JSON failures in that holdout. Broadly calling all 22 fallback paths “generation failures” obscured the actual causes. The screen rejected valid implementation choices as missing requirements; some real defects also came from undefined processing effects, SQL scope/grain and wording projection.

Before changing the generator, four fresh OOP configurations exercised the final Phase 7.1 correction with real Azure generation and PostgreSQL RAG. Two provider outputs retained **“Unavailable capability:”** correctly: bounded reader rollback and plugin publication. The other two cases used fallbacks: one contradictory achievable/unavailable specification failed validation, and one valid staged-writer draft was rejected for depth. The qualifier correction fixes a real compiler defect, but does not solve every OOP construction or screening problem. Some baseline wording remained awkward.

Isolated regressions now cover positive and negatively phrased unavailable capabilities, capability contradictions, every reviewed variant's visible facts, maximum prose budgets, private-field exclusion and ranked SQL output meanings. The compiler no longer replaces a ranked output's full meaning with only its identity.

## Hybrid construction

`problem_families.py` introduces **44 agent-reviewed role/topic/profile-specific technical kernels**, with boundary and extension variants. They cover ten Software Engineer topics across entry/senior profiles; aliases such as Software Developer resolve through the existing role catalog. Other roles and uncovered narrow topics retain their existing construction path. No retrieval taxonomy or database records were changed.

Each kernel fixes its assumptions, output/invariant, failure boundary, implementation goal and valid alternatives. The AI response contains only:

```text
family_id
variant: boundary | extension
scenario: 15–100 characters
reasoning_decision: 35–180 characters, one question
follow_up_direction: 15–200 characters, private
```

The AI chooses the variant and authors the setting, primary ask and private follow-up using the actual RAG facts and candidate context. The compiler instantiates the full existing typed problem specification, then validates and renders it. A wrong family ID, altered contract, invalid scope, malformed response or failed review never becomes a successful question. No automatic repair chain or second generation attempt was added.

**“Hybrid AI” is deliberately narrower than freeform generation.** The technical kernel is authored/reviewed application content; the model does not invent arbitrary new invariants. The evaluation operator confirms successful provider output matches the compiled delivered question before classifying it as hybrid AI. Returning a fixed bank question is counted separately as fallback. This distinction matters when interpreting the higher pass rate.

Examples of stronger kernels include a balance increment committed atomically with its durable event identity; SQL selection and aggregates over one explicit snapshot; bounded non-seekable rollback; atomic manifest publication with recoverable cleanup; signed retry identities with explicit expiry; and reset-token consumption racing with reissue. Scope and capability limits are explicit instead of being left for the model to improvise.

Three fixed fallback texts were added only where Phase 7.1 measured exhaustion: one distinct reset-token task per profile and an experienced snapshot/aggregate SQL task. Total fixed fallback texts increased from 42 to 45; they are not the 44 hybrid kernels. Existing reservation and revocation variants continue to share family coverage. New reset-token work is a distinct security competency, not another revocation paraphrase.

### Compiler and session behavior

Candidate text is organized as setting, coherent technical contract and primary ask. Internal derived indexes do not become another decorative checklist. Exact/contained duplicate facts are removed; debugging's synthetic internal goal is omitted; HTTP punctuation is normalized; output meanings and unavailable-capability qualifiers are preserved. Private solutions, predictions, follow-ups and coverage markers stay private. The existing 900-character bound remains, with 1,200 for SQL schema clarity.

The same plain text can be displayed or passed to existing TTS. No STT/TTS code, configuration or playback/recording behavior changed. SQL declarations remain dense when spoken, and occasional semantic repetition remains; there was **no live Azure Speech or microphone verification** in this task.

Both variants use the same private family marker. Known curated questions in older histories are recognized even if their sessions predate family markers, reducing paraphrase recycling. After genuine same-topic/profile exhaustion, generation is explicitly unavailable. The saved-answer recovery path, idempotent retry, evaluation persistence and mock difficulty behavior remain unchanged and are covered by the existing integration tests.

The final policy remains at most one generation plus one screen under a shared ten-second model deadline. Provider retries remain disabled. Retrieval retains its existing timeout behavior; the ten seconds is not a global end-to-end SLA.

## Screen simplification and development evidence

The hybrid path uses a shorter defect-oriented review: minimum reasoning, one blocking issue, an exact question quote and a reason. Issues include technical correctness, clarity, depth, profile, scope and session duplication. The prompt retains the frozen seven-axis standard, but no longer asks for seven redundant numeric judgments during generation. Independent evaluation still records all seven axes and novelty.

A defect must cite real candidate-facing text. Invented quotes are controlled screening-format failures. Harmless diagnostic-length excess is bounded for logging rather than causing another paid request; decisions/evidence are not rewritten to force acceptance. New diagnostic logs identify provider, format, contract, presentation, text-validation and screen stages, including Pydantic field/error codes without raw candidate input or provider internals.

Development results were retained rather than overwritten:

- First eight-case hybrid pilot: seven valid-JSON responses exceeded prose limits, one draft was semantically rejected, zero hybrid deliveries. The schema was supplied in the prompt, not enforced by an API structured-output mode.
- After explicitly stating limits and concise examples: zero format failures, four hybrid deliveries and four screen rejections in eight development cases. No truncation of technical facts or automatic paid retries was used.
- One already charged calibration response was replayed locally after fixing diagnostic-length parsing. It was not regenerated.

The same unchanged 16-case development reference set has seven positive and nine negative labels:

| Screen | Gate false accepts / 9 negatives | False rejects / 7 positives | Invalid reviews |
|---|---:|---:|---:|
| Phase 7.1 final reference result | 4/9 | 1/7 | 0 |
| Phase 7.2 initial simplified review | 1/9 | 4/7 | 1 negative case |
| Phase 7.2 reviewed distinctions | 4/9 | 3/7 | 1 negative case |

Invalid reviews count as rejection in gate totals. Among valid negative reviews only, false accepts were 1/8 and then 4/8. All positive references had valid reviews. Development distinctions helped some depth judgments and hurt negative detection. **There is no evidence that the final screen is a generally better calibrated oracle.** Its remaining false accepts are a release concern, even though constrained generation produces fewer defective drafts.

## Fresh preregistered evaluation

Manifest SHA-256:

`1a8178d42bfbcab543c1fe90d07bc0669e43f2e651308b43ee28daecefbec199`

The final run used new Rust/SQLite and Scala/PostgreSQL candidate profiles, 15 normal requests per profile over all ten topics, and actual in-session history. A sixteenth security request per profile deliberately exhausted both reviewed families. These two probes are reported separately so availability is not hidden or counted as a quality success.

The frozen pass rule is R=T=H=E=C=2, L/F≥1 and session novelty, on 0–2 axes. No thresholds or labels changed after seeing outputs. The real configured Azure provider and Gemini query embeddings retrieved role/difficulty-scoped context from PostgreSQL. No permanent user interviews or paid grading sessions were created; this exercises the actual retrieval/generation nodes, not a full paid adaptive interview.

| Final outcome | Delivered | Agent passes | Pass rate |
|---|---:|---:|---:|
| Hybrid AI | 28 | 26 | **92.9%** |
| Fixed fallback | 2 | 2 | **100%**, n=2 |
| All delivered | 30 | 28 | **93.3%** |
| Fresher delivered | 15 | 15 | 100% |
| Experienced delivered | 15 | 13 | 86.7% |

Each profile delivered 14 hybrid questions and one fallback. Provider delivery was 28/30 normal requests (93.3%); **passing hybrid output per normal attempt was 26/30 (86.7%)**, counting both rejected and failed provider drafts against the AI path. That avoids presenting only selectively accepted output as generation reliability.

Unavailable: **0/30 normal requests**, **2/32 all requests (6.25%)**, both planned probes. There were zero observed critical technical correctness failures, session novelty failures, silent downgrades or off-topic fallbacks. The fresh final OOP questions preserved their stated limitations. These are observed provisional results, not proof of absence in future generation.

All failures and screen disagreements:

- **E07, experienced Git — FAIL (H=1):** the contract already rules out old binaries and the ask prescribes forward recovery. The faulty behavior and compatibility details are too generic to force substantial implementation reasoning. The screen accepted it.
- **E08, experienced Testing — FAIL (C=1):** the body requires lost-write/mixed-generation oracles, while the primary ask narrows to paused-reader lifetime. A narrower answer can satisfy the ask without the central write-visibility oracle. The screen accepted it. Its opening also repeats the first technical sentence.
- **F08 provider draft — false rejection:** latest-query results and B-specific error states are already observable; naming concrete component props is an implementation choice. A valid same-topic testing fallback was delivered.
- **E04 provider draft — false rejection:** deadlock retry and same-ID committed-outcome recovery belong to one transaction lifecycle. The contract explicitly defines rollback and replay; this was not an unrelated bundled task. A valid reservation fallback was delivered.

Across all 30 screened drafts: **2 false rejections / 28 agent-positive drafts (7.1%)**, and **2 false acceptances / 2 agent-negative drafts (100%)**. All reviews parsed and cited actual question text. The negative denominator is very small and defective drafts are less prevalent than in Phase 7.1; this cannot support a broad specificity claim.

## Performance and API usage

Times start before RAG retrieval and include Gemini query embedding, SQL retrieval, construction, validation and screening. p95 uses nearest rank.

| Cohort | Median | p95 | Maximum |
|---|---:|---:|---:|
| Phase 7.1 original 30 | 6.195 s | 18.301 s | 61.692 s |
| Phase 7.2 normal 30 | **4.740 s** | **6.346 s** | **6.613 s** |
| Phase 7.2 all 32 | 4.695 s | 6.346 s | 6.613 s |
| Two expected unavailable probes | 1.519 s | 1.765 s | 1.765 s |

There were **zero provider timeouts** in this task. Shorter structured output and review replaced the earlier large repeated specification/screen payloads, but different cohorts and external service conditions prevent an isolated causal latency claim. Across all development/evaluation requests, generation median/p95 was 1.992/3.233 seconds; screening 1.396/2.323; embeddings 0.694/1.269. Cancellation regressions preserve bounded failure behavior even though no final live timeout was induced.

Actual total task usage:

- Azure OpenAI **`gpt-5.4-mini`**: **124 requests**, 50 construction and 74 screening; **180,932 input / 11,718 output tokens**.
- Gemini **`gemini-embedding-001`, 768 dimensions**: **52 query-embedding requests**, zero document embeddings. Estimated 6,044 query tokens from characters/4, not provider-reported usage.
- **176 sent requests**, all provider responses succeeded. Local parsing/screening failures remain in evidence. Zero SDK retries and zero automatic regeneration calls.
- Conservative booked estimate **$0.595350** under the $2 task budget. Public-price reference estimate **$0.189337**. **Actual billing unavailable.** No Azure Speech calls.

The guard reserves with $2.50/M Azure input, $10/M Azure output and $1/M Gemini embedding input before sending. Reference arithmetic uses $0.75/$4.50 and $0.15 respectively. [OpenAI model pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini) is not a verified Azure invoice; [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) is a public estimate. Full request counts, token receipts, timings and reservations are in `storage/phase72/api-usage.json` and `execution-summary.json`.

## Regression and database verification

- **428 backend tests passed**, zero skipped, against a verified disposable PostgreSQL restore with external paid HTTP blocked. Two existing deprecation warnings remain. The earlier 425-test run also passed before three executable SQL examples were added.
- **113 focused construction/contract tests passed**, including all 44 families' two variants and maximum prose budgets; the final 62-case hybrid module additionally checks projection of all candidate-visible contract facts.
- Three new PostgreSQL examples assert actual expected rows for independent counts, latest eligible identity/ties/missing parents, and same-snapshot selection plus independent aggregates/NULLs. They corroborate these kernels, not every possible SQL implementation.
- **3 budget guard tests passed**. **49 frontend tests passed** and TypeScript/Vite production build passed. Existing bundle-size/Router warnings remain.
- An intermediate full run crashed in an existing concurrency test using two SQLite sessions on one `StaticPool` handle. The fixture now uses an isolated file with independent connections, closes its setup session and disposes the engine; application authentication/interview behavior was not changed. Final JUnit and `isolated-regression.json` confirm child exit 0 and 428 passes. The log-capture PowerShell wrapper separately returned 1 on Docker progress stderr; it was not a pytest failure.

Read-only final verification confirms **61 chunks**, 31 unchanged legacy records and 30 Software Engineer rows (ten each difficulty), all expected 768-dimensional float32 vectors and idempotent scoped ingestion preview. All eleven live tables' contents, schema and sequences match preflight; **zero knowledge/user-data writes**. Legacy digest remains:

`0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`

All **551 frozen prior evidence files** and evaluated production hashes remain unchanged. No grading weights, historical evaluations, LangGraph state/routing, reports, HR flow, Azure Voice, resume or Practice production code was modified in Phase 7.2. Full regression covers the preserved saved-answer/restart/retry behavior; no new browser or live microphone acceptance is claimed.

## Changed files and remaining work

Production:

- `backend/app/modules/interview/problem_families.py` — reviewed kernels and scoped variant instantiation.
- `problem_construction.py` — hybrid path, explicit prose limits, bounded review and staged diagnostics.
- `problem_spec.py` — non-revocation security boundary contract and safer readable projection.
- `question_quality.py` — shorter evidence-grounded review alongside the unchanged legacy screen.
- `hard_fallbacks.py` — three narrowly justified distinct fallback texts and their shared coverage mappings.

Tests: new `unit/test_reviewed_families.py`, new `integration/test_reviewed_sql_examples.py`, updated `unit/test_problem_contracts.py`, legacy-path fixture in `unit/test_phase7_questions.py`, and the concurrency fixture in `integration/test_phase39_reliability.py`. Operator: `scripts/evaluate_phase72.py`; reports and local evidence helpers. Existing unrelated uncommitted work was preserved.

Next work should target the observed failures: make experienced Git kernels require a concrete compatibility decision; tie the AI ask explicitly to the family's required reasoning coverage; and independently adjudicate screen disagreements on a new development set before another preregistered evaluation. Do not fix E07/E08 and silently replace these results. More general knowledge rows or more fallback volume would not address those causes.

The constrained path meets the recorded cohort's provisional quality target and delivers passing AI questions far more often. The screen remains a weak link, coverage is finite, other roles retain the legacy path, and SQL/voice presentation still needs usability review. No deployment, commit, push or merge was performed.

Technical references for kernel primitives, not endorsements of the generated questions: [OWASP reset-token guidance](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html), [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).
