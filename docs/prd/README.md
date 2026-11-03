# Tlilli Product Requirements Document (PRD)

**Status:** Draft 1 (2026-11-03) · **Owner:** bioedca (sole maintainer) · **Governs:** build, release and maintenance of Tlilli from Phase 0 through v1.0 and the post-1.0 maintenance cycle.

This PRD is the single tracking source for the project. The concept document ([Tlilli — Concept & Definition](../../Tlilli%20-%20Concept%20%26%20Definition.md)) states what Tlilli is and why; this PRD turns every statement in it into a numbered, testable requirement and adds the complete engineering process the project runs on: git workflow, pull requests, code review, CI/CD, testing, documentation, issue tracking, project management, packaging, releases, maintenance and GitHub configuration.

The process sections follow the [INTERSECT research-software curriculum](https://intersect-training.org/curriculum/) (Collaborative Git, Making Good PRs, Code Review, CI/CD, Testing, Documentation, Issue Tracking, Project Management, Packaging, Licensing, Software Design, Building a Community, Threat Assessment). Where INTERSECT states a rule, this PRD adopts it and says where. Where this project deviates, the deviation is recorded in the [decision log](41-risks-and-decision-log.md).

## Document map

| File | Contents |
| --- | --- |
| [01 Vision and scope](01-vision-and-scope.md) | Product summary, goals, non-goals, personas, invariants, success metrics, assumptions, constraints |
| [10 FR v0.1 Black ink](10-fr-v0.1-black-ink.md) | Functional requirements: editor, document model, markup, snapshots, import/export; no agent |
| [11 FR v0.2 Red ink](11-fr-v0.2-red-ink.md) | MCP server, run lifecycle, suggestion tools, review pane, provenance, first skills |
| [12 FR v0.3 Ledger](12-fr-v0.3-ledger.md) | Sources, full text, claim links, verification, citation export |
| [13 FR v0.4 Sweep and style](13-fr-v0.4-sweep-and-style.md) | Style sheet, consistency sweep, mechanical edits, figures, docx/LaTeX/PDF export |
| [14 FR v0.5 Beyond the article](14-fr-v0.5-beyond-the-article.md) | Methods from protocols, reviewer response, cover letter, shared pool, Zotero, ChatGPT |
| [15 FR v1.0 Public](15-fr-v1.0-public.md) | Installers, docs site, skill installer, sample manuscript, public-release checklist |
| [20 Non-functional requirements](20-non-functional-requirements.md) | Performance, reliability, privacy, accessibility, portability, compatibility, observability |
| [21 Architecture and tech stack](21-architecture-and-tech-stack.md) | Locked technology decisions, crate layout, dependency policy, ADR process |
| [22 Security and threat model](22-security-and-threat-model.md) | Threat assessment (INTERSECT method), trust boundaries, mitigations, disclosure |
| [30 Git workflow](30-git-workflow.md) | Branching, naming, commits, DCO, rebase-merge, rulesets, merge queue, agent rules |
| [31 Pull requests](31-pull-requests.md) | Draft vs Ready, PR template, size cap, auto-merge, labels an agent may apply |
| [32 Code review](32-code-review.md) | Codex → CodeRabbit → Greptile pipeline, human gates, CODEOWNERS, severity, etiquette |
| [33 CI/CD](33-ci-cd.md) | Every workflow, job, trigger, required check, secret and schedule |
| [34 Testing](34-testing.md) | Test layers, mandatory techniques, fixtures, coverage, agent TDD rules |
| [35 Documentation](35-documentation.md) | MkDocs site, Diátaxis structure, generated protocol reference, sync rules, ADRs, changelog |
| [36 Issues, labels and projects](36-issues-labels-and-projects.md) | Issue forms, label scheme, milestones, Projects board, triage, definitions of Ready and Done |
| [37 Releases and packaging](37-releases-and-packaging.md) | Versioning, release-plz, tauri-action, artifacts, zero-cost trust posture, updater, channels |
| [38 Maintenance and support](38-maintenance-and-support.md) | Support matrix, backports, security response, deprecation, diagnostics, bus factor |
| [39 GitHub configuration](39-github-configuration.md) | Organization, repository settings, rulesets, apps, secrets inventory, GitHub Pro perks |
| [40 Roadmap and gates](40-roadmap-and-gates.md) | Phases 0 to 1.0, exit criteria, gate test procedure, release mapping |
| [41 Risks and decision log](41-risks-and-decision-log.md) | Risk register and every decision taken for this PRD, dated |
| [42 Bootstrap backlog](42-bootstrap-backlog.md) | The first issues to open, in order, with labels and requirement references |

## How to use this PRD

1. **Issues cite requirement IDs.** Every issue of type feature, task or bug names the FR, NFR or PR rule it implements or violates. Issues without an ID are triaged to one or closed as out of scope.
2. **Gate tests check requirements off.** A roadmap phase closes when its gate test ([40](40-roadmap-and-gates.md)) passes on the tagged release build and every FR of that phase is either verified or explicitly deferred in the decision log.
3. **Agents read this PRD.** `CLAUDE.md` and `AGENTS.md` point here; the process sections are binding on agent-authored work exactly as on human work (INTERSECT Collaborative Git: agent configuration files are context, so the rules must be stated where agents read them).
4. **Deviations are decisions.** Anything the project does differently from this PRD is recorded as a dated entry in the decision log before or with the change, and the PRD text is updated in the same PR.

## Requirement identifiers

| Prefix | Meaning | Example |
| --- | --- | --- |
| `INV-nn` | Invariant that holds in every phase; violating one is a P0 bug | `INV-01` the author holds the pen |
| `FR-<phase>-<nnn>` | Functional requirement, phase `01` to `05` and `10` for v1.0 | `FR-02-014` |
| `NFR-<AREA>-<nnn>` | Non-functional requirement; areas PERF, REL, SEC, PRIV, USE, PORT, COMPAT, OBS, I18N | `NFR-PERF-003` |
| `PR-<AREA>-<nnn>` | Process rule; areas GIT, PRQ, REV, CI, TST, DOC, ISS, REL, MNT, GH | `PR-REV-007` |
| `D-nnn` | Decision in the decision log | `D-012` |
| `R-nn` | Risk in the risk register | `R-07` |
| `ADR-nnnn` | Architecture decision record under `docs/adr/` | `ADR-0003` |

Requirement language follows RFC 2119: **MUST** and **MUST NOT** are binding, **SHOULD** needs a written reason to skip, **MAY** is optional. Every FR carries acceptance criteria and a verification method (unit, property, snapshot, contract, e2e, gate or manual).

## Change control

- The PRD lives in the repository and is versioned with it. Changes go through the normal pull-request flow; `docs/prd/**` is a human-gated path (see [32](32-code-review.md)), so the maintainer approves every change.
- Editorial fixes (typos, links) are `docs(prd):` commits and need no decision-log entry. Any change to a MUST, a gate criterion, a tool choice or a budget is a decision and gets a `D-nnn` entry.
- The PRD is re-baselined at each roadmap gate: requirements verified by the gate test are marked `✅ verified vX.Y.Z` in place, deferred ones are moved to the next phase with a decision entry.
- A PRD "version" is the git history; the status line at the top records the draft number and date of the last re-baseline.

## Terminology

Three Nahuatl terms are used in the product and this document: **Tlilli** (the app; black ink, the author's text), **Tlapalli** (the suggestion layer; red ink, what an agent proposes), **amoxtli** (a manuscript). Everything else is plain English. "Agent" means any MCP client acting for the author (Claude Code, Codex, ChatGPT). "Maintainer" means the human with merge rights, currently bioedca alone. "Gated path" means a repository path whose changes require maintainer approval.
