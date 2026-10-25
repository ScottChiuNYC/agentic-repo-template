# Agent Instructions

This repository is the canonical **Agentic Repo Template (ART)**.

## Read first

Before structural, Docker, CodeBinder, Copier, or publication changes, read:

1. `README.md`;
2. `docs/ecosystem-architecture.md`;
3. the focused workflow, Dockerfile, template file, skill, and tests for the behavior being changed.

The ecosystem document is the authority for cross-repository ownership and change propagation.

## Ownership

ART owns the generated agent router, repository-local CodeBinder PDF skill/publication workflow, builder Dockerfile, pinned GHCR image digest, and `.codebinderignore.d/art` fragment.

ART does not own:

- the Python/C++ build/package skeleton from `copier-pypackage-cpp`;
- ICC/C2C protocol semantics from `implementation-convergence`;
- CodeBinder discovery/conversion semantics from `codebinder`.

Do not collapse independently owned Copier answers files or CodeBinder ignore fragments into shared generated files.

## Change discipline

- Keep reusable behavior in its canonical upstream repository.
- When CodeBinder behavior changes, merge/test CodeBinder first, pin its new commit in the Dockerfile, build/test a new GHCR image, pin the new image digest in ART, then propagate ART by genuine Copier updates.
- When only generated ART behavior changes, do not rebuild the builder image unless its contents must change.
- Use immutable image digests as downstream authority; do not replace them with floating tags.
- Validate cross-repository behavior with a real consumer when the change crosses a repository boundary.
- Prefer focused branches and squash merges after applicable validation passes.
