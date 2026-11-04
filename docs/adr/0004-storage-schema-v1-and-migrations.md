# ADR-0004: Storage schema v1 and migration policy

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

The concept keeps everything in one workspace folder: `workspace.sqlite` (rusqlite), `sources/` with PDFs and extracted text, `figures/`, `exports/`, and `tlilli export --canonical` writing JSON for git ("local-first, portable, inspectable"). The PRD fixes the folder (`<name>.tlilli/` with `workspace.sqlite`, `sources/`, `figures/`, `exports/`, `logs/`, `backups/` and a `tlilli.json` marker carrying the schema version, `FR-01-001`), the engine (SQLite via `rusqlite`, bundled, WAL, FTS5) and the migration tool (`rusqlite_migration`: numbered SQL, forward-only, pre-migration backup) ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions), D-054). It states what the store must guarantee: an append-only event log in WAL that loses at most the last uncommitted transaction on a crash or power loss (`NFR-REL-001` as amended by D-066 in pull request 52, which prescribes `synchronous=FULL` for the workspace database); integrity verification and snapshot rebuild on startup (`NFR-REL-002`); a backup to `backups/<timestamp>-pre-<version>.sqlite` before every migration, each migration reversible or documented as one-way (`NFR-REL-003`); a schema version that opens equal or lower versions, migrates forward and refuses newer ones (`NFR-COMPAT-001`); every released schema version opens forever (`PR-MNT-005`, `PR-MNT-023`); folders that survive moving and syncing, with a warning about concurrent writers (`NFR-PRIV-004`, `NFR-PORT-002`, `NFR-PORT-004`); full-text search over 80 sources in ≤ 300 ms (`NFR-PERF-006`); the complete tool-call log per run (`NFR-OBS-002`). `tlilli-core::storage` is the only module that touches the filesystem, no module reaches into another's tables, and `tlilli-mcp` never calls storage ([PRD 21 §4](../prd/21-architecture-and-tech-stack.md#4-core-model-boundaries)). A storage schema change that is not purely additive requires an ADR ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records)), and `src/storage/**` is a gated path.

`rusqlite` with the `bundled` feature compiles SQLite from C source. A dependency with native code requires an ADR (`PR-ARCH-002`); this record is it.

## Decision

**Engine and file layout.** SQLite through `rusqlite` with the `bundled` feature, so every OS ships the same SQLite build with FTS5 compiled in, plus the backup API. One `workspace.sqlite` per workspace, opened with `journal_mode=WAL`, `synchronous=FULL` and `foreign_keys=ON`. FULL is what `NFR-REL-001` as amended by D-066 (pull request 52) prescribes for the workspace database, because in WAL mode only FULL meets the requirement's loss bound on power loss; ADR-0006 gives the reasoning and the checkpoint cadence. The amendment allows `synchronous=NORMAL` only for caches held in a separate database; v1 keeps the resolver cache inside `workspace.sqlite`, so the whole file runs FULL. Large content stays in files referenced from rows by workspace-relative paths: `sources/<ulid>/source.pdf` and `source.txt` (`FR-03-002`), `sources/protocols/<ulid>/` (v0.5, `FR-05-001`), `figures/<ulid>/` (`FR-01-014`), `exports/`, `logs/` (`NFR-OBS-001`), `backups/`. Every file write goes through temp-file-and-rename ([PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component)); paths are NFC-normalized and avoid characters illegal on Windows (`NFR-PORT-004`); timestamps are UTC RFC 3339 text ([PRD 21 §7](../prd/21-architecture-and-tech-stack.md#7-software-design-rules-intersect-software-design)). `tlilli.json` mirrors the schema version so a folder is recognized without opening the database.

**Schema v1.** Version 1 is the schema `v0.1.0` ships. It defines a table for every object of the concept's domain model with the columns v0.1 needs; later phases add columns and tables additively. Materialized state tables are derived from the event log and rebuildable from it (`NFR-REL-002`); the log and the snapshots are the durable truth.

