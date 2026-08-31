# Durable Agent Execution Protocol

## Purpose

This document defines the generic repository protocol for efficient long-running AI work, cross-run continuity, executor neutrality, and durable audit/remediation handoff.

It supplements `AI_AGENT_OPERATING_POLICY.md`, `AI_AGENT_GITHUB_WORKFLOW.md`, and `INDEPENDENT_PRE_FREEZE_AUDIT.md`. Within the scope owned here, this document is authoritative when older inherited wording is ambiguous or stricter than the rules below.

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

The central design principle is:

> **LLMs may be disposable; workflow state must be durable.**

A second optimization principle is:

> **Reason as many times as necessary; mutate shared GitHub state as few times as possible.**

Neither principle weakens validation, exact-head merge safety, or post-merge verification.

## 1. Scope and ownership

This protocol owns four generic concerns:

1. pre-final-head transaction convergence and latency reduction;
2. durable checkpoints and restart after interrupted agent execution;
3. executor-neutral workflow identity;
4. audit-relevant authority isolation and durable Auditor/Reconciler/Remediator handoff.

Project-specific scientific, product, security, deployment, cost, model-selection, or backend-runtime policy remains project-owned.

A project MAY add stricter controls, but it MUST NOT silently weaken the invariants in this document.

## 2. Pre-final-head convergence

For a normal repository mutation, the preferred critical path is:

```text
READ latest main and authorities
-> resolve owner decisions already known to be required
-> PLAN the complete intended final diff
-> CREATE one canonical task branch
-> CONVERGE the branch using cheap/readback/guarded validation
-> establish one intended final branch head
-> OPEN one focused PR
-> run required expensive final-head validation
-> exact-head squash merge
-> verify main
-> verify publication/artifacts
-> clean task state
```

The agent SHOULD avoid using GitHub or CI as a scratchpad.

In particular:

- repository writes SHOULD represent intended durable progress, not API experiments;
- the agent SHOULD discover current files, tools, schemas, and likely affected authorities before the first write;
- related multi-file semantic changes SHOULD be planned as one coherent transaction rather than discovered one file at a time after PR creation;
- cheap deterministic checks and complete-file readback SHOULD happen before expensive PR validation when possible;
- a heavy validation workflow SHOULD run against the intended final head, not every intermediate thought or small edit;
- once a PR exists, avoid changing its head unless validation discovers a real defect or current `main` requires reconciliation;
- a changed PR head invalidates earlier head-specific merge authority and MUST be revalidated.

This optimization is subordinate to correctness. A required build, test, audit, publication, or exact-head gate MUST NOT be skipped merely to reduce wall-clock time.

## 3. Validation placement

Repositories SHOULD distinguish between:

```text
cheap convergence checks
and
expensive integration evidence
```

Examples of cheap pre-PR convergence checks include:

- exact current-state reads;
- intended-path inventory;
- semantic readback;
- diff inspection;
- Markdown/math/link validation;
- syntax checks;
- deterministic Safe Patch guards;
- targeted local/unit validation when inexpensive.

Examples of expensive integration evidence may include:

- full build matrices;
- large test suites;
- CodeBinder/PDF publication;
- deployment packaging;
- long numerical reference runs.

Where repository workflow permits, expensive integration evidence SHOULD be generated once for the final intended PR head and once after merge when the post-merge publication/deployment contract independently requires it.

The post-merge run is not redundant with PR validation when it establishes a different invariant such as publication from `main`, deployment identity, or external upload.

## 4. Durable checkpoint contract

Any long-running task MUST be able to survive loss of the current agent execution window without requiring private scratch reasoning to reconstruct task state.

At each coherent boundary, durable state SHOULD make the following discoverable when applicable:

```text
repository / task identity
base main SHA
canonical branch
current exact branch head SHA
intended outcome / governing authority
durable owner decisions already made
open PR and exact head, if any
validation already completed and against which SHA
remaining transaction state
```

Durable checkpoint state MAY live in normal repository files, branch/PR state, issues, audit records, or an external deterministic state store. Chat history alone is not a durable checkpoint.

An execution interruption MUST NOT change the Definition of Done.

An agent approaching an execution limit MUST NOT:

- weaken validation;
- merge an incompletely validated head;
- mark a finding closed without durable evidence;
- skip publication verification;
- claim completion because the conversation is ending.

Instead it SHOULD leave repository/GitHub state at a coherent recoverable boundary.

## 5. Resume semantics

A new run resumes by observation, not by replaying the prior call sequence.

The recovery rule is:

```text
READ durable task identity and current external state
-> identify the exact invariant already established
-> reconcile with current main / branch / PR / workflow state
-> continue from the first unmet invariant
```

Do not redo completed semantic reconstruction merely because the prior model run ended, unless current repository authority changed or the durable checkpoint is insufficient/contradictory.

Unknown operation outcome remains a reconciliation problem. Never create a duplicate commit, branch, PR, audit result, or merge attempt simply because an earlier response was lost.

## 6. Executor-neutral workflow identity

Repository workflow semantics MUST NOT depend on one particular model product or execution backend.

The same durable workflow MAY be executed by, for example:

```text
human-supervised ChatGPT
subscription-backed coding agent / Codex-style runner
metered API worker
Steward or another deterministic orchestrator
human operator
```

