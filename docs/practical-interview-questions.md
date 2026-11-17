# Practical interview difficulty — question evidence

Completed 2026-11-17. These are actual provider/fallback outputs, reviewed provisionally by the agent under the user’s revised practical-interview criteria. No independent human review was available. Previous Phase 7/7.1/7.2 labels are unchanged and are not compared as though the criteria were identical.

Review covers relevance, correctness, clarity, interview practicality, experience-appropriate challenge and conversational variety. A familiar or standard technique is not a failure. “Usable” is a qualitative assessment, not a benchmark score or grading change.

See [implementation and verification](practical-interview-difficulty.md). Raw requests, sources, diagnostics and usage remain under `storage/practical-interviews/`.

## First representative run — 60 questions

The first run exposed an overly strict diagnostic parser. Its 18 Hard fallback deliveries are retained, not replaced with later successes. Easy and Medium generation did not use that parser.

### F-easy-01 — Data Structures · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 4.709s.

When would you choose a set instead of a list for checking whether an item exists?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-02 — Object-Oriented Programming · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 3.122s.

In an object-oriented program, what is the difference between state shared by a class and state owned by an individual instance?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-03 — SQL · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.764s.

How does a LEFT JOIN differ from an INNER JOIN?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-04 — HTTP · fresher · easy

Origin: AI plain. Type tag: applied. Elapsed: 2.977s.

If a client sends a DELETE request for a resource and then sends the same DELETE request again, what should you expect to happen, and why?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-05 — Algorithms · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.736s.

What is the main precondition for binary search to work correctly?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-06 — Git · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.619s.

Why would you use git revert instead of git reset on a branch that other people may already have pulled?

Review: **usable**. A practical version-control/recovery discussion. Clarify the intended surviving behavior when necessary.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-07 — Testing · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 3.338s.

What is a test fixture, and why is it important to keep tests isolated from each other?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-08 — Debugging · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.972s.

If a program is failing with an error, what information would you collect first to help debug it?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-09 — REST APIs · fresher · easy

Origin: AI plain. Type tag: applied. Elapsed: 2.966s.

If your API has an endpoint to fetch a single order, how would you handle the case where the order ID does not exist so the client can tell the difference between a successful response and a missing resource?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-easy-10 — Security Fundamentals · fresher · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.861s.

How is authorization different from authentication?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-01 — Data Structures · fresher · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.993s.

How would you deduplicate a list of records while preserving the first occurrence, and what data structure would you use to do it?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-02 — Object-Oriented Programming · fresher · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.724s.

Suppose your checkout code currently talks directly to one payment provider, but you want to replace that provider later without changing the checkout flow. How would you design the payment part using an interface and composition?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-03 — SQL · fresher · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.892s.

What is the difference between putting a condition in the ON clause of a LEFT JOIN versus putting the same condition in the WHERE clause?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-04 — HTTP · fresher · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.740s.

If a client sends a POST request to place an order and the request times out, what should the client assume about whether the order was created, and how would you handle a retry safely?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-05 — Algorithms · fresher · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.888s.

In a binary search on a sorted array, what invariant do you keep true about the search range, and why can the algorithm get stuck if you update low and high incorrectly when only two elements remain?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-06 — Git · fresher · medium

Origin: AI plain. Type tag: applied. Elapsed: 3.655s.

A feature branch has already been merged into the shared main branch, and later you discover that the merge introduced a bug. Some newer commits on main also depend on nearby code from that feature. How would you handle the rollback in Git so you avoid breaking the later work?

Review: **usable**. A practical version-control/recovery discussion. Clarify the intended surviving behavior when necessary.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-07 — Testing · fresher · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.562s.

How would you test timeout recovery in code without depending on a live external service?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-08 — Debugging · fresher · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.577s.

Suppose an API sometimes returns data that seems to belong to a different request. How would you investigate that, and what would you check first?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-09 — REST APIs · fresher · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.977s.

How would you prevent a client from accidentally overwriting someone else’s changes when both are editing the same resource through a REST API?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-medium-10 — Security Fundamentals · fresher · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.801s.

How would you test a report endpoint to make sure one logged-in user cannot view or edit another user’s report by changing the report ID in the URL?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-01 — Data Structures · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.979s.

A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-02 — Object-Oriented Programming · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.615s.

A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-03 — SQL · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.555s.

Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-04 — HTTP · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.904s.

