# Phase 7: complete returned-question evidence

Agent review, 16 November 2026. This is not independent human validation. Read [the main report](phase7-question-quality-results.md) for sampling, budget, source changes and limitations. The frozen rubric is unchanged. Scores are R/T/L/H/E/C/F, each 0–2. PASS requires R=T=H=E=C=2 and L,F>=1, with no same-session near-duplicate. Requested difficulty is Hard throughout; an explicit Medium fallback is a failed Hard request. Do not count a curated fallback as a generated success.

All 61 returned texts are below, including failures and Medium/off-topic fallbacks. All 87 actual drafts, including rejected drafts and one unfinished case, are preserved in `storage/phase7/draft-inventory.json` and raw API files. Additional cases do not replace or remove failed primary cases.

## First run

| Case | Profile | Topic | Origin | Actual tier | Verdict | R/T/L/H/E/C/F |
| --- | --- | --- | --- | --- | --- | --- |
| E01 | experienced | Data Structures | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| E02 | experienced | Algorithms | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| E03 | experienced | Object-Oriented Programming | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| E04 | experienced | SQL | Provider | hard | FAIL | 2/1/2/1/2/1/1 |
| E05 | experienced | HTTP | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| E06 | experienced | REST APIs | Provider | hard | FAIL | 2/2/2/2/2/1/1 |
| E07 | experienced | Git | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| E08 | experienced | Testing | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| E09 | experienced | Debugging | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| E10 | experienced | Security Fundamentals | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| F01 | fresher | Data Structures | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| F02 | fresher | Algorithms | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| F03 | fresher | Object-Oriented Programming | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| F04 | fresher | SQL | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| F05 | fresher | HTTP | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| F06 | fresher | REST APIs | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| F07 | fresher | Git | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| F08 | fresher | Testing | Provider | hard | FAIL | 2/2/2/2/2/1/1 |
| F09 | fresher | Debugging | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| F10 | fresher | Security Fundamentals | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| U01 | fresher | Data Structures | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| U02 | experienced | Algorithms | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| U03 | fresher | Object-Oriented Programming | Provider | hard | FAIL | 2/1/2/1/2/1/1 |
| U04 | experienced | SQL | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| U05 | fresher | HTTP | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| U06 | experienced | REST APIs | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| U07 | fresher | Git | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| U08 | experienced | Testing | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| U09 | fresher | Debugging | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| U10 | experienced | Security Fundamentals | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| R01 | experienced | Testing | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| R02 | fresher | Data Structures | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| R03 | fresher | SQL | Provider | hard | FAIL | 2/1/2/2/2/1/1 |

### E01 — PASS

Imagine a search service that ingests a stream of user queries and must suppress duplicate processing for the last 24 hours, but memory is capped and events may be replayed after a crash. What data structure approach would you use to track “already seen” queries, and how would you handle the edge case where a query reappears after the 24-hour window or after recovery? Assume the system only needs exact deduplication within the retention window.

Assessment: Exact windowed deduplication under bounded memory and restart requires a durable identity/state boundary, not merely a set.

Evidence: experienced; provider-generated; actual tier hard; source IDs 67; API requests 2, 3, 4.

### E02 — PASS

Let’s say you’re building a collaboration app’s activity feed. It stores 10 million items ordered by (updated_at, id), and new edits arrive in one-minute bursts of about 10,000 per second while users keep reading time-ranged pages. Updated items must be visible immediately, memory is bounded, and reads should be fast even during a burst. If you had to choose one indexing approach for the hot path, would you use a balanced tree, a sorted base plus delta structure, or a different design? Assume exact ordering and no missed updates; explain how your choice handles the burst, especially the case where a range read overlaps items that were just updated.

Assessment: Acknowledge visibility, updates during range reads and burst/index trade-offs require an implementable merge/index design.

Evidence: experienced; provider-generated; actual tier hard; source IDs 64; API requests 5, 6, 7.

### E03 — FAIL

Imagine a file-storage client with two operations: uploadBlob() for ordinary file uploads and createLockFile() for a mutual-exclusion marker that must be atomic, even across retries. Backend X supports conditional writes; backend Y only supports read/overwrite but gives you versioned object keys. If a request times out, the caller must be able to tell whether the lock was created, definitely not created, or the outcome is unknown. How would you shape the interfaces or class boundaries so uploadBlob can use Y, while createLockFile either preserves the atomic contract or clearly rejects unsupported use? Assume callers rely on those outcome distinctions.

Assessment: Typed capability interfaces and unsupported-operation handling largely restate the explicit mismatch. No concrete caller recovery sequence or competing implementation choice is required.

Evidence: experienced; provider-generated; actual tier hard; source IDs 79; API requests 8, 9, 10.

### E04 — FAIL

Imagine an analytics service records one row per customer event, and a nightly job marks all events for a given customer as processed by updating a status column. New events for that customer can arrive while the job runs, and a retry may happen after a deadlock or serialization failure. If you had to make the job correct and idempotent under this contention, what transaction strategy would you use for the UPDATE, and where would you place the retry boundary? Assume the job must never mark an event processed unless it was actually selected in that run, and duplicate processing is worse than a temporary delay.

Assessment: The processing effect and selected-in-this-run semantics are unspecified. Updating status alone is not a defined exactly-once processing contract; a clarification is needed before choosing transaction boundaries.

Evidence: experienced; provider-generated; actual tier hard; source IDs 88; API requests 11, 12, 13.

### E05 — PASS

