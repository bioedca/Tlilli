#!/bin/bash
# The checks of a pull request's diff in ci.yml (PRD 33 §2), and the size/* label for the same
# count, which the labeler workflow sets from the API's file list. scripts/ci.sh runs the checks.
#   scripts/pr_checks.sh size           the size/limit check (PR-PRQ-020, PR-PRQ-021, PR-GIT-031)
#   scripts/pr_checks.sh contract-sync  the docs/contract-sync check (PR-DOC-001)
#   scripts/pr_checks.sh size-label     print the size/* label (PR-PRQ-022)
# Input from the environment, all optional:
#   PR_BASE, PR_HEAD  the diff is PR_BASE...PR_HEAD (default origin/main...HEAD)
#   PR_FILES          a file of "additions<TAB>deletions<TAB>path" lines to count instead of that diff
#   PR_BRANCH         the head branch (default: the current one); release-plz-* skips CHANGELOG.md
#   PR_LABELS         the PR's labels, comma-separated; PR_BODY: its description
# A failed check prints an ::error:: line and exits 1; bad input exits 2.
set -euo pipefail

usage() { sed -n '4,12p' "$0" | sed 's/^# \{0,1\}//'; }

case "$#:${1-}" in
  1:size | 1:contract-sync | 1:size-label) ;;
  1:-h | 1:--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

cd "$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
base=${PR_BASE:-origin/main}
head=${PR_HEAD:-HEAD}
branch=${PR_BRANCH:-$(git symbolic-ref --short -q HEAD || true)}
status=0

error() { printf '::error::%s\n' "$*"; status=1; }

has_label() { [[ ",${PR_LABELS:-}," == *",$1,"* ]]; }

# The text after "<key>:" on the first line of the description that starts with it, trimmed.
body_value() {
  printf '%s\n' "${PR_BODY:-}" | awk -v key="$1:" 'index($0, key) == 1 && !found {
    v = substr($0, length(key) + 1); gsub(/^[ \t\r]+|[ \t\r]+$/, "", v); print v; found = 1 }'
}

# "additions<TAB>deletions<TAB>path" for each changed file: a renamed file under its new path, a
# binary file with "-" for both counts.
listing() {
  if [[ -n ${PR_FILES:-} ]]; then
    cat "$PR_FILES"
    return
  fi
  local rec rest path
  git diff --numstat -z -M "$base...$head" | while IFS= read -r -d '' rec; do
    rest=${rec#*$'\t'}
    path=${rest#*$'\t'}
    # A rename leaves the path empty and sends the old and the new path as the next two fields.
    [[ -n $path ]] || { IFS= read -r -d '' path && IFS= read -r -d '' path; }
    printf '%s\t%s\t%s\n' "${rec%%$'\t'*}" "${rest%%$'\t'*}" "$path"
  done
}

# Hand-written changed lines (PR-PRQ-020): additions and deletions, without the lockfiles, insta
# snapshots, the generated MCP reference, fixtures, images and binary files, nor CHANGELOG.md in a
# release-plz pull request.
changed_lines() {
  local add del path total=0
  while IFS=$'\t' read -r add del path; do
    case $path in
      '' | Cargo.lock | */Cargo.lock | pnpm-lock.yaml | */pnpm-lock.yaml | *.snap | docs/reference/mcp/* | \
        tests/fixtures/* | *.svg | *.png | *.jpg | *.jpeg | *.gif | *.webp | *.ico | *.icns)
        continue
        ;;
      CHANGELOG.md | */CHANGELOG.md) [[ $branch != release-plz-* ]] || continue ;;
    esac
    [[ $add == - ]] || total=$((total + add + del))
  done <<<"$files"
  echo "$total"
}

# At most 400 lines, unless the PR has size:override and a "Size override: <reason>" line. No file
# over 2 MiB; at most 50 MiB in tests/fixtures/ and in docs/assets/, the places for binary assets.
check_size() {
  local lines caps line
  lines=$(changed_lines)
  printf 'size/limit: %s hand-written changed lines (cap 400)\n' "$lines"
  if ((lines > 400)); then
    if has_label size:override && [[ -n $(body_value 'Size override') ]]; then
      printf 'size/limit: over the cap with size:override (PR-PRQ-021)\n'
    else
      error "$lines hand-written changed lines exceed the cap of 400 (PR-PRQ-020): split the pull" \
        "request, or add a 'Size override: <reason>' line to its description and then the" \
        "size:override label (PR-PRQ-021)"
    fi
  fi
  # ls-tree -l prints "<mode> <type> <object> <size><TAB><path>" for each file at the head.
  caps=$(git ls-tree -r -l "$head" | awk -F '\t' '
    { split($1, f, / +/); size = f[4] + 0
      if (size > 2097152) printf "%s is %.1f MiB, over the 2 MiB file cap (PR-GIT-031)\n", $2, size / 1048576
      if ($2 ~ /^tests\/fixtures\//) dir["tests/fixtures/"] += size
      if ($2 ~ /^docs\/assets\//) dir["docs/assets/"] += size }
    END { for (d in dir) if (dir[d] > 52428800)
      printf "%s holds %.1f MiB, over the 50 MiB directory cap (PR-GIT-031)\n", d, dir[d] / 1048576 }')
  while IFS= read -r line; do [[ -z $line ]] || error "$line"; done <<<"$caps"
}

# A change to a contract path changes docs/ too, or the PR has docs:not-needed and a "Docs not
# needed because: <reason>" line (PR-DOC-001, D-024).
check_contract_sync() {
  local add del path contract="" docs=false
  while IFS=$'\t' read -r add del path; do
    case $path in
      crates/tlilli-mcp/src/tools/* | crates/tlilli-mcp/src/resources/* | crates/tlilli-mcp/src/prompts/* | \
        skills/* | crates/tlilli-core/src/storage/* | crates/tlilli-cli/src/* | src-tauri/tauri.conf.json)
        contract="$contract $path"
        ;;
      docs/*) docs=true ;;
    esac
  done <<<"$files"
  if [[ -z $contract ]]; then
    printf 'docs/contract-sync: no contract path changed\n'
  elif $docs; then
    printf 'docs/contract-sync: contract paths changed, and docs/ with them:%s\n' "$contract"
  elif has_label docs:not-needed && [[ -n $(body_value 'Docs not needed because') ]]; then
    printf 'docs/contract-sync: docs:not-needed: %s\n' "$(body_value 'Docs not needed because')"
  else
    error "contract paths changed but nothing under docs/:$contract. Update the docs, or add a" \
      "'Docs not needed because: <reason>' line to the description and then the docs:not-needed" \
      "label (PR-DOC-001, PR-PRQ-031)"
  fi
}

# PR-PRQ-022: XS up to 50 lines, S up to 150, M up to 400, L up to 800, XL above.
size_label() {
  local lines
  lines=$(changed_lines)
  if ((lines <= 50)); then echo size/XS
  elif ((lines <= 150)); then echo size/S
  elif ((lines <= 400)); then echo size/M
  elif ((lines <= 800)); then echo size/L
  else echo size/XL; fi
}

if [[ -z ${PR_FILES:-} ]]; then
  for rev in "$base" "$head"; do
    git rev-parse -q --verify "$rev^{commit}" >/dev/null ||
      { printf 'pr_checks.sh: no commit %s: fetch it, or set PR_BASE and PR_HEAD\n' "$rev" >&2; exit 2; }
  done
fi
files=$(listing)

case $1 in
  size) check_size ;;
  contract-sync) check_contract_sync ;;
  size-label) size_label ;;
esac
exit "$status"
