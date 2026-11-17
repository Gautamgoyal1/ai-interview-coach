---
knowledge_id: core.test_automation
schema_version: 1
revision: 1
status: active
roles: qa_engineer
skill: test automation
topic: test_automation
subtopic: test_automation
difficulty: mixed
source_name: PrepMate original cross-role notes
source_url: https://playwright.dev/docs/best-practices
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Reliable browser automation

## Definition
Test automation repeatedly exercises observable behavior with controlled inputs and checks. Browser automation should test a user contract while isolating unrelated sources of nondeterminism.

## Core principles
Use resilient user-facing locators and assertions tied to actual state. Keep tests isolated and control test accounts/data. Wait for observable readiness rather than guessing delays. Separate simulated network behavior from checks that require a real service.

## Practical applications
Verify Stop & Review followed by explicit Submit while injecting a delayed final transcription event.

## Common misconceptions
A fixed sleep does not prove readiness. Passing with mocked speech does not establish microphone or cloud recognition behavior. Automatically retrying a flaky test can hide an application race.

## Engineering scenario
A test sometimes submits twice because the UI enables a control before an earlier request settles. Make the race deterministic with a deferred response, verify one request, and inspect the actual disabled state rather than adding a longer sleep.

## Trade-offs and limitations
End-to-end tests expose integration behavior but are more costly to maintain than focused component tests. Trace artifacts aid diagnosis but need secret filtering. A small representative set of real-service checks complements deterministic mocks.

## Provenance
Original PrepMate explanations and scenarios with AI-assisted drafting and primary-source review on 2026-11-15. Reference: https://playwright.dev/docs/best-practices . No third-party wording or proprietary question bank is copied; CC-BY-4.0 applies to these original notes only.

## Easy
Question: Why prefer a labelled control locator to a brittle DOM path?
Expected concepts: user contract; accessible name; reduced markup coupling.
Follow-up: What if two controls have the same name?


## Medium
Question: How do you make an asynchronous double-submit bug repeatable?
Expected concepts: deferred response; controlled event order; request count; state assertion.
Follow-up: Which part still needs an integration test?


## Hard
Question: Design a browser suite spanning mocks and a rate-limited speech service.
Expected concepts: offline determinism; explicit real-service gate; cleanup; truthful evidence scope.
Follow-up: How will you distinguish a product failure from an environment outage?
