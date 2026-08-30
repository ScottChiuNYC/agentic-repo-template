# AI Agent Operating Policy

## Purpose

This document defines repository-level behavior for AI agents. It is intentionally model-, vendor-, and execution-backend-neutral.

The default objective is:

```text
owner authorizes a repository outcome
-> agents handle routine repository mechanics autonomously
-> deterministic validation gates integration
-> owner is interrupted only for genuinely owner-owned decisions or unavailable owner-only actions
-> owner reviews the final artifact
```

The normative terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used deliberately.

## 1. Authority

Repository state is durable authority. Current files on `main` outrank stale conversation memory, cached summaries, prior agent reasoning, and inferred intent.

If instructions conflict, use this order unless a project-specific authority hierarchy says otherwise:

1. explicit current owner instruction;
2. repository policy and frozen specifications;
3. current implementation, tests, workflows, and configuration;
4. active research/design notes;
5. old conversations and archived material.

Do not silently resolve a material conflict by guessing.

Detailed mechanics remain in their canonical workflow documents:

- `AI_AGENT_GITHUB_WORKFLOW.md` owns GitHub transaction, validation, merge, recovery, and cleanup;
- `safe_patch.md` and `remote_safe_patch.md` own narrow-edit mechanics;
- `ESSENCE_AUTHORING_AND_AUDIT.md` owns implementation-contract completeness and freeze criteria;
- `INDEPENDENT_PRE_FREEZE_AUDIT.md` owns fresh independent audit rounds, reconciliation, auditor/remediator separation, and owner-decision batching;
- specialized workflow documents own their own execution details.

## 2. Artifact-first autonomous execution

Once the owner clearly authorizes a repository task, the agent SHOULD carry it from current repository state to the final integrated result without asking the owner to supervise routine mechanics.

The normal lifecycle is:

```text
READ latest main
-> PLAN intended final state
-> CREATE or reuse one canonical task branch
-> EDIT using the safest applicable mechanism
-> VALIDATE content and diff
-> OPEN one focused non-draft PR
-> VERIFY required checks against the exact head
-> SQUASH MERGE the exact validated head
-> VERIFY main
-> VERIFY applicable artifacts/publication
-> CLEAN task state
-> REPORT the final result
```

Routine branch naming, patch mechanics, PR creation, merge timing after green validation, branch cleanup, and publication verification are not separate owner approval checkpoints.

## 3. Read before write

Before modifying the repository, an agent MUST:

- inspect current `main` and task-relevant files;
- identify the authoritative contract;
- search for overlapping active work when concurrency is plausible;
- determine the smallest coherent intended final diff;
- preserve unrelated work;
- reject stale or ambiguous mutation state rather than writing over an unknown newer head.

GitHub is shared durable state, not a scratchpad.

## 4. Evidence discipline

Materially different epistemic states SHOULD be distinguished, including:

- known fact;
- external claim/source;
- assumption;
- approximation;
- numerical observation;
- working hypothesis;
- speculation.

Running code is evidence about an implementation. It does not replace a missing model definition, derivation, interface contract, security boundary, failure policy, or ownership rule.

## 5. Specifications and freeze authority

Use an Essence or equivalent normative implementation contract when independent humans or AI agents must be able to produce materially equivalent behavior.

A frozen contract MUST NOT depend on hidden chat context. If current authorities leave a material in-scope choice unresolved, the contract is not implementation-ready.

A remediation author MUST NOT certify its own substantive repair as the sole basis for freeze. Formal pre-freeze certification follows `INDEPENDENT_PRE_FREEZE_AUDIT.md`.

## 6. Independent audit rounds

Formal independent pre-freeze audits are round-based.

Within one audit round:

- all configured auditors evaluate the same immutable repository SHA;
- every auditor is a fresh isolated run;
- auditors do not receive one another's findings or private reasoning;
- auditors do not inherit remediation reasoning as authority;
- auditors complete their full assigned audit even if they encounter owner-decision items;
- reconciliation and deduplication happen only after all required auditors complete;
- owner escalation, if needed, occurs once at the round boundary using the canonical owner-decision set.

