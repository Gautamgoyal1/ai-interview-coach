---
knowledge_id: swe.sql
schema_version: 1
revision: 3
status: active
roles: ml_engineer,data_scientist,python_developer,software_engineer,backend_developer,full_stack_developer,data_analyst,qa_engineer
skill: sql
topic: sql
subtopic: sql
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://www.postgresql.org/docs/16/transaction-iso.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# SQL joins, transactions and concurrent updates

## Definition
SQL queries express relational operations; transactions group database changes under consistency and isolation rules. Join cardinality and concurrent execution both affect correctness.

## Core principles
A LEFT JOIN preserves unmatched left rows with null right-side values. A right-table condition in WHERE may remove those rows. In PostgreSQL Read Committed, separate statements can observe different committed snapshots. Atomic conditional updates can enforce constraints without an application read-then-write race.

## Practical applications
List customers with no orders and reserve limited inventory without overselling.

## Common misconceptions
A transaction is not automatically serializable. COUNT(column) excludes null values; COUNT(*) counts joined rows. An index can improve a plan but adds write/storage cost and is not always chosen.

## Engineering scenario
Two checkouts read stock=1 and both proceed. Replace separate application read/decrement logic with a conditional UPDATE that requires stock>0 and check the affected-row count; consider multi-item ordering, rollback and retry behavior.

## Trade-offs and limitations
Stronger isolation can require retries. Locks improve coordination but can block or deadlock. Index choice depends on predicates, selectivity and actual execution plans; no one index makes every query fast.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting reviewed against PostgreSQL 16 primary documentation on 2026-11-15. References by claim:
- Join row preservation and ON versus WHERE filtering: https://www.postgresql.org/docs/16/queries-table-expressions.html
- Read Committed snapshots, concurrent updates and serializable retries: https://www.postgresql.org/docs/16/transaction-iso.html
- Conditional UPDATE and affected-row counts: https://www.postgresql.org/docs/16/sql-update.html
- COUNT(*) versus COUNT(expression) null behavior: https://www.postgresql.org/docs/16/functions-aggregate.html
- Index access methods and supported predicates: https://www.postgresql.org/docs/16/indexes-types.html
- Single-quoted SQL string constants: https://www.postgresql.org/docs/16/sql-syntax-lexical.html#SQL-SYNTAX-CONSTANTS
No proprietary question bank or third-party prose is imported. CC-BY-4.0 covers these original notes only, not the linked PostgreSQL documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://www.postgresql.org/docs/16/explicit-locking.html.

## Easy
Question: How does LEFT JOIN differ from INNER JOIN?
Expected concepts: row preservation; unmatched nulls; multiplicity.
Follow-up: What happens to unmatched rows after WHERE orders.status = 'paid'?


## Medium
Question: How do you stop two requests from selling the last inventory item?
Expected concepts: atomic conditional update; affected rows; transaction boundary.
Follow-up: What if the checkout reserves several items?


## Hard
Question: A reservation must acquire all requested seats or none. Transactions request overlapping seat sets in different orders, retries may occur after deadlocks or serialization failures, and a worker sends confirmations only for committed reservations. Design the transaction and retry boundary under contention.
Expected concepts: Lock seat rows in a consistent order or use atomic conditional writes, check every requested seat and roll back the whole reservation on failure. Serializable isolation can detect anomalies but requires retrying the entire transaction from a fresh snapshot; Read Committed row locking can suffice for explicitly protected invariants. Retry deadlock/serialization failures with bounded backoff, not arbitrary integrity errors. Insert an outbox record with the reservation in the same transaction; delivery still needs deduplication and must not be advertised as magical exactly-once messaging. Keep remote side effects outside retryable transaction bodies. Compare contention and abort rates.
Follow-up: What happens if the worker delivers a confirmation but crashes before marking its outbox row sent?
