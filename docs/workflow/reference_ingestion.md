# Reference Ingestion Workflow

This repository includes an optional GitHub Actions control plane for durable PDF ingestion.

## Components

- `tools/reference_ingest.py`: validates request shape, source version, page ranges, and output coverage.
- `tools/reference_ingest_render.py`: renders page text into the canonical transcript/manifest format.
- `tools/reference_ingest_ocr.sh`: OCR fallback helper.
- `tools/reference_ingest_commit.sh`: commits generated output on a task branch.
- `.github/workflows/reference-ingestion.yml`: executes a prepared ingestion request.
- `.github/workflows/reference-ingestion-control.yml`: connector-facing control workflow.

## Lifecycle

```text
PDF committed below ref/
        |
        v
prepare request bound to source blob SHA
        |
        v
validate request + page range
        |
        v
extract text; OCR only if needed
        |
        v
render transcript + manifest
        |
        v
validate complete page coverage
        |
        v
focused PR with versioned transcript
```

The source PDF remains authoritative. The transcript is a reusable access layer with explicit provenance.

## When to enable

Keep the subsystem when the project regularly reasons over papers, specifications, reports, or scanned PDFs. Remove the two reference-ingestion workflows and tools if the project will never maintain a reference corpus.
