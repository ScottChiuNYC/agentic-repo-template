# Reference Ingestion Workflow

This repository includes an optional GitHub Actions control plane for durable PDF ingestion.

## Components

- `tools/reference_ingest.py`: validates request shape, source version, page ranges, and output coverage.
- `tools/reference_ingest_render.py`: renders page text into the canonical transcript/manifest format.
- `tools/reference_ingest_ocr.sh`: OCR fallback helper.
- `tools/reference_ingest_commit.sh`: commits generated output on a task branch.
- `.github/workflows/reference-ingestion.yml`: executes a source-bound ingestion request with trusted default-branch tooling.
- `.github/workflows/reference-ingestion-control.yml`: owner-only permanent issue that prepares a request PR.

## Lifecycle

```text
PDF committed below ref/
        |
        v
owner/control intent
        |
        v
request branch bound to source blob SHA
        |
        v
trusted executor validates request + source
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
same PR updated with versioned transcript
```

The source PDF remains authoritative. The transcript is a reusable access layer with explicit provenance.

## Control issue

After the control workflow is merged to `main`, it creates or reopens an issue titled `[reference-ingestion-control]`. The repository owner may edit its body to:

```text
[reference-ingestion-intent]
version = 1
source = "ref/example.pdf"
start_page = 1
end_page = 0
```

`end_page = 0` means the final PDF page. The control workflow resolves the exact source blob SHA on `main`, creates a request branch, and opens a `[reference-ingestion]` PR. The privileged executor then performs ingestion using trusted default-branch tooling.

The permanent issue is a control surface, not a place for secrets or research notes.

## When to enable

Keep the subsystem when the project regularly reasons over papers, specifications, reports, or scanned PDFs. Remove the two reference-ingestion workflows and tools if the project will never maintain a reference corpus.
