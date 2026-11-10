# 40 · Roadmap and gates

Concept rule kept: **a phase ends when its test passes on a real manuscript, not when its features are merged**, and **no dates are committed until v0.1 ships and the pace is known**. Added by this PRD (D-034): each phase ends with a tagged `v0.X.0` release; the gate test runs on that release build; the result is filed as a Gate test report issue; the milestone closes only on a pass; a failed gate produces fix issues and a `v0.X.1`.

## 1. Phases

| Phase | Milestone | FR file | Process deliverables | Release | Gate |
| --- | --- | --- | --- | --- | --- |
| 0 | `0 Foundation` | — | Everything in [42](42-bootstrap-backlog.md): account and repository settings, licenses, CODEOWNERS, rulesets, labels, forms, templates, workflows, reviewer apps, docs skeleton, devcontainer, companion repo, initial ADRs, trademark search started | none (CI artifacts) | G0 |
| v0.1 | `v0.1 Black ink` | [10](10-fr-v0.1-black-ink.md) | Trademark search complete (D-035); `tlilli-core` published to crates.io; tutorial "first manuscript" | `v0.1.0` | G1 |
| v0.2 | `v0.2 Red ink` | [11](11-fr-v0.2-red-ink.md) | Discussions on; updater key generated; `tlilli-mcp`, `tlilli-cli` on crates.io; agent how-tos; beta channel first used | `v0.2.0` | G2 |
| v0.3 | `v0.3 Ledger` | [12](12-fr-v0.3-ledger.md) | Network allow-list test; ADR-0007 (PDF extraction) decided | `v0.3.0` | G3 |
| v0.4 | `v0.4 Sweep and style` | [13](13-fr-v0.4-sweep-and-style.md) | Mutation score ≥ 70% on core; LaTeX nightly compile; Linux arm64 experimental builds | `v0.4.0` | G4 |
| v0.5 | `v0.5 Beyond the article` | [14](14-fr-v0.5-beyond-the-article.md) | ChatGPT plan matrix re-checked and documented; tunnel ADR exception | `v0.5.0` | G5 |
| v1.0 | `v1.0 Public` | [15](15-fr-v1.0-public.md) | Homebrew, winget, Flathub; versioned docs; GOVERNANCE successor and backup admin; newcomer dry run; Scorecard ≥ 7 | `v1.0.0` | G6 |
| post-1.0 | `post-1.0` | — | Maintenance per [38](38-maintenance-and-support.md); SignPath application; JOSS; tracked changes in docx; Zotero write-back | `v1.x` | per minor: smoke journey on each channel |

## 2. Gate procedure (PR-GATE-001 … 008)

| ID | Rule |
| --- | --- |
| `PR-GATE-001` | The gate runs on the **published release build** (draft published after `verify` passes), installed from the GitHub Release on at least the maintainer's primary OS, and on all three OSes for G6. |
| `PR-GATE-002` | The manuscript is a **real manuscript of the maintainer's** (or a co-author's with consent); the report records only metrics and redacted notes, never text. The maintainer decides which agent vendor may see which manuscript (INTERSECT GenAI guidance on unpublished data). |
| `PR-GATE-003` | The script is `docs/gates/G<n>.md`, written before the phase starts (it is the acceptance test suite of the phase), updated during the phase in gated PRs, and followed literally at the gate. |
| `PR-GATE-004` | Each script step maps to FR IDs; the report marks each FR **verified**, **failed** or **deferred (D-nnn)**. All `INV-*` applicable to the phase are checked explicitly. |
| `PR-GATE-005` | Verdict **pass** requires: no failed step that maps to a MUST; every success metric for the phase ([01](01-vision-and-scope.md) §6) met or explicitly waived with a decision entry; no open `priority/P0`/`P1` in the milestone. |
| `PR-GATE-006` | Verdict **fail** opens fix issues (`priority/P1`, same milestone), the fixes ship as `v0.X.1` (or `.2`…), and the gate is re-run on that build. The milestone stays open. |
| `PR-GATE-007` | After a pass: close the milestone; file the retrospective; re-baseline the PRD (mark verified FRs, move deferrals); announce in Discussions (from v0.2). |
| `PR-GATE-008` | Velocity (merged PRs per week, FRs verified per phase, lead time) is recorded in each report; from G1 on, a projection for the next phase is written in the retro, labelled as a projection, never a commitment. |

