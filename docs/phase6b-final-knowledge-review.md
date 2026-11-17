# Phase 6B: final knowledge review and rollout recommendation

> Current outcome: [local autonomous completion](phase6b-autonomous-completion.md). The reviewed 30 Software Engineer rows are committed and verified (61 total). Earlier failures and approval instructions below are historical; the newer user development policy governs local work.

Date: 15 November 2026. **Recommendation: GO to request separate approval for the controlled 30-row Software Engineer rollout. This review does not authorize ingestion.**

The evaluated notes are technically sound enough to ground the bounded interview scenarios and follow-ups reviewed here. They are sparse as worked implementation references, particularly in several Hard topics. Those limitations should constrain rollout claims: this is an initial, monitored RAG expansion, not a complete advanced Software Engineer curriculum or a validated autonomous answer key. No critical technical contradiction, newly unsafe guarantee or unsupported mandatory answer was identified in the reviewed context.

No source record, frozen evaluation label/threshold, cached vector, application code, rubric or historical data was changed. No paid API call, live ingestion, commit or push occurred. The only database operation was an explicitly read-only ingestion preview saved to a separate directory so the evaluated snapshots remained frozen.

## Evidence reviewed

- Actual cached Gemini rankings and retrieved text for all ten Hard cases, the OOP Medium miss and all 17 secondary-context omission cases.
- Expected support concepts, primary and secondary relevance judgments, source provenance, current revision-2 notes and the frozen 32-case dataset.
- Source, request, result and vector-cache hashes against the Approval A artifact inventory.
- Fresh read-only PostgreSQL preview and the prepared apply, postcheck, receipt-based retirement and restoration procedures. No approved write path was run.

The frozen scores remain 29/30 Hit@1, 30/30 Hit@3, MRR 0.9833 and nDCG@3 0.9404; both policy negatives abstain and role/difficulty violations are zero. Every Hard case retrieves its intended primary at rank 1. These scores establish retrieval over this small author-curated set; they do not establish broad question-generation, grading or production-interview quality. This is an agent technical review, not independent human SME certification.

## Hard-mode depth matrix

**S** means sufficient to frame and probe the specific bounded scenario. **P** means partial: more explanation or a candidate-proposed implementation is needed. Neither rating means a complete answer is present. ?Depth priority? ranks future source enrichment, not a discovered correctness failure.

| Topic | Advanced reasoning | Realistic scenario | Failures / edges | Trade-offs | Implementation discussion | Follow-ups | Depth priority |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Data Structures | P | S | S | S | P | S | Medium |
| Algorithms | S | S | S | S | P | S | Low |
| Object-Oriented Programming | S | S | S | S | P | S | Medium |
| SQL | S | S | S | S | P | S | Medium |
| HTTP | P | S | S | S | P | S | High |
| REST APIs | P | S | S | S | P | S | High |
| Git | P | S | S | S | P | S | High |
| Testing | P | S | S | S | P | S | High |
| Debugging | S | S | S | S | P | S | Medium |
| Security Fundamentals | P | S | S | P | P | S | High |

### Data Structures ? `ds-hard`

The stream/replay-window question is appropriately advanced. Durable identity, retention, recovery, memory bounds and duplicates after expiry are present; the seven-day window in the query is compatible with the note. It does not prescribe a durable uniqueness schema, atomic deduplication-and-processing boundary, checkpoint protocol, late-event policy or storage sizing. Hash membership and bounded retention are accurate, but the simple Python data-structures citation does not substantiate a complete distributed deduplication design.

A suitable follow-up: What happens when a worker crashes after applying the effect but before recording completion, or when an event arrives just outside the retention window?

### Algorithms ? `algo-hard`

The corrected balanced-tree assumption is explicit. Logarithmic balanced search/insertion, linear array insertion, output-dependent range cost, duplicate boundaries, locality and workload measurement support advanced reasoning without claiming all trees have logarithmic worst cases. Binary-search non-progress provides a concrete failure mode. The note lacks pseudocode, a stated comparator/key model, a balancing example and an explicit batch-rebuild cost calculation. Python bisect supports the search-versus-insertion distinction, not a proof of balanced-tree guarantees.

A suitable follow-up: How do burst size, duplicate-key policy and range-output size change the break-even point for rebuilding?

### Object-Oriented Programming ? `oop-hard`

