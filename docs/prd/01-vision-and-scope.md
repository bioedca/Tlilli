# 01 · Vision and scope

## 1. Product summary

Tlilli is a local-first desktop editor for scientific manuscripts that turns any MCP-capable coding agent into a disciplined co-editor. The author writes in black ink. The agent, connected over the Model Context Protocol, may only propose: suggestions with alternatives, comments, verified citations and a short allow-list of mechanical fixes. Accepting a proposal turns red ink black, and the manuscript remembers which was which.

The app owns four things an agent needs and a chat window never has: the manuscript as structured, addressable text (sections, blocks, sentence spans with stable IDs); the citation ledger (sources, full text, claim links); the style sheet; and the run history. Work is marked up in the text and sent as a batch; there is no prompt box, no model host, no cloud service.

## 2. Problem and goals

The concept names four pains of writing with today's assistants. Each maps to a rule the software enforces rather than a guideline the agent is asked to follow.

| Pain | Goal | Enforced by |
| --- | --- | --- |
| Lost context between pastes | The manuscript is the context | Whole manuscript, style sheet and ledger exposed as MCP resources; every request carries its anchor (`FR-02-0xx`) |
| Re-explaining sources | Sources are objects, not strings | Ledger entries with metadata, full text and claim links (`FR-03-0xx`) |
| Unrequested rewrites | Red ink only where asked | Write tools refuse targets outside the frozen queue or standing-check scope (`INV-03`) |
| No audit trail | Every run is a ledger entry | Snapshots before and after, frozen queue, tool-call log, report, one-action rollback (`INV-05`) |

**G1.** An author can complete a mark-up → send → review cycle on a real manuscript section in under ten minutes of their own time, with no copy-paste.
**G2.** No agent action ever changes author text without an explicit accept; the system makes this impossible, not merely discouraged.
**G3.** Every sentence in an exported manuscript carries machine-readable provenance (author, agent-accepted, mechanical, mixed) and the export can produce an AI-use disclosure the author edits.
**G4.** The agent protocol is a public contract that any MCP client can implement; the product never prefers a model or vendor.
**G5.** Data never leaves the author's machine except for network calls the author initiates (identifier resolution, full-text retrieval) and the agent's own traffic.
**G6.** The project is open source from the first public release and sustainable for a solo maintainer with AI agents doing most implementation work, under the process defined in this PRD.

## 3. Non-goals (explicitly out of scope)

- **Not a chat.** No prompt box, no free-form conversation, no streaming tokens into the document.
- **Not a model host.** No API keys, no model picker, no inference in-process. Whatever agent subscription the author already pays for does the thinking. Local models are supported only in the sense that any MCP client with a local model already works.
- **Not a reference manager.** A per-manuscript ledger and import from identifiers, PDFs and (v0.5) Zotero. No library management, no sync, no browser connector.
- **Not a cloud service.** No accounts, no server, no telemetry, no analytics. The ChatGPT connector (v0.5) is a user-run tunnel to the user's own machine.
- **Not a literature search engine.** Search belongs to the agent's own MCP configuration (PubMed, Semantic Scholar, Scite, bioRxiv servers). Tlilli ships the ledger, not search.
- **Not a general word processor.** Document types are research article, reviewer response and cover letter. Slides, grants and theses are not targets before v1.0.
- **Not real-time collaborative.** One author edits at a time; co-authors receive exports (docx with comments, LaTeX, PDF).
- **Not mobile.** Desktop only: macOS, Windows, Linux.

## 4. Personas

| Persona | Who | Needs from Tlilli | Primary phases |
| --- | --- | --- | --- |
| **Author** | A scientist (postdoc, PI, graduate student) writing or revising a manuscript, often in a second language, with an existing Claude Code, Codex or ChatGPT subscription | Fast mark-up, trustworthy suggestions with alternatives, verified citations, exports co-authors and journals accept, complete control over every word | all |
| **Agent** | An MCP client acting for the author under a skill pack | Addressable text, unambiguous requests, narrow write tools with clear refusals, labelled untrusted input, a report format | v0.2+ |
| **Co-author / reviewer** | Receives exports; may never install Tlilli | docx with comments and (later) tracked changes, provenance summary, consistent references | v0.4+ |
| **Maintainer** | bioedca, sole human with merge rights | A process where agents do the implementation and review work and the human decides only at defined gates | Phase 0+ |
| **Contributor** | External developer or skill author after v1.0 | Clear CONTRIBUTING, forks and PRs, same automated review, good first issues | v1.0+ |
| **Packager** | Homebrew, winget, Flathub, crates.io consumers | Reproducible release artifacts, checksums, provenance attestations, SemVer | v1.0+ |

