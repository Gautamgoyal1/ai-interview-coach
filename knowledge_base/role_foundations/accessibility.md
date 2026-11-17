---
knowledge_id: core.accessibility
schema_version: 1
revision: 1
status: active
roles: frontend_developer,full_stack_developer
skill: accessibility
topic: accessibility
subtopic: accessibility
difficulty: mixed
source_name: PrepMate original cross-role notes
source_url: https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-15
---
# Keyboard-operable interfaces

## Definition
An accessible interaction can be operated through the required input methods and exposes meaningful names, roles and states. Keyboard support is a behavior contract, not a visual theme.

## Core principles
Prefer native controls with established keyboard behavior. Ensure keyboard users can reach and operate functionality. Keep focus visible and predictable, including after a dialog closes. A complete accessibility review also considers semantic structure, assistive technology and other success criteria.

## Practical applications
Build a configurable interview form and a confirmation dialog that can be used without a pointer.

## Common misconceptions
A click handler on a div does not provide button semantics or keyboard operation automatically. Adding a tabindex alone does not implement a composite widget pattern.

## Engineering scenario
A dialog closes and focus falls onto the document body. Record the triggering element, move focus into the open dialog, contain keyboard navigation while modal, and restore a meaningful target after closing. Test actual keyboard actions rather than only element visibility.

## Trade-offs and limitations
Native controls reduce custom interaction burden. Custom widgets need a documented keyboard pattern and more testing. Automated checks do not establish complete accessibility or replace human assistive-technology review.

## Provenance
Original PrepMate explanations and scenarios with AI-assisted drafting and primary-source review on 2026-11-15. Reference: https://www.w3.org/WAI/WCAG22/Understanding/keyboard.html . No third-party wording or proprietary question bank is copied; CC-BY-4.0 applies to these original notes only.

## Easy
Question: Why prefer a native button to a clickable div?
Expected concepts: native semantics; keyboard activation; accessible name.
Follow-up: What must a custom control implement?


## Medium
Question: How would you test a confirmation dialog using only a keyboard?
Expected concepts: initial focus; Tab order; Escape; focus restoration; visible focus.
Follow-up: What happens if the trigger is removed while open?


## Hard
Question: Design focus recovery for an asynchronous multi-step editor.
Expected concepts: stable focus target; announcements; prevented accidental actions; real assistive-technology testing.
Follow-up: How do loading transitions avoid moving focus unexpectedly?
