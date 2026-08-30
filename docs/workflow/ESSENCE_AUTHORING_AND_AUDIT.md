# Essence Authoring and Audit Standard

## Purpose

An Essence is a normative, implementation-ready contract shared by human and AI implementers. Its purpose is not to summarize discussion. Its purpose is to remove material implementation ambiguity.

The primary acceptance criterion is:

> A fresh implementation agent can implement every in-scope phase from current repository authorities without inventing an unstated public, numerical, data, security, ownership, configuration, reproducibility, or failure-handling convention.

Conciseness matters, but reconstructibility and implementation fidelity take precedence over brevity.

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

## 1. Core equivalence test

A frozen Essence is sufficient only if competent independent implementers, without access to the originating conversation, can produce materially equivalent in-scope implementations.

The freeze criteria are:

```text
remaining unstated in-scope implementation decisions = none
remaining unintended in-scope degrees of freedom = none
materially different compliant implementations caused by specification ambiguity = none
```

If materially different compliant implementations remain possible because the contract is silent or contradictory, the Essence is not ready to freeze.

## 2. Authority

Every Essence MUST state its authority and relationship to other artifacts.

Required:

- what the Essence governs;
- what it explicitly does not govern;
- which files/interfaces become normative after freeze;
- which higher-authority constraints remain outside the Essence;
- how conflicts are resolved;
- which active research/design artifacts provide rationale without overriding normative implementation contracts.

A frozen Essence MUST NOT depend on hidden chat context.

Do not duplicate long derivations or architecture documents that already have a canonical owner. Link to them and retain the implementation-critical consequences needed to prevent ambiguity.

## 3. Required authoring content

### 3.1 Purpose, scope, naming, and exclusions

State the problem, intended result, supported use cases, canonical naming, and explicit non-goals. Future extensions MUST NOT be described as if they are already supported inside the frozen scope.

### 3.2 Terminology and invariants

Define material domain terms once. List invariants that must hold across implementations, including applicable ownership, accounting/conservation, ordering, determinism, state-transition, security, and idempotency guarantees.

### 3.3 Architecture and dependency direction

For every major boundary, state:

- who owns the abstraction;
- which layer may depend on which;
- what must not cross the boundary;
- construction/lifetime/session ownership where relevant;
- which operation owns parsing, normalization, validation, caching, persistence, execution, serialization, and reporting.

Do not write only `use library X`. Define what X is allowed to own and which project-native contract remains authoritative.

### 3.4 Normative file manifest and build surface

List the in-scope files/modules and each responsibility. Include applicable public headers, sources, bindings, language modules, tests, configuration/specification files, workflows, build/package files, and generated-interface ownership.

The manifest is normative, not illustrative. It SHOULD be precise enough that independent implementers do not invent materially different project shapes.

### 3.5 Public and cross-layer contracts

For every public interface or cross-layer message, define as applicable:

- names/signatures;
- required fields;
- input types, shapes, units, coordinate systems, time zones, and conventions;
- output types and semantic meaning;
- optional/default behavior;
- ordering and determinism;
- mutability and ownership;
- invalid-input and failure behavior;
- compatibility/versioning requirements.

Examples are not substitutes for contracts.

### 3.6 Input provenance and parameter roles

Every material input or parameter MUST have one clear role and owner. Classify applicable quantities as product/input terms, external observations/data, fixed assumptions, calibrated/optimized variables, numerical configuration, experiment/policy axes, cached/persisted state, or derived quantities.

For each material input class state:

- source/provenance;
- who supplies/parses/normalizes it;
- valid range/domain and units;
- required coverage/order/identity;
- default/fallback policy;
- whether it contributes to configuration, cache, snapshot, or reproducibility identity.

A parameter MUST NOT silently migrate between roles.

### 3.7 Algorithm and numerical contract

When numerical behavior matters, define the executable leaves of the method, including applicable:

- equations/algorithm steps;
- state and coordinate conventions;
- discretization/grid/event rules;
- quadrature/rule/normalization semantics;
- retained/adaptive dimensions;
- root-solving/bracketing behavior;
- tolerances and stopping criteria;
- limiting/degenerate branches;
- covariance/factorization/admissibility policy;
- random seed/reproducibility policy;
- floating-point exceptional behavior;
- independent convergence axes;
- performance constraints that materially change the algorithm.

A named library, backend, solver, or algorithm family is not a complete specification when materially different subchoices exist.

### 3.8 State, persistence, cache, concurrency, and recovery

If state exists, define:

- authoritative state owner;
- serialization/schema/version identity;
- cache keys and invalidation;
- restart/crash recovery;
- concurrency assumptions;
- atomicity/transaction boundaries;
- stale-state handling;
- idempotency/deduplication;
- reconciliation after partial or unknown external outcomes.

Blind retry is not a safe default when an external side effect may already have occurred.

### 3.9 External providers and adapters

For external APIs, model providers, storage, brokers, databases, services, or execution backends, define:

- provider-neutral project abstraction;
- adapter responsibilities;
- dependency/version policy;
- connection/session ownership;
- authentication/secret ownership;
- timeout/retry/backoff policy;
- rate limits/backpressure;
- reconnect behavior;
- idempotency keys/deduplication;
- reconciliation after partial or unknown outcome;
- fail-open versus fail-closed behavior.

Provider-specific objects SHOULD NOT leak across a provider-neutral boundary unless the Essence explicitly permits it.