## 5. Invariants

Invariants hold in every phase from the moment the feature they govern exists. A violation is a `priority/P0` bug and blocks any release.

| ID | Invariant | Where enforced | Verified by |
| --- | --- | --- | --- |
| `INV-01` | **The author holds the pen.** No MCP tool, skill or import path writes author text. Agents produce suggestions, comments, proposed sources and allow-listed mechanical edits only | `tlilli-core` event validation; `tlilli-mcp` tool set | Property tests over all tool inputs; contract tests; fuzzing of tool inputs |
| `INV-02` | **Every change is an event.** The UI and the MCP server emit events through the same core API; no state lives only in the view or only in the server | `tlilli-core` event log; UI transactions map 1:1 to events | Property test: replay(log) equals materialized state; UI integration tests |
| `INV-03` | **Red ink only where asked.** Every write tool requires a claimed run and a target inside the frozen queue or a standing-check scope; other targets are refused with a hint to comment | `tlilli-mcp` guardrails | Unit and contract tests per tool; fuzzing |
| `INV-04` | **One open run per manuscript.** The manuscript is read-only to the author while a run is open; author comments typed during a run queue for the next | `tlilli-core` run state machine | State-machine property tests; e2e smoke |
| `INV-05` | **Runs are complete and reversible.** Snapshot before and after, frozen queue, full tool-call log, report; rollback of a run's mechanical edits is one action | `tlilli-core` run/snapshot model | Snapshot and property tests; gate test |
| `INV-06` | **Provenance is recorded per span.** Author, agent-accepted (run, alternative, edited-before-accept), agent-mechanical or mixed; preserved across edits and exports | `tlilli-core` provenance marks | Property tests under random edits; export snapshot tests |
| `INV-07` | **Untrusted text is labelled.** Source full text, PDFs and reviewer comments are marked untrusted in every resource and never executed as instructions by the app | `tlilli-mcp` resources; skills | Contract tests on resource envelopes; skill review |
| `INV-08` | **Local-first.** One workspace folder, SQLite plus files, no telemetry, works offline except for author-initiated resolver calls | Architecture; NFR-PRIV | Network allow-list tests; offline e2e |
| `INV-09` | **Agent-agnostic by contract.** The MCP surface and skill pack are the product; no code path depends on a model or vendor | Architecture review | Contract tests run against at least two clients at each gate |
| `INV-10` | **Stable identity.** Block IDs are ULIDs that never change; span IDs survive author edits by diff-anchored re-segmentation | `tlilli-core` segmentation | Property tests on revision corpora; gate metric |

## 6. Success metrics

Measured at gate tests on the maintainer's own manuscripts, recorded in the gate test report issue.

| Metric | Target | From |
| --- | --- | --- |
| Author time per cycle (mark-up + review, excluding agent time) for a 3-request run | ≤ 10 min | v0.2 |
| Agent turn wall-clock for a 3-request run on an Introduction | ≤ 5 min typical; ≤ 30 min hard timeout | v0.2 |
| Span-ID survival across a real revision history (IDs that keep their sentence after a full author pass) | ≥ 99% of unchanged sentences; 100% of locked spans | v0.1 |
| Author-text overwrites by an agent | 0, ever | v0.2 |
| Suggestions accepted (any alternative, with or without edit) per run on a real manuscript | ≥ 50% | v0.2 |
| Claim links verified with a correct status on a 20-citation sample judged by the author | ≥ 90% agreement | v0.3 |
| Consistency sweep true positives on a seeded manuscript (10 planted errors) | ≥ 8 found; ≤ 3 false positives | v0.4 |
| docx export opened without repair prompts in Word and LibreOffice; comments visible | 100% of gate manuscripts | v0.4 |
| Installer start-to-first-manuscript on a clean machine per OS | ≤ 5 min, documented bypass included | v1.0 |
| Process: median PR lead time (open → merged) for agent PRs | ≤ 24 h | Phase 0+ |
| Process: PRs merged with zero human intervention on ungated paths | ≥ 80% | Phase 0+ |

