# Phase 7.2 — frozen question evidence

Date: 2026-11-16. Reviews are agent-only and provisional, not independent human or blinded judgments. Original outputs are reproduced without replacement wording. The previous Phase 7.1 holdouts remain unchanged. Production hashes and the manifest were frozen before this run; no production changes followed the holdout.

The AI authors the setting, primary ask and follow-up and selects a reviewed boundary/extension variant. The technical kernel is supplied by the application. “Hybrid AI” therefore does not mean unconstrained model-authored technical requirements; it is also distinct from returning a fixed fallback without using the provider output.

Rubric: R relevance, T technical correctness, L interview likelihood, H experience-relative Hard reasoning, E profile appropriateness, C clarity, F follow-up potential, each 0–2. PASS requires R=T=H=E=C=2, L/F≥1 and in-session novelty. Unavailable is not a passing question.

See [implementation, diagnosis, usage and results](phase72-question-reliability-results.md). Private raw provider payloads, RAG sources, full specifications, hashes and receipts remain under `storage/phase72/`.

## Fresh preregistered evaluation

Thirty normal configurations plus two deliberately exhausted security-family requests. Each profile has one 15-question history; its 16th request probes exhaustion. No permanent interview session or grading call was created. The operator exercises real generation/retrieval nodes, not a paid full adaptive interview.

### F01 — Data Structures · fresher · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.921 seconds end to end.

A media cache is tracking recently accessed clips.

Capacity K is a nonnegative integer. VIEW(id) marks it most recent; HAS(id) checks presence without changing order. HAS, refresh and eviction must each take constant time; new IDs evict the least recent only when full. A repeated VIEW at capacity must not evict another ID; K=0 retains nothing. DELETE(id) must also take constant time, including the most recent ID.

How would you keep VIEW, HAS, and DELETE all constant time while preserving recency and evicting only the least recent item when full?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Constant-time lookup, non-mutating presence, recency, deletion and zero capacity interact. The primary implementation task is clear and Fresher-relative Hard.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [85, 86, 87].

### F02 — Algorithms · fresher · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.853 seconds end to end.

A monitoring board merges many time windows over sorted events.

Events have sorted integer timestamps; duplicates are distinct events. Unsorted half-open windows may overlap or nest. Count events covered by any window once per event, avoiding a full event rescan for each window. A timestamp at a window's end is excluded; empty windows cover nothing; an empty event list returns zero. Many windows can be identical; memory need not depend on the timestamp range.

How would you count each covered event once, handle duplicate or nested window edges, and justify the total cost?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Union coverage must exclude half-open ends without double-counting duplicate events across nested/duplicate windows; asks for algorithm and cost, not a definition.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [88, 89, 90].

### F03 — Object-Oriented Programming · fresher · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 5.031 seconds end to end.

An event hub is updating subscribers during live callbacks.

Each dispatch uses its start-of-call listener snapshot; a nested dispatch uses current registrations. Listeners can add/remove listeners or dispatch recursively. Continue the outer snapshot even when a callback raises. Collect callback errors after delivery; do not skip outer listeners or corrupt later dispatches. Removing then re-adding a listener affects nested calls but not the captured outer snapshot.

How would you keep each dispatch isolated by its call-time snapshot while nested dispatches see current registrations and errors are collected after delivery?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Outer immutable listener snapshot, nested current registration and deferred callback errors require explicit per-dispatch state and reentrancy ownership.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [91, 92, 93].

### F04 — SQL · fresher · PASS

Origin: hybrid_ai. Requested Hard; type applied; 5.218 seconds end to end.

A social feed is tallying posts and likes per user.

Tables: users(id; PK id); posts(id, user_id; PK id); likes(id, user_id; PK id). One result row per users.id. Return: user_id: users.id; posts: post count; likes: like-record count. All rows are in scope; foreign keys user_id reference users.id. Include every user; each absent child count is zero. Multiple like rows by the same user count separately. Counts are independent: two posts and three likes must produce 2 and 3, not 6.

How would you write a query that keeps each user's post and like counts independent despite join multiplication?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Two independent one-to-many counts must preserve zero users and avoid multiplication; the 2/3 example makes the trap observable. Appropriate bounded Fresher Hard.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [94, 95, 96].

### F05 — HTTP · fresher · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.331 seconds end to end.

A job board must survive a post-commit crash in its submit path.

POST /jobs creates a durable job and retry record in one DB transaction. Effects: One job; no external call inside this request. Use a server-issued signed key with a 24-hour expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Racing identical calls and lost-response retries return the same committed job ID. Retain keys for 24 hours; reject older keys. External delivery is not guaranteed exactly once. A crash can occur after commit but before returning the job ID.

How would you atomically claim a request, detect conflicts, and recover the same job ID after commit but before the reply?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Atomic principal/key claim, body conflict, expiry and lost-response outcome require a concrete transactional algorithm, not just an HTTP header.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [97, 98, 99].

### F06 — REST APIs · fresher · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 5.407 seconds end to end.

A catalog service is merging edits to article metadata.

A document has title, summary and monotonically increasing version. PATCH carries base values for changed fields and an operation ID. Merge disjoint edits but reject any changed field whose current value differs from its base; record each operation outcome once. Conflict checks plus updates are atomic; response loss must not reapply a previously successful patch. Even if a field returns to its old value, operation identity must prevent duplicate application.

How would you atomically merge disjoint PATCH edits, reject stale field bases, and prevent a retry from applying the same change twice?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Field-level base checks, concurrent disjoint edits and stable operation outcomes must share an atomic boundary. The ABA-like same-value case cannot bypass replay identity.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [100, 101, 102].

### F07 — Git · fresher · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.723 seconds end to end.

A billing repo is cleaning up a shared commit chain after a bad parser fix.

Shared commits A,B,C are consecutive: A adds parseAmount accepting a trailing minus by mistake; B uses it for valid decimal prices; C fixes a typo. Remove trailing-minus acceptance while preserving B's valid-price feature, C and published history. Reverting A removes the helper B calls; tests must cover valid decimals and rejection of the faulty syntax. Other developers have already based work on C; rewriting their ancestry is not allowed.

How would you patch the dependency chain so valid prices keep working while the faulty syntax is removed without rewriting published ancestry?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Unlike the old unspecified faulty commit, trailing-minus behavior and B compatibility are concrete. A forward or selective inverse patch must preserve ancestry and test both behaviors.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [103, 104, 105].

### F08 — Testing · fresher · PASS

Origin: fallback. Requested Hard; type conceptual; 4.757 seconds end to end.

A cache write schedules expiry at t+60. A refresh creates a new generation and timer, but the old timer may still fire; at age >=60 the current generation expires. How would you build a deterministic test that proves an old expiry cannot delete the refreshed generation and the new one expires at its own boundary, without sleeps?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Returned fallback tests old-timer versus current-generation expiry, exact time boundary and no sleeps. In-session distinct; the rejected provider draft was also valid.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [106, 107, 108].

### F09 — Debugging · fresher · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.230 seconds end to end.

A support API is isolating user replies under load.

Compare: Responses use a cache key missing the user ID versus Concurrent handlers share mutable response data. Wrong-user responses occur during overlap. You can bypass the cache, control request overlap and tag user-specific results. The same request pair can run sequentially or with a barrier-controlled overlap. Both causes may coexist; report evidence separately rather than force a single diagnosis.

How would you design a test that separates cache-key leakage from shared mutable state when the same pair runs sequentially or with overlap?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Cache bypass and controlled overlap distinguish two possible causes; the question explicitly permits coexistence instead of treating timing as a disjoint explanation.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [109, 110, 111].

### F10 — Security Fundamentals · fresher · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.244 seconds end to end.

A helpdesk is issuing one-time password reset links.

A user's password can change only through a valid password-reset token. Tokens arrive in concurrent requests; store only a token digest, user binding and expiry, never the raw high-entropy token. Token validation/consumption and password update share one DB transaction; one token permits at most one successful change. The token expires after 15 minutes; invalid, expired or reused tokens change nothing. Two valid-token requests race, or the response is lost after commit; never apply a second password change. A crash before commit must leave both the password and token unchanged.

How would you store only a digest and make redemption and password change one atomic step so a race or retry never changes it twice?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Digest-only user-bound expiring token, racing requests, atomic consumption/password update and precommit crash provide a sound bounded security implementation problem.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [112, 113, 114].

### F11 — Data Structures · fresher · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.810 seconds end to end.

A live stack service must support pushes, pops, and undo.

PUSH(x), POP and MAX must take constant time; values may repeat. Empty POP/MAX return empty. MAX returns the largest remaining value. UNDO reverses the latest successful PUSH or POP, also in constant time. MAX, failed POP and UNDO itself do not enter undo history; empty UNDO is a no-op. Trace PUSH(4), PUSH(7), PUSH(7), POP, UNDO, POP, POP.

