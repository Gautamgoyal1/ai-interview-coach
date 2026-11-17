# PrepMate: post-rollout verification and Hard-mode question quality audit

Date: 15 November 2026. **Rollout integrity: PASS. Hard-question quality: inconsistent.** All **15 actual final questions** below came from the configured AI provider through PrepMate's production retrieval and generation nodes. Under the criteria frozen before generation, **7 passed and 8 failed**. The experienced subset was **5 pass / 5 fail**; the fresher subset was **2 pass / 3 fail** against experience-relative Hard standards. These are single-reviewer judgments on this sample, not general success probabilities.

No baseline question, quality threshold, knowledge source, production prompt or application code was changed during this audit. No historical evaluation, user record, schema or knowledge vector was rewritten. No deployment, commit or push occurred. The purpose was to establish a candid baseline and prioritize fixes, not tune until the sample looked successful.

## 1. Verified database state

All verification ran in explicit read-only PostgreSQL transactions before paid generation. Verification was repeated after a transient embedding failure and the entire database state was checked again at completion.

| Requirement | Actual result |
| --- | --- |
| `public.chunks` total | **61** |
| Legacy records | **31 unchanged**, metadata/content/vector digest matched |
| Receipt match | **30/30**, IDs **62?91**, exact ID/name/hash/role pairs |
| New difficulty distribution | **10 Easy, 10 Medium, 10 Hard** |
| Stored dimensions | **768** for all 61 vectors |
| New-vector validity | **30/30** finite, correct dimensions and exact float32 storage-bit match with cached embeddings |
| New metadata/content comparison | **30/30** match the reviewed source manifest |
| Representative role/topic/difficulty retrieval | **30/30** positive cases and **2/2** explicit abstentions passed |
| Repeated Software Engineer-only preview | **0 changes, 0 pending embeddings, 30 unchanged sources** |
| Database state after the audit | **Identical** table data digests, schema metadata and sequences to this task's starting snapshot |

Legacy digest: `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b`.

[Verification evidence](../storage/phase6b/hard-mode-quality-audit/database-verification.json) ? [Idempotent preview](../storage/phase6b/hard-mode-quality-audit/idempotent-preview.json). No data repair was needed or performed. Existing content embeddings were not regenerated.

## 2. Audit protocol and frozen quality standard

The preregistered matrix contained ten experienced cases covering every Software Engineer topic and five fresher cases covering Algorithms, OOP, SQL, HTTP and Security. All requested and returned difficulty fields were `hard`.

Each case called **`InterviewNodes.retrieve_knowledge` then `InterviewNodes.generate_question`**, with actual database context and the configured provider. Candidate profiles were synthetic skill lists without fabricated employment or project claims. Question histories and fingerprints were retained in memory separately for each experience profile, so the existing within-session deduplication and generation validator were active. There were no permanent interview sessions, checkpoints, candidate answers or grading calls.

Topic and Hard difficulty were selected by the audit matrix to ensure coverage. The adaptive topic/difficulty selector was not exercised, so this audit cannot establish how often a full interview would select these cases. These are real question-node tests, not a browser session or complete adaptive interview.

The criteria file was saved before generation, SHA-256 `917e421c4f41f72a6113f0035e2d271a2362c45152d09f7627fbf584a36731e0`. Seven axes use **0 = deficient, 1 = partial/routine, 2 = meets the stated bar**:

| Axis | Meaning at score 2 |
| --- | --- |
| R | Directly relevant to Software Engineer interviews |
| T | Technically sound premises and contracts |
| L | Plausible, bounded real interview question |
| H | Actual reasoning depth relative to the configured experience |
| E | Challenging but appropriate assumptions/background for that profile |
| C | One focused, answerable task with enough stated assumptions |
| F | A concrete follow-up can deepen reasoning without first repairing the question |

A **PASS** requires **R=T=H=E=C=2**, **L?1**, **F?1**, and no near-duplicate of an earlier question in the same profile run. A high average cannot hide a depth or clarity failure.

For **experienced Hard**, a defensible decision must involve interacting constraints, failure/edge reasoning or meaningful trade-offs; a standard definition, obvious contract violation or routine checklist is insufficient. For **fresher Hard**, integrated fundamentals with a nontrivial application/edge case can pass without senior distributed-systems assumptions. Absolute experienced-Hard depth is recorded separately for every question. The fresh-profile passes do not imply senior-level challenge.

