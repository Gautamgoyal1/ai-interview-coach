# Phase 7.1 — reliable Hard-mode construction: implementation and measured results

Date: 2026-11-16. **Recommendation: HOLD the question-quality release.** Functional safeguards and recovery are implemented, but the unseen quality target was not met. The original 30-case holdout produced **22/30 passing returned questions (73.3%)**, below 80%. A separate ten-case check returned seven questions, four passing, including one critical OOP projection error. That projection error was subsequently corrected and tested offline; there is no new paid unseen evaluation of the final correction.

All quality assessments here are **agent-only**, without independent human adjudication or blinded review. The LLM screen is not treated as ground truth. [Complete question texts, scores, reasons, rejected drafts and calibration evidence](phase71-question-results.md) accompany this report. Original Phase 6B/7 labels, thresholds and artifacts remain frozen.

## Implemented construction path

Hard questions now use one structured construction response, deterministic validation and one bounded rubric screen. Candidate wording is compiled from the validated specification, without a separate phrasing call. Easy/Medium generation and interview grading remain on their existing paths.

The internal Pydantic `ProblemSpecification` contains:

| Field | Purpose |
|---|---|
| `role`, `experience_level`, `topic`, `requested_difficulty` | Authoritative request identity; difficulty fixed to Hard |
| `competency`, `scenario` | Tested skill and concrete setting |
| `assumptions`, `constraints` | Explicit conditions, indexed from the technical contract |
| `observable_goal`, `edge_case` | Candidate-visible output/invariant and failure boundary |
| `reasoning_decision` | One primary implementation/decision question |
| `valid_alternative_approaches` | At least two distinct private approaches |
| `follow_up_direction` | Private extension direction |
| `technical_contract` | Discriminated SQL/OOP/security/HTTP/debugging/general contract |

The provider authors a compact six-field draft (`competency`, `scenario`, `reasoning_decision`, alternatives, follow-up, contract). The compiler supplies request identity and derives repeated assumption/constraint/goal/edge indexes from contract facts. It also accepts the complete schema. This reduces duplicated provider output while preserving a complete typed internal object. Unknown fields are rejected. Private solutions, follow-up direction, debugging predictions and family markers are not exposed in the question API.

The complete JSON Schema is saved at `storage/phase71/problem-spec-schema.json`; the topic-pruned SQL draft schema is `provider-draft-schema-sql.json`. Candidate text keeps the 900-character Hard limit except **SQL, which allows 1,200** to retain schema and output semantics. Existing Easy/Medium bounds are unchanged. Compaction removes only exact/contained repeated facts, not arbitrary explanatory text.

### Deterministic checks and their limits

- **SQL:** declared tables/columns/primary keys, unique table/output names, all structured references defined, result identity returned, ranked identity unique and present in ordering and output. Known-table/backticked prose references are checked without misclassifying domain names or namespaced functions. Time eligibility, NULL/missing rows and join/aggregate rules are required candidate-visible fields.
- **OOP:** explicit caller guarantee, multi-step workflow, failure observation and achievable versus capability-split contract. A split requires an explicitly unavailable capability; an achievable contract cannot simultaneously declare that capability unavailable. The final compiler labels the latter **“Unavailable capability:”** rather than accidentally rendering it as a promise.
- **Security:** revocation must exercise the same principal/resource/action that was allowed before and denied after. Enforcement boundary, freshness and unaffected permissions are explicit.
- **HTTP:** mutation, effects, principal-scoped retry identity, changed-body behavior, concurrent/lost-response behavior and guarantee boundary are mandatory.
- **Debugging:** at least two different hypotheses with distinct predicted observations, available controls, and a coexistence policy.

These checks establish structured relationships. They do **not** prove that arbitrary prose is logically coherent, that every SQL join has the correct cardinality, or that an answer implementation exists. Remaining mistakes in processing-effect boundaries, SQL time/grain semantics and OOP guarantees demonstrate this limit. Valid alternatives are not rejected merely for omitting one preferred solution keyword.

### Fallback, novelty and recovery

