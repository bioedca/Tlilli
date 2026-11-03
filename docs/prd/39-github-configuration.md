# 39 · GitHub configuration

Everything the project relies on in GitHub, as a checklist that can be audited. Settings that cannot be expressed as files are exported to `docs/dev/github-settings.md` (rulesets as JSON, app list, environment protection) and reviewed at each gate.

## 1. Organization (D-013)

| Setting | Value |
| --- | --- |
| Organization | `tlilli` (free plan), created and the repository transferred before `v0.1.0`; old URLs redirect. Owners: bioedca (+ a backup owner from v1.0, [38](38-maintenance-and-support.md) §8) |
| Base permissions | Read |
| 2FA | Required for all members |
| Teams | `maintainers` (bioedca) used in CODEOWNERS; `contributors` dormant |
| Actions | "Allow select actions and reusable workflows": GitHub-owned, verified creators, plus the allow-list in `PR-CI-019`; default workflow permissions **read**; "Allow GitHub Actions to create and approve pull requests" **off** (release-plz uses its own token) |
| Fork PR workflows | Require approval for all outside collaborators |
| Secrets | Organization-level: none. Repository environment `release` only |
| Sponsors | Org Sponsors profile enabled; `FUNDING.yml` points to it (or to the personal profile until the org profile is approved) |
| Projects | "Tlilli roadmap" owned by the org |
| Discussions | Enabled at v0.2 |

## 2. Repository settings

| Setting | Value |
| --- | --- |
| Visibility | Public |
| Features | Issues on; Projects on; Discussions on from v0.2; Wiki **off** (docs site instead); Sponsorships on; Preserve this repository (Arctic Code Vault) default |
| Default branch | `main` |
| Pull requests | Allow **rebase merging only** (merge commits off, squash off); "Always suggest updating pull request branches" on; "Allow auto-merge" on; "Automatically delete head branches" on |
| Merge queue | Enabled on `main` via the ruleset (§3) |
| Pages | Source: GitHub Actions; custom domain after D-035; HTTPS enforced |
| Security | Dependabot alerts and security updates on; Dependabot version updates per `dependabot.yml`; secret scanning + push protection on (already); private vulnerability reporting on; code scanning (CodeQL) via workflow; dependency graph on |
| Code review limits | "Limit to users explicitly granted access" on (only collaborators can approve/request changes) |
| Interaction limits | None by default; temporary limits available during incidents |
| Topics | `scientific-writing`, `manuscript`, `mcp`, `model-context-protocol`, `tauri`, `rust`, `local-first`, `citations`, `agents` |
| Social preview, description, website | Set to the docs site |

## 3. Rulesets (exported JSON kept in `docs/dev/github-settings.md`)

**Ruleset `main`** (target: `main`, enforcement: active, bypass list: **empty**)
- Restrict deletions; block force pushes; require linear history.
- Require a pull request before merging: required approvals **0** (the gate is a status check, [32](32-code-review.md) §5); dismiss stale approvals on push; require conversation resolution; require review from Code Owners **off** (cannot be satisfied by the author of record, D-014); allowed merge methods: rebase.
- Require status checks to pass: strict mode off (the queue rebases); checks listed in `PR-GIT-043`.
- Require merge queue: method rebase; build concurrency 5; min group 1; max group 5; wait 2 min; timeout 60 min; only merge non-failing entries.
- Require signed commits: off (D-012).
- Require deployments to succeed: off.

**Ruleset `release/*`** (post-1.0): same as `main` except merge queue optional and the `backport` label required by `gate.yml` logic.

**Ruleset `tags v*`**: restrict creation to the `release-plz` app/token identity and org owners; block update and deletion.

**Ruleset `all branches`**: block force pushes to any branch not owned by the pusher (GitHub cannot express this; approximated by `PR-GIT-005` and the one-writer rule) — recorded as a policy, not a technical rule.

## 4. Repository files that configure GitHub

