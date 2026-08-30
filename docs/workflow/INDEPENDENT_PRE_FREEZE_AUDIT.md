# Independent Pre-Freeze Audit Protocol

## Purpose

This document is the canonical execution protocol for independently auditing an Essence or equivalent implementation contract before it is declared `FROZEN`, `IMPLEMENTATION-READY`, or equivalent.

[`ESSENCE_AUTHORING_AND_AUDIT.md`](ESSENCE_AUTHORING_AND_AUDIT.md) defines what implementation completeness means. This document defines how fresh auditors are bootstrapped, how independence is preserved, how findings are reconciled, how owner decisions are collected, and how audit/remediation rounds converge.

The primary question is:

> Can competent independent implementers, using only the current repository authorities, produce materially equivalent in-scope implementations without inventing or selecting an unstated public, numerical, data, failure, reproducibility, or ownership convention?

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

## 1. Audit-remediation convergence model

Closing known findings is necessary but not sufficient for freeze. A remediator MUST NOT restore a freeze merely because previously recorded findings are marked `CLOSED`.

The required model is a **batched parallel independent audit-remediation convergence loop**:

```text
NOT FROZEN
-> freeze one immutable audit target SHA
-> run multiple fresh independent auditors in parallel
-> wait for all required auditors to complete
-> reconcile raw findings into one canonical finding set
-> collect one canonical owner-decision set
-> obtain owner decisions if required
-> perform separate consolidated remediation
-> validate / integrate the remediation
-> start a new parallel audit round from the new main SHA
-> ...
-> round PASS
-> FROZEN / IMPLEMENTATION-READY
```

There is no expectation that the first post-remediation round will PASS. Later auditors may expose deeper ambiguities after earlier blockers are removed. This is normal convergence behavior.

The loop is not permission for endless preference-driven review. A finding blocks freeze only when leaving it unresolved could permit materially different in-scope compliant implementations or materially change correctness, authority, public/numerical behavior, failure semantics, reproducibility, security, or ownership.

## 2. Audit-round invariants

Every formal audit attempt is an **audit round**.

Each round MUST satisfy all of the following:

1. one exact repository commit SHA is frozen as the audit target;
2. every auditor evaluates that same immutable target SHA;
3. every auditor is a fresh isolated run;
4. auditors do not receive one another's findings or reasoning;
5. auditors do not receive remediation reasoning as implementation authority;
6. all required auditors complete before round-level findings are finalized;
7. reconciliation occurs only after independent audits complete;
8. substantive remediation does not occur inside an auditor run;
9. the next round starts from a new current repository snapshot after remediation is integrated.

Parallelism is an execution property, not a relaxation of independence.

## 3. Fresh-context independence

A fresh auditor MUST:

- start from a new conversation/session/process or equivalent isolated model context;
- start from a clean repository workspace or immutable read-only snapshot of the audit SHA;
- reconstruct context from repository authorities beginning with `AGENTS.md`;
- not inherit the remediator's private reasoning or conversation history;
- treat prior `CLOSED` labels, prior PASS claims, and author explanations as evidence to verify rather than conclusions to inherit;
- not have performed the substantive remediation being judged in that round.

A new agent identity without context isolation is not sufficient. Freshness is a state boundary, not a prompt style.

## 4. Auditor role and permissions

The auditor acts as an independent senior implementation reviewer.

The auditor MUST:

- simulate implementation phase by phase through the proposed freeze scope;
- actively search for new gaps rather than only re-check previous findings;
- verify that current repository authorities uniquely determine material behavior;
- identify choices that two reasonable compliant implementations could make differently with material consequences;
- classify findings by decision class;
- return a binary `PASS` or `FAIL` verdict for its own audit result;
- identify the exact audited SHA in its result.

The auditor MUST NOT:

- substantively modify the implementation contract it is judging;
- silently choose a reasonable numerical, public-API, scientific, product, security, or ownership convention when the repository leaves a material choice open;
- certify its own substantive repair as independent closure.

Purely mechanical audit-result recording MAY be performed by a separate deterministic integration step. An auditor SHOULD otherwise be read-only.

## 5. Required audit simulation

The auditor MUST apply the complete checklist in [`ESSENCE_AUTHORING_AND_AUDIT.md`](ESSENCE_AUTHORING_AND_AUDIT.md) and at minimum test the following areas.

### 5.1 Authority and contradiction

Verify that current authorities agree about scope, ownership, public behavior, numerical methods, configuration, failure policy, and phase gates. Archived or superseded material must not accidentally override current contracts.

### 5.2 Public construction and defaults

For every public or cross-layer type, verify fields, units, ordering, identity, validation, defaults, unsupported modes, and invalid-input behavior. Hidden defaults that can materially alter output or method identity are findings.

### 5.3 Input provenance and parameter roles

Every material quantity must have an unambiguous source and role, such as product input, market data, fixed assumption, calibrated variable, numerical configuration, experiment axis, or derived quantity.

### 5.4 Numerical hidden degrees of freedom

A library or algorithm-family name is not a complete numerical contract. Recursively decompose material choices until each leaf is fixed by a named authority, explicitly owned configuration with a defined domain, experiment-only, or out of scope.

### 5.5 Failure semantics

Ask whether a well-intentioned implementation could reasonably clamp, clip, skip, renormalize, extrapolate, silently repair, substitute, retry, or fall back differently. If materially different behaviors remain compliant, record a finding.

### 5.6 State, persistence, concurrency, and recovery

Where state exists, verify authoritative ownership, persistence identity, restart behavior, stale-state handling, idempotency, concurrency assumptions, reconciliation after unknown external outcomes, and fail-open/fail-closed behavior.

### 5.7 Manifest, build, package, and dependency ownership