### 3.10 Failure semantics and unsupported cases

Enumerate material failure classes and required behavior.

For each, define whether the implementation must reject, retry, degrade, return partial results, persist diagnostic state, reconcile, stop, or fail closed.

Silently clamping, clipping, skipping, extrapolating, renormalizing, substituting plausible values, or falling back to a different method is prohibited unless explicitly part of the contract.

Unsupported modes need explicit failure semantics.

### 3.11 Security and authority

Define:

- secret classes and allowed storage locations;
- which process/role may access which credentials;
- least-privilege expectations;
- production versus test credential separation;
- trusted/untrusted execution boundaries;
- destructive-action authority;
- redaction/logging rules;
- owner-only decisions/actions.

Never place secret values in the Essence.

### 3.12 Observability and provenance

Define metadata required to reproduce, reconcile, or diagnose behavior, such as:

- code/repository SHA;
- data/source version;
- configuration/policy version;
- timestamps and as-of semantics;
- run/workflow/request IDs;
- model/algorithm version;
- external operation IDs;
- execution status/failure reason.

### 3.13 Acceptance tests

Acceptance criteria MUST be executable or objectively checkable.

Cover applicable:

- happy path;
- boundary/degenerate cases;
- invalid input;
- failure/recovery behavior;
- determinism/reproducibility;
- integration boundaries;
- cross-language agreement;
- numerical convergence;
- regression-sensitive invariants;
- security/authority failures.

A statement such as `works correctly` is not an acceptance test.

### 3.14 Implementation phases and gates

If implementation is staged, each phase MUST state:

- concrete capability created;
- important files/layers involved;
- evidence required to proceed;
- dependencies on external data or owner decisions;
- whether the gate establishes implementation readiness, scientific validity, or production readiness.

The next coding milestone must be identifiable without reconstructing the originating conversation.

## 4. Author self-check

Before formal audit, the author/remediator SHOULD perform a phase-by-phase implementation simulation and ask:

> If I started coding this phase now, what material choice would I still need to make that current authorities have not fixed or explicitly delegated?

Any unresolved in-scope choice affecting public behavior, numerics, data semantics, ownership, failure behavior, security, reproducibility, or architecture is a contract gap.

Self-check is useful but has no independent freeze authority.

## 5. Mandatory independent pre-freeze audit

An Essence MUST pass the formal protocol in [`INDEPENDENT_PRE_FREEZE_AUDIT.md`](INDEPENDENT_PRE_FREEZE_AUDIT.md) before it is described as `implementation-ready`, `complete`, `frozen`, or equivalent.

The protocol requires fresh independent auditors, auditor/remediator separation, exact audited repository state, complete implementation reconstruction, canonical finding reconciliation, and a later fresh audit round after substantive remediation.

When the configured protocol uses multiple parallel auditors, a PASS from one auditor does not freeze the Essence. Freeze authority belongs to the reconciled round-level result.

Closing all known findings is not sufficient. After remediation, a new fresh audit round MUST actively search for new, residual, or newly exposed ambiguities.

## 6. Substantive finding test

Formal audit is not prose-quality review and MUST NOT become an endless preference loop.

A finding blocks freeze only when leaving it unresolved could:

- permit materially different in-scope compliant implementations; or
- materially change correctness, authority, public behavior, numerical behavior, data semantics, failure semantics, reproducibility, security, or ownership.

Style preferences, harmless naming alternatives, methods explicitly delegated to experiment axes, and issues explicitly outside the proposed freeze scope do not by themselves block freeze.

## 7. Owner-decision boundary

An unresolved item requires owner decision only when current repository authorities neither determine nor explicitly delegate the answer and multiple materially different reasonable choices remain that change owner-level scientific, product, public-API, market/model, security, or scope intent.

Routine contract completion MUST NOT be escalated merely for approval when the existing authority chain already determines closure.

Parallel audit rounds collect owner decisions only after all required independent auditors complete and raw findings are reconciled into one canonical decision package.

## 8. Freeze record

A freeze record SHOULD identify:

- exact audited repository SHA;
- proposed freeze scope;
- audit protocol/configuration used;
- audit round identity/date;
- reconciled PASS verdict;
- explicit confirmation that the three core equivalence criteria are all `none`;
- resulting freeze version/state.

A PASS is valid only for the audited authority snapshot. If material audited authority changes before freeze writeback/integration, a new audit round is required.

## 9. Reopening

A frozen Essence MAY be reopened when the contract must change.

Record:

- why it is reopened;
- which normative decisions change;
- compatibility/migration impact;
- new validation required;
- new freeze scope/version/date.

Do not silently mutate a frozen contract while implementation proceeds.

## 10. Compact audit checklist

Before freeze, verify that:

- authority and exclusions are explicit;
- dependency direction and ownership are unambiguous;
- normative files/build/package surface are enumerated;
- public/cross-layer contracts are complete;
- provenance and parameter roles are defined;
- numerical leaves are fixed where material;
- state/cache/concurrency/recovery behavior is explicit;
- external adapters define timeout/retry/idempotency/reconciliation rules;
- failure semantics and unsupported modes are explicit;
- security and credential boundaries are explicit;
- observability/provenance is sufficient;
- acceptance tests are objective and trace high-risk contracts;
- implementation phases/gates are defined where needed;
- no material behavior depends on hidden conversation context;
- the formal independent audit protocol has produced a round-level PASS.

If any material item is unresolved, do not freeze.
