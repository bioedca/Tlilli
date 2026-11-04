#!/bin/bash
# Build or serve the docs site locally with the same pinned toolchain docs.yml uses.
#   scripts/docs.sh            build with `mkdocs build --strict` into site/
#   scripts/docs.sh serve      live preview on http://127.0.0.1:8000/Tlilli/
#   scripts/docs.sh <args...>  any other mkdocs subcommand, e.g. `scripts/docs.sh build --verbose`
# The Python packages are installed from docs/requirements.txt (hash-checked) into
# .cache/venv-docs, and reinstalled only when that file changes. Rustdoc (/api) is not
# built here; run `cargo doc --workspace --no-deps` for it.
set -eu

cd "$(dirname "$0")/.."

# Material 9.8 prints its end-of-life notice at every build (see docs.yml).
export NO_MKDOCS_2_WARNING=1

venv=.cache/venv-docs
stamp=$venv/requirements.sha256

if [ ! -x "$venv/bin/mkdocs" ] || ! sha256sum --check --status "$stamp" 2>/dev/null; then
  rm -rf "$venv"
  python3 -m venv "$venv"
  "$venv/bin/pip" install --quiet --require-hashes -r docs/requirements.txt
  sha256sum docs/requirements.txt > "$stamp"
fi

if [ "$#" -eq 0 ]; then
  exec "$venv/bin/mkdocs" build --strict
fi
exec "$venv/bin/mkdocs" "$@"
