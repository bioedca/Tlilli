# 42 · Bootstrap backlog (Phase 0 Foundation)

The first issues to open, in dependency order. Each becomes a `type/task` issue (or an epic with sub-issues) with the labels shown, `phase/0-foundation`, milestone `0 Foundation`, and the requirement references. Items marked **H** need the maintainer's hands (GitHub settings, accounts, keys); everything else can be done by an agent in a PR. Sizes are T-shirt estimates for one PR each.

## A. Account and repository (H)

| # | Task | Labels | Refs | Size |
| --- | --- | --- | --- | --- |
| 1 | Account settings: 2FA on; designate a GitHub account successor; confirm Pro (Student Developer Pack) status and note its expiry in `docs/dev/github-settings.md`. Repository settings: Actions allow-list, default workflow permissions read, fork-PR approval; add the backup admin collaborator before v1.0 (admin on the repository, CODEOWNERS entry, allowed `release` environment reviewer) | `area/repo`, `gate` | D-057, [39](39-github-configuration.md) §1 | S |
| 2 | Repository settings: rebase-merge only, auto-delete branches, auto-merge, Discussions off until v0.2, Wiki off, topics, description, website | `area/repo`, `gate` | [39](39-github-configuration.md) §2 | XS |
| 3 | Install apps: Codex (automatic reviews off), CodeRabbit (Team plan; Open Source plan when eligible), Greptile (label trigger), Codecov, DCO, Zenodo; record permissions in `docs/dev/github-settings.md` | `area/repo`, `gate` | [32](32-code-review.md) §2, [39](39-github-configuration.md) §5 | S |
| 4 | Create environment `release` (required reviewers: maintainer, backup admin once named; `v*` tags and `main`) for the signing keys and packaging tokens, and environment `automation` (no reviewer; `main` only) for `RELEASE_PLZ_TOKEN` and `PROJECT_TOKEN`; create those fine-grained PATs; create the repository Actions variable `HANDOFF_ACTIVE=false`; crates.io trusted-publisher entries (after first crate exists) | `area/release`, `gate` | `PR-CI-007`, [39](39-github-configuration.md) §5 | S |
| 5 | Generate the updater minisign keypair offline; store per `PR-REL-034`; add public key to `tauri.conf.json` (task 14) and private key to `release` | `area/release`, `gate` | `PR-REL-034`, T-09 | XS |
| 6 | Create the Project "Tlilli roadmap" with fields and views; create milestones `0 Foundation` … `v1.0 Public`, `post-1.0` | `area/repo` | [36](36-issues-labels-and-projects.md) §3–4 | S |
| 7 | Create the private companion repo `bioedca/tlilli-release-rehearsal` (user-owned) and the `bioedca/homebrew-tlilli` tap repo (empty cask skeleton); grant the backup admin admin access to both once named | `area/release` | [39](39-github-configuration.md) §6, `PR-REL-021` | XS |
| 8 | Start the trademark search (USPTO, EUIPO, WIPO GBD; classes 9, 42); record result in the decision log before `v0.1.0`; prepare `scripts/rename.sh` | `area/repo`, `gate` | D-035, R-07 | S |

## B. Legal and project files

| # | Task | Labels | Refs | Size |
| --- | --- | --- | --- | --- |
| 9 | Replace root `LICENSE` with Apache-2.0; add `skills/LICENSE` (MIT), `NOTICE`, SPDX headers policy and a `reuse`-style check in CI; license roadmap paragraph in README | `area/repo`, `gate` | D-003, `PR-ARCH-003` | S |
| 10 | Add `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1), `SECURITY.md`, `SUPPORT.md`, `GOVERNANCE.md`, `CITATION.cff` (validated), `.github/FUNDING.yml`; README per `PR-DOC-006` | `area/docs`, `gate` | [35](35-documentation.md) §4, `PR-SEC-001` | M |
| 11 | Rewrite `CLAUDE.md` and add `AGENTS.md`: layout incl. `tlilli-cli`, commands, pointer to CONTRIBUTING and this PRD, agent git rules (`PR-GIT-050..059`; the no-session-URL rule is added to both files by pull request #3, so verify it is present and in step), `## Review guidelines` for Codex; set the agent git identity instructions; keep the two files in step | `area/repo`, `gate` | D-002, D-014, D-055, [30](30-git-workflow.md) §4 | S |

