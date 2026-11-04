# Reference

Reference pages are for looking things up: what a tool, resource, prompt, schema, command or shortcut is and does, stated once and precisely. They describe; they do not advise (see [How-to guides](../how-to/index.md)).

Most of this section is generated and never hand-edited (`PR-DOC-003`). The `tlilli` command produces it from the running code, every generated file carries a header comment saying so, and the `protocol-ref/drift` CI job fails when a committed page differs from the generator's output. The generators and the drift job are bootstrap task 29.

| Page | Generator | Source of truth |
| --- | --- | --- |
| `mcp/tools.md`, `mcp/resources.md`, `mcp/prompts.md` | `tlilli mcp schema --markdown` | the MCP server's schema (`crates/tlilli-mcp`) |
| `schemas/*.json` | `tlilli schema dump` | canonical JSON, style sheet and tool-input schemas (`crates/tlilli-core`) |
| `cli.md` | `tlilli --help-markdown` | the clap command tree (`crates/tlilli-cli`) |
| `skills.md` | `tlilli skills build --docs` | the skill sources under `skills/` |

The hand-written pages PRD 35 §2 lists (workspace format, keyboard shortcuts, style-sheet fields, request tags, claim-link statuses) arrive with the features they describe. `FR-10-020` requires the quadrant to be complete at v1.0.

The Rust API is documented separately: rustdoc for the crates is published at [/api/](https://bioedca.github.io/Tlilli/api/) by the same workflow that builds this site (PRD 35 §1).
