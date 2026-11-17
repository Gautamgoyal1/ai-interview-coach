# Practical interview difficulty — implementation and verification

Completed 2026-11-17. Difficulty now prioritizes questions a human technical interviewer would plausibly ask. Familiar coding problems, ordinary SQL, OOP comparisons, debugging and standard techniques are valid. Hard no longer requires several constraints, multiple failures, concurrency or architecture.

The Phase 7.2 hybrid path, RAG, adaptive progression, answer grading and saved-answer recovery remain in place. There are no new dependencies, screening chains, database migrations or persisted state fields.

## What changed

| Difficulty | Generation guidance |
|---|---|
| Easy | Mostly direct fundamentals, roughly 80% direct / 20% simple applied; short and beginner-friendly |
| Medium | Roughly 50% direct explanations/comparisons / 50% everyday implementation or scenarios |
| Hard | Roughly 20% challenging direct questions / 80% realistic applied problems; concise and familiar is acceptable |

These are flexible targets, not rejection quotas. A small deterministic style guide rotates using the existing session ID, so a late adaptive Hard question does not always land on the same style. Refresh/restart does not reroll the style. Topic/focus selection and the adaptive difficulty update are unchanged; only the technical question's direct/applied preference is selected after difficulty is known. HR selection is unchanged.

Fresher guidance uses basic-to-intermediate programming and applied fundamentals, without invented production ownership. Experienced guidance favors independent implementation reasoning, optimization and relevant trade-offs, without automatically asking for distributed systems.

Direct Hard questions now reuse the existing lightweight question payload, just like Easy/Medium. They do not need an internal elaborate problem specification. Applied Hard questions retain the hybrid family/compiler path and existing correctness checks. Ordinary debugging openings reuse the simple input/output/boundary contract rather than requiring two predefined hypotheses; the specialized two-hypothesis validator still rejects invalid comparisons when that richer contract is used.

Several family openings were simplified: maximum-stack operations without mandatory undo; deduplication without a mandatory durable event-processing system; ordinary staged exports and plugin cleanup; practical cache-refresh/integration tests; common Git compatibility recovery; simpler retry assumptions, authorization and live pagination. Optional extensions are encouraged in the private follow-up direction rather than added by default to the opening.

Hard RAG context now keeps facts, principles, misconceptions, limitations and provenance instead of copying the older elaborate worked Hard examples. Retrieval filters, embedding configuration, knowledge records and vectors are unchanged.

The quality screen now checks interview relevance, technical correctness, clarity, practical challenge, experience fit and actual session repetition. It explicitly accepts familiar problems and standard techniques. A definition/comparison is no longer structurally rejected just for its phrasing. Real SQL-reference/output errors, impossible guarantees, invalid revocation tests and contradictory contracts are still rejected. An empty optional diagnostic no longer forces a valid question into fallback; blocking decisions and their quoted evidence remain validated.

Easy and Medium gained no screening call. Hard keeps one generation plus one existing review under its shared model deadline; no repair chain was added. Changed-topic provider metadata is rejected. Fallback exhaustion at every tier now returns explicit unavailability instead of switching topics or difficulty. Existing session recovery preserves saved answers/evaluations on that path.

Follow-up guidance probes one detail from a strong answer and gives a simpler clarification for a weak answer. It does not automatically escalate to architecture. Candidate grading prompts, weights, difficulty plans and historical results are unchanged.

## Real-pipeline evaluation

Used Azure OpenAI **gpt-5.4-mini** and Gemini **gemini-embedding-001**, with actual role/difficulty-scoped PostgreSQL retrieval. Runs used synthetic profiles and generation histories, not permanent user interview sessions. No paid grading or Azure Speech calls were made.

The first run covered 60 questions: ten topics at each difficulty for both Fresher and Experienced. It exposed a diagnostic parser defect: most suitable Hard reviews used a short/empty `minimum_reasoning` value, which the older parser rejected. Those outputs are retained. After correcting the parser and simplifying ordinary debugging, a separate fresh 20-question Hard run verified the new behavior.

| Run | Provider output | Fixed fallback | Unavailable |
|---|---:|---:|---:|
| First Easy: 20 | 20 | 0 | 0 |
| First Medium: 20 | 20 | 0 | 0 |
| First Hard: 20, before diagnostic fix | 2 | 18 | 0 |
| Separate final Hard confirmation: 20 | 17 | 3 | 0 |

The runs are not pooled into a new “quality success percentage.” Reviews use the revised practical standard, so they are also not a numerical comparison against the frozen Phase 7.2 rubric. All judgments are provisional agent review; independent human review was unavailable.

The first Easy outputs carried 16 direct / 4 applied tags; Medium 10 / 10. Final Hard carried 4 / 16. Tags and wording are not identical classifications: some conceptual requests are phrased as small scenarios. These targets remain guidance rather than enforcement. The final session-ID rotation was tested offline across fixed late interview positions and in the full suite; these generation runs used their declared style schedule.

Representative actual questions:

- **Easy:** “How does a LEFT JOIN differ from an INNER JOIN?”
- **Medium:** “What is the difference between putting a condition in the ON clause of a LEFT JOIN versus putting the same condition in the WHERE clause?”
- **Hard direct:** “Given a sorted array of integers that may contain duplicates, how would you use binary search to find the first index of a target value? Please explain the invariant you would maintain, how you handle the boundary cases, and the time complexity.”
- **Hard applied:** a plugin writes through temporary files; only completed output is published, and a failed step must clean its files while leaving the previous result readable. The ask is how to design that plugin boundary, without a distributed cleanup protocol.