This is the strongest clarified contract example: same key and amount, no duplicate charge across timeouts, eventual-outcome lookup, and an adapter unable to honor that promise. It correctly distinguishes contract preservation from shared method names and allows rejecting the adapter or exposing weaker capabilities. Local deduplication is correctly not presented as an atomic solution for an uncertain external effect. There is no worked interface, outcome type, state sequence or contract-test implementation. The Python classes reference supports object state, not the payment-retry contract itself.

A suitable follow-up: Which outcomes must be represented explicitly, and how would a caller behave when the provider cannot distinguish an unknown result from a failed charge?

### SQL ? `sql-hard`

The multi-item reservation is realistic. Conditional UPDATE and affected rows, lock ordering, serialization aborts, contention and external side effects support the expected concepts. PostgreSQL isolation documentation supports retrying the whole aborted transaction; lock acquisition and serializable execution should not be treated as mutually exclusive or as making external effects transactional. The note does not supply SELECT FOR UPDATE, a deterministic multi-row lock sequence, complete rollback/retry pseudocode, SQLSTATE handling or invariant tests. Its named concepts are correct but insufficient as a worked implementation reference.

A suitable follow-up: How do you acquire several item locks consistently, and what exact transaction and external operations are repeated after an abort?

### HTTP ? `http-hard`

Provider success followed by local persistence failure is an appropriate hard scenario. Unknown outcomes, durable outcome storage, payload validation, expiry, bounded retry and reconciliation are present; no naive exactly-once guarantee is asserted. HTTP method idempotence and application idempotency keys are correctly separated. The durable state machine and reconciliation policy are mostly names in expected concepts: no crash-window sequence, concrete states, concurrent same-key handling or operator repair protocol is provided. RFC 9110 supports method/retry semantics, not a provider-specific payment recovery guarantee.

A suitable follow-up: Which durable state exists before dispatch, how are concurrent retries deduplicated, and how is a stuck unknown result reconciled?

### REST APIs ? `rest-hard`

Changing feeds and old mobile clients create real ordering, consistency and compatibility trade-offs. Offset skip/repeat behavior, stable ordering, cursor contracts and authorization are correctly identified. The material does not define a total ordering/tie-breaker, cursor encoding/integrity, snapshot versus live-feed guarantees, deletion behavior or an example compatible API evolution. Consequently it can frame the interview but cannot by itself settle implementation choices. RFC 9110 supports HTTP semantics; a complete pagination/versioning contract is original design work beyond that citation.

A suitable follow-up: How do tied timestamps, deletes and concurrent inserts affect the cursor guarantee, and what behavior must an old client continue to observe?

### Git ? `git-hard`

The irreversible-migration scenario correctly separates source history from application/data recovery, and contrasts focused revert with a forward fix. Merge-parent interpretation and effects on later merges are correctly flagged. The note does not explain choosing -m against an actual merge graph, reversing relative to the chosen parent, or a staged application/schema compatibility plan. Those omissions matter for implementation discussion, but the note makes no false promise that a revert restores data. The linked git-revert manual supplies the missing parent semantics.

A suitable follow-up: Which parent defines the retained line of history, and what compatibility evidence is needed before older application code can be redeployed?

### Testing ? `testing-hard`

The two-service retry workflow supports discussion of layered tests, controlled dependencies, failure injection, idempotency and real integration boundaries. It explicitly avoids treating mocks or high coverage as proof. There is no concrete fault matrix, crash-before/after-commit test, invariant-based assertion, scheduler control or sample contract test. Thus it is a good strategy prompt with shallow implementation grounding. The fixtures reference supports setup/cleanup, not a full multi-service correctness argument.

A suitable follow-up: At which crash boundaries would you inject faults, and which observable invariant should hold after replay rather than merely checking call counts?

### Debugging ? `debug-hard`

The production-only latency scenario supports scoping, traces, falsifiable hypotheses, controlled change and safe mitigation. Timing perturbation, overhead and the distinction between correlation and cause are addressed, making the reasoning direction sound. It lacks a worked diagnostic sequence, queue/database/dependency measurements, competing-hypothesis examples and evidence thresholds. pdb documentation supports local state inspection rather than a full production observability strategy. The material is sufficient to open and probe a realistic incident discussion.

