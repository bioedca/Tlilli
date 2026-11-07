#!/bin/bash
# Tests for scripts/ci.sh (PR-CI-010). Each case runs a copy of ci.sh in a throwaway repository,
# with stub cargo and pnpm first on PATH: the stubs record their command lines and fail on request,
# so no toolchain runs and nothing in the real checkout is touched.
set -euo pipefail

ci="$(cd "$(dirname "$0")/.." && pwd)/ci.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

mkdir "$tmp/bin"
for tool in cargo pnpm zizmor actionlint; do
  cat >"$tmp/bin/$tool" <<'EOF'
#!/bin/bash
line="$(basename "$0")${*:+ $*}"
echo "$line" >>"$STUB_LOG"
if [[ -n $STUB_FAIL && $line == "$STUB_FAIL"* ]]; then exit "$STUB_FAIL_STATUS"; fi
EOF
  chmod +x "$tmp/bin/$tool"
done
# The jobs check that the cargo subcommands they call are installed; the cargo stub runs them.
for tool in cargo-deny cargo-nextest; do
  printf '#!/bin/bash\n' >"$tmp/bin/$tool"
  chmod +x "$tmp/bin/$tool"
done

# make_repo <dir> <file>...: a repository root holding ci.sh and the given (empty) manifests.
make_repo() {
  local dir=$1 file
  shift
  mkdir -p "$dir/scripts"
  cp "$ci" "$dir/scripts/ci.sh"
  for file in "$@"; do
    mkdir -p "$(dirname "$dir/$file")"
    : >"$dir/$file"
  done
}
make_repo "$tmp/full" Cargo.toml ui/package.json .github/workflows/ci.yml
# protocol-ref/drift calls the repository's own generator script; this one only records the call.
# shellcheck disable=SC2016 # $* and $STUB_LOG expand when the stub runs
printf '#!/bin/bash\necho "gen_reference.sh $*" >>"$STUB_LOG"\n' >"$tmp/full/scripts/gen_reference.sh"
chmod +x "$tmp/full/scripts/gen_reference.sh"
make_repo "$tmp/bare"

failures=0
fail_on=""

# check <name> <repo> <want status> <want calls> <ci.sh args>...
check() {
  local name=$1 repo=$2 want_status=$3 want_calls=$4 status=0 calls
  shift 4
  : >"$tmp/log"
  STUB_LOG="$tmp/log" STUB_FAIL="$fail_on" STUB_FAIL_STATUS=101 PATH="$tmp/bin:$PATH" \
    "$repo/scripts/ci.sh" "$@" >"$tmp/out" 2>&1 || status=$?
  calls=$(cat "$tmp/log")
  if [[ $status == "$want_status" && $calls == "$want_calls" ]]; then
    printf 'ok   %s\n' "$name"
  else
    printf 'FAIL %s: exit %s (want %s)\ncalls:\n%s\nwant:\n%s\noutput:\n' \
      "$name" "$status" "$want_status" "$calls" "$want_calls"
    cat "$tmp/out"
    failures=$((failures + 1))
  fi
}

rust_calls="cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo deny check
cargo doc --workspace --no-deps
cargo nextest run --workspace --all-features
cargo nextest run -p tlilli-core --no-default-features
cargo test --doc --workspace"
ui_calls="pnpm -C ui install --frozen-lockfile
pnpm -C ui exec biome ci .
pnpm -C ui typecheck
pnpm -C ui exec vitest run --coverage
pnpm -C ui build
pnpm -C ui exec playwright test --grep @smoke"
tauri_calls="pnpm -C ui install --frozen-lockfile
pnpm -C ui tauri build --no-bundle"

check "--help exits 0" "$tmp/full" 0 "" --help
check "no arguments exit 2" "$tmp/full" 2 ""
check "an unknown job exits 2 and runs nothing" "$tmp/full" 2 "" rust no-such-job
check "a pending job exits 2 and runs nothing" "$tmp/full" 2 "" rust e2e/smoke
check "passing jobs run CI's commands in order" "$tmp/full" 0 "$rust_calls
$ui_calls" rust ui
check "tauri/linux runs CI's no-bundle build" "$tmp/full" 0 "$tauri_calls" tauri/linux
check "the drift and workflow checks run CI's commands" "$tmp/full" 0 "gen_reference.sh --check
zizmor --offline --min-severity low .github/workflows
actionlint" protocol-ref/drift workflows/zizmor
check "missing manifests skip the jobs" "$tmp/bare" 0 "" rust-lint rust-test ui tauri/linux \
  protocol-ref/drift workflows/zizmor

# all_case <name> <want in the last line> <ci.sh args>...: `all` in a repository with no manifests,
# where the docs, diff, scripts and reuse jobs find stubs, so nothing real runs; checks the closing
# line.
stubs="scripts/docs.sh scripts/pr_checks.sh scripts/tests/test_ci.sh scripts/tests/test_api_docs.sh
  scripts/tests/test_pr_checks.sh .cache/venv-reuse-6.3.0/bin/reuse"
# shellcheck disable=SC2086 # one path per word
make_repo "$tmp/stubs" $stubs
for stub in $stubs; do chmod +x "$tmp/stubs/$stub"; done
printf 'import unittest\n\n\nclass Stub(unittest.TestCase):\n    def test_stub(self):\n        pass\n' \
  >"$tmp/stubs/scripts/tests/test_stub.py"
all_case() {
  local name=$1 want=$2 status=0 last
  shift 2
  : >"$tmp/log"
  STUB_LOG="$tmp/log" STUB_FAIL="" STUB_FAIL_STATUS=101 PATH="$tmp/bin:$PATH" \
    "$tmp/stubs/scripts/ci.sh" "$@" >"$tmp/out" 2>&1 || status=$?
  last=$(tail -n 1 "$tmp/out")
  if [[ $status == 0 && $last == "$want" ]]; then
    printf 'ok   %s\n' "$name"
  else
    printf 'FAIL %s: exit %s, last line:\n%s\nwant:\n%s\noutput:\n' "$name" "$status" "$last" "$want"
    cat "$tmp/out"
    failures=$((failures + 1))
  fi
}
pending="e2e/smoke"
all_case "all names reuse as not run" "ci.sh: not run: reuse (only when named), $pending (pending)" all
all_case "all reuse does not name reuse as not run" "ci.sh: not run: $pending (pending)" all reuse

fail_on="cargo clippy"
check "the first failure stops the run with its status" "$tmp/full" 101 "cargo fmt --all --check
cargo clippy --workspace --all-targets --all-features -- -D warnings" rust ui

if [[ $failures -gt 0 ]]; then
  printf '%s test(s) of scripts/ci.sh failed\n' "$failures"
  exit 1
fi
printf 'all tests of scripts/ci.sh passed\n'
