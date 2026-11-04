# 31 · Pull requests

INTERSECT (Making Good PRs): a good PR makes **one cohesive change**, stays a **reasonable size**, and describes **what, how (including side effects) and why**; GenAI may draft the description but only the author knows the why and must verify it; the human owns the merge decision. This section turns that into rules an agent can follow and CI can check.

## 1. Lifecycle (PR-PRQ-001 … 013)

```
branch pushed ──▶ Draft PR ──▶ (Linux lane CI, Codex local rounds done, Codex cloud round, CodeRabbit round)
          ──▶ author marks Ready ──▶ full matrix + gate check + (Greptile if gated)
          ──▶ author enables auto-merge or merges ──▶ branch up to date + checks green ──▶ main
```

| ID | Rule |
| --- | --- |
| `PR-PRQ-001` | **Every PR opens as a Draft.** Draft means: work in progress, Linux lane CI runs on each push, AI reviewers are driven by the author, the maintainer does not look at it. |
| `PR-PRQ-002` | **Ready for review** is asserted by the author (agent or human) only when all of: Linux lane green; Codex local rounds done (a cloud session without the Codex CLI records `0` with that reason) and one Codex cloud round clean ([32](32-code-review.md)); CodeRabbit round done and threads resolved or answered; PR body complete per the template; commits squashed (in a cloud session, unpushed fix-ups only, `PR-GIT-054`) and conventional; branch rebased on `origin/main`; size within cap or `size:override` justified; docs updated or `docs:not-needed` justified; tests included or `needs-tests` explained. Marking Ready triggers the full matrix and, for gated PRs, Greptile and the maintainer's attention. A cloud session marks Ready through the GitHub MCP tools (`PR-GIT-058`); its pushed commits stay unsquashed (`PR-GIT-054`). |
| `PR-PRQ-003` | **Auto-merge** is enabled by the author at Ready with the rebase method (`gh pr merge --auto --rebase <n>`, the UI, or the GitHub MCP tool `enable_pr_auto_merge` from a cloud session). GitHub lands the PR (rebase) when the branch is up to date with `main` and every required check passes, including `gate/maintainer` for gated PRs. GitHub refuses auto-merge on a PR that is already mergeable; the author then merges it with the rebase method and the head SHA it checked as the guard (`PUT /repos/bioedca/Tlilli/pulls/<n>/merge` with `merge_method: rebase` and `sha`, or `merge_pull_request` with `merge_method: rebase` and `expectedHeadSha`). An agent merges only a PR with no open maintainer decision, or one the maintainer authorized (`PR-GIT-058`, D-078). |
| `PR-PRQ-004` | A Ready PR that receives new review findings goes back to work in place (not to Draft); the author fixes, pushes, resolves threads, re-requests review. Converting back to Draft is only for substantial rework and is announced in a comment. |
| `PR-PRQ-005` | **Stale policy:** no activity for 14 days → `status/stale` label and a comment; 7 more days → closed with a comment naming the branch (recoverable). Gated PRs waiting on the maintainer are exempt. |
| `PR-PRQ-006` | PRs that touch gated paths get the `gate` label automatically (path labeler) and cannot merge without maintainer approval ([32](32-code-review.md) §5) or the maintainer's relayed authorization (`PR-GIT-058`). |
| `PR-PRQ-007` | PR titles follow Conventional Commits (`type(scope): subject`) and are linted; with rebase-merge the title is not a commit, but it names the change in the PR list, release-notes drafts and notifications. |
| `PR-PRQ-008` | Link the issue with a closing keyword (`Closes #12`) in the body; a PR without an issue link is allowed only for `chore`/`docs` changes under 50 lines and says why. |
| `PR-PRQ-009` | Dependabot PRs (grouped weekly) are Ready on open; the auto-merge workflow enables auto-merge for the patch and minor groups of the entries PR CI builds and tests (`PR-MNT-010`) after CI; majors and anything touching `.github/workflows` wait for the maintainer (gated). |
| `PR-PRQ-010` | release-plz PRs (`chore(release): vX.Y.Z`) are gated (`CHANGELOG.md`, versions, `CITATION.cff`); the maintainer approves them as the release decision ([37](37-releases-and-packaging.md)). |
| `PR-PRQ-011` | A PR description is written for a reader who was not in the session: no "as discussed", no session-only context. Agents include the issue text they worked from if it is short. |
| `PR-PRQ-012` | Screenshots or short recordings are required for UI changes (Playwright-generated, committed under the PR as attachments, not in git). |
| `PR-PRQ-013` | Immediately after creating or editing a PR, the author checks the description for an appended footer containing a session URL and removes it (`PR-GIT-059`). The PR template has no attribution section; AI assistance is declared in the `AI assistance:` line without links to sessions. |

## 2. Size (PR-PRQ-020 … 024)

INTERSECT: review at most 500 lines per hour and at most 60 minutes per session; "hundreds of changed lines are hard to review".

| ID | Rule |
| --- | --- |
| `PR-PRQ-020` | **Cap: ≤ 400 changed lines** (additions + deletions) of hand-written code. Excluded from the count: `Cargo.lock`, `pnpm-lock.yaml`, `*.snap` (insta), `docs/reference/mcp/**` (generated), `tests/fixtures/**`, `*.svg`/images, `CHANGELOG.md` when produced by release-plz. |
| `PR-PRQ-021` | The `size/limit` check computes the number and fails above the cap unless `size:override` is present **and** the PR body has a line `Size override: <reason>`; the weekly audit lists every override. |
| `PR-PRQ-022` | Size labels `size/XS` (≤ 50), `size/S` (≤ 150), `size/M` (≤ 400), `size/L` (≤ 800), `size/XL` (> 800) are applied automatically for triage statistics. |
| `PR-PRQ-023` | Split by design, not by diff: a feature that exceeds the cap is planned as a stack of PRs (`stacked`) or a sequence of issues (sub-issues), each independently valuable or clearly scaffolding (e.g., "add storage schema", "add model", "add tools"). |
| `PR-PRQ-024` | Mechanical mass changes (formatter upgrade, rename) are a single PR with `size:override`, no logic changes mixed in, and the command that produced them in the body. |