A suitable follow-up: What observation would falsify your leading hypothesis, and how would you distinguish a successful mitigation from a root-cause fix?

### Security Fundamentals ? `security-hard`

Multiple access paths, job principals, sharing revocation and caches are realistic security design concerns. Deny-by-default, object/policy-scoped lookup, least privilege and consistent authorization are accurate. Revocation and cache behavior occur largely as expected concepts and a follow-up rather than an explained enforcement design. Missing detail includes principal propagation, cache key/authorization boundary, revocation invalidation or policy-version checks, token expiry and authorization-aware negative tests. OWASP supports per-request checks and testing, but this note is not a complete share-link/cache security specification.

A suitable follow-up: Which principal authorizes an export job, and how does a cached response fail closed after a share is revoked?

No record contains a full worked end-to-end implementation. Candidates should be able to choose reasonable alternative designs; the short expected-concept lists must not be interpreted as the only acceptable solution. Existing question-generation instructions use retrieved material for factual grounding and experience calibration. Existing grading instructions prohibit inventing mistakes and treat retrieved text as untrusted. Those prompts reduce the risk but do not substitute for future generated-question/answer review; no such paid test was run here.

## OOP Medium: first-place miss

Query: ?Checkout must support two payment providers with different error types. Where would you put the boundary so orchestration stays testable??

| Rank | Family | Cosine | Frozen relevance |
| --- | --- | ---: | ---: |
| 1 | Testing | 0.674668 | 0 |
| 2 | OOP | 0.670335 | 3 |
| 3 | REST APIs | 0.627687 | 0 |

Testing shares checkout/gateway/testability terms and provides useful fakes/contract-test context. It does not directly answer composition or adapter error translation. The second-ranked OOP record explicitly contains an interchangeable payment gateway interface, composition, failure behavior and the error-translation follow-up. Consequently a top-three consumer receives the needed grounding, but a top-one consumer would get only part of the answer framing. The 0.004333 cosine gap supports describing this as close semantic competition, not a confidence probability or proof about the model's internal cause.

The recorded secondary is Debugging; its Medium record concerns cross-request shared state and is a weak supplement for this particular interface-design query. Testing is more useful in practice than the frozen grade 0 suggests. **The frozen label is retained**, so the miss and published metrics stand. Existing explicit OOP topic filtering narrows this case to the OOP record; do not remove that filter based on the broader semantic benchmark.

Future improvement: enrich the OOP adapter/error contract explanation and evaluate new unseen paraphrases in a separately approved source/benchmark revision. Do not tune this run's labels, thresholds or similarity cutoffs to eliminate the miss.

## All secondary-context omissions and annotation quality

Seventeen cases omit a frozen grade-1 related family from the first three positions. In every case the intended primary is still available, and no required concept depends solely on the omitted related family. The primary records sometimes name a concept without explaining its implementation; that is a depth limitation, not evidence that an omitted generic family would supply the missing explanation.

