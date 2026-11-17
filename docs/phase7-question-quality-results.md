# Phase 7: implementation and actual-question evaluation

Review date: 16 November 2026 (Asia/Calcutta). **Recommendation: HOLD on declaring Hard-mode question quality ready.** Implementation, database validation and regression testing were performed, but the desired question-quality reliability has not been achieved. This is an agent technical assessment, without independent human adjudication. No Git commit, push, merge or production deployment was performed.

The complete question texts, seven-axis assessments, individual failures, provider/fallback identity, and source IDs are in [the question appendix](phase7-question-results.md). All outputs and rejected drafts are retained; the tables below do not select only successful samples.

## What changed

- Added one shared experience/difficulty contract. Requested/planned difficulty stays Hard during normal generation. Entry-level Hard retrieves role/topic-scoped **Medium factual knowledge**, then asks for integrated fundamentals. Experienced Hard retains Hard factual knowledge. Aliases normalize consistently; unknown roles still abstain. Existing difficulty distributions, adaptive transitions, mock planning and HR grading were not rewritten.
- Added topic-specific reasoning requirements: interacting data-structure operations; boundary-aware algorithms; observable OOP invariants; precise SQL output semantics; atomic HTTP enforcement; pagination/update contracts; commit dependencies; deterministic test oracles; discriminating debugging experiments; authorization transitions.
- Replaced the 420-character Hard ceiling with a **900-character bound**, with a 60–110 spoken-word prompt target. Easy/Medium retain 420. Single-primary-task, deduplication and grounding checks remain. The generator keeps the selected topic instead of accepting a model-supplied replacement topic.
- Added one bounded semantic screen per Hard draft, with independent technical-soundness, reasoning-depth, clarity, realism, experience and session-novelty booleans. Maximum **two drafts and two screens**, no recursive quality retry. Failures/reasons are logged. Easy/Medium and HR do not acquire this extra call. This screen assesses questions, never candidate scores.
- Fixed a measured screen defect: familiarity is not repetition. Empty history is deterministically novel; the prompt compares only actual previous tasks and distinguishes designing retry handling from testing it. This improves policy correctness, but semantic screening still has false accepts/rejects.
- Added twenty reviewed outage scenarios across ten topics and two experience profiles. Removed the easy-to-hard relabel path and assumed-work wording. Real project references now require actual project evidence, rather than a skill name alone. **The finite pack can exhaust: four measured replacement runs returned Medium, and one changed topic. This remains a blocker for claiming mock difficulty/topic continuity during repeated provider rejection.** It is not hidden as a successful Hard answer.
- Follow-up difficulty step-down and grading prompts/weights remain unchanged. Primary Hard-definition rejection is not imposed on a clarification follow-up.

## Experience contract

| Configuration | Retrieved facts | Required reasoning |
| --- | --- | --- |
| Internship/Fresher Easy or Medium | Requested tier | Focused practical fundamentals, calibrated to profile |
| Internship/Fresher Hard | Medium, same role/topic | A small implementation/query/debugging task combining fundamentals, interacting boundaries and a nontrivial edge; no assumed senior production ownership |
| Intermediate Hard | Hard, same role/topic | Bounded component decisions and implementation; avoid assuming senior ownership |
| Experienced Hard | Hard, same role/topic | Consequential decisions under workload, concurrency/recovery, performance or failure constraints; an implementation-level explanation |
| Retrieval without an experience argument | Existing requested-tier behavior | Compatibility for callers without profile calibration |

A correct unfamiliar solution is welcome. There is no required algorithm/language keyword or candidate-answer score in this policy. A long scenario does not establish Hard depth.

## Knowledge revisions and local database changes

Eight existing sources advanced **revision 2 to 3**: Algorithms, OOP, SQL, HTTP, REST, Debugging, Testing and Security. Data Structures and Git remain revision 2. Their Hard material now includes workload/merge costs, capability boundaries and uncertain outcomes, multi-item transaction/outbox boundaries, durable request claiming, retained snapshot requirements, evidence-led pool diagnostics, deterministic crash/redelivery testing and bounded authorization revocation. Provenance distinguishes original engineering synthesis from primary-document support; no linked source is claimed to prove an entire design.

