"""Reviewed, bounded Software Engineering scenarios for provider outages.

These are fallbacks, not substituted for measured provider-generated questions.
Order is topic/profile-specific. Exhaustion is explicit; no lower tier, topic
substitution or paraphrased recycling is permitted.
"""

ENTRY = {
    "data_structures": "A search box keeps the last 100 distinct queries in most-recent-first order. Repeating a query moves it to the front; adding a 101st evicts the oldest. How would you implement these operations without scanning all 100 entries, including the repeat-then-evict boundary?",
    "algorithms": "A calendar uses half-open intervals [start, end), and touching intervals do not overlap. Given an unsorted list that can contain duplicates and nested intervals, how would you compute the maximum number of simultaneous meetings without counting a meeting ending at 10:00 against one starting at 10:00?",
    "object_oriented_programming": "A file-import pipeline must validate each row before saving it. CSV and JSON readers share validation, but a dry-run must report exactly the same validation errors without writing anything. How would you separate the responsibilities so adding a reader cannot accidentally bypass validation or write during a dry-run?",
    "sql": "Given users(id), events(id, user_id, created_at, status), return every user with their latest successful event ID, or NULL when none exists. Timestamps can tie, so larger event ID wins. How would you write the query without losing users who have only failed events or returning tied duplicates?",
    "http": "An editor loads a document and its version, then saves a full replacement. Two tabs load version 7; one saves before the other. The server can atomically compare versions and update. How would you design the HTTP save request and response so the stale tab cannot silently overwrite the first save, including its retry after a lost response?",
    "rest_apis": "A task API lists tasks by (created_at, id), newest first. New tasks may appear between page requests, IDs break timestamp ties, and the client wants each older task once while scrolling. How would you define the next-page cursor and query, including what happens if the last returned task is deleted?",
    "git": "On a shared Git branch, commit A adds a parser function, B calls it, and C fixes an unrelated typo. A's faulty behavior must be undone without rewriting history, but B's intended feature and C must keep working. Reverting A alone breaks B. How would you prepare and verify a safe recovery patch?",
    "testing": "A cache entry expires exactly 60 seconds after insertion. Reading it must not extend its lifetime; a new write does. How would you test this deterministically without sleeping, including reads just before and at expiry and an overwrite before expiry?",
    "debugging": "A list page shows duplicate items only when two filter requests finish out of order. Each response is correct in isolation; refreshing removes the duplicates. How would you use a controlled reproduction to locate the state-update error and verify a fix when the older response arrives last?",
    "security_fundamentals": "A file-download endpoint accepts a file ID and requires login. Users may belong to several teams; a file is private to its owning team, and IDs are easy to guess. How would you implement and test the authorization decision so changing the ID cannot expose another team's file, including a user removed from a team?",
}

SENIOR = {
    "data_structures": "A messaging consumer deduplicates event IDs for 24 hours at 50,000 events/second, but cannot keep the full window in RAM. Replays can arrive after restart and false positives would lose messages. How would you structure durable state and memory acceleration so a crash cannot mark an unprocessed event complete?",
    "algorithms": "An in-memory search index has 10 million timestamped records, 100 range reads per second and 10,000 inserts per second in one-minute bursts. Results must include acknowledged inserts, and queries may return many records. How would you choose and implement an indexing strategy rather than just compare Big-O, accounting for update cost, locality and merge work?",
    "object_oriented_programming": "A storage interface promises atomic create-if-absent and returns created or already-exists. One backend offers conditional writes, another only read and overwrite, but both allow versioned keys. How would you redesign the interfaces and calling workflow so clients cannot accidentally assume atomicity on the weaker backend, while still supporting useful uploads?",
    "sql": "A booking transaction must reserve all requested seats or none. Requests overlap, locks can deadlock, and confirmations are sent by a separate worker after commit. How would you implement the transaction and retry boundary to prevent overselling and avoid sending confirmations for aborted reservations?",
    "http": "A file-import POST can finish importing after the client times out. The server stores request keys and jobs in one database transaction; clients may retry concurrently with the same key but different bodies. How would you define and implement the retry contract, including a response lost after commit?",
    "rest_apis": "An activity API promises a snapshot of the items visible when page one is requested, sorted by (created_at, id). Inserts and deletions continue during paging, and storing a full result per client is too costly. How would you implement a bounded-lifetime cursor contract without silently promising consistency that your storage cannot provide?",
    "git": "A deployed merge changed both code and a data format. The migration cannot be reversed and the previous binary cannot read the new format; the shared branch has subsequent unrelated fixes. How would you plan a verifiable forward recovery using Git without treating a code revert as a data rollback?",
    "testing": "A message worker writes a result and acknowledges delivery separately. A crash can happen between them, and the queue redelivers unacknowledged messages. How would you build deterministic fault-injection tests that distinguish lost work from duplicate externally visible results across restarts?",
    "debugging": "After a release, p99 latency triples while median latency, CPU and database query duration stay flat. Traces show the extra time before acquiring a database connection, and active connections remain at the pool limit after requests finish. How would you discriminate a leak from longer legitimate connection ownership using a safe experiment before choosing a mitigation?",
    "security_fundamentals": "A report export runs asynchronously and can be downloaded through a cached sharing link. Access must be revoked within 30 seconds of team removal even if the export was queued earlier. How would you enforce this contract across the job, download authorization and cache without assuming an expiring URL alone provides timely revocation?",
}


