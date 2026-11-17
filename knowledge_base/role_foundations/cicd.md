---
knowledge_id: core.cicd
schema_version: 1
revision: 1
status: active
roles: ml_engineer,devops_engineer,qa_engineer
skill: ci/cd
topic: ci_cd
subtopic: cicd
difficulty: mixed
source_name: PrepMate original cross-role notes
source_url: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Release pipelines and recovery gates

## Definition
Continuous integration validates combined changes frequently. Continuous delivery keeps releases deployable through repeatable checks; automatic production deployment is a separate policy choice.

## Core principles
Build an identifiable artifact and promote the same artifact through environments. Gate deployment on relevant tests and reviewed permissions. Deployment environments may restrict triggering branches, require approval or limit access to secrets. Verify deployment health after the release step reports success.

## Practical applications
Release an API change through staging with a reversible application rollout and a separately reviewed schema plan.

## Common misconceptions
A green pipeline does not prove production health. Rebuilding from the same source in every environment does not guarantee identical artifacts. Rolling back an application does not undo an incompatible data migration.

## Engineering scenario
A release changes both an API and a database column. Use a backward-compatible expand-and-contract sequence, exercise old/new compatibility, and define a health-based stop condition before rollout.

## Trade-offs and limitations
Gates reduce some risks but can slow feedback. Credentials should be scoped to the environment and operation. Recovery may require a forward fix when data or external state has changed; avoid promising universal rollback.

## Provenance
Original PrepMate explanations and scenarios with AI-assisted drafting and primary-source review on 2026-11-15. Reference: https://docs.github.com/en/actions/concepts/workflows-and-actions/deployment-environments . No third-party wording or proprietary question bank is copied; CC-BY-4.0 applies to these original notes only.

## Easy
Question: How do continuous delivery and automatic deployment differ?
Expected concepts: deployable state; approval policy; automated checks.
Follow-up: When would a manual production gate be appropriate?


## Medium
Question: How do you detect and recover from a bad API deployment?
Expected concepts: immutable artifact; health signals; stop condition; compatible rollback.
Follow-up: What if database state changed?


## Hard
Question: Design a pipeline for a backward-incompatible database change.
Expected concepts: expand/contract; compatibility period; artifact promotion; recovery rehearsal.
Follow-up: Which stages require an explicit human review?
