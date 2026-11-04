# ADR-0002: `rmcp` for the MCP server

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

The concept makes the MCP surface the product: an agent connects over MCP, reads the manuscript, style sheet and ledger as resources, pulls the queue, and writes back through a narrow set of tools that can only produce red ink. Claude Code and Codex connect over stdio or HTTP; ChatGPT needs a public HTTPS URL, which a tunnel provides in front of the HTTP transport (concept "Architecture", "MCP surface", "Skill pack and agent integration"; `INV-09`). The PRD specifies the transports and their security: `tlilli-mcp stdio --workspace <path>` serves one client and exits with it (`FR-02-010`); the in-app server listens on `127.0.0.1:7141` (configurable) with streamable HTTP and requires `Authorization: Bearer <workspace token>` (`FR-02-011`, `NFR-SEC-001`); tools, resources and prompts are advertised with JSON schemas, an `x-tlilli-version` and a `protocol_version`, snapshot-tested and generated into the docs (`FR-02-013`, `NFR-COMPAT-003`). Guardrails are enforced server-side, never by prompting ([PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component)). The server must survive disconnects, malformed JSON-RPC and concurrent clients (`NFR-REL-005`) and answer the read tools within `NFR-PERF-005`.

[PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) locks `rmcp`, the Rust SDK maintained by the Model Context Protocol organization, because it tracks the specification and is maintained (D-054); the alternative named there is a hand-rolled JSON-RPC layer. Dependencies come from crates.io releases, pass the INTERSECT selection test and the `deny.toml` license allow-list (`PR-ARCH-001`, `PR-ARCH-003`), and a dependency that brings more than 200 transitive crates needs an ADR (`PR-ARCH-002`). This record serves that purpose for `rmcp` with its HTTP transport enabled, should the `cargo tree` count taken in bootstrap task 12 cross that line.

## Decision

`crates/tlilli-mcp` is built on `rmcp` from crates.io, using the crate's server-side handler API and its stdio and streamable HTTP transports. Tlilli writes no JSON-RPC framing, capability negotiation or transport code of its own; it implements tool, resource and prompt handlers and the guardrails around them.

**Surface.** Exactly the three MCP primitives the concept names: tools, resources and prompts. Tool input schemas are generated with `schemars` and committed as snapshots ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions), Serialization); prompts are generated from `skills/` at build time so they cannot drift (`FR-02-060`). Other protocol features (resource subscriptions, sampling, elicitation, roots) are not used until a requirement names them; `FR-02-026` makes subscriptions optional and v0.2 does not ship them.

**Transports.**

- *stdio*: one client per process, launched by the agent (`claude mcp add tlilli -- tlilli-mcp stdio --workspace …`; Codex `[mcp_servers.tlilli]`); trusts the parent process; exits when the client closes (`FR-02-010`, [PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component)).
- *Streamable HTTP*: bound to `127.0.0.1` only, default port 7141, configurable; every request carries `Authorization: Bearer <token>`; the comparison is constant-time; failed attempts are logged and rate-limited at 10 per minute; cross-origin requests are denied and requests carrying a browser `Origin` are refused (`FR-02-011`, `NFR-SEC-001`, T-03). The HTTP transport is what the v0.5 tunnel forwards to (ADR-0005); the tunnel adds no second server.

**Token.** One token per workspace with 256 bits of entropy, generated on first enable, stored in the workspace's SQLite `settings` ([PRD 22 §1](../prd/22-security-and-threat-model.md#1-assets-and-trust-boundaries)), shown once, copyable, revocable and rotatable from Settings → Agents; revocation disconnects clients immediately (`FR-02-011`, `FR-02-012`, `NFR-SEC-001`). No token is ever logged or exported (`NFR-SEC-008`). The MCP specification's authorization flows (OAuth) are not adopted: the server runs on the author's machine for one author, and the bearer token is the authentication both locally and through the tunnel (`NFR-SEC-006`).

**Guardrails and boundaries.** `tlilli-mcp::guard` checks every write before the core is called: a claimed run; a target inside the frozen queue or a standing-check scope; at most three alternatives; a non-empty rationale per alternative; no locked spans; the mechanical allow-list; the per-run call budget (default 500) and the 1 MB payload cap; schema validation and ULID checks on every input (`INV-01`, `INV-03`, `FR-02-004`, `FR-02-030..036`, `NFR-SEC-002`, T-02). The scope predicate keeps the PRD's explicit exceptions, and the guard contract lists them by tool: `comment_add` is allowed on any target in the manuscript, because comments are the escape valve, and is refused only on locked spans (`FR-02-034`); `claim_link_set` is allowed on spans inside the queue, on spans in the citation-verification standing-check scope, and on any span already linked to the same source (`FR-03-024`); `source_resolve` writes nothing and needs no run (`FR-03-020`); `run_heartbeat`, `request_resolve` and `run_report` are scoped to the claimed run, not to a target (`FR-02-021`, `FR-02-035`, `FR-02-036`). Every other write tool refuses an out-of-scope target with `out_of_scope` and the hint to use `comment_add` (`INV-03`). `tlilli-mcp` calls `tlilli-core`'s event API only and never its `storage` module ([PRD 21 §4](../prd/21-architecture-and-tech-stack.md#4-core-model-boundaries)). Source, PDF and reviewer text leaves the server inside an envelope marked `untrusted: true` (`INV-07`, `NFR-SEC-003`). The in-app server and the standalone binary share this one crate (`NFR-PORT-003`).

**Versioning.** `protocol_version` is the MCP specification revision `rmcp` implements; `x-tlilli-version` is the app version. Within a major version tools and resources are only added or extended; a deprecated tool stays one minor, is marked in its description and logs a warning (`NFR-COMPAT-003`, `PR-MNT-020`); a breaking MCP change needs an ADR ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records)). `rmcp` upgrades arrive through Dependabot's grouped cargo updates (`PR-MNT-010`); a major upgrade that changes the handler API or the wire format is a `type/protocol` issue, because contract transcripts and generated reference pages must be regenerated in the same PR (`PR-TST-017`, `PR-DOC-001`).