Because source metadata/provenance is shared by all three difficulty sections, the read-only role-only preview proposed **24 updates, six unchanged, zero inserts, zero retirements and zero deletions**. This scope was rehearsed before local application. Twenty-four new document embeddings were prepared; six exact-text vectors were reused. The source manifest and vector cache were frozen separately from Phase 6B artifacts.

The fresh private backup was restored into a disposable PostgreSQL/pgvector container. Contents, constraints, sequences and indexes were compared, permitting only the previously documented equivalent cast form. Both a deterministic-vector rehearsal and an actual-cache-vector commit/re-read rehearsal passed. The local apply then rechecked the manifest, source/cache identities, exact plan and preflight database state under advisory lock 634220061; all updates committed in one transaction. All non-knowledge data was compared before commit and independently afterward.

| Check | Actual result |
| --- | --- |
| Total knowledge records | 61 |
| Legacy preserved | 31; original digest `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b` |
| Software Engineer records | 30; IDs 62–91 preserved |
| Difficulty distribution | 10 Easy, 10 Medium, 10 Hard |
| Stored vectors | All 30 match expected float32 storage bytes; 768 dimensions |
| Scope | 24 existing-row updates, zero new/deleted/retired rows |
| User data / schema | All other table digests and schema unchanged; all sequences unchanged; 11 tables checked |
| Repeated role-only preview | Zero changes and zero embedding inputs |
| Cached role/difficulty retrieval | Hit@1 29/30, Hit@3 30/30, MRR 0.9833; no new API calls |

Updated IDs: `62, 63, 64, 68, 69, 70, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91`.

- Backup SHA-256: `23b84b2d14f9797e86ff240953252fbfa39836b9387ab3fd7398393ea20b0909`.
- Revised source manifest SHA-256: `f92c1a6ea0786b598da6595d93bc28697e105b97c5068df7c30e392bbabec277`.
- Revised vector cache SHA-256: `fb5ab58ca7db998f1d1aa95c9f8e2dd14a4f11e55a47b7fb8ee8b31b483a5a99`.
- Applied plan identifier: `1399c9cde2023ea980a302e07a62f2da93fc054cb0d4b0d3320c5a7aa6e5662e`.
- Frozen original rubric SHA-256: `917e421c4f41f72a6113f0035e2d271a2362c45152d09f7627fbf584a36731e0`.

The original Phase 6B manifest, vector cache, semantic dataset and audit rubric hashes remain unchanged. The historical no-Hard-intern retrieval label is preserved as history; the regression test explicitly documents the new Medium-context policy instead of relabelling the frozen dataset.

## Measurement design and results

Actual `InterviewNodes.retrieve_knowledge` and `InterviewNodes.generate_question` ran with PostgreSQL RAG and the configured provider in read-only transactions. No permanent test user/interview/report records were created. Candidate skills were supplied, projects were empty, and scenarios were hypothetical. Every completed case retrieved one correctly scoped source: Medium for Freshers, Hard for Experienced candidates.

The first matrix was frozen before calls: 20 development/regression configurations and 10 unseen profile/type combinations, plus three replacements to obtain 30 confirmed provider-generated finals. Its 33 returned outputs and all drafts remain intact.

The subsequent correction used only development E/F evidence. A fresh 20-case mixed-type set was registered and production hashes frozen before any refined output; no prompt/source changes were made from refined results. Eight completed replacements are reported too, including repeated-topic exhaustion cases. Two later replacements used fresh sessions to separate exhaustion from ordinary fresh generation. The original 20-case result is always reported separately, so replacements cannot improve its denominator.

Scores use the **original frozen seven-axis rubric**: R relevance, T technical correctness, L interview likelihood, H experience-relative Hard depth, E experience appropriateness, C clarity, F follow-up potential, each 0–2. PASS requires R=T=H=E=C=2, L>=1 and F>=1, without a same-session near-duplicate. There is no weighted average hiding a critical failure. Fresher passes do not imply experienced absolute Hard depth.

| Cohort | Agent PASS | Agent FAIL | Provider finals / fallbacks |
| --- | ---: | ---: | --- |
| Original frozen Phase 6B baseline | 7/15 | 8/15 | 15 / 0 |
| Phase 7 first registered matrix | 16/30 | 14/30 | 27 / 3 |
| First run including replacements | 17/33 | 16/33 | 30 / 3 |
| Refined registered matrix | 10/20 | 10/20 | 16 / 4 |
| Refined run including replacements | 13/28 | 15/28 | 18 / 10 |
| All completed Phase 7 outputs | 30/61 | 31/61 | 48 / 13 |

