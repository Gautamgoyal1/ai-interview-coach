# Phase 7.1 — complete question evidence

Date: 2026-11-16. All quality judgments are agent-only, without independent human adjudication. These are actual pipeline outputs, including unsuccessful questions; no replacement wording is substituted.

The 30-case holdout was frozen before execution. A subsequent 10-case, separately preregistered recovery/coverage check used different code and seeded history. It is reported separately, not pooled into a replacement success rate. Later deterministic projection/deadline corrections have offline tests only.

Rubric: R relevance, T technical correctness, L interview likelihood, H experience-relative Hard reasoning, E experience appropriateness, C clarity, F follow-up potential; each 0–2. PASS requires R=T=H=E=C=2, L/F≥1 and in-session novelty. An unavailable result is not a question-quality pass.

See [implementation, costs, timing and limitations](phase71-question-construction-results.md). Raw requests, responses, RAG sources, private specifications and review JSON are preserved under `storage/phase71/`.

## Original unseen holdout: 30 configurations

### HF01 — Data Structures · fresher · PASS

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 18.301 s.

A search service tracks recently viewed query IDs with capacity K. Input: K, then operations GET id or VIEW id. GET returns present status; VIEW refreshes recency. At capacity, viewing an existing ID must not evict it; a new ID evicts the least recent. How would you implement get/view so lookup, refresh, and eviction stay O(1) and a repeated ID at capacity is handled correctly?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Constant-time lookup, recency mutation and bounded eviction interact; full-capacity repeat must not evict an unrelated item. Relative Fresher Hard.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [128, 129, 130].

### HF02 — Algorithms · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 5.837 s.

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Half-open interval sweep must handle nested/duplicate intervals and equal end/start times, rather than just name a data structure.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [131, 132, 133].

### HF03 — Object-Oriented Programming · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 3.782 s.

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Separating readers, validation and persistence must preserve identical dry-run errors and avoid partial publication after parse failure.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [134, 135].

### HF04 — SQL · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 61.692 s.

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Return a selected child ID with deterministic ties, eligibility and unmatched parents; a meaningful relative-Hard relational task.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [136, 137].

### HF05 — HTTP · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 6.126 s.

An editor loads a document and its version, then saves a full replacement. Two tabs load version 7; one saves before the other. The server can atomically compare versions and update. How would you design the HTTP save request and response so the stale tab cannot silently overwrite the first save, including its retry after a lost response?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Atomic version enforcement and recovery after a lost save response require a client/server flow; a safe conflict/read-back policy is acceptable without promising exactly-once delivery.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [138, 139, 140].

### HF06 — REST APIs · fresher · PASS

Origin: Provider / compiled specification. Requested Hard; question type: applied. Pipeline elapsed: 6.405 s.

A scheduling API stores each task with title, assignee, and status plus a version number. Input: task id, base version, patch fields, current version. Return updated row id, new version, or conflict. Same field edits conflict; status may only advance. How should the PATCH request and conflict checks be implemented so disjoint field updates can merge, same-field edits never silently overwrite, and a status change only moves forward?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Disjoint-field merging versus same-field conflict and monotonic status require server conflict metadata or an improved request contract. It asks for that design, so the candidate may propose per-field versions/base values.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [141, 142, 143].

### HF07 — Git · fresher · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 6.142 s.

In a shared Git branch, commit A adds a parser helper, B depends on it, and C only fixes a typo. History is shared; A,B,C are consecutive commits. B’s feature and C’s typo fix still exist afterward. Undoing A must not rewrite shared history. How would you undo only A’s faulty behavior without removing B’s intended feature or C, while keeping shared history auditable?

Scores: R=2, T=2, L=2, H=1, E=2, C=2, F=2. Novel: True.

A/B/C dependencies are named but the faulty behavior is unspecified. Generic revert/compatibility-patch/test advice largely answers it; insufficient concrete reasoning for the requested tier.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [144, 145, 146].

### HF08 — Testing · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 6.910 s.

A cache write schedules expiry at t+60. A refresh creates a new generation and timer, but the old timer may still fire; at age >=60 the current generation expires. How would you build a deterministic test that proves an old expiry cannot delete the refreshed generation and the new one expires at its own boundary, without sleeps?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

A deterministic stale-expiry/refreshed-generation schedule and an exact >=TTL oracle must detect incorrect state deletion, not just mock a clock.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [147, 148, 149].

### HF09 — Debugging · fresher · PASS

Origin: Provider / compiled specification. Requested Hard; question type: applied. Pipeline elapsed: 6.427 s.

A Java service returns mixed responses for different users after a deploy. Compare: Cache key omits the user id. versus Handler keeps mutable fields across requests.. Use two users, same path, different payloads; then repeat with unique paths and fixed payloads. Logging may change timing; causes may coexist and must be separated by predictions. Distinguish the causes with a bounded experiment. How would you design one isolation test and the fix to distinguish cache-key collisions from shared mutable handler state?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Controlled paths/users and overlapping requests allow different predictions for cache-key collision versus shared state; a bounded practical debugging task.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [150, 151, 152].

### HF10 — Security Fundamentals · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 5.640 s.

Mira can edit a shared note until its grant is revoked; its owner retains edit access. An edit can read the old permission, then revocation can commit before the edit writes. Both policy and note live in one database. How would you make authorization plus mutation atomic so an edit ordered after revocation cannot commit, and construct a test for that interleaving without denying the owner's edit?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Permission-check/write races with revocation demand coordinated commit ordering while preserving owner access; a live membership predicate alone is insufficient.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [153, 154, 155].

### HF11 — Data Structures · fresher · FAIL

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 5.826 s.

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: False.

Individually valid recency/eviction task, but it repeats HF01 under new nouns. The pre-fix fallback path missed semantic family coverage.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [156, 157, 158].

### HF12 — Algorithms · fresher · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: applied. Pipeline elapsed: 5.724 s.

A coworking desk system stores unsorted busy intervals for one room; some extend outside office hours, overlap, nest, or just touch. Input: open, close, k, and unsorted busy [start,end) intervals. Return the earliest free [s,e) with e-s>=k, or none. Touching intervals do not block a free slot. How would you find the earliest free slot of length k inside [open, close) without checking every minute?

Scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1. Novel: True.

Touching busy intervals leave no positive gap, whereas a candidate slot may touch a busy endpoint. The unqualified touching rule is ambiguous; >=k output versus a length-k ask also needs reconciliation.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [159, 160, 161].

### HF13 — SQL · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 3.797 s.

Tables: users(id PK), posts(id PK,user_id), likes(id PK,user_id). Return every user with their post count and received-like-record count, including zero for each missing child set. A user can have several rows in both child tables. How would you write the query without multiplying one count by the other, and verify the case with two posts and three like rows?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Two independent child aggregates, empty parents and a concrete 2-by-3 multiplication counterexample make the desired query behavior observable.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [162, 163].

### HF14 — Object-Oriented Programming · fresher · PASS

Origin: Provider / compiled specification. Requested Hard; question type: gap_probe. Pipeline elapsed: 7.977 s.

A report exporter can swap between plain and encrypted writers while building a file privately, then publishing it atomically. A successful publish replaces the old file whole; cancellation preserves the last readable file. Caller creates a writer, writes chunks, then either publish() or cancel(). After cancel or mid-write failure, no partial new content is observable. How would you design the writer API and state flow so cancellation after any chunk leaves the previous published file readable, while a failed swap never exposes partial new content?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

A writer lifecycle must stage privately, preserve the previous readable file and handle cancellation/failure before atomic publication; distinct from input-validation/dry-run orchestration.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [164, 165, 166].

### HF15 — Security Fundamentals · fresher · FAIL

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 7.769 s.

A shared-note user can write while their grant is ACTIVE, then is changed to READ_ONLY but remains allowed to read. Login tokens may contain the old role. After the role change commits, how would you enforce and test that their next write fails while reads and the owner's writes still succeed, including replay of an earlier update request?

Scores: R=2, T=2, L=2, H=1, E=2, C=2, F=2. Novel: False.

The narrower current-role predicate is shallower and revisits the authorization transition already tested more strongly in HF10. Failed depth and session novelty.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [167, 168, 169].

### HE01 — Data Structures · experienced · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 7.690 s.

A search service replays query events after crashes; each event has a durable event_id, user_id, query, and expires_at. Input is a stream of events with event_id, user_id, query, expires_at. Replayed event_ids must not re-run while unexpired. Expired IDs may be processed again; false positives are not allowed. How would you design the deduplication state so replayed events are processed once, retention stays bounded, and expired IDs do not cause false drops?

Scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1. Novel: True.

Processed once is not scoped to a defined observable processing effect or atomic boundary. Durable ID retention alone cannot establish end-to-end processing semantics across a crash.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [170, 171, 172].

### HE02 — Algorithms · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 6.247 s.

An in-memory search index has 10 million timestamped records, 100 range reads per second and 10,000 inserts per second in one-minute bursts. Results must include acknowledged inserts, and queries may return many records. How would you choose and implement an indexing strategy rather than just compare Big-O, accounting for update cost, locality and merge work?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Acknowledged visibility, burst inserts, range output cost and bounded index memory require an implementation choice beyond a complexity table.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [173, 174, 175].

### HE03 — Object-Oriented Programming · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 5.890 s.

A parser reads from seekable files or non-seekable network streams. It needs at most 64 KB of lookahead, may roll back an incomplete header, and must release resources on cancellation. How would you design the reader objects and caller workflow so retrying a parse does not consume bytes twice or leak a stream, without buffering the whole file?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Seekable and streaming inputs need bounded rollback ownership, retained lookahead and cancellation-safe resource handling; no arbitrary universal-seek promise.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [176, 177, 178].

### HE04 — SQL · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 8.243 s.

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Overlapping all-or-none reservations, lock/retry ordering and committed-only confirmation work require a coherent transaction and effect boundary.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [179, 180, 181].

### HE05 — HTTP · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 6.529 s.

A file-import POST can finish importing after the client times out. The server stores request keys and jobs in one database transaction; clients may retry concurrently with the same key but different bodies. How would you define and implement the retry contract, including a response lost after commit?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Concurrent same-key requests, payload mismatch and lost-after-commit recovery require durable claiming/result state; no unsupported external exactly-once promise.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [182, 183, 184].

### HE06 — REST APIs · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 5.921 s.

An activity API promises a snapshot of the items visible when page one is requested, sorted by (created_at, id). Inserts and deletions continue during paging, and storing a full result per client is too costly. How would you implement a bounded-lifetime cursor contract without silently promising consistency that your storage cannot provide?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Snapshot traversal through deletion requires retained/as-of backing state or a justified contract change, not a watermark cursor alone.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [185, 186, 187].

### HE07 — Git · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 6.603 s.

A deployed merge changed both code and a data format. The migration cannot be reversed and the previous binary cannot read the new format; the shared branch has subsequent unrelated fixes. How would you plan a verifiable forward recovery using Git without treating a code revert as a data rollback?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Irreversible migrated data and unrelated good fixes rule out a blind binary/code rollback; recovery must preserve history and read compatibility.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [188, 189, 190].

### HE08 — Testing · experienced · PASS

Origin: Provider / compiled specification. Requested Hard; question type: gap_probe. Pipeline elapsed: 5.485 s.

A feature refresh swaps search generations while imports and reads continue. Input has generation, item_id, acknowledged_at, and refresh_id. After restart, acknowledged inserts remain visible exactly once. No sleep-based timing; barriers must force both commit and refresh boundaries. How would you build deterministic tests that expose lost acknowledged inserts or mixed-generation reads without sleeps?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Deterministic generation-swap barriers and independent acknowledged-insert/mixed-generation oracles test a meaningful concurrency boundary.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [191, 192, 193].

### HE09 — Debugging · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 6.760 s.

After a release, p99 latency triples while median latency, CPU and database query duration stay flat. Traces show the extra time before acquiring a database connection, and active connections remain at the pool limit after requests finish. How would you discriminate a leak from longer legitimate connection ownership using a safe experiment before choosing a mitigation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Pool evidence plus competing leak/ownership explanations require a bounded falsifiable intervention and predicted observations.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [194, 195, 196].

### HE10 — Security Fundamentals · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 5.791 s.

A report export runs asynchronously and can be downloaded through a cached sharing link. Access must be revoked within 30 seconds of team removal even if the export was queued earlier. How would you enforce this contract across the job, download authorization and cache without assuming an expiring URL alone provides timely revocation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

The stated 30-second revocation bound crosses queued work, cache/link policy and download authorization; the implementation must enforce the actual bound.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [197, 198, 199].

### HE11 — Data Structures · experienced · FAIL

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 6.581 s.

A messaging consumer deduplicates event IDs for 24 hours at 50,000 events/second, but cannot keep the full window in RAM. Replays can arrive after restart and false positives would lose messages. How would you structure durable state and memory acceleration so a crash cannot mark an unprocessed event complete?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: False.

The memory/rate constraint adds scale, but the replay/retention/durable-dedup core repeats HE01 as a primary question. It would be more appropriate as a targeted follow-up.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [200, 201, 202].

### HE12 — Algorithms · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 5.926 s.

An input larger than RAM contains highly skewed word frequencies. Return the exact top k words, breaking count ties lexicographically, with bounded memory and limited disk passes. How would you choose a partition/merge strategy and handle a single hot partition without silently switching to approximate counts?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Exact external-memory top-k under skew, disk-pass and tie constraints requires a robust partition/merge design, not approximate streaming counts.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [203, 204, 205].

### HE13 — SQL · experienced · FAIL

Origin: Reviewed fallback. Requested Hard; question type: conceptual. Pipeline elapsed: 7.418 s.

A reservation request has a durable request ID and several item quantities. Concurrent requests overlap, and deadlocks may force full transaction retries; confirmation delivery uses an at-least-once worker. How would you atomically prevent negative stock, deduplicate the reservation and create recoverable confirmation work without charging a remote service inside the retry loop?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: False.

Request identity adds a useful extension, but the same reservation/retry/outbox workflow repeats HE04. The coverage policy now groups these cards into one family.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [206, 207, 208].

### HE14 — Object-Oriented Programming · experienced · PASS

Origin: Reviewed fallback. Requested Hard; question type: gap_probe. Pipeline elapsed: 5.691 s.

A plugin pipeline acquires a stream, a temporary writer and a result handle in stages. Any stage can fail or be canceled; only a complete result may become visible, and cleanup must run exactly once per acquired resource. How would you design ownership and composition so adding a plugin cannot bypass cleanup or publish a partial result, including retry after cancellation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Plugin acquisition, cancellation, cleanup ownership and atomic result publication require a concrete composable lifecycle.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [209, 210, 211].

### HE15 — Security Fundamentals · experienced · FAIL

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 5.914 s.

An export job was authorized for a tenant user when queued, but that user's access is revoked before execution. The worker itself has broad service privileges and results are cached. How would you bind and recheck the original principal, resource and policy at execution and publication so worker credentials cannot bypass revocation, including a revocation during generation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: False.

Queued export principal revocation/publication was already inside the broader HE10 boundary; this repeats a subset of that primary task.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [212, 213, 214].

## Separate seeded-history check: 10 configurations

