# Architecture decision records

This folder holds Tlilli's architecture decision records (ADRs): the decisions that lock a technology, a storage format, a trust boundary or a deviation from the PRD, written so that a reader who was not there can see the context, the decision, its consequences and the alternatives. The product rationale lives in the concept document ([Tlilli — Concept & Definition](https://github.com/bioedca/Tlilli/blob/main/Tlilli%20-%20Concept%20%26%20Definition.md), at the repository root) and the requirements in the [PRD](../prd/README.md); an ADR cites both by ID and does not restate them. The process is defined in [PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records) and [PRD 35](../prd/35-documentation.md) (`PR-DOC-009`).

## When an ADR is required

[PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records) requires an ADR for: a new native or binary dependency (`PR-ARCH-002`); a sidecar (`PR-ARCH-004`); a storage schema change that is not purely additive; a breaking MCP change; a deviation from the PRD; a change to the trust boundary. Anything the PRD marks **locked** changes only through an ADR plus a decision-log entry ([PRD 41 §2](../prd/41-risks-and-decision-log.md#2-decision-log)). An ADR that changes what the PRD says appends its `D-nnn` entry and updates the PRD text in the same pull request ([PRD README](../prd/README.md), "Deviations are decisions").

## Format

MADR, one file per decision at `docs/adr/NNNN-short-title.md` (lower-case, hyphens). Sections, in this order: title, status block, Context, Decision, Consequences (positive, negative, risks), Alternatives considered, References (requirement IDs, decisions, threats, other ADRs). Every statement in an ADR traces to the PRD or the concept document; where the PRD leaves a choice open, the ADR says so, records the option taken and names the alternatives. Keep an ADR short enough to read in one sitting.

## Status lifecycle

```text
Proposed ──▶ Accepted ──▶ Superseded by ADR-mmmm
```

- **Proposed.** The ADR is drafted in a pull request, by an agent or a person ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records): "an agent drafts; the maintainer accepts"). `docs/adr/**` is a gated path, so the path labeler applies `gate` and the PR cannot merge without the maintainer's approval (`PR-PRQ-006`, `PR-DOC-017`).
- **Accepted.** The maintainer's approval and merge of the pull request records acceptance; nothing else does. The merged file still reads `Proposed`; a follow-up editorial commit (`docs(docs): mark ADR-nnnn accepted`, gated like any change under `docs/adr/`) sets `**Status:** Accepted` and the acceptance date. After that the ADR is immutable: typo fixes are the only other edit it receives.
- **Superseded.** A later ADR replaces it. The old file gets `**Status:** Superseded by ADR-mmmm` and no other change; the new ADR names what it supersedes and why.

A draft the maintainer declines is closed with its pull request; nothing is merged and its number becomes free again.

## Numbering

Four digits, sequential, never reused. The next number is the highest in the index plus one. ADR-0007 is reserved for the PDF extraction strategy, which the PRD decides at gate G3 ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records), R-16).

## Index

The PRD plans a generated index page (`PR-DOC-009`); until that generator exists this table is kept by hand in the PR that adds or changes an ADR. The MkDocs navigation for this folder is added by bootstrap task 28.

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [ADR-0001](0001-repository-layout-and-cli.md) | Repository layout and the `tlilli` command-line interface | Proposed | 2026-11-04 |
| [ADR-0002](0002-rmcp-for-the-mcp-server.md) | `rmcp` for the MCP server | Proposed | 2026-11-04 |
| [ADR-0003](0003-hayagriva-for-bibliography.md) | `hayagriva` for citations and bibliography | Proposed | 2026-11-04 |
| [ADR-0004](0004-storage-schema-v1-and-migrations.md) | Storage schema v1 and migration policy | Proposed | 2026-11-04 |
| [ADR-0005](0005-sidecar-policy-and-tunnel-exception.md) | Sidecar policy and the tunnel exception | Proposed | 2026-11-04 |
| [ADR-0006](0006-event-log-hash-chain-and-snapshot-cadence.md) | Event-log hash chain and snapshot cadence | Proposed | 2026-11-04 |
| ADR-0007 | PDF extraction strategy | Reserved; decided at gate G3 | — |

## Template

```markdown
# ADR-NNNN: Short title

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **Deciders:** bioedca (maintainer). Drafted by <agent or person>, <issue or task>.

## Context

What forces the decision: the concept and PRD statements it serves, by ID.

## Decision

What is decided, in the present tense. Where the PRD leaves a choice open, say so and name the option taken.

## Consequences

### Positive

### Negative

### Risks

## Alternatives considered

One bullet per alternative: what it is, why it was not chosen.

## References

Concept sections; PRD files and sections; requirement IDs; decisions (D-nnn); risks (R-nn); threats (T-nn); related ADRs.
```
