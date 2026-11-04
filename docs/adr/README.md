# Architecture decision records

This folder holds Tlilli's architecture decision records (ADRs): the decisions that lock a technology, a storage format, a trust boundary or a deviation from the PRD, written so that a reader who was not there can see the context, the decision, its consequences and the alternatives. The product rationale lives in the concept document ([Tlilli — Concept & Definition](https://github.com/bioedca/Tlilli/blob/main/Tlilli%20-%20Concept%20%26%20Definition.md), at the repository root) and the requirements in the [PRD](../prd/README.md); an ADR cites both by ID and does not restate them. The process is defined in [PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records) and [PRD 35](../prd/35-documentation.md) (`PR-DOC-009`).

## When an ADR is required

[PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records) requires an ADR for: a new native or binary dependency (`PR-ARCH-002`); a sidecar (`PR-ARCH-004`); a storage schema change that is not purely additive; a breaking MCP change; a deviation from the PRD; a change to the trust boundary. Anything the PRD marks **locked** changes only through an ADR plus a decision-log entry ([PRD 41 §2](../prd/41-risks-and-decision-log.md#2-decision-log)). An ADR that changes what the PRD says needs a `D-nnn` entry and matching PRD text. The [PRD README](../prd/README.md) ("Deviations are decisions") says that a deviation "is recorded as a dated entry in the decision log before or with the change, and the PRD text is updated in the same PR": the entry and the PRD text land in one pull request. The change is the ADR's acceptance, not its draft: a Proposed ADR decides nothing yet (Status lifecycle below), so it does not yet deviate from the PRD. A Proposed ADR therefore lists each PRD change it needs, with the issue or pull request that carries it, under [PRD changes pending](#prd-changes-pending). The PRD amendment and its `D-nnn` entry merge before, or in the same pull request as, the commit that marks the ADR Accepted; no ADR is marked Accepted while a change it lists is unmerged.

## Format

MADR, one file per decision at `docs/adr/NNNN-short-title.md` (lower-case, hyphens). Sections, in this order: title, status block, Context, Decision, Consequences (positive, negative, risks), Alternatives considered, References (requirement IDs, decisions, threats, other ADRs). Every statement in an ADR traces to the PRD or the concept document; where the PRD leaves a choice open, the ADR says so, records the option taken and names the alternatives. Keep an ADR short enough to read in one sitting.

## Status lifecycle

```text
Proposed ──▶ Accepted ──▶ Superseded by ADR-mmmm
```

- **Proposed.** The ADR is drafted in a pull request, by an agent or a person ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records): "an agent drafts; the maintainer accepts"). `docs/adr/**` is a gated path ([PRD 32 §3](../prd/32-code-review.md#3-human-review-scoped-gates)), so the PR needs the maintainer's approval to merge (`PR-PRQ-006`, `PR-DOC-017`). The rule is enforced once the path labeler (pull request 44) and the `gate/maintainer` check with `CODEOWNERS` (pull request 54) are on `main`; until then it is kept by hand.
- **Accepted.** The maintainer's approval and merge of the pull request records acceptance; nothing else does. The `Accepted` status is written before the merge: the last commit of the pull request (`docs(docs): mark ADR-nnnn accepted`, made by the maintainer or by the drafting agent at the maintainer's request) sets `**Status:** Accepted` and the acceptance date in the ADR and in the index, and the maintainer approves the head that carries it. That commit is made only when every PRD change the ADR lists under [PRD changes pending](#prd-changes-pending) has merged or is in the same pull request, and it removes the ADR's rows from that table. No ADR is merged reading `Proposed`. From the merge on, the ADR is immutable ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records), `PR-DOC-009`): its text never changes again, the status line changes only for the Superseded step below, and any correction is a new ADR.
- **Superseded.** A later ADR replaces it. The old file gets `**Status:** Superseded by ADR-mmmm` and no other change; the new ADR names what it supersedes and why.

A draft the maintainer declines is closed with its pull request, and nothing is merged.

## Numbering

Four digits, sequential. A number that appears in the index or in a merged ADR is never reused; a number held only by a declined, unmerged draft may be reused. The next number is the highest in the index plus one. ADR-0007 is reserved for the PDF extraction strategy, which the PRD decides at gate G3 ([PRD 21 §6](../prd/21-architecture-and-tech-stack.md#6-architecture-decision-records), R-16).

## PRD changes pending

The PRD changes that the Proposed records need, each with the pull request or issue that carries it. A row leaves the table when its change merges, or with the commit that marks the ADR Accepted when the change travels in the ADR's own pull request. The pull request that adds ADR-0001 to ADR-0006 therefore merges after pull request 52 and after the PRD round-3 amendment for issue 55, unless it carries that amendment itself.

| ADR | PRD change | Carried by |
| --- | --- | --- |
| ADR-0001 | [PRD 37 §2](../prd/37-releases-and-packaging.md#2-release-flow-stable) sample `release-plz.toml` and [PRD 21 §2](../prd/21-architecture-and-tech-stack.md#2-repository-layout-locked): `tlilli-mcp` and `tlilli-cli` carry `publish = false` until v0.2 (`PR-REL-024`) | issue 55 |
| ADR-0003 | [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) Citations and LaTeX rows and [PRD 13](../prd/13-fr-v0.4-sweep-and-style.md) `FR-04-041`: BibTeX export through a Tlilli-owned mapping and the `biblatex` crate's writer, not `hayagriva`; a new `D-nnn` entry | issue 55 |
| ADR-0004, ADR-0006 | [PRD 20](../prd/20-non-functional-requirements.md) `NFR-REL-001`: `synchronous=FULL` for the workspace database (D-066) | pull request 52 |
| ADR-0004, ADR-0006 | [PRD 10](../prd/10-fr-v0.1-black-ink.md) `FR-01-030`: permanent deletion removes a manuscript's whole chain in one transaction and is recorded in the workspace chain | issue 55 |
| ADR-0005 | Tunnel provider traffic outside `NFR-SEC-004` (D-065) | pull request 52 |
| ADR-0005 | [PRD 22](../prd/22-security-and-threat-model.md) tunnel threat (T-04 extended, or a new T-16) and `NFR-SEC-006`: the tunnel program is a trust boundary; its path, SHA-256 and version are confirmed before it runs, and again on any change | issue 55 |
| ADR-0006 | [PRD 10](../prd/10-fr-v0.1-black-ink.md) `FR-01-012`: a locked span keeps its ID through any author edit confined to it | issue 55 |
| ADR-0006 | [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) Editor row: "transactions map 1:1 to core events" becomes one commit group of one or more events per transaction (`FR-01-020`) | issue 55 |

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
| [ADR-0008](0008-tauri-dependency-footprint.md) | The Tauri 2 dependency footprint of the desktop shell | Proposed | 2026-11-04 |

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
