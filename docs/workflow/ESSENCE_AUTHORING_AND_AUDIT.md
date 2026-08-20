# Essence Authoring and Audit Standard

An Essence is a normative, implementation-ready contract shared by human and AI implementers. Its purpose is not to summarize discussion. Its purpose is to remove material implementation ambiguity.

## Core test

A frozen Essence is sufficient only if two competent implementers, without access to the originating conversation, can independently produce materially equivalent implementations.

If they could reasonably choose different behavior because the Essence is silent, the Essence is not ready to freeze.

## Authority

Every Essence must state its authority and relationship to other artifacts.

Required:

- what the Essence governs;
- what it explicitly does not govern;
- which files/interfaces become normative after freeze;
- what higher-authority constraints, if any, remain outside the Essence;
- how conflicts are resolved.

A frozen Essence must not depend on hidden chat context.

## Required sections

### 1. Purpose and scope

State the problem, intended result, supported use cases, and exclusions. Define non-goals explicitly when they prevent accidental scope expansion.

### 2. Terminology and invariants

Define domain terms once. List invariants that must hold across implementations.

Examples:

- ownership boundaries;
- conservation or accounting identities;
- monotonicity/order constraints;
- idempotency guarantees;
- state transition restrictions.

### 3. Architecture and dependency direction

Specify component ownership and allowed dependency direction.

For each boundary, state:

- who owns the abstraction;
- which layer may depend on which;
- which third-party types may cross the boundary;
- lifetime/session ownership where relevant.

Do not write only "use library X." Define what X is allowed to own and what must remain project-native.

### 4. Normative file manifest

List the files/modules that must exist or change, with each file's responsibility.

The manifest should be precise enough that an implementer does not invent a materially different project shape.

### 5. Public and cross-layer contracts

For every public interface or cross-layer message, define as applicable:

- names and signatures;
- input types, units, coordinate systems, time zones, and conventions;
- output types and semantic meaning;
- optional/default behavior;
- ordering and determinism;
- mutability and ownership;
- error/failure behavior;
- compatibility requirements.

Examples are not substitutes for contracts.

### 6. Input provenance and parameter roles

For each material input or parameter, state:

- source/provenance;
- who supplies it;
- whether it is configuration, calibration, inferred state, cached state, or runtime observation;
- valid range/domain;
- fallback/default policy;
- versioning requirements.

### 7. Algorithm and numerical contract

When numerical behavior matters, define:

- equations/algorithm steps;
- discretization and approximation choices;
- tolerance semantics;
- convergence/stopping criteria;
- random seed/reproducibility policy;
- floating-point exceptional behavior;
- boundary/degenerate cases;
- performance constraints that affect the algorithm.

Do not replace a derivation or algorithm with "use a standard implementation" when materially different standards exist.

### 8. State, persistence, cache, and concurrency

If state exists, define:

- authoritative state owner;
- serialization format/version;
- cache key and invalidation policy;
- restart/recovery behavior;
- concurrency assumptions;
- atomicity/transaction boundaries;
- stale-state handling.

### 9. External providers and adapters

For brokers, databases, APIs, model providers, storage systems, or similar adapters, define:

- provider-neutral project abstraction;
- adapter responsibilities;
- third-party library/version policy;
- connection/session ownership;
- authentication/secret ownership;
- timeout and retry rules;
- rate limits/backpressure;
- reconnect behavior;
- idempotency keys/deduplication;
- reconciliation after partial failure;
- behavior when the external outcome is unknown;
- fail-open versus fail-closed behavior.

Provider-specific objects should not leak across a provider-neutral boundary unless the Essence explicitly allows it.

### 10. Failure semantics

Enumerate material failure classes and required behavior.

For each class, define whether the implementation should:

- reject immediately;
- retry;
- degrade;
- return partial results;
- persist diagnostic state;
- reconcile before continuing;
- stop/kill/fail closed.

Unknown external side effects require an explicit reconciliation rule; blind retry is not a safe default.

### 11. Security and secrets

Define:

- what constitutes a secret;
- where secrets may live;
- which process/workflow may access them;
- least-privilege expectations;
- redaction/logging rules;
- production versus test credential separation.

Never place secret values in the Essence.

### 12. Observability and provenance

Define the metadata needed to reproduce or diagnose behavior, such as:

- code/version SHA;
- data/source version;
- configuration version;
- timestamps and as-of semantics;
- run/request IDs;
- model/algorithm version;
- execution status and failure reason.

### 13. Acceptance tests

Acceptance criteria must be executable or objectively checkable.

Cover at least:

- happy path;
- boundary cases;
- invalid input;
- failure/recovery behavior;
- determinism/reproducibility where promised;
- integration boundaries;
- regression-sensitive invariants.

A statement such as "works correctly" is not an acceptance test.

### 14. Implementation phases and gates

If implementation is staged, define phase boundaries and the evidence required to proceed. Separate research gates from production gates when their standards differ.

## Freeze process

Before freeze:

1. author the Essence from current authoritative repository state;
2. perform a self-audit against every required section;
3. run an independent pre-freeze audit from the perspective of an implementer who does not know the originating discussion;
4. resolve all material ambiguities;
5. record the freeze state/version.

The independent audit should actively look for places where two reasonable implementers could diverge.

## Reopening

A frozen Essence may be reopened when the contract must change.

Record:

- why it is reopened;
- which normative decisions change;
- compatibility/migration impact;
- new validation required;
- new freeze version/date.

Do not silently mutate a frozen contract while implementation proceeds.

## Audit checklist

Before freeze, verify:

- authority and exclusions are explicit;
- dependency direction is unambiguous;
- normative files are enumerated;
- public/cross-layer contracts are complete;
- provenance and parameter roles are defined;
- numerical conventions are fixed where material;
- state/cache/concurrency behavior is defined;
- provider adapters include timeout/retry/reconnect/idempotency/reconciliation rules;
- failure semantics are explicit;
- security and secret boundaries are explicit;
- acceptance tests are objective;
- implementation phases/gates are defined when needed;
- no material behavior depends on hidden conversation context.

If any item is materially unresolved, do not freeze.
