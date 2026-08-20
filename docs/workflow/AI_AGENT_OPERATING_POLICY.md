# AI Agent Operating Policy

This document defines repository-level behavior for AI agents. It is intentionally model- and vendor-neutral.

## Authority

Repository state is durable authority. Current files on `main` outrank stale conversation memory, cached summaries, and inferred intent.

If instructions conflict, use this order:

1. explicit current user/owner instruction;
2. repository policy and frozen specifications;
3. current implementation, tests, workflows, and configuration;
4. active research notes;
5. old conversations and archived material.

Do not silently resolve a material conflict by guessing.

## Read before write

Before modifying the repository:

- inspect current state and task-relevant files;
- identify the authoritative contract;
- determine the smallest coherent final diff;
- check whether another branch/PR already owns the same work;
- preserve unrelated work.

GitHub is not a scratchpad. Exploratory reasoning may happen outside the repository; only durable conclusions and intentional artifacts belong in Git.

## Evidence discipline

Label materially different epistemic states:

- known fact;
- external claim/source;
- assumption;
- approximation;
- numerical observation;
- working hypothesis;
- speculation.

Running code is evidence about an implementation. It does not replace a missing model definition, derivation, interface contract, or failure policy.

## Change discipline

- One task should produce one focused branch and one focused pull request.
- Avoid opportunistic refactors unless required for correctness.
- Update documentation in the same task when behavior or interfaces change.
- Prefer deterministic, reviewable transformations over broad autonomous rewrites.
- Reject stale state instead of applying a mutation to a newer unknown head.
- Never expose secrets in code, logs, comments, prompts, issues, or artifacts.

## Specifications

Use an Essence when implementation must be reproducible across independent humans or AI agents.

A frozen Essence is normative. Implementers must not use hidden chat context to fill material gaps. If the specification is insufficient, reopen and amend it before implementation.

See `ESSENCE_AUTHORING_AND_AUDIT.md`.

## External references

When a project relies on PDFs or other stable reference material, prefer repository-backed, source-versioned transcripts over repeatedly re-reading opaque external documents. Preserve provenance and page coverage. Use OCR only when direct text extraction is insufficient.

See `reference_ingestion_protocol.md`.

## Mutation policy

Normal changes use branch/PR workflows. Narrow existing-file edits should prefer Safe Patch when its constraints fit. Connector-only remote edits should use the repository's Remote Safe Patch control plane.

A mutation mechanism must fail closed on ambiguous target, stale head, invalid request shape, oversized diff, protected target, or failed validation.

## Handoff

At the end of substantial work, leave enough durable context that another competent human or AI agent can continue without the current conversation. Update `docs/CURRENT_STATE.md` when project state materially changes.
