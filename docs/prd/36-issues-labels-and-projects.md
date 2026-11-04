# 36 · Issues, labels and project management

INTERSECT Issue Tracking and Project Management rules adopted: one problem per issue; a good bug report has a specific title, numbered reproduction steps, expected vs actual behaviour and environment; templates embed those fields; curate the default labels to the team size; Kanban for small teams; a shared Definition of Done; the roadmap is a series of releases, the first being an MVP; verify AI-suggested labels and drafts; keep a record of how AI shaped plans.

## 1. Issue forms (`.github/ISSUE_TEMPLATE/*.yml`)

Blank issues are disabled (`config.yml`: `blank_issues_enabled: false`); contact links point to Discussions Q&A (from v0.2) and to private vulnerability reporting for security issues.

| Form | File | Auto labels | Fields (required marked *) |
| --- | --- | --- | --- |
| Bug report | `bug.yml` | `type/bug`, `status/triage` | Title prefix `[bug]`; What happened*; Steps to reproduce* (numbered); Expected*; Actual*; Tlilli version* (from About, dropdown of releases + "main build"); OS and version*; Agent and client (Claude Code / Codex / ChatGPT / none, with version); Manuscript size (words, sources); Diagnostics bundle attached? (checkbox + reminder that it is redacted); Requirement IDs if known; Logs excerpt |
| Feature request | `feature.yml` | `type/feature`, `status/triage` | User story* ("As a <role>, I want <goal>, so that <impact>"); Motivation*; Alternatives considered; Proposed acceptance criteria; Related requirement IDs; Phase suggestion (dropdown) |
| Task / chore | `task.yml` | `type/task`, `status/triage` | Goal*; Acceptance criteria* (checklist); Requirement IDs*; Area* (dropdown); Size estimate (XS–XL); Dependencies (issue links) |
| Protocol change | `protocol.yml` | `type/protocol`, `area/mcp`, `gate`, `status/triage` | Tool / resource / prompt affected*; Proposed schema (JSON)*; Guardrail impact* (scope, allow-list, limits); Backwards compatibility* (additive / deprecation / breaking); Docs and skills to update*; Transcripts to add*; ADR needed? |
| Skill change | `skill.yml` | `type/skill`, `area/skills`, `gate`, `status/triage` | Skill*; Behaviour to change*; Evidence (run log or transcript); Clients affected*; Prompt mirror affected*; Rubric impact |
| Gate test report | `gate-report.yml` | `type/gate-report`, `gate` | Phase*; Release tag tested*; Manuscript description (redacted)*; Script followed* (link to `docs/gates/G*.md`); Results per step* (pass/fail + notes); Metrics* (table from [01](01-vision-and-scope.md) §6); Verdict*; Fix issues opened |
| Retrospective | `retro.yml` | `type/retro` | Phase*; What went well*; What hurt*; Process changes proposed* (each becomes a decision or an issue); Review-lane metrics summary*; Budget use* |
| Documentation | `docs.yml` | `type/docs`, `area/docs`, `status/triage` | Page*; Problem* (wrong / missing / unclear / out of date); Diátaxis quadrant; Proposed text |
| Agent-session report | `agent-report.yml` | `type/agent-report`, `status/triage` | Agent and session kind*; Branch and PR*; Issue worked*; Done*; Not done*; Blocked by*; Next step for the next session*; Review pipeline state*; Budget notes (CodeRabbit/Greptile requests made) |

Rules:

| ID | Rule |
| --- | --- |
| `PR-ISS-001` | One problem or one feature per issue; bundles are split at triage. |
| `PR-ISS-002` | Every actionable issue carries exactly one `type/*`, at least one `area/*`, one `priority/*`, one `phase/*` (or `phase/post-1.0`), a milestone when the phase is current or next, and names requirement IDs (or gets one assigned at triage). |
| `PR-ISS-003` | Issues are closed by PRs (`Closes #N`) or at triage with a close reason (`completed`, `not planned`) and a comment; `status/duplicate` is expressed with GitHub's duplicate close reason plus a link. |
| `PR-ISS-004` | Agents may open issues (reports, tasks they discover, follow-ups) and must use the forms; agent-opened issues start in `status/triage` like any other. |
| `PR-ISS-005` | Epics are issues with sub-issues (GitHub sub-issues); the epic names the FR group and the gate; sub-issues are sized to one PR each (≤ 400 lines). |
| `PR-ISS-006` | Security reports never go through public forms (`PR-SEC-004`). |
| `PR-ISS-007` | Issue text and labels proposed by an AI are verified by a human at triage before they drive planning (INTERSECT). |

## 2. Label scheme (`.github/labels.yml`, synced by `labels-sync.yml`)

Prefixed, filterable, machine-readable (D-040). Colours are families: type = blues, area = greens, priority = reds→greys, status = yellows, phase = purples, control = orange, size = teal.