### NEW01 — Data Structures · fresher · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: applied. Pipeline elapsed: 6.948 s.

A collaborative editor keeps a temporary action stack for one user. Operations: push(x), pop(), max(), undo(). max() returns the current maximum after every step. Duplicate maxima and undo after a pop must be handled correctly. How would you implement push, pop, max, and undo so duplicate maxima stay correct?

Scores: R=2, T=2, L=2, H=1, E=2, C=1, F=1. Novel: True.

No time/space target prevents a simple full-snapshot implementation. The meaning of undo after a non-mutating max operation and empty-state behavior is also unspecified.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [215, 216, 217].

### NEW02 — Data Structures · experienced · PASS

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 5.817 s.

A collaboration service stores per-document edits with a short replay window and concurrent cache refreshes. Each document ID has one active generation and optional tombstone. Only the newest generation may become visible. Expired or deleted generations must not reappear. How would you implement state updates so an older in-flight load cannot overwrite a newer edit or revive a deleted generation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Generation/tombstone checks must prevent stale load publication and deletion resurrection under overlapping updates; distinct from the seeded replay-dedup task.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [218, 219, 220].

### NEW03 — Algorithms · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 4.802 s.

Event timestamps are sorted and duplicates represent different events. Unsorted half-open query windows may overlap or nest. Count events covered by any window exactly once, without rescanning every event per window; empty windows contribute nothing. How would you combine the windows and event boundaries so events at a window's end are excluded but duplicate events inside it all count?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Counting events under the union of overlapping windows integrates interval reasoning with duplicate timestamp entries and event-boundary counting; distinct from seeded peak overlap.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [221, 222, 223].

### NEW04 — SQL · experienced · NOT RETURNED

Origin: UNAVAILABLE. Requested Hard; question type: conceptual. Pipeline elapsed: 7.351 s.

No returned question. The screened draft leaves the snapshot-day relationship for eligible edits versus hourly aggregates insufficiently explicit. Do not call its unavailability a successful Hard question.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [224, 225, 226].

### NEW05 — Object-Oriented Programming · fresher · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: applied. Pipeline elapsed: 7.068 s.

A note exporter stages edits privately, then publishes them as one visible snapshot. Publish is atomic: readers see either the old snapshot or the full new one. Caller edits a draft, may cancel mid-way, then either publish or discard. If publish fails halfway, the previous visible content remains readable. One object may both buffer and expose live content directly. How would you design the objects and method flow so a cancelled publish never exposes a partial snapshot?

Scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1. Novel: True.

The compiler emitted an unavailable-capability description without identifying it as unavailable, making the staged/private versus live-buffer promise misleading. Projection fixed afterward; this observed text is not relabelled.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [227, 228, 229].

### NEW06 — Object-Oriented Programming · experienced · FAIL

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 6.325 s.

A document importer runs plugins that reserve, transform, and publish assets; any stage may fail or be canceled. Publish happens only after all stages succeed; partial results stay hidden. Callers start a run, execute stages, then either commit publication or cancel cleanup. Timeouts must expose created, already-published, canceled, or unknown outcomes. A single always-successful publish method for every plugin. How would you design the plugin interfaces and caller workflow so no partial asset is published, cleanup is composable, and a retry can safely distinguish a completed run from an unknown timeout?

Scores: R=2, T=0, L=2, H=2, E=2, C=0, F=0. Novel: True.

The rendered always-successful publish fragment contradicts failure/cancellation and unknown outcomes. Its internal unavailable-capability qualifier was lost. This critical projection defect was fixed and replay-tested offline; observed failure remains counted.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [230, 231, 232].

### NEW07 — Security Fundamentals · fresher · NOT RETURNED

Origin: UNAVAILABLE. Requested Hard; question type: applied. Pipeline elapsed: 1.217 s.

Explicit coverage exhaustion before generation; no returned question and no fabricated success.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [233].

### NEW08 — Security Fundamentals · experienced · NOT RETURNED

Origin: UNAVAILABLE. Requested Hard; question type: conceptual. Pipeline elapsed: 1.055 s.

Explicit coverage exhaustion before generation; no returned question and no fabricated success.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [234].

### NEW09 — HTTP · fresher · PASS

Origin: Reviewed fallback. Requested Hard; question type: applied. Pipeline elapsed: 6.014 s.

POST /tasks accepts a retry key scoped to the logged-in user. Two identical retries may race; a changed body with the same key must conflict, and a response can be lost after commit. Tasks and keys share one database transaction. How would you implement the key claim and result lookup so the client gets one task ID rather than two tasks or an incorrect conflict after its own successful commit?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Atomic principal-scoped create-key claim, payload conflicts and lost-response result lookup are a new HTTP competency relative to the seeded versioned edit.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [235, 236, 237].

### NEW10 — Testing · experienced · PASS

Origin: Provider / compiled specification. Requested Hard; question type: conceptual. Pipeline elapsed: 5.303 s.

A collaboration service refreshes an index generation while writes and reads continue. Writes may commit during refresh; reads continue concurrently. After restart, every acknowledged insert is visible once with one generation tag. No sleep-based timing; the same row must not appear from two generations. How would you design deterministic tests that expose acknowledged inserts lost on generation swap or mixed-generation reads?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2. Novel: True.

Index generation publication needs deterministic write/read interleavings and durable oracles; distinct from the seeded message/outbox delivery boundary.

Evidence: `postfix-results.json`, `postfix-agent-review.json`; request IDs [238, 239, 240].

## All semantically screened holdout/check drafts

Includes rejected drafts, not only successful returned questions. Technical contract failures that never reached the semantic screen appear in the following section. A false accept/reject compares the model with agent review, not human truth.

### holdout HF01 — screen request 130

A search service tracks recently viewed query IDs with capacity K. Input: K, then operations GET id or VIEW id. GET returns present status; VIEW refreshes recency. At capacity, viewing an existing ID must not evict it; a new ID evicts the least recent. How would you implement get/view so lookup, refresh, and eviction stay O(1) and a repeated ID at capacity is handled correctly?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Integrated O(1) recency/eviction invariant.

Model rationale: Single bounded SWE/data-structure task; premise is coherent and interview-plausible. It asks for O(1) lookup/refresh/eviction with an explicit repeat-at-capacity edge case, which requires interacting invariants rather than a definition. The contract is focused and supports follow-up tracing.

### holdout HF02 — screen request 133

A collaboration tool logs sorted message timestamps, and analysts attach unsorted overlapping [a,b) review windows. Inputs: sorted timestamps with duplicates; windows may overlap or nest. Count every covered timestamp once, even if many windows include it. Touching endpoints do not overlap; empty [a,a) windows cover nothing. How would you count each message timestamp covered by any window exactly once without rescanning all messages for every window?

Model: REJECT; agent: PASS.

Model scores: R=2, T=2, L=2, H=1, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Union-of-windows counting is more than a lone lower-bound query.

Model rationale: Core task is a standard interval-union count over sorted data. It has one main decision (merge windows vs sweep/scan) and one edge rule (half-open, empty windows), but no strong interacting constraints beyond routine boundary handling.

### holdout HF05 — screen request 140

A messaging API creates one durable draft message per send request. POST /drafts creates a durable draft message. Effects: Persist one draft record; Emit one delivery-attempt log entry. Client-supplied key plus principal id Scoped to the same authenticated principal Return conflict; do not create a second draft Concurrent same-key requests resolve to one stored draft; lost-response retry returns the existing outcome Exactly one durable draft per principal, key, and payload How would you implement the send endpoint so retries and races create at most one draft per principal and payload?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Key-scoped versus principal/payload-scoped uniqueness and the secondary delivery log effect are not coherently bounded.

Model rationale: The prompt is a fresher HTTP/backend correctness question about one durable draft per principal+key+payload under concurrent retries. It has a concrete contract, one main implementation task, and a meaningful race/duplicate edge case. Compared with the nearest earlier idempotency/retry review, this is novel in the session.

### holdout HF06 — screen request 143

A scheduling API stores each task with title, assignee, and status plus a version number. Input: task id, base version, patch fields, current version. Return updated row id, new version, or conflict. Same field edits conflict; status may only advance. How should the PATCH request and conflict checks be implemented so disjoint field updates can merge, same-field edits never silently overwrite, and a status change only moves forward?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Meaningful field-level conflict/merge design under a monotonic status rule.

Model rationale: Directly relevant REST update-contract question. It has a concrete bounded implementation task with interacting constraints: sparse patching, version-based conflict detection, field-level merge rules, and monotonic status transitions. It is fresher-level, plausible, and supports follow-up on retries, partial failures, and status transition policy.

### holdout HF07 — screen request 146

In a shared Git branch, commit A adds a parser helper, B depends on it, and C only fixes a typo. History is shared; A,B,C are consecutive commits. B’s feature and C’s typo fix still exist afterward. Undoing A must not rewrite shared history. How would you undo only A’s faulty behavior without removing B’s intended feature or C, while keeping shared history auditable?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=1, E=2, C=2, F=2; novel=True.

Faulty behavior remains generic; dependency names alone do not establish Hard depth.

Model rationale: Single bounded Git recovery task. It is directly SWE-relevant, plausible, and asks for a concrete safe sequence under shared-history and dependency constraints. The main tricky point is that undoing A must not break B, so the answer needs reasoning about inverse effects and verification rather than a named command alone.

### holdout HF08 — screen request 149

A search UI sends query requests q1 then q2; q1 may finish after q2. Each query has a request id and text; responses may arrive out of order. Only the latest issued query may update visible results. A canceled earlier request finishing later must be ignored. How would you implement the test oracle and state update so only the latest query can change visible results?

Model: REJECT; agent: PASS.

Model scores: R=2, T=1, L=2, H=1, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Deferred out-of-order completion and cancellation require a concrete observable async test oracle.

Model rationale: Single bounded SWE test-oracle/state-update problem with concrete race/out-of-order constraint; no bundled second task. The prompt is clear enough, but the exact cancellation semantics for the latest query are slightly implied rather than fully spelled out.

### holdout HF09 — screen request 152

A Java service returns mixed responses for different users after a deploy. Compare: Cache key omits the user id. versus Handler keeps mutable fields across requests.. Use two users, same path, different payloads; then repeat with unique paths and fixed payloads. Logging may change timing; causes may coexist and must be separated by predictions. Distinguish the causes with a bounded experiment. How would you design one isolation test and the fix to distinguish cache-key collisions from shared mutable handler state?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Two controlled hypotheses and a causal isolation experiment.

Model rationale: The prompt is a bounded debugging task for a fresher. It has two plausible hypotheses, a concrete experiment with predicted outcomes, and a single primary decision: distinguish cache-key collisions from shared mutable handler state. The contracts are coherent and interview-plausible.

### holdout HF10 — screen request 155

An e-commerce listing service lets an ACTIVE writer edit product descriptions, then a moderator may downgrade that writer to READ_ONLY while reads stay allowed. writer can write product_description before this change: writer is downgraded to READ_ONLY after initial check Afterward that action must be denied. Server-side check at the resource update boundary. Authorization must be revalidated against the latest role before commit. How would you implement the edit path so a write that passed its first check cannot commit after the downgrade, while owner writes still work?

Model: REJECT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Atomic authorization/mutation commit ordering is nontrivial relative fresher reasoning.

Model rationale: Concrete boundary: an ACTIVE writer is downgraded to READ_ONLY after the first check; the task is to prevent commit using latest role and preserve owner writes. This is a bounded server-side authorization race, plausible for SWE interview, with a clear testable outcome and follow-up space.

### holdout HF11 — screen request 158

A note app keeps undoable edits on one stack; each edit is a signed integer. Operations arrive in order: PUSH x, POP, MAX, UNDO. Popped values may be negative. MAX returns the current maximum after each step; UNDO restores the exact prior state. Duplicate maxima and empty-stack undo must be handled explicitly. How would you implement push, pop, current_max, and undo so duplicate maxima stay correct after any trace?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=1, E=2, C=1, F=1; novel=True.

Undo/empty behavior and performance constraints are insufficiently specified.

Model rationale: The prompt is a focused fresher DS implementation with one main task, explicit edge cases, and interacting invariants (max tracking plus exact undo). It is clear, interview-plausible, and admits multiple standard solutions; the empty-undo contract is the only minor underspecification.

### holdout HF12 — screen request 161

A coworking desk system stores unsorted busy intervals for one room; some extend outside office hours, overlap, nest, or just touch. Input: open, close, k, and unsorted busy [start,end) intervals. Return the earliest free [s,e) with e-s>=k, or none. Touching intervals do not block a free slot. How would you find the earliest free slot of length k inside [open, close) without checking every minute?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Ambiguous touching-interval rule and requested slot length.

Model rationale: One primary task, bounded fresher algorithms problem. The edge cases are real and observable because the returned slot depends on clipping and whether touching intervals block. Requires merging unsorted intervals before scanning gaps; not just a routine lower-bound or single overlap check.

### holdout HF14 — screen request 166

A report exporter can swap between plain and encrypted writers while building a file privately, then publishing it atomically. A successful publish replaces the old file whole; cancellation preserves the last readable file. Caller creates a writer, writes chunks, then either publish() or cancel(). After cancel or mid-write failure, no partial new content is observable. How would you design the writer API and state flow so cancellation after any chunk leaves the previous published file readable, while a failed swap never exposes partial new content?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Concrete publication/cancellation object lifecycle.

Model rationale: The prompt is a focused fresher OOP design around atomic publish/cancel and no-partial-read visibility after mid-write failure. It is technically coherent, interview-plausible, and asks for a concrete API/state-flow decision with meaningful edge-case reasoning. It is novel relative to the prior questions.

### holdout HF15 — screen request 169

A note editor and the owner share one database. editor can write note before this change: Grant revoked after authorization read but before write commit. Afterward that action must be denied. Server-side policy check and note mutation in one transaction. A write ordered after revocation must fail; earlier committed writes and owner writes stay valid. How would you make the write and permission check atomic so a write started before revocation cannot commit after it, while the owner still writes successfully?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=False.

Individually coherent but repeats the earlier atomic authorization transition.

Model rationale: Directly about SWE security/transactions. Contract is mostly clear and bounded, but the phrase 'make the write and permission check atomic' leaves multiple valid implementation approaches. It is a plausible fresher interview problem with a concrete interleaving edge case and testability. Distinct from prior questions in this session because no earlier prompt asks exactly about owner-vs-revoked shared note writes with commit-time revocation.

### holdout HE01 — screen request 172

A search service replays query events after crashes; each event has a durable event_id, user_id, query, and expires_at. Input is a stream of events with event_id, user_id, query, expires_at. Replayed event_ids must not re-run while unexpired. Expired IDs may be processed again; false positives are not allowed. How would you design the deduplication state so replayed events are processed once, retention stays bounded, and expired IDs do not cause false drops?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Processing effect and crash atomic boundary are unspecified.

Model rationale: Concrete SWE data-structure task with one primary decision: dedupe replayed events under TTL while keeping retention bounded. It has interacting constraints (crash replay, no false positives, reprocessing after expiry) and supports bounded implementation/failure follow-up. The prompt is coherent and interview-plausible.

### holdout HE02 — screen request 175