**Deferred.** Resource subscriptions; the tunnel exposure (v0.5, ADR-0005); the ledger, figure, table and mechanical tools and the remaining prompts, which arrive with their phases ([PRD 12 §12.3](../prd/12-fr-v0.3-ledger.md#123-ledger-tools-and-resources-mcp), [PRD 13 §13.3–13.4](../prd/13-fr-v0.4-sweep-and-style.md#133-mechanical-edits), `FR-05-051`); any form of remote or multi-user authentication.

## Consequences

### Positive

- Specification fidelity comes with the SDK: new clients work by contract (`INV-09`), and the contract tests drive an in-process server with the `rmcp` client against golden JSON-RPC transcripts ([PRD 34 §1](../prd/34-testing.md#1-test-layers)).
- One crate, two transports, two deployment forms (in-app, standalone) and later the tunnel, all on the same auth and guard code.
- Fuzzing targets the tool inputs and the JSON-RPC framing the SDK exposes ([PRD 34 §1](../prd/34-testing.md#1-test-layers), Fuzz) rather than a framing layer of our own.

### Negative

- The SDK is young and moves with the specification; handler APIs may change between minors, and each change touches a gated crate.
- The HTTP transport brings an async runtime and an HTTP stack into a desktop app that otherwise needs neither; binary size counts against `NFR-PERF-010`.
- The in-app server runs inside the Tauri process ([PRD 21 §1](../prd/21-architecture-and-tech-stack.md#1-system-shape)), so its runtime must coexist with the shell's; the standalone binary has no such constraint.

### Risks

- An `rmcp` release changes behaviour on the wire: the contract snapshots and `protocol-ref/drift` fail the PR, which is the intended signal (`PR-TST-017`).
- A misconfigured bind address exposes the port beyond the machine (T-03): the port-binding test and the port-scan test that verify `NFR-SEC-001` guard it.
- A crashed server leaves a run claimed: claims expire with the heartbeat (`NFR-REL-005`, `FR-02-021`), exercised by the chaos test.

## Alternatives considered

- **Hand-rolled JSON-RPC over stdio and HTTP** ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions)). Rejected: tracking the specification, capability negotiation and transport edge cases is ongoing work with no product value, and it widens the fuzzing surface.
- **A community MCP crate not maintained by the protocol organization.** Rejected by the INTERSECT selection rule (`PR-ARCH-003`): the official SDK has the clearest maintenance signal.
- **A TypeScript MCP server as a Node sidecar.** Rejected: sidecars are forbidden by default (ADR-0005, `PR-ARCH-004`), and the server must share `tlilli-core` in-process ([PRD 21 §1](../prd/21-architecture-and-tech-stack.md#1-system-shape)).
- **stdio only, or HTTP only.** Rejected: Claude Code and Codex use stdio, and HTTP is what the tunnel exposes for ChatGPT (concept agent table; `FR-02-010`, `FR-02-011`, `FR-05-050`).
- **OAuth-based MCP authorization.** Not adopted: one author on one machine; a per-workspace bearer token is simpler to audit, revoke and rotate (`NFR-SEC-001`, T-03, T-04).

## References

- Concept document: "Architecture" (MCP server row), "MCP surface", "Skill pack and agent integration".
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §1, §3 (MCP, Serialization), §4, §5, §6; [22](../prd/22-security-and-threat-model.md) §1–§3; [34](../prd/34-testing.md) §1 (contract layer), §3 (MCP server); [11](../prd/11-fr-v0.2-red-ink.md) §11.1–11.4, §11.7.
- Requirements: `INV-01`, `INV-03`, `INV-07`, `INV-09`; `FR-02-004`, `FR-02-010..013`, `FR-02-020..036`, `FR-02-060`, `FR-03-020`, `FR-03-024`, `FR-05-050`, `FR-05-051`; `NFR-SEC-001..003`, `NFR-SEC-006`, `NFR-SEC-008`; `NFR-REL-005`; `NFR-PERF-005`, `NFR-PERF-010`; `NFR-PORT-003`; `NFR-COMPAT-003`; `PR-ARCH-001..004`; `PR-MNT-010`, `PR-MNT-020`; `PR-TST-017`; `PR-DOC-001`.
- Decisions and threats: D-054; T-02, T-03, T-04; ADR-0001, ADR-0005.