Verify that architecture objects have consistent file/build/package ownership and that implementation dependencies and language bindings do not create competing sources of truth.

### 5.8 Acceptance-test traceability

For each high-risk contract, identify an objective test, invariant, failure test, convergence check, reproducibility check, or phase gate that would detect a wrong implementation.

### 5.9 Residual-decision test

For every phase ask:

> If implementation began now, what material choice would still need to be made that current repository authorities have neither fixed nor explicitly delegated?

Then ask:

> Can two competent implementations both comply yet differ materially because the specification leaves a choice open?

## 6. Structured finding contract

Every substantive raw finding SHOULD contain stable machine-readable fields equivalent to:

```text
id
severity
affected_scope
affected_authority
decision_class
description
material_consequence
requires_owner_decision
status
```

`decision_class` SHOULD distinguish at least:

```text
contract_remediation
numerical_method_decision
scientific_decision
product_decision
public_api_decision
security_or_authority_decision
infrastructure_failure
mixed
```

Operational failures such as API timeouts or unavailable execution backends are not scientific findings and SHOULD be handled by workflow recovery policy rather than disguised as owner decisions.

A finding must be specific enough for a separate remediator to act without access to the auditor's private chain of thought.

## 7. Reconciliation and canonical findings

Independent auditors MUST NOT communicate or converge with one another during the audit phase.

After all required auditors reach a terminal result, a separate reconciliation step MUST map raw findings into one **canonical finding set**.

For every raw substantive finding, reconciliation MUST either:

- map it to exactly one canonical finding; or
- dismiss it with an explicit reason such as duplicate, non-substantive, out-of-scope, or contradicted by higher authority.

No substantive raw finding may silently disappear.

Semantically equivalent findings from different auditors SHOULD be deduplicated. The canonical record SHOULD retain provenance showing which auditors raised the issue and whether their classifications differed.

Auditor disagreement is evidence, not noise. Majority vote alone MUST NOT dismiss a credible material ambiguity.

Reconciliation MAY use an LLM classifier/adjudicator, but deterministic workflow code owns the final state transition and MUST preserve traceability from raw to canonical findings.

## 8. Owner decisions

Owner escalation occurs at the **round boundary**, not at the first auditor that encounters an ambiguity.

An auditor that identifies an owner-level decision MUST record the finding and continue its full audit. Other auditors continue independently. Only after all required auditors complete and findings are reconciled is the owner-decision package finalized.

The canonical owner-decision set MUST be deduplicated and SHOULD present, for each item:

- the decision question;
- materially viable alternatives;
- recommended choice when appropriate;
- downstream consequences;
- affected scope;
- source canonical finding(s).

A finding is owner-decision-required only when current repository authorities neither determine nor delegate the answer and materially different reasonable choices remain that change scientific interpretation, product intent, supported scope, public API, market/model convention, security boundary, or another owner-level policy.

Routine contract synchronization, schema completion, serialization details, build ownership, failure mapping, test traceability, and similar work MUST NOT be escalated when existing authorities uniquely determine closure.

If an audit round contains owner decisions, all required auditors still finish and the round is reconciled before the workflow enters `WAITING_FOR_OWNER`.

## 9. Remediation separation

Remediation begins only after the audit round has produced its canonical finding set and any required owner decisions have been resolved.

The remediator MAY receive:

- the audited SHA;
- canonical findings;
- recorded owner decisions;
- current repository authorities.

The remediator MUST NOT be used as the next independent auditor of its own changes.

When one round contains both auto-remediable findings and owner-decision findings, the default SHOULD be one coherent remediation phase after owner decisions are available. This avoids changing the audited repository snapshot while owner decisions are still scoped against it.

## 10. Round verdict

The round-level verdict is exactly one of:

```text
PASS
FAIL
```

`PASS` requires all of the following for the proposed freeze scope:

```text
canonical substantive findings = none
remaining unstated in-scope implementation decisions = none
remaining unintended in-scope degrees of freedom = none
materially different compliant implementations caused by specification ambiguity = none
```

A single auditor PASS is not sufficient when the configured round requires multiple auditors.

If any canonical substantive finding remains, the round is `FAIL`. An owner decision may resolve a finding for remediation, but the freeze still requires a later fresh parallel audit round to PASS after the resolved contract is integrated.

## 11. Audit target validity

The exact audited SHA is part of the verdict.

Before a PASS is used to freeze or before a mechanical freeze-state writeback is merged, compare current `main` with the audited SHA. If a canonical authority or other state materially affecting the audited scope changed, the PASS is invalid and a new audit round MUST run.

If `main` advanced only through demonstrably unrelated changes, a deterministic reconciliation step MAY rebase a mechanical writeback, but the non-overlap must be explicitly verified.

## 12. Workflow integration and Definition of Done

Audit, remediation, merge, publication, and cleanup follow [`AI_AGENT_GITHUB_WORKFLOW.md`](AI_AGENT_GITHUB_WORKFLOW.md).

A complete convergence cycle is conceptually:

```text
parallel audit round against exact main SHA
-> canonical finding reconciliation
-> owner decisions if required
-> separate remediation
-> validation
-> PR
-> exact-head validation
-> squash merge
-> verify main
-> verify applicable publication/artifacts
-> clean transaction state
-> next fresh parallel audit round
```

The audit system or execution platform MAY automate this lifecycle, but automation does not weaken any repository invariant.

## 13. Bootstrap contract

A bootstrap prompt for a fresh auditor SHOULD remain short. It should identify the repository and proposed freeze scope, require starting from the exact current repository snapshot, and instruct the auditor to read `AGENTS.md` and this protocol.

Do not paste remediation history, previous auditor reasoning, or claims about what was fixed into a fresh auditor prompt. The repository is the durable authority.