A collaboration feed ingests a one-day activity log larger than RAM. Input rows: action_id, actor_id, event_time. Every row is valid. Output up to k rows: rank, actor_id, total_actions. Equal counts break by smaller actor_id. How would you compute the exact top-k actor IDs by action count with deterministic ties and bounded memory?

Model: REJECT; agent: PASS.

Model scores: R=2, T=1, L=2, H=1, E=1, C=1, F=1; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Exact bounded-memory ranking requires an external algorithm and deterministic tie handling.

Model rationale: The prompt is a plausible bounded interview task, but as written exact top-k over an unbounded distinct set with bounded memory is underspecified unless external storage or multi-pass partitioning is allowed. It is technically coherent but not fully pinned down on the exact memory model or whether spill/sort is permitted.

### holdout HE03 — screen request 178

A document reader must support seekable files and live network streams. Bounded lookahead and rollback for partial headers. Caller may parse, cancel, then resume or discard safely. Cancellation after partial read must leave a recoverable state. Universal rollback on all backends. How would you design the reader interfaces and caller workflow so bounded lookahead and rollback work after partial headers, while cancellation keeps ownership and recovery clear?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=1, E=1, C=1, F=1; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Universal rollback fragment loses its unavailable qualifier and conflicts with bounded streaming rollback.

Model rationale: This is role-relevant OOP design, but the prompt is compact and mostly names desired properties. It has one main task and a plausible edge case, yet the constraints are not rich enough to force multi-step trade-off reasoning; 'universal rollback on all backends' is stated rather than challenged. The nearby history is a different problem space, so it is novel.

### holdout HE04 — screen request 181

An analytics dashboard shows the current approved plan per account plus monthly spend totals. Tables: accounts(account_id, status; PK account_id); plans(plan_id, account_id, state, effective_at, created_at, name; PK plan_id); spend_events(event_id, account_id, posted_at, amount; PK event_id). One result row per plans.plan_id. Return: account_id: Active account identifier.; plan_id: Selected latest eligible plan row ID.; plan_name: Name from the selected plan row.; month_spend: Sum of posted spend in the current month.. Include active accounts only. Eligible plan rows have state='approved' and effective_at <= current date. Spend is from the current calendar month in one snapshot. If an account has no eligible plan, return no row for it. If no spend rows exist, month_spend is 0. Choose the latest eligible plan per account by effective_at desc, then created_at desc, then plan_id desc. Aggregate spend independently by account over the month; keep both results aligned by account_id. How would you write one SQL query that returns each active account’s latest eligible approved plan row and its month-to-date spend under one snapshot?

Model: REJECT; agent: PASS.

Model scores: R=2, T=2, L=2, H=1, E=1, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Explicit eligible-plan selection, independent monthly sum and no-plan policy are coherent; a query must preserve the selected identity.

Model rationale: One focused SQL task with clear tables, output columns, and deterministic tie-break plus independent monthly aggregate. It is implementation-level and interview-plausible, but not especially deep beyond combining standard selection and aggregation correctly.

### holdout HE05 — screen request 184

A messaging import POST may timeout after commit; retries can race with the original call. POST /imports creates one durable import job and claims a key. Effects: Persist a job record.; Start exactly one downstream import attempt.. Idempotency key plus authenticated principal. Key is scoped to the authenticated principal and operation. Reject as a conflict when the payload hash differs. Concurrent identical retries converge to one job; a lost response returns the stable pending or completed result. HTTP retry handling is idempotent; downstream side effects need separate reconciliation. How would you implement the server-side retry contract and atomic state machine?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Exactly-one downstream attempt is not reconciled with the separate external-effect guarantee boundary.

Model rationale: Concrete, bounded HTTP backend contract with atomic claim and recovery. However, parts like ‘HTTP retry handling is idempotent’ and ‘downstream side effects need separate reconciliation’ blur the exact observable contract, so the prompt is mostly clear but not perfectly tight.

### holdout HE06 — screen request 187

A feed endpoint returns versioned item changes with tombstones; page-one must be a stable snapshot. Changes have change_id, item_id, created_at, deleted_at, payload. Requests include filter, opaque cursor, page_size. Pages never repeat or skip within one contract; tombstones are visible. Cursor expires after ten minutes; deleted rows and reordering may occur after page one. How would you implement a bounded resync contract when the cursor expires after ten minutes?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=1, F=1; novel=True.

Blends snapshot paging and expired-cursor resync without a sufficiently precise retention/continuation contract.

Model rationale: The prompt is a bounded REST pagination contract with tombstones, cursor expiry, and post-page-one reordering/deletes. It asks for one implementation decision, but the exact recovery semantics after expiry are underspecified: whether to preserve the old snapshot, resume from a checkpoint, or force a new snapshot is not fixed.

### holdout HE07 — screen request 190

A deployment merged a bad feature branch, then a migration rewrote on-disk metadata format; afterward a small follow-up fix landed on main. Git history is shared; commits and merge parents are visible. Recovery must preserve the good fix and auditable history. Old binaries cannot read the migrated format safely. How would you recover main so production can read both old and migrated data without losing the fix or requiring an unsafe old-binary redeploy?

Model: REJECT; agent: PASS.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Data compatibility and preserved fixes constrain the recovery sequence.

Model rationale: The prompt asks for a concrete recovery sequence under shared history, merge parents, and a format migration that breaks old binaries. That is a bounded SWE/Git recovery problem with a real compatibility trade-off. It is mostly clear and interview-plausible, but the exact acceptable recovery mechanism is underspecified, and the observable contract depends on whether the migrated data can be made readable before preserving the fix.

### holdout HE08 — screen request 193

A feature refresh swaps search generations while imports and reads continue. Input has generation, item_id, acknowledged_at, and refresh_id. After restart, acknowledged inserts remain visible exactly once. No sleep-based timing; barriers must force both commit and refresh boundaries. How would you build deterministic tests that expose lost acknowledged inserts or mixed-generation reads without sleeps?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Deterministic fault/interleaving tests with durable generation oracles.

Model rationale: Concrete, bounded testing task with specific state fields and no-sleep determinism. It asks for a single implementation-level test strategy under interacting commit/refresh/restart constraints, with clear failure modes.

### holdout HE09 — screen request 196

After a deployment, p99 latency triples while median latency, CPU, and query time stay flat; traces show the pool is saturated. Compare: Connections are leaked on some release paths. versus Transactions legitimately hold connections for too long.. Use a bounded canary with forced cancellations; compare acquisition wait, ownership duration, and release traces before and after. Both hypotheses may coexist; timing changes from logging are allowed, but the experiment must stay bounded and safe. Distinguish the causes with a bounded experiment. How would you distinguish leaked connections from legitimate long-held transactions using per-lease release traces and one bounded canary test?

Model: REJECT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Concrete evidence and bounded intervention distinguish different lease lifecycles.

Model rationale: The prompt asks for one bounded experiment and one diagnosis decision under two competing hypotheses. It is role-relevant, technically sound, interview-plausible, and has clear follow-up room, but the answer space is broad enough that clarity is only moderate.

### holdout HE10 — screen request 199

A warehouse report export is produced by a background job and downloaded through a cached link. original_requester can download report_export before this change: tenant removal revokes access before the cached link is used Afterward that action must be denied. Authorize queue submission, job execution, and download separately. Recheck current principal-resource policy at execution and publication; fail closed if policy data is unavailable. How would you enforce authorization so the original requester stays bound to the export, tenant removal revokes access within 30 seconds, and worker privileges never stand in for user authorization?

Model: REJECT; agent: PASS.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

A testable revocation deadline crosses worker and cache boundaries.

Model rationale: Directly SWE/security-relevant; plausible interview prompt; bounded but requires coordinating multiple authorization boundaries and a revocation window. The wording is somewhat compressed but answerable. It supports follow-up on cache invalidation, policy source failure, and worker/user identity separation.

### holdout HE11 — screen request 202

A search service replays events after crashes. Each event has event_id, query_id, expires_at, and payload. The stream is larger than RAM, and expired IDs may be processed again. Input is an append-only event stream. Replayed unexpired event_ids are skipped once. Expired IDs may be processed again; false positives are forbidden. How would you implement bounded deduplication state so replayed event_ids are suppressed before expiry, survive crash/restart, and never false-drop a non-duplicate?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=False.

Repeats the already asked durable replay/retention task.

Model rationale: Direct SWE data-structures / storage-state design. Contract is mostly coherent and bounded, but it is underspecified about the exact recovery mechanism and what “processed” means beyond dedup suppression. It’s a plausible interview prompt with an implementation-level trade-off, and the prior session question is meaningfully different enough in task framing.

### holdout HE12 — screen request 205

A collaboration index must report the top tags from a 12 TB event log on disk; RAM holds only 2 GB, inserts arrive in hourly bursts, and exact counts with deterministic ties are required. Input is a stream of (tag_id, event_id); duplicates are possible. Output exact counts for the top k tag_ids and their result row_identity. Ties break by smaller tag_id; if fewer than k tags exist, return all. How would you implement the bounded-memory top-k computation and tie-breaking so burst writes and skewed tags do not break correctness?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=1, E=1, C=1, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Duplicate event IDs have undefined count semantics and result row_identity is not defined for this stream output.

Model rationale: The prompt is interview-plausible and SWE-relevant, but it is underspecified on what row_identity means and how much external memory/disk I/O is allowed. It asks for one bounded implementation decision under skew/bursts, which is reasonable, but the core reasoning is mostly routine streaming aggregation unless row_identity has specific semantics.

### holdout HE13 — screen request 208

A photo-storage service reserves multiple files atomically for a restore job while retries and deadlocks occur. Tables: restore_job(job_id, principal_id, request_token, created_at; PK job_id); file_reservation(file_id, job_id, reserved_at; PK file_id); outbox(outbox_id, job_id, event_type, sent_at; PK outbox_id). One result row per restore_job.job_id. Return: reserved_job_id: Committed restore job row for the request.; reserved_file_id: Each file actually claimed by the job.; outbox_job_id: Outbox record tied to the committed job.. Only active jobs and current reservations matter; retries may reuse the same request_token for one principal. Missing reservations mean the job failed and no file was claimed; NULL sent_at means unsent outbox row. Return one row per claimed file and one outbox row per committed job; do not count partial claims as success. How would you implement the reservation transaction and retry boundary so each job either reserves every requested file or none, avoids duplicate side effects, and still behaves correctly under overlapping requests?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=0, L=2, H=2, E=2, C=0, F=0; novel=True.

Declared one-row-per-job grain conflicts with one-row-per-file output and active-job eligibility lacks a defined status.

Model rationale: The prompt is about SQL transaction/retry correctness for atomic reservation and duplicate side effects. It is plausible and interview-like, but the contract is under-specified on the actual requested-file source and exact committed-job lookup semantics. It has meaningful edge-case reasoning, yet the observable task is not fully pinned down.

### holdout HE14 — screen request 211

An analytics plugin pipeline acquires a cache, a file handle, then a publish token; any stage may fail or be canceled. No partial result is observable before publish succeeds. Caller may retry after timeout using the same operation identity. Canceled or failed stages must be cleaned up deterministically. Universal create-and-publish success across all plugins. How would you design the interfaces and caller workflow so no partial result becomes visible, retries are safe after timeout, and cleanup runs for every acquired stage?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=0, L=2, H=2, E=2, C=0, F=0; novel=True.

Unavailable universal publish success was projected as an unqualified promise.

Model rationale: Core asks for one implementation workflow preserving no-partial visibility, safe retries by operation identity, and cleanup over multiple acquired stages. It is a bounded OOP/concurrency contract question, not a generic design-pattern prompt.

### holdout HE15 — screen request 214

A background export for a shared report is downloaded through CDN links and policy caches. team_member can download shared_report_export before this change: Team removal revokes the same principal's download within 30 seconds. Afterward that action must be denied. Authorize queued export creation, job execution, and download. Policy-data misses or stale caches fail closed; CDN and link caches must honor the 30-second revocation window. How would you design the authorization checks and cache invalidation path so team removal revokes one principal's download within 30 seconds?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=False.

Repeats prior export/principal revocation coverage.

Model rationale: SWE-relevant security/authz problem with a concrete boundary workflow. The contract is somewhat underspecified about exact cache primitives and invalidation mechanics, but the core task is clear and testable. It is plausibly interviewable and supports follow-up on race timing, fallback checks, and cache propagation.

### postfix NEW01 — screen request 217

A collaborative editor keeps a temporary action stack for one user. Operations: push(x), pop(), max(), undo(). max() returns the current maximum after every step. Duplicate maxima and undo after a pop must be handled correctly. How would you implement push, pop, max, and undo so duplicate maxima stay correct?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=1, E=2, C=1, F=1; novel=True.

Undo semantics/performance insufficient.

Model rationale: One focused SWE task with interacting invariants and a concrete edge case. The prompt is clear and bounded, and support exists for follow-up probes on undo bookkeeping or alternative max-structure designs.

### postfix NEW02 — screen request 220

A collaboration service stores per-document edits with a short replay window and concurrent cache refreshes. Each document ID has one active generation and optional tombstone. Only the newest generation may become visible. Expired or deleted generations must not reappear. How would you implement state updates so an older in-flight load cannot overwrite a newer edit or revive a deleted generation?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Stale generation/tombstone publication is a new bounded concurrency task.

Model rationale: Single bounded implementation task; concrete interacting constraints are replay window, concurrent refresh, and stale overwrite/deletion revival. It is role-relevant, plausible, and the failure mode invites a concrete recovery/commit workflow rather than a pattern name.

### postfix NEW03 — screen request 223

A collaboration tool stores sorted event timestamps with duplicates and unsorted [a,b) windows. Input: events sorted ascending; windows unsorted; each window has start,end. Output covered event count and each event counted once. Empty or touching windows cover nothing; [a,a) is empty. How would you count each covered timestamp exactly once without rescanning all events per window?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=1, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=0, L=2, H=2, E=2, C=1, F=0; novel=True.

Empty OR touching windows cover nothing incorrectly conflates empty intersections with the nonempty union.

Model rationale: The prompt is a small fresher algorithm problem with two interacting constraints (sorted duplicate events + unsorted half-open windows) and one clear task (count each covered timestamp once). It is interview-plausible and answerable, but the boundary rules are explicit and the reasoning depth is modest rather than hard.

### postfix NEW04 — screen request 226

A collaboration app stores document edits and hourly usage per account under one snapshot. Tables: edits(edit_id, account_id, created_at, status, doc_id; PK edit_id); account_hours(account_id, hour_start, minutes_used; PK account_id,hour_start); accounts(account_id, plan, active; PK account_id). One result row per edits.edit_id. Return: selected_edit_id: selected edits.edit_id; account_id: Account owning the selected edit.; day_minutes_used: Sum of minutes_used for that account on the snapshot day.. Consider only active accounts; eligible edits have status='published'; use one snapshot day. If an account has no eligible edit, return no row for it; missing daily hours are zero. Choose the latest eligible edit per account with stable edit_id tie-break; join daily hours by account_id and snapshot day; aggregate minutes per account. Choose the latest by edits.created_at, edits.edit_id descending; return selected_edit_id. How would you query the latest eligible edit per account, then attach that account's hourly aggregate for the same day, returning the selected edit ID and handling accounts with no eligible edits?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=1, F=1; novel=True.