The review assesses question premises and answerability, not the correctness of generated reference answers or interview grading; neither was generated. Technical ambiguity is recorded under clarity unless the question actually asserts a false premise. Reviewer-authored follow-ups below are suggestions, not claimed as AI-generated or executed follow-ups.

## 3. Scores and observed counts

| ID | Profile | Topic | R | T | L | H | E | C | F | Outcome |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| E01 | experienced | Data Structures | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| E02 | experienced | Algorithms | 2 | 2 | 2 | 1 | 1 | 2 | 2 | FAIL |
| E03 | experienced | Object-Oriented Programming | 2 | 2 | 2 | 1 | 1 | 2 | 2 | FAIL |
| E04 | experienced | SQL | 2 | 2 | 2 | 1 | 1 | 2 | 2 | FAIL |
| E05 | experienced | HTTP | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| E06 | experienced | REST APIs | 2 | 2 | 1 | 2 | 2 | 1 | 1 | FAIL |
| E07 | experienced | Git | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| E08 | experienced | Testing | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| E09 | experienced | Debugging | 2 | 2 | 2 | 1 | 1 | 2 | 2 | FAIL |
| E10 | experienced | Security Fundamentals | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| F01 | fresher | Algorithms | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| F02 | fresher | Object-Oriented Programming | 2 | 2 | 2 | 1 | 2 | 2 | 2 | FAIL |
| F03 | fresher | SQL | 2 | 2 | 2 | 2 | 2 | 2 | 2 | PASS |
| F04 | fresher | HTTP | 2 | 2 | 2 | 1 | 2 | 1 | 1 | FAIL |
| F05 | fresher | Security Fundamentals | 2 | 2 | 2 | 1 | 2 | 2 | 2 | FAIL |

- Experienced: **5 passed, 5 failed**.
- Fresher-relative Hard: **2 passed, 3 failed**.
- Overall against the registered profile-relative rule: **7 passed, 8 failed**.
- Absolute experienced-Hard reasoning depth: **6 of 15**; one of these, E06, still failed clarity. Neither fresher-relative pass meets the absolute experienced bar.
- Confirmed real provider final outputs: **15/15**. Curated-question fallbacks: **0**.
- No near-duplicate final question was identified within a profile under the registered rule. However, E03, E05 and E08 reuse the payment/checkout/retry domain for different competencies; that concentration is a session-variety concern.
- F03 is a borderline fresher-relative pass; a reviewer using a stricter entry-level bar could call it medium. This uncertainty is explicit, not hidden in a claimed success percentage.

These are agent technical assessments, without independent human adjudication. The sample is small and source-adjacent. No improvement percentage or before/after quality claim is made: production behavior was held fixed throughout collection.

## 4. All 15 actual questions and individual assessments

### E01 ? Data Structures ? experienced

> Suppose your service receives a very large stream of event IDs, and you need to drop duplicates for only the most recent 24 hours because older events may be replayed later. How would you design the data structure and retention strategy so deduplication stays bounded in memory and can recover after a restart?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **yes**.

PASS. Bounded-memory deduplication plus a 24-hour guarantee and restart recovery require reasoning about durable identity, eviction and recovery together. The scenario is realistic and no indefinite/exactly-once guarantee is asserted. Clarify event-time versus processing-time semantics during discussion; this is a design choice rather than a required hidden answer.

Possible follow-up, proposed by the reviewer: *If an event is replayed just after its deduplication entry expires, what guarantee can the system still make?*

RAG database IDs: **67**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[1, 2]`.

Primary diagnosis: No material failure under the registered criteria. Observations: window semantics deserve an explicit follow-up.

### E02 ? Algorithms ? experienced

> You need to support frequent inserts and range queries on a large set of numeric keys. Would you choose a sorted array or a balanced binary search tree, and why? Please state the assumptions you need for correctness and the worst-case time cost of insert and range query in each structure.

**FAIL** ? R=2, T=2, L=2, H=1, E=1, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **no**.

FAIL Hard depth. The question is technically sound and interview-relevant, but a memorized array-versus-balanced-tree complexity table largely answers it. Frequent inserts make the basic choice unsurprising; there is no concrete read/write ratio, memory limit, batching constraint or adversarial workload forcing a difficult decision. Range-output cost and balance assumptions are useful, but this is a good medium-level opener for an experienced candidate.

Possible follow-up, proposed by the reviewer: *How would bursty inserts followed by long read-only periods change the case for batching and rebuilding the sorted array?*

RAG database IDs: **64**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[3, 4, 5]`.

