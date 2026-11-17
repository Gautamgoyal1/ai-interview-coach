---
knowledge_id: swe.data_structures
schema_version: 1
revision: 2
status: active
roles: software_engineer,frontend_developer
skill: data structures
topic: data_structures
subtopic: data_structures
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://docs.python.org/3/tutorial/datastructures.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Data structures and stable deduplication

## Definition
A data structure organizes values around operations and invariants, not merely syntax. Choose based on lookup, ordering, mutation and memory needs.

## Core principles
A hash set supports membership without preserving a sequence contract. An ordered output list plus a seen-set can retain first occurrence. Hash-table operations are expected constant time under suitable hashing; collisions can make individual operations slower. A queue needs efficient operations at both ends.

## Practical applications
Deduplicate event identifiers while retaining arrival order in a batch import.

## Common misconceptions
A tuple is not automatically hashable: every contained element must also be hashable. A hash map does not promise constant-time worst-case operations.

## Engineering scenario
An import contains repeated customer IDs. Preserve the first record, report duplicates and test empty input and unhashable keys. Define identity and normalization before choosing a container.

## Trade-offs and limitations
A seen-set adds memory proportional to distinct identifiers. Sorting changes ordering unless additional information is retained. An unbounded stream needs bounded retention or durable deduplication, not an ever-growing in-memory set.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://docs.python.org/3/tutorial/datastructures.html . The license above covers these original notes, not the linked documentation.

## Easy
Question: When would a set be preferable to a list for membership checks?
Expected concepts: membership semantics; expected lookup cost; order requirements.
Follow-up: What changes if arrival order must be preserved?


## Medium
Question: How would you deduplicate customer records while preserving the first occurrence?
Expected concepts: identity key; output order; seen-set; memory cost; test cases.
Follow-up: What if two records share an ID but disagree on values?


## Hard
Question: Design deduplication for a stream larger than memory with a replay window.
Expected concepts: bounded state; durable identity; retention; recovery; duplicates after expiry.
Follow-up: Which guarantees disappear when the retention window expires?