## C. Workspace skeleton

| # | Task | Labels | Refs | Size |
| --- | --- | --- | --- | --- |
| 12 | Cargo workspace: `crates/tlilli-core`, `crates/tlilli-mcp`, `crates/tlilli-cli`, `fuzz/` with `[workspace.package]` version/edition/license/rust-version, `version.workspace = true`, `#![forbid(unsafe_code)]`, clippy config, `deny.toml`; hello-world binaries | `area/core`, `area/mcp`, `area/cli` | [21](21-architecture-and-tech-stack.md) §2, `PR-ARCH-*` | M |
| 13 | `ui/`: Vite + React 19 + TypeScript strict + Biome + Vitest + Testing Library + Playwright skeleton; `pnpm` lockfile; `lefthook.yml` | `area/ui` | D-030, D-032 | M |
| 14 | `src-tauri/`: Tauri 2 shell with capabilities, updater plugin wired (public key from task 5), `tauri.conf.json` without `version`, `--no-bundle` build in CI | `area/tauri`, `gate` | `PR-REL-002`, `PR-REL-030` | M |
| 15 | `scripts/ci.sh` (local mirror of CI jobs), `scripts/gen_fixtures.py` skeleton, `tests/fixtures/LICENSES.md` | `area/ci`, `area/fixtures` | `PR-CI-010`, `PR-TST-016` | S |
| 16 | ADR-0001 … ADR-0006 drafted (layout incl. CLI; rmcp; hayagriva; storage schema v1 and migrations; sidecar policy and tunnel exception; event-log hash chain and snapshot cadence) | `area/docs`, `gate` | [21](21-architecture-and-tech-stack.md) §6, D-054, D-055 | M |

## D. CI/CD and automation

| # | Task | Labels | Refs | Size |
| --- | --- | --- | --- | --- |
| 17 | `.github/labels.yml` + `labels-sync.yml`; `.github/labeler.yml` (area, gate, review:deep) + `labeler.yml` workflow; prune default labels | `area/ci`, `gate` | D-040, `PR-REV-014` | S |
| 18 | Issue forms (ten) + `config.yml`; `PULL_REQUEST_TEMPLATE.md` | `area/ci`, `gate` | D-041, [31](31-pull-requests.md) §3 | M |
| 19 | `CODEOWNERS` with the gated paths (owners: `@bioedca`, plus the backup admin once named); `gate.yml` implementing `gate/maintainer` (approval or `gate:approved` by the maintainer, or by the backup admin only while the `HANDOFF_ACTIVE` variable is `true`; reset on push; actor check); the backup admin's CODEOWNERS entry lands in this same PR, never before the check | `area/ci`, `gate` | D-022, D-053, `PR-REV-010..015` | M |
| 20 | `ci.yml` rewrite: Linux lane jobs (`rust-lint`, `rust-test` with llvm-cov, `ui`, `docs-build`, `commits`, `size/limit`, `docs/contract-sync`, `protocol-ref/drift`, `workflows/zizmor`, `tauri/linux`, `e2e/smoke`) and the Draft-gated matrix (`build/*`); `cargo-nextest` in CI and `scripts/install_pkgs.sh`; `commitlint.config.mjs`; `codecov.yml`; all actions SHA-pinned | `area/ci`, `gate` | [33](33-ci-cd.md) §2, D-050 | L (split: lint/test; ui/docs; commits/size/sync; matrix) |
| 21 | `codeql.yml`, `scorecard.yml`, `dependabot.yml` (grouped), `dependabot-automerge.yml` | `area/ci`, `gate` | D-051, `PR-MNT-010` | S |
| 22 | `nightly.yml` (fuzz skeleton, Playwright full, lychee, deny advisories, criterion) and `weekly.yml` (mutants, label audit, stale sweep, budget ledger summary) with tracking issues | `area/ci`, `gate` | [33](33-ci-cd.md) §1, `PR-CI-014` | M |
| 23 | `project.yml` (add-to-project) | `area/ci` | D-043 | XS |
| 24 | `release-plz.toml`, `cliff.toml`, `release-plz.yml` (release PR + tag + trusted publishing), `CITATION.cff` version script | `area/release`, `gate` | D-025, [37](37-releases-and-packaging.md) §2 | M |
| 25 | `release.yml` (tauri-action matrix → draft release, SBOM, checksums, attestations, verify) and `prerelease.yml`; rehearse in the companion repo with `dry_run` | `area/release`, `gate` | [37](37-releases-and-packaging.md) §2, `PR-CI-018` | L (split: build; sbom/checksums; attest/verify; prerelease) |
| 26 | `post-release.yml` (tap bump, winget, updates JSON, Zenodo check, announcement draft); Flathub manifest deferred to v1.0 | `area/release`, `gate` | `PR-REL-021..025` | M |
| 27 | Ruleset `main` (bypass only for the repository-admin role on pull requests, checked with one agent-session merge, D-078; PR required, linear history, branch up to date before merging, conversation resolution, the required checks of `PR-GIT-043`), rulesets `tags v*` and `tags v* creation` (D-089); export JSON to `docs/dev/github-settings.md` (H) | `area/repo`, `gate` | D-010, D-011, [39](39-github-configuration.md) §3 | S |

