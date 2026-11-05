#!/bin/bash
# Tests for scripts/ci.sh (PR-CI-010). Each case runs a copy of ci.sh in a throwaway repository,
# with stub cargo and pnpm first on PATH: the stubs record their command lines and fail on request,
# so no toolchain runs and nothing in the real checkout is touched.
set -euo pipefail

ci="$(cd "$(dirname "$0")/.." && pwd)/ci.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

mkdir "$tmp/bin"
for tool in cargo pnpm; do
  cat >"$tmp/bin/$tool" <<'EOF'
#!/bin/bash
line="$(basename "$0") $*"
echo "$line" >>"$STUB_LOG"
if [[ -n $STUB_FAIL && $line == "$STUB_FAIL"* ]]; then exit "$STUB_FAIL_STATUS"; fi
EOF
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
make_repo "$tmp/full" Cargo.toml ui/package.json
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
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace"
ui_calls="pnpm -C ui install --frozen-lockfile
pnpm -C ui lint
pnpm -C ui typecheck
pnpm -C ui test
pnpm -C ui build"
tauri_calls="pnpm -C ui install --frozen-lockfile
pnpm -C ui tauri build --no-bundle"

check "--help exits 0" "$tmp/full" 0 "" --help
check "no arguments exit 2" "$tmp/full" 2 ""
check "an unknown job exits 2 and runs nothing" "$tmp/full" 2 "" rust no-such-job
check "a pending job exits 2 and runs nothing" "$tmp/full" 2 "" rust commits
check "passing jobs run CI's commands in order" "$tmp/full" 0 "$rust_calls
$ui_calls" rust ui
check "tauri/linux runs CI's no-bundle build" "$tmp/full" 0 "$tauri_calls" tauri/linux
check "missing manifests skip the jobs" "$tmp/bare" 0 "" rust-lint rust-test ui tauri/linux

fail_on="cargo clippy"
check "the first failure stops the run with its status" "$tmp/full" 101 "cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings" rust ui

if [[ $failures -gt 0 ]]; then
  printf '%s test(s) of scripts/ci.sh failed\n' "$failures"
  exit 1
fi
printf 'all tests of scripts/ci.sh passed\n'
