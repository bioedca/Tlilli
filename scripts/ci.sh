#!/bin/bash
# Run the CI jobs locally with the commands CI runs (PR-CI-010, PR-TST-018, PRD 33 §2).
#   scripts/ci.sh <job>...   run the named jobs in the order given; `all` runs every job in CI order
#   scripts/ci.sh --help     list the jobs and their commands
# The first failing command stops the run, and the script exits with that command's status.
# The jobs are those of .github/workflows/ci.yml but the build/* matrix, plus `scripts` (the tests
# of these dev scripts) and `reuse lint` from docs/dev/licensing.md, which joins `all` once CI runs
# it. No toolchain is installed: rustup, cargo-nextest, cargo-deny, pnpm, Node 22 and python3 must
# be on PATH, as in the cloud sandbox and the devcontainer; e2e/smoke also needs tauri-driver,
# WebKitWebDriver and xvfb-run.
set -euo pipefail

cd "$(dirname "$0")/.."

# Installed into .cache/ on first use; task 20 installs the same release in CI.
REUSE_VERSION=6.3.0

# JOBS follows the PRD 33 §2 table; scripts (the tests of these dev scripts) has no row there and
# runs last. EXTRA jobs run only when named: they are not in CI yet (reuse has no row in the table
# either).
JOBS="rust-lint rust-test ui docs-build commits size/limit docs/contract-sync protocol-ref/drift"
JOBS="$JOBS workflows/zizmor tauri/linux e2e/smoke scripts"
EXTRA="reuse"

