# AI Agent Instructions

## Read first

Before substantial work, read in order:

1. `docs/workflow/AI_AGENT_OPERATING_POLICY.md`
2. `docs/WRITING_AND_MARKDOWN_RULES.md`
3. `docs/START_HERE.md`
4. `docs/CURRENT_STATE.md`
5. task-relevant specifications and implementation files

Before GitHub mutation, also read `docs/workflow/AI_AGENT_GITHUB_WORKFLOW.md`.
For narrow edits, read `docs/workflow/safe_patch.md`; for connector-only mutation, also read `docs/workflow/remote_safe_patch.md`.
For reference ingestion, read `docs/workflow/reference_ingestion_protocol.md`.
For learning or relearning a technical topic with the repository owner, read `docs/workflow/learning.md`.
Before authoring, auditing, freezing, or reopening an Essence, read `docs/workflow/ESSENCE_AUTHORING_AND_AUDIT.md`.

`main` is the shared project source of truth. Repository state outranks stale chat history.

## Working rules

- One problem, one focused outcome, one branch, one pull request.
- Distinguish facts, assumptions, approximations, numerical observations, working hypotheses, and speculation.
- Do not treat executable code as a substitute for a missing mathematical or behavioral contract.
- Keep implementation and documentation synchronized when behavior, interfaces, workflows, or configuration change.
- Do not use GitHub as a scratchpad. Read current state, plan the final diff, then write.
- Do not write directly to `main`, except when bootstrapping an empty repository that has no commit from which a branch can be created.
- Prefer Safe Patch for narrow edits to tracked UTF-8 files.
- A frozen Essence is a human/AI executable implementation contract; never fill its gaps from private conversational context.
- Concision must not remove required assumptions, algorithms, interfaces, failure modes, or validation criteria.

## Merge and publication

- Merge only the exact PR head SHA that passed the required validation.
- Prefer squash merge for focused task branches.
- After merge, re-read `main` and verify any applicable publication workflow.
- PDF behavior is documented in `docs/workflow/codebinder_pdf_pipeline.md`.
