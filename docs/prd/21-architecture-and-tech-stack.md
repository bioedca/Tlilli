# 21 · Architecture and tech stack

This section locks the technology decisions the concept left open, states the dependency policy, and defines how architecture decisions are recorded. Anything marked **locked** changes only through an ADR plus a decision-log entry.

## 1. System shape

```
┌───────────────────────── Tauri 2 desktop app ─────────────────────────┐
│  ui/ (React 19 + TypeScript + ProseMirror)                             │
│     │  Tauri commands & events (typed, generated)                      │
│  src-tauri/ (Rust shell: window, menus, file dialogs, updater)         │
│     │  in-process calls                                                │
│  crates/tlilli-core  ← the only source of truth                        │
│     document model · event log · snapshots · ledger · style sheet ·    │
│     provenance · segmentation · import/export · storage (SQLite)       │
│     ▲                                                                  │
│  crates/tlilli-mcp (rmcp) — stdio and streamable HTTP on 127.0.0.1    │
└─────┼──────────────────────────────────────────────────────────────────┘
      │  MCP (JSON-RPC)                 ┌──────────────────────────────┐
      └────────────────────────────────▶│ external agent (Claude Code, │
                                        │ Codex, ChatGPT via tunnel)   │
                                        └──────────────────────────────┘
```

- **Two doors, one core.** The UI and the MCP server both call `tlilli-core` through the same event API; an author edit and an accepted suggestion are the same kind of change in the log (`INV-02`).
- **The MCP server is the only door for agents** and stands inside the trust boundary of the user's machine; the agent stands outside it ([22](22-security-and-threat-model.md)).
- **In-app and standalone server share code.** `tlilli-mcp` is a library crate with a thin binary; the Tauri shell embeds the library and can also spawn the binary for stdio clients.

## 2. Repository layout (locked)

| Path | Purpose | Crate / package | Gated |
| --- | --- | --- | --- |
| `crates/tlilli-core` | Document model, event log, ledger, style sheet, provenance, segmentation, import/export, storage | `tlilli-core` (lib, published) | partly: `src/model/**`, `src/event/**`, `src/storage/**` |
| `crates/tlilli-mcp` | MCP server: tools, resources, prompts, guardrails, transports, auth token | `tlilli-mcp` (lib + bin, published from v0.2) | yes |
| `crates/tlilli-cli` | `tlilli` command: `export --canonical`, `import`, `skills install`, `mcp` (proxy to server), `doctor` | `tlilli-cli` (bin, published from v0.2) | no |
| `src-tauri` | Tauri 2 shell, commands, updater, capabilities | `tlilli-app` (bin, not published) | `tauri.conf.json`, `capabilities/**` |
| `ui` | React + ProseMirror web UI | `@tlilli/ui` (private) | no |
| `skills` | Skill sources `tlilli-*` (MIT) and the per-agent package builder | — | yes |
| `docs` | MkDocs site source, PRD, ADRs, gates, generated reference | — | `docs/prd/**`, `docs/adr/**`, `docs/gates/**` |
| `tests/fixtures` | Synthetic manuscripts, vendored OA papers with `LICENSES.md`, revision corpora | — | `LICENSES.md` |
| `fuzz` | `cargo-fuzz` targets | `tlilli-fuzz` (not published) | no |
| `scripts` | Dev scripts (`install_pkgs.sh`, generators) | — | no |
| `.github` | Workflows, templates, labels, CODEOWNERS, dependabot, labeler | — | yes |

Adding `crates/tlilli-cli` extends the layout in `CLAUDE.md`; the bootstrap backlog updates `CLAUDE.md` ([42](42-bootstrap-backlog.md)). Every crate sets `version.workspace = true`, `edition.workspace = true`, `license.workspace = true`, `rust-version.workspace = true`. Until v0.2, `tlilli-mcp` and `tlilli-cli` carry `publish = false` in their manifests (`PR-REL-024`, D-077).

## 3. Technology decisions