A messaging API has `POST /imports` to create a bulk import job. Clients may retry after a timeout, and sometimes the response is lost after the server has already committed the job. You must guarantee that the same authenticated user can safely retry the same request, but if they reuse the same idempotency key with a different payload, the server should reject it. What server-side contract and storage/claim flow would you implement so concurrent identical retries do not create two jobs, while still returning a stable outcome for pending or completed requests?

Assessment: Requires atomic key claim, payload mismatch handling, concurrent retries and stable pending/completed outcomes after lost responses.

Evidence: experienced; provider-generated; actual tier hard; source IDs 76; API requests 14, 15, 16.

### E06 — FAIL

Let’s say you own GET /events for a scheduling app. Clients page through upcoming events sorted by (starts_at, id), and product wants page 2 to be a stable continuation of page 1 even if events are inserted or canceled while the user is paging. You can’t keep a full result set per client, and cursors expire after 10 minutes. What pagination contract and server-side cursor strategy would you implement so the client either gets a valid continuation or a clear expiration response? Assume you must re-check authorization on every page and prevent cursor tampering.

Assessment: Stable continuation is not defined as a snapshot or a live feed. Deletions and mutated starts_at require an explicit observable consistency contract, which the prompt leaves for interpretation.

Evidence: experienced; provider-generated; actual tier hard; source IDs 82; API requests 17, 18, 19.

### E07 — PASS

A release branch was merged into main, then production data was migrated in a way that older code cannot read safely. The merge commit is already pushed and other teams may have pulled it. If you need to recover from a bad release without rewriting shared history, what Git-based recovery plan would you use, and how would you decide between reverting the merge versus making a forward fix? Assume the only hard requirement is to keep history auditable and avoid leaving the repo in a state that would break a redeploy from main.

Assessment: Shared history plus incompatible migrated data forces a forward/revert decision and a verification plan, rather than a bare Git command.

Evidence: experienced; provider-generated; actual tier hard; source IDs 73; API requests 20, 21, 22.

### E08 — PASS

A message worker writes a result and acknowledges delivery separately. A crash can happen between them, and the queue redelivers unacknowledged messages. How would you build deterministic fault-injection tests that distinguish lost work from duplicate externally visible results across restarts?

Assessment: Reviewed fallback asks for deterministic crash/redelivery tests with durable externally visible oracles. This is a fallback, not a successful provider generation.

Evidence: experienced; curated fallback; actual tier hard; source IDs 91; API requests 23, 24, 25, 26, 27.

### E09 — PASS

After a deployment, p99 latency on an API triples, but median latency, CPU, and database query time stay flat. Traces show most of the extra time is waiting to acquire a DB connection, and the pool stays at its limit even after requests complete. Assuming requests are well-formed and the app must stay live, how would you distinguish a leaked connection from a legitimate long-held transaction, and what bounded change or instrumentation would you add first to prove it without widening the pool? Consider cancellation and exception paths too.

Assessment: Discriminating pool-wait evidence, competing leak/ownership hypotheses and cancellation paths require a bounded falsifiable experiment.

Evidence: experienced; provider-generated; actual tier hard; source IDs 70; API requests 28, 29, 30.

### E10 — PASS

Imagine an e-commerce admin portal where a manager can generate a CSV export of sensitive customer orders. The export is produced by a background job, stored in a cache/CDN, and shared through a download link. If a manager is removed from the team, access must stop within 30 seconds for queued jobs and for any link that has already been issued, but you cannot revoke a file that was already downloaded. What authorization and cache contract would you implement at the job boundary and the download boundary so revocation is enforced, and what would you do if the policy service is briefly unavailable? Assume links may be forwarded and the cache may serve stale objects.

Assessment: Requires revocation within a stated bound across queued work, cached links and unavailable policy data; downloaded copies are explicitly excluded.

Evidence: experienced; provider-generated; actual tier hard; source IDs 85; API requests 31, 32, 33.

### F01 — PASS

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Assessment: Reviewed fallback integrates hash lookup, recency mutation, bounded eviction and repeat/evict correctness. Relative fresher Hard, not experienced Hard.

Evidence: fresher; curated fallback; actual tier hard; source IDs 66; API requests 34, 35, 36, 37, 38.

### F02 — FAIL

You have a sorted array of timestamps that may contain duplicates, and you need to return the first timestamp that is at least a given cutoff. If no such timestamp exists, return -1. The array can be empty, and your solution should stay correct when several equal values sit around the cutoff. How would you adapt binary search so it always makes progress and still returns the first eligible timestamp rather than just any match?

Assessment: One lower-bound binary search with duplicates and empty input is a standard textbook implementation, without an additional interacting task.

Evidence: fresher; provider-generated; actual tier hard; source IDs 63; API requests 39, 40, 41.

### F03 — FAIL

Imagine a file storage app where each file has a name, size, and a method that returns its total cost. Regular files cost by size, but image files also have a fixed thumbnail fee. The app stores files in one list and prints the total bill by calling the same method on every item. If you add a new file type later, you should not have to change the billing loop. How would you design the classes and method contract so this works, while still handling the edge case that a file may report invalid state, like a negative size?

Assessment: Subclass price overrides and negative-size validation remain a routine polymorphism exercise; invalid input does not create substantial interacting constraints.

Evidence: fresher; provider-generated; actual tier hard; source IDs 78; API requests 42, 43, 44.

### F04 — PASS

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Assessment: Fallback requires latest eligible event, deterministic tied timestamp selection and unmatched parents. More than a lone LEFT JOIN/COUNT, but still near the relative threshold.

