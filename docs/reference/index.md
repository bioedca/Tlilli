# Reference

Reference pages are for looking things up: what a tool, resource, prompt, schema, command or shortcut is and does, stated once and precisely. They describe; they do not advise (see [How-to guides](../how-to/index.md)).

Most of this section is generated and never hand-edited (`PR-DOC-003`). The `tlilli` command produces it from the running code, and every generated file carries a header comment saying so. `scripts/gen_reference.sh` runs the generators and rewrites the pages; `scripts/gen_reference.sh --check`, and the `reference` test that `cargo test` runs for `crates/tlilli-cli`, fail when a committed page differs from the generator's output. The `protocol-ref/drift` CI job, which runs the same check, arrives with the `ci.yml` rewrite (bootstrap task 20).

Until the surfaces they document exist, the generated pages are skeletons that say so: the MCP pages and the tool-input schemas fill in with v0.2, the canonical JSON schema with v0.1, the style-sheet schema with v0.4 and the skill reference with v0.2. The command reference is complete: it is rendered from the command's own argument parser.

| Page | Generator | Source of truth |
| --- | --- | --- |
| [`mcp/tools.md`](mcp/tools.md), [`mcp/resources.md`](mcp/resources.md), [`mcp/prompts.md`](mcp/prompts.md) | `tlilli mcp schema --markdown` | the MCP server's schema (`crates/tlilli-mcp`) |
| `schemas/*.json` | `tlilli schema dump` | canonical JSON, style sheet and tool-input schemas (`crates/tlilli-core`) |
| [`cli.md`](cli.md) | `tlilli --help-markdown` | the clap command tree (`crates/tlilli-cli`) |
| [`skills.md`](skills.md) | `tlilli skills build --docs` | the skill sources under `skills/` |

The hand-written pages PRD 35 §2 lists (workspace format, keyboard shortcuts, style-sheet fields, request tags, claim-link statuses) arrive with the features they describe. `FR-10-020` requires the quadrant to be complete at v1.0.

The Rust API is documented separately: rustdoc for the crates is published at [/api/](https://bioedca.github.io/Tlilli/api/) by the same workflow that builds this site (PRD 35 §1).
