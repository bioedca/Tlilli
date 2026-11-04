# ADR-0001: Repository layout and the `tlilli` command-line interface

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

The concept document fixes the code names: repository `tlilli`, core crate `tlilli-core`, MCP server `tlilli-mcp`, skills `tlilli-*`, workspace folder `*.tlilli`. It also names two commands an author runs outside the app, `tlilli export --canonical` and `tlilli skills install`, without saying which binary provides them; D-055 adds `crates/tlilli-cli` for that reason. The PRD locks the system shape as "two doors, one core": the UI and the MCP server both call `tlilli-core` through the same event API, the MCP server is the only door for agents, and the in-app server and the standalone server share code ([PRD 21 §1](../prd/21-architecture-and-tech-stack.md#1-system-shape), `INV-02`, `INV-09`, `NFR-PORT-003`).

Releases come from one version source: `[workspace.package] version` in the root `Cargo.toml`, one tag `v<version>` for the whole workspace, and release-plz publishing `tlilli-core`, `tlilli-mcp` and `tlilli-cli` to crates.io in one version group (`PR-REL-002`, `PR-REL-024`, D-048). The skill pack's version equals the app version (`PR-REL-007`, `NFR-COMPAT-004`). The cloud sandbox's GitHub access is scoped to this repository, so dependencies come from crates.io and npm releases only (`PR-ARCH-001`, assumption A7 in [PRD 01](../prd/01-vision-and-scope.md#7-assumptions)).

Phase 0 needs the layout fixed before the workspace skeleton (bootstrap task 12), the Tauri shell (task 14) and the agent context files (task 11) are written.

## Decision

One Cargo workspace at the repository root holds every Rust crate; `ui/` is the one npm package. The layout is the locked table in [PRD 21 §2](../prd/21-architecture-and-tech-stack.md#2-repository-layout-locked), summarized here:

| Path | Package | Published | Role |
| --- | --- | --- | --- |
| `crates/tlilli-core` | `tlilli-core` (lib) | crates.io from v0.1 | Document model, event log, snapshots, ledger, style sheet, provenance, segmentation, import/export, storage. The only source of truth and, through `storage`, the only module that touches the filesystem. |
| `crates/tlilli-mcp` | `tlilli-mcp` (lib + thin bin) | crates.io from v0.2 | MCP tools, resources, prompts, guardrails, transports, auth token. The only door for agents (ADR-0002). |
| `crates/tlilli-cli` | `tlilli-cli` (bin `tlilli`) | crates.io from v0.2; built from v0.1 | Author and CI commands; see below. |
| `src-tauri` | `tlilli-app` (bin) | not published | Tauri 2 shell: window, menus, dialogs, updater, capabilities. Embeds `tlilli-mcp` as a library and can spawn its binary for stdio clients. |
| `ui` | `@tlilli/ui` (private) | — | React 19 + TypeScript + ProseMirror view; calls commands that return events and never constructs events itself. |
| `skills` | — (MIT) | with every release | Skill sources `tlilli-*` and the per-agent package builder. |
| `fuzz` | `tlilli-fuzz` | not published | `cargo-fuzz` targets. |
| `docs`, `tests/fixtures`, `scripts`, `.github` | — | — | Site source with PRD, ADRs and gates; fixtures with `LICENSES.md`; dev scripts; workflows and templates. |

**The `tlilli` command** lives in its own crate, `crates/tlilli-cli`, which depends on `tlilli-core` and `tlilli-mcp` as libraries. It holds no document logic: every subcommand is a thin call into a core or server API, with `anyhow` at the binary boundary only ([PRD 21 §7](../prd/21-architecture-and-tech-stack.md#7-software-design-rules-intersect-software-design)). Subcommands arrive with the phase that needs them: `export --canonical`, `import --canonical`, `import <file.md|docx>`, `doctor` and `--version` in v0.1 (`FR-01-050`); `mcp` (a proxy to the server), `mcp schema --markdown` and `schema dump` for the generated reference in v0.2 (`PR-DOC-003`); `skills build` in v0.2 and `skills install --claude-code | --codex | --chatgpt` with `--check` in v1.0 (`FR-02-061`, `FR-10-010`). Exit codes are 0 for success, 1 for a user error, 2 for an internal error (`FR-01-050`). Flags are never repurposed (`PR-MNT-024`).

**One version.** Every crate declares `version.workspace = true`, `edition.workspace = true`, `license.workspace = true` and `rust-version.workspace = true`; `src-tauri/tauri.conf.json` omits `version` so Tauri reads the shell crate's Cargo version; `ui/package.json` is private and carries no meaningful version; release-plz keeps the three published crates and `tlilli-app` in `version_group = "tlilli"` and cuts one tag per release (`PR-REL-002`, [PRD 37 §2](../prd/37-releases-and-packaging.md#2-release-flow-stable)).

**Boundaries.** Module boundaries follow [PRD 21 §4](../prd/21-architecture-and-tech-stack.md#4-core-model-boundaries): no module reaches into another's storage tables, the UI never constructs events, `tlilli-mcp` never calls `storage` directly. `tlilli-core` and `tlilli-mcp` carry `#![forbid(unsafe_code)]` (`PR-ARCH-005`); `tlilli-cli` does too, because nothing in it needs `unsafe`. Licenses: Apache-2.0 for the crates and the app, MIT for `skills/` (D-003).

### Why one workspace and one version

- One number names a consistent set: the MCP schemas (`x-tlilli-version`, `FR-02-013`), the skill pack and the workspace schema are all "versioned with the app" (`NFR-COMPAT-003`, `NFR-COMPAT-004`).
- A standalone `tlilli-mcp` installed with `cargo install` must open the same workspace as the app (`NFR-PORT-003`); sharing the version removes the question of which crate version wrote the database.
- One `Cargo.lock`, one `cargo-deny` run, one clippy configuration and one `cargo build --workspace` keep the supply-chain checks and the commands in `CLAUDE.md` simple (`PR-ARCH-006`, T-07).
- One release PR per version, approved by the maintainer as the release decision (D-025, `PR-PRQ-010`).

## Consequences

### Positive

- The CLI gives CI and scripts the canonical export and re-import without a display (`FR-01-043`, `NFR-REL-008`) and produces the generated reference pages (`PR-DOC-003`).
- Contract tests run against the in-app server and the binary from the same crate (`NFR-PORT-003`, [PRD 34 §1](../prd/34-testing.md#1-test-layers)).
- Gated paths map to directories (`crates/tlilli-core/src/{model,event,storage}/**`, `crates/tlilli-mcp/**`, `skills/**`, `docs/adr/**`), so CODEOWNERS routes maintainer review by path (D-022).

### Negative

- Every published crate bumps on every release, even when unchanged; crates.io carries versions of `tlilli-core` with no code change.
- `tlilli-cli` links `tlilli-mcp`, so the CLI binary carries the server's dependencies.
- The whole workspace compiles in CI on every pull request; the fast Linux lane and the Rust cache keep this inside the budget set in [PRD 33](../prd/33-ci-cd.md).

### Risks

- The layout in `CLAUDE.md` and `AGENTS.md` drifts from this ADR (R-21). Bootstrap task 11 updates both files, and the two are kept in step by rule.
- `tlilli-cli` becomes a home for logic that belongs in the core. The "no document logic" rule above and item 5 of the reviewer rubric ([PRD 31 §6](../prd/31-pull-requests.md#6-definition-of-a-good-pr-reviewer-rubric)) guard against it.
- The binary name `tlilli` is part of the name clearance (R-07, D-035); `scripts/rename.sh` covers it.

## Alternatives considered

- **One repository per crate.** Rejected: one version source, one lockfile and one review pipeline are PRD rules, and a solo maintainer (D-001) cannot keep three repositories in step.
- **Independent crate versions.** Rejected by `PR-REL-002` and `PR-REL-007`: the skill pack and the schemas are versioned with the app.
- **CLI subcommands inside the `tlilli-mcp` binary.** Rejected: `tlilli-mcp` is the agent door and a gated crate; export, import and `doctor` are author tools, and the concept names `tlilli export`, not `tlilli-mcp export`.
- **CLI inside `src-tauri`.** Rejected: the shell crate is not published and needs Tauri's build dependencies, so `cargo install` would not work.

## References

- Concept document: "Name" (code names), "Architecture", "Skill pack and agent integration".
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §1, §2, §4, §5 (`PR-ARCH-001`, `PR-ARCH-005`, `PR-ARCH-006`), §7; [37](../prd/37-releases-and-packaging.md) §1, §2, §5; [34](../prd/34-testing.md) §1; [42](../prd/42-bootstrap-backlog.md) rows 11, 12, 14.
- Requirements: `INV-02`, `INV-09`; `FR-01-043`, `FR-01-050`, `FR-02-010`, `FR-02-013`, `FR-02-061`, `FR-10-010`; `NFR-PORT-003`, `NFR-COMPAT-003`, `NFR-COMPAT-004`, `NFR-REL-008`; `PR-REL-002`, `PR-REL-007`, `PR-REL-024`; `PR-DOC-003`; `PR-MNT-024`; `PR-PRQ-010`.
- Decisions, risks, threats: D-001, D-003, D-022, D-025, D-035, D-048, D-054, D-055; R-07, R-21; T-07.
