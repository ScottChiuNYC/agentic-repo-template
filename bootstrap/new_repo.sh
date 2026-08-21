#!/usr/bin/env bash
set -euo pipefail

readonly DEFAULT_TEMPLATE="${AGENTIC_TEMPLATE_REPO:-ScottChiuNYC/agentic-repo-template}"
readonly DEFAULT_SECRETS_FILE="${AGENTIC_BOOTSTRAP_SECRETS_FILE:-$HOME/.config/agentic-repo-bootstrap/google-drive.env}"
readonly -a DRIVE_SECRET_NAMES=(
  GOOGLE_DRIVE_CLIENT_ID
  GOOGLE_DRIVE_CLIENT_SECRET
  GOOGLE_DRIVE_REFRESH_TOKEN
  GOOGLE_DRIVE_FOLDER_ID
)

usage() {
  cat <<'USAGE'
Create a repository from the Agentic Repo Template and apply settings that
GitHub templates cannot inherit.

Usage:
  bash bootstrap/new_repo.sh <repo-name> [options]

Options:
  --private                 Create a private repository (default).
  --public                  Create a public repository.
  --owner OWNER             Repository owner. Defaults to the authenticated user.
  --template OWNER/REPO     Template repository.
  --secrets-file PATH       Dotenv file containing the four Google Drive secrets.
  --no-drive-secrets        Do not install Google Drive repository secrets.
  --require-drive-secrets   Fail before repository creation if the secrets file is absent.
  -h, --help                Show this help.

Environment overrides:
  AGENTIC_TEMPLATE_REPO
  AGENTIC_BOOTSTRAP_SECRETS_FILE

The secrets file is never sourced as shell code. It must contain exactly the
four supported Google Drive secret names, one NAME=value entry per line, plus
optional blank lines or comments.
USAGE
}

fail() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

info() {
  printf '==> %s\n' "$*"
}

require_command() {
  command -v "$1" >/dev/null 2>&1 || fail "required command not found: $1"
}

