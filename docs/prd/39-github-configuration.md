# 39 · GitHub configuration

Everything the project relies on in GitHub, as a checklist that can be audited. Settings that cannot be expressed as files are exported to `docs/dev/github-settings.md` (rulesets as JSON, app list, environment protection) and reviewed at each gate.

## 1. Account (D-057)

| Setting | Value |
| --- | --- |
| Owner | Personal account `bioedca`; repository stays `bioedca/Tlilli`. GitHub Pro comes from the Student Developer Pack and applies to the personal account only; no organization is created (an organization would not inherit Pro, and an organization plan cannot be afforded). Revisit only when contributions or funding cover it |
| 2FA | Enabled on the account (required for Sponsors and recommended by the threat register) |
| Successor and backup admin | A GitHub account successor designated in Settings → Account → Successor settings (ownership transfer on an authorized request after death or incapacity; not a temporary-absence mechanism). A trusted collaborator gets admin on the repository before v1.0, is listed in CODEOWNERS (gate authority, used only during a handoff) and is added as an allowed `release` environment reviewer, so gated merges, releases and secret rotation can continue during an absence ([38](38-maintenance-and-support.md) §8) |
| Teams | None (personal accounts have no teams); CODEOWNERS names `@bioedca` |
| Actions (per repository) | "Allow select actions and reusable workflows": GitHub-owned, verified creators, plus the allow-list in `PR-CI-019`; default workflow permissions **read**; "Allow GitHub Actions to create and approve pull requests" **off** (release-plz uses its own token) |
| Fork PR workflows | Require approval for all outside collaborators |
| Secrets | Two repository environments: `release` (signing keys, packaging tokens; required reviewers) and `automation` (`RELEASE_PLZ_TOKEN`, `PROJECT_TOKEN`; no reviewer, `main` only). No repository-level or account-level secrets |
| Sponsors | Personal Sponsors profile; `FUNDING.yml` points to it |
| Projects | "Tlilli roadmap" owned by the user account |
| Discussions | Enabled at v0.2 |

## 2. Repository settings

| Setting | Value |
| --- | --- |
| Visibility | Public |
| Features | Issues on; Projects on; Discussions on from v0.2; Wiki **off** (docs site instead); Sponsorships on; Preserve this repository (Arctic Code Vault) default |
| Default branch | `main` |
| Pull requests | Allow **rebase merging only** (merge commits off, squash off); "Always suggest updating pull request branches" on; "Allow auto-merge" on; "Automatically delete head branches" on |
| Merge queue | Not available on personal-account repositories (D-057); replaced by "require branches to be up to date before merging" in the ruleset (§3) |
| Pages | Source: GitHub Actions; custom domain after D-035; HTTPS enforced |
| Security | Dependabot alerts and security updates on; Dependabot version updates per `dependabot.yml`; secret scanning + push protection on (already); private vulnerability reporting on; code scanning (CodeQL) via workflow; dependency graph on |
| Code review limits | "Limit to users explicitly granted access" on (only collaborators can approve/request changes) |
| Interaction limits | None by default; temporary limits available during incidents |
| Topics | `scientific-writing`, `manuscript`, `mcp`, `model-context-protocol`, `tauri`, `rust`, `local-first`, `citations`, `agents` |
| Social preview, description, website | Set to the docs site |

## 3. Rulesets (exported JSON kept in `docs/dev/github-settings.md`)