An editor loads a document and its version, then saves a full replacement. Two tabs load version 7; one saves before the other. The server can atomically compare versions and update. How would you design the HTTP save request and response so the stale tab cannot silently overwrite the first save, including its retry after a lost response?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-05 — Algorithms · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.395s.

A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-06 — Git · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 3.989s.

A shared branch has a merge that added search and broke validation.

Shared merge M adds a search feature and disables validation. Later commit D fixes search pagination and depends on the feature API. Restore validation without removing the search feature or D, preserving shared history. Blindly reverting M removes APIs D requires; inspect merge parents and test both validation and pagination.

How would you recover validation with a minimal commit, while keeping the search API and D intact and proving what stayed removed?

Review: **wording**. The final phrase about proving what stayed removed is awkward; ask to verify restored validation and retained pagination/search behavior.

Relevant to role/skill; no false premise observed; wording improvement. distinct within the tested fixed-difficulty history.

### F-hard-07 — Testing · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.121s.

A cache write schedules expiry at t+60. A refresh creates a new generation and timer, but the old timer may still fire; at age >=60 the current generation expires. How would you build a deterministic test that proves an old expiry cannot delete the refreshed generation and the new one expires at its own boundary, without sleeps?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-08 — Debugging · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.218s.

A list page shows duplicate items only when two filter requests finish out of order. Each response is correct in isolation; refreshing removes the duplicates. How would you use a controlled reproduction to locate the state-update error and verify a fix when the older response arrives last?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-09 — REST APIs · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.745s.

A task API lists tasks by (created_at, id), newest first. New tasks may appear between page requests, IDs break timestamp ties, and the client wants each older task once while scrolling. How would you define the next-page cursor and query, including what happens if the last returned task is deleted?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-hard-10 — Security Fundamentals · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.938s.

Mira can edit a shared note until its grant is revoked; its owner retains edit access. An edit can read the old permission, then revocation can commit before the edit writes. Both policy and note live in one database. How would you make authorization plus mutation atomic so an edit ordered after revocation cannot commit, and construct a test for that interleaving without denying the owner's edit?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-01 — Data Structures · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.812s.

When would you choose a set instead of a list for checking whether an item exists?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-02 — Object-Oriented Programming · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.970s.

In a language of your choice, what is the difference between state shared by a class and state owned by an individual object instance?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-03 — SQL · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.836s.

What is the difference between an INNER JOIN and a LEFT JOIN?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-04 — HTTP · experienced · easy

Origin: AI plain. Type tag: applied. Elapsed: 2.822s.

If a client times out after sending a DELETE request, would you retry it automatically? Why or why not?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-05 — Algorithms · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.903s.

What precondition does binary search require, and why does that matter for its correctness?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-06 — Git · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.851s.

What is the difference between git revert and git reset, and when would you prefer revert on a branch that other people already use?

Review: **usable**. A practical version-control/recovery discussion. Clarify the intended surviving behavior when necessary.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-07 — Testing · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.456s.

What is a test fixture, and why is it important to keep tests isolated?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-08 — Debugging · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.640s.

A bug only seems to happen when a cache is warm. How would you start investigating that, and what would you compare to narrow down the cause?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses. The wording is scenario-like despite its conceptual tag; the mix is a flexible target.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-09 — REST APIs · experienced · easy

Origin: AI plain. Type tag: applied. Elapsed: 2.993s.

If a client requests an order by ID and that order does not exist, how would you design the API response so the client can tell it was a missing resource rather than a server problem?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-easy-10 — Security Fundamentals · experienced · easy

Origin: AI plain. Type tag: conceptual. Elapsed: 2.837s.

How is authorization different from authentication?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-01 — Data Structures · experienced · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.627s.

How would you deduplicate a list of records while preserving the first occurrence, and what data structure choice would you make for that?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-02 — Object-Oriented Programming · experienced · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.657s.

Suppose your checkout flow should work with different payment providers, but you don’t want to change the orchestration code each time a provider changes. How would you structure the classes or interfaces, and what would you keep in the checkout flow versus in the provider-specific implementation?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-03 — SQL · experienced · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.950s.

In SQL, what is the practical difference between putting a filter on the right table in a LEFT JOIN’s ON clause versus in the WHERE clause?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-04 — HTTP · experienced · medium

Origin: AI plain. Type tag: applied. Elapsed: 3.062s.