How would you track stack state so each successful push or pop can be undone in constant time without copying the whole stack?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Undo history is explicit and non-mutating operations excluded; duplicate maxima and inverse push/pop must stay constant time without snapshots. Distinct from recency eviction.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [115, 116, 117].

### F12 — Object-Oriented Programming · fresher · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.935 seconds end to end.

A warehouse tool imports product sheets from CSV or JSON.

CSV and JSON imports share exactly the same row-validation rules. Read, validate and then publish all rows, or report errors. Dry-run reports the same errors and never writes. A parse or validation failure exposes no partial dataset; adding a reader must not bypass validation. Readers can stream, but all-or-none publication still applies.

How would you keep validation and publish ownership inside one boundary so streaming readers still cannot bypass all-or-none rules?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Swappable streaming readers, shared validation, dry-run and all-or-none publication force a concrete responsibility/publication design. Distinct from listener reentrancy.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [118, 119, 120].

### F13 — SQL · fresher · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.907 seconds end to end.

A newsroom is picking each reporter’s latest approved edit.

Tables: users(id; PK id); edits(id, user_id, at, approved; PK id). One result row per users.id. Return: user_id: users.id; edit_id: selected edit ID. edits.user_id references users.id. Only approved=true with non-NULL at is eligible; no time cutoff. Include every user; no eligible edit gives NULL edit_id, even when ineligible edits exist. NULL approved is ineligible. Return at most one selected edit for each user, preserving users without edits. Choose the latest by edits.at, edits.id descending; return edit_id.

How would you choose the latest eligible edit per user without dropping users who have no match?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Latest eligible identity changes on time ties; unmatched/only-ineligible parents and NULL eligibility have defined outputs. More than a routine joined count and appropriate for Fresher Hard.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [121, 122, 123].

### F14 — HTTP · fresher · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 5.211 seconds end to end.

An inventory API is replaying edits after a flaky mobile sync.

PUT replaces a document using its expected version and client operation ID. Effects: Replace content and increment version once. Use a server-issued signed ID expiring in 24 hours; retain outcomes until expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Committed retries return the recorded outcome, even after a newer write or lost response. For unseen operations, stale versions conflict; retry lookup and update must share one DB transaction. Racing identical operations must converge without reverting a newer replacement.

How would you order retry lookup and the optimistic write so identical racing replays converge without undoing a newer replacement?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Already-committed replay lookup must precede stale-version rejection without overwriting another replacement; atomic version/result ownership is the central implementation decision.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [124, 125, 126].

### F15 — Security Fundamentals · fresher · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.467 seconds end to end.

A notes app is revoking old editor tokens while edits are in flight.

editor can write note before this change: The editor's grant is revoked; the owner retains access. Afterward that action must be denied. Policy and note share one DB. Revocation can commit between the edit's first permission read and its attempted write. A successful edit must be ordered before revocation; a stale-authorized in-flight edit must not commit after it. Old login tokens may still contain the editor role.

How would you make the write boundary atomic so a stale in-flight edit cannot commit after revocation?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

The permission was held before revocation; policy and mutation race in one DB. The ask requires ordering/atomic enforcement rather than just denying an expired token.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [127, 128, 129].

### F16 — Security Fundamentals · fresher · UNAVAILABLE

Origin: unavailable. Requested Hard; type applied; 1.765 seconds end to end.

Planned third security request after both distinct families were used. Explicit unavailability is correct coverage handling, not a passing delivered question.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [130].

### E01 — Data Structures · experienced · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.036 seconds end to end.

A payment ledger replays events after outages.

Each event ID requests one balance increment. A transactional DB with unique constraints and row locks is available; deduplication exceeds RAM. An increment and its durable completion identity must commit together; never lose or repeat that increment. IDs replay for at most 24 hours after first receipt; retain completion identities through that boundary. No probabilistic drops. A crash may occur after commit but before acknowledgment; memory caches may be empty on restart.

How would you keep increments correct when a crash can happen after commit but before ack, with no cache on restart?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Processing is explicitly a database balance increment, committed atomically with completion identity. Durable retention and bounded memory after lost acknowledgment are now answerable.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [131, 132, 133].

### E02 — Algorithms · experienced · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.658 seconds end to end.

A log archive needs exact leaderboards from a huge event-ID stream.

A finite file of event IDs exceeds RAM; distinct IDs also exceed RAM. Disk spill and multiple passes are allowed. Return exact top K IDs by frequency, breaking equal counts by ascending ID, using bounded RAM. Heavy skew can overflow one partition; include external I/O and a correctness argument, not only an in-memory heap.

How would you design the external passes, skew handling, and tie-breaking so every true top-K ID is still found?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

External storage and multiple passes are allowed; exact top-K, skew and deterministic ties require external aggregation/selection reasoning without an impossible RAM-only promise.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [134, 135, 136].

### E03 — Object-Oriented Programming · experienced · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 5.597 seconds end to end.

A media parser reads from both files and sockets.

A parser can inspect up to 64 KiB, commit consumed bytes, or roll back within that retained prefix. Backends are seekable files and non-seekable streams. Partial headers may be retried; cancellation must release owned resources. A partial read must not lose or double-consume bytes. Exceeding retained lookahead returns an explicit limit error. The parser borrows a reader; only the owner may close the underlying stream. Unavailable capability: Rewinding a non-seekable stream beyond the retained prefix.

How would you split ownership and buffering so cancellation and rollback never double-consume bytes or close a borrowed reader?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

64 KiB rollback boundary, ownership of borrowed sources and cancellation are explicit. Non-seekable rewind is labelled unavailable, not accidentally promised.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [137, 138, 139].

### E04 — SQL · experienced · PASS

Origin: fallback. Requested Hard; type applied; 4.959 seconds end to end.

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Returned fallback combines all-or-none stock updates, deadlock retries and postcommit durable confirmation work. The provider transaction draft was also a coherent single recovery workflow.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [140, 141, 142].

### E05 — HTTP · experienced · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.000 seconds end to end.

A task queue API must survive retries and worker handoff.

POST /jobs creates a durable job and retry record in one DB transaction. Effects: One job; no external call inside this request. Use a server-issued signed key with a 24-hour expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Racing identical calls and lost-response retries return the same committed job ID. Retain keys for 24 hours; reject older keys. External delivery is not guaranteed exactly once.

How would you atomically claim the identity, detect body conflicts, and recover the same job after a post-commit crash?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Principal-scoped signed identity, body conflict and commit/response-loss recovery provide a plausible experienced backend correctness task. Worker behavior is not falsely promised exactly once.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [143, 144, 145].

### E06 — REST APIs · experienced · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.028 seconds end to end.

A sync service is handing off from snapshots to a live feed.

A change feed has monotonic sequence IDs and deletion tombstones, retained for seven days. Updates and feed entries commit atomically. Paginated sync returns every committed change after a client's cursor, allowing duplicates that clients deduplicate by sequence ID. An expired cursor requires full resync. Resync and feed handoff must have no gaps while writes continue. Deletion tombstones older than retention must not silently strand a stale client.

How would you define the handoff and expired-cursor recovery so no committed change is missed or stranded?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

The snapshot-to-change-feed handoff must prevent gaps and explicitly recover beyond tombstone retention; an implementable lifecycle, not a watermark-only historical promise.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [146, 147, 148].

### E07 — Git · experienced · FAIL

Origin: hybrid_ai. Requested Hard; type applied; 6.613 seconds end to end.

A release train must recover from a bad rule after a format upgrade.

A deployed merge changes record format v1 to v2 irreversibly; later commits include a required security fix. Old binaries cannot read v2. Remove a new faulty validation rule without losing migrated data or the security fix; shared history must remain auditable. An old-binary rollback is unsafe. State the chosen compatibility boundary and verify mixed-version deployment behavior.

How would you pick the safe forward-recovery release path and prove what cannot roll back now?

Scores: R=2, T=2, L=2, H=1, E=2, C=2, F=1; session novelty=True.

The facts already rule out old binaries and prescribe forward recovery. The ask mostly repeats that choice; faulty rule behavior and mixed-version compatibility are too unspecified to force substantial implementation reasoning.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [149, 150, 151].

### E08 — Testing · experienced · FAIL

Origin: hybrid_ai. Requested Hard; type conceptual; 4.143 seconds end to end.

An index rebuild swaps generations while reads stay online.

An index rebuild swaps generations while unique-key inserts are acknowledged. Reads must contain all inserts acknowledged before their start. Use deterministic barriers to expose lost inserts at swap and mixed-generation read results, without timing sleeps. Control build start, acknowledged write, catch-up, publish and read boundaries; define the expected visible key set for each read. A reader paused on the old generation must complete safely after the new generation publishes.

How would you build a deterministic interleaving that proves a paused old reader still finishes safely after publish?