Common techniques were assessed as legitimate answers, not rejected for familiarity. Some Experienced examples sit at the lower end of Hard and can be adapted through follow-up. A few SQL/HTTP kernels remain longer than ordinary conversational openings.

Specific remaining observations are preserved in the [complete question evidence](practical-interview-questions.md): one Medium Git question needs its buggy change identified more clearly; an initial legacy durable-dedup fallback leaves the processing effect underspecified; one generated Git phrase is awkward. The observed fixed Git fallback also needed B's intended behavior explicitly preserved. That bank sentence was clarified afterward, with offline bounds/history-detection checks and full regression; the original recorded question was not replaced or counted as a new paid success.

The final Hard screen still withheld three drafts: one invalid quoted review, one arguably overelaborate fresher pagination task, and one false ambiguity objection to an explicitly defined SQL NULL-sum rule. Screening is still imperfect; the simpler policy is not claimed to be a reliable oracle.

## Follow-ups and negative checks

Four real-provider follow-ups used declared synthetic candidate answers and feedback fixtures, not real grading:

- Strong SQL answer → a small example demonstrating ON versus WHERE behavior.
- Weak binary-search answer → a two-element trace checking progress.
- Strong retry answer → handling the same key with a different body.
- Weak debugging answer → request-ID evidence for shared state.

All four returned provider text. Strong Medium answers stayed Medium; weak answers received Easy clarification. Full wording and synthetic-fixture disclosure are in the evidence report.

Six authored screen probes were also attempted. Familiar coding, ordinary SQL and a practical OOP comparison were accepted. Actual repetition was rejected. The undefined-column probe timed out and was not retried; the impossible-OOP probe produced an invalid quoted review and therefore no usable verdict. These two are **not verified**, not counted as successful negative judgments. Deterministic SQL/OOP correctness regressions remain passing.

## Regression and integrity

- **446 backend tests passed**, zero skipped, in a verified disposable PostgreSQL restore with external paid HTTP blocked. This includes persistence/restart/retry, adaptive/HR/grading and technical-contract regressions. Two existing deprecation warnings remain.
- **49 frontend tests passed**; TypeScript/Vite production build passed. Existing Router and bundle-size warnings remain.
- Focused tests cover practical style targets, fixed late-position variation across sessions, lightweight direct Hard questions, ordinary debugging, topic continuity/exhaustion, technical-error rejection, bounded Hard review and answer-aware follow-ups.
- Final read-only database checks verified **61 chunks**, all **31 legacy rows unchanged**, all 30 Software Engineer records/vectors intact, and idempotent scoped ingestion preview. All eleven existing tables, schema digests and sequences match preflight. Zero knowledge/user-data writes.
- **951 prior evidence files** retain their hashes. Answer-grading prompts and difficulty-plan code were independently checked unchanged; RAG, graph routing, service recovery, reports, HR and Azure Voice production modules were preserved.

No live browser/microphone acceptance is claimed. The paid checks exercised retrieval/generation and follow-ups, not a full paid adaptive interview with real candidate grading. Final offline changes—the Git fallback clarification and session-based style rotation—are explicitly recorded separately from paid outputs.

## Usage and latency

Total: **210 API requests**. Azure OpenAI: 84 generation calls (80 primary plus four follow-ups), 46 screen attempts, with **168,798 input / 8,027 output tokens** available from successful responses. Gemini: 80 query embeddings, zero document embeddings; estimated 10,017.5 query tokens from characters/4.

Conservative booked estimate: **$0.592676**, below the $2 task target. Known public-price reference estimate: **$0.164223**; including the failed request at its maximum reference allowance: **$0.184551**. Actual billing is unavailable. The failed request retains its full conservative reservation. No SDK automatic retry or failed-probe retry was performed.

First-run primary latency: 2.98s median / 4.71s p95. Final Hard: **4.87s median / 7.23s p95**, maximum 17.16s; that maximum included an 11.44s query embedding. p95 uses nearest rank. The ten-second Hard model budget excludes retrieval and is not an end-to-end SLA.

One standalone undefined-SQL screen probe recorded **593.15s elapsed** before a timeout, despite the configured provider timeout being 60s. The cause of that discrepancy was not established. It was outside the interview's shared Hard deadline, was not retried, and is retained as failed evidence. This is not hidden inside the primary-generation latency distribution.

Reference arithmetic uses the previously checked public model rates, with higher conservative guard rates; it is not an Azure invoice. Raw receipts and unknown-usage reservations are in `storage/practical-interviews/api-usage.json`.

## Files

Generation policy and prompts: `difficulty_contract.py`, `calibration.py` (generation guidance only), `prompts.py`, `question_quality.py`.

Existing flow/compiler/fallback integration: `nodes.py` (style choice only), `question_generator.py`, `problem_construction.py`, `problem_families.py`, `problem_spec.py`, `question_bank.py`, `hard_fallbacks.py`, all under `backend/app/modules/interview/`.

Tests: new `backend/tests/unit/test_practical_difficulty.py`; updated question-context, calibration and Phase 7 generation tests. Operator: `scripts/evaluate_practical_interviews.py`; local metering, backup, restore and evidence helpers under `storage/practical-interviews/`.

The existing uncommitted work was preserved. No commit, push, merge or deployment was performed.