Snapshot-day eligibility/aggregate scope needs clarification.

Model rationale: Core task is a bounded SQL query under interacting constraints: independent one-to-many daily aggregation without row multiplication and deterministic latest-edit selection. The prompt is mostly coherent, though phrasing is redundant. It is clearly SWE/SQL interview material and not a repeat of the prior retry/transaction question.

### postfix NEW05 — screen request 229

A note exporter stages edits privately, then publishes them as one visible snapshot. Publish is atomic: readers see either the old snapshot or the full new one. Caller edits a draft, may cancel mid-way, then either publish or discard. If publish fails halfway, the previous visible content remains readable. One object may both buffer and expose live content directly. How would you design the objects and method flow so a cancelled publish never exposes a partial snapshot?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Unavailable-capability qualifier lost.

Model rationale: Single focused OOP boundary with atomic publish, cancel/discard, and half-failure visibility is coherent and interview-appropriate. It asks for one implementation flow under interacting invariants, without bundling unrelated tasks or requiring senior design.

### postfix NEW06 — screen request 232

A document importer runs plugins that reserve, transform, and publish assets; any stage may fail or be canceled. Publish happens only after all stages succeed; partial results stay hidden. Callers start a run, execute stages, then either commit publication or cancel cleanup. Timeouts must expose created, already-published, canceled, or unknown outcomes. A single always-successful publish method for every plugin. How would you design the plugin interfaces and caller workflow so no partial asset is published, cleanup is composable, and a retry can safely distinguish a completed run from an unknown timeout?

Model: ACCEPT; agent: FAIL.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=0, L=2, H=2, E=2, C=0, F=0; novel=True.

Always-successful publication contradicts permitted failure states.

Model rationale: Concrete SW boundary with reserve/transform/publish, cancellation, hidden partial results, and timeout outcome distinctions. It is a focused implementation workflow question with interacting constraints and a meaningful edge case; not a repetition of the earlier stream-reader task.

### postfix NEW09 — screen request 237

A collaboration API creates one durable review task per submit. Create a review task from a submit request. Effects: Persist one durable task record.; Notify the reviewer once.. Principal-scoped submit key. Same principal and same task body. Return conflict; do not create a second task. Concurrent same-key submits claim one task; a retry after lost response returns the existing outcome. Guarantee at-most-one durable task per principal and body. How should the submit endpoint handle retries, duplicate claims, and body changes?

Model: REJECT; agent: FAIL.

Model scores: R=2, T=1, L=2, H=1, E=2, C=1, F=2; novel=True.

Agent scores: R=2, T=1, L=2, H=2, E=2, C=1, F=1; novel=True.

Per-key versus per-body uniqueness and exactly-once notification effect are insufficiently bounded.

Model rationale: Focused, bounded fresher HTTP/server contract. It is technically plausible, but the prompt is terse and bundles several behaviors (duplicate claims, retries, body changes) without fully specifying response shape or recovery details. The reasoning demand is modest and close to standard idempotency patterns.

### postfix NEW10 — screen request 240

A collaboration service refreshes an index generation while writes and reads continue. Writes may commit during refresh; reads continue concurrently. After restart, every acknowledged insert is visible once with one generation tag. No sleep-based timing; the same row must not appear from two generations. How would you design deterministic tests that expose acknowledged inserts lost on generation swap or mixed-generation reads?

Model: ACCEPT; agent: PASS.

Model scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

Agent scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; novel=True.

A concrete independent generation-swap oracle is required.

Model rationale: Role-relevant SWE testing. The prompt is focused, but it asks for a test design, not implementation; the premise is coherent and the edge cases are explicit. Depth comes from coordinating refresh/write/read/restart boundaries and checking generation-tag consistency, though it is more implementation-test than production-hard.

## Construction drafts and rejection trace

Every stored construction draft from the 40 evaluated configurations is indexed here, including validation failures and failed/empty responses. Valid candidate projections are reproduced; invalid structured objects and full provider responses remain in the linked JSON evidence rather than being rewritten into invented questions.

### holdout HF01

Construction request 129:

A search service tracks recently viewed query IDs with capacity K. Input: K, then operations GET id or VIEW id. GET returns present status; VIEW refreshes recency. At capacity, viewing an existing ID must not evict it; a new ID evicts the least recent. How would you implement get/view so lookup, refresh, and eviction stay O(1) and a repeated ID at capacity is handled correctly?

Hard construction attempt 1: accepted

### holdout HF02

Construction request 132:

A collaboration tool logs sorted message timestamps, and analysts attach unsorted overlapping [a,b) review windows. Inputs: sorted timestamps with duplicates; windows may overlap or nest. Count every covered timestamp once, even if many windows include it. Touching endpoints do not overlap; empty [a,a) windows cover nothing. How would you count each message timestamp covered by any window exactly once without rescanning all messages for every window?

Hard construction attempt 1: Core task is a standard interval-union count over sorted data. It has one main decision (merge windows vs sweep/scan) and one edge rule (half-open, empty windows), but no strong interacting constraints beyond routine boundary handling.

### holdout HF03

Construction request 135:

No valid candidate projection. See original structured response.