Scores: R=2, T=2, L=2, H=2, E=2, C=1, F=2; session novelty=True.

The body requires tests for lost acknowledged inserts and mixed generations, but the primary ask narrows to paused-reader lifetime only. A candidate can answer that narrower test without defining the write-visibility oracle; the intended scope needs clarification. Intro also repeats the first contract sentence.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [152, 153, 154].

### E09 — Debugging · experienced · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 5.032 seconds end to end.

A checkout spike is slowing a read service after deploy.

Compare: Some acquired DB connections never return to the pool versus Valid owners hold connections across slow non-DB work. Acquisition wait rises while query duration is flat. Trace per-lease IDs, owner lifetimes and release events; run a bounded canary. Do not increase the pool during diagnosis; account for tracing overhead. Both causes may coexist; report evidence separately rather than force a single diagnosis.

How would you bound a canary to tell leaked leases from long owner phases without resizing the pool?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Lease identity, owner lifetimes, release evidence and a bounded live canary support a discriminating experiment. Both causes can coexist and no preferred pool-size fix is assumed.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [155, 156, 157].

### E10 — Security Fundamentals · experienced · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.333 seconds end to end.

A help desk resets passwords under concurrent traffic.

A user's password can change only through a valid password-reset token. Tokens arrive in concurrent requests; store only a token digest, user binding and expiry, never the raw high-entropy token. Token validation/consumption and password update share one DB transaction; one token permits at most one successful change. The token expires after 15 minutes; invalid, expired or reused tokens change nothing. Two valid-token requests race, or the response is lost after commit; never apply a second password change. Issuing a new token invalidates earlier tokens atomically, even if old redemption is in flight.

How would you store reset tokens and make reissue plus redemption atomic so one valid token can never change the password twice?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Concurrent token reissue versus redemption introduces a cross-record ordering requirement beyond ordinary consume-once. Atomic invalidation, expiry and postcommit replay are technically coherent.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [158, 159, 160].

### E11 — Data Structures · experienced · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 4.212 seconds end to end.

A device cache serves lookups while background loads still run.

A bounded cache supports GET, PUT and DELETE while per-key loads complete asynchronously. A load started before a newer PUT or DELETE must never overwrite it or resurrect deleted data. Keys may be evicted and reinserted while old loads run; metadata and in-flight work must remain bounded. Cancellation is advisory: a canceled loader may still complete.

How would you keep load publication tied to the right key version so a canceled or stale load never wins after PUT or DELETE?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Old in-flight publication must not overwrite PUT/DELETE or a reinserted generation. Bounded metadata and advisory cancellation introduce ownership/ABA/backpressure trade-offs.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [161, 162, 163].

### E12 — Object-Oriented Programming · experienced · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.666 seconds end to end.

A plugin host is retrying jobs after a crash during cleanup.

Plugins reserve resources privately; only an atomic manifest update makes a complete result visible. Use a durable run ID: acquire, transform, publish or cancel; query run status before retry after an unknown timeout. Failure leaves no partial visible result. Cleanup is idempotent and must never remove an already published result. Compensation can itself fail and must leave recoverable cleanup work. Unavailable capability: A universal always-successful publish operation across arbitrary plugins.

How would you model plugin capabilities and retry states so a failed compensation stays recoverable without exposing partial results?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Private reservations, atomic manifest publication, persisted run identity and failed-compensation recovery are concrete. Unavailable universal publish is explicitly qualified and not a success guarantee.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [164, 165, 166].

### E13 — SQL · experienced · PASS

Origin: hybrid_ai. Requested Hard; type applied; 4.177 seconds end to end.

A finance dashboard is reconciling monthly account snapshots.

Tables: accounts(id; PK id); events(id, account_id, at, eligible, amount; PK id). One result row per accounts.id. Return: account_id: accounts.id; event_id: selected event ID; count: eligible event count; sum: eligible non-NULL amount sum. One statement snapshot; scope is UTC [2026-01-01,2026-02-01). eligible=true and non-NULL at; account_id references accounts.id. Include all accounts; no eligible event gives NULL event_id, count 0 and sum 0; all-NULL amounts sum to 0. NULL eligible is ineligible. Latest identity and aggregates use the same scoped rows; ranking must not reduce the aggregate to one row. Choose the latest by events.at, events.id descending; return event_id.

How would you keep the chosen event and the aggregates on the same snapshot without multiplying counts or sums?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Latest unique identity and independent scoped count/sum use one snapshot; ties, missing parents, ineligible and all-NULL cases have exact outputs. SQL example execution corroborates the semantics.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [167, 168, 169].

### E14 — HTTP · experienced · PASS

Origin: hybrid_ai. Requested Hard; type conceptual; 6.346 seconds end to end.

A document editor is syncing edits across flaky clients.

PUT replaces a document using its expected version and client operation ID. Effects: Replace content and increment version once. Use a server-issued signed ID expiring in 24 hours; retain outcomes until expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Committed retries return the recorded outcome, even after a newer write or lost response. For unseen operations, stale versions conflict; retry lookup and update must share one DB transaction. Racing identical operations must converge without reverting a newer replacement.

How would you order retry lookup and the optimistic replace so identical races converge without undoing a newer write?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Atomic operation outcome lookup versus optimistic version update must recover an earlier success without reverting a newer write. This is a different task from creating one job.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [170, 171, 172].

### E15 — Security Fundamentals · experienced · PASS

Origin: hybrid_ai. Requested Hard; type gap_probe; 4.422 seconds end to end.

A report export is queued behind a shared download link.

tenant_user can download export before this change: The user's tenant grant is revoked during an export. Afterward that action must be denied. Queued jobs run with service credentials; generated results are private until publication; CDN links and policy caches may be stale. Within 30 seconds of revocation no new download may start; already delivered bytes cannot be recalled. Recheck original principal at execution/publication. An unavailable policy source must fail closed, including a cold CDN edge.

How would you fail closed on a cold policy edge while enforcing execution, publication, and download checks within the revocation window?

Scores: R=2, T=2, L=2, H=2, E=2, C=2, F=2; session novelty=True.

Original principal must govern execution/publication/download, including cold policy failures and stale CDN links. The 30-second window excludes already-delivered bytes; no impossible recall is promised.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [173, 174, 175].

### E16 — Security Fundamentals · experienced · UNAVAILABLE

Origin: unavailable. Requested Hard; type applied; 1.273 seconds end to end.

Planned third security request exhausts reviewed same-profile families; explicit unavailable before construction, not a fabricated successful question.

Evidence: `holdout-results.json`, `holdout-agent-review.json`; request IDs [176].

## All screened-draft decisions

All 30 screened drafts are covered, including both rejected positives. The two safe fallbacks above are different questions from those rejected drafts.

| Case | Model gate | Agent rubric | Error |
|---|---|---|---|
| F01 | Accept | Pass | Agreement |
| F02 | Accept | Pass | Agreement |
| F03 | Accept | Pass | Agreement |
| F04 | Accept | Pass | Agreement |
| F05 | Accept | Pass | Agreement |
| F06 | Accept | Pass | Agreement |
| F07 | Accept | Pass | Agreement |
| F08 | Reject | Pass | False rejection |
| F09 | Accept | Pass | Agreement |
| F10 | Accept | Pass | Agreement |
| F11 | Accept | Pass | Agreement |
| F12 | Accept | Pass | Agreement |
| F13 | Accept | Pass | Agreement |
| F14 | Accept | Pass | Agreement |
| F15 | Accept | Pass | Agreement |
| E01 | Accept | Pass | Agreement |
| E02 | Accept | Pass | Agreement |
| E03 | Accept | Pass | Agreement |
| E04 | Reject | Pass | False rejection |
| E05 | Accept | Pass | Agreement |
| E06 | Accept | Pass | Agreement |
| E07 | Accept | Fail | False acceptance |
| E08 | Accept | Fail | False acceptance |
| E09 | Accept | Pass | Agreement |
| E10 | Accept | Pass | Agreement |
| E11 | Accept | Pass | Agreement |
| E12 | Accept | Pass | Agreement |
| E13 | Accept | Pass | Agreement |
| E14 | Accept | Pass | Agreement |
| E15 | Accept | Pass | Agreement |

### Screen disagreement F08

A search panel is comparing two live queries for one list.

Search requests A then B can finish in either order; cancellation is advisory and canceled A may still return. Only the latest query B may update visible results; a B failure leaves a B-specific error and must not reveal stale A results. Control each response with deferred completions, no sleeps or real network; include completion after component unmount. Complete B before A, and separately fail B before A succeeds.

How would you test that only the latest query can change visible state when B finishes before A, and when B fails before A succeeds?

Model: {"minimum_reasoning": "The question asks for deterministic tests but doesn’t specify observable UI states/props to assert.", "blocking_issue": "clarity", "quote": "visible state", "reason": "Without naming the visible state shape, a fresher can’t tell what exact assertions prove B-only updates or B-specific error handling."}