If a client sends a POST to create an order and the request times out after the server may have processed it, what should the client do next to avoid creating a duplicate order?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-05 — Algorithms · experienced · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.857s.

In a sorted array, binary search is usually used to find a target value. What invariant would you keep while searching, and how would you choose the low, high, and mid updates so the loop always makes progress, even when the array has duplicate values or only two elements left?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-06 — Git · experienced · medium

Origin: AI plain. Type tag: applied. Elapsed: 3.671s.

A shared branch has a bug fix merged into it, but a later commit changed nearby lines in the same file. How would you safely revert the buggy change without breaking the follow-on work, and what would you check before deciding whether to use a revert or a forward fix?

Review: **clarify**. The prompt calls the earlier change a bug fix, then asks to revert the buggy change. Identify which commit/behavior should be undone before assessing the recovery plan.

Relevant to role/skill; no false premise observed; needs clarification. distinct within the tested fixed-difficulty history.

### E-medium-07 — Testing · experienced · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.984s.

How would you test a function’s observable behavior when it depends on time or an external service, and what would you choose to fake or mock versus verify with a real integration test?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-08 — Debugging · experienced · medium

Origin: AI plain. Type tag: applied. Elapsed: 3.438s.

Suppose an API occasionally returns part of another request’s data. How would you investigate that bug, and what evidence would you look for to confirm whether shared mutable state is the cause?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-09 — REST APIs · experienced · medium

Origin: AI plain. Type tag: conceptual. Elapsed: 2.857s.

How would you prevent lost updates when two clients edit the same ticket through a REST API?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-medium-10 — Security Fundamentals · experienced · medium

Origin: AI plain. Type tag: applied. Elapsed: 2.947s.

How would you test a report endpoint to make sure one authenticated user cannot read or modify another user’s report just by changing the report ID?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-01 — Data Structures · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.730s.

A messaging consumer deduplicates event IDs for 24 hours at 50,000 events/second, but cannot keep the full window in RAM. Replays can arrive after restart and false positives would lose messages. How would you structure durable state and memory acceleration so a crash cannot mark an unprocessed event complete?

Review: **clarify**. The retained legacy fallback does not define what processing an event means. Clarify the observable effect/atomic boundary before assessing crash recovery. This was a pre-fix fallback, not the final simple deduplication question.

Relevant to role/skill; effect underspecified; needs clarification. distinct within the tested fixed-difficulty history.

### E-hard-02 — Object-Oriented Programming · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.929s.

A parser reads from seekable files or non-seekable network streams. It needs at most 64 KB of lookahead, may roll back an incomplete header, and must release resources on cancellation. How would you design the reader objects and caller workflow so retrying a parse does not consume bytes twice or leak a stream, without buffering the whole file?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-03 — SQL · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.782s.

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-04 — HTTP · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.486s.

A file-import POST can finish importing after the client times out. The server stores request keys and jobs in one database transaction; clients may retry concurrently with the same key but different bodies. How would you define and implement the retry contract, including a response lost after commit?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-05 — Algorithms · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.159s.

An in-memory search index has 10 million timestamped records, 100 range reads per second and 10,000 inserts per second in one-minute bursts. Results must include acknowledged inserts, and queries may return many records. How would you choose and implement an indexing strategy rather than just compare Big-O, accounting for update cost, locality and merge work?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-06 — Git · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.245s.

A deployed merge changed both code and a data format. The migration cannot be reversed and the previous binary cannot read the new format; the shared branch has subsequent unrelated fixes. How would you plan a verifiable forward recovery using Git without treating a code revert as a data rollback?

Review: **usable**. A practical version-control/recovery discussion. Clarify the intended surviving behavior when necessary.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-07 — Testing · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.024s.

A message worker writes a result and acknowledges delivery separately. A crash can happen between them, and the queue redelivers unacknowledged messages. How would you build deterministic fault-injection tests that distinguish lost work from duplicate externally visible results across restarts?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-08 — Debugging · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.896s.

After a release, p99 latency triples while median latency, CPU and database query duration stay flat. Traces show the extra time before acquiring a database connection, and active connections remain at the pool limit after requests finish. How would you discriminate a leak from longer legitimate connection ownership using a safe experiment before choosing a mitigation?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-09 — REST APIs · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 3.875s.