There are 42 reviewed fallback texts across the ten covered topics and entry/senior profiles. Selection requires the requested role's catalog skills and the actual canonical topic. Broad retrieval aliases do not authorize borrowing a different topic's fallback. Finite coverage is intentional: no unused same-topic/profile Hard question means explicit `QuestionGenerationUnavailable`, never a Medium relabel or off-topic substitution.

Private reasoning-family markers share coverage between construction and fallback, in addition to existing text fingerprints. Reservation/outbox variants and authorization-transition variants are grouped so changing nouns does not reset coverage. Markers use the existing persisted fingerprint history; no graph state schema or database migration was introduced. This is reviewed-family coverage, not a general semantic proof against all paraphrases.

If generation is unavailable at interview start, the API returns controlled 503 and creates no session. If the previous answer was already evaluated, its answer and available evaluation are persisted first from durable evaluation history. A pending-generation snapshot is saved in existing session configuration JSON. Refresh returns `generation_unavailable=true`, no fabricated current question and no false completion.

The owner-only `POST /interview/{session_id}/retry-question` resumes after retrieval without repeating answer evaluation, difficulty advancement or turn submission. It creates only a valid next turn and clears pending state. Duplicate retries return current state without another generation call; duplicate submission of an already answered turn is rejected. The existing question/session fields remain compatible, with an additive availability flag and explicit retry endpoint. Mock assessment uses the same saved-answer recovery behavior. Grading failures remain unavailable, not invented scores.

The frontend shows a saved-answer recovery panel with an explicit retry action. It clears the local answer only after the backend confirms saving; End Interview remains accessible. This does not change recording, playback or transcript submission behavior.

## Evaluation design and results

Configured models: **Azure OpenAI `gpt-5.4-mini`** for construction/screening and **Gemini `gemini-embedding-001`, 768 dimensions**, for actual query retrieval against PostgreSQL. Synthetic profiles were passed to real interview nodes and RAG; no permanent interview sessions were created for evaluation.

Twenty development configurations preceded the benchmark. The holdout manifest and production hashes were frozen before executing 30 unseen configurations: 15 Fresher and 15 experienced, covering all ten Software Engineer topics with conceptual/applied variants and in-session history. The exact original wording and verdicts are retained, including failures.

The seven-axis frozen rule is R=T=H=E=C=2, L/F≥1, plus in-session novelty; each axis is scored 0–2. A familiar data structure is not automatically a duplicate. An unavailable result is not a passing question.

| Original 30-case holdout | Returned | Pass | Fail |
|---|---:|---:|---:|
| Provider specification → compiled question | 8 | 5 | 3 |
| Curated fallback | 22 | 17 | 5 |
| Total | 30 | 22 | 8 |
| Fresher | 15 | 11 | 4 |
| Experienced | 15 | 11 | 4 |

There were zero unavailable results, silent difficulty downgrades, off-topic fallbacks or T=0 critical technical failures in this original cohort. Four failures were in-session family repetitions; other failures included generic Git recovery, ambiguous interval boundaries, a shallow authorization predicate and undefined “processed once” effects.

| Quality comparison | Returned | Agent passes | Provider / fallback |
|---|---:|---:|---:|
| Latest supplied Phase 7 baseline | 61 | 30 | 48 / 13 |
| Phase 7.1 original holdout | 30 | 22 | 8 / 22 |

These are different configuration sets and substantially different fallback mixtures. The higher returned-question pass proportion does not establish an isolated causal improvement in provider generation. The high fallback share also shows that structured construction plus screening is still rejecting too much usable content or generating insufficiently usable drafts.

A separately preregistered **ten-case seeded-history check** followed a cross-path family bookkeeping correction. It used new candidate profiles and explicitly exercised prior coverage. It is not a replacement holdout and is not pooled with the original cohort:

| Separate ten-case check | Returned | Pass | Fail | Unavailable |
|---|---:|---:|---:|---:|
| Provider | 5 | 2 | 3 | — |
| Fallback | 2 | 2 | 0 | — |
| Total | 7 | 4 | 3 | 3 |
| Fresher | 4 | 2 | 2 | 1 |
| Experienced | 3 | 2 | 1 | 2 |

