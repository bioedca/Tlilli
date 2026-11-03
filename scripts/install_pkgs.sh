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

stamp=.cache/install_pkgs.sha256
inputs="scripts/install_pkgs.sh"
[ -f ui/pnpm-lock.yaml ] && inputs="$inputs ui/package.json ui/pnpm-lock.yaml"
[ -f Cargo.lock ] && inputs="$inputs Cargo.lock"

if sha256sum --check --status "$stamp" 2>/dev/null; then
  exit 0
fi

# Delete the old stamp first, so a failed install runs again next session.
rm -f "$stamp"
mkdir -p .cache
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
