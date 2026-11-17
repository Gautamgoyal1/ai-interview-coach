---
knowledge_id: swe.debugging
schema_version: 1
revision: 3
status: active
roles: python_developer,software_engineer,frontend_developer,backend_developer,qa_engineer
skill: debugging
topic: debugging
subtopic: debugging
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://docs.python.org/3/library/pdb.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Hypothesis-driven debugging

## Definition
Debugging is the process of narrowing an observed failure to a falsifiable explanation and verifying a correction. A debugger can inspect frames and execution state; logs and traces cover behavior that cannot be reproduced interactively.

## Core principles
Record expected versus observed behavior and minimize the failing case. Change one explanatory variable at a time. Inspect state at a boundary where correct behavior diverges. Preserve a regression test after identifying the cause.

## Practical applications
Diagnose a failure that appears only when a cache is warm or two requests overlap.

## Common misconceptions
Adding a delay may hide a race without fixing it. The line that raises an exception may be downstream from the invariant violation. Production debugging must avoid exposing secrets or modifying live state casually.

## Engineering scenario
An API occasionally returns another request's intermediate result. Use request IDs and a controlled two-request test to investigate shared mutable state, rather than attributing the failure to random network behavior.

## Trade-offs and limitations
Instrumentation changes timing and may create overhead. A debugger can pause processes and is unsuitable for unrestricted use in production. Choose safe observability and bounded reproductions based on incident impact.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://docs.python.org/3/library/pdb.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://opentelemetry.io/docs/concepts/signals/traces/.

## Easy
Question: What information makes a bug report reproducible?
Expected concepts: inputs; environment; expected/actual behavior; minimal steps.
Follow-up: What should not be copied into logs?


## Medium
Question: How would you investigate intermittent cross-request state leakage?
Expected concepts: request correlation; shared state; controlled concurrency; regression test.
Follow-up: How could logging change the timing of the failure?


## Hard
Question: After a deployment, p99 latency triples but median latency, CPU and database execution time remain flat. Traces place the delay in connection acquisition; checked-out connections remain at the limit after requests finish. Discriminate leaked connections from legitimate long-held transactions using a bounded, safe investigation.
Expected concepts: Instrument acquisition wait separately from ownership duration and query time, correlate checkout/release with request/transaction IDs, inspect idle-in-transaction sessions, and compare release paths including cancellation and exceptions. A leak and a slow transaction can produce the same pool saturation. Use a bounded canary or controlled cancellation test and predicted observations to distinguish hypotheses. Raising the pool size can shift overload to the database and is mitigation, not proof of cause. Avoid logging secrets; verify recovery and absence of residual checked-out resources.
Follow-up: What evidence would falsify your leading hypothesis before widening the mitigation?