## 7. Assumptions

- A1. The maintainer is the only human committer through v1.0; agents (Claude Code cloud and local, Codex CLI and cloud) author most code under the rules in [30](30-git-workflow.md)–[34](34-testing.md).
- A2. Agent review budgets: Codex via ChatGPT Pro (rounds not scarce), CodeRabbit Open Source plan (rate-limited), Greptile one paid seat (≈15–20 deep reviews per month). See [32](32-code-review.md).
- A3. No money is available for code signing or notarization. Trust is established with checksums, Sigstore build attestations and the updater's minisign signatures. See [37](37-releases-and-packaging.md).
- A4. GitHub-hosted runners are free for the public repository; macOS and Windows jobs are slow and run only on Ready PRs and `main`.
- A5. The repository stays on the maintainer's personal account (`bioedca/Tlilli`), whose GitHub Pro plan comes from the Student Developer Pack. Organization-only features (merge queue, teams, organization rulesets) are not used, and no required capability depends on Pro, which only enlarges quotas ([D-057](41-risks-and-decision-log.md), [39](39-github-configuration.md) §6). An organization move is revisited only when contributions or funding cover it.
- A6. Authors already hold an agent subscription; Tlilli never needs its own API key.
- A7. The cloud development sandbox has no display, 4 vCPU, 16 GB RAM, 30 GB disk, raised Bash timeouts, and GitHub access scoped to this repository; dependencies therefore come from crates.io and npm releases only.

## 8. Constraints

- C1. **Local-first and private** by design (INV-08, NFR-PRIV). The only outbound traffic from the app is author-initiated resolver calls to a fixed list of hosts.
- C2. **Rust is the only source of truth** for the document; the ProseMirror view is a projection (INV-02).
- C3. **Dependencies from crates.io and npm only.** No `git =` dependencies, no vendored forks without an ADR.
- C4. **No secrets in the repository or environment variables**; release secrets live in GitHub Actions environments.
- C5. **Licenses:** Apache-2.0 for the application and crates, MIT for `skills/`. Dependencies must be compatible (checked by `cargo-deny`).
- C6. **Agent protocol stability:** from v0.2 the MCP tool and resource schemas are versioned; breaking changes follow the deprecation policy in [38](38-maintenance-and-support.md).
- C7. **Solo-maintainer bandwidth:** human review is reserved for gated paths; everything else must merge on automated evidence.

## 9. Release phases at a glance

| Phase | Name | Closes with | Gate (summary) |
| --- | --- | --- | --- |
| 0 | Foundation | Repo scaffolding, account and repository settings, CI green on skeleton workspace | A hello-world Tauri build passes every required check |
| v0.1 | Black ink | Tag `v0.1.0` | Import, edit, mark up, snapshot and export a real manuscript; span IDs stable |
| v0.2 | Red ink | Tag `v0.2.0` | Run 7 scenario end to end with Claude Code and Codex |
| v0.3 | Ledger | Tag `v0.3.0` | 20 citations resolved, linked and verified on a real manuscript |
| v0.4 | Sweep and style | Tag `v0.4.0` | Style sheet applied, sweep finds planted errors, docx/LaTeX/PDF exports accepted by co-author |
| v0.5 | Beyond the article | Tag `v0.5.0` | Reviewer response drafted and cross-linked; ChatGPT connector works through the tunnel |
| v1.0 | Public | Tag `v1.0.0` | Clean-machine installs on three OSes, docs site complete, trademark cleared, skills installer works |

Details, exit criteria and gate scripts: [40 Roadmap and gates](40-roadmap-and-gates.md). No dates are committed until v0.1 ships and velocity is known (concept decision, kept).
