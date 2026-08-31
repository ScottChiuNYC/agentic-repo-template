# Formal Audit Role Bootstrap

## Purpose

This document defines the minimum bootstrap information needed to enter a formal pre-freeze Auditor, Reconciler, or Remediator role.

It supplements `INDEPENDENT_PRE_FREEZE_AUDIT.md` and `DURABLE_EXECUTION_PROTOCOL.md`. Those protocols remain authoritative for substantive role semantics, audit-relevant authority isolation, reconciliation, owner decisions, remediation separation, target validity, durable handoff, and round completion.

The bootstrap principle is:

> **Bootstrap identifies the durable workflow; repository authority determines the work.**

A role prompt should route a fresh run into durable repository/workflow state. It should not duplicate protocol prose, raw findings, remediation history, or private reasoning.

## 1. Common rules

Every formal role bootstrap MUST:

- identify the repository;
- identify the role;
- provide the minimum durable workflow identity the role cannot discover from repository state;
- instruct the run to start from root `AGENTS.md` and follow repository authority;
- avoid pasting protocol prose that is already canonical in the repository;
- avoid copying private chain-of-thought or ephemeral chat state into the next role;
- rely on durable repository/workflow records for cross-run handoff.

The bootstrap prompt is routing metadata, not implementation authority.

## 2. Auditor bootstrap

An Auditor must be bound to one immutable target and one preassigned raw-result slot before substantive audit execution begins.

The minimum bootstrap identifies:

```text
role: Auditor <slot>
repository
audit exact SHA
freeze scope
round-control identity
assigned raw-result-slot identity
start from AGENTS.md / canonical audit protocol
```

The Auditor MUST NOT be given sibling result-slot content, sibling findings, reconciliation output, private remediation reasoning, or unrecorded owner decisions/closure claims that would resolve the current audit outside repository authority.

A concise shape is:

```text
You are Independent Auditor <slot> for <round>.
Repository: <owner/repo>
Audit exact SHA: <sha>
Freeze scope: <scope>
Round control: <durable-round-id>
Assigned raw-result slot: <durable-slot-id>
Start from AGENTS.md and follow the canonical independent pre-freeze audit protocol.
```

Any additional bootstrap text should exist only when repository protocol cannot reconstruct a required execution fact.

## 3. Reconciler bootstrap

A Reconciler starts only after every required raw-result slot is durably sealed.

The minimum bootstrap identifies:

```text
role: Reconciler
repository
round-control identity
start from AGENTS.md / canonical audit protocol
```

The Reconciler SHOULD discover from durable round state:

- exact audited SHA;
- freeze scope;
- required auditor slots;
- sealed raw-result identities;
- reconciliation-record convention;
- current round status.

The prompt SHOULD NOT paste raw findings, mapping rules, owner-decision rules, remediation history, or protocol text already present in repository authority.

A concise shape is:

```text
You are the Reconciler for <round>.
Repository: <owner/repo>
Round control: <durable-round-id>
Start from AGENTS.md and follow the canonical independent pre-freeze audit protocol.
Reconcile the completed round from durable repository/workflow state.
```

The Reconciler is expected to read all sealed raw results because convergence is its role. Auditor sibling-isolation rules do not apply after the audit phase is complete.

## 4. Remediator bootstrap

A Remediator starts only after reconciliation is durable and every required owner decision has a durable resolution.

The minimum bootstrap identifies:

```text
role: Remediator
repository
round-control identity
start from AGENTS.md / canonical audit/remediation and GitHub workflow protocols
```

The Remediator SHOULD reconstruct from durable state:

- audited SHA;
- canonical reconciliation record;
- canonical findings;
- durable owner decisions;
- current `main`;
- any required current-state reconciliation before mutation.

The prompt SHOULD NOT paste raw auditor reports or private auditor reasoning. Canonical findings and durable owner decisions are the authoritative remediation inputs.

A concise shape is:

```text
You are the Remediator for <round>.
Repository: <owner/repo>
Round control: <durable-round-id>
Start from AGENTS.md and follow the canonical audit/remediation and GitHub workflow protocols.
Remediate the completed round from durable repository/workflow state.
```

Repository mutation follows the repository's GitHub workflow: one focused transaction, exact-head validation, squash merge, post-merge verification, and cleanup.

## 5. Owner-decision handoff

Owner decisions are not encoded by expanding the Remediator prompt.

The canonical sequence is:

```text
Reconciler creates canonical owner-decision set
-> workflow enters WAITING_FOR_OWNER
-> owner resolves decisions
-> resolutions are recorded durably against canonical decision identities
-> round becomes remediation-eligible
-> fresh Remediator reconstructs those resolutions from durable state
```

A private chat answer is not sufficient shared workflow authority until the resolution is durably recorded.

## 6. Why prompts stay short

Long role prompts create avoidable problems:

- duplicate protocol text can drift from repository authority;
- copied findings can omit provenance or become stale after reconciliation;
- manual copy/paste becomes an owner burden;
- hidden chat context becomes harder to distinguish from durable state;
- automated dispatch becomes harder because the orchestrator must synthesize large prompts instead of passing workflow identity.

Short bootstraps make supervised ChatGPT execution, subscription-backed coding-agent execution, API execution, and deterministic orchestration converge on the same operating model:

```text
role + durable workflow identity
-> repository authority
-> current durable state
-> role execution
```

## 7. Bootstrap transport

A repository without a dedicated audit state store MAY use GitHub issues as a bootstrap durable transport:

```text
one round-control issue
one preassigned raw-result issue per auditor slot
one reconciliation record after all slots seal
```

This transport is durable but does not provide per-issue read ACLs. Auditors therefore MUST NOT inspect sibling result issues before sealing; known sibling-result exposure invalidates the slot under `DURABLE_EXECUTION_PROTOCOL.md`.

A mature orchestrator SHOULD replace discipline-only isolation with structural recorder/storage boundaries while preserving the same durable role identities.

## 8. Automation implication

A deterministic dispatcher should not need to manufacture substantive prompts for each phase. It should only determine that a role is eligible and provide the role's durable workflow identity.

Conceptually:

```text
all raw slots SEALED
-> dispatch Reconciler(round-control-id)

owner decisions RESOLVED
-> dispatch Remediator(round-control-id)

remediation integrated
-> create next round / slots
-> dispatch Auditor(slot-id) for each slot
```

The dispatcher owns eligibility and state transitions; the role reconstructs substantive authority from the repository.