| Case | Omitted secondary | Technical assessment |
| --- | --- | --- |
| ds-hard | `swe.algorithms` | Weak optional label: the Hard Algorithms record compares array/tree workloads; it does not supply durable replay-window deduplication. The primary already names retention/recovery; retrieved HTTP adds useful retry context. |
| oop-easy | `swe.debugging` | Generic reproduction help is optional. Retrieved Testing and Data Structures are at least as directly relevant to shared state and isolation. |
| oop-medium | `swe.debugging` | The debugging-medium record concerns cross-request state leakage, not adapter composition or error translation. Testing, although frozen at grade 0, is practically relevant supplementary context. Primary rank 2 remains essential. |
| oop-hard | `swe.debugging` | Generic production diagnosis is weaker support than the actually retrieved HTTP retry semantics and Testing contracts. The primary supplies the substitutability/retry guarantee. |
| sql-easy | `swe.debugging` | Reproduction methodology is optional; it does not explain join/null/WHERE semantics. Those concepts are present in the SQL primary. |
| sql-medium | `swe.debugging` | Controlled concurrency is related, but the missing generic debugging note is not needed to explain the atomic UPDATE and affected-row check. |
| sql-hard | `swe.debugging` | Incident measurement may assist contention investigation but is not a source for lock ordering or transaction retry correctness. SQL supplies the required concepts. |
| http-hard | `swe.rest` | The related REST Hard record is about pagination/API evolution. Retrieved OOP retry-contract and SQL transaction notes are useful alternatives; REST omission does not remove the payment-recovery framing. |
| rest-medium | `swe.security` | Authorization is valid supplementary context but does not establish optimistic-concurrency validators. REST and HTTP supply the requested stale-write concepts. |
| rest-hard | `swe.security` | Authorization/revocation is useful optional API context, not required to establish stable ordering and client compatibility. Security-specific guarantees should still be probed separately. |
| git-easy | `swe.testing` | Recovery verification is sensible, but the Testing Easy fixture note does not establish shared ancestry. Git provides the primary explanation. |
| git-hard | `swe.testing` | Testing recovery is useful, but the Testing Hard checkout/retry scenario does not itself supply migration compatibility or merge-parent semantics. The Git primary names those concerns; worked recovery evidence remains a depth gap. |
| testing-easy | `swe.debugging` | Generic bug reproduction is optional. The primary and retrieved OOP/shared-state context directly support isolation and cleanup. |
| testing-medium | `swe.debugging` | The debugging-medium state-leak scenario is less specific than retrieved HTTP/OOP retry/contract material. Controlled time, fake failures and mock-contract checking remain in Testing. |
| testing-hard | `swe.debugging` | Production incident diagnosis is optional for a layered failure-injection test strategy. HTTP and OOP complement the primary retry/idempotency concepts. |
| debug-medium | `swe.testing` | Controlled dependencies and regression testing are useful, but the selected Testing Medium timeout example is not the same as cross-request leakage. The primary explicitly names controlled concurrency and a regression test. |
| debug-hard | `swe.testing` | Tests are useful after a hypothesis is isolated, but a checkout test-strategy note does not replace production traces and safe mitigation. These are present in Debugging. |

Primary relevance judgments match the intended query and were retained. Secondary annotations are often broad family associations repeated across difficulty levels rather than chunk-specific evidence that a required concept is supported. In particular, OOP?Debugging and HTTP Hard?REST Hard are weak relevance judgments. Actual useful HTTP/OOP/Testing supplements can receive grade 0 under the current annotations. Therefore interpret secondary omissions and nDCG as results under the registered labels, not an authoritative assessment of all useful context. A future benchmark should independently annotate individual chunks and required concepts, with adjudication before provider evaluation. Do not revise this frozen dataset after observing its rankings.

## Source support and material concerns

| Concern | Severity for this controlled rollout | Assessment / action |
| --- | --- | --- |
| Sparse implementation explanations in Hard records | Moderate | HTTP, REST, Git, Testing and Security are the clearest enrichment priorities. Current text can frame questions but is insufficient alone to validate every implementation detail. Keep the rollout limited and review generated Hard questions and feedback during controlled use. |
| Citations support foundations more directly than advanced scenarios | Moderate | Original engineering scenarios are clearly identified as original notes. The linked foundational documentation should not be read as certifying all distributed-system, payment or cache-design claims. Add more specific primary references only in a separately reviewed revision. |
| Small, author-curated benchmark closely aligned with source scenarios | Moderate | Good initial smoke evidence, limited generalization evidence. An independent unseen holdout and human review remain valuable before a broader beta or wider curriculum claim. |
| Broad secondary relevance labels | Moderate for measurement; low for core-topic retrieval | Published metrics remain valid under frozen labels. Do not infer a technical-context failure from every grade-1 omission or treat grade-0 Testing as wholly useless in the OOP miss. |
| Shared advanced prose in easy chunks | Moderate calibration risk | Easy chunks include the shared scenario/trade-offs. The existing generation prompt calibrates to experience; actual generated difficulty has not been established by retrieval metrics. |
| OOP rank-one confusion | Low with existing topic scope / top-three retrieval | Primary context is at rank 2 and all required concepts are available. Monitor adapter-design phrasing; a top-one-only consumer would require reassessment. |

