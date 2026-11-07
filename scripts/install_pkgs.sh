#!/bin/bash
# Cloud-only dependency install, run by the SessionStart hook in .claude/settings.json.
# On a laptop it exits at once. In a cloud session it installs the UI's packages and fetches
# crates, but only when a lockfile (or this script) changed since the last successful run,
# so resumed sessions start in a second.
set -u

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 1
mkdir -p .cache

# cargo-nextest runs the Rust tests (scripts/ci.sh rust-test), at the version ci.yml installs. Its
# build takes minutes, so it runs in the background and the session starts at once; the output
# goes to .cache/cargo-nextest.log. The check comes before the stamp's, so a session whose
# lockfiles have not changed still gets it. flock -n skips the build while an earlier session's
# build still holds the lock; cargo install is a no-op once that build has finished.
NEXTEST_VERSION=0.9.150
if [ -f Cargo.lock ] && ! command -v cargo-nextest >/dev/null 2>&1; then
  nohup flock -n .cache/cargo-nextest.lock \
    cargo install --locked "cargo-nextest@$NEXTEST_VERSION" >>.cache/cargo-nextest.log 2>&1 &
fi

# tauri-driver starts the app for the desktop smoke suite (scripts/ci.sh e2e/smoke), at the version
# ci.yml installs. It builds in the background the same way, logging to .cache/tauri-driver.log.
TAURI_DRIVER_VERSION=2.1.0
if [ -f src-tauri/Cargo.toml ] && ! command -v tauri-driver >/dev/null 2>&1; then
  nohup flock -n .cache/tauri-driver.lock \
    cargo install --locked "tauri-driver@$TAURI_DRIVER_VERSION" >>.cache/tauri-driver.log 2>&1 &
fi

stamp=.cache/install_pkgs.sha256
inputs="scripts/install_pkgs.sh"
[ -f ui/pnpm-lock.yaml ] && inputs="$inputs ui/package.json ui/pnpm-lock.yaml"
[ -f Cargo.lock ] && inputs="$inputs Cargo.lock"

if sha256sum --check --status "$stamp" 2>/dev/null; then
  exit 0
fi

# Delete the old stamp first, so a failed install runs again next session.
rm -f "$stamp"
ok=1

if [ -f ui/pnpm-lock.yaml ]; then
  pnpm -C ui install --frozen-lockfile || ok=0
fi

if [ -f Cargo.lock ]; then
  CARGO_NET_GIT_FETCH_WITH_CLI=true cargo fetch || ok=0
fi

if [ "$ok" = 1 ]; then
  # shellcheck disable=SC2086
  sha256sum $inputs > "$stamp" || rm -f "$stamp"
fi

exit 0