No seeded family was reused. Two security cases exhausted reviewed coverage before generation; one SQL draft failed clarity screening with no unused fallback. That is safe unavailability, not a quality success. A max-stack question omitted the operation-cost target/undo semantics. Two OOP questions lost the unavailable-capability qualifier during projection; one became critically contradictory (T=0/C=0). The compiler correction is regression-tested and replayed against four cached specifications, but **the original failures stay counted**.

No source records, reference labels, scores or frozen holdout wording were altered to improve the reported numbers. Post-evaluation operational fixes are identified in `post-evaluation-code-changes.json`; they are not a new measured quality result. No human review was available.

### Semantic-screen calibration

The reviewed 16-case reference set has seven positives and nine negatives, copied from earlier evidence plus explicit alternative/impossibility cases. Original scores were not rewritten. It includes routine questions disguised as Hard, SQL ambiguity, impossible contracts, Fresher-relative Hard, valid alternatives and novelty distinctions. The current exact calibration case is excluded from supplied anchors.

| Screen version | False accepts / negative cases | False rejects / positive cases |
|---|---:|---:|
| Initial | 4/9 | 0/7 |
| Evidence-first reasoning | 5/9 | 1/7 |
| Trusted topic-matched anchors | 4/9 | 1/7 |

The screen now supplies minimum-solution, observable-edge and novelty evidence with strict scores. This made failures inspectable but did **not** establish better calibration. On all 27 screened holdout drafts, agent review found 13 positive/14 negative: **3 false accepts and 8 false rejects**. On eight screened check drafts: two positive/six negative, **3 false accepts and 0 false rejects**. These denominators exclude drafts rejected before semantic screening. Rejected drafts are included in the evidence report; returned-question pass counts are a different measurement.

## Performance, requests and budget

Final policy is at most **one construction and one screen**; no automatic regeneration. A shared **10-second model deadline** covers both calls before safe fallback/unavailability. Retrieval has its existing limits. This deadline was added after the observed timeout and verified with cancellation tests for both stages; its final end-to-end latency has **not** been measured in a paid run. It does not change global grading or HR timeouts.

| Pipeline timing | Median | p95, nearest rank | Maximum |
|---|---:|---:|---:|
| Prior Phase 7 baseline | 5.96 s | 9.94 s | — |
| Original 30-case holdout | 6.195 s | 18.301 s | 61.692 s |
| Separate ten-case check, all outcomes | 5.915 s | 7.351 s | 7.351 s |
| Separate check, seven returned only | 6.014 s | 7.068 s | 7.068 s |

The original holdout has a **tail-latency regression**, including a 60.013-second provider timeout. The smaller seeded-history check has different history lengths/outcome mix and cannot establish a causal improvement. Construction request median/p95 was 2.436/4.274 seconds; screen 2.432/3.973; embedding 0.849/1.199. A single screen took 14.523 seconds during development.

Actual task usage, including calibration and development:

- **240 requests sent:** 180 Azure attempts (74 construction, 106 screen), 60 Gemini query-embedding requests, zero document-embedding requests.
- Azure: 179 responses with **433,015 input and 45,442 output tokens**. One failed timeout has no usage receipt; its full conservative reservation remains charged to the guard. No SDK automatic retry. Early development used 16 additional construction iterations; the final one-attempt policy does not regenerate rejected drafts.
- Gemini: 60 query inputs; token estimate **6,754.5** from characters/4, not provider-reported token usage.
- Public reference estimate **$0.530264** for known usage; **$0.559057** including the failed call's maximum reference allowance. Conservative booked estimate **$1.641889**, below the $2 task budget. Actual Azure/Gemini billing is unavailable.

The guard reserves against $2.50/M input and $10/M output Azure, $1/M Gemini input. Reference arithmetic uses $0.75/M input, $4.50/M output for the named OpenAI model and $0.15/M Gemini embedding input. OpenAI public pricing is a comparison, not a verified Azure deployment invoice: [model pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini), [Gemini embedding pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding). No Azure Speech calls were made. Full failures, per-request usage and reservations are retained in `storage/phase71/api-usage.json` and `execution-summary.json`.

