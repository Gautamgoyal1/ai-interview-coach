---
knowledge_id: swe.http
schema_version: 1
revision: 3
status: active
roles: software_engineer,frontend_developer,backend_developer,full_stack_developer,qa_engineer
skill: http
topic: http
subtopic: http
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://www.rfc-editor.org/rfc/rfc9110.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# HTTP method semantics and safe retries

## Definition
HTTP defines request/response semantics, including methods, representations and status codes. Method semantics describe intended effects, not the absence of every operational side effect.

## Core principles
Safe methods do not request state-changing behavior. Idempotent methods have the same intended effect when repeated, not necessarily the same status or response body. GET is safe; PUT and DELETE are idempotent by defined semantics. POST is not generally idempotent.

## Practical applications
Choose a retry policy for a client whose request timed out after the server may have committed.

## Common misconceptions
An idempotent DELETE may return a different status on the second call. A timeout does not prove the operation failed. Automatically retrying every POST can duplicate side effects.

## Engineering scenario
A payment client times out after submitting an order. Define an application idempotency key with durable outcome storage, request-payload validation and a documented expiration policy before enabling automatic retries.

## Trade-offs and limitations
Retries need bounded backoff, deadlines and observability. Idempotency storage adds coordination costs and does not by itself atomically coordinate unrelated external systems. Method semantics do not replace application authorization.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://www.rfc-editor.org/rfc/rfc9110.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://www.rfc-editor.org/rfc/rfc9110.html.

## Easy
Question: What does idempotent mean for DELETE?
Expected concepts: same intended effect; response may differ.
Follow-up: Does a logging side effect invalidate the definition?


## Medium
Question: What should a client do after an order POST times out?
Expected concepts: unknown outcome; idempotency key; lookup or reconciliation.
Follow-up: What if the same key arrives with a different payload?


## Hard
Question: A file-import POST can finish after a client timeout. Request keys and jobs live in one database; two concurrent retries can use the same key, and a mistaken client can reuse that key with a different body. Define the server retry contract and implementation when the response is lost after commit.
Expected concepts: Scope keys to the authenticated principal and operation; record a canonical request fingerprint, operation state and stable result. Atomically claim the key and create durable work, handling unique-key conflicts. Same key and different payload must be rejected under the documented contract; concurrent identical work must not create two jobs. Return a retrievable pending/completed outcome. HTTP method semantics or a custom header alone do not guarantee exactly-once side effects; downstream effects need their own idempotency/reconciliation. Define expiry and behavior after key retention ends.
Follow-up: How would you expose and recover a job stuck in a pending state after a worker crash?