| Layer | Decision (locked) | Why | Alternatives considered |
| --- | --- | --- | --- |
| Language | Rust, stable channel; MSRV = the stable release current at each minor release, declared in `[workspace.package] rust-version` and tested in CI | Ships binaries, not a library for old toolchains; modern features | stable-2 (friendlier to packagers; rejected, D-031) |
| Shell | Tauri 2 | Native window, small binary, Rust in-process, three OSes | Electron (size, no Rust in-process) |
| UI framework | React 19 + TypeScript (strict) + Vite | Largest ProseMirror ecosystem, agent familiarity | Svelte 5, SolidJS, Lit (D-030) |
| Editor | ProseMirror (`prosemirror-model/state/view/transform`) with a schema mirroring blocks and spans; bindings via `@handlewithcare/react-prosemirror` | Mature structured editing; each transaction maps to one commit group of one or more core events (`FR-01-020`, D-073) | Tiptap (extra abstraction over the same engine), CodeMirror (not rich text) |
| View state | Zustand store fed only by core events; derived data memoized; no persisted UI state except window geometry and pane sizes | `INV-02`: no truth in the view | Redux (boilerplate) |
| Core data | ULID block IDs; span IDs derived by segmentation and stabilized by diff anchoring; append-only event log with hash chain; materialized snapshots | Runs, diffs and rollback cost nothing extra | CRDTs (no multi-writer need) |
| Storage | SQLite via `rusqlite` (bundled, WAL, FTS5); one `workspace.sqlite`; files under `sources/`, `figures/`, `exports/`, `logs/`, `backups/`; migrations with `rusqlite_migration` (numbered SQL, forward-only, pre-migration backup) | Local-first, portable, inspectable | sled/redb (no FTS, no tooling) |
| MCP | `rmcp` (official Rust MCP SDK): stdio and streamable HTTP transports; HTTP bound to 127.0.0.1 with bearer token | Spec-tracking, maintained by the MCP org | hand-rolled JSON-RPC |
| Serialization | `serde` + `serde_json`; JSON Schema for tool inputs generated with `schemars` and committed as snapshots | Contract tests, generated docs | — |
| Text processing | Rule-based sentence segmentation seeded by the style sheet's abbreviation list (`unicode-segmentation` for graphemes/words); diff anchoring with `similar` (Myers/patience) | All local, deterministic | ML segmenters (dependency weight, non-determinism) |
| Citations | CSL-JSON canonical; rendering with `hayagriva` (CSL styles and locales, maintained by Typst); BibTeX export through a Tlilli-owned CSL-JSON-to-BibTeX mapping written with the `biblatex` crate's writer; `.bib` import through `hayagriva`'s BibTeX reader plus a Tlilli-owned conversion to CSL-JSON (D-071) | One engine for PDF and reference lists; active maintenance | `citeproc-rs` (stalled) — recorded in ADR-0003 |
| Resolvers | `reqwest` (rustls) to Crossref, NCBI E-utilities, arXiv, Europe PMC, Unpaywall, doi.org, Zotero local API; rate-limited, cached in SQLite | Author-initiated only | — |
| PDF text | Pure Rust first: `pdf-extract`/`lopdf`; `pdfium-render` (bundled pdfium, BSD) only by ADR if extraction quality is insufficient at the v0.3 gate | Sidecar policy (§5) | MuPDF (AGPL, incompatible) |
| docx | Import and export through `zip` + `quick-xml` with our own OOXML model; comments on export v0.4, tracked changes later | Control over fidelity; no heavy dependency | `docx-rs` (import gaps) |
| LaTeX | Export through `minijinja` templates + `.bib` from the BibTeX export (`FR-03-051`); import of basic LaTeX with a small hand-written parser | Predictable output | pandoc sidecar (policy) |
| PDF | `typst` + `typst-pdf` crates in-process with a bundled template and fonts | One binary, deterministic | Typst CLI sidecar (policy) |
| Markdown | `pulldown-cmark` import; custom writer with span-ID comment markers for the agent view | Round-trip control | — |
| Logging | `tracing` + `tracing-subscriber` (JSON lines, daily rotation) | NFR-OBS | — |
| Updater | `tauri-plugin-updater` with minisign; endpoints on the docs site (`updates/stable.json`, `updates/beta.json`) | Free, signed, no server | — |
| UI tooling | pnpm, Biome (lint + format), Vitest + Testing Library, Playwright; `tauri-driver` smoke suite | One fast toolchain | ESLint + Prettier (D-032) |
| Rust tooling | `cargo-nextest`, `cargo-llvm-cov`, `cargo-deny`, `cargo-mutants`, `cargo-fuzz`, `cargo-semver-checks`, `insta`, `proptest`, `criterion` | [34](34-testing.md) | — |
| Release tooling | `release-plz` (release PR, version bump, changelog via `git-cliff`, tag, crates.io publish), `tauri-apps/tauri-action` (bundles, draft release, `latest.json`), `anchore/sbom-action`, `actions/attest` | [37](37-releases-and-packaging.md) | cargo-dist (no Tauri bundles) |
| Docs | MkDocs + Material, `mike` after 1.0 (provisional, D-063), `mkdocs-redirects`, `lychee` link check; rustdoc under `/api` | [35](35-documentation.md) | mdBook (no Diátaxis navigation features) |

## 4. Core model boundaries