## Data integrity and regression verification

Read-only preflight and final checks confirm **61 knowledge rows**, including 31 unchanged legacy rows and Software Engineer IDs 62–91 (ten Easy, ten Medium, ten Hard). All 30 stored vectors have 768 dimensions and match the expected float32 cached embeddings; source identities/content/metadata match the existing approved state. Scoped ingestion preview is idempotent. Legacy digest:

`0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`

All eleven existing tables' row counts/content digests, schema digests and sequences match the task's preflight snapshot. No live knowledge/user data was written. Eleven frozen prior evidence artifacts retain their hashes. A private fresh database backup was restored into disposable PostgreSQL and verified, including the narrow previously reviewed cast normalization, before regressions. Test network transports blocked external paid HTTP.

- Full backend suite, including actual isolated PostgreSQL vector/knowledge/recovery checks: **363 passed**, zero skipped. Two existing deprecation warnings.
- Focused construction/contracts: **51 passed**, including generation/screen cancellation, projection, role/topic/family exhaustion and private serialization.
- Budget guard tests: **3 passed**.
- Frontend: **49 passed**; TypeScript/Vite production build passed. Existing bundle-size and React Router future warnings remain.
- Real Edge with mocked API at **375 and 1440 px**: keyboard Enter retry, refresh recovery, accessible End action, button bounding boxes and no horizontal overflow. Each flow sent exactly one retry, zero answer submissions and zero speech requests. This is not live microphone verification.
- PostgreSQL recovery checks use a new service/connection after failure and assert the stored evaluation and family history survive. Duplicate submission/retry, authorization, missing grades and session completion are covered. An unrelated existing concurrent deletion test fixture was corrected to give concurrent SQLite clients separate file-backed connections instead of sharing one in-memory connection; application deletion behavior was not changed.

Screenshots: [mobile pending](../storage/phase71/browser/pending-375.png), [mobile recovered](../storage/phase71/browser/recovered-375.png), [desktop pending](../storage/phase71/browser/pending-1440.png), [desktop recovered](../storage/phase71/browser/recovered-1440.png). Browser assertions: `storage/phase71/browser/results.json`.

## Files and remaining work

Focused production work: `backend/app/modules/interview/{problem_spec,problem_construction,question_families,generation_errors,question_quality,hard_fallbacks,question_generator,question_bank,schemas,nodes,service,router}.py`, `quality_reference.json`; frontend `useInterview.ts`, `InterviewRoom.tsx`, `interview.service.ts`, `types/interview.ts`.

Tests: `backend/tests/problem_examples.py`, `unit/test_problem_contracts.py`, `unit/test_phase7_questions.py`, `unit/test_question_calibration.py`, `integration/test_question_recovery.py`, the concurrent-deletion fixture, and `frontend/tests/interviewSubmission.test.tsx`. Operators: `scripts/evaluate_phase71.py`, additive per-task guard support in `scripts/phase7_meter.py`, local verification/evidence helpers under `storage/phase71/`. The much larger existing Phase 6/7 dirty working tree was preserved; it is not all Phase 7.1 work.

Priority recommendations:

1. Strengthen executable contract evidence: SQL result grain/cardinality, explicit time anchors and small expected-output fixtures; OOP publication/cancellation/unknown-outcome boundaries; deduplication's observable processing effect and atomic boundary. Merely requiring prose fields is insufficient.
2. Have technical reviewers adjudicate screen disagreements and calibrate on a separate development set. Preserve the current holdout unchanged. Do not ship a screen that rejects eight of thirteen agent-positive holdout drafts or use it as the quality oracle.
3. Expand genuinely different reviewed Hard families where measured exhaustion occurs, with concrete Git failure behavior and explicit complexity/undo semantics. Retain explicit unavailability when coverage is exhausted.
4. Run a new preregistered unseen cohort after substantive fixes, including full session-length history and cancellation/latency checks. Do not report cached projection replay as new quality performance.

Functional correctness and safe recovery improved. **The 80% quality/no-critical-failure release gate remains unproven and failed in the measured evidence.** No production deployment, Git commit, push or merge was performed.