Hard construction attempt 1 rejected: 1 validation error for ProblemSpecification
technical_contract.oop
  Value error, Cannot promise an achievable contract while declaring its capability unavailable [type=value_error, input_value={'kind': 'oop', 'interfac...ffect the same upload.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/value_error

### holdout HF04

No constructed draft (provider failure or explicit coverage exhaustion).

Hard construction provider unavailable: LLMError

### holdout HF05

Construction request 139:

A messaging API creates one durable draft message per send request. POST /drafts creates a durable draft message. Effects: Persist one draft record; Emit one delivery-attempt log entry. Client-supplied key plus principal id Scoped to the same authenticated principal Return conflict; do not create a second draft Concurrent same-key requests resolve to one stored draft; lost-response retry returns the existing outcome Exactly one durable draft per principal, key, and payload How would you implement the send endpoint so retries and races create at most one draft per principal and payload?

Hard construction attempt 1: The prompt is a fresher HTTP/backend correctness question about one durable draft per principal+key+payload under concurrent retries. It has a concrete contract, one main implementation task, and a meaningful race/duplicate edge case. Compared with the nearest earlier idempotency/retry review, this is novel in the session.

### holdout HF06

Construction request 142:

A scheduling API stores each task with title, assignee, and status plus a version number. Input: task id, base version, patch fields, current version. Return updated row id, new version, or conflict. Same field edits conflict; status may only advance. How should the PATCH request and conflict checks be implemented so disjoint field updates can merge, same-field edits never silently overwrite, and a status change only moves forward?

Hard construction attempt 1: accepted

### holdout HF07

Construction request 145:

In a shared Git branch, commit A adds a parser helper, B depends on it, and C only fixes a typo. History is shared; A,B,C are consecutive commits. B’s feature and C’s typo fix still exist afterward. Undoing A must not rewrite shared history. How would you undo only A’s faulty behavior without removing B’s intended feature or C, while keeping shared history auditable?

Hard construction attempt 1: accepted

### holdout HF08

Construction request 148:

A search UI sends query requests q1 then q2; q1 may finish after q2. Each query has a request id and text; responses may arrive out of order. Only the latest issued query may update visible results. A canceled earlier request finishing later must be ignored. How would you implement the test oracle and state update so only the latest query can change visible results?

Hard construction attempt 1: Single bounded SWE test-oracle/state-update problem with concrete race/out-of-order constraint; no bundled second task. The prompt is clear enough, but the exact cancellation semantics for the latest query are slightly implied rather than fully spelled out.

### holdout HF09

Construction request 151:

A Java service returns mixed responses for different users after a deploy. Compare: Cache key omits the user id. versus Handler keeps mutable fields across requests.. Use two users, same path, different payloads; then repeat with unique paths and fixed payloads. Logging may change timing; causes may coexist and must be separated by predictions. Distinguish the causes with a bounded experiment. How would you design one isolation test and the fix to distinguish cache-key collisions from shared mutable handler state?

Hard construction attempt 1: accepted

### holdout HF10

Construction request 154:

An e-commerce listing service lets an ACTIVE writer edit product descriptions, then a moderator may downgrade that writer to READ_ONLY while reads stay allowed. writer can write product_description before this change: writer is downgraded to READ_ONLY after initial check Afterward that action must be denied. Server-side check at the resource update boundary. Authorization must be revalidated against the latest role before commit. How would you implement the edit path so a write that passed its first check cannot commit after the downgrade, while owner writes still work?

Hard construction attempt 1: Concrete boundary: an ACTIVE writer is downgraded to READ_ONLY after the first check; the task is to prevent commit using latest role and preserve owner writes. This is a bounded server-side authorization race, plausible for SWE interview, with a clear testable outcome and follow-up space.

### holdout HF11

Construction request 157:

A note app keeps undoable edits on one stack; each edit is a signed integer. Operations arrive in order: PUSH x, POP, MAX, UNDO. Popped values may be negative. MAX returns the current maximum after each step; UNDO restores the exact prior state. Duplicate maxima and empty-stack undo must be handled explicitly. How would you implement push, pop, current_max, and undo so duplicate maxima stay correct after any trace?

Hard construction attempt 1: The prompt is a focused fresher DS implementation with one main task, explicit edge cases, and interacting invariants (max tracking plus exact undo). It is clear, interview-plausible, and admits multiple standard solutions; the empty-undo contract is the only minor underspecification.

### holdout HF12

Construction request 160:

A coworking desk system stores unsorted busy intervals for one room; some extend outside office hours, overlap, nest, or just touch. Input: open, close, k, and unsorted busy [start,end) intervals. Return the earliest free [s,e) with e-s>=k, or none. Touching intervals do not block a free slot. How would you find the earliest free slot of length k inside [open, close) without checking every minute?

Hard construction attempt 1: accepted

### holdout HF13

Construction request 163:

No valid candidate projection. See original structured response.

Hard construction attempt 1 rejected: 1 validation error for ProblemSpecification
technical_contract.sql
  Value error, SQL output must include its declared result row identity [type=value_error, input_value={'kind': 'sql', 'tables':...regating their counts.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/value_error

### holdout HF14

Construction request 165:

A report exporter can swap between plain and encrypted writers while building a file privately, then publishing it atomically. A successful publish replaces the old file whole; cancellation preserves the last readable file. Caller creates a writer, writes chunks, then either publish() or cancel(). After cancel or mid-write failure, no partial new content is observable. How would you design the writer API and state flow so cancellation after any chunk leaves the previous published file readable, while a failed swap never exposes partial new content?

Hard construction attempt 1: accepted

### holdout HF15

Construction request 168:

A note editor and the owner share one database. editor can write note before this change: Grant revoked after authorization read but before write commit. Afterward that action must be denied. Server-side policy check and note mutation in one transaction. A write ordered after revocation must fail; earlier committed writes and owner writes stay valid. How would you make the write and permission check atomic so a write started before revocation cannot commit after it, while the owner still writes successfully?

Hard construction attempt 1: Directly about SWE security/transactions. Contract is mostly clear and bounded, but the phrase 'make the write and permission check atomic' leaves multiple valid implementation approaches. It is a plausible fresher interview problem with a concrete interleaving edge case and testability. Distinct from prior questions in this session because no earlier prompt asks exactly about owner-vs-revoked shared note writes with commit-time revocation.

### holdout HE01

Construction request 171:

A search service replays query events after crashes; each event has a durable event_id, user_id, query, and expires_at. Input is a stream of events with event_id, user_id, query, expires_at. Replayed event_ids must not re-run while unexpired. Expired IDs may be processed again; false positives are not allowed. How would you design the deduplication state so replayed events are processed once, retention stays bounded, and expired IDs do not cause false drops?

Hard construction attempt 1: accepted

### holdout HE02

Construction request 174:

A collaboration feed ingests a one-day activity log larger than RAM. Input rows: action_id, actor_id, event_time. Every row is valid. Output up to k rows: rank, actor_id, total_actions. Equal counts break by smaller actor_id. How would you compute the exact top-k actor IDs by action count with deterministic ties and bounded memory?

Hard construction attempt 1: The prompt is a plausible bounded interview task, but as written exact top-k over an unbounded distinct set with bounded memory is underspecified unless external storage or multi-pass partitioning is allowed. It is technically coherent but not fully pinned down on the exact memory model or whether spill/sort is permitted.

### holdout HE03

Construction request 177:

A document reader must support seekable files and live network streams. Bounded lookahead and rollback for partial headers. Caller may parse, cancel, then resume or discard safely. Cancellation after partial read must leave a recoverable state. Universal rollback on all backends. How would you design the reader interfaces and caller workflow so bounded lookahead and rollback work after partial headers, while cancellation keeps ownership and recovery clear?

Hard construction attempt 1: This is role-relevant OOP design, but the prompt is compact and mostly names desired properties. It has one main task and a plausible edge case, yet the constraints are not rich enough to force multi-step trade-off reasoning; 'universal rollback on all backends' is stated rather than challenged. The nearby history is a different problem space, so it is novel.

### holdout HE04

Construction request 180:

An analytics dashboard shows the current approved plan per account plus monthly spend totals. Tables: accounts(account_id, status; PK account_id); plans(plan_id, account_id, state, effective_at, created_at, name; PK plan_id); spend_events(event_id, account_id, posted_at, amount; PK event_id). One result row per plans.plan_id. Return: account_id: Active account identifier.; plan_id: Selected latest eligible plan row ID.; plan_name: Name from the selected plan row.; month_spend: Sum of posted spend in the current month.. Include active accounts only. Eligible plan rows have state='approved' and effective_at <= current date. Spend is from the current calendar month in one snapshot. If an account has no eligible plan, return no row for it. If no spend rows exist, month_spend is 0. Choose the latest eligible plan per account by effective_at desc, then created_at desc, then plan_id desc. Aggregate spend independently by account over the month; keep both results aligned by account_id. How would you write one SQL query that returns each active account’s latest eligible approved plan row and its month-to-date spend under one snapshot?

Hard construction attempt 1: One focused SQL task with clear tables, output columns, and deterministic tie-break plus independent monthly aggregate. It is implementation-level and interview-plausible, but not especially deep beyond combining standard selection and aggregation correctly.

### holdout HE05

Construction request 183:

A messaging import POST may timeout after commit; retries can race with the original call. POST /imports creates one durable import job and claims a key. Effects: Persist a job record.; Start exactly one downstream import attempt.. Idempotency key plus authenticated principal. Key is scoped to the authenticated principal and operation. Reject as a conflict when the payload hash differs. Concurrent identical retries converge to one job; a lost response returns the stable pending or completed result. HTTP retry handling is idempotent; downstream side effects need separate reconciliation. How would you implement the server-side retry contract and atomic state machine?

Hard construction attempt 1: Concrete, bounded HTTP backend contract with atomic claim and recovery. However, parts like ‘HTTP retry handling is idempotent’ and ‘downstream side effects need separate reconciliation’ blur the exact observable contract, so the prompt is mostly clear but not perfectly tight.

### holdout HE06

Construction request 186:

A feed endpoint returns versioned item changes with tombstones; page-one must be a stable snapshot. Changes have change_id, item_id, created_at, deleted_at, payload. Requests include filter, opaque cursor, page_size. Pages never repeat or skip within one contract; tombstones are visible. Cursor expires after ten minutes; deleted rows and reordering may occur after page one. How would you implement a bounded resync contract when the cursor expires after ten minutes?

Hard construction attempt 1: The prompt is a bounded REST pagination contract with tombstones, cursor expiry, and post-page-one reordering/deletes. It asks for one implementation decision, but the exact recovery semantics after expiry are underspecified: whether to preserve the old snapshot, resume from a checkpoint, or force a new snapshot is not fixed.

### holdout HE07

Construction request 189:

A deployment merged a bad feature branch, then a migration rewrote on-disk metadata format; afterward a small follow-up fix landed on main. Git history is shared; commits and merge parents are visible. Recovery must preserve the good fix and auditable history. Old binaries cannot read the migrated format safely. How would you recover main so production can read both old and migrated data without losing the fix or requiring an unsafe old-binary redeploy?

Hard construction attempt 1: The prompt asks for a concrete recovery sequence under shared history, merge parents, and a format migration that breaks old binaries. That is a bounded SWE/Git recovery problem with a real compatibility trade-off. It is mostly clear and interview-plausible, but the exact acceptable recovery mechanism is underspecified, and the observable contract depends on whether the migrated data can be made readable before preserving the fix.

### holdout HE08

Construction request 192:

A feature refresh swaps search generations while imports and reads continue. Input has generation, item_id, acknowledged_at, and refresh_id. After restart, acknowledged inserts remain visible exactly once. No sleep-based timing; barriers must force both commit and refresh boundaries. How would you build deterministic tests that expose lost acknowledged inserts or mixed-generation reads without sleeps?

Hard construction attempt 1: accepted

### holdout HE09

Construction request 195:

After a deployment, p99 latency triples while median latency, CPU, and query time stay flat; traces show the pool is saturated. Compare: Connections are leaked on some release paths. versus Transactions legitimately hold connections for too long.. Use a bounded canary with forced cancellations; compare acquisition wait, ownership duration, and release traces before and after. Both hypotheses may coexist; timing changes from logging are allowed, but the experiment must stay bounded and safe. Distinguish the causes with a bounded experiment. How would you distinguish leaked connections from legitimate long-held transactions using per-lease release traces and one bounded canary test?

Hard construction attempt 1: The prompt asks for one bounded experiment and one diagnosis decision under two competing hypotheses. It is role-relevant, technically sound, interview-plausible, and has clear follow-up room, but the answer space is broad enough that clarity is only moderate.

### holdout HE10

Construction request 198:

A warehouse report export is produced by a background job and downloaded through a cached link. original_requester can download report_export before this change: tenant removal revokes access before the cached link is used Afterward that action must be denied. Authorize queue submission, job execution, and download separately. Recheck current principal-resource policy at execution and publication; fail closed if policy data is unavailable. How would you enforce authorization so the original requester stays bound to the export, tenant removal revokes access within 30 seconds, and worker privileges never stand in for user authorization?

Hard construction attempt 1: Directly SWE/security-relevant; plausible interview prompt; bounded but requires coordinating multiple authorization boundaries and a revocation window. The wording is somewhat compressed but answerable. It supports follow-up on cache invalidation, policy source failure, and worker/user identity separation.

### holdout HE11

Construction request 201:

A search service replays events after crashes. Each event has event_id, query_id, expires_at, and payload. The stream is larger than RAM, and expired IDs may be processed again. Input is an append-only event stream. Replayed unexpired event_ids are skipped once. Expired IDs may be processed again; false positives are forbidden. How would you implement bounded deduplication state so replayed event_ids are suppressed before expiry, survive crash/restart, and never false-drop a non-duplicate?

Hard construction attempt 1: Direct SWE data-structures / storage-state design. Contract is mostly coherent and bounded, but it is underspecified about the exact recovery mechanism and what “processed” means beyond dedup suppression. It’s a plausible interview prompt with an implementation-level trade-off, and the prior session question is meaningfully different enough in task framing.

### holdout HE12

Construction request 204:

A collaboration index must report the top tags from a 12 TB event log on disk; RAM holds only 2 GB, inserts arrive in hourly bursts, and exact counts with deterministic ties are required. Input is a stream of (tag_id, event_id); duplicates are possible. Output exact counts for the top k tag_ids and their result row_identity. Ties break by smaller tag_id; if fewer than k tags exist, return all. How would you implement the bounded-memory top-k computation and tie-breaking so burst writes and skewed tags do not break correctness?

Hard construction attempt 1: The prompt is interview-plausible and SWE-relevant, but it is underspecified on what row_identity means and how much external memory/disk I/O is allowed. It asks for one bounded implementation decision under skew/bursts, which is reasonable, but the core reasoning is mostly routine streaming aggregation unless row_identity has specific semantics.

### holdout HE13

Construction request 207:

A photo-storage service reserves multiple files atomically for a restore job while retries and deadlocks occur. Tables: restore_job(job_id, principal_id, request_token, created_at; PK job_id); file_reservation(file_id, job_id, reserved_at; PK file_id); outbox(outbox_id, job_id, event_type, sent_at; PK outbox_id). One result row per restore_job.job_id. Return: reserved_job_id: Committed restore job row for the request.; reserved_file_id: Each file actually claimed by the job.; outbox_job_id: Outbox record tied to the committed job.. Only active jobs and current reservations matter; retries may reuse the same request_token for one principal. Missing reservations mean the job failed and no file was claimed; NULL sent_at means unsent outbox row. Return one row per claimed file and one outbox row per committed job; do not count partial claims as success. How would you implement the reservation transaction and retry boundary so each job either reserves every requested file or none, avoids duplicate side effects, and still behaves correctly under overlapping requests?

Hard construction attempt 1: The prompt is about SQL transaction/retry correctness for atomic reservation and duplicate side effects. It is plausible and interview-like, but the contract is under-specified on the actual requested-file source and exact committed-job lookup semantics. It has meaningful edge-case reasoning, yet the observable task is not fully pinned down.

### holdout HE14

Construction request 210:

An analytics plugin pipeline acquires a cache, a file handle, then a publish token; any stage may fail or be canceled. No partial result is observable before publish succeeds. Caller may retry after timeout using the same operation identity. Canceled or failed stages must be cleaned up deterministically. Universal create-and-publish success across all plugins. How would you design the interfaces and caller workflow so no partial result becomes visible, retries are safe after timeout, and cleanup runs for every acquired stage?

Hard construction attempt 1: Core asks for one implementation workflow preserving no-partial visibility, safe retries by operation identity, and cleanup over multiple acquired stages. It is a bounded OOP/concurrency contract question, not a generic design-pattern prompt.

### holdout HE15

Construction request 213:

A background export for a shared report is downloaded through CDN links and policy caches. team_member can download shared_report_export before this change: Team removal revokes the same principal's download within 30 seconds. Afterward that action must be denied. Authorize queued export creation, job execution, and download. Policy-data misses or stale caches fail closed; CDN and link caches must honor the 30-second revocation window. How would you design the authorization checks and cache invalidation path so team removal revokes one principal's download within 30 seconds?

Hard construction attempt 1: SWE-relevant security/authz problem with a concrete boundary workflow. The contract is somewhat underspecified about exact cache primitives and invalidation mechanics, but the core task is clear and testable. It is plausibly interviewable and supports follow-up on race timing, fallback checks, and cache propagation.

### postfix NEW01

Construction request 216:

A collaborative editor keeps a temporary action stack for one user. Operations: push(x), pop(), max(), undo(). max() returns the current maximum after every step. Duplicate maxima and undo after a pop must be handled correctly. How would you implement push, pop, max, and undo so duplicate maxima stay correct?

Hard construction attempt 1: accepted

### postfix NEW02

Construction request 219:

A collaboration service stores per-document edits with a short replay window and concurrent cache refreshes. Each document ID has one active generation and optional tombstone. Only the newest generation may become visible. Expired or deleted generations must not reappear. How would you implement state updates so an older in-flight load cannot overwrite a newer edit or revive a deleted generation?

Hard construction attempt 1: accepted

### postfix NEW03

Construction request 222:

A collaboration tool stores sorted event timestamps with duplicates and unsorted [a,b) windows. Input: events sorted ascending; windows unsorted; each window has start,end. Output covered event count and each event counted once. Empty or touching windows cover nothing; [a,a) is empty. How would you count each covered timestamp exactly once without rescanning all events per window?

Hard construction attempt 1: The prompt is a small fresher algorithm problem with two interacting constraints (sorted duplicate events + unsorted half-open windows) and one clear task (count each covered timestamp once). It is interview-plausible and answerable, but the boundary rules are explicit and the reasoning depth is modest rather than hard.

### postfix NEW04

Construction request 225:

A collaboration app stores document edits and hourly usage per account under one snapshot. Tables: edits(edit_id, account_id, created_at, status, doc_id; PK edit_id); account_hours(account_id, hour_start, minutes_used; PK account_id,hour_start); accounts(account_id, plan, active; PK account_id). One result row per edits.edit_id. Return: selected_edit_id: selected edits.edit_id; account_id: Account owning the selected edit.; day_minutes_used: Sum of minutes_used for that account on the snapshot day.. Consider only active accounts; eligible edits have status='published'; use one snapshot day. If an account has no eligible edit, return no row for it; missing daily hours are zero. Choose the latest eligible edit per account with stable edit_id tie-break; join daily hours by account_id and snapshot day; aggregate minutes per account. Choose the latest by edits.created_at, edits.edit_id descending; return selected_edit_id. How would you query the latest eligible edit per account, then attach that account's hourly aggregate for the same day, returning the selected edit ID and handling accounts with no eligible edits?

Hard construction attempt 1: Core task is a bounded SQL query under interacting constraints: independent one-to-many daily aggregation without row multiplication and deterministic latest-edit selection. The prompt is mostly coherent, though phrasing is redundant. It is clearly SWE/SQL interview material and not a repeat of the prior retry/transaction question.

### postfix NEW05

Construction request 228:

A note exporter stages edits privately, then publishes them as one visible snapshot. Publish is atomic: readers see either the old snapshot or the full new one. Caller edits a draft, may cancel mid-way, then either publish or discard. If publish fails halfway, the previous visible content remains readable. One object may both buffer and expose live content directly. How would you design the objects and method flow so a cancelled publish never exposes a partial snapshot?

Hard construction attempt 1: accepted

### postfix NEW06

Construction request 231:

A document importer runs plugins that reserve, transform, and publish assets; any stage may fail or be canceled. Publish happens only after all stages succeed; partial results stay hidden. Callers start a run, execute stages, then either commit publication or cancel cleanup. Timeouts must expose created, already-published, canceled, or unknown outcomes. A single always-successful publish method for every plugin. How would you design the plugin interfaces and caller workflow so no partial asset is published, cleanup is composable, and a retry can safely distinguish a completed run from an unknown timeout?

Hard construction attempt 1: accepted

### postfix NEW07

No constructed draft (provider failure or explicit coverage exhaustion).

### postfix NEW08

No constructed draft (provider failure or explicit coverage exhaustion).

### postfix NEW09

Construction request 236:

A collaboration API creates one durable review task per submit. Create a review task from a submit request. Effects: Persist one durable task record.; Notify the reviewer once.. Principal-scoped submit key. Same principal and same task body. Return conflict; do not create a second task. Concurrent same-key submits claim one task; a retry after lost response returns the existing outcome. Guarantee at-most-one durable task per principal and body. How should the submit endpoint handle retries, duplicate claims, and body changes?

Hard construction attempt 1: Focused, bounded fresher HTTP/server contract. It is technically plausible, but the prompt is terse and bundles several behaviors (duplicate claims, retries, body changes) without fully specifying response shape or recovery details. The reasoning demand is modest and close to standard idempotency patterns.

### postfix NEW10

Construction request 239:

A collaboration service refreshes an index generation while writes and reads continue. Writes may commit during refresh; reads continue concurrently. After restart, every acknowledged insert is visible once with one generation tag. No sleep-based timing; the same row must not appear from two generations. How would you design deterministic tests that expose acknowledged inserts lost on generation swap or mixed-generation reads?

Hard construction attempt 1: accepted

## Calibration: frozen reference labels

Development reference set: 7 positive and 9 negative cases. These are not the unseen holdout. Each of three versions screens the same unchanged labels. The current exact case is excluded from its calibration anchors.

| Version | False accepts / 9 negatives | False rejects / 7 positives |
|---|---:|---:|
| Initial | 4 | 0 |
| Evidence-first | 5 | 1 |
| Trusted anchors | 4 | 1 |

### ref-F01 — Data Structures · fresher

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Reviewed fallback integrates hash lookup, recency mutation, bounded eviction and repeat/evict correctness. Relative fresher Hard, not experienced Hard.

Final model rationale: Single bounded implementation task with interacting constraints (dedup, recency update, size-bound eviction) and a concrete boundary case. Suitable for a fresher SWE interview. The prompt is clear and answerable, with many valid implementations and natural follow-ups.

### ref-E05 — HTTP · experienced

A messaging API has `POST /imports` to create a bulk import job. Clients may retry after a timeout, and sometimes the response is lost after the server has already committed the job. You must guarantee that the same authenticated user can safely retry the same request, but if they reuse the same idempotency key with a different payload, the server should reject it. What server-side contract and storage/claim flow would you implement so concurrent identical retries do not create two jobs, while still returning a stable outcome for pending or completed requests?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Requires atomic key claim, payload mismatch handling, concurrent retries and stable pending/completed outcomes after lost responses.

Final model rationale: Focused on POST retry safety with lost responses, duplicate-prevention under concurrent identical submits, and same-key/different-payload rejection. This is a single bounded implementation contract with a concrete storage/claim flow and retry edge case.

### ref-E09 — Debugging · experienced

After a deployment, p99 latency on an API triples, but median latency, CPU, and database query time stay flat. Traces show most of the extra time is waiting to acquire a DB connection, and the pool stays at its limit even after requests complete. Assuming requests are well-formed and the app must stay live, how would you distinguish a leaked connection from a legitimate long-held transaction, and what bounded change or instrumentation would you add first to prove it without widening the pool? Consider cancellation and exception paths too.

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Discriminating pool-wait evidence, competing leak/ownership hypotheses and cancellation paths require a bounded falsifiable experiment.

Final model rationale: Direct SWE debugging with concrete latency symptom and bounded evidence collection. One primary task: distinguish leak vs long-held transaction and prove it without widening the pool. Includes interacting constraints (live service, cancellation/exception paths, p99 only, pool saturation).

### ref-E03 — Object-Oriented Programming · experienced

Imagine a file-storage client with two operations: uploadBlob() for ordinary file uploads and createLockFile() for a mutual-exclusion marker that must be atomic, even across retries. Backend X supports conditional writes; backend Y only supports read/overwrite but gives you versioned object keys. If a request times out, the caller must be able to tell whether the lock was created, definitely not created, or the outcome is unknown. How would you shape the interfaces or class boundaries so uploadBlob can use Y, while createLockFile either preserves the atomic contract or clearly rejects unsupported use? Assume callers rely on those outcome distinctions.

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Typed capability interfaces and unsupported-operation handling largely restate the explicit mismatch. No concrete caller recovery sequence or competing implementation choice is required.

Final model rationale: Direct SWE/OOP boundary design with backend capability differences and timeout recovery is relevant. The contract is technically coherent: it asks for explicit outcome distinctions and unsupported-path handling. It is plausible in an interview, has multi-step reasoning under competing constraints, and supports follow-ups about retries, capability detection, and verification.

### ref-F02 — Algorithms · fresher

You have a sorted array of timestamps that may contain duplicates, and you need to return the first timestamp that is at least a given cutoff. If no such timestamp exists, return -1. The array can be empty, and your solution should stay correct when several equal values sit around the cutoff. How would you adapt binary search so it always makes progress and still returns the first eligible timestamp rather than just any match?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): REJECT / REJECT / REJECT.

Reference basis: One lower-bound binary search with duplicates and empty input is a standard textbook implementation, without an additional interacting task.

Final model rationale: Direct SWE fit. The contract is sound and bounded, but the task is a standard lower-bound search with an empty-array case; the added duplicate/cutoff wording does not create interacting constraints beyond a routine boundary. The ask is clear and interview-plausible, but not Hard depth.

### ref-F03 — Object-Oriented Programming · fresher

Imagine a file storage app where each file has a name, size, and a method that returns its total cost. Regular files cost by size, but image files also have a fixed thumbnail fee. The app stores files in one list and prints the total bill by calling the same method on every item. If you add a new file type later, you should not have to change the billing loop. How would you design the classes and method contract so this works, while still handling the edge case that a file may report invalid state, like a negative size?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): REJECT / REJECT / REJECT.

Reference basis: Subclass price overrides and negative-size validation remain a routine polymorphism exercise; invalid input does not create substantial interacting constraints.

Final model rationale: Single focused fresher OOP design task. The only edge case is a negative size, but the prompt doesn’t require a deeper trade-off beyond defining validation vs failure. Adding new file types without changing the billing loop is straightforward polymorphic dispatch, not multi-constraint reasoning.

### ref-E04 — SQL · experienced

Imagine an analytics service records one row per customer event, and a nightly job marks all events for a given customer as processed by updating a status column. New events for that customer can arrive while the job runs, and a retry may happen after a deadlock or serialization failure. If you had to make the job correct and idempotent under this contention, what transaction strategy would you use for the UPDATE, and where would you place the retry boundary? Assume the job must never mark an event processed unless it was actually selected in that run, and duplicate processing is worse than a temporary delay.

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / REJECT.

Reference basis: The processing effect and selected-in-this-run semantics are unspecified. Updating status alone is not a defined exactly-once processing contract; a clarification is needed before choosing transaction boundaries.

Final model rationale: The task is a focused SQL concurrency/update contract with contention, failure recovery, and idempotence. It is interview-plausible and role-relevant, but the prompt underspecifies the exact selection/claim mechanism and durable meaning of “actually selected,” so correctness is not fully pinned down. It has some follow-up potential, but the answer space is broad and not deeply constrained enough for strong hard reasoning as written.

### ref-P7F03 — Object-Oriented Programming · fresher

Suppose a file-storage app has a `Storage` interface with `save(file)` and `delete(fileId)`. The app also guarantees this caller-visible rule: if `save()` fails halfway, no partial file should be visible to later `get()` calls. You need to add a new `EncryptedStorage` implementation without changing the code that orchestrates uploads and deletes. How would you structure the objects so that encryption can be swapped in while preserving that no-partial-file invariant, especially if `save()` can fail after writing the first chunk?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / REJECT / ACCEPT.

Reference basis: A swappable encrypted writer must preserve no-partial-read visibility after a chunk failure; staged write/publication/cleanup is a concrete OOP boundary with a meaningful failure case.

Final model rationale: Concrete SWE/OOP task: swap in EncryptedStorage while preserving a caller-visible invariant across a failure boundary. It asks for one implementation approach under two interacting constraints (pluggable storage + no partial visibility).

### ref-P7F04 — SQL · fresher

A platform has `customers(customer_id, name)` and `orders(order_id, customer_id, status, created_at)`, where `status` is `PAID` or `CANCELLED`. Write a query that returns every customer plus three columns: total paid orders, total cancelled orders, and the date of their most recent PAID order. If a customer has no paid orders, that last column must be `NULL`. If two paid orders share the same `created_at`, pick the one with the larger `order_id`. How would you avoid row multiplication between the two counts and still make the latest-order rule deterministic?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Only the latest PAID date is returned, so selecting a larger order_id for tied dates has no observable effect. Two conditional counts over the same table are routine and do not inherently create independent join multiplication.

Final model rationale: One focused fresher SQL task: independent aggregates plus deterministic latest-row selection over nullable unmatched parents. The contract is clear and bounded, with a concrete tie case and no hidden distributed or senior-design assumptions.

### ref--refinedR04 — Security Fundamentals · fresher

A note app lets users own notes and share them with teammates. A share can also be revoked, but revocation is processed asynchronously: for a short time, the note may still show in a client cache even after the server has marked the share as revoked. If a user is the owner, they can edit; if they are only a shared viewer, they can read but not edit. How would you enforce access at the server boundary so a revoked viewer cannot keep editing by replaying an old note ID, and what single test would you run to prove the revoke takes effect on the next write even if the cached view is stale?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): REJECT / ACCEPT / ACCEPT.

Reference basis: Shared viewers could never edit, so denying their writes before and after revocation does not prove revocation worked. The test would pass even if revoked read access remained exposed.

Final model rationale: Single bounded access-control task with one tricky boundary: asynchronous revocation plus stale cache. It asks for server-side enforcement and one proving test. It is clear, plausible for a fresher, and supports follow-up on read-vs-write handling or cache invalidation.

### ref-P7F09 — Debugging · fresher

An API sometimes returns one user’s draft comment to another user, but only when two requests overlap and the server logs are enabled. You can add one temporary request ID to each request and run a controlled two-request test. What is the first explanation you would try to confirm, and what single experiment would you run to distinguish shared mutable state from a timing issue caused by logging? Include what result you would expect in each case.

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): REJECT / ACCEPT / ACCEPT.