Primary diagnosis: knowledge depth, prompt instructions, LLM generation, difficulty validation. Observations: routine complexity comparison; insufficient workload constraints.

### E03 ? Object-Oriented Programming ? experienced

> A `PaymentGateway` interface promises that calling `charge(amount, idempotency_key)` again with the same key and amount will not create a second charge, even if the first call timed out, and callers can later query the eventual outcome. If one adapter ignores the key and the provider has no idempotency support or outcome lookup, how would you handle that in your design?

**FAIL** ? R=2, T=2, L=2, H=1, E=1, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **no**.

FAIL Hard depth. The contract is now explicit and technically coherent, but the contradiction is supplied in the question: an adapter cannot meet either guarantee. A short reject-or-expose-weaker-capabilities answer can suffice. It does not require designing the weaker interface, representing unknown outcomes or choosing between concrete operational constraints. This tests substitutability application more than experienced Hard reasoning.

Possible follow-up, proposed by the reviewer: *How would you expose a weaker provider capability without allowing a caller to mistake an unknown charge outcome for a safe retry?*

RAG database IDs: **79**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[6, 7, 8]`.

Primary diagnosis: prompt instructions, LLM generation, difficulty validation. Observations: obvious contract violation; redesign objective not constrained.

### E04 ? SQL ? experienced

> You have a `reservations` table for booking the last available item of a product. When two requests arrive at the same time, how would you use SQL transaction behavior to prevent both from reserving the same item, and when would you prefer row locking versus serializable retries?

**FAIL** ? R=2, T=2, L=2, H=1, E=1, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **no**.

FAIL Hard depth. Preventing two reservations of the last item is a realistic SQL problem, and comparing locking with serializable retries is valid. However, this is a familiar single-resource race; a conditional update or suitable uniqueness invariant can resolve the core case. It lacks the multi-item lock ordering, contention evidence, retry boundary or external side effect needed to force experienced Hard discussion. An earlier length-rejected draft did include more of those demands.

Possible follow-up, proposed by the reviewer: *What changes if each checkout reserves several products in a different order and may already have triggered an external payment?*

RAG database IDs: **88**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[9, 10, 11]`.

Primary diagnosis: difficulty validation, LLM generation, prompt/length constraint interaction. Observations: single-resource race simplifies Hard source; richer rejected draft lost constraints.

### E05 ? HTTP ? experienced

> Let's say your API calls a payment provider over HTTP to charge a card. The provider successfully commits the payment, but your service crashes before it can persist the result in your database. How would you design the retry and recovery flow so the system does not double-charge the customer, and how would you detect and repair any stuck or unknown payment states later?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **yes**.

PASS. The provider-commit/local-crash gap forces reasoning about durable intent, ambiguous outcomes, retry safety and reconciliation across a non-atomic boundary. Detecting and repairing stuck outcomes adds operational failure analysis. A sound answer must state the external provider capabilities it relies on; HTTP status or a local deduplication table alone is insufficient.

Possible follow-up, proposed by the reviewer: *If the payment provider has neither idempotency support nor outcome lookup, which guarantee must your recovery contract weaken?*

RAG database IDs: **76**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[12, 13]`.

Primary diagnosis: No material failure under the registered criteria. Observations: payment domain overlaps OOP and Testing, but the competency is distinct.

### E06 ? REST APIs ? experienced

> Let’s say you own an orders feed API that changes frequently as new orders arrive and old ones are updated or canceled. How would you design pagination so clients see a stable, non-duplicating view as the feed changes, and how would you evolve the API over time without breaking existing clients?

**FAIL** ? R=2, T=2, L=1, H=2, E=2, C=1, F=1 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **yes**.

FAIL clarity/focus. Concurrent-feed pagination has Hard reasoning potential, but the question combines pagination consistency with API evolution, two independently large tasks. Stable, non-duplicating view is not defined as snapshot or live-feed behavior, and updates/cancellations can change ordering. This is answerable only after choosing a consistency contract and narrowing the axis. The underlying concepts are sound, not a proven technical falsehood.

Possible follow-up, proposed by the reviewer: *First fix the contract: if new orders arrive during pagination, must an existing cursor see them or preserve its original snapshot?*

RAG database IDs: **82**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[14, 15]`.

