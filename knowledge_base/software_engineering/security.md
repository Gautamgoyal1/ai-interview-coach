---
knowledge_id: swe.security
schema_version: 1
revision: 3
status: active
roles: software_engineer,frontend_developer,backend_developer,full_stack_developer,devops_engineer,cybersecurity_analyst,qa_engineer
skill: security fundamentals
topic: security_fundamentals
subtopic: security
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Authorization at resource boundaries

## Definition
Authentication establishes identity; authorization decides whether an action on a particular resource is allowed. Both need server-side enforcement at trustworthy boundaries.

## Core principles
Deny access by default and grant only required privileges. Check object ownership or policy for each operation, not merely whether a user is logged in. Keep data access scoped to the authenticated principal. Use safe error behavior and test horizontal as well as vertical privilege changes.

## Practical applications
Prevent one authenticated user from retrieving or editing another user's interview report by changing a URL identifier.

## Common misconceptions
An opaque identifier does not replace authorization. Hiding a button does not enforce access control. A valid token does not grant access to every object.

## Engineering scenario
A report endpoint checks the token but loads records solely by report ID. Scope lookup by both ID and authorized owner or a reviewed sharing policy, and test read, edit, export and delete paths with a second user.

## Trade-offs and limitations
Centralized policy checks reduce omissions but must model resource-specific rules. Avoid leaking object existence when the product requires that confidentiality. Audit logs help investigation but must avoid tokens and private answer content.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html.

## Easy
Question: How is authorization different from authentication?
Expected concepts: identity versus permission; resource scope.
Follow-up: Can a logged-in user still be forbidden from accessing a report?


## Medium
Question: How would you test a report endpoint for cross-user access?
Expected concepts: two principals; object ownership; read and mutation paths; denial.
Follow-up: What if reports can be shared explicitly?


## Hard
Question: A report export runs in a background job and its cached download is shared through a link. Team removal must revoke access within 30 seconds, including queued jobs and already issued links. Design the authorization boundaries and cache contract to meet that bound.
Expected concepts: Authorize queue submission, recheck current principal/resource policy at job execution and download, and bind object access to ownership/tenant context. Long-lived signed links alone cannot enforce earlier revocation. Use an authenticated proxy, bounded cache/credential lifetime or a revocation/version check, including CDN behavior and invalidation propagation. Job service privileges must not substitute for the requester policy. Define the revocation window, fail-closed behavior on unavailable policy data, policy tests and privacy-preserving audit evidence. No scheme can revoke a copy already downloaded by an authorized user.
Follow-up: How would you measure the revocation bound when a cache node misses an invalidation?