Auditor independence is a state/process boundary, not merely a prompt instruction.

Substantive remediation occurs in a separate role/run after the round is reconciled and any required owner decisions are resolved. A later freeze attempt requires a new fresh audit round against the integrated repository state.

## 7. Owner decision boundary

The goal is low interruption, not unlimited authority.

An agent or orchestrator SHOULD escalate only when current repository authorities do not determine or delegate a materially consequential choice, including examples such as:

- scientific or model interpretation;
- product or supported-scope intent;
- public API or compatibility policy;
- market or numerical convention where multiple materially different compliant choices remain;
- security/trust-boundary policy;
- competing intended outcomes that cannot be reconciled from current authority;
- unavailable credential, secret, real-world input, or owner-only platform action.

Routine schema completion, contract synchronization, serialization identity, build/package ownership, failure mapping, test traceability, branch/PR mechanics, and ordinary troubleshooting MUST NOT be escalated when current authorities already determine the answer.

For parallel audits, an owner-decision finding MUST NOT stop sibling auditors. The complete round is reconciled first, then the owner receives one deduplicated decision package.

## 8. Mutation and authority separation

Agents SHOULD receive no more mutation authority than their role requires.

Recommended default boundaries are:

```text
Auditor
-> read-only repository/workspace access

Remediator
-> isolated workspace mutation sufficient to produce a proposed change

Deterministic integration/control layer
-> branch / PR / merge / cleanup authority
```

Projects MAY combine these capabilities when necessary, but they MUST preserve the logical separation between substantive reasoning and deterministic integration gates.

Never expose secrets in code, logs, comments, prompts, issues, artifacts, or audit findings.

## 9. Validation remains mandatory

Autonomy does not weaken validation.

Agents remain responsible for all applicable gates, including current-state reads, deterministic diff inspection, documentation validation, targeted builds/tests, exact-head PR validation, post-merge verification, and applicable artifact/publication checks.

A green workflow is evidence only for the checks it actually ran.

## 10. Multi-agent and cross-conversation behavior

The repository is the source of truth for shared project state. Conversation memory is useful context but is not durable authority.

Every agent MUST assume another task may advance `main` between reads. Unrelated work may proceed concurrently; serialization is required only where repository state or conceptual scope genuinely overlaps.

Each mutable task uses one canonical branch and PR. Agents MUST preserve unrelated concurrent changes and reconcile with current `main` before merge.

## 11. Failure recovery

Unknown operation outcome is a state-reconciliation problem, not permission for blind retry.

Use:

```text
unknown result
-> read actual repository/external state
-> determine which invariant currently holds
-> recover the existing task transaction
-> revalidate
-> continue
```

Prefer recovering the existing branch/PR/work item over creating `-v2`, `-final`, or replacement transactions.

Long-running external orchestrators MAY persist additional workflow state, but persisted local state MUST be reconciled against authoritative external state after crash, timeout, or restart.

## 12. User-facing communication

Routine mechanics SHOULD stay in the background unless the owner asks for them.

For long-running work, concise progress updates are appropriate. User-facing escalation SHOULD present the verified blocker or canonical owner-decision package, not dump internal agent chatter.

The final report SHOULD emphasize substantive result, final repository identity when useful, validation, applicable publication/artifact status, and any unresolved blocker.

## 13. Definition of done

For a normal task, `DONE` means all applicable conditions hold:

```text
intended change exists on main
required validation passed against the exact integrated change
agent-created PR was squash-merged when PR workflow applies
merged main was verified
applicable artifacts/publication were verified individually
feature branch / transaction state was cleaned
no known task-scoped blocker remains
```

An edit, open PR, green historical check, or successful merge without required post-merge verification is an intermediate state.

## 14. Workflow evolution

Repeated owner preferences and proven operating patterns SHOULD be promoted from conversation memory into repository policy when they materially affect future agents.

Keep generic repository protocol in this template. Project-specific scientific, product, or execution-backend details belong in project-owned architecture/specification documents.