Reference basis: Shared mutable state and logging-induced timing are not mutually exclusive hypotheses. Toggling logging may expose the same race rather than distinguish its cause; the requested each-case oracle is misleading.

Final model rationale: Single bounded debugging experiment, two plausible hypotheses, and an expected-result split. It is SWE-relevant, plausible for a fresher interview, and asks for one primary diagnostic step rather than a checklist.

### ref-P7E06 — REST APIs · experienced

Suppose GET /activities must return a stable snapshot of page 1 as-of the first response, ordered by (created_at, id), even while new rows are inserted and some rows are deleted. The cursor must expire after 10 minutes, and you cannot keep a full result set per client. If you had to choose one backing approach that actually enforces that contract, what would you implement so page 2 still reflects the same snapshot, and how would it handle one concrete race where a row is deleted after page 1 but before page 2?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Explicit snapshot semantics under deletion require retained/as-of state or a clearly costed snapshot mechanism; a cursor alone does not satisfy the contract.

Final model rationale: REST API pagination with snapshot consistency, cursor expiry, and a delete race is directly SWE-relevant. The prompt is focused and answerable, but it still allows multiple implementations. It is experienced-level hard because it asks for one implementation choice under interacting constraints, not a named pattern alone.

### familiar-not-repeated — Data Structures · fresher

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / ACCEPT.

Reference basis: Familiar LRU pattern is still a new task relative to this unrelated question.

Final model rationale: Directly relevant SWE data-structure problem; premise is sound; bounded interview; requires coordinating deduplication, recency update, and eviction; appropriate for fresher; focused and answerable; strong follow-up potential on concurrency, persistence, or alternative implementations.

### near-duplicate — Data Structures · fresher

Keep the latest 100 distinct search terms, moving repeats to newest and evicting oldest without a scan. How would you implement it?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): ACCEPT / REJECT / REJECT.

Reference basis: Same recency/dedup/eviction reasoning as the earlier question despite different wording.

Final model rationale: The prompt is a focused fresher data-structures task with one clear implementation decision and a boundary case. It is technically sound, interview-plausible, clear, and has natural follow-ups on deletion, updates, or concurrency. It is novel relative to the prior question only in phrasing, not substance.

### valid-alternative-index — Algorithms · experienced

An index has ten million timestamped rows, 10,000 inserts/second in bursts and concurrent range reads. Acknowledged inserts must be visible; memory allows one base plus a small delta. A colleague proposes a sorted base with a searchable delta rather than a balanced tree. How would you implement read merging and rebuild publication so an interrupted rebuild cannot lose acknowledged inserts, and which workload would make you reject this design?

Frozen label: PASS; model decisions (initial / evidence-first / anchors): ACCEPT / ACCEPT / REJECT.

Reference basis: A correct unfamiliar/alternative strategy can meet the invariant; no required tree answer.

Final model rationale: Single bounded implementation task for a search/index component with interacting constraints: high write bursts, concurrent range reads, small-memory delta, and crash-safe rebuild publication. It is clearly SWE-relevant and plausible, but the contract is a bit broad because 'how would you implement' plus 'which workload would you reject' asks for one main design and one suitability judgment.

### impossible-exactly-once — HTTP · experienced

An email provider has no idempotency key or delivery lookup and does not share transactions with your database. A send may succeed while its response is lost. Without changing those capabilities or weakening guarantees, implement automatic retries that always eventually deliver exactly one email. What local database flag makes this possible?

Frozen label: FAIL; model decisions (initial / evidence-first / anchors): REJECT / REJECT / REJECT.

Reference basis: The demanded guarantee is impossible with these capabilities; the question forbids the necessary redesign and falsely promises a flag solution.

Final model rationale: The prompt asks for an exactness guarantee despite no idempotency key, no delivery lookup, and no shared transaction with the DB. That contract is contradictory/underspecified: a local flag cannot prevent duplicate sends after a lost response. It is a routine impossibility check, not a bounded Hard implementation task.

## Development pilots (not a quality benchmark)

Twenty configurations were used for iteration before the holdout. Their outputs and automated rejection traces are included for completeness; no independent per-question agent verdict was assigned to this development cohort, so they are not included in pass/fail percentages.

### pilot DEV01 — Data Structures · fresher

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

A cache stores page IDs with timestamps. Calls are get(id) and put(id). Capacity is fixed. On access, the ID becomes most recent. On insert when full, evict least recent. Each operation names one integer ID and optional value. Returned evicted ID must match the least recent live entry. When inserting an existing full-capacity ID, refresh it without extra eviction. IDs are unique integers. Python 3.12; no concurrency. Both get and put must be near O(1). Updating an existing ID must refresh recency. At capacity, repeat insert of current key must not evict another key. Return the evicted ID, or -1 when no eviction happens. Capacity 2; sequence: put(7), put(8), put(8), put(9). Observe which ID leaves. Which data structure combination would you implement, and how does it handle update-vs-evict at full capacity?

Draft request 18:

A cache stores page IDs with timestamps. Calls are get(id) and put(id). Capacity is fixed. On access, the ID becomes most recent. On insert when full, evict least recent. Each operation names one integer ID and optional value. Returned evicted ID must match the least recent live entry. When inserting an existing full-capacity ID, refresh it without extra eviction. IDs are unique integers. Python 3.12; no concurrency. Both get and put must be near O(1). Updating an existing ID must refresh recency. At capacity, repeat insert of current key must not evict another key. Return the evicted ID, or -1 when no eviction happens. Capacity 2; sequence: put(7), put(8), put(8), put(9). Observe which ID leaves. Which data structure combination would you implement, and how does it handle update-vs-evict at full capacity?

Hard construction attempt 1: accepted

### pilot DEV02 — Algorithms · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Draft request 21:

A log viewer stores event times in one sorted array, duplicates allowed. Build countEvents(timestamps, start, end) for half-open [start,end). Input: sorted int array timestamps; int start,end; duplicates allowed; no null elements. Count only values in half-open range [start,end). If start>=end or array empty, return 0; no per-item scan. timestamps already sorted ascending. PostgreSQL not involved; in-memory array only. Must run in O(log n) time. Empty array allowed; start may equal end. Return the count of timestamps x where start <= x < end. When start == end, the count must be 0 without scanning. Should you implement one boundary search or two, and why?

Draft request 23:

A log viewer stores event timestamps in one sorted array. Given many queries [a,b), return how many timestamps fall inside each half-open window. Input is an int array and query bounds a,b. Count elements x with a<=x<b. Empty array or a>=b yields 0; do not overcount b. PostgreSQL not involved. Array is sorted nondecreasing; duplicates allowed. Must not scan the whole array per query. Return 0 for empty array or a>=b. Implement queryCount(timestamps,a,b) for exact counts. Equal bounds, and all values equal to a or b. Use one or two boundary searches to count [a,b)?

Hard construction attempt 1: Useful SWE/algorithms task with a precise in-memory range-count contract. It is clear and interview-plausible, but the core reasoning is a routine bounded binary-search/count problem with a standard half-open edge case; the “one boundary search or two” prompt does not create strong multi-constraint depth.

Hard construction attempt 2: Core task is a standard range-count query on a sorted array using boundary searches; the only edge cases are empty input and half-open bounds, which are routine. The prompt is also bundled/redundant: it repeats the same ask three times and asks for both exact counts and boundary searches without one focused contract, so clarity is only partial and the reasoning depth is one-step rather than multi-constraint.

### pilot DEV03 — Object-Oriented Programming · fresher

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

Implement a DocumentEventHub. Subscribers register listeners, then trigger(event) delivers to a stable snapshot. trigger(event) uses start-of-call membership only; later mutations affect future triggers. Caller registers listeners, fires one event, then mutates registry, then fires again. If live iteration is used, a newly added listener may receive the same event or an unsubscribed one may be skipped. Python 3.11. Single-threaded calls. A listener may unsubscribe itself during delivery. A listener may add a new listener during delivery. One trigger call must invoke only listeners present at start, once each, in registration order. If L2 unsubscribes L3 while event E is being delivered, L3 still receives E but not later events. How should you implement trigger so delivery stays snapshot-stable while registrations still mutate future calls?

Draft request 26:

Design a FileWatcher registry. A watcher receives a stable snapshot per publish call. During one delivery, a listener may unsubscribe itself or add another listener; those edits must not affect the current publish. publish(path) calls only listeners present at start of that publish. Caller adds listeners, publishes paths, may mutate registry inside callbacks. If snapshot rules fail, a later-added listener fires too early or a removed listener is skipped too late. Python 3.12. Single-threaded; no locks. Listeners are objects with on_event(path). A listener can be added once only. Removed listeners stay absent for later publishes. Given add, remove, publish, return the exact call order for each publish. A listener removes itself, then adds a new listener, while another listener also removes that new listener before the next publish. What registry design preserves the snapshot guarantee while keeping listener ownership clear?

Draft request 27:

