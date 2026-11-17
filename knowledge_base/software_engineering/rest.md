---
knowledge_id: swe.rest
schema_version: 1
revision: 3
status: active
roles: ai_engineer,software_engineer,frontend_developer,backend_developer,full_stack_developer
skill: rest apis
topic: rest_apis
subtopic: rest
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://www.rfc-editor.org/rfc/rfc9110.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Resource-oriented APIs and evolution

## Definition
A resource-oriented API exposes domain resources through representations and documented operations. HTTP semantics inform API design but do not by themselves establish every REST architectural constraint.

## Core principles
Choose stable resource identities and apply authorization per operation. Validate input and distinguish client errors from server failures. Define pagination order and behavior under concurrent changes. Use conditional requests when concurrent edits must not overwrite one another silently.

## Practical applications
Expose orders and order status to a web client with predictable pagination and edit conflicts.

## Common misconceptions
Using JSON or nouns in URLs does not automatically make an API REST-compliant. Status codes are not a substitute for useful error contracts. Resource identifiers are not permissions.

## Engineering scenario
Two support agents edit the same ticket. Return a representation validator and require an appropriate conditional update so a stale edit produces a documented conflict rather than overwriting another agent.

## Trade-offs and limitations
Offset pagination is simple but can skip or repeat records during mutation; cursor designs require a stable ordering and contract. Compatibility, caching and authorization constraints affect endpoint evolution.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://www.rfc-editor.org/rfc/rfc9110.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://www.postgresql.org/docs/16/transaction-iso.html ; https://www.rfc-editor.org/rfc/rfc9110.html.

## Easy
Question: How would you represent retrieving an order and distinguish a missing resource?
Expected concepts: resource identity; GET semantics; documented status and error body.
Follow-up: How should authorization affect which data is returned?


## Medium
Question: How would you prevent lost updates when two clients edit a ticket?
Expected concepts: validator; conditional request; conflict recovery.
Follow-up: Which changes should require a new representation validator?


## Hard
Question: An activity endpoint must enumerate a stable snapshot as of page one, ordered by (created_at, id), while records are inserted and deleted. The cursor expires in ten minutes and storing a full result per client is too costly. Design a pagination contract and storage strategy that can actually meet it.
Expected concepts: A timestamp/id keyset gives deterministic traversal but does not preserve deleted records or mutable ordering. A creation watermark alone excludes new inserts but cannot recreate deleted snapshot rows. True snapshot paging needs retained versions/as-of queries or an explicitly bounded snapshot mechanism; otherwise negotiate a weaker live-feed contract and describe omissions. Bind opaque cursors to filters, principal, ordering, snapshot/version and expiry, protect them against tampering, and recheck current authorization. Avoid a long-lived database transaction per anonymous client without accounting for resources.
Follow-up: How should the endpoint respond when the snapshot expires before the next page?