usage() {
  cat <<'EOF'
Usage: scripts/ci.sh <job>... | all | --help

Jobs, in CI order (docs/prd/33-ci-cd.md §2):
  rust-lint           cargo fmt --all --check; cargo clippy --workspace --all-targets --all-features
                      -- -D warnings; cargo deny check; cargo doc --workspace --no-deps (warnings denied)
  rust-test           cargo nextest run --workspace --all-features; the same for tlilli-core with
                      --no-default-features; cargo test --doc --workspace (CI adds coverage)
  ui                  pnpm -C ui install --frozen-lockfile; biome ci .; typecheck; vitest run
                      --coverage; build; playwright test --grep @smoke (needs a Chromium)
  docs-build          scripts/docs.sh (mkdocs build --strict); scripts/api_docs.sh (rustdoc into
                      site/api) when Cargo.toml exists
  commits             scripts/pr_checks.sh commits: commitlint on the commits since origin/main,
                      their count, merge commits and the branch name (PR_TITLE and PR_BODY add the
                      title and the description); then cargo check at each commit (build-each)
  size/limit          scripts/pr_checks.sh size: hand-written changed lines against origin/main
                      (cap 400) and the file-size caps
  docs/contract-sync  scripts/pr_checks.sh contract-sync: a change to a contract path also changes
                      docs/ (PR_LABELS and PR_BODY stand in for the PR's labels and description)
  protocol-ref/drift  scripts/gen_reference.sh --check: the generated pages under docs/reference/
                      against their generators
  workflows/zizmor    zizmor --offline --min-severity low .github/workflows; actionlint (zizmor
                      1.32.0 and actionlint 1.7.12, the releases CI pins)
  tauri/linux         pnpm -C ui install --frozen-lockfile; pnpm -C ui tauri build --no-bundle
  e2e/smoke           pnpm -C ui install --frozen-lockfile; pnpm -C ui tauri build --debug
                      --no-bundle; xvfb-run -a pnpm -C ui test:e2e:desktop (the tauri-driver suite;
                      needs tauri-driver, WebKitWebDriver and xvfb-run)
  scripts             the tests of ci.sh, api_docs.sh, pr_checks.sh and gen_fixtures.py under
                      scripts/tests (not in ci.yml yet)
  rust                alias: rust-lint, then rust-test
  all                 alias: every job above, in that order

Runs only when named, until CI runs it:
  reuse               reuse lint (docs/dev/licensing.md)

Not mirrored: the build/* matrix (run on Ready), the coverage that rust-test collects under
cargo-llvm-cov in CI, and codecov/patch/* (the Codecov service). A Rust or UI job is skipped when
Cargo.toml or ui/package.json is missing; tauri/linux and e2e/smoke need both.
EOF
}

job=""
status=""
summary=""

# Print a command, run it, and stop the whole run with its status if it fails.
run() {
  printf '\n==> %s\n' "$*"
  "$@" || fail "$?" "$*"
}

fail() {
  printf '\nci.sh: job %s failed (exit %s): %s\n' "$job" "$1" "$2" >&2
  exit "$1"
}

need() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'ci.sh: job %s needs %s on PATH (%s)\n' "$job" "$1" "$2" >&2
    exit 1
  }
}

skip() {
  printf 'ci.sh: no %s, so %s is skipped\n' "$1" "$job"
  status=skipped
}

job_rust_lint() {
  [ -f Cargo.toml ] || { skip Cargo.toml; return 0; }
  need cargo "rustup; rust-toolchain.toml picks the channel"
  need cargo-deny "cargo install cargo-deny --locked"
  run cargo fmt --all --check
  run cargo clippy --workspace --all-targets --all-features -- -D warnings
  run cargo deny check
  run env RUSTDOCFLAGS="-D warnings" cargo doc --workspace --no-deps
}

job_rust_test() {
  [ -f Cargo.toml ] || { skip Cargo.toml; return 0; }
  need cargo "rustup; rust-toolchain.toml picks the channel"
  need cargo-nextest "cargo install cargo-nextest --locked; a cloud session builds it at start, see .cache/cargo-nextest.log"
  run cargo nextest run --workspace --all-features
  run cargo nextest run -p tlilli-core --no-default-features
  run cargo test --doc --workspace
}

job_ui() {
  [ -f ui/package.json ] || { skip ui/package.json; return 0; }
  need pnpm "the version in the packageManager field of ui/package.json"
  run pnpm -C ui install --frozen-lockfile
  run pnpm -C ui exec biome ci .
  run pnpm -C ui typecheck
  run pnpm -C ui exec vitest run --coverage
  run pnpm -C ui build
  # Playwright's own Chromium (pnpm -C ui exec playwright install chromium), or TLILLI_PW_CHROMIUM.
  run pnpm -C ui exec playwright test --grep @smoke
}

# The docs-build job: the strict MkDocs build, then rustdoc once the workspace exists.
job_docs_build() {
  need python3 "3.13, the version docs/requirements.txt was compiled with"
  run scripts/docs.sh
  if [ -f Cargo.toml ]; then
    need cargo "rustup; rust-toolchain.toml picks the channel"
    run scripts/api_docs.sh
  fi
}

# The checks of a pull request's commits and diff, on the current branch against origin/main.
job_commits() {
  run scripts/pr_checks.sh commits
  run scripts/pr_checks.sh build-each
}
job_size_limit() { run scripts/pr_checks.sh size; }
job_contract_sync() { run scripts/pr_checks.sh contract-sync; }

# The generated reference pages under docs/reference/ against their generators (PR-DOC-003).
job_protocol_ref_drift() {
  [ -f Cargo.toml ] || { skip Cargo.toml; return 0; }
  need cargo "rustup; rust-toolchain.toml picks the channel"
  run scripts/gen_reference.sh --check
}

# The workflows' own lint, with the audits CI runs: zizmor offline, then actionlint.
job_workflows_zizmor() {
  [ -d .github/workflows ] || { skip .github/workflows; return 0; }
  need zizmor "zizmor 1.32.0, e.g. pip install zizmor==1.32.0"
  need actionlint "actionlint 1.7.12, from its GitHub release"
  run zizmor --offline --min-severity low .github/workflows
  run actionlint
}

# The compile check of the full app: the UI build, then the release shell with the UI embedded,
# without bundling or signing.
job_tauri_linux() {
  [ -f Cargo.toml ] || { skip Cargo.toml; return 0; }
  [ -f ui/package.json ] || { skip ui/package.json; return 0; }
  need cargo "rustup; rust-toolchain.toml picks the channel"
  need pnpm "the version in the packageManager field of ui/package.json"
  run pnpm -C ui install --frozen-lockfile
  run pnpm -C ui tauri build --no-bundle
}

# The desktop smoke suite: the debug app with the UI embedded, which tauri-driver starts and drives
# through WebKitWebDriver under a virtual display (Linux only).
job_e2e_smoke() {
  [ -f Cargo.toml ] || { skip Cargo.toml; return 0; }
  [ -f ui/package.json ] || { skip ui/package.json; return 0; }
  need cargo "rustup; rust-toolchain.toml picks the channel"
  need pnpm "the version in the packageManager field of ui/package.json"
  need tauri-driver "cargo install --locked tauri-driver@2.1.0, the release CI installs"
  need WebKitWebDriver "the webkit2gtk-driver package"
  need xvfb-run "the xvfb package"
  run pnpm -C ui install --frozen-lockfile
  run pnpm -C ui tauri build --debug --no-bundle
  run xvfb-run -a pnpm -C ui test:e2e:desktop
}

# The dev scripts' own tests: bash and python3 only, no network.
job_scripts() {
  need python3 "for the gen_fixtures.py tests"
  run python3 -B -m unittest discover -s scripts/tests -p 'test_*.py'
  run scripts/tests/test_ci.sh
  run scripts/tests/test_api_docs.sh
  run scripts/tests/test_pr_checks.sh
}

job_reuse() {
  need python3 "for the reuse virtual environment"
  local venv=".cache/venv-reuse-$REUSE_VERSION"
  if [ ! -x "$venv/bin/reuse" ]; then
    rm -rf "$venv"
    run python3 -m venv "$venv"
    run "$venv/bin/pip" install --quiet "reuse==$REUSE_VERSION"
  fi
  run "$venv/bin/reuse" lint
}

run_job() {
  job=$1
  status=passed
  local start=$SECONDS
  printf '\n=== %s\n' "$job"
  case $job in
    rust-lint) job_rust_lint ;;
    rust-test) job_rust_test ;;
    ui) job_ui ;;
    docs-build) job_docs_build ;;
    commits) job_commits ;;
    size/limit) job_size_limit ;;
    docs/contract-sync) job_contract_sync ;;
    protocol-ref/drift) job_protocol_ref_drift ;;
    workflows/zizmor) job_workflows_zizmor ;;
    tauri/linux) job_tauri_linux ;;
    e2e/smoke) job_e2e_smoke ;;
    scripts) job_scripts ;;
    reuse) job_reuse ;;
    *) fail 2 "no such job" ;;
  esac
  printf '=== %s %s in %ss\n' "$job" "$status" "$((SECONDS - start))"
  summary="$summary $job:$status"
}

if [ "$#" -eq 0 ]; then
  usage >&2
  exit 2
fi

# Expand the aliases and check every name before running anything.
selected=""
for arg in "$@"; do
  case $arg in
    -h | --help | help)
      usage
      exit 0
      ;;
    all) selected="$selected $JOBS" ;;
    rust) selected="$selected rust-lint rust-test" ;;
    *)
      case " $JOBS $EXTRA " in
        *" $arg "*) selected="$selected $arg" ;;
        *)
          printf 'ci.sh: unknown job %s (scripts/ci.sh --help lists the jobs)\n' "$arg" >&2
          exit 2
          ;;
      esac
      ;;
  esac
done

for name in $selected; do
  run_job "$name"
done

printf '\nci.sh: done:%s\n' "$summary"
# After `all`, name what it left out: the EXTRA jobs not also named.
case " $* " in
  *" all "*)
    unnamed=""
    for name in $EXTRA; do
      case " $selected " in
        *" $name "*) ;;
        *) unnamed="$unnamed $name" ;;
      esac
    done
    if [ -n "$unnamed" ]; then
      printf 'ci.sh: not run:%s (only when named)\n' "$unnamed"
    fi
    ;;
  *) ;;
esac
