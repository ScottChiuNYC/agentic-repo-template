# Agentic Repo Template (ART)

ART is a **minimal Copier template for agent-operable repositories**.

Its job is deliberately small:

1. provide an `AGENTS.md` **Skill Router** that sends agents to the right mature workflow only when that workflow is relevant;
2. provide the repository-native **CodeBinder PDF** skill and publication infrastructure that ART still owns.

ART does not try to reimplement every useful agent capability.

## Copier

ART is designed to be applied alongside an independent language/build-infrastructure Copier template. For example, one project can independently inherit Python/C++ build infrastructure from one template and ART from this template.

```bash
copier copy gh:ScottChiuNYC/agentic-repo-template .
```

Downstream Copier metadata is stored independently in:

```text
.copier-answers.art.yml
```

## Skill routing

Generated repositories route agents to these canonical external skills rather than vendoring them:

- GitHub repository contribution / PR workflow:
  https://github.com/github/awesome-copilot/blob/main/skills/make-repo-contribution/SKILL.md
- Implementation Contract Convergence:
  https://github.com/ScottChiuNYC/implementation-convergence/blob/main/skills/implementation-contract-convergence/SKILL.md
- Contract-to-Code Convergence:
  https://github.com/ScottChiuNYC/implementation-convergence/blob/main/skills/contract-to-code-convergence/SKILL.md
- General PDF work and scanned-PDF OCR:
  https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md

The generated `AGENTS.md` performs repository-curated automatic skill routing: classify the task, then load only the relevant skill.

## ART-owned capability

ART currently owns one repo-local skill:

```text
.agents/skills/codebinder-pdf/
```

It contains the CodeBinder publication rules, optional Google Drive upload, Markdown/math rendering guardrails, deterministic helpers, and regression tests. Heavy PDF dependencies are built once into ART's GHCR-hosted CodeBinder builder image; generated workflows pin that image by immutable digest rather than reinstalling TeX/Sphinx on every run.

## Deliberate omissions

ART v1 does **not** carry forward the Archive's Steward framework, Durable Execution protocol, reference-ingestion/OCR stack, learning workflow, or custom Safe Patch / Remote Safe Patch infrastructure.

The default policy is to use mature external skills and native runtime edit/patch capabilities first. If repeated real-world use demonstrates a concrete gap, ART can add the smallest missing capability later.

## Design principle

> ART teaches agents where to go instead of trying to teach them everything.