- `tlilli-core::model` — Workspace, Manuscript, Section, Block, Span, Request, IdeaStub, Suggestion, MechanicalEdit, Comment, Run, Snapshot, Source, ClaimLink, StyleSheet, ProvenanceMark, FigureAsset: exactly the objects in the concept's domain model, with the "created by" rule encoded in the event validator.
- `tlilli-core::event` — one enum of events; every mutation is an event with `actor` (`Author`, `Agent{run_id, identity}`, `System`), `at`, `parent_hash`, `payload`. The validator rejects events whose actor may not create the object (`INV-01`).
- `tlilli-core::segment` — segmentation and diff anchoring; pure functions, property-tested.
- `tlilli-core::storage` — SQLite schema, migrations, FTS, file layout; the only module touching the filesystem.
- `tlilli-core::ledger`, `::style`, `::provenance`, `::export`, `::import` — feature modules depending on `model` and `event` only.
- `tlilli-mcp::tools`, `::resources`, `::prompts`, `::guard` (run claim, scope check, allow-list, alternative cap, rationale requirement), `::auth`, `::transport`.

Rules: no module reaches into another's storage tables; the UI never constructs events (it calls commands that return events); `tlilli-mcp` never calls `storage` directly.

## 5. Dependency and sidecar policy (PR-ARCH)

| ID | Rule |
| --- | --- |
| `PR-ARCH-001` | Dependencies come from crates.io and npm releases. `git =` and `path` dependencies outside the workspace are forbidden (`cargo-deny` `sources` check). |
| `PR-ARCH-002` | Adding a dependency with native code (C/C++ builds, bundled binaries) or more than 200 transitive crates requires an ADR. |
| `PR-ARCH-003` | Choose dependencies the INTERSECT way: actively maintained (release or commit in the last 12 months), responsive issues, compatible license (allow-list in `deny.toml`: Apache-2.0, MIT, BSD-2/3, ISC, Zlib, MPL-2.0, Unicode-3.0, CC0; anything else needs an ADR). |
| `PR-ARCH-004` | Sidecars (external executables bundled with the app) are forbidden by default. An ADR may allow one if it states why no in-process option exists, pins the version, checksums the binary in CI and documents the fallback when it is missing. The v0.5 tunnel (cloudflared/ngrok) is the expected exception and uses the user's installed binary, never a bundled one. |
| `PR-ARCH-005` | `unsafe` is forbidden in `tlilli-core` and `tlilli-mcp` (`#![forbid(unsafe_code)]`); allowed in `src-tauri` only behind a documented `// SAFETY:` comment. |
| `PR-ARCH-006` | Every crate compiles with `-D warnings` under the clippy configuration in `Cargo.toml` (`pedantic` enabled, with a short documented allow-list). |
| `PR-ARCH-007` | Feature flags are additive and tested in CI with `--all-features` and `--no-default-features`. |

## 6. Architecture decision records

- Location: `docs/adr/NNNN-short-title.md`, MADR format (Context, Decision, Consequences, Alternatives, Status), numbered sequentially, immutable once `Accepted` (superseded by a new ADR).
- An ADR is **required** for: a new native or binary dependency; a sidecar; a storage schema change that is not purely additive; a breaking MCP change; a deviation from this PRD; a change to the trust boundary.
- ADRs are human-gated (`docs/adr/**` in CODEOWNERS). An agent drafts; the maintainer accepts.
- Initial ADRs opened by the bootstrap backlog: ADR-0001 crate layout including `tlilli-cli`; ADR-0002 `rmcp` as MCP SDK; ADR-0003 `hayagriva` as citation engine; ADR-0004 storage schema v1 and migration policy; ADR-0005 sidecar policy and the tunnel exception; ADR-0006 event log hash chain and snapshot cadence; ADR-0007 PDF extraction strategy (decided at v0.3 gate).

## 7. Software design rules (INTERSECT Software Design)

- Descriptive names (verbs for functions, nouns for values, `is_` for booleans); no magic numbers (constants in one module per crate); configuration in one place (`tlilli-core::config`).
- Small single-purpose functions; separate I/O from pure logic so pure logic is unit-tested and I/O is integration-tested.
- Loose coupling across the module boundaries in §4; information hiding (no `pub` fields on model types; builders and accessors).
- Comment the why, not the what; delete dead code rather than commenting it out; keep comments current.
- Every line is intentional: generated or copied code is understood before it is kept, and its origin is noted when it comes from a forum or a paper.
- Deliberate error handling: `thiserror` types per module, `anyhow` only at binary boundaries; no `unwrap` outside tests (clippy `unwrap_used` denied).
- Deliberate time: all timestamps UTC RFC 3339 in storage, displayed in local time.