Evidence: fresher; curated fallback; actual tier hard; source IDs 87; API requests 45, 46, 47, 48, 49.

### F05 — PASS

A messaging app lets a client send a POST /messages request to create one chat message. Sometimes the client times out after sending it, and the server may or may not have saved the message. If the user taps "send" again, how would you design the client and API behavior so the message is not duplicated, while still allowing a safe retry after a timeout? Assume the client can store one unique key per message attempt and the server can persist request outcomes.

Assessment: Integrates timeout uncertainty, stable client identity and durable server outcomes; the implementation must prevent duplicates while allowing a safe retry. Borderline relative depth.

Evidence: fresher; provider-generated; actual tier hard; source IDs 75; API requests 50, 51, 52.

### F06 — FAIL

A scheduling app exposes PUT /appointments/{id} to let a client change an appointment’s time and notes. Two frontends can edit the same appointment, and the server must not silently overwrite a newer change. Assume each successful response returns the current appointment representation and a validator value that changes when the saved content changes. What request pattern would you use so a stale edit is rejected instead of replacing the newer one, and what should the server return when that happens?

Assessment: A standard If-Match/412 explanation answers the task. It does not explicitly require the atomic compare/write implementation or recovery from a lost response.

Evidence: fresher; provider-generated; actual tier hard; source IDs 81; API requests 53, 54, 55, 56, 57.

### F07 — FAIL

A shared integration branch already includes a buggy feature commit, and later commits on the same branch fix nearby code that depends on it. You need to remove the buggy change from the shared branch without rewriting history, but one of the later fixes now conflicts with the rollback. Assuming the branch has already been pushed and teammates may have pulled it, what Git operation would you choose, and how would you handle the conflict so the branch still builds and the intended behavior is preserved?

Assessment: Revert plus generic conflict resolution is not a concrete dependency puzzle; actual commit contents or a surviving invariant are missing.

Evidence: fresher; provider-generated; actual tier hard; source IDs 72; API requests 58, 59, 60.

### F08 — FAIL

Let’s say you have a login API that should lock an account for 15 minutes after 3 failed attempts, but only failed attempts within that window count. You want to test this without sleeping or calling a real auth service. How would you structure the test setup so the time is fully deterministic, the failure counter resets correctly after the lock expires, and shared state from one test cannot affect another if the test fails midway?

Assessment: The relationship between failed-attempt window, lock-start time and expiry/reset semantics is ambiguous. A deterministic oracle requires clarification.

Evidence: fresher; provider-generated; actual tier hard; source IDs 90; API requests 61, 62, 63, 64, 65.

### F09 — PASS

Imagine a REST API has an endpoint that sometimes returns one user’s draft comment in another user’s response, but only when two requests hit the server at nearly the same time. You can reproduce it with a controlled two-request test using request IDs. What would you inspect first to confirm whether the bug is caused by shared mutable state versus a bad cache key, and how would you turn that finding into a regression test?

Assessment: Requires distinguishing shared mutable state from a cache-key fault and encoding a controlled interleaving as a regression test; practical integrated fundamentals.

Evidence: fresher; provider-generated; actual tier hard; source IDs 69; API requests 66, 67, 68.

### F10 — FAIL

Imagine an e-commerce app has GET /orders/{orderId} to show an order summary. The server verifies the user’s JWT, then loads the order only by orderId. The product team also wants users to see a 404 instead of 403 when the order belongs to someone else. How would you change the server-side check so one authenticated user cannot access another user’s order, while still keeping the 404 behavior and correctly handling a shared order that is explicitly allowed for a second user?

Assessment: An owner-or-explicit-share predicate plus 404 mapping is routine authorization. No revocation, stale state or other interacting boundary is required.

Evidence: fresher; provider-generated; actual tier hard; source IDs 84; API requests 69, 70, 71.

### U01 — FAIL

Imagine a search feature over a small product catalog where each item has a title and tags. You need to return unique results for a query, preserving the first match order from the original list, but two titles may differ only by case or extra spaces. Also, some tags are repeated inside the same item. Which data structure approach would you use to track duplicates and why, if the input can be empty and the result must not reorder matches?

Assessment: Case/space normalization plus ordered deduplication is a single routine pass; empty input and repeated tags do not raise the reasoning demand enough.

Evidence: fresher; provider-generated; actual tier hard; source IDs 66; API requests 72, 73, 74, 75, 76.

### U02 — PASS

Imagine a search service stores 10 million records sorted by (timestamp, id). It gets 10,000 acknowledged inserts per second in one-minute bursts, and range queries must see those inserts immediately. Memory is capped, so you can’t keep multiple full copies of the index. If you had to choose one indexing approach—balanced tree, sorted base plus delta, or another structure—what would you implement to keep range reads fast while avoiding long write stalls during a burst? Please explain the main trade-off you’d make and how you’d handle the case where a rebuild or merge is interrupted after some inserts were already acknowledged.

Assessment: Index choice must preserve acknowledged inserts through interrupted merges and bounded memory under a burst workload.

Evidence: experienced; provider-generated; actual tier hard; source IDs 64; API requests 77, 78, 79.

### U03 — FAIL

Imagine a classroom collaboration app with a shared document. Each user can edit, but only the document owner can rename it. You want a TextDocument class and a CommentedDocument feature that adds comments without changing how existing code saves or edits the document. If a method expects a base Document, what OOP design would you choose so that old code keeps working even when a commented document is passed in, and why is that safer than inheritance here?

