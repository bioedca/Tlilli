#!/bin/bash
# Tests for scripts/api_docs.sh. Each case runs a copy of the script in a throwaway repository with
# a stub cargo first on PATH: `cargo doc` writes two crates' pages into the target directory the
# stub's `cargo metadata` names, or fails on request, so no toolchain runs.
set -euo pipefail

script="$(cd "$(dirname "$0")/.." && pwd)/api_docs.sh"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

mkdir "$tmp/bin"
cat >"$tmp/bin/cargo" <<'EOF'
#!/bin/bash
case $1 in
  doc)
    if [[ -n $STUB_DOC_FAIL ]]; then exit 101; fi
    for crate in alpha beta; do
      mkdir -p "$STUB_TARGET/doc/$crate"
      echo "$crate" >"$STUB_TARGET/doc/$crate/index.html"
    done
    if [[ -n $STUB_ROOT_INDEX ]]; then echo root >"$STUB_TARGET/doc/index.html"; fi
    ;;
  metadata) printf '{"packages":[],"target_directory":"%s","version":1}\n' "$STUB_TARGET" ;;
  *) exit 2 ;;
esac
EOF
chmod +x "$tmp/bin/cargo"

failures=0

# run_case <name> <repo> [VAR=value]...: a fresh repository holding the script, run with the
# stub; leaves the exit status in $status.
run_case() {
  local repo=$2
  shift 2
  rm -rf "$repo"
  mkdir -p "$repo/scripts"
  cp "$script" "$repo/scripts/api_docs.sh"
  status=0
  env STUB_DOC_FAIL= STUB_ROOT_INDEX= "$@" PATH="$tmp/bin:$PATH" \
    "$repo/scripts/api_docs.sh" >"$tmp/out" 2>&1 || status=$?
}

# expect <name> <condition>...: one result line for the case.
expect() {
  local name=$1
  shift
  if "$@"; then
    printf 'ok   %s\n' "$name"
  else
    printf 'FAIL %s (exit %s)\noutput:\n' "$name" "$status"
    cat "$tmp/out"
    failures=$((failures + 1))
  fi
}

copied_with_list() {
  local api=$1
  [[ $status == 0 && -f $api/alpha/index.html && -f $api/beta/index.html ]] &&
    grep -q 'href="alpha/index.html"' "$api/index.html" &&
    grep -q 'href="beta/index.html"' "$api/index.html"
}

repo="$tmp/custom"
run_case custom "$repo" STUB_TARGET="$tmp/elsewhere"
expect "copies from the target directory cargo metadata names, and lists the crates" \
  copied_with_list "$repo/site/api"
expect "does not read ./target when the target directory is elsewhere" test ! -e "$repo/target"

repo="$tmp/root-index"
run_case root-index "$repo" STUB_TARGET="$tmp/root-target" STUB_ROOT_INDEX=1
expect "keeps an index page that cargo doc wrote itself" \
  grep -qx root "$repo/site/api/index.html"

repo="$tmp/fail"
run_case fail "$repo" STUB_TARGET="$tmp/fail-target" STUB_DOC_FAIL=1
expect "a failing cargo doc stops the script with its status and writes nothing" \
  test "$status" = 101 -a ! -e "$repo/site"

if [[ $failures -gt 0 ]]; then
  printf '%s test(s) of scripts/api_docs.sh failed\n' "$failures"
  exit 1
fi
printf 'all tests of scripts/api_docs.sh passed\n'
