#!/usr/bin/env bash
set -euo pipefail

: "${REPO_ROOT:?}"
: "${SOURCE:?}"
: "${START_PAGE:?}"
: "${END_PAGE:?}"
: "${OCR_DIR:?}"
: "${NATIVE_TEXT:?}"

if [[ ! "$START_PAGE" =~ ^[0-9]+$ || ! "$END_PAGE" =~ ^[0-9]+$ ]]; then
  echo 'REFERENCE_INGEST_REJECTED_PAGE_RANGE' >&2
  exit 3
fi

mkdir -p "$OCR_DIR"
pdftotext -f "$START_PAGE" -l "$END_PAGE" -layout "$REPO_ROOT/$SOURCE" "$NATIVE_TEXT"

for ((page=START_PAGE; page<=END_PAGE; page++)); do
  image="${RUNNER_TEMP:-/tmp}/reference-page-${page}"
  pdftoppm -f "$page" -l "$page" -singlefile -r 220 -gray -png "$REPO_ROOT/$SOURCE" "$image"
  printf -v page_id '%04d' "$page"
  tesseract "${image}.png" "$OCR_DIR/page-${page_id}" -l eng --psm 3 txt
  rm -f "${image}.png"
done