An activity API promises a snapshot of the items visible when page one is requested, sorted by (created_at, id). Inserts and deletions continue during paging, and storing a full result per client is too costly. How would you implement a bounded-lifetime cursor contract without silently promising consistency that your storage cannot provide?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-hard-10 — Security Fundamentals · experienced · hard

Origin: AI plain. Type tag: conceptual. Elapsed: 5.339s.

Suppose you have an API where a logged-in user can fetch, update, or delete resources by ID. What server-side checks would you put in place to make sure the user can only act on resources they’re actually allowed to access, and why is relying on a valid token or hidden UI controls not enough?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

## Separate final Hard confirmation — 20 fresh questions

Run after the diagnostic fix and ordinary-debugging simplification. The final Git bank clarification and stable session style rotation were subsequently verified offline and by regressions, not counted as new paid results.

### F-confirm-01 — Data Structures · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 7.228s.

A media app tracks recently viewed items in a small cache.

Capacity K is a nonnegative integer. VIEW(id) marks it most recent; HAS(id) checks presence without changing order. HAS, refresh and eviction must each take constant time; new IDs evict the least recent only when full. A repeated VIEW at capacity must not evict another ID; K=0 retains nothing.

How would you keep VIEW, HAS, and eviction all constant time while handling the K=0 and repeated VIEW boundary cases?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-02 — Object-Oriented Programming · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 6.854s.

A team drafts reports privately before publishing them.

Readers see the old complete document or the new complete document, never a prefix. A caller writes a report privately, then publishes it with an available atomic replacement. If writing fails, the previous report stays readable and the incomplete report stays private.

How would you separate draft writing from publish time so readers never see a partial report, even if writing fails?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-03 — SQL · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 5.221s.

A file portal shows each user's accessible documents.

Tables: users(id; PK id); docs(id, owner_id; PK id); shares(id, user_id, doc_id, active; PK id). One result row per users.id. Return: user_id: users.id; visible: distinct visible document count. owner_id and user_id reference users.id; shares.doc_id references docs.id; only active=true shares qualify. Include zero-count users. NULL active is ineligible; ownership always grants visibility. A document owned and shared to the same user counts once; duplicate shares never inflate the count.

How would you count distinct visible docs per user by combining ownership and active shares without losing users who have none?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-04 — HTTP · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.801s.

An editor saves a document through a versioned HTTP API.

PUT replaces a document using its expected version and client operation ID. Effects: Replace content and increment version once. The client supplies an operation ID; keep committed outcomes for this exercise. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Committed retries return the recorded outcome, even after a newer write or lost response. For unseen operations, stale versions conflict; retry lookup and update must share one DB transaction.

How would you order retry lookup and the optimistic version check so a committed retry returns the stored outcome and stale writes still conflict?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-05 — Algorithms · fresher · hard

Origin: AI plain. Type tag: conceptual. Elapsed: 5.324s.

Suppose you have a sorted array of integers, and you want to find the first position where a target value could be inserted while keeping the array sorted. The input is the sorted array and the target value, and the output is the leftmost index where the target belongs, even if the target already appears multiple times. How would you structure a binary search so that it always makes progress and still works correctly for duplicate values and the case where the target is not present?

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-06 — Git · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.502s.

On a shared Git branch, commit A adds a parser function, B calls it, and C fixes an unrelated typo. A must be undone without rewriting history, but reverting A alone breaks B. How would you prepare and verify a safe revert that preserves C?

Review: **clarify-fixed-offline**. The observed fixed fallback did not explicitly require preserving B. That bank sentence was clarified after evaluation and validated offline; this old output remains unchanged.

Relevant to role/skill; no false premise observed; needs clarification. distinct within the tested fixed-difficulty history.

### F-confirm-07 — Testing · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.391s.

A cache refreshes entries while timer callbacks may arrive late.

PUT creates a new cache generation expiring at its write time plus 60; old timer callbacks can fire after refresh. At age >=60 the current generation is absent. An earlier generation's callback must not delete a newer unexpired value. Use a fake monotonic clock and controlled callback delivery, no sleeps; reads observe expiry even if callback delivery is late.

How would you test that a late callback cannot delete a newer live value after refresh?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-08 — Debugging · fresher · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 5.238s.

A widget reattaches and then starts seeing each event twice.

A component receives duplicate event notifications after it is unmounted and mounted again. Choose a focused first check and explain what its result would tell you. Use evidence rather than assuming the cause; do not change several things at once.