Agent: Visible B results and B-specific errors are sufficient observable assertions; naming component props is an implementation choice, not a missing contract.

### Screen disagreement E04

A warehouse is confirming reservation requests under heavy contention.

Tables: requests(id, body_hash, status; PK id); stock(sku, qty; PK sku); lines(id, request_id, sku, qty; PK id); outbox(id, request_id; PK id). One result row per requests.id. Return: request_id: requests.id; status: committed reservation outcome. Caller supplies a unique request ID and positive item quantities. lines.request_id/outbox.request_id reference requests.id; lines.sku references stock.sku. Missing SKU or insufficient stock rejects all items. Reusing an ID with a changed body conflicts. Concurrent requests can deadlock; rollback and retry the entire transaction. Commit decrements, request and one outbox row together; no remote call. Same ID/body returns the committed outcome; rollback leaves no claim or reservation.

How would you retry deadlocked transactions and still return the committed outcome for a reused request ID?

Model: {"minimum_reasoning": "Deadlock retry is clear, but same-ID replay needs a durable identity lookup to return the prior committed outcome after rollback.", "blocking_issue": "scope", "quote": "How would you retry deadlocked transactions", "reason": "The ask centers on retrying deadlocks; it also demands idempotent return for reused IDs. That adds a separate recovery path beyond the retry focus."}

Agent: Same-ID recovery and deadlock rollback are one transaction/retry lifecycle. The contract now explicitly gives same-body committed outcomes and rollback cleanup.

### Screen disagreement E07

A release train must recover from a bad rule after a format upgrade.

A deployed merge changes record format v1 to v2 irreversibly; later commits include a required security fix. Old binaries cannot read v2. Remove a new faulty validation rule without losing migrated data or the security fix; shared history must remain auditable. An old-binary rollback is unsafe. State the chosen compatibility boundary and verify mixed-version deployment behavior.

How would you pick the safe forward-recovery release path and prove what cannot roll back now?

Model: {"minimum_reasoning": "The ask is about recovery/rollback boundaries after an irreversible format migration plus a security fix. It’s interview-plausible and role-relevant.", "blocking_issue": "none", "quote": "", "reason": "It is technically sound, experienced-level, and answerable: safe forward recovery, mixed-version behavior, and unrevertable state are all explicit."}

Agent: The facts already rule out old binaries and prescribe forward recovery. The ask mostly repeats that choice; faulty rule behavior and mixed-version compatibility are too unspecified to force substantial implementation reasoning.

### Screen disagreement E08

An index rebuild swaps generations while reads stay online.

An index rebuild swaps generations while unique-key inserts are acknowledged. Reads must contain all inserts acknowledged before their start. Use deterministic barriers to expose lost inserts at swap and mixed-generation read results, without timing sleeps. Control build start, acknowledged write, catch-up, publish and read boundaries; define the expected visible key set for each read. A reader paused on the old generation must complete safely after the new generation publishes.

How would you build a deterministic interleaving that proves a paused old reader still finishes safely after publish?

Model: {"minimum_reasoning": "The ask needs a concrete concurrent interleaving/oracle; it already gives boundaries and the paused-reader safety condition.", "blocking_issue": "none", "quote": "", "reason": "This is directly role-relevant, technically sound, Hard for experienced testing, and answerable with meaningful follow-up."}

Agent: The body requires tests for lost acknowledged inserts and mixed generations, but the primary ask narrows to paused-reader lifetime only. A candidate can answer that narrower test without defining the write-visibility oracle; the intended scope needs clarification. Intro also repeats the first contract sentence.

## Fresh OOP verification before hybrid changes

Four development cases used the final Phase 7.1 compiler, before Phase 7.2 generation changes. Two failed construction/screening and used fallbacks; two provider questions retained the unavailable-capability qualifier. Agent review finds no critical false guarantee in these two provider outputs. This is not independent human validation. Some wording remains awkward.

### OOP01 — fresher · fallback

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Hard construction attempt 1 rejected: 1 validation error for ProblemSpecification
technical_contract.oop
  Value error, Cannot promise an achievable contract while declaring its capability unavailable [type=value_error, input_value={'kind': 'oop', 'interfac...visible after failure.'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.14/v/value_error

### OOP02 — fresher · fallback

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Hard construction attempt 1: The prompt is a focused fresher OOP design task with a concrete invariant and one failure edge. It is technically sound and interview-plausible, but the core reasoning is a standard staged-write/atomic-publication pattern rather than multi-constraint Hard depth. It is clear and supports follow-ups on encryption, rollback, and reader consistency.

### OOP03 — experienced · provider

A parser reads headers from seekable files and network streams. Peeked bytes remain available until consumed or discarded. Parser may inspect a prefix, rollback once, then resume or cancel. Partial header reads must not lose buffered bytes. Unavailable capability: Universal rewind on all readers. How would you design the reader interface and buffering so the parser can do bounded lookahead and rollback after a partial header?

Hard construction attempt 1: accepted

### OOP04 — experienced · provider

A plugin pipeline acquires cache, temp file, and lock resources in order. A published result appears only after all stages succeed. Caller may retry after timeout using the same pipeline request id. Canceled or failed runs must leave no visible output. Unavailable capability: No universally successful publish method exists. How should you design interfaces and caller steps so no partial result is visible after cancel, failure, or retry?

Hard construction attempt 1: accepted

## Development pilots — retained failures

The first pilot had seven format failures (prose limits), one semantic rejection and zero provider deliveries. The second pilot explicitly stated the limits and had zero format failures, four provider deliveries and four screening rejections. These are development runs and are not pooled into the unseen pass rate. No independent per-question quality verdict is assigned to them.

### pilot DEV01 — Object-Oriented Programming · fresher

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Draft request 29:

{"family_id":"staged_writer","variant":"extension","scenario":"A team tool lets a user stage draft chunks privately before making a document visible to readers.","reasoning_decision":"How would you structure object ownership so a publish either exposes the previous complete document or the new complete document, while a failed cleanup can be retried later without ever removing a successfully published document?","follow_up_direction":"Ask how you would separate private staging state from the visible document so cancel, publish, and retry-safe cleanup stay correct under mid-chunk encryption failure."}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "staged_writer"}

### pilot DEV02 — Object-Oriented Programming · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A parser reads from seekable files or non-seekable network streams. It needs at most 64 KB of lookahead, may roll back an incomplete header, and must release resources on cancellation. How would you design the reader objects and caller workflow so retrying a parse does not consume bytes twice or leak a stream, without buffering the whole file?

Draft request 31:

{"family_id":"plugin_cleanup","variant":"extension","scenario":"A workflow engine runs plugins that reserve private resources before a manifest update can make the result visible.","reasoning_decision":"Design the plugin capabilities and state transitions so callers can tell whether a run is owned, published, canceled, or left needing cleanup after a failed compensation, without ever exposing a partial visible result.","follow_up_direction":"Ask how the API should represent recoverable cleanup work after compensation fails, so a later retry can resume safely without risking an already published result."}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "plugin_cleanup"}

### pilot DEV03 — SQL · fresher

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Draft request 33:

A dashboard lists every user and, if present, their latest approved edit.

Tables: users(id; PK id); edits(id, user_id, at, approved; PK id). One result row per users.id. Return: user_id: users.id; edit_id: selected edit ID. edits.user_id references users.id. Only approved=true with non-NULL at is eligible; no time cutoff. Include every user; no eligible edit gives NULL edit_id, even when ineligible edits exist. NULL approved is ineligible. Return at most one selected edit for each user, preserving users without edits. Choose the latest by edits.at, edits.id descending; return edit_id.

How would you write the query so each user keeps at most one newest eligible edit by at then id, while still returning users who have no eligible edit at all?

Hard family review: {"minimum_reasoning":"The query is straightforward latest-row selection with a left join and null-safe eligibility filter; not Hard for fresher.","blocking_issue":"depth","quote":"latest approved edit","reason":"Only asks for a standard top-1-per-group lookup; no harder lifecycle, trade-off, or controlled race aspect is required."}

Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "latest_eligible_identity"}

### pilot DEV04 — SQL · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Draft request 36:

{"family_id":"reservation_outbox","variant":"extension","scenario":"An order service reserves inventory for a unique request ID, writes the request, line items, stock changes, and an outbox record in one SQL transaction, and may see deadlocks when requests overlap.","reasoning_decision":"How would you structure the transaction and retry logic so a repeated request does not reserve twice, a changed body is rejected under the same ID, and deadlock retries still keep the stock, request, and outbox writes consistent?","follow_up_direction":"If a worker publishes the outbox message and crashes before marking it sent, how should the system avoid duplicate confirmations without moving the remote call into the reservation transaction?"}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "reservation_outbox"}

### pilot DEV05 — HTTP · fresher

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

