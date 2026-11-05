#!/usr/bin/env bash
# Regenerates the generated reference pages under docs/reference/ (PR-DOC-003): the MCP protocol
# reference (mcp/) and the JSON Schemas (schemas/). Each of those files says that it is
# generated; never edit one by hand.
#
#   scripts/gen_reference.sh           rewrite the pages in place
#   scripts/gen_reference.sh --check   regenerate into a scratch directory and exit 1 when the
#                                      committed pages differ (the protocol-ref/drift check)
set -euo pipefail

usage() { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; }

check=false
case "$#:${1-}" in
  0:) ;;
  1:--check) check=true ;;
  1:-h | 1:--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

# The repository that holds this script, wherever it is called from.
cd "$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
committed=docs/reference
# Generate into a scratch directory, so a failed run leaves the committed pages untouched.
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
tlilli() { cargo run --quiet --locked -p tlilli-cli -- "$@"; }
tlilli mcp schema --markdown "$out/mcp"
tlilli schema dump "$out/schemas"

status=0
for path in mcp schemas; do
  if "$check"; then
    # CRLF is folded as in the `reference` test, for checkouts that convert line endings.
    diff -r -u --strip-trailing-cr "$committed/$path" "$out/$path" || status=1
  else
    # Replace the whole directory, so a page the generator no longer writes goes away.
    rm -rf "${committed:?}/$path"
    mv "$out/$path" "$committed/$path"
  fi
done
if [[ $status -ne 0 ]]; then
  echo "docs/reference/ is out of date: run scripts/gen_reference.sh and commit the result" >&2
fi
exit "$status"
