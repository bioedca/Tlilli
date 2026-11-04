# AGENTS.md — crates/tlilli-mcp

Adds to the root [`AGENTS.md`](../../AGENTS.md), which applies here in full. `tlilli-mcp` is the only door for
agents ([PRD 21 §4](../../docs/prd/21-architecture-and-tech-stack.md),
[PRD 22](../../docs/prd/22-security-and-threat-model.md)); the whole crate is a gated path.

## Review guidelines

In addition to the root rules and severities:

- The pen rule (`INV-01`): write tools produce suggestions, comments, proposed sources or allow-listed mechanical
  edits only. A tool, argument or code path that can change author text is a Blocker.
- Every write tool requires a claimed run and a target inside the frozen queue or a standing-check scope, and
  refuses other targets with a hint to comment (`INV-03`); the mechanical-edit allow-list, the alternative cap and
  the rationale requirement hold for every tool. A path around `guard` is a Blocker; every refusal has a test.
- Tool inputs are validated against their JSON Schema before they reach the core; payloads over 1 MB are rejected
  (`NFR-SEC-002`). Schema changes are additive or deprecated properly, with snapshots and reference docs updated.
- Source text, PDFs and reviewer comments travel in envelopes marked `untrusted: true` and are never interpolated
  into app-generated instructions (`INV-07`, `NFR-SEC-003`).
- HTTP binds to 127.0.0.1 only and checks the per-workspace bearer token on every request (`NFR-SEC-001`); tokens
  never reach logs (`NFR-SEC-008`). On stdio, stdout carries protocol messages only.
- The server reaches `tlilli-core` through its event API, never `storage` directly, and no code path depends on a
  particular client, model or vendor (`INV-09`).