| Group | Labels | Applied by |
| --- | --- | --- |
| `type/` | `bug`, `feature`, `task`, `docs`, `protocol`, `skill`, `gate-report`, `retro`, `agent-report`, `security`, `question` | forms; triage |
| `area/` | `core`, `mcp`, `cli`, `tauri`, `ui`, `skills`, `docs`, `ci`, `release`, `deps`, `fixtures`, `repo` | forms; path labeler on PRs |
| `priority/` | `P0` (now, blocks everything), `P1` (this phase), `P2` (next phase), `P3` (someday) | triage; maintainer only for P0 |
| `status/` | `triage`, `needs-info`, `blocked`, `stale`, `needs-maintainer` | forms (`triage`); automation (`stale`); authors (`blocked`, `needs-maintainer`) |
| `phase/` | `0-foundation`, `v0.1`, `v0.2`, `v0.3`, `v0.4`, `v0.5`, `v1.0`, `post-1.0` | triage (mirrors milestone) |
| control | `gate`, `gate:approved`, `review:deep`, `ci:full`, `docs:not-needed`, `needs-tests`, `size:override`, `stacked`, `backport`, `breaking-change`, `release`, `dependencies`, `experimental` | see [31](31-pull-requests.md) §4 |
| size | `size/XS`, `size/S`, `size/M`, `size/L`, `size/XL` | automation |
| community | `good first issue`, `help wanted` | maintainer |

Total ≈ 55 labels; defaults not in this list are pruned by the sync. Each label has a one-line description shown in the picker.

## 3. Milestones

One milestone per roadmap phase, named exactly as the phase (`0 Foundation`, `v0.1 Black ink`, …, `v1.0 Public`), description = link to the gate in [40](40-roadmap-and-gates.md) and the exit criteria summary, no due date until v0.1 ships (concept decision). A milestone closes only when its gate report issue has verdict **pass** and no `priority/P0`/`P1` issue remains in it. Issues deferred at a gate move to the next milestone with a decision-log entry.

## 4. Project board ("Tlilli roadmap", GitHub Projects v2)

| Element | Specification |
| --- | --- |
| Fields | Status (Todo, Ready, In progress, In review, Gate, Done); Phase (single select mirroring `phase/*`); Area; Priority; Size (XS–XL); Gate (single select Yes/No: counts toward gate exit; Projects v2 has no checkbox field type); Lane (Agent / Human); CodeRabbit requests (text ledger); Greptile reviews (number, monthly) |
| Views | **Board** by Status with WIP limit 3 on In progress for Lane = Agent (`PR-GIT-012`); **Roadmap** as a table grouped by Phase until milestones carry due dates (the Roadmap layout needs date fields; milestones have none until v0.1 ships, §3), then the Roadmap layout by milestone; **Triage** table filtered `status/triage`; **Agent queue** table: Status = Ready, sorted by Priority then Size, filtered by Area (what an agent picks next); **Gate** view: Gate = Yes for the current phase; **Budgets** view: the two ledger fields |
| Automation | `project.yml` adds every new issue and PR; built-in workflows: item closed → Done; PR merged → Done; PR opened → In review when Ready; issue labelled `status/blocked` → stays with a Blocked marker |
| Ownership | Maintainer edits fields at triage and mirrors the ledger lines from PR bodies and agent-session reports into the ledger fields (agent sessions cannot reach Projects v2, D-064); agents move their own items between Ready → In progress → In review when a session with Project access exists |

## 5. Cadence and ceremonies (Kanban, solo maintainer)

| Ritual | When | Content |
| --- | --- | --- |
| **Weekly triage** (≤ 60 min) | Monday | New issues: type, area, priority, phase, milestone, requirement IDs; stale sweep; label-audit report (`docs:not-needed`, `size:override`, `needs-tests` uses); review budgets (CodeRabbit ledger, Greptile count); Dependabot majors; nightly/weekly tracking issues; Agent-session reports → next Ready items; WIP check |
| **Gate review** | At each phase end | Run the gate script on the release build; file the Gate test report; close or roll the milestone; re-baseline the PRD |
| **Retrospective** | After each gate | `retro.yml` issue; INTERSECT: lessons learned, what to change; each change is a decision or an issue |
| **Monthly metrics** | First triage of the month | Review metrics ([32](32-code-review.md) §7), lead time, zero-touch merge share, budgets, coverage/mutation trends; posted in the triage issue |
| **Quarterly retune** | Every 3 months | Review-lane instructions, runner image pins, dependency policy, threat register (`PR-SEC-005`) |

## 6. Definitions

**Definition of Ready (an issue an agent may pick):** has type/area/priority/phase and milestone; names requirement IDs; has acceptance criteria an agent can test; is sized ≤ M (≤ 400 lines expected) or is an epic with Ready sub-issues; dependencies closed or linked; no `status/*` blocker.

**Definition of Done (a PR may be Ready / an issue may close):** code merged through the queue; tests included and green (`PR-TST-001..002`); docs updated or justified (`PR-DOC-001..002`); Conventional Commits with DCO; review pipeline completed; acceptance criteria demonstrably met (tests or a gate step); no new TODOs without issues; the issue closed by the PR; if the FR is gate-relevant, the gate script updated.

## 7. Backlog hygiene

- User stories use "As a <role>, I want <goal>, so that <impact>" (INTERSECT); epics map to FR groups; stories to single FRs or sub-points.
- MoSCoW at phase planning: FRs are `Must` by definition of the phase; `Should` items are listed in the phase file's deferrals; anything `Could` is `phase/post-1.0`.
- Grooming: at each gate, issues untouched for two phases are closed as not planned with a note (reopenable).
- Estimation: T-shirt sizes only; velocity measured as merged PRs and closed FRs per week after v0.1 to inform (not promise) dates.

## 8. Discussions

Enabled at v0.2 (D-042) with categories Q&A, Ideas, Show-and-tell, Announcements; `SUPPORT.md` routes questions there; ideas that become actionable are converted to issues with a link back; announcements are posted for each release and each gate.
