# Reference Ingestion Protocol

Reference ingestion turns stable PDF sources into repository-backed, source-versioned transcripts that humans and AI agents can reuse without repeatedly re-reading opaque documents.

## Principle

Prefer direct text extraction. Use OCR only when the source is scanned or extraction quality is insufficient.

Every transcript must preserve:

- repository-relative source path;
- exact Git blob SHA of the PDF;
- page range;
- page-by-page coverage;
- transcript hash;
- extraction/OCR method.

## Request shape

```text
.github/reference-ingestion-request/
├── request.toml
└── READY
```

`READY` must contain `ready`.

`request.toml`:

```toml
version = 1
source = "ref/example.pdf"
expected_source_blob_sha = "<40-hex git blob sha>"
start_page = 1
end_page = 0
```

`end_page = 0` means the final page. A single request may ingest at most 100 pages by default.

## Output layout

```text
ref/transcripts/<source-slug>/source-<blob-prefix>/pages-0001-0010/
├── transcript.md
└── manifest.json
```

A new source blob produces a new versioned output directory; old transcripts remain auditable.

## Transcript format

Each page appears exactly once:

```markdown
## PDF page 1

...

## PDF page 2

...
```

The manifest records expected and transcribed page lists plus the SHA-256 hash of `transcript.md`.

## Validation

The ingestion engine fails closed when:

- the request shape is wrong;
- the source is outside `ref/` or is not a PDF;
- the source blob moved after the request was prepared;
- the page range is invalid or too large;
- output for the same source version/range already exists;
- any page is missing or duplicated;
- the transcript hash does not match the manifest.

## OCR

OCR is a fallback, not the default. The workflow may use `pdftotext` first and invoke OCR tooling only when required by the source. OCR output remains provenance-tagged; it is not treated as a perfect copy of the source.

## Commit discipline

Generated transcripts should land through a focused branch/PR and remain tied to the exact source blob SHA. Do not overwrite an older transcript when a PDF changes.