An editor loads a document and its version, then saves a full replacement. Two tabs load version 7; one saves before the other. The server can atomically compare versions and update. How would you design the HTTP save request and response so the stale tab cannot silently overwrite the first save, including its retry after a lost response?

Draft request 38:

{"family_id":"idempotent_create","variant":"boundary","scenario":"A payroll service accepts POST /jobs to create a durable job record with a signed retry key.","reasoning_decision":"How would you make one transaction atomically claim the signed key, detect body conflicts, and recover so a crash after commit but before the response still lets a retried identical call return the same job ID?","follow_up_direction":"If the first response is lost, what record lookup or state transition would you rely on to distinguish a safe retry from a conflicting reuse of the same key?"}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "idempotent_create"}

### pilot DEV06 — Security Fundamentals · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A report export runs asynchronously and can be downloaded through a cached sharing link. Access must be revoked within 30 seconds of team removal even if the export was queued earlier. How would you enforce this contract across the job, download authorization and cache without assuming an expiring URL alone provides timely revocation?

Draft request 40:

{"family_id":"single_use_reset","variant":"extension","scenario":"A customer portal sends password reset emails while users may request a new reset link before the previous one is used.","reasoning_decision":"Design the token record and transaction flow so a reset token is redeemed exactly once, and explain how you prevent an older in-flight redemption from succeeding after a newer token has been issued for the same user.","follow_up_direction":"If the password-reset service becomes briefly unavailable, how would you keep the one-time and reissue rules correct when requests are retried?"}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "single_use_reset"}

### pilot DEV07 — Git · fresher

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

On a shared Git branch, commit A adds a parser function, B calls it, and C fixes an unrelated typo. A must be undone without rewriting history, but reverting A alone breaks B. How would you prepare and verify a safe revert that preserves C?

Draft request 42:

{"family_id":"dependent_revert","variant":"boundary","scenario":"A shared pricing library has three commits in the published branch: A introduced a parseAmount helper that wrongly accepts a trailing minus, B started using that helper for valid decimal prices, and C only corrected a typo. A teammate has already built work on top of C.","reasoning_decision":"What recovery patch would you choose so the branch stops accepting trailing-minus amounts while keeping the valid decimal behavior from B and the published ancestry from C intact, and how would you verify the patch in an order that avoids breaking the downstream work?","follow_up_direction":"If reverting A would remove code that B depends on, explain the safer dependency-aware alternative and the exact tests you would run for both a valid decimal price and the rejected trailing-minus case."}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "dependent_revert"}

### pilot DEV08 — Data Structures · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A messaging consumer deduplicates event IDs for 24 hours at 50,000 events/second, but cannot keep the full window in RAM. Replays can arrive after restart and false positives would lose messages. How would you structure durable state and memory acceleration so a crash cannot mark an unprocessed event complete?

Draft request 44:

{"family_id":"durable_dedup","variant":"extension","scenario":"A payment ledger service ingests event IDs and applies one balance increment per ID. The service can crash after the database commit but before sending acknowledgment, and its in-memory cache may be empty after restart.","reasoning_decision":"How would you design the processing path and retention boundary so each increment and its durable completion identity are committed together, while keeping memory bounded and still preventing repeats across the 24-hour replay window?","follow_up_direction":"If a redelivery arrives after the retention window has expired, what guarantee no longer holds, and how would you explain that trade-off to the product team?"}

Hard family diagnostic: {"stage": "format", "error": "ValidationError", "family": "durable_dedup"}

### pilot-v2 DEV201 — Object-Oriented Programming · fresher

Delivered origin: hybrid AI; quality verdict: NOT REVIEWED (development).

An editor app is staging article chunks before one publish.

Readers see the old complete document or the new complete document, never a prefix. A caller stages chunks privately, then publishes or cancels. Atomic replacement is available; encryption can fail mid-chunk. Failure before replacement preserves old content; cancellation cleans private staging, not the visible document. A failed cleanup may be retried without deleting a successfully published document.

How would you keep staged ownership clear, cancel safely, and retry cleanup without risking a published article?

Draft request 46:

An editor app is staging article chunks before one publish.

Readers see the old complete document or the new complete document, never a prefix. A caller stages chunks privately, then publishes or cancels. Atomic replacement is available; encryption can fail mid-chunk. Failure before replacement preserves old content; cancellation cleans private staging, not the visible document. A failed cleanup may be retried without deleting a successfully published document.

How would you keep staged ownership clear, cancel safely, and retry cleanup without risking a published article?

Hard family review: {"minimum_reasoning":"The prompt is clear and scoped; no blocking defect.","blocking_issue":"none","quote":"","reason":"It’s role-relevant, fresh, technically sound, and answerable for a fresher OOP design with meaningful follow-up on ownership, cancel, and retry."}

Hard family diagnostic: {"stage": "screen", "accepted": true, "family": "staged_writer"}

### pilot-v2 DEV202 — Object-Oriented Programming · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A parser reads from seekable files or non-seekable network streams. It needs at most 64 KB of lookahead, may roll back an incomplete header, and must release resources on cancellation. How would you design the reader objects and caller workflow so retrying a parse does not consume bytes twice or leak a stream, without buffering the whole file?

Draft request 49:

A plugin host is retrying failed jobs after a lost network reply.

Plugins reserve resources privately; only an atomic manifest update makes a complete result visible. Use a durable run ID: acquire, transform, publish or cancel; query run status before retry after an unknown timeout. Failure leaves no partial visible result. Cleanup is idempotent and must never remove an already published result. Compensation can itself fail and must leave recoverable cleanup work. Unavailable capability: A universal always-successful publish operation across arbitrary plugins.

How would you model plugin capabilities and retry states when compensation may fail but must remain recoverable?

Hard family review: {"minimum_reasoning":"Reject: asks to model capabilities and retry states, but no concrete failure lifecycle or state machine is specified for recoverable compensation.","blocking_issue":"depth","quote":"compensation may fail but must remain recoverable","reason":"This states the constraint but not the concrete lifecycle or transitions needed to judge a hard, answerable OOP design question."}

Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "plugin_cleanup"}

### pilot-v2 DEV203 — SQL · fresher

Delivered origin: hybrid AI; quality verdict: NOT REVIEWED (development).

A moderation dashboard is listing each user’s most recent approved edit.

Tables: users(id; PK id); edits(id, user_id, at, approved; PK id). One result row per users.id. Return: user_id: users.id; edit_id: selected edit ID. edits.user_id references users.id. Only approved=true with non-NULL at is eligible; no time cutoff. Include every user; no eligible edit gives NULL edit_id, even when ineligible edits exist. NULL approved is ineligible. Return at most one selected edit for each user, preserving users without edits. Choose the latest by edits.at, edits.id descending; return edit_id.

How would you select the latest eligible edit per user while still returning users with no matching edit?

Draft request 52:

A moderation dashboard is listing each user’s most recent approved edit.

Tables: users(id; PK id); edits(id, user_id, at, approved; PK id). One result row per users.id. Return: user_id: users.id; edit_id: selected edit ID. edits.user_id references users.id. Only approved=true with non-NULL at is eligible; no time cutoff. Include every user; no eligible edit gives NULL edit_id, even when ineligible edits exist. NULL approved is ineligible. Return at most one selected edit for each user, preserving users without edits. Choose the latest by edits.at, edits.id descending; return edit_id.

How would you select the latest eligible edit per user while still returning users with no matching edit?

Hard family review: {"minimum_reasoning":"Need a left join with eligibility in the join/filter and a per-user latest-row selector.","blocking_issue":"none","quote":"","reason":"The task is clear, role-relevant, and answerable as a standard SQL latest-per-group with preserved unmatched users."}

Hard family diagnostic: {"stage": "screen", "accepted": true, "family": "latest_eligible_identity"}

### pilot-v2 DEV204 — SQL · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Draft request 55:

A ticketing service is reserving inventory under peak load.

Tables: requests(id, body_hash, status; PK id); stock(sku, qty; PK sku); lines(id, request_id, sku, qty; PK id); outbox(id, request_id; PK id). One result row per requests.id. Return: request_id: requests.id; status: committed reservation outcome. Caller supplies a unique request ID and positive item quantities. lines.request_id/outbox.request_id reference requests.id; lines.sku references stock.sku. Missing SKU or insufficient stock rejects all items. Reusing an ID with a changed body conflicts. Concurrent requests can deadlock; rollback and retry the entire transaction. Commit stock decrements, successful request and one outbox row together; retries must not reserve twice. No remote call inside the transaction.

How would you make the reservation transaction safe to retry after deadlocks while keeping the outbox and stock change consistent?

