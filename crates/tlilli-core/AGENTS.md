# AGENTS.md — crates/tlilli-core

Adds to the root [`AGENTS.md`](../../AGENTS.md), which applies here in full. `tlilli-core` is the only source of
truth ([PRD 21 §4](../../docs/prd/21-architecture-and-tech-stack.md)).

## Review guidelines

In addition to the root rules and severities:

- Every mutation is an event with `actor`, `at`, `parent_hash` and `payload`; the validator rejects an actor that
  may not create the object (`INV-01`, `INV-02`). A write around the log, or a change after which replaying the
  log no longer reproduces the materialized state, is a Blocker.
- The log is append-only and hash-chained, and the chain is verified at startup (`NFR-REL-001`, `NFR-REL-002`).
  Flag anything that rewrites or reorders events, weakens durability or skips the check.
- Migrations are numbered SQL, forward-only and preceded by a backup under `backups/` (`NFR-REL-003`); a schema
  change that is not purely additive needs an ADR.
- Block IDs are ULIDs that never change; span IDs survive author edits through diff-anchored re-segmentation
  (`INV-10`). Segmentation and anchoring stay pure functions with property tests.
- Provenance survives edits and exports (`INV-06`); runs keep snapshots before and after and roll back their
  mechanical edits in one action (`INV-05`); one open run per manuscript (`INV-04`).
- Only `storage` touches the filesystem; `ledger`, `style`, `provenance`, `export` and `import` depend on `model`
  and `event` only; model types have no `pub` fields.
- Parsers run with memory and time limits and never panic on malformed input (`NFR-SEC-005`); timestamps are UTC
  RFC 3339 in storage.