Assessment: The prompt presupposes composition is safer than inheritance without stating the violated contract. Owner rename policy is introduced but not connected to the design task.

Evidence: fresher; provider-generated; actual tier hard; source IDs 78; API requests 80, 81, 82, 83, 84.

### U04 — PASS

Let’s say a collaboration app lets a user add a list of tags to a document, and the rule is: either all requested tags are attached or none are. Two workers may try to attach overlapping tag sets to the same document at the same time, and the API may retry after deadlocks or serialization failures. What transaction pattern would you use to make that safe in SQL, and where would you draw the retry boundary so a failed attempt never creates a partial attach or a duplicate confirmation?

Assessment: Atomic overlapping tag changes, transaction retries and confirmation effects require a coherent durable boundary, including handling duplicate outcomes.

Evidence: experienced; provider-generated; actual tier hard; source IDs 88; API requests 85, 86, 87.

### U05 — FAIL

A file-storage app sends an HTTP POST to upload a document, but the client times out after waiting for the response. The server may have already stored the file. The product owner wants the app to safely retry automatically without creating duplicate uploads. What should the client use to decide whether to retry, and what extra check should the server support if the same retry token is sent again with a different file payload?

Assessment: The ask stops at deciding to retry and rejecting key/body mismatch; it does not require implementing concurrency-safe server claiming. Familiar idempotency explanation alone suffices.

Evidence: fresher; provider-generated; actual tier hard; source IDs 75; API requests 88, 89, 90.

### U06 — PASS

Consider a file-storage API that lists a folder’s contents with cursor pagination. Clients require a stable snapshot for up to 10 minutes, ordered by (created_at, id), even while files are uploaded and some are deleted. You can’t keep a full per-client result set in memory. What pagination contract would you design so page 2 can still reflect the same snapshot as page 1, and what would the server store in the cursor or backing state to make that possible? Assume the cursor must be opaque, unforgeable, and revalidated for auth on each request.

Assessment: An explicit stable snapshot across deletion/insertion forces a backing-state/version strategy; opaque signed cursors alone cannot satisfy it.

Evidence: experienced; provider-generated; actual tier hard; source IDs 82; API requests 91, 92, 93.

### U07 — FAIL

A shared main branch has a bad commit that causes a bug, but two later commits on top of it are already correct and depend on the same files. You cannot rewrite history because teammates may have pulled main, and you want the bug fixed without losing those later changes. Would you choose git revert or git reset here, and what specific edge case would you watch for if the bad commit was actually a merge commit?

Assessment: The answer is naming revert and a merge mainline; no actual dependent-code invariant makes the recovery sequence challenging.

Evidence: fresher; provider-generated; actual tier hard; source IDs 72; API requests 94, 95, 96.

### U08 — PASS

Imagine an analytics worker reads events from a queue, writes an aggregate row to PostgreSQL, and then publishes a “rollup completed” notification to a second service. A crash after the DB commit but before the notification can cause redelivery, and a crash before the commit must not lose the aggregate update. If you had to design one deterministic test that proves the critical boundary is correct, what would you do? Assume you can add fault hooks, but not rely on sleeps or method-call counts. Focus on the test setup and the assertions you’d make after restart.

Assessment: A deterministic crash/restart test must prove durable aggregate and external notification behavior with meaningful assertions, not method calls.

Evidence: experienced; provider-generated; actual tier hard; source IDs 91; API requests 97, 98, 99.

### U09 — FAIL

Imagine a messaging API where a user sends two chat requests back-to-back, and sometimes the second response includes part of the first request’s draft text. The bug only appears when both requests are in flight, but not when tested one at a time. You can add logging or a request ID, but you should avoid changing the production behavior too much. What would you investigate first to decide whether this is shared mutable state, and what one controlled test would you run to prove it?

Assessment: The single favored shared-state hypothesis and generic concurrent reproduction are weaker than the two-hypothesis/evidence task; a routine debugging explanation can answer it.

Evidence: fresher; provider-generated; actual tier hard; source IDs 69; API requests 100, 101, 102.

### U10 — PASS

Consider a messaging app where users can export the contents of a private channel. The export runs in a background job and the finished file is served from cache behind a shared download link. If a user is removed from the channel, access to both queued exports and any previously issued links must stop within 30 seconds. What authorization boundary and cache/revocation check would you put in place to make that true? Assume the system should fail closed if policy data is unavailable, but a file already fully downloaded by an authorized user cannot be taken back.

Assessment: Explicit queued/cached-link revocation deadline, fail-closed policy and already-downloaded exclusion create a coherent advanced authorization problem.

Evidence: experienced; provider-generated; actual tier hard; source IDs 85; API requests 103, 104, 105.

### R01 — PASS

Imagine a search API that returns the top 20 results for a query from an index that refreshes every few minutes. Product wants a test suite that proves a ranking change is safe before rollout, but the live index is too large to rebuild for every test, and results can change slightly during refresh. If you had to choose one testing approach for this release gate, how would you design it so it catches regressions in ordering and relevance drift without becoming flaky? Assume the contract is: for a fixed frozen snapshot, the top 20 results must match exactly, while during refresh only the snapshot boundary may move.

Assessment: Frozen snapshot correctness versus rolling index refresh and a bounded release gate require choosing an independent nonflaky oracle and integration boundary.

Evidence: experienced; provider-generated; actual tier hard; source IDs 91; API requests 106, 107, 108, 109, 110. Additional case following E08; earlier failure remains counted.

### R02 — FAIL