Implement a DocumentEventHub. Subscribers register listeners, then trigger(event) delivers to a stable snapshot. trigger(event) uses start-of-call membership only; later mutations affect future triggers. Caller registers listeners, fires one event, then mutates registry, then fires again. If live iteration is used, a newly added listener may receive the same event or an unsubscribed one may be skipped. Python 3.11. Single-threaded calls. A listener may unsubscribe itself during delivery. A listener may add a new listener during delivery. One trigger call must invoke only listeners present at start, once each, in registration order. If L2 unsubscribes L3 while event E is being delivered, L3 still receives E but not later events. How should you implement trigger so delivery stays snapshot-stable while registrations still mutate future calls?

Hard construction attempt 1 rejected: Rendered question has 936 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2: accepted

### pilot DEV04 — SQL · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Draft request 30:

Analytics query for parent projects with two child streams. Tables: projects(project_id, name, is_active; PK project_id); tasks(task_id, project_id, created_at; PK task_id); comments(comment_id, project_id, created_at; PK comment_id). Return: task_count: Number of tasks per included project; comment_count: Number of comments per included project. Include only projects where projects.is_active = true. Count all tasks and comments for those projects. Projects with no matching tasks or comments remain in output with zero counts. NULL child timestamps do not affect counts. Avoid a single join that multiplies tasks by comments. Counts must be independent per project. PostgreSQL 16. Each table is already populated. Three tables only; no extra lookup tables. Preserve parents with zero child rows. Counts must not multiply across child joins. Return one row per active project with two separate child counts. A project has tasks but no comments; another has comments but no tasks. How would you write the query so both counts are exact and missing children stay visible?

Draft request 31:

Analytics for projects, tasks, and comments. Find eligible projects and one representative project. Tables: projects(project_id, created_at, status; PK project_id); tasks(task_id, project_id, opened_at, closed_at; PK task_id); comments(comment_id, project_id, posted_at; PK comment_id). Return: project_id: Eligible project id; task_count: Count of tasks for that project; comment_count: Count of comments for that project. Eligible projects are those created in 2026 and status='active'. Projects with no tasks or comments must still appear; COUNT(column) ignores nulls. Counts must not multiply across the two child tables; apply one row per child or pre-aggregate before final join. PostgreSQL 16. All tables are current. Three tables only. Two independent child counts per project. Never lose projects with zero children. Return each eligible project's id, task_count, comment_count. A project with tasks but no comments, and another with neither. Which SQL shape keeps counts correct and tie-breaking observable?

Hard construction attempt 1 rejected: Rendered question has 1073 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2 rejected: Rendered question has 1017 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

### pilot DEV05 — Security Fundamentals · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

Mira can read a team's private files but cannot write them. After membership removal commits, her next read must fail even with an old login token or cached file link; another team she belongs to must still work. How would you enforce and test the read boundary, including a request begun before removal that reaches authorization afterward?

Draft request 33:

A note app has shared notes with owner and collaborators. collaborator can write shared_note before this change: note changes ACTIVE to READ_ONLY Afterward that action must be denied. Server-side note update endpoint Authorization must use current note status, not cached state Server enforces auth on each request. Postgres stores note ACL and status. ACTIVE note allows collaborator write. READ_ONLY note still allows everyone to read. Owner keeps write after status change. Implement the permission decision for note write requests. A collaborator retries the same write after READ_ONLY. What server-side rule should determine write access for owner, collaborator, and replayed requests after the status change?

Draft request 35:

A shared note starts ACTIVE. Its owner and one collaborator can edit it; later the note switches to READ_ONLY for collaborators only. collaborator can write shared_note before this change: ACTIVE to READ_ONLY; same collaborator, same note, same write payload Afterward that action must be denied. Edit endpoint on the note service Reject retries after role change even if the original write was never acknowledged Server checks auth on every edit request. Same note ID, same principal, same payload may repeat. Owner can still edit after the switch. Collaborator can still read after the switch. Replayed collaborator writes must not apply after READ_ONLY. Define the rule that decides whether an edit is accepted and which principal/resource pair it protects. A collaborator sends an edit, the role flips to READ_ONLY, then the same edit is retried after a lost response. What authorization and replay rule should the API enforce for this transition?

Hard construction attempt 1: Role/topic fit is strong and the scenario is interview-plausible. However the contract is under-specified: it asks for a permission rule but does not pin down whether replayed requests are idempotent, whether ownership/collaboration is mutable, or what exact observable outcome should be judged after the READ_ONLY transition. The answer space is broad and the boundary between collaborator write denial and replay handling is not fully defined.

Hard construction attempt 2 rejected: Rendered question has 951 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

### pilot DEV06 — SQL · experienced

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Draft request 37:

No valid projection; original response retained.

Draft request 38:

Analytics: latest eligible event per account, plus totals. Tables: accounts(account_id, created_at; PK account_id); events(event_id, account_id, event_ts, is_eligible, amount; PK event_id). Return: account_id: Account identifier; selected_event_id: Latest eligible event row id; eligible_amount_total: Sum of eligible amounts in scope. Use events with event_ts <= :as_of and is_eligible = true. No eligible event returns NULL selected_event_id; sum is 0. Compute latest eligible row per account independently from the aggregate over all eligible events in scope. Choose the latest by events.event_ts, events.event_id descending; return selected_event_id. PostgreSQL 16. One row may be ineligible or missing. Snapshot fixed at :as_of. Tie-break by smallest event_id. Return selected event_id and account totals. Two eligible events share the same timestamp. How do you query the latest eligible event per account and independent aggregates in one result?

Hard construction attempt 1 rejected: 1 validation error for ProblemSpecification
technical_contract.sql.outputs
  List should have at most 4 items after validation, not 5 [type=too_long, input_value=[{'name': 'account_id', '... view events in scope'}], input_type=list]
    For further information visit https://errors.pydantic.dev/2.14/v/too_long

Hard construction attempt 2 rejected: Rendered question has 953 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

### pilot DEV07 — HTTP · experienced

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A file-import POST can finish importing after the client times out. The server stores request keys and jobs in one database transaction; clients may retry concurrently with the same key but different bodies. How would you define and implement the retry contract, including a response lost after commit?

Draft request 40:

A messaging API accepts POST /imports for batch enrollments. Two retries may share one client key. Requests can time out after commit, before the response returns. POST /imports creates a batch-enrollment job. Effects: Durable job row; One downstream enrollment attempt set. Idempotency key plus request fingerprint Authenticated principal and import endpoint 409 conflict or equivalent documented rejection Identical concurrent calls converge; lost response returns stable pending/completed state HTTP retry handling only; downstream side effects need their own reconciliation PostgreSQL 16. One authenticated principal per request. Store request fingerprint, job state, and result. Atomic key claim and durable job creation. Describe the server behavior and storage flow for POST /imports. Same principal reuses a key with changed CSV bytes. What implementation should reject that reuse while still converging concurrent identical POSTs and recovering a lost response?

Draft request 41:

POST /imports starts one durable import job. Same principal may retry with same key. Two concurrent identical requests may race. A response can be lost after commit. POST /imports creates a durable import job. Effects: Writes job record.; Starts worker-visible import work.. Idempotency key plus authenticated principal. Per principal, per import operation. 409 conflict; body hash mismatch. Concurrent identical calls converge on one job; lost response returns the existing job state. Exactly-once response is not promised; durable job creation and repeatable state are. PostgreSQL 16. One API node; worker may crash. Key is scoped to authenticated principal. Body hash must be stored with the key. Changed body under same key is a conflict. Return stable job state for repeats; never create two jobs. Client times out after commit, then retries same key while worker is pending. How should the POST handler atomically claim the key and decide 202, 200, or 409?

Hard construction attempt 1 rejected: Rendered question has 970 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2 rejected: Rendered question has 962 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

### pilot DEV08 — Debugging · experienced

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

After a release, p99 latency triples while median latency, CPU and database query duration stay flat. Traces show the extra time before acquiring a database connection, and active connections remain at the pool limit after requests finish. How would you discriminate a leak from longer legitimate connection ownership using a safe experiment before choosing a mitigation?

Draft request 43:

After a deployment, p99 request latency triples. Median latency, CPU, and SQL time stay flat. Pool checkout wait rises. Checked-out connections remain at limit after requests end. Compare: Connection leak on exception or cancel path versus Legitimate long-held transaction or handler. Run a bounded canary with forced cancel on selected requests; compare checkout/release traces and pool saturation. A leak and a slow transaction may coexist; distinguish by per-lease traces, not pool depth alone. PostgreSQL 16. One shared pool per service instance. Use safe, bounded observation in prod. Do not increase pool size yet. Need per-request release traces. Identify which hypothesis the bounded canary supports. Slow handlers and leaks can both saturate the pool; logging may shift timing. What single bounded experiment would you run first, and what observation would make you choose leak over long ownership?

Draft request 44:

No valid projection; original response retained.