Hard family review: {"minimum_reasoning":"The retry safety requirement is clear, but the question never states how the idempotency/body_hash check should behave on a retried deadlocked transaction, so a candidate can’t know the required conflict path.","blocking_issue":"clarity","quote":"Reusing an ID with a changed body conflicts.","reason":"This omits the retry rule for same ID/same body after rollback or partial failure, so the intended safe-retry invariant is underspecified."}

Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "reservation_outbox"}

### pilot-v2 DEV205 — HTTP · fresher

Delivered origin: hybrid AI; quality verdict: NOT REVIEWED (development).

A hiring portal is saving job posts during repeated submits.

POST /jobs creates a durable job and retry record in one DB transaction. Effects: One job; no external call inside this request.. Use a server-issued signed key with a 24-hour expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Racing identical calls and lost-response retries return the same committed job ID. Retain keys for 24 hours; reject older keys. External delivery is not guaranteed exactly once. A crash can occur after commit but before returning the job ID.

How would you atomically claim a signed key, detect body conflicts, and recover the committed job ID after a crash before response?

Draft request 58:

A hiring portal is saving job posts during repeated submits.

POST /jobs creates a durable job and retry record in one DB transaction. Effects: One job; no external call inside this request.. Use a server-issued signed key with a 24-hour expiry. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Racing identical calls and lost-response retries return the same committed job ID. Retain keys for 24 hours; reject older keys. External delivery is not guaranteed exactly once. A crash can occur after commit but before returning the job ID.

How would you atomically claim a signed key, detect body conflicts, and recover the committed job ID after a crash before response?

Hard family review: {"minimum_reasoning":"The prompt is clear and answerable. It asks for concrete atomic claim, conflict detection, and crash recovery within one transactional idempotent-create flow.","blocking_issue":"none","quote":"","reason":"It is directly role-relevant, technically sound, appropriately hard for fresher, and includes a meaningful failure/retry scenario with follow-up potential."}

Hard family diagnostic: {"stage": "screen", "accepted": true, "family": "idempotent_create"}

### pilot-v2 DEV206 — Security Fundamentals · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A report export runs asynchronously and can be downloaded through a cached sharing link. Access must be revoked within 30 seconds of team removal even if the export was queued earlier. How would you enforce this contract across the job, download authorization and cache without assuming an expiring URL alone provides timely revocation?

Draft request 61:

A helpdesk app issues password reset links for locked accounts.

A user's password can change only through a valid password-reset token. Tokens arrive in concurrent requests; store only a token digest, user binding and expiry, never the raw high-entropy token. Token validation/consumption and password update share one DB transaction; one token permits at most one successful change. The token expires after 15 minutes; invalid, expired or reused tokens change nothing. Two valid-token requests race, or the response is lost after commit; never apply a second password change. Issuing a new token invalidates earlier tokens atomically, even if old redemption is in flight.

How would you store, redeem, and reissue reset tokens so a race or replay still allows only one password change?

Hard family diagnostic: {"stage": "screen", "error": "ValueError", "family": "single_use_reset"}

### pilot-v2 DEV207 — Git · fresher

Delivered origin: hybrid AI; quality verdict: NOT REVIEWED (development).

A payments repo must fix a shared parse bug without upsetting released work.

Shared commits A,B,C are consecutive: A adds parseAmount accepting a trailing minus by mistake; B uses it for valid decimal prices; C fixes a typo. Remove trailing-minus acceptance while preserving B's valid-price feature, C and published history. Reverting A removes the helper B calls; tests must cover valid decimals and rejection of the faulty syntax. Other developers have already based work on C; rewriting their ancestry is not allowed.

How would you preserve C and B’s valid-price behavior while removing A’s bad trailing-minus path without rewriting shared ancestry?

Draft request 64:

A payments repo must fix a shared parse bug without upsetting released work.

Shared commits A,B,C are consecutive: A adds parseAmount accepting a trailing minus by mistake; B uses it for valid decimal prices; C fixes a typo. Remove trailing-minus acceptance while preserving B's valid-price feature, C and published history. Reverting A removes the helper B calls; tests must cover valid decimals and rejection of the faulty syntax. Other developers have already based work on C; rewriting their ancestry is not allowed.

How would you preserve C and B’s valid-price behavior while removing A’s bad trailing-minus path without rewriting shared ancestry?

Hard family review: {"minimum_reasoning":"No defect: it’s a valid dependency-aware Git recovery scenario with a clear follow-up.","blocking_issue":"none","quote":"","reason":"Requires choosing a non-rewrite recovery path that preserves C and B while removing A’s bug and verifying both behaviors."}

Hard family diagnostic: {"stage": "screen", "accepted": true, "family": "dependent_revert"}

### pilot-v2 DEV208 — Data Structures · experienced

Delivered origin: fallback; quality verdict: NOT REVIEWED (development).

A messaging consumer deduplicates event IDs for 24 hours at 50,000 events/second, but cannot keep the full window in RAM. Replays can arrive after restart and false positives would lose messages. How would you structure durable state and memory acceleration so a crash cannot mark an unprocessed event complete?

Draft request 67:

A billing worker replays event IDs after a crash.

Each event ID requests one balance increment in a database. Redeliveries can follow a crash; deduplication exceeds RAM. An increment and its durable completion identity must commit together; never lose or repeat that increment. IDs replay for at most 24 hours after first receipt; retain completion identities through that boundary. No probabilistic drops. A crash may occur after commit but before acknowledgment; memory caches may be empty on restart.

How would you keep the increment and completion identity durable across a crash before ack, while bounding memory use?

Hard family review: {"minimum_reasoning":"The task is under-specified for a senior design question: it asks how to do durability/bounded memory but gives no storage constraints or DB capabilities.","blocking_issue":"clarity","quote":"How would you keep","reason":"The prompt asks for a design but omits the persistence primitives and system limits needed to choose a concrete durable dedup strategy, so answers can’t be meaningfully evaluated."}

Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "durable_dedup"}

## Development calibration — unchanged reference labels

Two passes over the same 16 development cases; not an unseen benchmark. Gate totals count an invalid review as rejection, with the invalid result explicitly shown. Valid-review-only false accepts are 1/8 then 4/8; overall gate false accepts are 1/9 then 4/9. All seven positive references had valid reviews.

| Case | Frozen label | Initial screen | Revised screen |
|---|---|---|---|
| ref-F01 | Pass | Accept | Reject |
| ref-E05 | Pass | Accept | Accept |
| ref-E09 | Pass | Reject | Reject |
| ref-E03 | Fail | INVALID → reject | Accept |
| ref-F02 | Fail | Reject | Reject |
| ref-F03 | Fail | Reject | Reject |
| ref-E04 | Fail | Reject | Accept |
| ref-P7F03 | Pass | Reject | Accept |
| ref-P7F04 | Fail | Reject | Accept |
| ref--refinedR04 | Fail | Reject | Accept |
| ref-P7F09 | Fail | Accept | Reject |
| ref-P7E06 | Pass | Reject | Accept |
| familiar-not-repeated | Pass | Accept | Reject |
| near-duplicate | Fail | Reject | INVALID → reject |
| valid-alternative-index | Pass | Reject | Accept |
| impossible-exactly-once | Fail | Reject | Reject |

### Reference ref-F01

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Frozen basis: Reviewed fallback integrates hash lookup, recency mutation, bounded eviction and repeat/evict correctness. Relative fresher Hard, not experienced Hard.

Initial: {"minimum_reasoning": "The question is directly role-relevant and technically sound for a fresher data-structures interview. It asks for an implementation strategy with an explicit boundary case (repeat-then-evict) and the core reasoning is about maintaining O(1)-style updates with a map plus ordered structure or equivalent. It is answerable, plausible as an interview prompt, and novel given empty history.", "blocking_issue": "none", "quote": "", "reason": "No defect found. The prompt is clear, bounded, and appropriate for the stated profile and topic; it asks for a concrete data structure design including a boundary case rather than requiring an underspecified or contradictory solution."}

Revised: {"minimum_reasoning": "Need O(1)-style update with recency order and duplicate lookup, including eviction after a repeat. This is a standard small-cache/LRU task, not Hard enough for fresher.", "blocking_issue": "depth", "quote": "last 100 distinct queries", "reason": "The prompt is directly relevant and clear, but it only asks for a straightforward LRU-style implementation. It lacks Hard-level depth for a fresher interview question."}

### Reference ref-E05

A messaging API has `POST /imports` to create a bulk import job. Clients may retry after a timeout, and sometimes the response is lost after the server has already committed the job. You must guarantee that the same authenticated user can safely retry the same request, but if they reuse the same idempotency key with a different payload, the server should reject it. What server-side contract and storage/claim flow would you implement so concurrent identical retries do not create two jobs, while still returning a stable outcome for pending or completed requests?

Frozen basis: Requires atomic key claim, payload mismatch handling, concurrent retries and stable pending/completed outcomes after lost responses.