## 3. The PR template (`.github/PULL_REQUEST_TEMPLATE.md`)

The template is lean (INTERSECT: keep templates matching what the team fills in) and uses HTML comments for tips. Required sections are checked by the `commits` job (presence of headings and of the `Requirements` and `Review pipeline` lines).

```markdown
## Summary
<!-- What changes and why, in two to five sentences, for someone who was not here. -->

Closes #

## Requirements
<!-- IDs this PR implements or affects: FR-02-031, NFR-PERF-005, PR-CI-004. "none" is allowed for chores. -->
Requirements: 

## Changes
<!-- How: the approach, notable side effects, migrations, schema or protocol changes, follow-ups. -->
- 

## Testing
<!-- What you ran and what you added. Name AI-written tests explicitly. Bug fixes: name the failing-first test. -->
- [ ] New or changed tests: 
- [ ] AI-written tests reviewed and run by the author: yes / none
- [ ] `cargo nextest run --workspace`, `pnpm -C ui test` pass locally

## Docs
<!-- Pages updated, or the reason docs are not needed (label docs:not-needed). -->
- 

## Review pipeline
<!-- Filled by the author as the pipeline advances. -->
- Codex local rounds: N · Codex cloud: clean / pending
- CodeRabbit: round N clean / pending
- Greptile: n/a / requested / clean
- Gated paths touched: none / <paths>

## Checklist
- [ ] One cohesive change; ≤ 400 hand-written lines or `Size override: <reason>` below
- [ ] Conventional commits, each signed off (DCO), squashed, rebased on `main`
- [ ] No secrets, no `git =` dependencies, no files > 2 MB
- [ ] CHANGELOG not hand-edited (release-plz generates it)
- [ ] Breaking change? `!` in the commit and a `BREAKING CHANGE:` footer, migration noted in Docs

Size override: 
Docs not needed because: 
AI assistance: <!-- tools used, e.g. "Claude Code (cloud) wrote the implementation and tests; Codex reviewed." -->
```

Until bootstrap task 20 adds `cargo-nextest` to CI and `scripts/install_pkgs.sh`, the Testing line is met by `cargo test --workspace` (D-077).

## 4. Labels an author may apply (PR-PRQ-030 … 034)

| ID | Rule |
| --- | --- |
| `PR-PRQ-030` | Agents MAY apply freely: `ci:full` (run the matrix on a Draft), `review:deep` (request a Greptile review), `needs-tests` (declares tests are missing with the reason and a follow-up issue; blocks auto-merge until removed by the maintainer or replaced by tests), `stacked`, `area/*` corrections. |
| `PR-PRQ-031` | Agents MAY apply with a written reason in the PR body: `docs:not-needed` (`Docs not needed because:` line) and `size:override` (`Size override:` line). Both are listed in the weekly audit report and may be reverted by the maintainer. |
| `PR-PRQ-032` | Only automation applies `gate` (from CODEOWNERS paths) and `size/*`; only the maintainer applies `gate:approved` (or the backup admin while the handoff state is active, `PR-REV-010`, `PR-REV-012`), `priority/P0`, `breaking-change` (after confirming), `backport`. |
| `PR-PRQ-033` | Removing a label that automation applied is forbidden; the automation re-applies it and posts a comment. |
| `PR-PRQ-034` | Label definitions and colours live in `.github/labels.yml` ([36](36-issues-labels-and-projects.md)). |

## 5. Responding to review (PR-PRQ-040 … 045)

| ID | Rule |
| --- | --- |
| `PR-PRQ-040` | Every review comment gets a reply: "fixed in `<sha>`", a question, or a reasoned decline. The author resolves the thread only after the reply; reviewers may unresolve. |
| `PR-PRQ-041` | AI-reviewer findings are handled by severity ([32](32-code-review.md) §6): blocker and major are fixed; minor is fixed or declined with a reason; nit is optional but acknowledged. |
| `PR-PRQ-042` | Disagreement with an AI reviewer that the author cannot resolve in two rounds is escalated to the maintainer with the `needs-maintainer` label and a three-line summary (claim, counter-claim, what evidence would settle it). INTERSECT: bring in a third party rather than argue. |
| `PR-PRQ-043` | Push fixes as new commits during review; squash them before the final Ready assertion so the landed history is clean (`PR-GIT-024`; a cloud session keeps pushed fixes as commits, `PR-GIT-054`). Force-pushes during review include a comment "rebased, no content change" or "squashed review fixes". |
| `PR-PRQ-044` | Re-request review after addressing a human review; for AI reviewers, re-trigger per [32](32-code-review.md). |
| `PR-PRQ-045` | Tone: critique code, not people; prefer "we could…" and questions; label nits as `Nit:`; praise good solutions (INTERSECT Code Review). |

## 6. Definition of a good PR (reviewer rubric)

Reviewers (AI lanes are configured with this, the maintainer uses it at gates) check that the PR:
1. does one thing and says what, how and why;
2. is within the size cap or justifies the override;
3. has tests that would fail without the change, and names AI-written tests;
4. updates docs for every contract change;
5. keeps the invariants (`INV-*`) and the architecture boundaries ([21](21-architecture-and-tech-stack.md) §4);
6. has clean, conventional, signed-off commits;
7. leaves no unexplained TODO, commented-out code or dead code;
8. has a description a stranger could act on.