## E. Documentation and developer environment

| # | Task | Labels | Refs | Size |
| --- | --- | --- | --- | --- |
| 28 | `mkdocs.yml` + Material + plugins; `docs/requirements.txt` with hashes; Diátaxis skeleton pages; `docs.yml` deploying to Pages with rustdoc under `/api`; `site_url` | `area/docs` | D-052, [35](35-documentation.md) §1–2 | M |
| 29 | `tlilli mcp schema --markdown` and `tlilli schema dump` generators (skeleton outputs) + `protocol-ref/drift` job wiring; `docs/reference/` generated headers | `area/cli`, `area/docs` | `PR-DOC-003` | S |
| 30 | `docs/gates/G0.md`–`G6.md` from [40](40-roadmap-and-gates.md) §3; `docs/dev/review-severity.md`, `release-runbook.md`, `agent-playbook.md`, `fixtures.md`, setup pages | `area/docs`, `gate` | `PR-GATE-003`, `PR-DOC-013` | M |
| 31 | `.devcontainer/devcontainer.json` (Rust, Node, pnpm, Tauri deps, xvfb, desktop-lite/noVNC) and a how-to for Codespaces | `area/repo` | D-044 | S |
| 32 | `docs/explanation/built-with-agents.md` first version | `area/docs` | `PR-DOC-014` | XS |

## F. Phase 0 exit (Gate G0)

Run [G0](40-roadmap-and-gates.md#gate-g0-phase-0-foundation): audit checklist passes; an agent PR on an ungated path merges with zero human clicks; a gated PR is blocked until `gate:approved` (without the label, only the admin bypass on a relayed authorization recorded in the PR body merges it, `PR-GIT-058`); release workflows rehearsed; docs site deployed; all required checks reporting. File the Gate test report; open milestone `v0.1 Black ink` with its epics (one per FR group in [10](10-fr-v0.1-black-ink.md)).

## G. Rules that follow from staying on the personal account (D-057)

- Merge queue is organization-only, so the `main` ruleset uses "require branches to be up to date before merging" with auto-merge; agents rebase their Ready PRs whenever `main` moves (`PR-GIT-042`, `PR-GIT-045`).
- CODEOWNERS names `@bioedca`; there are no teams.
- Succession uses GitHub's account-successor setting plus a backup admin on the repository ([38](38-maintenance-and-support.md) §8).
- Channel identifiers follow the account: `bioedca/homebrew-tlilli`, `io.github.bioedca.Tlilli`, attestations against `bioedca/Tlilli` (D-058).
- An organization move is reconsidered only when contributions or funding cover an organization plan; if it happens, a new decision records the move with its own timing (D-013's "before v0.1" condition stays superseded) and the merge queue replaces the up-to-date rule.