validate_secrets_file() {
  local file="$1"
  local mode=""
  local raw line key value allowed required
  declare -A seen=()

  [[ -f "$file" ]] || fail "secrets file is not a regular file: $file"
  [[ ! -L "$file" ]] || fail "secrets file must not be a symlink: $file"

  if mode="$(stat -c '%a' "$file" 2>/dev/null)" && [[ -n "$mode" ]]; then
    if (( (8#$mode & 077) != 0 )); then
      fail "secrets file must not be group/world accessible; run: chmod 600 '$file'"
    fi
  fi

  while IFS= read -r raw || [[ -n "$raw" ]]; do
    line="${raw#"${raw%%[![:space:]]*}"}"
    [[ -z "$line" || "${line:0:1}" == "#" ]] && continue

    if [[ ! "$line" =~ ^([A-Z][A-Z0-9_]*)=(.*)$ ]]; then
      fail "invalid secrets-file entry; expected NAME=value without shell syntax"
    fi

    key="${BASH_REMATCH[1]}"
    value="${BASH_REMATCH[2]}"
    [[ -n "$value" && "$value" != '""' && "$value" != "''" ]] || fail "secret $key has an empty value"

    allowed=false
    for required in "${DRIVE_SECRET_NAMES[@]}"; do
      if [[ "$key" == "$required" ]]; then
        allowed=true
        break
      fi
    done
    [[ "$allowed" == true ]] || fail "unexpected secret name in $file: $key"
    [[ -z "${seen[$key]:-}" ]] || fail "duplicate secret name in $file: $key"
    seen[$key]=1
  done < "$file"

  for required in "${DRIVE_SECRET_NAMES[@]}"; do
    [[ -n "${seen[$required]:-}" ]] || fail "missing required secret in $file: $required"
  done
}

repo_name=""
visibility="private"
owner=""
template="$DEFAULT_TEMPLATE"
secrets_file="$DEFAULT_SECRETS_FILE"
install_drive_secrets=true
require_drive_secrets=false

while (( $# > 0 )); do
  case "$1" in
    --private)
      visibility="private"
      shift
      ;;
    --public)
      visibility="public"
      shift
      ;;
    --owner)
      (( $# >= 2 )) || fail "--owner requires a value"
      owner="$2"
      shift 2
      ;;
    --template)
      (( $# >= 2 )) || fail "--template requires OWNER/REPO"
      template="$2"
      shift 2
      ;;
    --secrets-file)
      (( $# >= 2 )) || fail "--secrets-file requires a path"
      secrets_file="$2"
      shift 2
      ;;
    --no-drive-secrets)
      install_drive_secrets=false
      shift
      ;;
    --require-drive-secrets)
      require_drive_secrets=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    --*)
      fail "unknown option: $1"
      ;;
    *)
      [[ -z "$repo_name" ]] || fail "only one repository name may be supplied"
      repo_name="$1"
      shift
      ;;
  esac
done

[[ -n "$repo_name" ]] || { usage >&2; exit 2; }
[[ "$repo_name" != */* ]] || fail "pass a bare repository name and use --owner separately"
[[ "$repo_name" =~ ^[A-Za-z0-9._-]+$ ]] || fail "repository name contains unsupported characters"
[[ "$template" == */* && "$template" != */*/* ]] || fail "--template must be OWNER/REPO"

require_command gh
require_command grep
require_command stat

gh auth status >/dev/null 2>&1 || fail "GitHub CLI is not authenticated; run 'gh auth login' first"

if [[ -z "$owner" ]]; then
  owner="$(gh api user --jq '.login')"
fi
[[ "$owner" =~ ^[A-Za-z0-9-]+$ ]] || fail "invalid owner: $owner"

target="$owner/$repo_name"

if gh repo view "$target" >/dev/null 2>&1; then
  fail "repository already exists; refusing to modify it: $target"
fi

template_is_template="$(gh repo view "$template" --json isTemplate --jq '.isTemplate')"
[[ "$template_is_template" == "true" ]] || fail "configured template is not a GitHub template repository: $template"

use_drive_secrets=false
if [[ "$install_drive_secrets" == true ]]; then
  if [[ -f "$secrets_file" ]]; then
    validate_secrets_file "$secrets_file"
    use_drive_secrets=true
  elif [[ "$require_drive_secrets" == true ]]; then
    fail "required secrets file does not exist: $secrets_file"
  else
    info "Google Drive secrets file not found; Drive publication will remain disabled"
  fi
fi

info "Creating $target from $template ($visibility)"
gh repo create "$target" "--$visibility" --template "$template" >/dev/null

info "Applying repository settings"
gh repo edit "$target" \
  --delete-branch-on-merge \
  --enable-squash-merge >/dev/null

# Keep the default GITHUB_TOKEN read-only. Individual workflows must request only
# the write permissions they need. The second field maps to the GitHub UI option
# "Allow GitHub Actions to create and approve pull requests."
gh api \
  --method PUT \
  "repos/$target/actions/permissions/workflow" \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=true >/dev/null

if [[ "$use_drive_secrets" == true ]]; then
  info "Installing Google Drive Actions secrets"
  gh secret set --repo "$target" --app actions --env-file "$secrets_file" >/dev/null
fi

info "Verifying bootstrap state"
[[ "$(gh repo view "$target" --json deleteBranchOnMerge --jq '.deleteBranchOnMerge')" == "true" ]] \
  || fail "verification failed: delete-branch-on-merge is not enabled"
[[ "$(gh repo view "$target" --json squashMergeAllowed --jq '.squashMergeAllowed')" == "true" ]] \
  || fail "verification failed: squash merge is not enabled"
[[ "$(gh api "repos/$target/actions/permissions/workflow" --jq '.can_approve_pull_request_reviews')" == "true" ]] \
  || fail "verification failed: Actions cannot create/approve pull requests"

if [[ "$use_drive_secrets" == true ]]; then
  secret_names="$(gh secret list --repo "$target" --app actions --json name --jq '.[].name')"
  for required in "${DRIVE_SECRET_NAMES[@]}"; do
    grep -Fxq "$required" <<<"$secret_names" \
      || fail "verification failed: repository secret is missing: $required"
  done
fi

repo_url="$(gh repo view "$target" --json url --jq '.url')"
printf '\nRepository bootstrap complete: %s\n' "$repo_url"
if [[ "$use_drive_secrets" == false ]]; then
  printf 'Google Drive secrets were not installed. PDF publication will keep the GitHub artifact and skip Drive.\n'
fi