## 3. Gate scripts (outline; full scripts live in `docs/gates/`)

### Gate G0 (Phase 0 Foundation)
1. Account and repository settings per [39](39-github-configuration.md) (2FA, successor, Actions allow-list, rulesets, labels, forms, templates present); the audit checklist passes.
2. A hello-world workspace (`crates/*` skeletons, `src-tauri`, `ui`) builds; `ci.yml` green with every required check reporting; a Draft PR by an agent (local or cloud session, D-078) goes through Codex → (CodeRabbit when labelled `review:coderabbit`, D-089) → Ready → auto-merge or the agent's merge (branch up to date) → `main` with zero human clicks (ungated path), and a second PR touching a gated path is blocked until `gate:approved` (without the label, only the admin bypass on a relayed authorization recorded in the PR body can merge it, `PR-GIT-058`).
3. `release.yml` rehearsed in the companion repo with `dry_run=true`; `docs.yml` deploys the skeleton site.
4. DCO, commitlint, size, docs-sync, zizmor, Scorecard all report.

### Gate G1 (v0.1.0 Black ink)
1. Install `v0.1.0` from the draft→published release (unsigned bypass documented) — `FR-10-003` draft text used.
2. Create a workspace; import the maintainer's current draft from docx and from Markdown; import report lists unsupported constructs (`FR-01-040..041`).
3. Edit for a 45-minute session: paragraphs, headings, a figure drop, a table; undo/redo across a restart (`FR-01-020`).
4. Mark up 10 requests across sentence/paragraph/section levels with Cmd/Ctrl-K; lock two spans; add two idea stubs (`FR-01-021`, `FR-01-013`).
5. Send → run opens → cancel → requests preserved (`FR-01-022`).
6. Snapshot, edit a full pass over one section, diff; measure span-ID survival on the real revision (≥ 99%) (`FR-01-012`, metric).
7. Export Markdown with and without markers; canonical export; re-import; byte-identical canonical JSON (`FR-01-042..043`).
8. Kill the app during typing; relaunch; integrity check passes; ≤ 1 s loss (`NFR-REL-001..002`).
9. Keyboard-only pass and axe audit on all screens (`NFR-USE-001..002`); dark/light.
10. Diagnostics bundle produced and inspected for redaction (`NFR-PRIV-003`).
11. Trademark search result recorded (D-035); `tlilli-core` on crates.io.

### Gate G2 (v0.2.0 Red ink)
1. Install `v0.2.0`; enable the MCP server; connect Claude Code via stdio and Codex CLI via HTTP with the token (`FR-02-010..012`).
2. Run 7 scenario on the Introduction with Claude Code: 3 requests + untagged comment; agent turn ≤ 5 min; report; review: accept edited alternative, accept stub draft, reject move with redo, close (`FR-02-001..045`).
3. Repeat with Codex; compare behaviour; both skill packages installed by copying (installer at v1.0).
4. Attempt forbidden actions from a scripted client: write without claim, out-of-scope target, locked span, 4 alternatives, missing rationale, oversize payload: all refused (`INV-01`, `INV-03`, `FR-02-030..036`).
5. Timeout drill: stop the agent mid-run; run times out at the configured 5 min; suggestions stay as red ink; editor unlocks (`NFR-REL-004`).
6. Rollback a run; History shows diffs, report and tool log (`FR-02-044..045`).
7. Show ink: provenance marks correct; percentages per section (`FR-02-050..051`).
8. Updater: point the app at a staged `beta.json`; check, see notes, install the beta build, relaunch (`FR-02-070`); verify request carries no identifiers.
9. Metrics: author time per cycle ≤ 10 min; accepted share ≥ 50%; zero author-text overwrites.