Changing executor MUST NOT silently change:

- repository authority;
- role boundaries;
- audit independence requirements;
- owner-decision boundaries;
- validation requirements;
- exact-head merge semantics;
- durable handoff format;
- Definition of Done.

Executor selection, pricing, credentials, model choice, token budget, VPS topology, CLI flags, and backend failover are runtime/project concerns unless explicitly promoted into repository policy.

Role bootstrap therefore identifies **role + durable workflow identity**, not a product-specific transcript.

## 7. Formal audit freshness: authority isolation, not total amnesia

For formal independent audit, freshness is an **audit-relevant authority/evidence boundary**, not a requirement for total model amnesia.

A fresh auditor MUST still be a separate new run/session/process from the remediator and sibling auditors and MUST evaluate the same immutable audit SHA from repository authority.

Ordinary ambient context MAY exist, including:

- saved user preferences;
- general project familiarity;
- non-sensitive background;
- facts independently recoverable from the audited repository.

Such ambient context is non-authoritative. It MUST NOT be used to fill or resolve a repository contract gap.

The following are audit-relevant privileged context and invalidate the slot if supplied before sealing:

```text
sibling current-round findings, verdicts, raw payloads, or reasoning
current-round reconciliation/adjudication output
private remediation reasoning for the state being audited
unrecorded owner decisions that resolve in-scope ambiguity
targeted author/remediator closure claims not established by repository authority
state that materially steers the auditor toward a predetermined verdict/finding set
```

If such context is known to have reached the auditor before sealing, the auditor MUST stop and the slot MUST be replaced by a fresh run.

If older inherited protocol wording can be read to require manual disabling of ordinary product memory/history or total absence of ambient context, interpret that wording according to this section. The required boundary is **independent audit-relevant authority isolation**.

## 8. Durable audit result transport

A formal multi-auditor round MUST NOT depend on the owner manually copying reports between conversations.

Before each auditor begins, the workflow SHOULD establish:

```text
one durable round-control identity
one immutable audit target SHA
one preassigned raw-result slot per auditor
one freeze scope
```

Each auditor seals only its own result. Reconciliation begins only after all required raw-result slots are durably sealed.

The durable handoff sequence is:

```text
parallel isolated auditors
-> sealed raw-result slots
-> one canonical reconciliation record
-> durable owner decisions, if required
-> separate remediator reconstructs from canonical durable state
-> integrated remediation
-> next fresh round
```

Every substantive raw finding MUST map to a canonical finding or an explicit dismissal reason. Credible disagreement is preserved; majority vote alone does not erase a material ambiguity.

During a bootstrap phase, GitHub issues MAY serve as durable round/result/reconciliation records. Because ordinary GitHub issues do not provide per-issue read ACLs, discoverability is not structural isolation: auditors MUST NOT inspect sibling result slots before sealing, and known sibling exposure invalidates the slot.

A mature orchestrator SHOULD enforce isolation and recording structurally rather than relying only on discipline.

## 9. Minimal role bootstrap

Formal role prompts SHOULD be short and should route a run into durable state rather than duplicate protocol prose.

Use `AUDIT_ROLE_BOOTSTRAP.md` for the canonical minimal shapes.

The general rule is:

> **Bootstrap identifies the durable workflow; repository authority determines the work.**

Auditor bootstrap identifies the repository, exact audit SHA, scope, round, and its own result slot.

Reconciler bootstrap identifies the repository and round-control identity.

Remediator bootstrap identifies the repository and round-control identity after reconciliation and owner decisions are durable.

Private chain-of-thought and copied cross-chat transcripts are not workflow inputs.

## 10. Measurement and workflow optimization

When evaluating workflow efficiency, count state-transition cost rather than only commit count.

Useful measurements include:

```text
GitHub writes
branch commits
branch-head changes
PR-head revisions
expensive CI generations
serial tool/reconciliation rounds
wall-clock time from authorized decision to integrated/publication-complete state
number of execution-window continuations
amount of semantic work repeated after interruption
```

A good optimization reduces unnecessary state transitions and repeated expensive validation while preserving every required correctness/safety invariant.

Decision latency and execution latency SHOULD be distinguished. Time spent obtaining a genuine owner scientific/product decision is not the same problem as avoidable repository transaction latency after the decision is fixed.

## 11. Consumer synchronization

ART is the canonical generic source for this protocol. Existing ART consumers SHOULD synchronize the generic semantics while preserving project-local additions.

Consumer synchronization is a semantic reconciliation, not a blind file overwrite.

A project-specific protocol may extend the generic contract, but inherited generic behavior SHOULD remain recognizable so that an agent or future orchestrator can switch among repositories without inventing a different workflow each time.

## 12. Definition of successful adoption

A repository has adopted this protocol when all applicable statements are true:

```text
pre-PR convergence is preferred over repeated PR-head churn
expensive validation is tied to the intended final head
execution can resume from durable state after interruption
executor choice does not redefine workflow semantics
formal audit freshness uses audit-relevant authority isolation
formal audit results and owner decisions have durable handoff
role bootstrap does not require owner copy/paste of private chats
exact-head merge and post-merge verification remain mandatory
```