Imagine a product search page where users type a prefix like "app" and the system must return up to 5 matching product names in alphabetical order. The catalog is fixed for the session, but queries can repeat many times. You may precompute once at startup, and you should handle the empty catalog and duplicate product names correctly. What data structure or combination of structures would you use for fast prefix lookup, and what would you store at each node or entry to avoid scanning the whole list on every query?

Assessment: Static top-five prefix lookup with empty/duplicate catalog is a conventional trie or sorted-array exercise without an interacting update or resource constraint.

Evidence: fresher; provider-generated; actual tier hard; source IDs 66; API requests 111, 112, 113, 114, 115. Additional case following F01; earlier failure remains counted.

### R03 — FAIL

Imagine a collaboration app has tables users(id), tasks(id, owner_id), and task_access(task_id, user_id) for shared tasks. You need one query that returns every user plus the count of tasks they can access, including users with zero accessible tasks. A teammate adds a filter so only shared tasks with access type = 'edit' should count, but some users only have owned tasks and no shared rows. How would you write the query so those users are still included and the count is correct when matching rows are missing?

Assessment: task_access schema lacks the access-type field the filter uses; ownership/share overlap counting semantics are not specified, so the intended output requires clarification.

Evidence: fresher; provider-generated; actual tier hard; source IDs 87; API requests 116, 117, 118. Additional case following F04; earlier failure remains counted.

## Refined frozen run

| Case | Profile | Topic | Origin | Actual tier | Verdict | R/T/L/H/E/C/F |
| --- | --- | --- | --- | --- | --- | --- |
| P7E01 | experienced | Data Structures | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7E02 | experienced | Algorithms | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| P7E03 | experienced | Object-Oriented Programming | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| P7E04 | experienced | SQL | Provider | hard | FAIL | 2/2/2/2/2/1/1 |
| P7E05 | experienced | HTTP | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7E06 | experienced | REST APIs | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7E07 | experienced | Git | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7E08 | experienced | Testing | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| P7E09 | experienced | Debugging | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7E10 | experienced | Security Fundamentals | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7F01 | fresher | Data Structures | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| P7F02 | fresher | Algorithms | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| P7F03 | fresher | Object-Oriented Programming | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| P7F04 | fresher | SQL | Provider | hard | FAIL | 2/1/2/1/2/2/1 |
| P7F05 | fresher | HTTP | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| P7F06 | fresher | REST APIs | Provider | hard | FAIL | 2/2/2/2/2/1/1 |
| P7F07 | fresher | Git | Provider | hard | FAIL | 2/2/2/1/2/2/2 |
| P7F08 | fresher | Testing | Provider | hard | FAIL | 2/2/2/1/2/1/1 |
| P7F09 | fresher | Debugging | Provider | hard | FAIL | 2/1/2/2/2/1/1 |
| P7F10 | fresher | Security Fundamentals | Fallback | hard | FAIL | 2/2/2/1/2/2/2 |
| -refinedR01 | experienced | Testing | Provider | hard | PASS | 2/2/2/2/2/2/2 |
| -refinedR02 | fresher | Data Structures | Fallback | medium | FAIL | 2/2/2/0/1/2/2 |
| -refinedR03 | fresher | Algorithms | Fallback | medium | FAIL | 2/2/2/0/1/2/2 |
| -refinedR04 | fresher | Security Fundamentals | Provider | hard | FAIL | 2/0/2/1/2/1/1 |
| -refinedR05 | fresher | Data Structures | Fallback | medium | FAIL | 2/2/2/0/1/2/2 |
| -refinedR06 | fresher | Algorithms | Fallback | medium | FAIL | 2/2/2/0/1/2/2 |
| -refinedR07 | fresher | Data Structures | Fallback | hard | PASS | 2/2/2/2/2/2/2 |
| -refinedR08 | fresher | Algorithms | Fallback | hard | PASS | 2/2/2/2/2/2/2 |

### P7E01 — PASS

Suppose you’re building an in-memory index for a search service that must answer "have we seen this document ID in the last 10 minutes?" and also keep the most recent 1 million IDs available for eviction and replay after a crash. IDs can arrive out of order, duplicates are common, and the process may restart with only a write-ahead log of new arrivals. If you had to choose one primary data-structure approach to maintain both recency and bounded retention, what would you use, and how would you handle the edge case where a duplicate arrives right as an ID is expiring?

Assessment: A bounded hot index plus exact time-window answers and WAL recovery requires state/retention coordination and duplicate-at-expiry reasoning. Event-time versus receipt-time should be clarified, but receipt-time semantics gives a defensible implementation.

Evidence: experienced; provider-generated; actual tier hard; source IDs 67; API requests 119, 120, 121, 122, 123.

### P7E02 — FAIL

Imagine a collaboration app keeps an in-memory list of shared edits ordered by (edit_time, edit_id). New edits arrive in minute-long bursts, and acknowledged edits must be searchable immediately for range views like “all edits in this document between 10:00 and 10:05.” Memory is capped, and reads are frequent during bursts. If you had to choose one primary indexing approach to support fast range scans and inserts under this workload, what would you use, and how would you handle the case where a late edit lands with the same timestamp as an existing one but must still appear in a stable order?

Assessment: Burst inserts and a composite tie key improve realism, but there is no consequential workload/latency choice or recovery condition; a balanced-tree recommendation plus (time,id) ordering largely answers it. Still shallow for experienced Hard.

Evidence: experienced; provider-generated; actual tier hard; source IDs 64; API requests 124, 125, 126.

### P7E03 — FAIL

