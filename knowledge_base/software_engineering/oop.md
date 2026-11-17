---
knowledge_id: swe.oop
schema_version: 1
revision: 3
status: active
roles: python_developer,software_engineer,backend_developer,full_stack_developer
skill: object-oriented programming
topic: object_oriented_programming
subtopic: oop
difficulty: mixed
source_name: PrepMate original engineering notes
source_url: https://docs.python.org/3/tutorial/classes.html
license: CC-BY-4.0 (original PrepMate notes)
reviewed_on: 2026-11-16
---
# Object boundaries and substitutability

## Definition
Object-oriented design groups state with behavior behind interfaces. The useful design question is which invariants a boundary protects and which contracts callers rely on.

## Core principles
Keep mutation behind methods that preserve valid state. Composition delegates to collaborating objects; inheritance extends an existing contract. Subtypes should preserve caller-visible expectations rather than merely share method names. Python instance attributes and class attributes have different sharing behavior.

## Practical applications
Model interchangeable payment gateways behind a small charge interface.

## Common misconceptions
Inheritance is not automatically preferable to composition. Python naming conventions do not make attributes a security boundary. Putting a mutable collection on a class can unintentionally share it among instances.

## Engineering scenario
Two shopping carts unexpectedly share items because a class-level list stores cart contents. Reproduce with two instances, move per-cart state to instance initialization and add an isolation test.

## Trade-offs and limitations
Extra abstraction can hide a simple implementation. Composition introduces delegation but avoids coupling unrelated domain concepts through inheritance. Choose a boundary that makes a specific change safer, not a hierarchy for every noun.

## Provenance
Original PrepMate explanations and interview scenarios; AI-assisted drafting with linked primary-document review on 2026-11-15. No proprietary question bank or source prose is copied. Primary reference: https://docs.python.org/3/tutorial/classes.html . The license above covers these original notes, not the linked documentation.


Phase 7 scenario is original PrepMate engineering synthesis (agent reviewed 2026-11-16), not a third-party benchmark. Additional primary support for protocol/storage/authorization or test primitives (not a proof of the complete design): https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html.

## Easy
Question: In a language of your choice, explain the difference between state shared by a class and state owned by an individual instance. Use that language's terminology; a language-neutral object example is also welcome.
Expected concepts: shared versus per-object state; mutation and isolation; language-specific terminology is optional, and not every language uses Python attribute lookup rules.
Follow-up: Show a test with two independent carts.


## Medium
Question: How would you replace a payment provider without changing checkout orchestration?
Expected concepts: interface contract; composition; failure behavior; fake provider tests.
Follow-up: Which errors should the adapter translate?


## Hard
Question: A storage client needs atomic create-if-absent for lock files and ordinary overwrites for images. Backend A supports conditional writes; backend B supports only read/overwrite but allows versioned object keys. Design interfaces and caller workflows that keep the lock-file invariant while still using B for uploads, including ambiguous timeout outcomes.
Expected concepts: Split capabilities rather than exposing a universally successful create-if-absent method. A read-then-write adapter does not make B atomic; reject unsupported lock creation or use a genuinely coordinating store. Versioned keys support immutable upload identities but not atomic ownership by themselves. Model created/already-exists/unknown outcomes explicitly, preserve exception contracts, and test substitutability at caller-visible boundaries. Composition and small interfaces can isolate policy from transport without requiring a specific programming language.
Follow-up: How would you test that an adapter cannot silently turn an unknown outcome into a safe-to-retry failure?