def hard_fallback_candidates(topic: str, experience_level: str) -> list[str]:
    return [text for text, _ in hard_fallback_records(topic, experience_level)]


def hard_fallback_records(topic: str, experience_level: str) -> list[tuple[str, str]]:
    from app.modules.knowledge.retriever import retrieval_topics
    from app.modules.interview.question_families import family_marker, covered_topic_key

    if covered_topic_key(topic) is None:
        return []

    pack = ENTRY if experience_level in {"internship", "fresher"} else SENIOR
    extra = (
        EXTRA_ENTRY if experience_level in {"internship", "fresher"} else EXTRA_SENIOR
    )
    entry = experience_level in {"internship", "fresher"}
    keys = {
        "data_structures": (
            ["recency_eviction", "maximum_stack", "circular_resize"]
            if entry
            else ["durable_dedup", "inflight_cache_publication"]
        ),
        "algorithms": (
            ["peak_overlap", "covered_event_count", "earliest_free_slot"]
            if entry
            else ["burst_range_index", "external_exact_topk"]
        ),
        "object_oriented_programming": (
            ["validated_import", "listener_snapshot"]
            if entry
            else ["bounded_reader_rollback", "plugin_cleanup"]
        ),
        "sql": (
            ["latest_eligible_identity", "independent_aggregates"]
            if entry
            else ["reservation_outbox", "reservation_outbox", "snapshot_aggregates"]
        ),
        "http": (
            ["versioned_retry", "idempotent_create"]
            if entry
            else ["idempotent_create", "versioned_retry"]
        ),
        "rest_apis": (
            ["live_cursor", "field_patch_merge"]
            if entry
            else ["snapshot_cursor", "sync_retention"]
        ),
        "git": (
            ["dependent_revert", "dependent_revert"]
            if entry
            else ["migration_recovery", "security_revert_chain"]
        ),
        "testing": (
            ["stale_expiry", "out_of_order_response"]
            if entry
            else ["crash_outbox_oracle", "generation_swap_oracle"]
        ),
        "debugging": (
            ["cache_vs_shared_state", "listener_vs_upstream"]
            if entry
            else ["pool_lease_hypotheses", "cache_refresh_hypotheses"]
        ),
        "security_fundamentals": (
            ["authorization_transition", "authorization_transition", "single_use_reset"]
            if entry
            else [
                "revoked_export_principal",
                "revoked_export_principal",
                "single_use_reset",
            ]
        ),
    }
    canonical = {
        "object_oriented_programming": "oop",
        "security_fundamentals": "security",
    }
    return [
        (text, family_marker(canonical.get(key, key), experience_level, family))
        for key in retrieval_topics(topic)
        if key in pack
        for text, family in zip(
            [pack[key], *extra.get(key, [])], keys[key], strict=True
        )
    ]