Suppose you’re designing a file storage client with two operations: create a lock file only if it does not already exist, and upload images with ordinary overwrite semantics. One backend can do conditional writes, but another only supports read/overwrite and returns a versioned object key after each write. If caller code must see a stable invariant that lock creation is atomic, while image uploads may be retried after timeouts, how would you design the object boundaries and interfaces so the unsupported backend cannot silently fake atomic lock creation? Assume the caller must be able to distinguish created, already-exists, and unknown outcomes.

Assessment: Again primarily exposes a deliberately incompatible backend. Interface segregation plus an unknown-outcome enum answers most of the task; it does not require the concrete caller recovery workflow the contract asks for.

Evidence: experienced; provider-generated; actual tier hard; source IDs 79; API requests 127, 128, 129.

### P7E04 — FAIL

You have tables: customers(customer_id PK), orders(order_id PK, customer_id FK, created_at), and order_items(order_id FK, sku, qty). The product team wants one row per customer with: total distinct orders in the last 30 days, total quantity across all items in those orders, and the most recent order_id, but only if that latest order was not canceled in a separate status table(order_id PK, status, updated_at). Some customers have no orders, some orders have multiple items, and a status row may be missing. If you had to write this so counts stay correct without row multiplication and the latest order is chosen deterministically when timestamps tie, what SQL pattern would you use, and how would you handle customers whose latest order has no status row?

Assessment: The SQL is nontrivial, but latest order scope (all time versus last 30 days) and the missing-status-row eligibility contract need clarification. Choosing a query pattern cannot resolve unspecified output semantics.

Evidence: experienced; provider-generated; actual tier hard; source IDs 88; API requests 130, 131, 132, 133, 134.

### P7E05 — PASS

Suppose a POST /imports endpoint creates a long-running import job, and clients may retry if the response times out. Two retries can arrive concurrently with the same idempotency key, and a buggy client might reuse that key with a different request body. What server-side contract would you implement so that: the same key plus the same authenticated user always maps to one durable outcome, a different body under the same key is rejected, and a lost response after commit can still be recovered without creating a second job? Please describe the single most important atomic decision the server must make.

Assessment: Concurrent key claims, principal scoping, payload mismatch and lost-after-commit recovery require one durable atomic decision with meaningful failure behavior.

Evidence: experienced; provider-generated; actual tier hard; source IDs 76; API requests 135, 136, 137.

### P7E06 — PASS

Suppose GET /activities must return a stable snapshot of page 1 as-of the first response, ordered by (created_at, id), even while new rows are inserted and some rows are deleted. The cursor must expire after 10 minutes, and you cannot keep a full result set per client. If you had to choose one backing approach that actually enforces that contract, what would you implement so page 2 still reflects the same snapshot, and how would it handle one concrete race where a row is deleted after page 1 but before page 2?

Assessment: Explicit snapshot semantics under deletion require retained/as-of state or a clearly costed snapshot mechanism; a cursor alone does not satisfy the contract.

Evidence: experienced; provider-generated; actual tier hard; source IDs 82; API requests 138, 139, 140.

### P7E07 — PASS

A release branch already merged a feature branch, then a database migration commit went in that cannot be reversed once applied to production data. A day later, you discover the feature must be disabled, but the branch history is already shared and older app code still needs to run against the migrated schema during rollback testing. If you had to choose one safe recovery plan in Git, what sequence would you use to preserve auditability and avoid breaking the surviving app/data contract, and what would you verify before re-deploying the older code?

Assessment: Shared history and irreversible data compatibility require a recovery sequence and verification beyond simply naming revert. Feasibility of older-code compatibility must be tested rather than assumed.

Evidence: experienced; provider-generated; actual tier hard; source IDs 73; API requests 141, 142, 143, 144, 145.

### P7E08 — PASS

A message worker writes a result and acknowledges delivery separately. A crash can happen between them, and the queue redelivers unacknowledged messages. How would you build deterministic fault-injection tests that distinguish lost work from duplicate externally visible results across restarts?

Assessment: Reviewed fallback requires deterministic crash/redelivery scheduling and externally visible durable oracles. It is not counted as a provider-generated success.

Evidence: experienced; curated fallback; actual tier hard; source IDs 91; API requests 146, 147, 148, 149, 150.

### P7E09 — PASS

After a deployment, p99 latency for one REST endpoint triples, but median latency, CPU, and database query time stay flat. Traces show most of the extra time is waiting to acquire a DB connection, and the pool stays at its limit even after requests complete. You can’t pause production, and raising the pool size is allowed only as a temporary mitigation. What is the single best bounded investigation you’d run to distinguish a leaked connection from a legitimate long-held transaction, and what result would you expect for each hypothesis?

Assessment: Explicit competing hypotheses and expected outcomes make this a falsifiable production experiment rather than a checklist.

Evidence: experienced; provider-generated; actual tier hard; source IDs 70; API requests 151, 152, 153.

### P7E10 — PASS

Suppose an e-commerce admin UI lets a manager share a product-report export with a teammate, but access can also be revoked when that teammate is removed from the team. Downloads may be served from a CDN-backed cached link, and the business wants revocation to take effect within 30 seconds even if a queued export job is still running or a link was already issued. If you had to pick one server-side authorization boundary to enforce this reliably, what would you implement so a removed user cannot keep downloading, and how would you handle the edge case where the export job finishes after revocation but before cache invalidation completes?

Assessment: Queued work, cached links and a revocation deadline interact; an authenticated boundary plus race/cache policy must actually enforce the guarantee.

