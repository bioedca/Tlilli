#!/usr/bin/env bash
# Install the Tauri 2 Linux prerequisites, run by action.yml. The .deb files in ~/.cache/tauri-debs
# (restored from the cache) go into apt's archive first, so apt downloads only what changed.
set -euo pipefail

# webkit2gtk-driver and xvfb serve the e2e/smoke job: WebKitWebDriver, which tauri-driver drives,
# and the virtual display it runs under (the runner image has xvfb; the list makes it explicit).
packages=(libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev
  libayatana-appindicator3-dev librsvg2-dev webkit2gtk-driver xvfb)
cache=~/.cache/tauri-debs
archives=/var/cache/apt/archives

mkdir -p "$cache"
find "$cache" -maxdepth 1 -name '*.deb' -exec sudo cp -t "$archives" {} +
sudo timeout 300 apt-get update -o Acquire::Retries=3
sudo apt-get autoclean # drops cached versions the package index no longer offers

# A slow mirror once kept a download going for half an hour, so each try stops after 8 minutes.
# Stopping a download is safe: apt keeps the finished files and fetches the rest on the next try.
for try in 1 2 3; do
  if sudo timeout 480 apt-get install -y --download-only -o Acquire::Retries=3 "${packages[@]}"; then
    break
  fi
  if ((try == 3)); then
    echo "::error::apt-get could not download the Tauri prerequisites in three tries" >&2
    exit 1
  fi
  echo "::warning::apt-get download try $try stopped; trying again"
done

# Copy the files for the cache before installing, in case a dpkg hook cleans the archive.
rm -rf "$cache" && mkdir -p "$cache"
find "$archives" -maxdepth 1 -name '*.deb' -exec cp -t "$cache" {} +
sudo apt-get install -y --no-download "${packages[@]}"