Provider-generated finals alone passed **14/30** in the first run and **8/18** in the refined run. On the 15 configuration families matching the old baseline, both Phase 7 runs scored **9/15**, versus 7/15 before; these are fresh, unpaired generations, include fallback outcomes, and are not evidence of a statistically reliable improvement. The refined primary Experienced group scored 7/10 and Fresher group 3/10, including fallbacks.

The local conservative budget guard ended the refined expansion at 18 confirmed provider finals, short of its additional 20-final target. Across the task, the requested minimum of 30 fresh provider finals was exceeded: **48 confirmed provider finals**, 61 completed outputs, and **87 actual generation drafts**. One further case completed retrieval, one draft and one rejection screen; the guard blocked its second draft before transport. That partial case is also preserved. There were no transport failures or automatic SDK retries. Twenty-five regeneration requests were sent after rejected drafts; these are quality retries, not network retries.

**There is no demonstrated broad Hard-mode quality improvement.** Retrieval remains strong; generator calibration, contract clarity and fallback exhaustion are still limiting. The semantic screen's success flag is not used as the measured pass rate. No independent human approval or beta-readiness claim is made.

## Before and after examples (actual provider text)

**Debugging: a concrete improvement**

Before: A production API started showing a 5x latency spike after a deployment, but the issue is intermittent and you can’t reproduce it reliably in staging. How would you debug it without taking the service down, and what would you look at first to narrow the scope before choosing a mitigation?

After: After a deployment, p99 latency for one REST endpoint triples, but median latency, CPU, and database query time stay flat. Traces show most of the extra time is waiting to acquire a DB connection, and the pool stays at its limit even after requests complete. You can’t pause production, and raising the pool size is allowed only as a temporary mitigation. What is the single best bounded investigation you’d run to distinguish a leaked connection from a legitimate long-held transaction, and what result would you expect for each hypothesis?

Assessment: Explicit competing hypotheses and expected outcomes make this a falsifiable production experiment rather than a checklist.

**OOP: a stronger fresher failure boundary**

Before: Suppose you’re designing a simple online shopping cart in Java or Python with a base Product type and a few specific product types like Book and Electronics. If the checkout logic needs to apply different pricing or discount rules based on the actual product type, how would you structure the classes so the code stays easy to extend without adding a lot of if-else checks?

After: Suppose a file-storage app has a `Storage` interface with `save(file)` and `delete(fileId)`. The app also guarantees this caller-visible rule: if `save()` fails halfway, no partial file should be visible to later `get()` calls. You need to add a new `EncryptedStorage` implementation without changing the code that orchestrates uploads and deletes. How would you structure the objects so that encryption can be swapped in while preserving that no-partial-file invariant, especially if `save()` can fail after writing the first chunk?

Assessment: A swappable encrypted writer must preserve no-partial-read visibility after a chunk failure; staged write/publication/cleanup is a concrete OOP boundary with a meaningful failure case.

**Algorithms: still shallow for experienced Hard**

Before: You need to support frequent inserts and range queries on a large set of numeric keys. Would you choose a sorted array or a balanced binary search tree, and why? Please state the assumptions you need for correctness and the worst-case time cost of insert and range query in each structure.

After: Imagine a collaboration app keeps an in-memory list of shared edits ordered by (edit_time, edit_id). New edits arrive in minute-long bursts, and acknowledged edits must be searchable immediately for range views like “all edits in this document between 10:00 and 10:05.” Memory is capped, and reads are frequent during bursts. If you had to choose one primary indexing approach to support fast range scans and inserts under this workload, what would you use, and how would you handle the case where a late edit lands with the same timestamp as an existing one but must still appear in a stable order?

Assessment: Burst inserts and a composite tie key improve realism, but there is no consequential workload/latency choice or recovery condition; a balanced-tree recommendation plus (time,id) ordering largely answers it. Still shallow for experienced Hard.

## Root causes that remain, and implementation priority