Primary diagnosis: knowledge example bundles concerns, prompt instructions, semantic clarity validation. Observations: pagination and versioning bundled; stability contract underspecified.

### E07 ? Git ? experienced

> Your team merged a feature branch into `main`, and that merge also included a data migration that cannot be safely reversed in place. The release has already been shared with other developers and deployed to production. How would you recover from the bad merge in Git and in the application rollout, and what would you verify before allowing older code to run again?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **yes**.

PASS. A shared deployed merge with an irreversible migration requires a recovery decision spanning commit ancestry and application/data compatibility. Source revert is deliberately insufficient, so the candidate must reason about forward recovery, rollout safety and verification. Those layers belong to the same incident rather than unrelated trivia.

Possible follow-up, proposed by the reviewer: *How does choosing the mainline parent for a merge revert affect what a later merge considers already integrated?*

RAG database IDs: **73**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[16, 17]`.

Primary diagnosis: No material failure under the registered criteria. Observations: No additional flag.

### E08 ? Testing ? experienced

> Imagine you own a retryable checkout flow that calls a payment service and then an inventory service. A payment timeout can happen even when the payment actually succeeded, and retries may be sent more than once. How would you design a test strategy for this workflow so you can verify the important failure cases without making the tests flaky?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **yes**.

PASS. Two-service ordering, timeout ambiguity and duplicate retries create interacting failure windows; testing them deterministically requires a fault model, observable invariants and controlled dependencies. A list of test types alone would not fully answer the scenario. Payment wording overlaps E05, but testing the guarantees is distinct from implementing recovery.

Possible follow-up, proposed by the reviewer: *Which invariant would you assert after a timeout and two repeated retries, rather than merely counting calls to a mock?*

RAG database IDs: **91**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[19, 20]`.

Primary diagnosis: No material failure under the registered criteria. Observations: same checkout/payment domain as E03/E05; one embedding transport error preceded the recovered case.


E08 recovery evidence: failed Gemini request **18** preceded the successful retrieval/generation path shown above and remains in the same ledger.

### E09 ? Debugging ? experienced

> A production API started showing a 5x latency spike after a deployment, but the issue is intermittent and you can’t reproduce it reliably in staging. How would you debug it without taking the service down, and what would you look at first to narrow the scope before choosing a mitigation?

**FAIL** ? R=2, T=2, L=2, H=1, E=1, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **no**.

FAIL Hard depth. This is a credible production-debugging opener, but the candidate can give a standard metrics/logs/traces/rollback checklist. The 5x spike and no-downtime constraint do not provide discriminating evidence that forces a hypothesis test or difficult mitigation trade-off. It needs concrete conflicting observations or a constrained diagnostic decision to become reliably Hard.

Possible follow-up, proposed by the reviewer: *If median latency is unchanged but tail latency spikes only on warm-cache requests, what observation would distinguish your two leading hypotheses?*

RAG database IDs: **70**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[21, 22]`.

Primary diagnosis: knowledge depth, generic prompt realization, difficulty validation. Observations: generic incident checklist; no diagnostic evidence to reason over.

### E10 ? Security Fundamentals ? experienced

> Let’s say your service lets users export reports, start background jobs that process those reports, and share a report through a link that expires after some time. How would you design authorization so the same access rules are enforced consistently at the API, in the job worker, and for the sharing link, including what should happen when a user’s access is revoked after a job or link has already been created?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **yes**.

PASS. API, worker and share-link access must obey one authorization policy despite time and revocation. The candidate must consider principal propagation, time-of-check/time-of-use behavior and what an already-created job or link is allowed to do. Multiple access paths are coupled by one security invariant, giving meaningful experienced-level design depth.

Possible follow-up, proposed by the reviewer: *At what point must a worker reauthorize a queued job when the requesting user has lost access since enqueueing it?*

RAG database IDs: **85**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[23, 24]`.

Primary diagnosis: No material failure under the registered criteria. Observations: near the current 420-character limit.

### F01 ? Algorithms ? fresher

> Let’s say you’re building a feature that shows the most recent 100 unique search terms a user typed, in the order they last appeared, and each new search can either add a new term or move an existing term to the most recent position. What data structure or combination of structures would you use to support this efficiently, and why?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **no**.

