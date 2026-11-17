---
knowledge_id: swe.git
schema_version: 1
revision: 2
status: active
roles: python_developer,software_engineer,frontend_developer,backend_developer,full_stack_developer,devops_engineer,qa_engineer
skill: git
topic: git
subtopic: git
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://git-scm.com/docs/git-revert
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Shared history and safe rollback

## Definition
Git records repository history as commits connected by parent relationships. Recovery choices depend on whether history has been shared and what must remain auditable.

## Core principles
A revert records a new commit that reverses a prior change. Rewriting branch history changes commit ancestry and can disrupt collaborators. Inspect the working tree and exact target before a recovery operation. Merge reversions require deliberate parent interpretation.

## Practical applications
Undo a regression already merged into a shared integration branch.

## Common misconceptions
Revert and reset are not interchangeable. Reverting a merge has implications for what later merges consider already integrated. A code rollback does not automatically reverse database migrations or external side effects.

## Engineering scenario
A deployed feature causes errors but later commits depend on nearby code. Make a focused revert or corrective commit, inspect conflicts, run relevant tests and document any state migration that cannot be undone by reverting source.

## Trade-offs and limitations
Reverts preserve shared history but may require conflict resolution. A forward fix can be safer than broad rollback when data has changed. Operational rollback and source history recovery are related but separate decisions.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://git-scm.com/docs/git-revert . The license above covers these original notes, not the linked documentation.

## Easy
Question: Why use revert on a shared branch?
Expected concepts: new inverse commit; shared ancestry; auditability.
Follow-up: What happens to later commits?


## Medium
Question: How would you handle a revert conflict after follow-on changes?
Expected concepts: inspect intended behavior; resolve deliberately; test dependencies.
Follow-up: When is a forward fix more appropriate?


## Hard
Question: Plan recovery for a bad merge with a non-reversible data migration.
Expected concepts: merge parent meaning; application/data compatibility; staged recovery.
Follow-up: What must be verified before redeploying older code?