1. **Entry-level context still anchors easy templates.** Mapping entry Hard to Medium restores safe factual RAG, but Medium binary-search/OOP/SQL examples repeatedly dominate the actual task. The current Hard context projection primarily recognizes a Hard section. Next, separate factual grounding from profile-calibrated reasoning examples within the existing versioned records, and explicitly project the selected profile's examples. Do not simply expose senior recovery examples to freshers or add more undifferentiated rows.
2. **The semantic gate is not a calibrated quality oracle.** It rejected appropriate failure-testing approaches as routine while accepting shallow polymorphism, unobservable SQL tie rules and a revoked-viewer write test that cannot prove revocation. Empty-history novelty is fixed; some broader over-rejection remains. Calibrate against a human-adjudicated fixture set of positive, negative and valid-alternative examples using the same rubric. Do not strengthen generic adjectives or reward more jargon.
3. **Correctness contracts need construction-time validation.** Specify selected columns, timestamp scope, eligibility of missing status rows, authorization transitions and conflict outcomes before phrasing. The SQL tie-break must affect an observable result; a viewer that could never write cannot prove write revocation. A structured internal problem scaffold could validate these facts before the bounded screen, without changing candidate grading.
4. **Finite fallback coverage is insufficient.** Four exhausted runs returned Medium and one selected a different topic. This is more honest than falsely labelling them Hard, but violates the desired fixed-tier/topic continuity. Add sufficiently varied, reviewed same-topic/profile scenarios and an explicit non-destructive exhaustion behavior; exercise long histories and display-topic aliases in mock/recovery tests. Avoid silently scoring an easier task as Hard.
5. **Independent review and controlled sampling are needed.** Review the full failure appendix, especially Algorithms/OOP/SQL, not just a favorable debugging example. Keep the frozen rubric and held-out outputs. The next iteration should prioritize fewer well-specified problem families and measured false-accept/false-reject rates before increasing retry counts.

## Regression verification

| Verification | Result |
| --- | --- |
| Complete backend suite, disposable restored PostgreSQL | **329 passed, zero skipped**; two existing deprecation warnings |
| PostgreSQL flags | `PREPMATE_VECTOR_POSTGRES=1`, `PREPMATE_KNOWLEDGE_POSTGRES=1` |
| Focused calibration/context/Phase 7 tests | **33 passed** |
| New budget-meter tests | **3 passed** |
| Frontend suite | **47 passed**, six test files |
| TypeScript + Vite production build | **PASS**; existing >500 kB bundle-size warning |
| Backup restore and scoped update rehearsals | **PASS**, disposable containers removed |
| Final live local DB integrity and read-only retrieval | **PASS**, original user data unchanged |
| Whitespace and audit-script compilation | **PASS** |

There are 23 added backend test cases relative to the 306-test baseline: contract normalization, both retrieval paths through their shared filter, actual PostgreSQL entry-Hard retrieval for ten topics/profiles, scoped stable-ID updates with legacy/other-role preservation, Hard length boundaries, definition rejection, project evidence, semantic retry bounds, unavailable/malformed-review behavior, empty-history novelty, and honest fallback difficulty. Existing grading/rubric, adaptive/mock, HR, persistence/report and frontend Voice tests remain in the full suites. These suites do not establish the quality of arbitrary generated questions or live microphone behavior.

The relevant executable operator commands used were:

```powershell
# Isolated backup restore, full backend tests and scoped rehearsal:
$env:PYTHONPATH='backend;storage/phase6b'
.venv/Scripts/python.exe storage/phase7/run_isolated.py
# Prepare only missing revised document vectors, metered; no DB writes:
.venv/Scripts/python.exe scripts/phase7_prepare.py
# Cached-vector local-only apply (already executed; receipt prevents reapply):
.venv/Scripts/python.exe scripts/apply_phase7_local.py --apply-local
# Read-only repeat verification:
.venv/Scripts/python.exe scripts/apply_phase7_local.py
# Actual question audit, persistent budget ledger:
.venv/Scripts/python.exe scripts/audit_phase7_questions.py
$env:PREPMATE_PHASE7_AUDIT_SUFFIX='-refined'
.venv/Scripts/python.exe scripts/audit_phase7_questions.py
# Frontend (frontend directory):
npm test
npm run build
```

Do not rerun the paid audit within this task: its persistent conservative guard is nearly exhausted. The receipt, backup and source hashes—not a broader folder/full-corpus plan—define the actual local update.

## API usage, billing limits and performance

