# Agentic Repo Template (ART)

ART is a minimal Copier template that equips an existing repository with:

- a curated `AGENTS.md` skill router;
- a repo-local CodeBinder PDF skill and publication workflow;
- optional Google Drive publication;
- Markdown/math rendering guardrails for the CodeBinder pipeline.

ART deliberately references mature external skills instead of vendoring or reimplementing them.

## Copier

ART is designed to be applied alongside an independent language/build-infrastructure Copier template.

```bash
copier copy gh:ScottChiuNYC/agentic-repo-template .
```

Downstream Copier metadata is stored in:

```text
.copier-answers.art.yml
```

## Design principle

> ART teaches agents where to go instead of trying to teach them everything.

External skills are routed from `AGENTS.md` and loaded only when relevant. Repository-native CodeBinder behavior is packaged as a local skill under `.agents/skills/codebinder-pdf/`.