Hard construction attempt 1 rejected: Rendered question has 907 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2 rejected: 1 validation error for ProblemSpecification
technical_contract
  Unable to extract tag using discriminator 'kind' [type=union_tag_not_found, input_value={'hypotheses': [{'cause':...ces and session state.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/union_tag_not_found

### pilot-v2 DEV201 — Data Structures · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Draft request 62:

Build a tiny cache for search suggestions with per-key recency. Operations: put(key), get(key), capacity fixed, keys unique strings. Each get/put on an existing key makes it most-recent; insert at full capacity evicts least-recent key. Touching the current most-recent key changes nothing. PostgreSQL 16. Keys are unique strings. Capacity is fixed after init. Each access must move key to most-recent. Lookups and updates should be O(1) average. Return evicted key on insert when full. Given duplicate accesses at full capacity, which data structure plan preserves recency and emits the correct evicted key?

Draft request 64:

A browser cache tracks recently used URL IDs with fixed capacity. Access stream of URL IDs; each access may insert or refresh one ID. Exact kept ID sequence after each access. Touching endpoints do not overlap. IDs are unique strings. PostgreSQL 16. Lookup and move-to-front must be constant-time. Capacity is one, then a repeat arrives. Return the kept URL ID after each access. Touching a full cache with the same URL again. Which data structure update rules preserve recency and eviction order?

Hard construction attempt 1: The prompt is a bounded fresher interview cache design with one primary task and a concrete boundary (duplicate access at full capacity). It is technically sound, clear, and plausible, but not novel relative to the prior recency-cache question. The hardest reasoning is routine LRU bookkeeping, so H is not 2.

Hard construction attempt 2: There is one bounded, interview-plausible freshers DS task, but the prompt is underspecified: 'Exact kept ID sequence after each access' conflicts with 'Return the kept URL ID after each access', and it never states whether to output the full sequence, a final state, or one ID per step. The PostgreSQL mention is unrelated.

### pilot-v2 DEV202 — Algorithms · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Draft request 67:

A collaboration app stores event timestamps in sorted order with duplicates. Input: sorted timestamps array; queries are [a,b) ranges; duplicates allowed; empty array possible. Output count is upper_bound(b)-lower_bound(a). Touching endpoint b is excluded; a==b returns 0. Sorted ascending timestamps. PostgreSQL 16. Count only timestamps in [a,b). At most four SQL outputs. Return the count for each query range. a equals b; no timestamp should match. Implement the query logic using two boundaries or an equivalent approach?

Draft request 69:

A collaboration app stores message timestamps in one sorted array. Sorted nondecreasing array of timestamps; query interval is [a,b). Count every timestamp x with a <= x and x < b. Empty array and a == b both yield 0. Sorted nondecreasing timestamps. PostgreSQL 16. Count messages in [a,b). Return 0 for empty input. Implement exact count for a single query. a == b must return 0 without scanning. Which two-boundary approach would you implement, and how do you prove it handles duplicates and empty input?

Hard construction attempt 1: The prompt is a routine range-count query with duplicates and empty input, fully specified enough to answer, but it asks only for one count logic and an obvious boundary case. No interacting constraints beyond standard half-open interval handling; not Hard. It is interview-plausible and role-relevant, but closer to a basic fresher query exercise than a multi-step reasoning problem.

Hard construction attempt 2: Single sorted-array interval count with duplicate and empty-input boundaries is a standard two-boundary lookup. It is directly relevant and plausible, but the reasoning depth is routine rather than multi-constraint. The prompt is clear and answerable, yet not hard beyond textbook binary search.

### pilot-v2 DEV203 — Object-Oriented Programming · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Draft request 72:

A plugin host delivers document events to registered listeners. dispatch() uses a stable listener snapshot for one event. Register listeners, emit one event, observe which callbacks run. A listener added mid-delivery does not run until the next event. Python 3.12. Listeners are plain objects with methods. A dispatch uses one stable snapshot. Listeners may unsubscribe during delivery. Listeners may add listeners during delivery. Implement the dispatch behavior and listener ownership rules. A listener removes itself and adds another listener. What exact listener set should the current delivery use?

Draft request 74:

A document editor broadcasts autosave events to plugins. A broadcast calls listeners from one stable snapshot. Caller registers listeners, triggers one broadcast, and inspects callbacks. If a listener unsubscribes or adds another listener mid-broadcast, that change affects later broadcasts only. Python 3.11. Listeners are ordinary objects. Stable listener snapshot during delivery. Listeners may unsubscribe during delivery. Listeners may add listeners during delivery. Implement dispatch over one snapshot only. Touching changes do not alter this delivery. Should the dispatcher use a copied snapshot and defer mutations until after the current broadcast?

Hard construction attempt 1: The prompt has one focused implementation task and a concrete boundary. But it is underspecified on ownership rules and exactly what “dispatch behavior” means beyond stable snapshot, so correctness is not fully pinned down. It is plausible for a fresher OOP interview, with follow-up room on unsubscribe/add semantics.

Hard construction attempt 2: The task is a small OOP/event-dispatch implementation with one primary invariant: stable snapshot delivery plus deferred mutation effects. That is clear and interview-plausible, but not Hard depth because the required reasoning is a routine snapshot/queue pattern rather than interacting constraints with a difficult trade-off. The prompt is also slightly redundant, since the final sentence largely repeats the earlier contract.

### pilot-v2 DEV204 — SQL · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Draft request 77:

A museum app reports monthly exhibit participation by gallery. Tables: galleries(gallery_id, gallery_name; PK gallery_id); exhibits(exhibit_id, gallery_id, opened_at; PK exhibit_id); visits(visit_id, exhibit_id, visitor_id, visited_at; PK visit_id). Return: exhibit_count: Number of exhibits per gallery in June 2026.; visitor_count: Number of distinct visitors tied to those June visits per gallery.. Include galleries with zero matching exhibits in June 2026. No matching child rows means count 0, not NULL. Count exhibits and distinct visitors per gallery; never let a join between child tables inflate either count. PostgreSQL 16. Exhibit logs use event timestamps. Each gallery may have zero exhibits. Two child counts must not multiply. Return one row per gallery for June 2026. A gallery with no exhibits still appears. How would you query the three tables so each gallery shows its exhibit count and active-visitor count without double counting?

Draft request 78:

A museum dashboard must summarize exhibit participation by room. Tables: rooms(room_id, room_name, is_open; PK room_id); visits(visit_id, room_id, visited_at; PK visit_id); room_tags(tag_id, room_id, tag; PK tag_id). Return: visit_count: count of visits per room; tag_count: count of tags per room. Only is_open rooms; all history. No visits or tags means count 0. Count each child table independently before combining. PostgreSQL 16. Rooms with no visits still appear. preserve parents with no children never multiply joined counts Return one row per room with two child counts. A room with zero visits and zero tags appears with 0, 0. Which SQL shape correctly avoids inflated counts and keeps empty rooms?

Hard construction attempt 1 rejected: Rendered question has 953 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2: The prompt is a focused fresher SQL aggregation problem with clear schema, output, and edge case. It is technically sound and interview-plausible. Depth is moderate: avoid row multiplication while preserving empty parents. Clarity is mostly good, though wording is slightly redundant. No prior-question repetition.

### pilot-v2 DEV205 — Security Fundamentals · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

Mira can read a team's private files but cannot write them. After membership removal commits, her next read must fail even with an old login token or cached file link; another team she belongs to must still work. How would you enforce and test the read boundary, including a request begun before removal that reaches authorization afterward?

Draft request 81:

A team note service lets a member edit a shared note. memberA can write shared_note before this change: ACTIVE to READ_ONLY Afterward that action must be denied. Server-side authorization on each note update Use the current stored role at request time PostgreSQL 16. Same authenticated principal retries the same request. Deny access by default and grant only required privileges. Check object ownership or policy for each operation, not merely whether a user is logged in. Keep data access scoped to the authenticated principal. Return the same note version for reads and reject unauthorized writes. A replayed write arrives after role change. Given one principal, one note, and a role change from ACTIVE to READ_ONLY, should the write be allowed before the change and denied after it?

Draft request 83:

A user can edit one shared note, then the owner changes its role. user123 can write shared_note_7 before this change: ACTIVE to READ_ONLY role change Afterward that action must be denied. Server-side enforcement at the note update endpoint Use the current stored role at request time Authentication is already verified. PostgreSQL-style row lookup is available. Deny access by default and grant only required privileges. Check object ownership or policy for each operation, not merely whether a user is logged in. A valid token does not grant access to every object. Reject replayed writes after the role change. The same principal can still read the note after the change. Should the update be allowed or denied after the role transition?

Hard construction attempt 1: One principal, one note, one role transition, and one yes/no decision. The prompt asks for server-side enforcement on update with current stored role at request time, but gives no conflicting policy branches or deeper trade-off. It is plausible as a fresher interview question, though mostly a direct authorization check.

Hard construction attempt 2: The prompt is a single bounded security decision with clear state transition and request-time enforcement. It is role-relevant and interview-plausible, but it is routine rather than deep: the answer is simply deny based on current stored role, with no multi-step trade-off or hard edge beyond replayed write rejection.

### pilot-v2 DEV206 — SQL · experienced

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Draft request 86:

An analytics job emits one report row per account. Tables: accounts(account_id, region; PK account_id); events(event_id, account_id, created_at, status, amount; PK event_id). Return: selected_event_id: Unique ID of latest eligible event per account; selected_created_at: Timestamp of selected event; eligible_amount_sum: Sum of eligible amounts at :as_of. Eligible rows have status='eligible' and created_at <= :as_of. Accounts with no eligible rows return NULL selected fields and zero aggregates. Compute latest row per account and aggregates independently; do not let the ranking filter change totals. Choose the latest by events.created_at, events.event_id descending; return selected_event_id. PostgreSQL 16. Eligible means status='eligible'. Latest eligible row per account; stable tie-break. Only rows created before :as_of. Output the selected unique row ID. No eligible row yields NULLs. How do you write the query so each account returns its latest eligible row plus independent aggregates at :as_of?

Draft request 87:

An analytics team needs one row per account for a monthly export. Tables: accounts(account_id, created_at; PK account_id); events(event_id, account_id, event_time, status, amount; PK event_id). Return: selected_event_id: Unique ID of latest eligible event per account.; eligible_amount_sum: Sum of eligible amounts in the scope.; eligible_event_count: Count of eligible events in the scope.. Eligible = status='posted'; scope = events with event_time < month_end. No eligible event => selected_event_id NULL; aggregates over no rows return NULL or 0 only if specified. Use left join from accounts; rank latest eligible event by event_time then event_id; aggregate independently under same snapshot. PostgreSQL 16. Snapshot is fixed at query start. Accounts with no eligible row still appear. Tie-break must be stable and visible. Return the selected row ID plus aggregates. Missing rows produce NULL metrics, not dropped accounts. How would you write the query so latest eligibility and aggregates stay correct under the snapshot and tie-break rules?

Hard construction attempt 1 rejected: Rendered question has 1010 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

Hard construction attempt 2 rejected: Rendered question has 1050 characters; shorten duplicate prose, keep essential contract facts (maximum 900)

### pilot-v2 DEV207 — HTTP · experienced

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

An import POST may time out after commit. POST /imports creates one durable import job. Effects: Enqueue a worker task.; Persist import records.. Idempotency-Key plus canonical request fingerprint. Authenticated principal and import operation. 409 Conflict; same key, changed body is rejected. Identical retries converge on one job; lost response can fetch stable pending/completed state. HTTP retries alone do not guarantee exactly-once downstream effects. PostgreSQL 16. One authenticated principal per request. Request keys and jobs live in one database. Concurrent retries can use the same key. A mistaken client can reuse that key with a different body. Return a retrievable pending/completed outcome. Same key and different payload must be rejected. How should the server claim the key and recover a lost response?

Draft request 89:

An import POST may time out after commit. POST /imports creates one durable import job. Effects: Enqueue a worker task.; Persist import records.. Idempotency-Key plus canonical request fingerprint. Authenticated principal and import operation. 409 Conflict; same key, changed body is rejected. Identical retries converge on one job; lost response can fetch stable pending/completed state. HTTP retries alone do not guarantee exactly-once downstream effects. PostgreSQL 16. One authenticated principal per request. Request keys and jobs live in one database. Concurrent retries can use the same key. A mistaken client can reuse that key with a different body. Return a retrievable pending/completed outcome. Same key and different payload must be rejected. How should the server claim the key and recover a lost response?

Hard construction attempt 1: accepted

### pilot-v2 DEV208 — Debugging · experienced

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

After a rollout, p99 wait time spikes but median query time and CPU stay flat. Compare: Leaked connections after request completion versus Legitimate long ownership during transactions. Bounded canary: cancel a few slow requests; compare acquisition wait, lease duration, and release traces; no pool resize. A leak and a slow transaction may coexist; logging must not expose secrets. Checked-out connections are capped per pool. PostgreSQL 16. Pool acquisition wait rises while query time stays flat. Use per-lease release traces and a bounded canary. Hypotheses can coexist. Correlate checkout/release with request IDs. Idle-in-transaction and a leak can both saturate the pool. Which intervention best distinguishes leak from long-held transactions?

Draft request 92:

After a rollout, p99 wait time spikes but median query time and CPU stay flat. Compare: Leaked connections after request completion versus Legitimate long ownership during transactions. Bounded canary: cancel a few slow requests; compare acquisition wait, lease duration, and release traces; no pool resize. A leak and a slow transaction may coexist; logging must not expose secrets. Checked-out connections are capped per pool. PostgreSQL 16. Pool acquisition wait rises while query time stays flat. Use per-lease release traces and a bounded canary. Hypotheses can coexist. Correlate checkout/release with request IDs. Idle-in-transaction and a leak can both saturate the pool. Which intervention best distinguishes leak from long-held transactions?

Hard construction attempt 1: accepted

### pilot-v3 DEV303 — Object-Oriented Programming · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Draft request 111:

A file-sync engine stores listeners on each folder node and delivers change events to them. One delivery sees a stable listener set for that folder. Caller registers listeners, triggers one change, then observes callbacks. If a listener mutates registration mid-delivery, that change affects later deliveries only. How should the folder API deliver one event from a stable snapshot when listeners may unsubscribe or add listeners during delivery?

Draft request 113:

A plugin manager dispatches file-events to registered listeners; listeners may add or remove listeners during dispatch. Each dispatch calls listeners from one stable snapshot only. Caller registers listeners, dispatches one event, then mutates registry for later events. A listener added or removed mid-dispatch must not affect that same event. How would you implement dispatch so one event sees a stable snapshot, while mid-dispatch add/remove changes only later events?

Hard construction attempt 1: This is a small OOP/event-dispatch problem with one clear implementation task and a mid-delivery mutation edge case. The contract is coherent and interview-plausible, but it is routine snapshot iteration rather than multi-constraint hard reasoning.

Hard construction attempt 2: Single bounded OOP implementation choice with a clear invariant and a concrete mutation timing edge case. The premise is sound, interview-plausible, and approachable for a fresher, but the reasoning depth is routine snapshot semantics rather than multi-constraint trade-off.

### pilot-v3 DEV304 — SQL · fresher

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

An analytics app tracks classes, attendance, and quiz attempts for each class. Tables: classes(class_id, name, is_active; PK class_id); attendance(attendance_id, class_id, present; PK attendance_id); quiz_attempts(attempt_id, class_id, passed; PK attempt_id). Return: class_id: Class identity.; present_count: Number of present attendance rows.; passed_count: Number of passed quiz attempts.; eligible: True only for active classes with at least 3 present and 2 passed.. Return every class once, regardless of child rows. Classes with no attendance or attempts stay in the result with zero counts; NULL child values do not count. Do not multiply counts across child tables; count each child table independently per class. How would you write one SQL query that returns each class’s eligibility flag and two independent counts without double-counting due to joins?

Draft request 116:

A museum analytics page must list each gallery's published exhibits, booked tours, and whether it is eligible for a promo. Tables: galleries(gallery_id, name, published_at, is_open; PK gallery_id); exhibits(exhibit_id, gallery_id, status, created_at; PK exhibit_id); tours(tour_id, gallery_id, starts_at, cancelled_at; PK tour_id). Return: gallery_id: Gallery unique id; published_exhibit_count: Published exhibits per gallery; active_tour_count: Non-cancelled tours starting this month per gallery; eligible_for_promo: True only for open galleries with at least one published exhibit. Count only exhibits with status='published'; count only tours starting in the current month and cancelled_at IS NULL. Keep galleries with zero matching exhibits or tours; counts must be 0, not NULL. Do not multiply counts across child tables; each child count must be independent per gallery. How would you write one SQL query that returns each gallery once with both counts and eligibility?

Draft request 118:

An analytics app tracks classes, attendance, and quiz attempts for each class. Tables: classes(class_id, name, is_active; PK class_id); attendance(attendance_id, class_id, present; PK attendance_id); quiz_attempts(attempt_id, class_id, passed; PK attempt_id). Return: class_id: Class identity.; present_count: Number of present attendance rows.; passed_count: Number of passed quiz attempts.; eligible: True only for active classes with at least 3 present and 2 passed.. Return every class once, regardless of child rows. Classes with no attendance or attempts stay in the result with zero counts; NULL child values do not count. Do not multiply counts across child tables; count each child table independently per class. How would you write one SQL query that returns each class’s eligibility flag and two independent counts without double-counting due to joins?

Hard construction attempt 1: Single focused fresher SQL task with precise output semantics. The main reasoning is independent aggregation without row multiplication plus a boolean derived from one count and a parent flag; no contradiction or hidden requirement.

Hard construction attempt 2: accepted

### pilot-v3 DEV305 — Security Fundamentals · fresher

Origin: fallback. Agent quality verdict: NOT REVIEWED (development).

Mira can edit a shared note until its grant is revoked; its owner retains edit access. An edit can read the old permission, then revocation can commit before the edit writes. Both policy and note live in one database. How would you make authorization plus mutation atomic so an edit ordered after revocation cannot commit, and construct a test for that interleaving without denying the owner's edit?

Draft request 121:

A document editor lets an ACTIVE writer save drafts; after downgrade, they keep read-only access. writer_A can write doc_7 before this change: role changes from ACTIVE_WRITER to READ_ONLY Afterward that action must be denied. Server-side authorization at the write commit boundary. Re-evaluate permission after the downgrade and before data update. How would you implement edit handling so a save cannot commit after a downgrade for the same writer and document?

Draft request 123:

A document service lets owners edit files; collaborators keep read-only access after downgrade. collaborator can write doc_17 before this change: role changes from writer to read_only Afterward that action must be denied. Enforce on the server before commit of the data update. Use the latest committed role state for the same principal and resource. How would you implement edit authorization so a write cannot commit if the user's role is downgraded after the initial check but before the data update?

Hard construction attempt 1: The prompt is a single fresher SWE/security implementation task with one edge case (downgrade racing a write). It is concrete and bounded, but the contract is somewhat underspecified about timing/transaction model, so clarity is not perfect. It is novel due to empty history.

Hard construction attempt 2: The prompt is a single bounded security implementation question with a clear race/edge case and one main decision: enforce write authorization using current committed role state before commit. It is plausible for a fresher interview, but the contract is slightly underspecified about the exact isolation/locking mechanism, so clarity is not perfect.

### pilot-v3 DEV306 — SQL · experienced

Origin: provider. Agent quality verdict: NOT REVIEWED (development).

An analytics job summarizes daily customer activity from event logs and account tiers. Tables: accounts(account_id, tier, created_at; PK account_id); events(event_id, account_id, event_at, event_type, score, is_eligible; PK event_id). Return: latest_event_id: selected events.event_id; eligible_event_count: Eligible event count in scope; score_sum: Sum of eligible scores in scope. PostgreSQL 16. Eligible means events.is_eligible=true. Scope is one snapshot day, from 2026-11-15 00:00:00 to 2026-11-16 00:00:00 UTC. If an account has no eligible event in scope, emit its account_id with latest_event_id NULL and counts zero. Join accounts to scoped events on account_id. Count and sum only eligible scoped events. Break ties by higher event_id after latest event_at. Choose the latest by events.event_at, events.event_id descending; return latest_event_id. How would you write one SQL query that returns each eligible account's latest eligible event row ID plus independent aggregates for the same snapshot, while preserving a stable tie-break?

Draft request 126:

An analytics job summarizes daily customer activity from event logs and account tiers. Tables: accounts(account_id, tier, created_at; PK account_id); events(event_id, account_id, event_at, event_type, score, is_eligible; PK event_id). Return: latest_event_id: selected events.event_id; eligible_event_count: Eligible event count in scope; score_sum: Sum of eligible scores in scope. PostgreSQL 16. Eligible means events.is_eligible=true. Scope is one snapshot day, from 2026-11-15 00:00:00 to 2026-11-16 00:00:00 UTC. If an account has no eligible event in scope, emit its account_id with latest_event_id NULL and counts zero. Join accounts to scoped events on account_id. Count and sum only eligible scoped events. Break ties by higher event_id after latest event_at. Choose the latest by events.event_at, events.event_id descending; return latest_event_id. How would you write one SQL query that returns each eligible account's latest eligible event row ID plus independent aggregates for the same snapshot, while preserving a stable tie-break?

Hard construction attempt 1: accepted

## Evidence preservation

The original Phase 6B/7 labels, thresholds and question files were not changed. `frozen-prior-evidence.json` and `final-integrity.json` verify their hashes. Per-stage manifest and production-code hashes identify the evaluated versions. `post-evaluation-code-changes.json` identifies the two production files changed only after the paid evaluation. Full raw model responses (including invalid or rejected structured drafts) and the budget ledger remain in ignored local storage; preserve that directory with this report.