PASS relative to a fresher. Combining uniqueness, recency updates and a fixed capacity requires more than naming one data structure: lookup, reordering and eviction must work together. It is a realistic integrated-fundamentals task without senior production assumptions. It is not experienced-level Hard; a familiar ordered map or hash-plus-linked-list design addresses it.

Possible follow-up, proposed by the reviewer: *What should happen to the ordering and eviction decision when a term already in the middle is searched again at full capacity?*

RAG database IDs: **None: native fresher-Hard retrieval exclusion**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[25]`.

Primary diagnosis: No material failure under the registered criteria. Observations: no RAG because of the existing fresher-Hard gate; relative Hard only.

### F02 ? Object-Oriented Programming ? fresher

> Suppose you’re designing a simple online shopping cart in Java or Python with a base Product type and a few specific product types like Book and Electronics. If the checkout logic needs to apply different pricing or discount rules based on the actual product type, how would you structure the classes so the code stays easy to extend without adding a lot of if-else checks?

**FAIL** ? R=2, T=2, L=2, H=1, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **no**.

FAIL relative Hard depth. The question appropriately targets a fresher and is clear, but straightforward polymorphism or a pricing strategy eliminates the named if/else chain. It has no concrete rule interaction, edge case or competing extension requirement. This is a useful introductory design question, not a sufficiently challenging Hard one under the registered criteria.

Possible follow-up, proposed by the reviewer: *If discounts vary independently by product type and customer membership, how would you avoid multiplying subclasses?*

RAG database IDs: **None: native fresher-Hard retrieval exclusion**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[26]`.

Primary diagnosis: difficulty calibration, fresher RAG policy, LLM generation, difficulty validation. Observations: textbook polymorphism example; no RAG.

### F03 ? SQL ? fresher

> Imagine you have a users table and an orders table, and you need to write one SQL query that returns each user’s name along with their most recent order date, but still includes users who have never placed an order. How would you structure that query?

**PASS** ? R=2, T=2, L=2, H=2, E=2, C=2, F=2 ? Review confidence: medium. Absolute experienced-Hard reasoning depth: **no**.

PASS, borderline relative to a fresher. The task combines an outer join, aggregation and preservation of users with no orders; the null/unmatched-user condition is a real edge case. A correct solution must group by user identity, not accidentally merge equal names. This fits the registered integrated-fundamentals bar, although many interviewers would call it medium. It is plainly not experienced-level Hard.

Possible follow-up, proposed by the reviewer: *If two users have the same name, what must your grouping key be to keep their results separate?*

RAG database IDs: **None: native fresher-Hard retrieval exclusion**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[27]`.

Primary diagnosis: No material failure under the registered criteria. Observations: borderline fresher Hard; reviewer disagreement plausible; classic join/aggregate problem; no RAG.

### F04 ? HTTP ? fresher

> Let’s say your frontend calls a REST API to update a user’s profile, but users sometimes click the save button twice or refresh the page while the request is in flight. How would you design the HTTP request and response so the update does not get applied twice, and what status codes or headers would you use to make the behavior clear?

**FAIL** ? R=2, T=2, L=2, H=1, E=2, C=1, F=1 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **no**.

FAIL clarity and relative Hard depth. The update operation is unspecified: replacing a profile, incrementing a field and sending a notification have different duplicate-effect semantics. Status codes and headers alone do not establish an at-most-once execution guarantee. The question is not an explicit false claim, but it invites an oversimplified use-PUT answer unless mutation and side effects are defined.

Possible follow-up, proposed by the reviewer: *If saving the profile also sends an email, which additional application-level contract is needed before retries are safe?*

RAG database IDs: **None: native fresher-Hard retrieval exclusion**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[28]`.

Primary diagnosis: prompt contract specificity, fresher RAG policy, LLM generation, clarity validation. Observations: update semantics unspecified; risk of equating method idempotence with one execution; no RAG.

### F05 ? Security Fundamentals ? fresher

> Let’s say you’re adding a login API for a simple web app, and the client sends a username and password over HTTPS. What would you do on the server side to store and verify the password safely, and how would you handle a successful login so the user stays authenticated without exposing the password again?

**FAIL** ? R=2, T=2, L=2, H=1, E=2, C=2, F=2 ? Review confidence: high. Absolute experienced-Hard reasoning depth: **no**.