# Agent-reviewed outage coverage. These are reported separately from provider
# construction/evaluation, and never establish semantic-screen ground truth.
ENTRY["security_fundamentals"] = (
    "Mira can edit a shared note until its grant is revoked; its owner retains edit access. An edit can read the old permission, then revocation can commit before the edit writes. Both policy and note live in one database. How would you make authorization plus mutation atomic so an edit ordered after revocation cannot commit, and construct a test for that interleaving without denying the owner's edit?"
)
ENTRY["testing"] = (
    "A cache write schedules expiry at t+60. A refresh creates a new generation and timer, but the old timer may still fire; at age >=60 the current generation expires. How would you build a deterministic test that proves an old expiry cannot delete the refreshed generation and the new one expires at its own boundary, without sleeps?"
)
SENIOR["object_oriented_programming"] = (
    "A parser reads from seekable files or non-seekable network streams. It needs at most 64 KB of lookahead, may roll back an incomplete header, and must release resources on cancellation. How would you design the reader objects and caller workflow so retrying a parse does not consume bytes twice or leak a stream, without buffering the whole file?"
)

EXTRA_ENTRY = {
    "data_structures": [
        "A stack must support push, pop and maximum in constant time without scanning. Values may repeat, and undoing a push must restore the earlier maximum. How would you represent the extra state and trace push(4), push(7), push(7), pop, pop so removing one 7 does not prematurely lose the maximum?",
        "A fixed-size FIFO uses a circular array. After dequeues its live elements wrap across the array boundary; it must grow when full without losing order. How would you implement the resize and index updates so enqueue and dequeue still work after wrapping, including an empty queue?",
    ],
    "algorithms": [
        "Event timestamps are sorted and duplicates represent different events. Unsorted half-open query windows may overlap or nest. Count events covered by any window exactly once, without rescanning every event per window; empty windows contribute nothing. How would you combine the windows and event boundaries so events at a window's end are excluded but duplicate events inside it all count?",
        "Find the earliest free slot of length k inside opening hours [open,close). Busy half-open intervals are unsorted, can nest or overlap, and may extend outside opening hours; touching intervals leave no gap. How would you find the slot without scanning each time unit, including an empty busy list and a slot that ends exactly at close?",
    ],
    "object_oriented_programming": [
        "A registry dispatches to a start-of-call listener snapshot. A listener may change registration and trigger a nested dispatch; the nested call uses current registration while the outer snapshot stays unchanged. How would you implement per-dispatch ownership and cleanup so mutation, reentrancy and a callback exception cannot skip an outer listener or corrupt the next dispatch?"
    ],
    "sql": [
        "Tables: users(id PK), posts(id PK,user_id), likes(id PK,user_id). Return every user with their post count and received-like-record count, including zero for each missing child set. A user can have several rows in both child tables. How would you write the query without multiplying one count by the other, and verify the case with two posts and three like rows?"
    ],
    "http": [
        "POST /tasks accepts a retry key scoped to the logged-in user. Two identical retries may race; a changed body with the same key must conflict, and a response can be lost after commit. Tasks and keys share one database transaction. How would you implement the key claim and result lookup so the client gets one task ID rather than two tasks or an incorrect conflict after its own successful commit?"
    ],
    "rest_apis": [
        "PATCH /tasks carries base field values and proposed changes. Concurrent edits to different fields may merge, while two edits to the same field must conflict; DONE cannot return to OPEN. How would you atomically validate and apply a patch so a stale name edit can preserve a newer DONE status, including a stale patch that tries to reopen the task?"
    ],
    "git": [
        "Commit A changes a shared parser to reject empty input, B adds a caller that depends on its new return type, and C fixes an unrelated typo. The rejection must be removed without breaking B or losing C, on a published branch. How would you prepare a history-preserving recovery and tests rather than blindly reverting A's entire patch?"
    ],
    "testing": [
        "A canceled search request may still finish after a later query's response. Only the latest query may update visible results, including when an earlier rejection arrives last. How would you build deferred-response tests that force both completion orders and cancellation without sleeps, and assert against the displayed query/result pair rather than just call counts?"
    ],
    "debugging": [
        "A component emits duplicate notifications after repeated mount/unmount cycles. Either listeners are not removed or the upstream source emits each event twice, and both defects could coexist. With control over source delivery and lifecycle calls, what experiment would separate these causes and what distinct observations would you expect?"
    ],
    "security_fundamentals": [
        "A shared-note user can write while their grant is ACTIVE, then is changed to READ_ONLY but remains allowed to read. Login tokens may contain the old role. After the role change commits, how would you enforce and test that their next write fails while reads and the owner's writes still succeed, including replay of an earlier update request?"
    ],
}