What first check would you run to tell whether the duplicate comes from registration or from upstream emission?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-09 — REST APIs · fresher · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 5.751s.

A task API lists tasks by (created_at, id), newest first. New tasks may appear between page requests, IDs break timestamp ties, and the client wants each older task once while scrolling. How would you define the next-page cursor and query, including what happens if the last returned task is deleted?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot. The rejected kernel is elaborate for a fresher; the delivered cursor fallback is more focused.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### F-confirm-10 — Security Fundamentals · fresher · hard

Origin: AI plain. Type tag: conceptual. Elapsed: 4.875s.

A logged-in user can view their own account details, and the frontend hides the "Edit other users" option for everyone except admins. What should the server check before allowing an update to a user record, and why is checking only that the requester is authenticated not enough?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-01 — Data Structures · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.101s.

A log processor must emit each event ID only once.

Process a large iterator of event IDs, keeping only the first occurrence of each ID. Preserve first-seen order without loading the entire input; explain time and memory costs. IDs may repeat far apart. A probabilistic filter must not silently discard a new ID.

How would you deduplicate this stream exactly while preserving first-seen order and keeping memory bounded by distinct IDs?

Review: **usable**. Useful collection/lookup/order choice or implementation; standard techniques are legitimate. Lower end of Experienced Hard for some candidates; use an answer-aware implementation/optimization follow-up rather than adding arbitrary failures.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-02 — Object-Oriented Programming · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.503s.

A media editor chains plugins that write through temp files.

A plugin transforms input using temporary files; only a completed result is published. A caller runs plugins in sequence and owns their intermediate files. If a plugin fails, release its temporary files and keep the previous result readable.

How would you design the plugin boundary so a failed step cleans its temp files and leaves the last good result readable?

Review: **usable**. Ordinary object responsibilities and implementation boundaries, without requiring architecture for its own sake. Lower end of Experienced Hard for some candidates; use an answer-aware implementation/optimization follow-up rather than adding arbitrary failures.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-03 — SQL · experienced · hard

Origin: fixed fallback. Type tag: applied. Elapsed: 4.869s.

A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?

Review: **usable**. A plausible query or comparison; accept correct alternative SQL forms and explain NULL/tie behavior where relevant.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-04 — HTTP · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 17.156s.

A profile API stores versioned documents with client-supplied operation IDs.

PUT replaces a document using its expected version and client operation ID. Effects: Replace content and increment version once. The client supplies an operation ID; keep committed outcomes for this exercise. Identity is principal-scoped and bound to a canonical body hash. Reusing an identity with different content conflicts. Committed retries return the recorded outcome, even after a newer write or lost response. For unseen operations, stale versions conflict; retry lookup and update must share one DB transaction.

How would you order retry lookup and optimistic version update so duplicates, stale writes, and lost responses all return the right outcome?

Review: **usable**. A realistic request/update/retry discussion; idempotence does not require identical response codes or exactly-once external effects.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-05 — Algorithms · experienced · hard

Origin: AI plain. Type tag: conceptual. Elapsed: 4.383s.

Given a sorted array of integers that may contain duplicates, how would you use binary search to find the first index of a target value? Please explain the invariant you would maintain, how you handle the boundary cases, and the time complexity.

Review: **usable**. Common problem-solving and reasoning about correctness/cost; familiarity is not a defect.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-06 — Git · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.400s.

A repo is re-adding a reverted feature after a security hotfix.

A feature merge M contained a security fix S. Revert R removed M and S. A later branch reintroduces the feature via commits descended from M. Restore the feature and S without resurrecting a known feature regression; preserve shared history. Merging the old branch alone may consider reverted commits already merged; inspect ancestry and merge parents.

How would you restore the feature and the security fix without bringing back the old regression, while keeping shared history intact?

Review: **usable**. A practical version-control/recovery discussion. Clarify the intended surviving behavior when necessary.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-07 — Testing · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 5.108s.

A checkout service writes an order and sends email confirmations.

An endpoint writes an order in a DB transaction and queues confirmation only after commit. Test success and DB rollback so only committed orders can queue confirmation. Use a test database or controlled transaction fake and a fake queue; assert observable state and call ordering.

How would you test commit success, rollback, and the call order with a fake DB and queue so only committed orders can enqueue confirmation?

Review: **usable**. Useful behavior, test inputs and assertions; ordinary fakes and mocks are valid.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-08 — Debugging · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 4.361s.