**Ruleset `main`** (target: `main`, enforcement: active, bypass list: the **Repository admin** role with bypass mode **pull requests only**, D-078)
- Bypass: a pull request merge only, never a push (`PR-GIT-040`); used only for a gated PR on the maintainer's decision, by the maintainer or by an agent with a relayed authorization recorded in the PR body (`PR-GIT-058`). Bootstrap task 27 checks that an agent session's merge (the maintainer's account through the Claude GitHub App) counts as the admin role; if it does not, relayed gated PRs wait for the maintainer to merge them and `docs/dev/github-settings.md` records the gap.
- Restrict deletions; block force pushes; require linear history.
- Require a pull request before merging: required approvals **0** (the gate is a status check, [32](32-code-review.md) §5); dismiss stale approvals on push; require conversation resolution; require review from Code Owners **off** (cannot be satisfied by the author of record, D-014); allowed merge methods: rebase.
- Require status checks to pass: **strict** ("Require branches to be up to date before merging") on; checks listed in `PR-GIT-043`, with `gate/maintainer` required as a commit status context from GitHub Actions (`PR-REV-010`).
- Require signed commits: off (D-012).
- Require deployments to succeed: off.

**Ruleset `release/*`** (post-1.0): same as `main`, with the `backport` label required by `gate.yml` logic.

**Ruleset `tags v*`**: restrict creation to the `release-plz` token identity and the repository owner; block update and deletion.

**Ruleset `all branches`**: block force pushes to any branch not owned by the pusher (GitHub cannot express this; approximated by `PR-GIT-005` and the one-writer rule) — recorded as a policy, not a technical rule.

## 4. Repository files that configure GitHub

| File | Content |
| --- | --- |
| `.github/CODEOWNERS` | gated paths → `@bioedca` and the backup admin once named ([32](32-code-review.md) §3; the backup admin uses gate authority only during a handoff) |
| `.github/labels.yml` | label scheme ([36](36-issues-labels-and-projects.md) §2) |
| `.github/labeler.yml` | path → `area/*`, `gate`, `review:deep` |
| `.github/ISSUE_TEMPLATE/*.yml`, `config.yml` | ten forms, blank disabled, contact links |
| `.github/PULL_REQUEST_TEMPLATE.md` | [31](31-pull-requests.md) §3 |
| `.github/dependabot.yml` | cargo, npm, github-actions, pip, devcontainers weekly with a 7-day cooldown; version updates grouped `patch-minor` and `major`, security updates ungrouped; `open-pull-requests-limit: 5` (`PR-MNT-010`, D-074) |
| `.github/FUNDING.yml` | Sponsors |
| `.github/workflows/*.yml` | [33](33-ci-cd.md) |
| `SECURITY.md` (root only; no `.github/SECURITY.md`, which GitHub would show instead of the full policy) | disclosure policy |
| `codecov.yml` | flags per crate; patch status 80% for `tlilli-core`, `tlilli-mcp`; project informational; comment layout minimal |
| `.coderabbit.yaml`, `greptile.json`, `AGENTS.md` | review lanes ([32](32-code-review.md) §2) |
| `release-plz.toml`, `cliff.toml` | releases ([37](37-releases-and-packaging.md)) |
| `deny.toml` | advisories deny, licenses allow-list, bans, sources crates.io only |
| `commitlint.config.mjs` | types, scopes, lengths |
| `lefthook.yml` | local hooks |
| `.devcontainer/devcontainer.json` | Codespaces (§6) |
| `CITATION.cff` | citation metadata |

## 5. Apps, integrations and secrets inventory

| Integration | Kind | Permissions (minimum) | Notes |
| --- | --- | --- | --- |
| Claude (GitHub App) | agent sessions | contents, pull requests, issues (as granted) | already installed |
| OpenAI Codex | GitHub App | pull requests read/write, contents read | automatic reviews **off**; `@codex review` |
| CodeRabbit | GitHub App | pull requests, contents read, checks | Team plan, one seat (Open Source plan when the repository qualifies, D-062); auto-review off |
| Greptile | GitHub App | pull requests, contents read | label-triggered |
| Codecov | GitHub App + OIDC | checks, statuses | Codecov GitHub App installed; `codecov/codecov-action` runs with `use_oidc: true` and the uploading jobs grant `id-token: write`; no token is stored (`PR-CI-007`, D-061); the coverage upload is skipped for Dependabot-authored PRs |
| DCO | GitHub App (probot) | statuses | required check `DCO` |
| Zenodo | webhook | releases read | archives on publish |
| Dependabot | native | — | grouped weekly |
| release-plz | Action + token | `RELEASE_PLZ_TOKEN`: fine-grained PAT (or a GitHub App if a second maintainer joins) with contents write, pull requests write, workflows read; expires yearly | environment `automation`; needed so tags trigger workflows |
| crates.io | trusted publishing (OIDC) | per-crate trusted publisher config for the `release-plz.yml` workflow | no long-lived token |
| GitHub Pages | OIDC | `pages: write`, `id-token: write` | — |
| Projects | token | `PROJECT_TOKEN`: fine-grained PAT with project write | `project.yml` (environment `automation`) |
| Homebrew tap | token | `HOMEBREW_TAP_TOKEN`: fine-grained PAT scoped to `bioedca/homebrew-tlilli` contents+PRs | `release` environment |
| winget | token | `WINGET_TOKEN`: **classic** PAT with the single scope `public_repo`, one-year expiry. The only classic token: `vedantmgoyal9/winget-releaser` opens the pull request on `microsoft/winget-pkgs`, a repository the maintainer does not own, and fine-grained PATs cannot create pull requests there (D-061) | `release` environment; created only when `post-release.yml` lands and after `microsoft/winget-pkgs` is forked under `bioedca` |
| Updater | secret | `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | `release` environment; offline backups |

Environment `release`: required reviewers bioedca and the backup admin once named (any one approves); deployment branches and tags limited to `v*` tags and `main`; holds `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD`, `HOMEBREW_TAP_TOKEN`, `WINGET_TOKEN`; wait timer 0. Environment `automation`: no required reviewer; deployment branches limited to `main`; holds `RELEASE_PLZ_TOKEN` and `PROJECT_TOKEN`; declared by the `release-plz.yml`, `prerelease.yml` (tag push) and `project.yml` jobs, which run on `main` or in base-branch context, so a PR workflow can never read them. All PATs except `WINGET_TOKEN` are fine-grained and scoped to the minimum repositories; `WINGET_TOKEN` is a classic PAT limited to the `public_repo` scope (D-061). All are tracked in `docs/dev/github-settings.md` with expiry dates; a yearly rotation task is scheduled.

## 6. GitHub Pro perks and platform extras in use (D-044)

| Perk / feature | Use |
| --- | --- |
| **Codespaces** (Pro via the Student Developer Pack includes 180 core-hours and 20 GB per month; 120 core-hours and 15 GB if Pro lapses) | `.devcontainer/devcontainer.json`: Ubuntu 24.04 image with Rust, Node 22, pnpm, Tauri Linux prerequisites, `xvfb`, the `desktop-lite` feature (noVNC on a forwarded port) so a Tauri window can be seen in a browser; prebuilds off (cost); used for visual checks the cloud sandbox cannot do and as a second environment for agents |
| **Private companion repository** `bioedca/tlilli-release-rehearsal` (user-owned so Pro's 3,000 private Actions minutes and private branch protection apply; made public with dummy secrets if Pro lapses, see the Student Developer Pack row) | Mirror of `.github/workflows/release*.yml`, `post-release.yml`, `release-plz.yml` with dummy secrets; every change to those workflows is rehearsed there with `dry_run=true` before landing (INTERSECT: test publishing first). Disposable: recreated from `main` on any ownership change ([38](38-maintenance-and-support.md) §8) |
| **Repository insights** (pulse, contributors, traffic, dependency graph) | Reviewed at monthly metrics; traffic informs docs priorities |
| **Sponsors** | `FUNDING.yml`; income earmarked first for Apple notarization (USD 99/yr) and then Windows signing if SignPath is not granted |
| **Private vulnerability reporting + security advisories** | Disclosure channel and CVE issuance |
| **Artifact attestations** | Free on public repos; used for every release asset |
| **Rulesets, code owners, auto-merge, environments, Pages, attestations** | Available on personal public repositories on every plan, so none of them depends on Pro. Merge queue is organization-only and is replaced by the up-to-date rule (D-057) |
| **Student Developer Pack** | Source of the Pro upgrade (time-limited to student status; Pro only enlarges quotas: 3,000 instead of 2,000 private Actions minutes per month for the rehearsal repository and 180 instead of 120 Codespaces core-hours; if it lapses, the rehearsal repository is made public with dummy secrets, which is mandatory because a private repository on the free plan loses rulesets and branch protection, and public Actions minutes are unlimited); its one-year free domain offers are a candidate for the docs custom domain after D-035; Copilot Pro is included but is not a review lane (D-015) |
| **GitHub Pages** | Docs site and updater manifests |
| **Projects v2** | Roadmap board |
| **Discussions** | Community from v0.2 |
| Not used | GitHub Copilot (not a review lane by decision; the three lanes are Codex, CodeRabbit, Greptile), Wiki, GitHub Packages |

## 7. Audit checklist (run at each gate)

- Ruleset `main` matches §3 (export JSON, diff against `docs/dev/github-settings.md`).
- Required checks list equals `PR-GIT-043`.
- Apps installed equal §5; permissions unchanged; automatic reviews off in Codex and CodeRabbit.
- Secrets: all in `release` environment; expiry dates > 90 days away.
- Labels match `labels.yml` (sync workflow green).
- Pages, Discussions, security features as in §2.
- Codespaces and companion repo still within free quotas (billing page).
