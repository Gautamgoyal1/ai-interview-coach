"""Reviewed technical kernels, not prewritten final questions or candidate grades.

AI chooses a variant and authors scenario, primary ask and private follow-up.
The compiler owns correctness facts. Variants share one coverage marker: changing
the setting or a boundary does not make the same reasoning task novel in-session.
"""

from dataclasses import dataclass
from copy import deepcopy
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.interview.problem_spec import materialize_problem
from app.modules.interview.question_families import covered_topic_key, family_marker
from app.modules.interview.generation_errors import QuestionGenerationUnavailable
from app.modules.resume.catalog import resolve_role


class FamilyDraft(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    family_id: str
    variant: Literal["boundary", "extension"]
    scenario: str = Field(min_length=15, max_length=100)
    reasoning_decision: str = Field(min_length=35, max_length=180)
    follow_up_direction: str = Field(min_length=15, max_length=200)


@dataclass(frozen=True)
class ProblemFamily:
    id: str
    topic: str
    profile: str
    contract: dict
    extension: tuple[str, str]
    reasoning_goal: str
    approaches: tuple[str, str]

    def instantiate(self, draft: FamilyDraft, role: str, topic: str, level: str):
        if self not in reviewed_families(role, topic, level):
            raise ValueError("Reviewed family must match role, topic and experience")
        if draft.family_id != self.id:
            raise ValueError("Provider must use the selected reviewed family")
        if (
            not draft.reasoning_decision.endswith("?")
            or draft.reasoning_decision.count("?") != 1
        ):
            raise ValueError("Author one primary reasoning question")
        contract = deepcopy(self.contract)
        if draft.variant == "extension":
            key, extra = self.extension
            contract[key] += " " + extra
        return materialize_problem(
            dict(
                competency=self.reasoning_goal,
                scenario=draft.scenario,
                reasoning_decision=draft.reasoning_decision,
                valid_alternative_approaches=list(self.approaches),
                follow_up_direction=draft.follow_up_direction,
                technical_contract=contract,
            ),
            role,
            topic,
            level,
        )

    def brief(self):
        return dict(
            family_id=self.id,
            profile=self.profile,
            technical_contract=self.contract,
            extension=dict(field=self.extension[0], fact=self.extension[1]),
            reasoning_goal=self.reasoning_goal,
        )


FAMILIES: list[ProblemFamily] = []


def general(topic, profile, name, inputs, output, edge, extension, goal, approaches):
    FAMILIES.append(
        ProblemFamily(
            name,
            topic,
            profile,
            dict(
                kind="general",
                input_rules=inputs,
                required_observation=output,
                boundary_rule=edge,
            ),
            ("boundary_rule", extension),
            goal,
            approaches,
        )
    )


def oop(
    profile,
    name,
    guarantee,
    workflow,
    failure,
    unavailable,
    extension,
    goal,
    approaches,
):
    FAMILIES.append(
        ProblemFamily(
            name,
            "oop",
            profile,
            dict(
                kind="oop",
                interface_guarantee=guarantee,
                caller_workflow=workflow,
                failure_observation=failure,
                capability="capability_split_required" if unavailable else "achievable",
                unavailable_capability=unavailable,
                caller_steps=[workflow, failure],
            ),
            ("failure_observation", extension),
            goal,
            approaches,
        )
    )


general(
    "data_structures",
    "entry",
    "recency_eviction",
    "Capacity K is a nonnegative integer. VIEW(id) marks it most recent; HAS(id) checks presence without changing order.",
    "HAS, refresh and eviction must each take constant time; new IDs evict the least recent only when full.",
    "A repeated VIEW at capacity must not evict another ID; K=0 retains nothing.",
    "DELETE(id) must also take constant time, including the most recent ID.",
    "Implement bounded lookup, ordering and eviction with a concrete trace.",
    (
        "Hash lookup plus linked ordering.",
        "Indexed intrusive ordering with a free-node pool.",
    ),
)
general(
    "data_structures",
    "entry",
    "maximum_stack",
    "PUSH(x), POP and MAX must take constant time; values may repeat. Empty POP/MAX return empty.",
    "MAX returns the largest remaining value without scanning the stack.",
    "Removing one copy of the maximum must preserve another equal maximum.",
    "Trace PUSH(4), PUSH(7), PUSH(7), POP, POP.",
    "Implement a maximum stack and explain the extra state and cost.",
    (
        "Store a running maximum with each node.",
        "Use separate value and maximum stacks with duplicate counts.",
    ),
)
general(
    "data_structures",
    "entry",
    "circular_resize",
    "A FIFO queue uses a full circular array of capacity K>0; live items can wrap around the end.",
    "On enqueue to a full queue, double capacity and preserve FIFO; normal enqueue/dequeue are constant time.",
    "Resizing takes linear time; preserve order after dequeue, wrap, resize and an eventual empty queue.",
    "An iterator created after resizing must visit each remaining item once in FIFO order.",
    "Implement resize and index transitions, explaining amortized enqueue cost.",
    (
        "Copy live items to a contiguous new array.",
        "Copy the two wrapped spans with normalized head/tail.",
    ),
)
general(
    "data_structures",
    "senior",
    "durable_dedup",
    "Process a large iterator of event IDs, keeping only the first occurrence of each ID.",
    "Preserve first-seen order without loading the entire input; explain time and memory costs.",
    "IDs may repeat far apart. A probabilistic filter must not silently discard a new ID.",
    "Consider how your choice changes if the distinct IDs no longer fit in memory.",
    "Choose an exact deduplication approach and justify its memory trade-off.",
    (
        "A seen-ID hash set with streaming output.",
        "Ordered dictionary or equivalent exact membership structure.",
    ),
)
general(
    "data_structures",
    "senior",
    "inflight_cache_publication",
    "A bounded cache supports GET, PUT and DELETE while per-key loads complete asynchronously.",
    "A load started before a newer PUT or DELETE must never overwrite it or resurrect deleted data.",
    "Keys may be evicted and reinserted while old loads run; metadata and in-flight work must remain bounded.",
    "Cancellation is advisory: a canceled loader may still complete.",
    "Design publication identity, eviction and load ownership with a failing interleaving.",
    (
        "Generation tokens and conditional publication under a per-key guard.",
        "Unique load ownership handles with compare-and-swap publication.",
    ),
)
general(
    "algorithms",
    "entry",
    "peak_overlap",
    "Input is unsorted half-open integer intervals [start,end), start<=end; duplicates represent different bookings.",
    "Return the maximum simultaneous bookings and the earliest time it occurs, without scanning every time unit.",
    "Ignore empty intervals; end and start at the same time do not overlap. Empty input returns (0,none).",
    "Negative timestamps are valid and intervals may nest.",
    "Build an efficient sweep and justify tie handling using an example.",
    (
        "Grouped endpoint deltas in sorted time order.",
        "Sorted starts/ends with end-before-start processing.",
    ),
)
general(
    "algorithms",
    "entry",
    "covered_event_count",
    "Events have sorted integer timestamps; duplicates are distinct events. Unsorted half-open windows may overlap or nest.",
    "Count events covered by any window once per event, avoiding a full event rescan for each window.",
    "A timestamp at a window's end is excluded; empty windows cover nothing; an empty event list returns zero.",
    "Many windows can be identical; memory need not depend on the timestamp range.",
    "Design the algorithm and its cost under duplicate and overlapping boundaries.",
    (
        "Merge windows then scan event positions.",
        "Merge windows then binary-search event bounds.",
    ),
)
general(
    "algorithms",
    "entry",
    "earliest_free_slot",
    "Given open<close, k>0 and unsorted busy half-open intervals, find a free slot of exactly length k inside [open,close).",
    "Return the earliest [s,s+k), or none, without scanning every time unit; clip busy intervals to opening hours.",
    "Busy intervals can nest or touch; touching busy intervals leave no gap. A free slot may end exactly at a busy start or close.",
    "Ignore zero-length and fully out-of-hours busy intervals.",
    "Find the earliest slot efficiently and justify its boundary conditions.",
    (
        "Sort/merge clipped intervals then inspect gaps.",
        "Sweep endpoints while tracking free-gap start.",
    ),
)
general(
    "algorithms",
    "senior",
    "burst_range_index",
    "An append-only store acknowledges unique-key inserts; exact ordered range scans must include all inserts acknowledged before scan start.",
    "Millions of rows exceed RAM; disk is available and rebuilds run concurrently with inserts. Define scan visibility for later inserts.",
    "A crash during rebuilding must not lose acknowledged rows or expose duplicate keys; account for read/write amplification.",
    "Bursts can exceed the in-memory buffer, so backpressure and durable acknowledgment boundaries must be explicit.",
    "Choose an index/rebuild strategy and show how a scan and interrupted rebuild remain correct.",
    (
        "Durable ordered index with copy-on-write rebuild generations.",
        "Logged sorted runs with a bounded memtable and merged snapshot scans.",
    ),
)
general(
    "algorithms",
    "senior",
    "external_exact_topk",
    "A finite file of event IDs exceeds RAM; distinct IDs also exceed RAM. Disk spill and multiple passes are allowed.",
    "Return exact top K IDs by frequency, breaking equal counts by ascending ID, using bounded RAM.",
    "Heavy skew can overflow one partition; include external I/O and a correctness argument, not only an in-memory heap.",
    "No approximate sketch may drop a possible winner.",
    "Design an external aggregation/selection algorithm handling skew and deterministic ties.",
    (
        "External sort, streaming group counts and bounded selection.",
        "Recursive disk partitioning with exact per-partition counts and global merge.",
    ),
)
oop(
    "entry",
    "validated_import",
    "CSV and JSON imports share exactly the same row-validation rules.",
    "Read, validate and then publish all rows, or report errors. Dry-run reports the same errors and never writes.",
    "A parse or validation failure exposes no partial dataset; adding a reader must not bypass validation.",
    None,
    "Readers can stream, but all-or-none publication still applies.",
    "Design responsibility boundaries and publication ownership, not just name a pattern.",
    (
        "Reader strategies and a shared validation/publication coordinator.",
        "Typed parsed batches followed by pure validation and a transactional sink.",
    ),
)
oop(
    "entry",
    "staged_writer",
    "Readers see the old complete document or the new complete document, never a prefix.",
    "A caller writes a report privately, then publishes it with an available atomic replacement.",
    "If writing fails, the previous report stays readable and the incomplete report stays private.",
    None,
    "Keep cancellation or cleanup ownership clear if the caller stops the export.",
    "Separate writing from publication so a failed export cannot expose a partial report.",
    (
        "Owned staging handle with explicit atomic commit.",
        "Immutable document builder and a separate publication capability.",
    ),
)
oop(
    "entry",
    "listener_snapshot",
    "Each dispatch uses its start-of-call listener snapshot; a nested dispatch uses current registrations.",
    "Listeners can add/remove listeners or dispatch recursively. Continue the outer snapshot even when a callback raises.",
    "Collect callback errors after delivery; do not skip outer listeners or corrupt later dispatches.",
    None,
    "Removing then re-adding a listener affects nested calls but not the captured outer snapshot.",
    "Design per-dispatch state and exception-safe reentrancy.",
    (
        "Immutable per-dispatch snapshots and deferred error collection.",
        "Copy-on-write registry versions captured by each dispatch.",
    ),
)
oop(
    "senior",
    "bounded_reader_rollback",
    "A parser can inspect up to 64 KiB, commit consumed bytes, or roll back within that retained prefix.",
    "Backends are seekable files and non-seekable streams. Partial headers may be retried; cancellation must release owned resources.",
    "A partial read must not lose or double-consume bytes. Exceeding retained lookahead returns an explicit limit error.",
    "Rewinding a non-seekable stream beyond the retained prefix.",
    "The parser borrows a reader; only the owner may close the underlying stream.",
    "Design capability boundaries, buffering and caller recovery under cancellation.",
    (
        "Bounded buffering adapter with checkpoint/commit operations.",
        "Explicit parser-owned prefix buffer with capability-specific source readers.",
    ),
)
oop(
    "senior",
    "plugin_cleanup",
    "A plugin transforms input using temporary files; only a completed result is published.",
    "A caller runs plugins in sequence and owns their intermediate files.",
    "If a plugin fails, release its temporary files and keep the previous result readable.",
    None,
    "Cleanup can itself fail; preserve the original error while reporting the cleanup problem.",
    "Design a small plugin interface with clear ownership and failure cleanup.",
    (
        "A coordinator with explicit cleanup in a finally block.",
        "Context-managed plugin resources and a separate publisher.",
    ),
)


def sql(
    profile,
    name,
    tables,
    outputs,
    eligibility,
    missing,
    joins,
    ranking,
    extension,
    goal,
    approaches,
):
    refs = [dict(table=t[0], column=t[2][0]) for t in tables]
    contract = dict(
        kind="sql",
        tables=[dict(name=n, columns=c, primary_key=p) for n, c, p in tables],
        row_identity=refs[0],
        references=refs,
        outputs=[
            dict(name=n, sources=[dict(table=t, column=c) for t, c in src], meaning=m)
            for n, src, m in outputs
        ],
        ranking=ranking,
        eligibility_and_time_scope=eligibility,
        missing_rows_and_nulls=missing,
        join_and_aggregation_rule=joins,
    )
    FAMILIES.append(
        ProblemFamily(
            name,
            "sql",
            profile,
            contract,
            ("missing_rows_and_nulls", extension),
            goal,
            approaches,
        )
    )


sql(
    "entry",
    "independent_aggregates",
    [
        ("users", ["id"], ["id"]),
        ("posts", ["id", "user_id"], ["id"]),
        ("likes", ["id", "user_id"], ["id"]),
    ],
    [
        ("user_id", [("users", "id")], "users.id"),
        ("posts", [("posts", "id")], "post count"),
        ("likes", [("likes", "id")], "like-record count"),
    ],
    "All rows are in scope; foreign keys user_id reference users.id.",
    "Include every user; each absent child count is zero.",
    "Counts are independent: two posts and three likes must produce 2 and 3, not 6.",
    None,
    "Multiple like rows by the same user count separately.",
    "Write a query avoiding one-to-many join multiplication.",
    (
        "Preaggregate each child and left join.",
        "Correlated aggregates or distinct child-key counts.",
    ),
)
sql(
    "entry",
    "latest_eligible_identity",
    [("users", ["id"], ["id"]), ("edits", ["id", "user_id", "at", "approved"], ["id"])],
    [
        ("user_id", [("users", "id")], "users.id"),
        ("edit_id", [("edits", "id")], "selected edit ID"),
    ],
    "edits.user_id references users.id. Only approved=true with non-NULL at is eligible; no time cutoff.",
    "Include every user; no eligible edit gives NULL edit_id, even when ineligible edits exist.",
    "Return at most one selected edit for each user, preserving users without edits.",
    dict(
        order_by=[dict(table="edits", column="at"), dict(table="edits", column="id")],
        selected_row_identity=dict(table="edits", column="id"),
        output_name="edit_id",
    ),
    "NULL approved is ineligible.",
    "Write a latest-eligible selection without losing unmatched parents.",
    (
        "Window rank before a left join.",
        "Lateral or correlated ordered top-one selection.",
    ),
)
sql(
    "entry",
    "owned_shared_union",
    [
        ("users", ["id"], ["id"]),
        ("docs", ["id", "owner_id"], ["id"]),
        ("shares", ["id", "user_id", "doc_id", "active"], ["id"]),
    ],
    [
        ("user_id", [("users", "id")], "users.id"),
        (
            "visible",
            [("docs", "id"), ("shares", "doc_id")],
            "distinct visible document count",
        ),
    ],
    "owner_id and user_id reference users.id; shares.doc_id references docs.id; only active=true shares qualify.",
    "Include zero-count users. NULL active is ineligible; ownership always grants visibility.",
    "A document owned and shared to the same user counts once; duplicate shares never inflate the count.",
    None,
    "An inactive share does not remove ownership visibility.",
    "Combine two access paths without double counting or losing zero users.",
    (
        "Union user/document pairs then aggregate and left join users.",
        "Correlated union with distinct document identity.",
    ),
)
sql(
    "senior",
    "snapshot_aggregates",
    [
        ("accounts", ["id"], ["id"]),
        ("events", ["id", "account_id", "at", "eligible", "amount"], ["id"]),
    ],
    [
        ("account_id", [("accounts", "id")], "accounts.id"),
        ("event_id", [("events", "id")], "selected event ID"),
        ("count", [("events", "id")], "eligible event count"),
        ("sum", [("events", "amount")], "eligible non-NULL amount sum"),
    ],
    "One statement snapshot; scope is UTC [2026-01-01,2026-02-01). eligible=true and non-NULL at; account_id references accounts.id.",
    "Include all accounts; no eligible event gives NULL event_id, count 0 and sum 0; all-NULL amounts sum to 0.",
    "Latest identity and aggregates use the same scoped rows; ranking must not reduce the aggregate to one row.",
    dict(
        order_by=[dict(table="events", column="at"), dict(table="events", column="id")],
        selected_row_identity=dict(table="events", column="id"),
        output_name="event_id",
    ),
    "NULL eligible is ineligible.",
    "Build snapshot-consistent selection plus independent aggregate without multiplication.",
    (
        "Scoped CTE with separate rank and aggregation.",
        "Lateral ordered selection plus a matching scoped aggregate.",
    ),
)
# Transaction questions still declare every referenced table and result identity.
sql(
    "senior",
    "reservation_outbox",
    [
        ("requests", ["id", "body_hash", "status"], ["id"]),
        ("stock", ["sku", "qty"], ["sku"]),
        ("lines", ["id", "request_id", "sku", "qty"], ["id"]),
        ("outbox", ["id", "request_id"], ["id"]),
    ],
    [
        ("request_id", [("requests", "id")], "requests.id"),
        ("status", [("requests", "status")], "committed reservation outcome"),
    ],
    "Caller supplies a unique request ID and positive item quantities. lines.request_id/outbox.request_id reference requests.id; lines.sku references stock.sku.",
    "Missing SKU or insufficient stock rejects all items. Reusing an ID with a changed body conflicts.",
    "Commit decrements, request and one outbox row together; no remote call. Same ID/body returns the committed outcome; rollback leaves no claim or reservation.",
    None,
    "Concurrent requests can deadlock; rollback and retry the entire transaction.",
    "Implement all-or-none reservations, retry identity and recoverable confirmation work.",
    (
        "Ordered row locking with unique request/outbox guards.",
        "Serializable transactions with whole-transaction retry and durable identity.",
    ),
)


def http(
    profile,
    name,
    mutation,
    effects,
    identity,
    outcome,
    boundary,
    extension,
    goal,
    approaches,
):
    FAMILIES.append(
        ProblemFamily(
            name,
            "http",
            profile,
            dict(
                kind="http",
                mutation=mutation,
                side_effects=[effects],
                retry_identity=identity,
                identity_scope="Identity is principal-scoped and bound to a canonical body hash.",
                same_key_different_body="Reusing an identity with different content conflicts.",
                concurrent_or_lost_response_outcome=outcome,
                guarantee_boundary=boundary,
            ),
            ("guarantee_boundary", extension),
            goal,
            approaches,
        )
    )


for profile in ["entry", "senior"]:
    http(
        profile,
        "idempotent_create",
        "POST /jobs creates a durable job and retry record in one DB transaction.",
        "One job; no external call inside this request.",
        "The client supplies a retry key; keep its committed outcome for this exercise.",
        "Racing identical calls and lost-response retries return the same committed job ID.",
        "This guarantees one database job, not exactly-once external delivery.",
        "A crash can occur after commit but before returning the job ID.",
        "Implement a retry-safe create request with one recoverable job ID.",
        (
            "Unique identity claim, job creation and stored response in one transaction.",
            "Unique principal/key job identity plus transactional body-hash comparison.",
        ),
    )
    http(
        profile,
        "versioned_retry",
        "PUT replaces a document using its expected version and client operation ID.",
        "Replace content and increment version once.",
        "The client supplies an operation ID; keep committed outcomes for this exercise.",
        "Committed retries return the recorded outcome, even after a newer write or lost response.",
        "For unseen operations, stale versions conflict; retry lookup and update must share one DB transaction.",
        "Racing identical operations must converge without reverting a newer replacement.",
        "Design the order and atomic boundary of retry lookup versus optimistic update.",
        (
            "Transactionally stored operation outcome with version compare-and-swap.",
            "Locked document version plus a unique operation log in the same transaction.",
        ),
    )

general(
    "rest_apis",
    "entry",
    "live_cursor",
    "Rows have immutable unique (created_at,id). Page 1 fixes a creation watermark; later inserts may have older created_at but a larger monotonic ingest_id.",
    "Use a signed cursor carrying the last returned ordering pair and maximum ingest_id from page 1; return descending order without duplicates.",
    "Rows can be deleted, including the cursor row. The API is live: deletions may disappear, not a historical snapshot.",
    "Equal created_at values must not skip rows; the cursor must not require its row to still exist.",
    "Design cursor predicates and the insertion/deletion contract.",
    (
        "Keyset ordering with an ingestion fence.",
        "Equivalent compound-key range scan under a retained insertion fence.",
    ),
)
general(
    "rest_apis",
    "entry",
    "field_patch_merge",
    "A document has title, summary and monotonically increasing version. PATCH carries base values for changed fields and an operation ID.",
    "Merge disjoint edits but reject any changed field whose current value differs from its base; record each operation outcome once.",
    "Conflict checks plus updates are atomic; response loss must not reapply a previously successful patch.",
    "Even if a field returns to its old value, operation identity must prevent duplicate application.",
    "Implement atomic field-level merge and replay recovery without overwriting a concurrent edit.",
    (
        "Row lock with base-value checks and operation ledger.",
        "Conditional multi-field update with transactional operation identity.",
    ),
)
general(
    "rest_apis",
    "senior",
    "snapshot_cursor",
    "GET /activities lists rows newest first by immutable created_at and unique id; inserts can arrive between pages.",
    "Choose pagination that avoids returning an item twice, and explain whether new rows appear during the traversal.",
    "Timestamps can tie and the cursor row can be deleted. This is a live list, not a historical snapshot.",
    "Explain when offset pagination would be acceptable instead.",
    "Choose and implement pagination for a changing list, explaining the practical trade-off.",
    (
        "A keyset cursor using a compound ordering comparison.",
        "Equivalent seek predicates using time and ID as explicit range conditions.",
    ),
)
general(
    "rest_apis",
    "senior",
    "sync_retention",
    "A change feed has monotonic sequence IDs and deletion tombstones, retained for seven days. Updates and feed entries commit atomically.",
    "Paginated sync returns every committed change after a client's cursor, allowing duplicates that clients deduplicate by sequence ID.",
    "An expired cursor returns an explicit full-resync-required response, not an incomplete change page.",
    "Deletion tombstones older than retention must not silently strand a stale client.",
    "Design a practical incremental-sync endpoint and its expired-cursor behavior.",
    (
        "Consistent snapshot plus feed high-water mark with retained catch-up.",
        "Versioned snapshot generation and sequence-based incremental handoff.",
    ),
)
general(
    "git",
    "entry",
    "dependent_revert",
    "Shared commits A,B,C are consecutive: A adds parseAmount accepting a trailing minus by mistake; B uses it for valid decimal prices; C fixes a typo.",
    "Remove trailing-minus acceptance while preserving B's valid-price feature, C and published history.",
    "Reverting A removes the helper B calls; tests must cover valid decimals and rejection of the faulty syntax.",
    "Other developers have already based work on C; rewriting their ancestry is not allowed.",
    "Choose and justify a dependency-aware recovery patch and verification sequence.",
    (
        "Forward fix for the faulty parser behavior.",
        "Revert plus a replacement compatibility helper preserving the public contract.",
    ),
)
general(
    "git",
    "entry",
    "merge_recovery",
    "Shared merge M adds a search feature and disables validation. Later commit D fixes search pagination and depends on the feature API.",
    "Restore validation without removing the search feature or D, preserving shared history.",
    "Blindly reverting M removes APIs D requires; inspect merge parents and test both validation and pagination.",
    "The fix must be safe to merge into a branch that already contains D.",
    "Plan a minimal recovery commit and prove retained versus removed behavior.",
    (
        "Targeted forward patch restoring validation.",
        "Selective inverse patch with compatibility-preserving reconciliation.",
    ),
)
general(
    "git",
    "senior",
    "migration_recovery",
    "A shared release changed CSV dates from YYYY-MM-DD to DD/MM/YYYY, breaking existing consumers. A later commit fixes a security bug.",
    "Restore the original CSV date format while keeping the security fix and published history.",
    "Reverting the whole release also removes the security fix; test the CSV output expected by existing consumers.",
    "Another team has already based a release branch on these commits.",
    "Choose and verify a safe compatibility fix without losing unrelated changes.",
    (
        "Patch the date formatter forward and retain the security change.",
        "Selectively invert the date-format change with regression tests.",
    ),
)
general(
    "git",
    "senior",
    "security_revert_chain",
    "A feature merge M contained a security fix S. Revert R removed M and S. A later branch reintroduces the feature via commits descended from M.",
    "Restore the feature and S without resurrecting a known feature regression; preserve shared history.",
    "Merging the old branch alone may consider reverted commits already merged; inspect ancestry and merge parents.",
    "A targeted test must fail when S is absent and another must expose the old feature regression.",
    "Plan explicit reconciliation commits and explain which changes each restores or excludes.",
    (
        "Revert the revert then fix the regression before release.",
        "Explicitly reapply reviewed feature/security changes with ancestry-aware reconciliation.",
    ),
)
general(
    "testing",
    "entry",
    "stale_expiry",
    "PUT creates a new cache generation expiring at its write time plus 60; old timer callbacks can fire after refresh.",
    "At age >=60 the current generation is absent. An earlier generation's callback must not delete a newer unexpired value.",
    "Use a fake monotonic clock and controlled callback delivery, no sleeps; reads observe expiry even if callback delivery is late.",
    "Deliver a canceled old callback after refresh, then advance exactly to the new expiry.",
    "Build a deterministic test oracle that distinguishes stale deletion from late timer delivery.",
    (
        "Fake clock plus separately queued generation-tagged callbacks.",
        "Manual scheduler with parameterized interleaving traces.",
    ),
)
general(
    "testing",
    "entry",
    "out_of_order_response",
    "Search requests A then B can finish in either order; cancellation is advisory and canceled A may still return.",
    "Only the latest query B may update visible results; a B failure leaves a B-specific error and must not reveal stale A results.",
    "Control each response with deferred completions, no sleeps or real network; include completion after component unmount.",
    "Complete B before A, and separately fail B before A succeeds.",
    "Design deterministic tests and assertions for visible state across those schedules.",
    (
        "Deferred promises and explicit lifecycle steps.",
        "Controllable request fake with event-driven state assertions.",
    ),
)
general(
    "testing",
    "senior",
    "crash_outbox_oracle",
    "An endpoint writes an order in a DB transaction and queues confirmation only after commit.",
    "Test success and DB rollback so only committed orders can queue confirmation.",
    "Use a test database or controlled transaction fake and a fake queue; assert observable state and call ordering.",
    "Consider what happens if queuing fails after the order commit.",
    "Design practical integration tests for transaction success, rollback and post-commit work.",
    (
        "Integration tests with a real test transaction and a queue fake.",
        "A controlled transaction fake exercising commit and rollback hooks.",
    ),
)
general(
    "testing",
    "senior",
    "generation_swap_oracle",
    "A search cache replaces its visible results only after a refresh succeeds.",
    "Test that successful refreshes replace the result list and failed refreshes keep the last successful list.",
    "Use controlled responses and observable result assertions, not real network requests or sleeps.",
    "A refresh can return an empty successful result, which must replace the old list.",
    "Design practical tests for successful and failed cache refresh behavior.",
    (
        "A controllable refresh fake and explicit state assertions.",
        "Table-driven tests for successful, failed and empty refreshes.",
    ),
)


def debugging(profile, name, observations, extra):
    # An ordinary symptom does not require two predefined competing hypotheses.
    # Keep the specialized DebuggingContract validator for questions that do
    # explicitly claim distinct causes/predictions; use the existing simple
    # input/output/boundary contract for an opening investigation question.
    general(
        "debugging",
        profile,
        name,
        observations,
        "Choose a focused first check and explain what its result would tell you.",
        "Use evidence rather than assuming the cause; do not change several things at once.",
        extra,
        "Investigate this symptom and explain how you would narrow the cause.",
        (
            "Inspect a focused trace and reproduce the symptom.",
            "Use a controlled input to isolate the affected code path.",
        ),
    )


debugging(
    "entry",
    "cache_vs_shared_state",
    "An API occasionally returns another request's data when requests overlap; each isolated response is correct.",
    "You can add request IDs and control whether two requests overlap.",
)
debugging(
    "entry",
    "listener_vs_upstream",
    "A component receives duplicate event notifications after it is unmounted and mounted again.",
    "You can inspect registered listeners and inject one tagged event.",
)
debugging(
    "senior",
    "pool_lease_hypotheses",
    "API latency rises while query time stays flat; traces show waiting for a DB connection and a persistently full pool.",
    "You can trace connection acquisition/release and compare request lifetimes.",
)
debugging(
    "senior",
    "cache_refresh_hypotheses",
    "Requests become slow just after cache expiry, but normal cached requests are fast.",
    "You can measure cache wait time and upstream call duration separately.",
)


def security(
    profile,
    name,
    principal,
    resource,
    action,
    transition,
    boundary,
    freshness,
    extra,
    goal,
):
    FAMILIES.append(
        ProblemFamily(
            name,
            "security",
            profile,
            dict(
                kind="security",
                tested_permission=dict(
                    principal=principal,
                    resource=resource,
                    action=action,
                    before="allowed",
                    after="denied",
                    transition=transition,
                ),
                enforcement_boundary=boundary,
                freshness_rule=freshness,
            ),
            ("freshness_rule", extra),
            goal,
            (
                "Transactional policy/version enforcement with the protected operation.",
                "Guarded operation ownership and current-principal authorization at publication.",
            ),
        )
    )


security(
    "entry",
    "authorization_transition",
    "editor",
    "note",
    "write",
    "The editor's grant is revoked; the owner retains access.",
    "Check authorization on the server; a login token may contain an old role.",
    "Writes started after revocation must fail for the editor, while the owner retains write access.",
    "Consider an edit already in flight when permission changes.",
    "Implement and test the authorization decision using current permissions.",
)
security(
    "senior",
    "revoked_export_principal",
    "tenant_user",
    "export",
    "download",
    "The user's tenant grant is revoked during an export.",
    "A background export runs with service credentials, but its result is private until publication.",
    "Recheck the original requester before publishing or downloading; service credentials must not replace user authorization.",
    "If permission lookup fails, do not publish a result to that requester.",
    "Choose where to enforce requester permissions for an asynchronous export.",
)

# Measured exhaustion: a genuinely different security competency, not another
# rephrasing of the same authorization-revocation predicate.
for profile in ["entry", "senior"]:
    FAMILIES.append(
        ProblemFamily(
            "single_use_reset",
            "security",
            profile,
            dict(
                kind="security_boundary",
                assets="A user's password can change only through a valid password-reset token.",
                untrusted_inputs="Tokens arrive in concurrent requests; store only a token digest, user binding and expiry, never the raw high-entropy token.",
                safety_invariant="Token validation/consumption and password update share one DB transaction; one token permits at most one successful change.",
                allowed_behavior="The token expires after 15 minutes; invalid, expired or reused tokens change nothing.",
                failure_case="Two valid-token requests race, or the response is lost after commit; never apply a second password change.",
            ),
            (
                "failure_case",
                (
                    "Issuing a new token invalidates earlier tokens atomically, even if old redemption is in flight."
                    if profile == "senior"
                    else "A crash before commit must leave both the password and token unchanged."
                ),
            ),
            "Design secure token storage and atomic one-time redemption"
            + (
                " including concurrent reissue/redeem ordering."
                if profile == "senior"
                else "."
            ),
            (
                "Guarded token-row transaction with password update.",
                "Conditional token consumption and password mutation in one transaction.",
            ),
        )
    )


def reviewed_families(role: str, topic: str, level: str) -> list[ProblemFamily]:
    role_info = resolve_role(role)
    if not role_info or role_info["id"] != "software_engineer":
        return []
    profile = "entry" if level in {"internship", "fresher"} else "senior"
    return [
        f
        for f in FAMILIES
        if f.topic == covered_topic_key(topic) and f.profile == profile
    ]


def select_reviewed_family(
    role, topic, level, index, asked_fingerprints, previous_questions=None
):
    families = reviewed_families(role, topic, level)
    if not families:
        return None
    # Older sessions may contain curated text but predate private family markers.
    # Recognize known reviewed coverage rather than offering its AI paraphrase.
    from app.modules.interview.hard_fallbacks import hard_fallback_records
    from app.modules.interview.deduplication import is_duplicate_or_paraphrase

    covered = set(asked_fingerprints or [])
    for text, marker in hard_fallback_records(topic, level):
        if is_duplicate_or_paraphrase(text, topic, previous_questions or [])[0]:
            covered.add(marker)
    start = (max(1, index) - 1) % len(families)
    for offset in range(len(families)):
        family = families[(start + offset) % len(families)]
        marker = family_marker(family.topic, level, family.id)
        if marker not in covered:
            return family, marker
    raise QuestionGenerationUnavailable(topic, "hard", reason="coverage_exhausted")