A news feed becomes sluggish right after its cache expires.

Requests become slow just after cache expiry, but normal cached requests are fast. Choose a focused first check and explain what its result would tell you. Use evidence rather than assuming the cause; do not change several things at once.

What first check would you make, and what would its result tell you about the slowdown?

Review: **usable**. A realistic symptom or investigation step; the opening need not enumerate multiple hypotheses.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-09 — REST APIs · experienced · hard

Origin: AI hybrid. Type tag: applied. Elapsed: 3.907s.

A dashboard is paging through live activity rows.

GET /activities lists rows newest first by immutable created_at and unique id; inserts can arrive between pages. Choose pagination that avoids returning an item twice, and explain whether new rows appear during the traversal. Timestamps can tie and the cursor row can be deleted. This is a live list, not a historical snapshot.

How would you paginate the changing list so no row is returned twice, and what happens to new rows during traversal?

Review: **usable**. A common API behavior/design discussion; live pagination is distinct from a historical snapshot.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

### E-confirm-10 — Security Fundamentals · experienced · hard

Origin: AI plain. Type tag: conceptual. Elapsed: 6.180s.

A user is authenticated with a valid token, but your API lets them read and update individual account records by ID. If the token is valid, what checks should the server still perform before returning or modifying a specific record, and why is hiding the record ID or the UI button not enough?

Review: **usable**. Relevant server-side authentication/authorization reasoning; a valid token alone is not an object permission. Lower end of Experienced Hard for some candidates; use an answer-aware implementation/optimization follow-up rather than adding arbitrary failures.

Relevant to role/skill; no false premise observed; answerable. distinct within the tested fixed-difficulty history.

## Final Hard rejection evidence

The final confirmation used three fallbacks. These are not counted as successful AI deliveries.

### F-confirm-06

Rejected draft:

A shared branch has a merge that added search and broke validation.

Shared merge M adds a search feature and disables validation. Later commit D fixes search pagination and depends on the feature API. Restore validation without removing the search feature or D, preserving shared history. Blindly reverting M removes APIs D requires; inspect merge parents and test both validation and pagination.

How would you restore validation without losing the search fix or the later pagination commit, and verify what stays changed?

Diagnostics:

- Hard family diagnostic: {"stage": "screen", "error": "ValueError", "family": "merge_recovery", "fields": []}

### F-confirm-09

Rejected draft:

A feed API pages live items after deletes and late inserts.

Rows have immutable unique (created_at,id). Page 1 fixes a creation watermark; later inserts may have older created_at but a larger monotonic ingest_id. Use a signed cursor carrying the last returned ordering pair and maximum ingest_id from page 1; return descending order without duplicates. Rows can be deleted, including the cursor row. The API is live: deletions may disappear, not a historical snapshot.

How would you design the cursor predicate and page contract so deleted rows and late inserts never cause duplicates or missed items?

Diagnostics:

- Hard family review: {"minimum_reasoning":"none","blocking_issue":"depth","quote":"Rows can be deleted, including the cursor row.","reason":"Plausible, but too open-ended for a fresher and combines pagination, deletes, late inserts, and cursor semantics into one deep design problem."}
- Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "live_cursor"}

### E-confirm-03

Rejected draft:

A billing dashboard needs per-account snapshot totals from event rows.

Tables: accounts(id; PK id); events(id, account_id, at, eligible, amount; PK id). One result row per accounts.id. Return: account_id: accounts.id; event_id: selected event ID; count: eligible event count; sum: eligible non-NULL amount sum. One statement snapshot; scope is UTC [2026-01-01,2026-02-01). eligible=true and non-NULL at; account_id references accounts.id. Include all accounts; no eligible event gives NULL event_id, count 0 and sum 0; all-NULL amounts sum to 0. Latest identity and aggregates use the same scoped rows; ranking must not reduce the aggregate to one row. Choose the latest by events.at, events.id descending; return event_id.

How would you return the chosen event and the aggregate from the same snapshot without letting the row choice multiply the totals?

Diagnostics:

- Hard family review: {"minimum_reasoning":"none","blocking_issue":"clarity","quote":"all-NULL amounts sum to 0","reason":"Ambiguous whether SUM ignores NULLs only after filtering or needs explicit COALESCE; otherwise the SQL task is plausible for experienced."}
- Hard family diagnostic: {"stage": "screen", "accepted": false, "family": "snapshot_aggregates"}