Evidence: experienced; provider-generated; actual tier hard; source IDs 85; API requests 154, 155, 156.

### P7F01 — PASS

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Assessment: Fallback requires non-scanning recency updates, deduplication and eviction; accepted as relative fresher Hard under the original rubric.

Evidence: fresher; curated fallback; actual tier hard; source IDs 66; API requests 157, 158, 159, 160, 161.

### P7F02 — PASS

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Assessment: Fallback combines unsorted input, nested/duplicate intervals and half-open endpoint ordering in a sweep/count algorithm; relative fresher Hard.

Evidence: fresher; curated fallback; actual tier hard; source IDs 63; API requests 162, 163, 164, 165, 166.

### P7F03 — PASS

Suppose a file-storage app has a `Storage` interface with `save(file)` and `delete(fileId)`. The app also guarantees this caller-visible rule: if `save()` fails halfway, no partial file should be visible to later `get()` calls. You need to add a new `EncryptedStorage` implementation without changing the code that orchestrates uploads and deletes. How would you structure the objects so that encryption can be swapped in while preserving that no-partial-file invariant, especially if `save()` can fail after writing the first chunk?

Assessment: A swappable encrypted writer must preserve no-partial-read visibility after a chunk failure; staged write/publication/cleanup is a concrete OOP boundary with a meaningful failure case.

Evidence: fresher; provider-generated; actual tier hard; source IDs 78; API requests 167, 168, 169.

### P7F04 — FAIL

A platform has `customers(customer_id, name)` and `orders(order_id, customer_id, status, created_at)`, where `status` is `PAID` or `CANCELLED`. Write a query that returns every customer plus three columns: total paid orders, total cancelled orders, and the date of their most recent PAID order. If a customer has no paid orders, that last column must be `NULL`. If two paid orders share the same `created_at`, pick the one with the larger `order_id`. How would you avoid row multiplication between the two counts and still make the latest-order rule deterministic?

Assessment: Only the latest PAID date is returned, so selecting a larger order_id for tied dates has no observable effect. Two conditional counts over the same table are routine and do not inherently create independent join multiplication.

Evidence: fresher; provider-generated; actual tier hard; source IDs 87; API requests 170, 171, 172, 173, 174.

### P7F05 — FAIL

A mobile client sends a POST to create a chat message, and the app may time out after the server has already committed it. The client is allowed to retry once automatically, but only if it can be sure the user won’t see two messages. The server can store a small durable record of past requests. What client/server contract would you use so that a retry either returns the same created message or a clear “already processed” result, and what should the server do if the same retry key arrives again with a different message body?

Assessment: The question asks for a standard idempotency contract, not concurrent claim implementation or an additional boundary. A key/result lookup plus payload conflict explanation suffices.

Evidence: fresher; provider-generated; actual tier hard; source IDs 75; API requests 175, 176, 177.

### P7F06 — FAIL

A task API exposes `GET /tasks/{id}` and `PUT /tasks/{id}`. Clients may rename a task and also change its `status`, but the business rule is: once a task is `DONE`, its `name` can still change, but `status` can never move back to `OPEN`. The client sends the last seen representation with the update, and two users might edit the same task at the same time. How would the server enforce that a stale update does not silently overwrite someone else’s change, while still rejecting only the illegal `DONE -> OPEN` transition and not every concurrent edit?

Assessment: Reject only the illegal transition, avoid lost updates, and do not reject every concurrent edit leave conflict/merge semantics insufficiently specified for full-representation PUT. A field merge/base-version contract needs clarification.

Evidence: fresher; provider-generated; actual tier hard; source IDs 81; API requests 178, 179, 180, 181, 182.

### P7F07 — FAIL

A shared `main` branch already contains commit `M` that introduced a bug. Two later commits, `A` and `B`, were added on top of `M`, and `B` depends on code added in `A`. You need to undo only `M` on `main` without rewriting history, and `A`/`B` must keep working after the recovery. What sequence of Git actions would you choose, and what would you verify afterward to make sure the branch still builds and the dependency between `A` and `B` is preserved?

Assessment: A/B depend on each other, but their relationship to the reverted M is unspecified. Generic revert-and-test advice still answers the task without resolving a concrete dependency.

Evidence: fresher; provider-generated; actual tier hard; source IDs 72; API requests 183, 184, 185.

### P7F08 — FAIL

A refresh-token endpoint should behave like this: if the same request ID is retried within 5 minutes, it must return the same new token; if the retry body differs, it should fail clearly. You’re asked to test this logic without calling a real auth service or using real wall-clock time. What single test setup would you use to make the retry behavior deterministic, and what exact edge case would you assert for the 5-minute boundary?

Assessment: Fake clock/request store setup is routine; exact expiry/retry semantics at five minutes are not stated, so a supposedly exact boundary oracle needs a product decision.

Evidence: fresher; provider-generated; actual tier hard; source IDs 90; API requests 186, 187, 188.

### P7F09 — FAIL

An API sometimes returns one user’s draft comment to another user, but only when two requests overlap and the server logs are enabled. You can add one temporary request ID to each request and run a controlled two-request test. What is the first explanation you would try to confirm, and what single experiment would you run to distinguish shared mutable state from a timing issue caused by logging? Include what result you would expect in each case.

Assessment: Shared mutable state and logging-induced timing are not mutually exclusive hypotheses. Toggling logging may expose the same race rather than distinguish its cause; the requested each-case oracle is misleading.

Evidence: fresher; provider-generated; actual tier hard; source IDs 69; API requests 189, 190, 191.

