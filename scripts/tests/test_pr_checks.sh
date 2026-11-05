#!/bin/bash
# Tests for scripts/pr_checks.sh. Each repository is a throwaway one: `main` holds the script and a
# 300-line file, and the pull request's commits go on the `feature` branch, which stays checked out.
set -euo pipefail

script="$(cd "$(dirname "$0")/.." && pwd)/pr_checks.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

failures=0
n=0

git_() { git -C "$repo" -c user.name=test -c user.email=test@example.com "$@"; }

new_repo() {
  n=$((n + 1))
  repo="$tmp/repo$n"
  mkdir -p "$repo/scripts"
  git init -q -b main "$repo"
  cp "$script" "$repo/scripts/pr_checks.sh"
  seq 300 >"$repo/old.txt"
  git_ add -A
  git_ commit -qm base
  git_ switch -qc feature
}

# commit_lines <count> <path>: commit a file of that many lines.
commit_lines() {
  mkdir -p "$(dirname "$repo/$2")"
  seq "$1" >"$repo/$2"
  git_ add -A
  git_ commit -qm "add $2"
}

# expect <name> <status> <text> <check> [VAR=value]...: run the check with only the given PR_*
# variables set, then want that exit status and that text in the output.
expect() {
  local name=$1 want=$2 text=$3 check=$4 status=0
  shift 4
  env -u PR_HEAD -u PR_FILES -u PR_BRANCH -u PR_LABELS -u PR_BODY PR_BASE=main "$@" \
    "$repo/scripts/pr_checks.sh" "$check" >"$tmp/out" 2>&1 || status=$?
  if [[ $status == "$want" ]] && grep -qF -- "$text" "$tmp/out"; then
    printf 'ok   %s\n' "$name"
  else
    printf 'FAIL %s: exit %s (want %s and "%s")\noutput:\n' "$name" "$status" "$want" "$text"
    cat "$tmp/out"
    failures=$((failures + 1))
  fi
}

new_repo
commit_lines 380 src/a.rs
for path in Cargo.lock ui/pnpm-lock.yaml tests/fixtures/f.txt docs/reference/mcp/t.md src/x.snap; do
  commit_lines 900 "$path"
done
git_ mv old.txt moved.txt
git_ commit -qm "move old.txt"
expect "counts hand-written lines only, and nothing for a rename" 0 "380 hand-written" size
commit_lines 21 src/b.rs
expect "fails above 400 lines" 1 "401 hand-written changed lines exceed" size
expect "size:override without a reason still fails" 1 "exceed the cap" size \
  PR_LABELS=area/ci,size:override "PR_BODY=Size override: "
body=$'- [ ] ≤ 400 lines or `Size override: <reason>` below\r\nSize override:\r\nSize override: generated tables\r\n'
expect "passes with size:override and a reason line" 0 "over the cap with size:override" size \
  PR_LABELS=size:override,area/ci "PR_BODY=$body"
expect "a reason line without the label still fails" 1 "exceed the cap" size "PR_BODY=$body"
expect "labels 401 lines size/L" 0 "size/L" size-label
commit_lines 500 CHANGELOG.md
expect "counts CHANGELOG.md in other pull requests" 0 "size/XL" size-label
expect "skips CHANGELOG.md in a release-plz pull request" 0 "size/L" size-label \
  PR_BRANCH=release-plz-2026-11-05

printf '30\t20\tsrc/a.rs\n-\t-\tlogo.bin\n7\t0\tCargo.lock\n' >"$tmp/files.tsv"
expect "reads a listing from PR_FILES" 0 "size/XS" size-label "PR_FILES=$tmp/files.tsv"
expect "a missing base exits 2" 2 "no commit nope" size PR_BASE=nope
commit_lines 1 $'src/tab\tname.rs'
expect "a path with a tab exits 2" 2 "a path with a tab or a newline" size
git_ rm -q $'src/tab\tname.rs'
git_ commit -qm "drop the tab"

# Zero-filled files: 26 of exactly 2 MiB in tests/fixtures/, under names git quotes unless told
# not to, and one byte more for big.bin.
new_repo
mkdir -p "$repo/tests/fixtures"
for i in $(seq 26); do head -c 2097152 /dev/zero >"$repo/tests/fixtures/figuré$i.bin"; done
head -c 2097153 /dev/zero >"$repo/big.bin"
git_ add -A
git_ commit -qm "add binaries"
expect "fails on a file over 2 MiB" 1 "big.bin is 2.0 MiB, over the 2 MiB file cap" size
expect "fails on more than 50 MiB in tests/fixtures/" 1 "tests/fixtures/ holds 52.0 MiB" size