## Declared screen probes

These are authored diagnostic inputs, not generated interview questions or a new benchmark. Unusable/failed reviews are not counted as successful negative judgments.

### familiar-coding

How would you remove duplicate IDs from a list while preserving first-seen order?

Expected: accept; observed: accept.

{"minimum_reasoning": "Suitable: common coding task for a fresher; tests basic data-structure choice and order preservation.", "blocking_issue": "none", "quote": "", "reason": "Clear, ordinary implementation question with no contradictions or hidden constraints."}

### ordinary-sql

Given customers(id) and orders(id, customer_id), how would you list every customer with their number of orders, including zero?

Expected: accept; observed: accept.

{"minimum_reasoning": "Suitable: standard LEFT JOIN + GROUP BY task for a fresher SQL interview.", "blocking_issue": "none", "quote": "", "reason": "Clear, common, and answerable without extra constraints."}

### practical-oop

When would you favor composition over inheritance when adding a second payment provider, and what would your small interface look like?

Expected: accept; observed: accept.

{"minimum_reasoning": "Experienced OOP design choice; asks for a common trade-off and simple interface, which is plausible and not overconstrained.", "blocking_issue": "none", "quote": "", "reason": "Standard design judgment for adding another provider; concise and appropriate for the role level."}

### undefined-sql

Given users(id) and orders(id, user_id), write a query returning users.email and the order count for each user.

Expected: reject; observed: NOT VERIFIED / no usable review.

{"error": "APITimeoutError", "retried": false}

### impossible-oop

A stream cannot seek, buffer bytes or reopen its source. Implement a rewind method that always succeeds after any amount of reading.

Expected: reject; observed: NOT VERIFIED / no usable review.

{"error": "ValueError", "retried": false}

### actual-repeat

How would you remove duplicate IDs from a list while preserving first-seen order?

Expected: reject; observed: reject.

{"minimum_reasoning": "Yes, this is a plausible fresher question on arrays/lists and basic de-duplication using a set or hash-based approach.", "blocking_issue": "duplicate", "quote": "How would you remove duplicate IDs from a list while preserving first-seen order?", "reason": "Same question already appears in previous_questions; it repeats the exact task."}

## Answer-aware follow-ups

Candidate answers and feedback below are synthetic fixtures to test generation. No real candidate grading call or stored evaluation was made. All four follow-up texts were confirmed against actual provider responses.

### F-medium-03

Primary: What is the difference between putting a condition in the ON clause of a LEFT JOIN versus putting the same condition in the WHERE clause?

Synthetic candidate answer: An ON filter limits matches while keeping all left rows. A WHERE filter removes rows where the predicate is not true, including unmatched rows.

Follow-up (medium): If you had to verify this behavior in a database, how would you write a simple example query or test to show the difference between the ON and WHERE versions of a LEFT JOIN?

### F-medium-05

Primary: In a binary search on a sorted array, what invariant do you keep true about the search range, and why can the algorithm get stuck if you update low and high incorrectly when only two elements remain?

Synthetic candidate answer: When the midpoint is not the target I set low to mid or high to mid. I think this should always finish.

Follow-up (easy): Can you walk me through a smallest example, like an array with two elements, and show whether setting low = mid or high = mid actually makes the search range smaller on each step?

### E-medium-04

Primary: If a client sends a POST to create an order and the request times out after the server may have processed it, what should the client do next to avoid creating a duplicate order?

Synthetic candidate answer: A timeout does not tell us whether the order committed. Reuse a client operation key and have the server atomically store one job and its principal-scoped key, body hash and result.

Follow-up (medium): What would the server do if the same idempotency key is reused but the request body doesn’t match the original one?

### E-medium-08

Primary: Suppose an API occasionally returns part of another request’s data. How would you investigate that bug, and what evidence would you look for to confirm whether shared mutable state is the cause?

Synthetic candidate answer: I would increase the connection pool because then requests should stop seeing other users data.

Follow-up (easy): If you had two requests happening at the same time, what specific evidence would you look for in logs or request IDs to tell whether they were accidentally sharing state?

## Preserved evidence

Original outputs and stage-specific input hashes remain unchanged. `post-evaluation-changes.json` records the single Git fallback clarification; `final-integrity.json` records the later stable session-based style rotation and protected data checks. The initial 60 and final 20 are separate runs; no pooled “new quality pass rate” is claimed.