### Gate G3 (v0.3.0 Ledger)
1. Add 10 sources by DOI/PMID, 5 by PDF drop (DOI sniffed), 5 proposed by the agent during a run; dedupe prompt exercised (`FR-03-001..005`).
2. Link 20 citations; run citation verification as a standing check with Claude Code; author judges statuses: ≥ 90% agreement (`FR-03-020..031`, metric).
3. A `contradicted` and an `unsupported` case planted; agent follow-ups present per `FR-03-013`.
4. Export CSL-JSON (opens in Zotero), BibTeX (compiles), Markdown with references in two styles and one non-English locale (`FR-03-050..052`).
5. Recording proxy confirms only allow-listed hosts contacted (`NFR-SEC-004`); offline mode queues an add and resolves later.
6. Malformed PDF fixture does not crash the app (`NFR-SEC-005`).

### Gate G4 (v0.4.0 Sweep and style)
1. Apply the target journal preset; set limits, abbreviations, terminology, auto-fix list, two locked spans (`FR-04-001..004`).
2. Plant 10 inconsistencies; run the sweep with Codex; ≥ 8 found, ≤ 3 false positives (`FR-04-010..012`, metric).
3. Accept mechanical renumbering and abbreviation fixes; revert one; cancel a run with mechanical edits → auto-reverted (`FR-04-020..022`).
4. Figures: a missing panel reference and a wrong order planted; `figure_check` finds both; caption rewrite via suggestion; image resource read by a vision-capable client (`FR-04-030..033`).
5. Export docx with comments → co-author opens in Word and LibreOffice, reads comments, returns a docx whose comments import (`FR-04-040`, `FR-04-043`).
6. LaTeX export compiles with `latexmk`; PDF via Typst renders with references (`FR-04-041..042`).
7. Provenance summary and disclosure paragraph produced and edited (`FR-04-044`).
8. Mutation score report ≥ 70% on core (`PR-TST-012`).

### Gate G5 (v0.5.0 Beyond the article)
1. Import a protocol; draft a Methods paragraph from a `protocol:` stub; provenance link to the protocol passage (`FR-05-001..003`).
2. Create a reviewer response from two reviewer reports; draft responses with Codex; cross-link; `response_check` finds a planted unfulfilled promise; export docx (`FR-05-010..013`).
3. Draft a cover letter from abstract and significance stub (`FR-05-020`).
4. Shared pool used by two manuscripts; Zotero import of a 50-item collection via Better BibTeX export and via the local API (`FR-05-030..041`).
5. ChatGPT Developer-mode connector through the tunnel: `verify-citations` prompt runs; tunnel stops with the app; token required (`FR-05-050..052`, `NFR-SEC-006`).

### Gate G6 (v1.0.0 Public)
1. Clean VMs (macOS 13 or newer arm64, Windows 11, Ubuntu 22.04): install from GitHub Release and from Homebrew/winget/Flathub respectively; verify checksums and `gh attestation verify`; first run ≤ 5 min to a completed run with the sample manuscript following the tutorial only (`FR-10-001..004`).
2. `tlilli skills install --claude-code`, `--codex`, `--chatgpt`; `--check` reports drift after editing a skill (`FR-10-010..011`).
3. Docs site: every quadrant present; search works; `latest`/`dev`; link check clean; newcomer dry run of CONTRIBUTING and setup completed by someone other than the maintainer (`FR-10-020..022`, `PR-DOC-018`).
4. Root files complete; `CITATION.cff` validates; Zenodo DOI minted on publish (`FR-10-030..032`).
5. Public-release checklist in [15](15-fr-v1.0-public.md) §5 all green; threat register reviewed; GOVERNANCE successor and backup admin named.
6. Release runbook executed literally by following the doc (bus-factor drill).

## 4. Velocity and dates

No dates before `v0.1.0`. After G1, each retrospective publishes: PRs merged per week, FRs verified, median lead time, review rounds per PR, and a projection for the next gate as a range. Projections are revised at each gate; the roadmap page on the docs site shows the current range and the last three actuals.