FAIL relative Hard depth. Password hashing and session/token handling are important, realistic fresher security fundamentals. But this asks for the standard authentication checklist with no concrete attack, revocation, leakage or failure scenario requiring a nontrivial decision. The two steps form a coherent login lifecycle, so the failure is depth rather than technical correctness or obscure content.

Possible follow-up, proposed by the reviewer: *How would logout or a stolen session change what the server accepts on the next authenticated request?*

RAG database IDs: **None: native fresher-Hard retrieval exclusion**. Pipeline fallback: **no**. Provider request IDs for the final generation path: `[29]`.

Primary diagnosis: difficulty calibration, fresher RAG policy, LLM generation, difficulty validation. Observations: standard authentication checklist; no RAG.


## 5. Failure evidence and root-cause analysis

### Retrieval is generally selecting the intended knowledge

All ten experienced cases retrieved exactly one correct role/topic/Hard source from the actual database. There were no wrong-role or wrong-difficulty rows. Because each topic has one eligible Hard chunk, these runtime results primarily establish filtering and source availability; there was little within-topic semantic-ranking competition. Adding more embeddings or rebuilding the index is not supported as a solution to the observed depth failures.

All five fresher cases received **zero RAG context** because `retrieve_chunks_async` explicitly excludes Hard context for `fresher`/`internship`. The generation node nevertheless receives `difficulty='hard'`, while its experience guidance prioritizes practical fundamentals. It invokes the model with the standard-fundamentals/no-reference instruction. This is a configured policy interaction, not a missing-row or vector-corruption problem. It also differs from a curated-question fallback: all five final fresher questions were live model outputs.

The mixed Hard contract contributes to F02/F03/F05 being common fundamentals despite a Hard label. Relative Hard can be legitimate, but the current data and label do not explain which interpretation is intended or provide experience-specific Hard grounding.

### The built-in validator does not assess cognitive difficulty

`validate_generated_question` checks minimum/maximum length, obvious multi-question patterns, duplicate similarity, a short academic-term blocklist and unsupported project references. It does not establish whether answering requires interacting constraints, compare plausible designs, test a hard failure mode, or exceed a textbook one-step response.

Returned question metadata assigns the normalized requested difficulty. A generated task being easy is not detected merely because the output says `hard`; the model-provided difficulty field is not an independent quality check. This explains how E02/E03/E04/E09 and F02/F05 can pass the runtime validator while failing this audit's Hard-depth bar. No failures here came from curated fallback selection, since no final fallback was used.

### The 420-character ceiling can discard useful constraints

E02, E03 and E04 each required one additional model attempt after the first draft was rejected as ?overly long or broad.? All three logged rejections used the same length message; none was a semantic depth rejection.



| Case | Rejected draft characters | Accepted question characters |
| --- | ---: | ---: |
| E02 | 436 | 289 |
| E03 | 531 | 372 |
| E04 | 466 | 280 |

In E04's rejected draft, the provider described reserving **two seats out of five**, protecting a correctness invariant, expected contention/failure, and an external operation outside the retryable transaction. The accepted draft instead asks about the last item and a general lock-versus-serializable preference. E03's longer draft explicitly asked about redesigning the interface/adapter boundary; the accepted version ends with ?how would you handle that in your design?? E02's rejected draft also stated a concrete range example and the unbalanced-tree edge.

The audit directly observed these details disappear after brevity feedback. It did not run a controlled A/B test, so it cannot quantify the ceiling's causal contribution. Nevertheless, the interaction is specific and reproducible from the saved raw responses, and a better question-assembly/clarity rule is higher priority than adding more rows.

### Knowledge examples set a limited ceiling

There is one Hard question example per role/topic. Algorithms is already framed around sorted array versus tree; OOP around a directly stated contract violation; Debugging around a generic production-latency investigation. The generator often closely rephrases that framing. The focused Hard context retains the selected question, definition, trade-offs and provenance, but it does not add concrete evidence, counterexamples, workload facts or worked implementation constraints absent from the source.

E02 and E09 therefore reflect both source depth and generic model realization. E06 inherits a source question that combines pagination with API evolution. The source notes remain technically useful; selecting them correctly does not prove that their question example meets the intended Hard bar.

### Prompt and model failures remain observable despite prior refinements