Spot checks of primary documentation support the underlying distinctions: Python documents [binary-search versus insertion cost](https://docs.python.org/3/library/bisect.html), PostgreSQL documents [isolation and whole-transaction retries](https://www.postgresql.org/docs/16/transaction-iso.html), RFC 9110 distinguishes [method idempotence and non-idempotent retries](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2), Git defines [merge-revert mainline selection](https://git-scm.com/docs/git-revert), and OWASP recommends [per-request authorization and authorization tests](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html). Python [classes](https://docs.python.org/3/tutorial/classes.html), [debugger](https://docs.python.org/3/library/pdb.html) and pytest [fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) substantiate the narrower examples they document; the additional advanced architecture discussion remains original engineering reasoning.

These concerns do not require changing the frozen revision before this bounded rollout. They would be material blockers to claiming the notes are an exhaustive hard-mode curriculum or that complete grading behavior has been independently validated. A future correction to an actual false claim, rather than optional enrichment, should trigger a fresh source review and manifest; none was identified here.

## Frozen integrity and fresh PostgreSQL state

All source-file hashes in the reviewed source inventory still match, all ten notes remain revision 2, all evaluated artifact file hashes still match the Approval A inventory, and all 30 rollout texts have their evaluated 768-dimensional document vectors in the cache. The 81 inspected backend/taxonomy module files remain unchanged by this review.

| Artifact | Verified SHA-256 / identifier |
| --- | --- |
| Frozen request SHA-256 | `2808da2d365ad56b943629b1777c9c82b07cb55c77665506050f25b25e77f79b` |
| Source-manifest file SHA-256 | `fcf5c52bc3e86222832dca72c98146272f762b7f1bd4c73028e3c4f495c8780d` |
| Source-manifest internal content digest | `02f5660e48757787b255e38b0151e333dfdaaffc745c44642e572590005c9f44` |
| Evaluated vector-cache SHA-256 | `fbf87e80d48c2c0f2926316aa451760791a5994ecf47a75e4cf854d89cde40c9` |
| Frozen dataset SHA-256 | `6f4f43b0734bafb783209c1735e046c3c4a7293f0e3160ed0a22cc7fe473d424` |
| Role-only preview file SHA-256 | `cac0234b7a0e712ed35e5d38dff16e39d6b61403ae8271207a5cae397a0903d4` |
| Role-only approval-plan identifier | `5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070` |
| Legacy row-content/vector digest | `0cb2fefcfd095bfb6f5cb8f8a95533c0699b3cc91766cb842a827d2037938e2b` |

The internal manifest digest and the file-byte SHA-256 are deliberately labelled separately. Per-file source hashes remain in [the frozen readiness inventory](../storage/phase6b/evaluation-readiness.json). [Fresh final-review integrity results](../storage/phase6b/final-review-integrity.json) and [fresh role-only read-only preview](../storage/phase6b/final-review-preview/preview-software-only.json) are saved separately from the evaluated artifacts.

Fresh database confirmation: **31 existing rows**, matching the frozen legacy digest including metadata, text and vectors. The refreshed role-only plan is byte-equivalent in parsed JSON to the reviewed plan: **30 inserts, zero updates, zero retirements and no orphaned managed identities**. No existing source identity or row is targeted for replacement. No user-data table was mutated or historical score recalculated.

The preview reports **30 embedding inputs required by the new rows**, not 30 unavoidable paid calls. The prepared role-only apply injects `cached_embed` into the existing `apply_plan` extension point; every required text hash is present in the evaluated cache. Therefore **zero new embedding calls are required**. No new provider attempt is included in Approval B.

## Exact changes requiring Approval B

Only table `public.chunks` is in scope. Insert these stable identities, each with role `software_engineer`, the frozen revision-2 content/metadata/hash and corresponding evaluated document vector:

| Identity prefix | Difficulty suffixes | New rows |
| --- | --- | ---: |
| `prepmate:swe.algorithms:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.data_structures:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.debugging:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.git:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.http:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.oop:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.rest:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.security:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.sql:software_engineer:` | `easy`, `medium`, `hard` | 3 |
| `prepmate:swe.testing:software_engineer:` | `easy`, `medium`, `hard` | 3 |

The prefixes plus suffixes above specify all 30 full source names, for example `prepmate:swe.sql:software_engineer:hard`. [Exact row inventory including every content hash and embedding-input hash](../storage/phase6b/final-reviewed-rollout-rows.csv) and [the frozen 30-row source manifest](../storage/phase6b/software-manifest.json) are the detailed change specification. Database row IDs and creation timestamps will be allocated on insertion and recorded in the receipt; they are not invented in advance.

Expected post-approval state: **61 total rows**, comprising the unchanged 31 legacy rows and 30 active Software Engineer rows, ten at each difficulty. No update, delete, retirement, schema change, role-taxonomy change, index migration or embedding-model change is included. The **156-row folder plan** and **183-row full-corpus plan** are explicitly outside this proposed approval. No other roles' shared copies or role-foundation records are included.

The proposed Approval B must bind the role-only plan token **`5b7b004975edfd5ae85ef47943e725bf4b5e252bc7c26735a46395efd2d84070`**, source-manifest file hash and evaluated cache hash above. It authorizes only this insertion transaction, cache reuse and its read-only verification. It does not authorize another embedding evaluation, historical rescoring, user-data changes, Azure calls or a subsequent recovery write.

## Transaction, verification and receipt-based recovery

The prepared scripts were inspected; their live write paths have not been executed. The safe procedure after explicit Approval B is:

1. Preserve the frozen artifacts and verify their byte hashes immediately before execution. The apply script compares source/cache metadata and current source contents but does not itself pin the complete cache byte hash; the operator's frozen-hash check is required. Keep the local files unchanged during the run.
2. Prevent competing knowledge-ingestion jobs during the cutover. The transaction advisory lock `634220061` serializes cooperating managed ingestion, not arbitrary SQL writers. Recheck the live legacy snapshot, count 31, exact 30-insert plan and approval token inside that lock. Abort on any mismatch; never widen the plan automatically.
3. Reuse only the 30 evaluated document vectors with `cached_embed`. The existing ingestion path validates vector counts, dimensions, finite values and nonzero contents before flushing. It adds the rows, rechecks legacy integrity before commit and verifies the 30 active identities. All database mutations are in one transaction; a pre-commit failure rolls them back.
4. After commit, save `rollout-receipt.json` with the 30 allocated IDs, names, content hashes, original role and legacy digest. Receipt-file creation occurs after the database commit, so a filesystem error does not imply rollback. Do not blindly rerun apply in that situation: use the prepared read-only postcheck to reconstruct `postcheck-receipt.json`, review it against the frozen manifest and preserve it as the recovery receipt.
5. Run the prepared read-only postcheck: total 61; unchanged legacy digest; exactly the intended 30 active rows; ten per difficulty; repeat role-only preview has no changes and zero pending embedding inputs. For full cache-integrity verification, also compare new row content/metadata and stored vectors to the frozen manifest/cache in a read-only check, allowing normal PostgreSQL float32 vector rounding. The current postcheck checks identities/content hashes and legacy vectors but does not itself perform that full new-vector comparison; it must not be described as doing so.
6. Verify scoped retrieval with cached query vectors and inspect representative sources and difficulty. This needs no new paid call. Stop and investigate any drift; live generation or real interviews are a separate verification scope.
7. If an already committed rollout must be disabled, seek separate recovery approval. Use only the exact receipt IDs/names/hashes/expected roles: change those 30 roles from `software_engineer` to `retired` in one locked transaction. Retain their text, IDs and vectors; never delete or modify the legacy 31. A changed receipt row causes refusal. Restoration of those roles is another explicit approval. Role-only retirement retains the active content hash, so an unchanged-content ingestion preview is not a reliable reactivation mechanism; use the reviewed explicit restore procedure.

This is recoverable scoped activation, not proof that a rollback has been live-tested. The receipt-file edge case, cooperating-writer limitation, hash pinning and postcheck coverage are explicit operator responsibilities, not silent guarantees of the current scripts. No new safety feature or architecture change was introduced in this review.

The prepared [command sheet](phase6b-rollout-commands.md) contains the guarded future commands. **Do not execute its Approval A embedding command again; that one attempt is consumed. Do not execute Approval B or recovery commands without new explicit approval.**

## Final recommendation

**GO for a separate, controlled 30-row Software Engineer-only ingestion approval request.** The frozen semantic results, topic grounding, corrected contracts, fresh legacy-preservation check and cached-vector coverage justify that limited scope. The implementation-depth, calibration, annotation and generalization caveats remain part of the review record and should govern subsequent real-user observation and source expansion.

**Actual rollout status: NOT APPROVED / NOT EXECUTED.** If the scope becomes a full curriculum rollout, an autonomous hard-answer reference, or a cache/source hash changes, this recommendation does not carry over; stop for a new review rather than reuse the token.