| Provider / model | Actual requests | Usage |
| --- | ---: | --- |
| Azure OpenAI / gpt-5.4-mini | 174 | 87 generation + 87 semantic screens; 267,465 input, 22,404 output tokens |
| Gemini / gemini-embedding-001, 768 dimensions | 63 | 24 document inputs in one request, 62 one-query requests; 25,108.5 estimated tokens by characters/4 |
| All sent requests | 237 | All succeeded at transport; zero in flight, zero automatic network retries |

Estimated public-reference cost: **USD $0.305183**. Conservative ledger charge: **USD $1.888659**, below $2; a new worst-case reservation was refused. This is not an invoice. Actual Azure account/deployment pricing and billed charges were unavailable. Gemini embedding responses supplied no exact token usage; estimates are labelled rather than represented as measured tokens.

Reference rates were checked against [OpenAI's model pricing](https://developers.openai.com/api/docs/models/gpt-5.4-mini) ($0.75/M input, $4.50/M output) and [Gemini embedding pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) ($0.15/M input) on 16 November. These are public reference rates, not verified Azure account rates. The guard reserved at $5/M Azure input, $20/M Azure output and $1/M Gemini input, using UTF-8 byte input bounds and the actual 4000-token maximum output setting before each call. Successful Azure responses replaced reservations with observed-token conservative charges; failures would retain the full reservation. Input limits for the revised English documents were screened by size (maximum 3,865 characters, approximately 966 tokens by characters/4), not a falsely claimed exact Gemini token count.

| Measured operation | Median | p95 | Maximum |
| --- | ---: | ---: | ---: |
| One generation request | 1.660s | 2.410s | 3.807s |
| One semantic screen | 1.923s | 2.640s | 3.367s |
| One embedding request | 1.036s | 1.312s | 2.659s |
| Completed RAG + generation/screen/fallback path | 5.957s | 9.938s | 11.656s |

These are direct wall-clock observations from local development calls, not production latency guarantees. The extra screen materially increases latency. No Azure Speech requests, paid interview-session creation, candidate answer grading, production traffic or human microphone verification were performed.

## Files and preserved evidence

Only the following existing files were additionally edited or new files created for Phase 7; other pre-existing uncommitted Phase 6 work was preserved:

- `backend/app/modules/interview/difficulty_contract.py`
- `backend/app/modules/interview/question_quality.py`
- `backend/app/modules/interview/hard_fallbacks.py`
- `backend/app/modules/interview/question_generator.py`
- `backend/app/modules/interview/question_bank.py`
- `backend/app/modules/interview/prompts.py`
- `backend/app/modules/knowledge/retriever.py`
- `backend/tests/unit/test_phase7_questions.py`
- `backend/tests/unit/test_question_calibration.py`
- `backend/tests/integration/test_phase6_knowledge.py`
- `scripts/phase7_meter.py`
- `scripts/phase7_prepare.py`
- `scripts/apply_phase7_local.py`
- `scripts/audit_phase7_questions.py`
- `scripts/tests/test_phase7_meter.py`
- `knowledge_base/software_engineering/algorithms.md`
- `knowledge_base/software_engineering/oop.md`
- `knowledge_base/software_engineering/sql.md`
- `knowledge_base/software_engineering/http.md`
- `knowledge_base/software_engineering/rest.md`
- `knowledge_base/software_engineering/debugging.md`
- `knowledge_base/software_engineering/testing.md`
- `knowledge_base/software_engineering/security.md`
- `docs/phase7-question-quality-results.md` (this report)
- `docs/phase7-question-results.md` (every returned question and individual assessment)

Local ignored evidence under `storage/phase7/`:

- `before-phase7.dump`, `preflight.json`, `isolated-rehearsal.json`, `backend-tests.xml`.
- `source-manifest.json`, `preview.json`, `vectors.json`, `vector-preparation.json`, `local-update-receipt.json`.
- `criteria.json`, `criteria-refined.json`, `generation-input-hashes*.json`.
- `questions.json`, `questions-refined.json`, `quality-review*.json`, `draft-inventory.json`, `partial-case.json`.
- Every `request-NNN.json` / `response-NNN.json`, `api-usage.json`, `usage-summary.json`, execution summaries.
- `post-update-verification.json`, `post-audit-database-state.json`, `final-integrity.json`, `artifact-inventory.json`.

The backup is private local evidence and is not intended for Git. Raw prompts contain only synthetic candidate context; credentials and endpoints were not written into the ledger. API vectors and logs remain available locally. There are no frontend UI changes/screenshots in this phase, and no claim of live Voice verification.
