# AI Agent Instructions

## Read first

Before substantial work, read in order:

1. `docs/workflow/AI_AGENT_OPERATING_POLICY.md`
2. `docs/workflow/DURABLE_EXECUTION_PROTOCOL.md`
3. `docs/WRITING_AND_MARKDOWN_RULES.md`
4. `docs/START_HERE.md`
5. `docs/CURRENT_STATE.md`
6. task-relevant specifications and implementation files

Before GitHub mutation, also read `docs/workflow/AI_AGENT_GITHUB_WORKFLOW.md`.
For narrow edits, read `docs/workflow/safe_patch.md`; for connector-only mutation, also read `docs/workflow/remote_safe_patch.md`.
For reference ingestion, read `docs/workflow/reference_ingestion_protocol.md`.
For learning or relearning a technical topic with the repository owner, read `docs/workflow/learning.md`.
Before authoring, remediating, auditing, freezing, or reopening an Essence, read `docs/workflow/ESSENCE_AUTHORING_AND_AUDIT.md`.
For a formal fresh independent pre-freeze audit, reconciliation, or remediation cycle, follow `docs/workflow/INDEPENDENT_PRE_FREEZE_AUDIT.md` as the canonical execution protocol and use `docs/workflow/AUDIT_ROLE_BOOTSTRAP.md` for the minimum role bootstrap contract.

`main` is the shared project source of truth. Repository state outranks stale chat history.

## Working rules

- One problem, one focused outcome, one branch, one pull request.
- Distinguish facts, assumptions, approximations, numerical observations, working hypotheses, and speculation.
- Do not treat executable code as a substitute for a missing mathematical or behavioral contract.
- Keep implementation and documentation synchronized when behavior, interfaces, workflows, or configuration change.
- Do not use GitHub as a scratchpad. Read current state, plan the final diff, then write.
- Before final-head validation, re-read and re-evaluate the repository's canonical current-state artifact (normally `docs/CURRENT_STATE.md`). Update it in the same task when the change materially alters recorded phase/status, completed milestones/capabilities, active decisions, blockers/open questions, immediate next work, authoritative artifacts, or validation/deployment/publication state; otherwise leave it unchanged.
- Converge semantic edits on the task branch before opening the PR when possible; expensive validation should target the intended final head rather than every intermediate edit.
- Long tasks MUST leave durable repository/workflow checkpoints sufficient for a new run to resume from exact state without private scratch reasoning.
- Executor choice is runtime policy: human-supervised ChatGPT, coding agents, API workers, or an orchestrator follow the same repository authority, role boundaries, validation, and Definition of Done.
- Do not write directly to `main`, except when bootstrapping an empty repository that has no commit from which a branch can be created.
- Prefer Safe Patch for narrow edits to tracked UTF-8 files.
- A frozen Essence is a human/AI executable implementation contract; never fill its gaps from private conversational context.
- Formal independent auditors and substantive remediators MUST be separate roles/runs.
- Parallel auditors in the same audit round MUST evaluate the same immutable repository SHA and MUST NOT receive one another's findings or remediation reasoning.
- Audit freshness means audit-relevant authority isolation, not total model amnesia; ordinary ambient context may exist but is non-authoritative and MUST NOT repair a repository contract gap.
- Formal audit/remediation handoff MUST use durable raw-result slots, canonical reconciliation, and durable owner decisions rather than manual copying of private chat transcripts.
- Owner escalation happens only after a complete audit round has been reconciled into a canonical owner-decision set.
- Concision must not remove required assumptions, algorithms, interfaces, failure modes, security boundaries, or validation criteria.

## Merge and publication

- Merge only the exact PR head SHA that passed the required validation.
- Prefer squash merge for focused task branches.
- After merge, re-read `main`, verify cleanup, and verify any applicable publication workflow.
- PDF behavior is documented in `docs/workflow/codebinder_pdf_pipeline.md`.