Initial: {"minimum_reasoning": "The prompt is asking for a concrete idempotency design: an authenticated-user-scoped idempotency key contract plus a server-side claim/store flow that atomically deduplicates concurrent identical POST retries, detects key reuse with a different payload, and returns the same pending/completed outcome. A good answer would describe validating `(user_id, idempotency_key)` against a stored request fingerprint, using an atomic insert-or-claim/lock to ensure only one job is created, and replaying the o", "blocking_issue": "none", "quote": "", "reason": "This is directly relevant to HTTP/API design, technically sound, and answerable. It has a clear experienced-level failure/trade-off dimension (timeouts, lost responses, concurrent retries, stable replay semantics). It also invites a meaningful follow-up on storage/atomicity and race handling without being overconstrained or contradictory."}

Revised: {"minimum_reasoning": "Need a concrete idempotency-key claim/lookup flow; otherwise concurrent retries can double-create jobs or diverge on payload mismatch.", "blocking_issue": "none", "quote": "", "reason": "The question is directly role-relevant, technically sound, experienced-level Hard, and answerable with a meaningful follow-up."}

### Reference ref-E09

After a deployment, p99 latency on an API triples, but median latency, CPU, and database query time stay flat. Traces show most of the extra time is waiting to acquire a DB connection, and the pool stays at its limit even after requests complete. Assuming requests are well-formed and the app must stay live, how would you distinguish a leaked connection from a legitimate long-held transaction, and what bounded change or instrumentation would you add first to prove it without widening the pool? Consider cancellation and exception paths too.

Frozen basis: Discriminating pool-wait evidence, competing leak/ownership hypotheses and cancellation paths require a bounded falsifiable experiment.

Initial: {"minimum_reasoning": "Question is role-relevant and technically sound, but asks for diagnosis strategy plus bounded proof without enough concrete failure surface or success criterion.", "blocking_issue": "depth", "quote": "how would you distinguish a leaked connection from a legitimate long-held transaction", "reason": "This is a broad troubleshooting prompt; the minimum implementation reasoning is underspecified, so it’s hard to judge a concrete bounded action or invariant to verify."}

Revised: {"minimum_reasoning": "The question asks for diagnosis and first instrumentation/change, but lacks a concrete observable invariant or success criterion to separate leak vs long-held tx.", "blocking_issue": "depth", "quote": "how would you distinguish a leaked connection from a legitimate long-held transaction", "reason": "It requires naming a diagnosis path, but not enough on expected connection lifecycle signals or current pool behavior to make the bounded proof task concrete."}

### Reference ref-E03

Imagine a file-storage client with two operations: uploadBlob() for ordinary file uploads and createLockFile() for a mutual-exclusion marker that must be atomic, even across retries. Backend X supports conditional writes; backend Y only supports read/overwrite but gives you versioned object keys. If a request times out, the caller must be able to tell whether the lock was created, definitely not created, or the outcome is unknown. How would you shape the interfaces or class boundaries so uploadBlob can use Y, while createLockFile either preserves the atomic contract or clearly rejects unsupported use? Assume callers rely on those outcome distinctions.

Frozen basis: Typed capability interfaces and unsupported-operation handling largely restate the explicit mismatch. No concrete caller recovery sequence or competing implementation choice is required.

Initial: ValueError: Screen defect quote is not present in the candidate question

Revised: {"minimum_reasoning": "The ask is interface/class design, but it also requires a concrete outcome contract for retries and timeouts.", "blocking_issue": "none", "quote": "", "reason": "This is a valid experienced design question: role-relevant, technically grounded, appropriately hard, and answerable with meaningful trade-offs."}

### Reference ref-F02

You have a sorted array of timestamps that may contain duplicates, and you need to return the first timestamp that is at least a given cutoff. If no such timestamp exists, return -1. The array can be empty, and your solution should stay correct when several equal values sit around the cutoff. How would you adapt binary search so it always makes progress and still returns the first eligible timestamp rather than just any match?

Frozen basis: One lower-bound binary search with duplicates and empty input is a standard textbook implementation, without an additional interacting task.

Initial: {"minimum_reasoning": "Needs a concrete boundary invariant; as written, it asks for standard lower_bound behavior without enough challenge for fresher Hard.", "blocking_issue": "depth", "quote": "first timestamp that is at least a given cutoff", "reason": "This is a basic lower_bound/first-true binary search task. The prompt names duplicates and progress, but the implementation is still straightforward and not Hard for the stated fresher profile."}

Revised: {"minimum_reasoning": "Standard lower_bound task; the prompt asks for a known binary-search adaptation, not a Hard implementation challenge.", "blocking_issue": "depth", "quote": "How would you adapt binary search", "reason": "This is answerable and role-relevant, but too shallow for a fresher Hard prompt; it mainly tests a standard lower-bound pattern."}

### Reference ref-F03

Imagine a file storage app where each file has a name, size, and a method that returns its total cost. Regular files cost by size, but image files also have a fixed thumbnail fee. The app stores files in one list and prints the total bill by calling the same method on every item. If you add a new file type later, you should not have to change the billing loop. How would you design the classes and method contract so this works, while still handling the edge case that a file may report invalid state, like a negative size?

Frozen basis: Subclass price overrides and negative-size validation remain a routine polymorphism exercise; invalid input does not create substantial interacting constraints.

Initial: {"minimum_reasoning": "The prompt asks for a specific class design and method contract, but the core behavioral rule is underspecified for invalid state handling.", "blocking_issue": "clarity", "quote": "handling the edge case", "reason": "It says a file may report invalid state but doesn't define whether billing should throw, skip, clamp, or mark invalid, so the required contract is ambiguous."}

Revised: {"minimum_reasoning": "This is a textbook polymorphism prompt; it only asks for a class/method design, not a harder implementation trade-off.", "blocking_issue": "depth", "quote": "same method on every item", "reason": "The question signals the OOP pattern but not a substantive Hard challenge for a fresher; the negative-size edge case is minor and doesn't add enough depth."}

### Reference ref-E04

Imagine an analytics service records one row per customer event, and a nightly job marks all events for a given customer as processed by updating a status column. New events for that customer can arrive while the job runs, and a retry may happen after a deadlock or serialization failure. If you had to make the job correct and idempotent under this contention, what transaction strategy would you use for the UPDATE, and where would you place the retry boundary? Assume the job must never mark an event processed unless it was actually selected in that run, and duplicate processing is worse than a temporary delay.

Frozen basis: The processing effect and selected-in-this-run semantics are unspecified. Updating status alone is not a defined exactly-once processing contract; a clarification is needed before choosing transaction boundaries.

Initial: {"minimum_reasoning": "Needs a concrete failure mode and recovery strategy, not just a named transaction pattern.", "blocking_issue": "technical", "quote": "what transaction strategy would you use for the UPDATE", "reason": "The prompt asks for a strategy but gives no DB model or isolation constraints; correctness depends on engine-specific semantics, making a definitive answer unverifiable."}

Revised: {"minimum_reasoning": "Need only a concrete transactional/update strategy and retry boundary for a contended, idempotent bulk update.", "blocking_issue": "none", "quote": "", "reason": "Experienced SQL concurrency design with clear invariants, failure modes, and trade-off; answerable and role-relevant."}

### Reference ref-P7F03

Suppose a file-storage app has a `Storage` interface with `save(file)` and `delete(fileId)`. The app also guarantees this caller-visible rule: if `save()` fails halfway, no partial file should be visible to later `get()` calls. You need to add a new `EncryptedStorage` implementation without changing the code that orchestrates uploads and deletes. How would you structure the objects so that encryption can be swapped in while preserving that no-partial-file invariant, especially if `save()` can fail after writing the first chunk?

Frozen basis: A swappable encrypted writer must preserve no-partial-read visibility after a chunk failure; staged write/publication/cleanup is a concrete OOP boundary with a meaningful failure case.

Initial: {"minimum_reasoning": "The question asks for structure, not a concrete implementation path or failure handling design.", "blocking_issue": "depth", "quote": "How would you structure the objects", "reason": "It’s too abstract for a fresher Hard OOP interview item; it names swapping encryption but doesn’t require a concrete lifecycle, invariant enforcement, or failure/recovery mechanism."}

Revised: {"minimum_reasoning": "Need a clear design task; the partial-write invariant makes staging/commit reasoning required. The ask is answerable for a fresher as OO structure, but not with this wording.", "blocking_issue": "none", "quote": "", "reason": "This is a valid, role-relevant OO design question. It asks for object structure and an invariant-preserving save flow, which a fresher can discuss without prescribing an exact implementation."}

### Reference ref-P7F04

A platform has `customers(customer_id, name)` and `orders(order_id, customer_id, status, created_at)`, where `status` is `PAID` or `CANCELLED`. Write a query that returns every customer plus three columns: total paid orders, total cancelled orders, and the date of their most recent PAID order. If a customer has no paid orders, that last column must be `NULL`. If two paid orders share the same `created_at`, pick the one with the larger `order_id`. How would you avoid row multiplication between the two counts and still make the latest-order rule deterministic?