| File | Content |
| --- | --- |
| `.github/CODEOWNERS` | gated paths → `@tlilli/maintainers` ([32](32-code-review.md) §3) |
| `.github/labels.yml` | label scheme ([36](36-issues-labels-and-projects.md) §2) |
| `.github/labeler.yml` | path → `area/*`, `gate`, `review:deep` |
| `.github/ISSUE_TEMPLATE/*.yml`, `config.yml` | nine forms, blank disabled, contact links |
| `.github/PULL_REQUEST_TEMPLATE.md` | [31](31-pull-requests.md) §3 |
| `.github/dependabot.yml` | cargo, npm, github-actions, pip weekly, grouped `patch-minor` and `major`; `open-pull-requests-limit: 5` |
| `.github/FUNDING.yml` | Sponsors |
| `.github/workflows/*.yml` | [33](33-ci-cd.md) |
| `.github/SECURITY.md` → root `SECURITY.md` | disclosure policy |
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
| CodeRabbit | GitHub App | pull requests, contents read, checks | Open Source plan; auto-review off |
| Greptile | GitHub App | pull requests, contents read | label-triggered |
| Codecov | GitHub App + token | checks, statuses | `CODECOV_TOKEN` repo secret (upload only) |
| DCO | GitHub App (probot) | statuses | required check `DCO` |
| Zenodo | webhook | releases read | archives on publish |
| Dependabot | native | — | grouped weekly |
| release-plz | Action + token | `RELEASE_PLZ_TOKEN`: fine-grained PAT (or org GitHub App) with contents write, pull requests write, workflows read; expires yearly | needed so tags trigger workflows |
| crates.io | trusted publishing (OIDC) | per-crate trusted publisher config for the `release-plz.yml` workflow | no long-lived token |
| GitHub Pages | OIDC | `pages: write`, `id-token: write` | — |
| Projects | token | `PROJECT_TOKEN`: fine-grained PAT with project write | `project.yml` |
| Homebrew tap | token | `HOMEBREW_TAP_TOKEN`: fine-grained PAT scoped to `tlilli/homebrew-tap` contents+PRs | `release` environment |
| winget | token | `WINGET_TOKEN`: PAT for the fork of `microsoft/winget-pkgs` | `release` environment |
| Updater | secret | `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | `release` environment; offline backups |

Environment `release`: required reviewer bioedca; deployment branches and tags limited to `v*` tags and `main`; secrets listed above; wait timer 0. All PATs are fine-grained, scoped to the minimum repositories, and tracked in `docs/dev/github-settings.md` with expiry dates; a yearly rotation task is scheduled.

## 6. GitHub Pro perks and platform extras in use (D-044)

| Perk / feature | Use |
| --- | --- |
| **Codespaces** (Pro includes 180 core-hours and 20 GB per month, billed to the personal account for org repos on the free plan) | `.devcontainer/devcontainer.json`: Ubuntu 24.04 image with Rust, Node 22, pnpm, Tauri Linux prerequisites, `xvfb`, the `desktop-lite` feature (noVNC on a forwarded port) so a Tauri window can be seen in a browser; prebuilds off (cost); used for visual checks the cloud sandbox cannot do and as a second environment for agents |
| **Private companion repository** `bioedca/tlilli-release-rehearsal` (user-owned so Pro's 3,000 private Actions minutes and private branch protection apply) | Mirror of `.github/workflows/release*.yml`, `post-release.yml`, `release-plz.yml` with dummy secrets; every change to those workflows is rehearsed there with `dry_run=true` before landing (INTERSECT: test publishing first) |
| **Repository insights** (pulse, contributors, traffic, dependency graph) | Reviewed at monthly metrics; traffic informs docs priorities |
| **Sponsors** | `FUNDING.yml`; income earmarked first for Apple notarization (USD 99/yr) and then Windows signing if SignPath is not granted |
| **Private vulnerability reporting + security advisories** | Disclosure channel and CVE issuance |
| **Artifact attestations** | Free on public repos; used for every release asset |
| **Merge queue, rulesets, code owners** | Available on org-owned public repos (reason for the org move) |
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
