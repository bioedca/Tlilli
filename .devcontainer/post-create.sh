#!/usr/bin/env bash
# postCreateCommand of .devcontainer/devcontainer.json (bootstrap task 31, D-044).
# Installs the Tauri 2 Linux prerequisites and xvfb, then the project's packages when the
# lockfiles exist. Idempotent: run `bash .devcontainer/post-create.sh` again after a failed
# first start, or after checking out a branch that adds ui/ or Cargo.lock.
set -euo pipefail

cd "$(dirname "$0")/.."

# Tauri 2 prerequisites for Ubuntu 24.04, the same list as .github/workflows/ci.yml, plus:
# pkg-config, which the -sys crates use to locate webkit2gtk; xvfb for the WebDriver tests
# (CLAUDE.md: `xvfb-run -a pnpm -C ui test:e2e`); webkit2gtk-driver, the WebDriver that
# tauri-driver talks to on Linux.
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev \
  libayatana-appindicator3-dev librsvg2-dev pkg-config \
  xvfb webkit2gtk-driver

# UI packages, then Playwright's Chromium with its system libraries, when ui/ exists
# (bootstrap task 13). `--frozen-lockfile` is what CI runs.
if [ -f ui/pnpm-lock.yaml ]; then
  pnpm -C ui install --frozen-lockfile
  if [ -x ui/node_modules/.bin/playwright ]; then
    pnpm -C ui exec playwright install --with-deps chromium
  fi
fi

# Warm the crates.io index and download the dependency sources, when the workspace exists
# (bootstrap task 12), so the first `cargo build` only compiles.
if [ -f Cargo.lock ]; then
  cargo fetch
fi