EXTRA_SENIOR = {
    "data_structures": [
        "A bounded cache starts an asynchronous load on a miss. Before it finishes, a newer write or delete may commit; old loads must not overwrite new values or resurrect deleted entries. How would you design per-key state and eviction so this invariant survives load completion racing with eviction, without retaining unbounded tombstones?"
    ],
    "algorithms": [
        "An input larger than RAM contains highly skewed word frequencies. Return the exact top k words, breaking count ties lexicographically, with bounded memory and limited disk passes. How would you choose a partition/merge strategy and handle a single hot partition without silently switching to approximate counts?"
    ],
    "object_oriented_programming": [
        "A plugin pipeline acquires a stream, a temporary writer and a result handle in stages. Any stage can fail or be canceled; only a complete result may become visible, and cleanup must run exactly once per acquired resource. How would you design ownership and composition so adding a plugin cannot bypass cleanup or publish a partial result, including retry after cancellation?"
    ],
    "sql": [
        "A reservation request has a durable request ID and several item quantities. Concurrent requests overlap, and deadlocks may force full transaction retries; confirmation delivery uses an at-least-once worker. How would you atomically prevent negative stock, deduplicate the reservation and create recoverable confirmation work without charging a remote service inside the retry loop?"
    ],
    "http": [
        "PUT /objects replaces content only at an expected version and carries a principal-scoped operation ID. Its response may be lost, and a later operation can then replace the object again. How would you store and check operation identity so retrying the first PUT recovers its original outcome without overwriting the later version or mistaking its own success for a new conflict?"
    ],
    "rest_apis": [
        "A sync API streams versioned updates and deletion tombstones through a cursor; retained history lasts seven days. A client returns after ten days and still has local rows deleted during its absence. How would you define and implement a bounded resync handshake that cannot silently miss those deletions or mix a full snapshot with concurrent incremental changes?"
    ],
    "git": [
        "A security fix in main was accidentally reverted with a feature merge. The team now needs that feature reintroduced on a shared branch with subsequent good commits preserved. How would you plan the revert-of-revert or forward-fix sequence and verification so the merge history does not silently omit the security fix?"
    ],
    "testing": [
        "An index rebuild snapshots a base, collects acknowledged inserts in a delta, then swaps generations. Reads must never mix generations and inserts acknowledged during rebuild must remain visible. How would you use deterministic barriers and independent expected-result assertions to expose a lost-delta or mixed-generation race without sleeps?"
    ],
    "debugging": [
        "Tail latency spikes when a hot cache entry expires. It could be synchronized refresh contention or a slow upstream request, and both can occur together. How would you use controlled expiry in a bounded canary and per-phase timings to distinguish these effects before choosing a mitigation that might overload the upstream?"
    ],
    "security_fundamentals": [
        "An export job was authorized for a tenant user when queued, but that user's access is revoked before execution. The worker itself has broad service privileges and results are cached. How would you bind and recheck the original principal, resource and policy at execution and publication so worker credentials cannot bypass revocation, including a revocation during generation?"
    ],
}

# Distinct competencies added only where Phase 7.1 measured exhaustion.
EXTRA_ENTRY["security_fundamentals"].append(
    "A password-reset token is bound to one user and expires after 15 minutes. Store only its digest. Two requests with that token may race to set different passwords, and a response may be lost after commit. How would you atomically validate and consume the token with the password update so at most one change succeeds and invalid, expired or reused tokens change nothing?"
)
EXTRA_SENIOR["security_fundamentals"].append(
    "Password resets use high-entropy tokens stored only as user-bound digests with expiry. Issuing a new token invalidates old ones, while two redemptions or a redemption and reissue may race. How would you define transaction boundaries and ordering so each valid token changes the password at most once, an old in-flight token cannot commit after reissue, and a lost response never causes a second change?"
)
EXTRA_SENIOR["sql"].append(
    "Tables: accounts(id PK), events(id PK,account_id,at,eligible,amount). In one statement snapshot over UTC [2026-01-01,2026-02-01), return every account ID, its latest eligible event ID, eligible event count and amount sum. Eligible means eligible=true and non-NULL at; ties choose higher event ID. Missing events give NULL ID and zero count/sum; NULL amounts contribute nothing and an all-NULL sum is zero. How would you select one identity without reducing or multiplying the independent aggregate?"
)