Existing prompts already request meaningful Hard decisions, explicit assumptions and one focused task. Yet E03 still permits a nearly one-line contract answer, E06 bundles two axes, and F04 leaves update semantics undefined. More repetitions of ?make it harder? are unlikely to resolve this reliably. The generator needs concrete task constraints and an observable acceptance check.

The question-selector was bypassed only to establish topic coverage; adaptive selection quality was not measured. Domain concentration across OOP/HTTP/Testing is observed, but it cannot be attributed solely to that untested selector. More explicit scenario-family selection and cross-topic diversity signals are plausible fixes to test.

### Transient retrieval failure and recovery

Gemini embedding request **18**, for E08, failed with **RemoteProtocolError**. The real retrieval node caught the error and returned empty context, as it would in normal operation. The audit stopped before generating that question, diagnosed the recorded transport failure, repeated the read-only database verification, and resumed only the incomplete case. Request **19** succeeded and the final E08 used its real Testing source.

Completed questions were not regenerated or replaced because they looked weak. Request 18, its full budget reservation, and all previous results remained in the same ledger. Normal product behavior would continue ungrounded after this error; that should be represented in provenance/telemetry rather than confused with successful retrieval or an intentional fresher policy exclusion.

## 6. API calls, usage and estimated cost

This task has its own ledger, separate from the prior rollout experiments. All calls in this audit were observed from the beginning: Azure at the SDK `responses.create` boundary and Gemini at the actual embedding request boundary.

| Provider / model | Requests | Available usage | Status |
| --- | ---: | --- | --- |
| Azure OpenAI / `gpt-5.4-mini` | **18** | **20,771 input tokens, 1,687 output tokens** | 18 completed responses; 15 accepted final questions and 3 length-triggered regenerations |
| Gemini Developer API / `gemini-embedding-001`, 768 dimensions | **11** | 10 successful query inputs, estimated **1572.25 input tokens** from characters/4; no provider token/billing metadata | 10 HTTP-200 responses, 1 transport failure, followed by one explicit recovery attempt |
| Total external request attempts | **29** | Mixed measured generation and estimated embedding usage | No document embeddings, grading, Speech or follow-up generation calls |

Successful-request reference-price estimate: **$0.02340559**. Conservative budget charge including the failed request reservation: **$0.282549 / $2**. Actual Azure/Gemini account billing is unavailable. The failed transport call's billed usage is unknown and is not assumed free.