new_repo
commit_lines 3 src/main.rs
expect "passes when no contract path changed" 0 "no contract path changed" contract-sync
commit_lines 3 skills/tlilli-review/SKILL.md
expect "fails on a contract path without docs" 1 "nothing under docs/: skills/tlilli-review/SKILL.md" \
  contract-sync
expect "passes with docs:not-needed and a reason line" 0 "docs:not-needed: wording only" \
  contract-sync PR_LABELS=docs:not-needed $'PR_BODY=## Docs\nDocs not needed because: wording only\n'
commit_lines 2 docs/skills.md
expect "passes when docs/ changes too" 0 "and docs/ with them" contract-sync

new_repo
commit_lines 30 skills/tlilli-review/SKILL.md
git_ switch -q main && git_ merge -q --ff-only feature && git_ switch -q feature
git_ mv skills/tlilli-review/SKILL.md archive.md
git_ commit -qm "move the skill out"
expect "counts a rename out of a contract path" 1 "nothing under docs/: skills/tlilli-review/SKILL.md" \
  contract-sync

# commits and build-each, with stubs: commitlint rejects a message or title that says BAD and prints
# whether the Dependabot switch is on; cargo fails in a tree that holds a file named broken.
stub="$tmp/stub"
mkdir -p "$stub"
# shellcheck disable=SC2016 # the stubs' own code, expanded when they run
printf '%s\n' '#!/bin/bash' 'echo "dependabot=${TLILLI_COMMITLINT_DEPENDABOT:-0}"' \
  'if [[ $1 == --from ]]; then git log --format=%B "$2..$4"; else cat; fi | { ! grep -q BAD; }' >"$stub/commitlint"
printf '%s\n' '#!/bin/bash' '[[ ! -e broken ]]' >"$stub/cargo"
chmod +x "$stub/commitlint" "$stub/cargo"
ok=("COMMITLINT=$stub/commitlint" PR_BRANCH=claude/p0-20-checks)
body=$'## Summary\n## Requirements\nRequirements: none\n## Changes\n## Testing\n## Docs\n## Review pipeline\n'
body+=$'- Codex local rounds: 0\n- CodeRabbit: pending\n- Greptile: n/a\n- Gated paths touched: none\n## Checklist\n'
new_repo
commit_lines 3 src/a.rs
expect "passes when every commit builds" 0 "cargo check at" build-each "PATH=$stub:$PATH"
commit_lines 3 broken
git_ rm -q broken
git_ commit -qm "fix the build"
expect "passes a pull request that follows the rules" 0 "commits: 3 commits" commits "${ok[@]}" \
  "PR_TITLE=ci(ci): add a check" "PR_BODY=$body"
expect "fails a title that commitlint rejects" 1 "the title is not" commits "${ok[@]}" PR_TITLE=BAD PR_BODY=
expect "fails a description without a section" 1 "lacks '## Docs'" commits "${ok[@]}" \
  "PR_TITLE=ci(ci): add a check" "PR_BODY=${body/'## Docs'/}"
expect "fails a branch name outside PR-GIT-003" 1 "branch 'Feature/x'" commits "${ok[@]}" PR_BRANCH=Feature/x
expect "lints Dependabot without the header cap and skips its description" 0 "dependabot=1" commits \
  "${ok[@]}" PR_AUTHOR='dependabot[bot]' PR_BRANCH=dependabot/cargo/serde-1.0.2 "PR_TITLE=chore(deps): bump" PR_BODY=
expect "fails a commit that does not build on its own" 1 "does not build on its own" build-each "PATH=$stub:$PATH"
[[ $(git_ worktree list | wc -l) == 1 ]] || { printf 'FAIL build-each left a worktree\n'; failures=$((failures + 1)); }
git_ switch -qc side main
git_ commit -q --allow-empty -m "side"
git_ switch -q feature
git_ merge -q --no-ff -m "BAD merge" side
for i in $(seq 8); do git_ commit -q --allow-empty -m "chore(ci): step $i"; done
expect "fails a bad message" 1 "a commit message breaks" commits "${ok[@]}"
expect "fails 13 commits" 1 "13 commits, over 10" commits "${ok[@]}"
expect "names the merge commit" 1 "merge commits $(git_ rev-parse HEAD~8)" commits "${ok[@]}"
expect "skips the build above 10 commits" 0 "over 10: not checked" build-each "PATH=$stub:$PATH"

if [[ $failures -gt 0 ]]; then
  printf '%s test(s) of scripts/pr_checks.sh failed\n' "$failures"
  exit 1
fi
printf 'all tests of scripts/pr_checks.sh passed\n'