### P7F10 — FAIL

A file-download endpoint accepts a file ID and requires login. Users may belong to several teams; a file is private to its owning team, and IDs are easy to guess. How would you implement and test the authorization decision so changing the ID cannot expose another team's file, including a user removed from a team?

Assessment: Fallback remains a standard live team-membership check and denial test. Revocation is mentioned, but no stale/queued authorization state requires a nontrivial enforcement decision.

Evidence: fresher; curated fallback; actual tier hard; source IDs 84; API requests 192, 193, 194, 195, 196.

### -refinedR01 — PASS

Suppose a service handles POST /reports by writing a report row in PostgreSQL and then publishing an event to a queue for downstream email delivery. The contract is: on a retry, the same request_id for the same user must create at most one durable report and at most one email event, even if the process crashes after the DB commit but before publish. What deterministic integration test would you build to prove that behavior across restart, using explicit fault injection rather than sleeps? Please focus on the single most important failure boundary and the observable assertions you'd make.

Assessment: A real-DB crash/restart test with request identity and externally visible report/event assertions is advanced. Passing this one boundary must not be presented as proving exactly-once publication across every broker/ack failure.

Evidence: experienced; provider-generated; actual tier hard; source IDs 91; API requests 197, 198, 199. Additional case following P7E08; earlier failure remains counted.

### -refinedR02 — FAIL

How does Data Structures work in practice, and what is one key trade-off to keep in mind?

Assessment: Exhausted reviewed pack fell back to an explicitly Medium generic explanation. It fails the requested Hard experience/difficulty contract.

Evidence: fresher; curated fallback; actual tier medium; source IDs 66; API requests 200, 201, 202, 203, 204. Additional case following P7F01; earlier failure remains counted.

### -refinedR03 — FAIL

How would you use Algorithms in a Software Engineer application, and what common mistake would you watch out for?

Assessment: Explicitly Medium generic application question after Hard-pack exhaustion; not a Hard success.

Evidence: fresher; curated fallback; actual tier medium; source IDs 63; API requests 205, 206, 207, 208, 209. Additional case following P7F02; earlier failure remains counted.

### -refinedR04 — FAIL

A note app lets users own notes and share them with teammates. A share can also be revoked, but revocation is processed asynchronously: for a short time, the note may still show in a client cache even after the server has marked the share as revoked. If a user is the owner, they can edit; if they are only a shared viewer, they can read but not edit. How would you enforce access at the server boundary so a revoked viewer cannot keep editing by replaying an old note ID, and what single test would you run to prove the revoke takes effect on the next write even if the cached view is stale?

Assessment: Shared viewers could never edit, so denying their writes before and after revocation does not prove revocation worked. The test would pass even if revoked read access remained exposed.

Evidence: fresher; provider-generated; actual tier hard; source IDs 84; API requests 210, 211, 212, 213, 214. Additional case following P7F10; earlier failure remains counted.

### -refinedR05 — FAIL

How does a hash map work under the hood, and what happens when two keys hash to the same bucket?

Assessment: Hash-collision definition is explicitly Medium and not the requested Hard task; retained as an exhaustion failure.

Evidence: fresher; curated fallback; actual tier medium; source IDs 66; API requests 215, 216, 217, 218, 219. Additional case following -refinedR02; earlier failure remains counted.

### -refinedR06 — FAIL

What is the main difference between SQL and NoSQL databases, and how do you decide which to use for a project?

Assessment: Fallback switches from Algorithms to SQL vs NoSQL and reports Medium. It fails both the requested reasoning depth and selected-topic continuity.

Evidence: fresher; curated fallback; actual tier medium; source IDs 63; API requests 220, 221, 222, 223, 224. Additional case following -refinedR03; earlier failure remains counted.

### -refinedR07 — PASS

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Assessment: Fresh-session fallback again requires non-scanning recency/eviction coordination. Counted as a fallback, not generated improvement.

Evidence: fresher; curated fallback; actual tier hard; source IDs 66; API requests 225, 226, 227, 228, 229. Additional case following -refinedR05; earlier failure remains counted.

### -refinedR08 — PASS

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Assessment: Fresh-session fallback interval sweep requires careful tied endpoint handling, duplicate/nested intervals and sorting/count invariants. Relative fresher Hard, not senior system design.

Evidence: fresher; curated fallback; actual tier hard; source IDs 63; API requests 230, 231, 232, 233, 234. Additional case following -refinedR06; earlier failure remains counted.

## Partial case -refinedR09 — not returned

Suppose you’re building a small search history feature for a browser. You receive a stream of typed queries, and you must keep only the most recent 5 unique queries in the order they were last seen. If a query appears again, it should move to the end; if a 6th unique query arrives, the oldest one should be removed. What data structure approach would you use to support this efficiently, and how would you handle the edge case where a repeated query is already in the history?

Actual semantic-screen reason: The problem is coherent and realistic, but it is a familiar LRU-style exercise with a straightforward data-structure answer. It asks for one primary implementation task with a simple repeated-item edge case, but the reasoning demand is limited and does not require substantial interaction among constraints beyond basic recency update and fixed-capacity eviction.

Agent observation: no explicit non-scanning/constant-time operation requirement is given; a five-entry list can answer this routine recency exercise. It is below the stated Hard target. This draft was rejected, not delivered as a final question. Its second draft reservation was denied by the budget guard. Requests 235–237 (query embedding, generation, screen) succeeded; no second generation was sent. It is excluded from returned-output and confirmed-final counts, but included in cost and draft evidence.