| Group | Tables in v1 | Notes |
| --- | --- | --- |
| Workspace | `settings` (key, value) | Preferences and the workspace MCP token ([PRD 22 §1](../prd/22-security-and-threat-model.md#1-assets-and-trust-boundaries)). The schema version lives in SQLite's `user_version`, managed by `rusqlite_migration`. |
| Manuscripts | `manuscripts` (id ULID, type, title, created_at, updated_at, archived_at); `sections` (id, manuscript_id, position, role, name) | `FR-01-002`, `FR-01-003`; archive is a soft delete. These are the "documents" of the backlog row. |
| Log | `events` (seq, manuscript_id, actor_kind, actor_run_id, actor_identity, at, parent_hash, hash, payload_version, payload JSON); `chain_heads` (manuscript_id nullable for the workspace chain, head_seq, head_hash) | `events` is append-only; rows are never updated or deleted. `chain_heads` is updated in the same transaction as the event it records and is the expected head that verification compares against; chain rules in ADR-0006. |
| Snapshots | `snapshots` (id, manuscript_id, event_seq, head_seq, head_hash, kind, label, root_hash, created_at); `snapshot_blocks` (hash, bytes); `snapshot_tree` (snapshot_id, position, block_hash) | Content-addressed and deduplicated (`FR-01-031`); kinds `before` and `after` for runs (`FR-02-002`); each snapshot repeats the chain head it was taken at (ADR-0006). |
| Materialized text | `blocks` (id ULID, section_id, position, kind, payload JSON); `spans` (id ULID, block_id, position, text, mark); `span_tombstones` (id, successor_id) | Current state for queries and the editor; one provenance mark per span (`INV-06`); tombstones per `FR-01-012`. |
| Annotations | `requests` (the queue), `comments`, `suggestions` (alternatives as JSON), `locked_spans` | `FR-01-021`, `FR-02-030..035`; the style sheet's locked-span list reads `locked_spans` from v0.4 (`FR-04-003`); `suggestions` stays empty until v0.2. |
| Runs | `runs` (id, manuscript_id, status, agent_identity, opened_at, claimed_at, closed_at, before_snapshot_id, after_snapshot_id, report JSON, calls_used); `run_calls` (run_id, seq, tool, request JSON, response JSON, started_at, duration_ms, outcome) | `FR-01-022`, `FR-02-001`, `FR-02-044`, `NFR-OBS-002`. |
| Ledger | `sources` (id ULID, manuscript_id nullable, status, doi_norm, pmid, pmcid, arxiv_id, csl JSON, fulltext_status, pdf_path, created_at); `source_fulltext` (FTS5: source_id, page, text); `claim_links` (id, span_id, source_id, quote, locator, status, rationale, checked_by_run_id, checked_at); `resolver_cache` (identifier, response JSON, fetched_at) | Empty until v0.3; the ledger resource returns empty structures before that (`FR-02-026`). `manuscript_id` is nullable so the v0.5 shared pool (`FR-05-030`) is an additive change; dedupe keys per `FR-03-004`; cache per [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions), Resolvers. |
| Style | `style_sheets` (manuscript_id, json) | JSON with a published schema (`FR-04-001`); empty until v0.4. |

**Migrations.** Numbered SQL files embedded in `tlilli-core::storage` (`migrations/NNNN_<name>.sql`) and run by `rusqlite_migration`, which records the version in `user_version`. Rules:

1. Forward-only at runtime. The app never downgrades; recovery from a bad migration is the pre-migration backup.
2. Before any migration the database is copied with SQLite's backup API to `backups/<timestamp>-pre-<version>.sqlite` (a plain file copy is unsafe under WAL). Backups are kept; a migration happens at most once per schema bump, so the folder stays small. A retention setting is a later refinement if sizes warrant it.
3. Every migration ships a down script used only by the test suite to prove reversibility; a migration that cannot be reversed is marked one-way in its header and listed under "Upgrade notes" in the release notes (`NFR-REL-003`, `PR-DOC-011`).
4. `events` rows are immutable: a migration may add columns to `events` but never rewrites `payload`, `parent_hash` or `hash`. Payload format changes bump `payload_version`, and the event decoder reads every version ever released (ADR-0006, `PR-MNT-005`).
5. Each released schema version leaves a fixture database in `tests/fixtures/db/`, and migrations run against each of them in CI ([PRD 34 §3](../prd/34-testing.md#3-what-to-test-by-component), `PR-MNT-023`). Opening a newer `user_version` is refused with a clear message (`NFR-COMPAT-001`).
6. Additive changes ship as ordinary gated PRs with `docs/reference/workspace-format.md` updated (`PR-DOC-001`); non-additive changes need an ADR and bump the schema version with a `BREAKING CHANGE` footer (`PR-REL-003`).

**Integrity.** On open: refuse a folder without `tlilli.json`; run `PRAGMA quick_check`; verify each event chain against its recorded head (ADR-0006) and rebuild materialized tables and snapshots that disagree with the log (`NFR-REL-002`). `tlilli doctor` runs the full `PRAGMA integrity_check`, the chain verification and a replay comparison (`FR-01-050`). The app warns when the workspace lives in a folder a sync client is known to manage (`NFR-PRIV-004`); SQLite's own locking serializes writers, and nothing more is attempted in v1.

## Consequences

### Positive

- Inspectable with any SQLite tool; one file to back up; FTS5 in-process meets `NFR-PERF-006` without a search service.
- The same SQLite build on every OS, so a workspace created on one OS opens on another (`NFR-PORT-002`).
- Plain SQL migrations are reviewable in the gated PR, and fixture databases make compatibility a test rather than a promise.

### Negative

- Compiling SQLite from source lengthens cold builds; the Rust cache in CI amortizes it.
- The materialized tables duplicate information held in the log and the snapshots; the duplication buys query speed and costs disk and rebuild code.
- Forward-only means a user who downgrades the app restores a backup by hand (documented in a how-to).

### Risks

- T-06 (crash, bad migration, synced-folder conflict): WAL, backups, startup verification and the sync warning are the mitigations; the kill-9 harness and the migration tests verify them.
- Full text in FTS5 grows the database with every PDF; the nightly bench on the reference workspace (80 sources) watches size and `NFR-PERF-006`.
- A change slips through as "additive" while changing semantics: the reviewer rubric checks `src/storage/**` diffs against this ADR.

## Alternatives considered

- **sled or redb** ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions)). Rejected: no full-text search, no inspection tooling.
- **One database per manuscript.** Rejected: settings, the MCP token and the v0.5 shared pool are workspace-level, and the concept names one `workspace.sqlite`.
- **Files only (JSON per manuscript).** Rejected: no transactions for `NFR-REL-001`, no FTS; the canonical JSON export already serves the git use case (`FR-01-043`).
- **An ORM or query builder.** Rejected: hand-written SQL keeps the schema inspectable and the migrations plain files.
- **Runtime down-migrations.** Rejected: the PRD makes migrations forward-only; the backup is the rollback.
- **Defining tables phase by phase.** Rejected in favour of the full domain model in v1: the ledger and style-sheet resources already exist in v0.2 and return empty structures (`FR-02-026`).

## References

- Concept document: "Architecture" (Storage row), "Domain model".
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §3 (Storage, Resolvers), §4, §6, §7; [22](../prd/22-security-and-threat-model.md) §1, §3; [34](../prd/34-testing.md) §3 (Storage, Event log); [38](../prd/38-maintenance-and-support.md) §5; [10](../prd/10-fr-v0.1-black-ink.md) §10.1–10.4; [12](../prd/12-fr-v0.3-ledger.md) §12.1–12.3.
- Requirements: `INV-02`, `INV-06`, `INV-08`; `FR-01-001..003`, `FR-01-010..014`, `FR-01-021`, `FR-01-022`, `FR-01-030`, `FR-01-031`, `FR-01-043`, `FR-01-050`; `FR-02-001`, `FR-02-002`, `FR-02-011`, `FR-02-026`, `FR-02-044`; `FR-03-001..004`, `FR-03-010`, `FR-03-023`; `FR-04-001`, `FR-04-003`; `FR-05-001`, `FR-05-030`; `NFR-REL-001..003`, `NFR-REL-007`, `NFR-REL-008`; `NFR-COMPAT-001`; `NFR-PRIV-004`; `NFR-PORT-002`, `NFR-PORT-004`; `NFR-PERF-001`, `NFR-PERF-006`; `NFR-OBS-001`, `NFR-OBS-002`; `PR-ARCH-002`; `PR-MNT-005`, `PR-MNT-023`; `PR-REL-003`; `PR-DOC-001`, `PR-DOC-011`.
- Decisions and threats: D-054, D-066 (pull request 52); T-06; ADR-0006.
