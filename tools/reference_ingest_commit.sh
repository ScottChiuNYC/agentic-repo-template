#!/usr/bin/env bash
set -euo pipefail

: "${WORK_ROOT:?}"
: "${OUTPUT_DIR:?}"
: "${HEAD_REF:?}"
: "${HEAD_SHA:?}"

repo="$WORK_ROOT"
git -C "$repo" config user.name 'github-actions[bot]'
git -C "$repo" config user.email '41898282+github-actions[bot]@users.noreply.github.com'

git -C "$repo" add -f -- "$OUTPUT_DIR/transcript.md" "$OUTPUT_DIR/manifest.json"
git -C "$repo" rm -r -- .github/reference-ingestion-request
git -C "$repo" diff --cached --check

mapfile -t changed < <(git -C "$repo" diff --cached --name-only | sort)
expected=(
  '.github/reference-ingestion-request/READY'
  '.github/reference-ingestion-request/request.toml'
  "$OUTPUT_DIR/manifest.json"
  "$OUTPUT_DIR/transcript.md"
)
mapfile -t expected < <(printf '%s\n' "${expected[@]}" | sort)
if [[ "${changed[*]}" != "${expected[*]}" ]]; then
  echo 'REFERENCE_INGEST_REJECTED_STAGED_SHAPE' >&2
  printf 'staged: %s\n' "${changed[@]}" >&2
  exit 3
fi

git -C "$repo" commit -m 'Ingest reference pages' >/dev/null
if [[ -n "$(git -C "$repo" status --porcelain)" ]]; then
  echo 'REFERENCE_INGEST_REJECTED_DIRTY_POST_COMMIT' >&2
  exit 3
fi

remote_sha="$(git -C "$repo" ls-remote origin "refs/heads/${HEAD_REF}" | awk '{print $1}')"
if [[ "$remote_sha" != "$HEAD_SHA" ]]; then
  echo "REFERENCE_INGEST_REJECTED_HEAD_MOVED: expected ${HEAD_SHA}, found ${remote_sha}" >&2
  exit 3
fi

git -C "$repo" push origin "HEAD:refs/heads/${HEAD_REF}"
git -C "$repo" rev-parse HEAD
