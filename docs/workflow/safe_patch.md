# Safe Patch

Safe Patch is a narrow, fail-closed editor for one existing tracked UTF-8 file.

Use it when the intended change is an exact replacement and broad repository write access is unnecessary.

## Guarantees

`tools/safe_patch.py` rejects the operation when:

- the repository is not a Git working tree;
- HEAD is detached;
- the current branch is `main` or `master`;
- `--write` is requested without the exact expected HEAD SHA;
- HEAD moved since the request was prepared;
- the target escapes the repository, is missing, untracked, or already dirty;
- the exact old-text anchor is missing or appears more than once;
- the diff exceeds the configured changed-line budget;
- Python, JSON, TOML, or Markdown validation fails.

Writes are atomic. Post-write validation failure restores the original file.

## Usage

Create two UTF-8 snippet files containing the exact old and replacement text.

Preview:

```bash
python tools/safe_patch.py replace \
  --path path/to/file.py \
  --old-file /tmp/old.txt \
  --new-file /tmp/new.txt
```

Apply:

```bash
python tools/safe_patch.py replace \
  --path path/to/file.py \
  --old-file /tmp/old.txt \
  --new-file /tmp/new.txt \
  --expected-head "$(git rev-parse HEAD)" \
  --write
```

Inspect guards without mutation:

```bash
python tools/safe_patch.py doctor
```

## Non-goals

Safe Patch is not a general refactoring engine, merge tool, or permission bypass. If the change spans files, requires fuzzy matching, or changes safety-critical patch infrastructure, use a normal branch/PR workflow.
