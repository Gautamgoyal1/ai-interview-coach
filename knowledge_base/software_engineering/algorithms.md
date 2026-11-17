---
knowledge_id: swe.algorithms
schema_version: 1
revision: 3
status: active
roles: software_engineer
skill: algorithms
topic: algorithms
subtopic: algorithms
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://docs.python.org/3/library/bisect.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Binary search invariants and total cost

## Definition
An algorithm is a finite procedure whose correctness follows from explicit preconditions and invariants. Complexity describes how resource use grows with input size.

## Core principles
Binary search repeatedly narrows a sorted search interval. Preserve a consistent half-open or closed interval and prove progress at every step. Boundary cases include an empty range, repeated values and a missing target. Separate comparison cost from data movement.

## Practical applications
Locate the first eligible timestamp in an ordered audit log.

## Common misconceptions
Logarithmic search does not imply logarithmic insertion into a contiguous array: shifting elements remains linear. Searching unsorted input violates the precondition.

## Engineering scenario
An endpoint looks up thresholds in a sorted array but sometimes loops forever with duplicate values. Trace low, high and mid through the smallest failing example and identify the invariant each assignment preserves.

## Trade-offs and limitations
Sorting once may pay off for repeated lookups but not a single query. Comparisons and key extraction may be expensive. A tree or database index offers different update, memory and locality trade-offs.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://docs.python.org/3/library/bisect.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://docs.python.org/3/library/bisect.html.

## Easy
Question: What precondition does binary search require?
Expected concepts: sorted order; consistent comparison; narrowing interval.
Follow-up: How would you return an insertion point for a missing value?


## Medium
Question: Debug a binary search that fails to progress when two elements remain.
Expected concepts: boundary convention; midpoint progress; invariant; empty and duplicate tests.
Follow-up: How do you find the first rather than any duplicate?


## Hard
Question: A search index holds ten million records ordered by (timestamp, id). Inserts arrive in one-minute bursts of 10,000 per second while range reads continue; acknowledged inserts must be visible immediately. Choose an indexing and merge strategy under a bounded memory budget, accounting for the number of results returned rather than only lookup cost.
Expected concepts: Compare a balanced search tree with O(log n + k) range traversal and O(log n) updates against a sorted array with O(log n + k) reads but O(n) arbitrary insertion. Cache locality and allocation matter. A sorted base plus searchable delta can amortize rebuilds but reads must merge both, resolve updates/deletions and synchronize publication. Balanced-tree bounds require actual balancing. State memory/latency assumptions; benchmark burst and steady-state workloads instead of promising one universal winner.
Follow-up: How would an interrupted rebuild avoid dropping inserts acknowledged during the rebuild?
