# Start Here

Use this file as the stable onboarding path for humans and AI agents.

## Source-of-truth order

1. `AGENTS.md`
2. `docs/workflow/AI_AGENT_OPERATING_POLICY.md`
3. `docs/WRITING_AND_MARKDOWN_RULES.md`
4. `docs/CURRENT_STATE.md`
5. frozen or active implementation specifications
6. current code, tests, workflows, and configuration
7. archived notes and old conversations

When sources conflict, prefer the higher-authority current repository artifact unless an explicit newer decision says otherwise.

## New repository bootstrap

Prefer the automated VPS bootstrap in `bootstrap/new_repo.sh`. It creates the repository from this template, applies non-inherited GitHub settings, optionally installs Google Drive Actions secrets from an external protected file, and verifies the resulting configuration. See `docs/workflow/repository_settings.md`.

After creating a repository from this template:

1. replace all placeholders in `docs/CURRENT_STATE.md`;
2. remove optional infrastructure that the project will not use;
3. confirm the bootstrap verification passed, or apply the manual settings in `docs/workflow/repository_settings.md` if automation was not used;
4. configure Google Drive publication only when the project needs external PDF delivery;
5. create project-specific architecture/research/specification files rather than overloading workflow documentation;
6. keep stable decisions in Git, not only in chat.

## During work

- Read before writing.
- Update durable state when a decision becomes stable.
- Keep exploratory notes separate from normative specifications.
- Use an Essence when independent implementers need to produce materially equivalent behavior.
- Reopen a frozen Essence explicitly when its contract must change.

## Before handoff

Leave the repository understandable without the current conversation:

- current status is accurate;
- decisions and unresolved questions are explicit;
- implementation and docs agree;
- validation commands/results are recorded where appropriate;
- no hidden conversational assumption is required to continue.
