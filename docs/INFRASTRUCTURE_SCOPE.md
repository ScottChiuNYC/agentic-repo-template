# Infrastructure Scope

This template is the reusable layer extracted from multiple real repositories. The boundary is capability-based, not a file-for-file copy of any one project.

## Included

- durable repository memory and onboarding;
- model-agnostic AI agent operating policy;
- exact-head GitHub mutation discipline;
- Essence authoring, freeze, reopen, and independent audit;
- Safe Patch and Remote Safe Patch control planes;
- source-versioned reference PDF ingestion with OCR fallback;
- Markdown/math fail-closed validation;
- whole-repository CodeBinder PDF build and structural validation;
- optional Google Drive publication.

## Intentionally excluded

- domain models, algorithms, strategies, experiments, and research notes;
- project-specific package/build skeletons;
- calibration, benchmarking, or application CI tied to one codebase;
- legacy content auto-normalization that rewrites documentation automatically;
- personal credentials, secret values, private storage identifiers, and organization-specific assumptions.

## Rule for future additions

A capability belongs here when it is useful across unrelated long-lived human/AI projects and can be expressed without importing a consumer repository's domain assumptions.

A capability stays in a consumer repository when its semantics depend on that project's model, runtime, deployment, data, or business domain.