Reference prices checked from [OpenAI's gpt-5.4-mini model page](https://developers.openai.com/api/docs/models/gpt-5.4-mini) ($0.75/M input and $4.50/M output) and [Google's Gemini embedding pricing](https://ai.google.dev/gemini-api/docs/pricing#gemini-embedding) ($0.15/M input). The OpenAI public rate is a comparison estimate, **not verified Azure account pricing**. Query-embedding token counts are estimates, not actual provider counts. No discounted batch rate was assumed.

The pre-request budget guard reserves at higher $10/M input and $40/M output generation assumptions with a byte-based input bound and the existing 4,000-output-token cap. Embedding calls reserve a byte-based bound at $1/M input. Those estimates are persistent across the resumed run. SDK transport retries are disabled; generation's three validator-driven retries and the one diagnosed embedding recovery are all accounted for. No credentials were exposed or changed.

## 7. Prioritized implementation recommendations

| Priority | Specific change to test | Evidence and intended benefit | Verification before shipping |
| --- | --- | --- | --- |
| **P0** | Define and implement one joint experience ? difficulty contract across retrieval, generation and labels. Keep fresher challenge grounded in integrated fundamentals; either provide suitable fresher-Hard context or explicitly normalize/describe the level rather than silently mixing a global Hard label with empty context. | All F cases have no RAG; three failed relative depth/clarity. Avoid lifting the guard blindly and exposing freshers to senior architecture. | Paired fresher/experienced fixtures must verify both retrieved level and actual task demand; include F01/F03 as borderline reference cases and independent human review. |
| **P0** | Add evidence-based Hard-draft acceptance beyond character counts: a concrete constraint, a consequential decision, and a failure/edge or competing valid option. Do not accept model self-labelling as evidence. | E02/E03/E04/E09 passed structural validation with routine answers. | New regression cases must reject one-line contract identification, a generic incident checklist and canned complexity-table answers, while accepting concise challenging alternatives. Use a reviewed holdout, not just these same 15. |
| **P1** | Separate compact scenario/constraints from the single asked decision, or use a profile-sensitive length/word budget. Shorten boilerplate before discarding invariants; do not just raise every question's limit. | Three real length rejections; E04 lost quantitative and failure/retry constraints. | A paired experiment should retain the important SQL/OOP constraints without bundling independent tasks or making questions needlessly long. Save rejected and accepted drafts. |
| **P1** | Make Hard source examples and the focused projection carry scenario facts, decision alternatives, boundaries and a short counterexample?not merely expected-concept nouns. Keep the existing topic set and review revisions. | Correct source retrieval still led to shallow Algorithms/OOP and generic Debugging. REST's source bundles independent axes. | Review exact revised-source diffs and test new unseen paraphrases. E06 should ask pagination consistency first, leaving compatibility to a follow-up; E09 should include evidence that distinguishes hypotheses. |
| **P1** | Require the mutation/effect contract where idempotency or substitutability is being assessed. | F04 does not define replacement versus increment or external effects; E03 supplies an obvious violation but not a constrained redesign goal. | Questions must state the effects/guarantees needed to answer, permit justified alternative designs and avoid a status-code-only guarantee. |
| **P2** | Add scenario-family variety across topics, keeping question deduplication and truthful candidate grounding. | Three experienced questions reuse payment/checkout/retry, although they test distinct competencies. | Test multiple sessions with different scenario families; do not invent candidate projects or mistake cross-topic shared nouns for exact duplicate questions. |
| **P2** | Preserve structured retrieval status internally: policy exclusion, no eligible rows and provider failure should be distinguishable. Apply a bounded, metered transient retry policy where appropriate. | E08 transport failure is currently collapsed to empty context, just like intentional fresh-Hard exclusion. | Inject a transport error and verify provenance/status, budget and retry counts. Never rewrite knowledge data to recover from a network error. |

These are recommendations, **not implemented changes or claimed improvements**. Start with the experience contract, Hard acceptance and question assembly before expanding the corpus. A future before/after audit should hold the rubric stable, include unseen questions, retain failures, and use independent reviewers where possible.

Technical guardrails for those future tests: [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2) distinguishes intended idempotent effects from identical responses or a universal single execution; [PostgreSQL isolation documentation](https://www.postgresql.org/docs/16/transaction-iso.html) explains serialization/retry behavior; [Git revert documentation](https://git-scm.com/docs/git-revert) defines mainline-parent selection; [OWASP authorization guidance](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) supports consistent per-operation checks. None of these references makes the generated questions complete answer keys.

## 8. Deliverables, boundaries and limitations

- This report contains all 15 final question texts verbatim, all seven scores, reasons, root-cause assignments and reviewer-proposed follow-ups.
- [Preregistered criteria/matrix](../storage/phase6b/hard-mode-quality-audit/criteria.json), [actual questions and RAG context](../storage/phase6b/hard-mode-quality-audit/questions.json), [machine-readable review](../storage/phase6b/hard-mode-quality-audit/quality-review.json), [request/usage ledger](../storage/phase6b/hard-mode-quality-audit/api-usage.json), and [execution summary](../storage/phase6b/hard-mode-quality-audit/execution-summary.json) are saved. Every provider request and successful raw response is retained locally.
- All production source hashes and frozen evaluation inputs are checked for preservation. Only the local audit harness and this review were added; no product code, prompt, knowledge source or grading behavior was tuned during the audit.
- Read-only assertions and actual generation were executed; the full pytest/frontend/browser suites were not rerun for this audit-only task. Earlier test counts are not presented as new execution.
- Topic selection was controlled; answer-adaptive flow, generated reference answers, follow-up generation, grading consistency and human microphone/browser behavior were not tested.
- The questions are a single stochastic sample from one configured model, assessed by one agent. Counts are descriptive under the registered bar, not objective model-wide success percentages. F03 and other depth boundaries can reasonably merit human adjudication.
- No permanent user sessions, historical evaluation changes, data repairs, migrations, production deployment, commits or pushes occurred. Artifacts remain local ignored files; no API key or real candidate resume was included.

**Conclusion: the reviewed rollout remains intact. Correct knowledge retrieval is verified, but experienced Hard calibration is not yet reliable under this standard. Prioritize task-demand validation and experience-aware question construction.**
