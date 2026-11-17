---
knowledge_id: swe.testing
schema_version: 1
revision: 3
status: active
roles: ml_engineer,ai_engineer,python_developer,software_engineer,frontend_developer,backend_developer,full_stack_developer,qa_engineer
skill: testing
topic: testing
subtopic: testing
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://docs.pytest.org/en/stable/how-to/fixtures.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Behavioral tests and isolated dependencies

## Definition
Tests exercise observable behavior under explicit conditions. A good test fails for a meaningful regression and has a clear source of truth for its expected result.

## Core principles
Use fixtures for controlled setup and teardown. Isolate time, network and external dependencies when verifying local behavior. Add integration coverage at real boundaries instead of assuming mocks prove compatibility. Include failure and boundary cases.

## Practical applications
Test a checkout operation with a fake gateway and separately validate the gateway integration contract.

## Common misconceptions
A high coverage percentage does not prove correct assertions. A test that repeats the implementation can preserve the same bug. Mock success does not prove that a real service behaves like the mock.

## Engineering scenario
A checkout test suite intermittently fails because shared fixture state is mutated and never reset. Create isolated fixtures, control time explicitly, and verify cleanup even when an assertion or setup step fails.

## Trade-offs and limitations
Unit tests are fast and precise but miss boundary incompatibilities. Integration tests add realism and maintenance cost. Use a small number of end-to-end journeys for critical workflows rather than making every assertion browser-dependent.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://docs.pytest.org/en/stable/how-to/fixtures.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://docs.pytest.org/en/stable/how-to/monkeypatch.html ; https://www.postgresql.org/docs/16/transaction-iso.html.

## Easy
Question: What is a test fixture and why should tests be isolated?
Expected concepts: controlled setup; teardown; reproducibility.
Follow-up: What shared mutable state can leak between tests?


## Medium
Question: How would you test timeout recovery without a live payment service?
Expected concepts: fake failure; deterministic clock; observable retry behavior; separate contract test.
Follow-up: How will you detect a drifted mock contract?


## Hard
Question: A message worker writes a result to a database and acknowledges queue delivery separately. A crash after the commit but before acknowledgment triggers redelivery; crashing earlier must not lose work. Design deterministic tests that exercise both boundaries and verify externally visible results after restart.
Expected concepts: Use explicit barriers/fault hooks instead of sleeps, a real transaction-capable integration database at the consistency boundary and a controllable queue fake for delivery schedules. Inject failures before commit, after commit/before acknowledgment and after acknowledgment. Assert durable work, idempotent externally visible effects and recoverable state, not just method-call counts. Unit mocks alone cannot prove transaction semantics. A separate external notification requires a durable outbox plus consumer idempotency/reconciliation, not a single atomic DB-and-queue commit assumption. Include cancellation and concurrent redelivery schedules.
Follow-up: Which guarantees are not established by a deterministic integration test and still need production observability?