Frozen basis: Only the latest PAID date is returned, so selecting a larger order_id for tied dates has no observable effect. Two conditional counts over the same table are routine and do not inherently create independent join multiplication.

Initial: {"minimum_reasoning": "The prompt asks for counts and a latest-order date, but not the specific tie-break implementation or SQL dialect support needed to make it unambiguous.", "blocking_issue": "clarity", "quote": "How would you avoid row multiplication", "reason": "This presupposes a join strategy instead of a clear task boundary, so multiple valid query shapes fit and the exact required result logic is under-specified."}

Revised: {"minimum_reasoning": "Need one customer row with separate aggregates; this is standard fresher SQL using grouped joins/windowing.", "blocking_issue": "none", "quote": "", "reason": "The question is directly role-relevant, technically sound, and answerable. It asks for a bounded SQL aggregation/join pattern with a deterministic tie-breaker, which is appropriate for a fresher."}

### Reference ref--refinedR04

A note app lets users own notes and share them with teammates. A share can also be revoked, but revocation is processed asynchronously: for a short time, the note may still show in a client cache even after the server has marked the share as revoked. If a user is the owner, they can edit; if they are only a shared viewer, they can read but not edit. How would you enforce access at the server boundary so a revoked viewer cannot keep editing by replaying an old note ID, and what single test would you run to prove the revoke takes effect on the next write even if the cached view is stale?

Frozen basis: Shared viewers could never edit, so denying their writes before and after revocation does not prove revocation worked. The test would pass even if revoked read access remained exposed.

Initial: {"minimum_reasoning": "The prompt is answerable and role-relevant, but it asks for a single test and a server-boundary fix without a concrete lifecycle or state model to evaluate against.", "blocking_issue": "depth", "quote": "what single test would you run", "reason": "It narrows the task to one test, but doesn't define the necessary revoke/write lifecycle details to make the enforcement strategy meaningfully assessable."}

Revised: {"minimum_reasoning": "Need only basic authorization at write time and a revoke-aware check; server must reject writes for stale viewer IDs after revocation.", "blocking_issue": "none", "quote": "", "reason": "The question is directly role-relevant, technically sound, fresher-appropriate Hard, and asks for a plausible server-boundary access test with a meaningful follow-up."}

### Reference ref-P7F09

An API sometimes returns one user’s draft comment to another user, but only when two requests overlap and the server logs are enabled. You can add one temporary request ID to each request and run a controlled two-request test. What is the first explanation you would try to confirm, and what single experiment would you run to distinguish shared mutable state from a timing issue caused by logging? Include what result you would expect in each case.

Frozen basis: Shared mutable state and logging-induced timing are not mutually exclusive hypotheses. Toggling logging may expose the same race rather than distinguish its cause; the requested each-case oracle is misleading.

Initial: {"minimum_reasoning": "The prompt asks for two explanations and an experiment, so it’s answerable and plausible, but not a defect in the question.", "blocking_issue": "none", "quote": "", "reason": "Clear, role-relevant debugging scenario with a concrete controlled test and expected outcomes; no blocking flaw."}

Revised: {"minimum_reasoning": "Needs a concrete first hypothesis and discriminating experiment; without that, the prompt is only a generic debugging checklist.", "blocking_issue": "depth", "quote": "What is the first explanation you would try to confirm", "reason": "For a fresher, this asks for diagnosis strategy but doesn’t anchor a specific debuggable mechanism or invariant beyond broad concurrency/logging."}

### Reference ref-P7E06

Suppose GET /activities must return a stable snapshot of page 1 as-of the first response, ordered by (created_at, id), even while new rows are inserted and some rows are deleted. The cursor must expire after 10 minutes, and you cannot keep a full result set per client. If you had to choose one backing approach that actually enforces that contract, what would you implement so page 2 still reflects the same snapshot, and how would it handle one concrete race where a row is deleted after page 1 but before page 2?

Frozen basis: Explicit snapshot semantics under deletion require retained/as-of state or a clearly costed snapshot mechanism; a cursor alone does not satisfy the contract.

Initial: {"minimum_reasoning": "The question presumes a stable snapshot plus expiring cursor without full per-client state, but asks only for “one backing approach” and a single race. That doesn’t force the candidate to design the snapshot token or recovery mechanism concretely enough.", "blocking_issue": "depth", "quote": "what would you implement", "reason": "This asks for a broad approach choice, not the concrete lifecycle and failure behavior needed to prove the snapshot contract is enforced."}

Revised: {"minimum_reasoning": "The prompt asks for a concrete backing approach and race handling; that’s a valid implementation task, not missing detail.", "blocking_issue": "none", "quote": "", "reason": "Directly REST/relevant, technically sound, Hard for experienced, and answerable with meaningful follow-up and no duplicate."}

### Reference familiar-not-repeated

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Frozen basis: Familiar LRU pattern is still a new task relative to this unrelated question.

Initial: {"minimum_reasoning": "Clear fresher DS prompt on O(1) recency/eviction with a boundary case.", "blocking_issue": "none", "quote": "", "reason": "Directly role-relevant, technically sound, appropriately hard for fresher, answerable, and novel; follow-up is meaningful."}

Revised: {"minimum_reasoning": "Need O(1) updates for recency and eviction; the prompt is a classic LRU variant, not a lookup/order hard problem.", "blocking_issue": "depth", "quote": "last 100 distinct queries", "reason": "For a fresher, this is an implementation of a standard bounded recency list; it doesn’t require enough nontrivial reasoning to be Hard."}

### Reference near-duplicate

Keep the latest 100 distinct search terms, moving repeats to newest and evicting oldest without a scan. How would you implement it?

Frozen basis: Same recency/dedup/eviction reasoning as the earlier question despite different wording.

Initial: {"minimum_reasoning": "Duplicate of prior question; same last-100 distinct queries with repeat-to-front and eviction.", "blocking_issue": "duplicate", "quote": "Keep the latest 100 distinct search terms", "reason": "It asks the same implementation/invariant as the previous prompt, only reworded."}

Revised: ValueError: Screen defect quote is not present in the candidate question

### Reference valid-alternative-index

An index has ten million timestamped rows, 10,000 inserts/second in bursts and concurrent range reads. Acknowledged inserts must be visible; memory allows one base plus a small delta. A colleague proposes a sorted base with a searchable delta rather than a balanced tree. How would you implement read merging and rebuild publication so an interrupted rebuild cannot lose acknowledged inserts, and which workload would make you reject this design?

Frozen basis: A correct unfamiliar/alternative strategy can meet the invariant; no required tree answer.

Initial: {"minimum_reasoning": "Core LSM/merge question is valid, but the prompt asks two distinct designs without enough lifecycle detail to anchor one answer.", "blocking_issue": "depth", "quote": "read merging and rebuild publication", "reason": "It bundles merge logic and crash-safe publication; missing failure/recovery specifics makes the expected implementation scope unclear."}

Revised: {"minimum_reasoning": "The question asks for concrete read-merge and rebuild publication mechanics plus a workload-based rejection criterion; that is a substantive experienced design task.", "blocking_issue": "none", "quote": "", "reason": "It is directly role-relevant, technically sound, experienced-Hard, and answerable; it requires lifecycle/failure reasoning and a meaningful trade-off."}

### Reference impossible-exactly-once

An email provider has no idempotency key or delivery lookup and does not share transactions with your database. A send may succeed while its response is lost. Without changing those capabilities or weakening guarantees, implement automatic retries that always eventually deliver exactly one email. What local database flag makes this possible?

Frozen basis: The demanded guarantee is impossible with these capabilities; the question forbids the necessary redesign and falsely promises a flag solution.

Initial: {"minimum_reasoning": "Impossible premise: lost response with no delivery lookup or idempotency means exact-once cannot be proven by a local flag alone.", "blocking_issue": "technical", "quote": "always eventually deliver exactly one email", "reason": "The prompt asks for an impossible guarantee under the stated constraints; a local DB flag cannot prevent duplicates after a lost response without provider-side idempotency or lookup."}

Revised: {"minimum_reasoning": "Exactly-once delivery is impossible with a non-idempotent external side effect plus lost responses and no shared transaction or delivery lookup.", "blocking_issue": "technical", "quote": "always eventually deliver exactly one email", "reason": "The premise asks for an impossible guarantee under the stated constraints, so the question is not answerable as written."}

## Preservation

`holdout-manifest.json` SHA-256: `1a8178d42bfbcab543c1fe90d07bc0669e43f2e651308b43ee28daecefbec199`. `final-integrity.json` verifies 551 prior evidence files, current evaluated production hashes, all eleven live tables and their sequences/schema. No labels or question texts were edited after execution. Both failed final questions remain failures. All paid responses, including invalid drafts and invalid reviews, remain available locally.
