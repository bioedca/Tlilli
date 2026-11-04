# 30 · Git workflow

Model: **GitHub Flow with short-lived feature branches, rebase-merge with auto-merge once the branch is up to date with `main`, tags on `main`, release branches only after v1.0 for backports.** This is INTERSECT's feature-branching workflow ("all development is done in feature branches", published early, merged by PR after tests), with GitLab Flow's release branches added only "when software is released to the outside world" and only when a patch must be backported.

## 1. Branches (PR-GIT-001 … 012)

| ID | Rule |
| --- | --- |
| `PR-GIT-001` | `main` is the only long-lived branch before v1.0. It is always releasable: every commit on it passed the full required-check set on a branch that was up to date with `main` at merge time. |
| `PR-GIT-002` | All work happens on short-lived branches created from current `origin/main` (`git fetch origin main && git switch -c <branch> origin/main`). INTERSECT: pull `main` before branching to avoid conflicts later. |
| `PR-GIT-003` | Branch names: agents use their platform prefix and slug (`claude/<slug>`, `codex/<slug>`); humans use `<type>/<issue>-<slug>` with `type ∈ {feat, fix, docs, chore, refactor, perf, test, ci, build}`, e.g. `feat/42-span-anchoring`. Lower-case, hyphens, ≤ 60 characters. Reserved prefixes: `release/` (maintenance branches), `release-plz-` (release tool), `dependabot/`, `backport/`. |
| `PR-GIT-004` | One branch = one PR = one issue (or one tightly scoped change). A branch lives at most 7 days before merge or closure; the weekly triage marks older branches `status/stale`. |
| `PR-GIT-005` | One writer per branch. Nobody pushes to a branch they did not create except the maintainer resolving an abandoned agent branch, announced in the PR. |
| `PR-GIT-006` | Keep the branch current by **rebasing onto `origin/main`** (`git pull --rebase origin main`), never by merging `main` into the branch (merge commits are refused by the linear-history rule). Force-push your own branch with `--force-with-lease` only. |
| `PR-GIT-007` | **Never rebase or force-push `main` or `release/*`** (INTERSECT: never rebase a public branch). Both are protected against force pushes and deletion. |
| `PR-GIT-008` | Branches are deleted automatically on merge (repository setting); closed-unmerged branches are deleted at triage. |
| `PR-GIT-009` | `release/<major>.<minor>` branches exist only after v1.0 and only when a security or critical fix must be backported to the previous minor ([38](38-maintenance-and-support.md)). They are cut from the `v<major>.<minor>.0` tag, protected like `main`, receive only cherry-picks (`git cherry-pick -x`) through PRs labelled `backport`, and are tagged `v<major>.<minor>.<patch>`. |
| `PR-GIT-010` | External contributors fork; same rules apply to fork branches. Fork PRs cannot run privileged workflows (no secrets). |
| `PR-GIT-011` | Stacked branches are allowed (branch B based on branch A's PR) and labelled `stacked`; B's PR body names A's PR; B is rebased onto `main` after A merges before it may merge. |
| `PR-GIT-012` | Work-in-progress limit: at most 3 open agent-authored PRs at a time, one per area (core, mcp, ui); an agent addresses review on an existing PR before opening a new one ([36](36-issues-labels-and-projects.md) WIP). |

## 2. Commits (PR-GIT-020 … 031)

| ID | Rule |
| --- | --- |
| `PR-GIT-020` | Every commit follows **Conventional Commits 1.0**: `type(scope)!: subject`. Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`. Scopes (closed list, linted): `core`, `mcp`, `cli`, `tauri`, `ui`, `skills`, `docs`, `prd`, `ci`, `release`, `deps`, `repo`, `fixtures`. A `!` or a `BREAKING CHANGE:` footer marks a breaking change. |
| `PR-GIT-021` | Subject: imperative mood, lower-case first letter, no trailing period, ≤ 72 characters. Body: wrap at 72, explain what and why (not how); reference requirements (`FR-02-031`) and issues (`Refs #12`, `Fixes #12`). |
| `PR-GIT-022` | **Every commit carries `Signed-off-by: <name> <email>`** matching the author (Developer Certificate of Origin 1.1). Use `git commit -s`. The DCO check is a required status and fails on any commit without a matching sign-off. There is no CLA. |
| `PR-GIT-023` | **Agent-authored commits are authored and signed off by the operating maintainer** (`bioedca <131809205+bioedca@users.noreply.github.com>` configured in the agent's git identity). No agent trailer is added (D-014); AI involvement is stated in the PR body. The maintainer certifies the contribution as the DCO requires. |
| `PR-GIT-024` | One logical change per commit; commits in a PR MUST be independently buildable (`cargo check` passes at each commit; verified by the `commits` job for PRs with ≤ 10 commits). Fix-ups are squashed before Ready: `git commit --fixup <sha>` then `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash origin/main` (works without an interactive editor). |
| `PR-GIT-025` | A PR has ≤ 10 commits when it is marked Ready; more requires splitting the PR. |
| `PR-GIT-026` | Commit messages never contain secrets, tokens, URLs with credentials, or model identifiers. |
| `PR-GIT-027` | `revert:` commits reference the reverted SHA and the reason; reverting on `main` goes through a PR like any change (fast lane allowed). |
| `PR-GIT-028` | Generated files (lockfiles, `insta` snapshots, generated protocol docs) are committed in the same commit as the change that produced them, never separately, so every commit is consistent. |
| `PR-GIT-029` | No merge commits anywhere in history: the repository disables merge-commit and squash buttons; only rebase-merge is enabled (D-010). |
| `PR-GIT-030` | Tags are annotated, named `v<semver>` (`v0.3.0`, `v0.3.1`, `v0.4.0-beta.1`), created only by the release tooling under the release token or by the maintainer; a tag ruleset forbids updating or deleting tags matching `v*`. |
| `PR-GIT-031` | Large binary assets (fixture PDFs, screenshots) are committed only under `tests/fixtures/` and `docs/assets/` with a 2 MB per-file and 50 MB per-directory cap enforced in CI; anything larger is a release asset or external download, not a git object. Git LFS is not used (D-036). |

### Commit message example

```
feat(core): anchor span ids across paragraph edits

Re-segment the edited paragraph and match old and new sentences by
position-aware token overlap (threshold 0.6) so comments and claim
links keep their anchors. Tombstones point deleted spans at the
nearest survivor for display.

Implements FR-01-012. Refs #57.

Signed-off-by: bioedca <131809205+bioedca@users.noreply.github.com>
```

## 3. Landing changes on `main` (PR-GIT-040 … 047)

| ID | Rule |
| --- | --- |
| `PR-GIT-040` | **Pull requests are the only way into `main`.** Direct pushes are blocked for everyone, including the repository owner; there is no bypass list on the `main` ruleset (D-011). |
| `PR-GIT-041` | **Rebase-merge only.** GitHub's rebase merge method is the only one enabled; commits land unchanged in content, re-parented onto `main`; history is linear (required by the ruleset). |
| `PR-GIT-042` | **Up-to-date rule instead of a merge queue.** GitHub offers merge queues only on organization-owned repositories, and the project stays on the personal account (D-057). The `main` ruleset therefore requires status checks to pass **with "require branches to be up to date before merging"**: a PR merges only when its base is the current tip of `main`, so the required checks always ran on the exact rebased result. When `main` moves, the author rebases onto `origin/main` and pushes (or the maintainer uses "Update branch → rebase"); auto-merge then lands the PR as soon as the checks are green again. |
| `PR-GIT-043` | Required status checks on `main` (exact names, all from `ci.yml` unless noted): `rust-lint`, `rust-test`, `ui`, `docs-build`, `commits`, `DCO` (app), `size/limit`, `docs/contract-sync`, `protocol-ref/drift`, `workflows/zizmor`, `tauri/linux`, `e2e/smoke`, `gate/maintainer`, `codecov/patch/tlilli-core`, `codecov/patch/tlilli-mcp`. Full-matrix checks (`build/macos-arm64`, `build/macos-x86_64`, `build/windows`) are required too; they run when the PR is Ready, so a Draft can never merge ([33](33-ci-cd.md)). The ruleset also requires the branch to be up to date with `main`, so the checks always ran on the exact result that lands. |
| `PR-GIT-044` | **Conversation resolution required**: every review thread (human or AI) is resolved before merge. The author resolves a thread only after fixing or answering it in the thread. |
| `PR-GIT-045` | Serialization is manual but cheap: with at most 3 agent PRs in flight (`PR-GIT-012`), a landing invalidates at most two other agent-authored PRs, each needing one rebase and one Linux-lane run; human, Dependabot and release PRs are rebased by their authors or with the maintainer's "Update branch" button when they come up for merge (the full matrix re-runs on Ready PRs). Agents check for "out of date" on their Ready PRs at the start of every session and after every merge notification. If checks fail after a rebase, the PR is the author's to fix; auto-merge stays enabled. |
| `PR-GIT-046` | **Emergency lane.** A P0 fix follows the same path with the `priority/P0` label: the author adds `ci:full` so the matrix runs on the Draft, requests reviews immediately, and the maintainer approves the gate at once. The lane changes urgency, never the checks (INTERSECT: human review is most needed under deadline pressure). |
| `PR-GIT-047` | Reverting a bad landing is a `revert:` PR through the same lane; `main` is never force-pushed. |

## 4. Agent operating rules for git (PR-GIT-050 … 058)

These are restated in `CLAUDE.md` and `AGENTS.md` (kept in step with each other), which point to this file (INTERSECT Collaborative Git: agent configuration files are context, not enforcement; the rules must be written where agents read them and enforced by the repository).

| ID | Rule |
| --- | --- |
| `PR-GIT-050` | Configure identity before the first commit: `git config user.name bioedca && git config user.email 131809205+bioedca@users.noreply.github.com`; commit with `-s`. |
| `PR-GIT-051` | Start from `origin/main`; name the branch per `PR-GIT-003`; push early as a Draft PR so work survives session restarts; push at least every 30 minutes of work. |
| `PR-GIT-052` | Commit often with conventional messages; squash fix-ups before marking Ready (`PR-GIT-024`). |
| `PR-GIT-053` | Rebase onto `origin/main` before marking Ready and whenever the PR shows conflicts; resolve conflicts in new commits only on your own branch (INTERSECT: address conflicts with additional commits); never resolve conflicts by discarding others' changes without noting it in the PR. |
| `PR-GIT-054` | Never run `git push --force` without `--force-with-lease`; never push to `main`, `release/*`, tags or another agent's branch. |
| `PR-GIT-055` | Never commit secrets, `.env`, keys, or files > 2 MB outside the allowed directories; never add `git =` dependencies. |
| `PR-GIT-056` | Respect the WIP limit (`PR-GIT-012`); if the limit is reached, leave an Agent-session report issue instead of opening a fourth PR. |
| `PR-GIT-057` | When a session ends with unfinished work: push, leave the PR as Draft, and file or update an Agent-session report issue naming the branch, what is done, what is blocked, and the next step. |
| `PR-GIT-058` | Agents do not merge, approve, close others' PRs, delete branches, edit rulesets, or manage secrets. They enable auto-merge on their own PRs when the PR is Ready ([31](31-pull-requests.md)). |
| `PR-GIT-059` | **No session URLs on GitHub.** The cloud integration appends a footer with a `claude.ai/code/session_…` link to every PR description it creates, and the `attribution` keys in `.claude/settings.json` do not reach that server-side footer. After opening or editing a PR, the agent re-reads the description and removes any line containing a session URL (an edit is not re-appended). Session URLs never appear in commit messages, PR bodies or comments; one found in a comment the agent posted is edited out. Stated in `CLAUDE.md` and `AGENTS.md` (D-059). |

## 5. Local setup for humans

- Clone your own copy; never share a clone or work in a synced folder (INTERSECT; `NFR-PRIV-004` for workspaces too).
- Install hooks with `pnpm -C ui install` (installs `lefthook`): pre-commit runs `cargo fmt --check`, `biome check`, `cargo clippy` on changed crates, commitlint on the message and adds `-s` if missing; pre-push runs `cargo nextest run -p <changed crates>`.
- `git config commit.gpgsign` is optional; signatures are not required (D-012).
- Conventional-commit help: `pnpm -C ui commit` (commitizen prompt) is available but not required.

## 6. What CI enforces from this file

`commits` job: commitlint on every PR commit (types, scopes, length), PR title format, ≤ 10 commits, buildability per commit (small PRs), no merge commits in the PR, branch name pattern. `DCO` app: sign-off per commit. Ruleset: PR required, linear history, branch up to date before merging, conversation resolution, required checks, no force-push, no deletion, no bypass. Tag ruleset: creation restricted, no update/delete. Size job: 2 MB file cap and 50 MB directory cap.
