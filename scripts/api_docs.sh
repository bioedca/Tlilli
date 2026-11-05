#!/bin/bash
# Build the rustdoc of the workspace into site/api, the /api/ part of the docs site (PRD 35 §1),
# with a landing page that lists the crates, because cargo doc writes no workspace-level index.
# Used by docs.yml (Pages), the docs-build job of ci.yml and scripts/ci.sh docs-build.
set -euo pipefail

cd "$(dirname "$0")/.."

cargo doc --workspace --no-deps
mkdir -p site/api
cp -R target/doc/. site/api/
if [ ! -f site/api/index.html ]; then
  {
    echo '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    echo '<title>Tlilli API documentation</title></head><body>'
    echo '<h1>Tlilli API documentation</h1><ul>'
    for crate in site/api/*/index.html; do
      name=$(basename "$(dirname "$crate")")
      echo "<li><a href=\"$name/index.html\">$name</a></li>"
    done
    echo '</ul><p><a href="../">Back to the documentation</a></p></body></html>'
  } >site/api/index.html
fi
