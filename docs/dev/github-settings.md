# GitHub settings record

The settings the project relies on that cannot be expressed as files in the repository: account, repository and Actions settings, environments, secrets and tokens, apps, rulesets, the roadmap Project and milestones. The target values come from [PRD 39](../prd/39-github-configuration.md); this page records what is actually set, by whom and when, and is diffed against the target at every gate ([PRD 39 §7](../prd/39-github-configuration.md#7-audit-checklist-run-at-each-gate)). Agents update this page from the maintainer's notes; the maintainer owns the settings themselves.

Provenance legend: **Observed** (read through the API by an agent on the date given), **Maintainer** (set by the maintainer and reported; not visible to the repository-scoped API an agent session has), **Pending** (outstanding), **Later** (scheduled for a later task or phase).

Last full review: 2026-11-04, after the maintainer completed the bootstrap runbook sessions A–F (bootstrap tasks 1–8).

What an agent session cannot read, and therefore records as Maintainer: Actions permissions, environments, variables, secrets, collaborators, Pages configuration, Dependabot alert status, other repositories, Projects v2 (GraphQL), and the third-party dashboards (Codex, CodeRabbit, Greptile, Codecov, Zenodo).

## 1. Account (`bioedca`, D-057)

| Setting | Target | State |
| --- | --- | --- |
| Owner | Personal account; no organization | Observed |
| Two-factor authentication | Enabled | Maintainer, 2026-11-04 |
| Account successor | Designated in Settings → Account → Successor settings | **Not yet designated** (2026-11-04): no GitHub account the maintainer trusts with this yet. Revisit before v1.0; Gate G6 requires GOVERNANCE to name a successor and a backup admin |
| Backup admin | Admin collaborator before v1.0 ([PRD 38 §8](../prd/38-maintenance-and-support.md#8-continuity-bus-factor)) | Later (before v1.0); the same person can be the successor |
| GitHub Pro (Student Developer Pack) | Active; re-verification date recorded here | Maintainer, 2026-11-04: active with about two years remaining (re-verification around 2028-11; the exact date is shown on education.github.com/pack). Review at the yearly maintenance pass |
| Sponsors profile | Personal Sponsors profile; `FUNDING.yml` points to it | Live since 2026-11-07 (maintainer); `FUNDING.yml` (bootstrap task 10) points at `github.com/sponsors/bioedca`. Observed signed out on 2026-11-07: the repository page shows the Sponsor button and a "Sponsor this project" section, which stay while Settings > General > Features > Sponsorships is on |

## 2. Repository settings (`bioedca/Tlilli`)

Target column: [PRD 39 §2](../prd/39-github-configuration.md#2-repository-settings).

| Setting | Target | State |
| --- | --- | --- |
| Visibility | Public | Observed |
| Default branch | `main` | Observed |
| Merge methods | Rebase only | Observed 2026-11-04: merge commits off, squash off, rebase on |
| Always suggest updating PR branches | On | Observed on, 2026-11-04 |
| Allow auto-merge | On | Observed on |
| Automatically delete head branches | On | Observed on (merged branches of PRs 6, 7 and 8 were removed) |
| Wiki | Off | Observed off |
| Discussions | Off until v0.2 | Observed off |
| Projects, Issues | On | Observed on |
| Description | Set | Observed |
| Website | Docs site | Observed: `https://bioedca.github.io/Tlilli/` (deploys with task 28) |
| Topics | `scientific-writing`, `manuscript`, `mcp`, `model-context-protocol`, `tauri`, `rust`, `local-first`, `citations`, `agents` | Observed, all nine |
| Code review limits | Limit to users explicitly granted access | Maintainer, 2026-11-04 |
| Dependabot alerts | On | Maintainer, 2026-11-04 (alert status not readable by the session) |
| Dependabot security updates | On | Observed enabled |
| Secret scanning, push protection | On | Observed enabled |
| Private vulnerability reporting | On | Observed enabled |
| Code scanning | Via `codeql.yml` (task 21); **default setup off** | Observed not configured (correct) |
| Pages source | GitHub Actions | Maintainer, 2026-11-04; verified when `docs.yml` deploys (task 28) |
| Interaction limits | None | Observed none |

## 3. Actions settings

| Setting | Target | State |
| --- | --- | --- |
| Actions permissions | Allow `bioedca` plus select actions: GitHub-created, Marketplace verified creators, and the allow-list in `PR-CI-019` | Maintainer, 2026-11-04 |
| Require actions to be pinned to a full-length commit SHA | On (D-050) | Observed on by behaviour: runs 21 and 22 failed at startup with tag references; run 23 passed once pull request 7 pinned `ci.yml` (`actions/checkout` v4.4.0, `actions/setup-node` v4.4.0, `pnpm/action-setup` v4.3.0, `Swatinem/rust-cache` v2.9.3, `dtolnay/rust-toolchain` stable branch head) |
| Fork pull request workflows | Require approval for all external contributors | Maintainer, 2026-11-04 |
| Default workflow permissions | Read repository contents and packages | Maintainer, 2026-11-04 |
| Allow GitHub Actions to create and approve pull requests | Off | Maintainer, 2026-11-04 |

## 4. Environments and variables (`PR-CI-007`, D-060)

| Item | Target | State |
| --- | --- | --- |
| Environment `release` | Required reviewer `bioedca` (backup admin once named); admin bypass off; deployment refs: branch `main`, tag `v*`; wait timer 0 | Maintainer, 2026-11-04 |
| Environment `automation` | No reviewer; deployment ref: branch `main` | Maintainer, 2026-11-04 |
| Repository variable `HANDOFF_ACTIVE` | `false` | Maintainer, 2026-11-04 |
| Repository variable `BACKUP_ADMIN` | Not created. Holds the backup admin's login without `@`, empty until one is named; `gate.yml` (pull request #54) accepts that login as a gate authority only while `HANDOFF_ACTIVE` is `true` and the login is also listed in `CODEOWNERS` (PRD 32 §3, D-053) | Pending: create together with the CODEOWNERS entry (task 1) |
| Repository-level secrets | None | Maintainer: none |

## 5. Secrets and tokens inventory

All tokens are issued by the maintainer's account and rotated yearly ([PRD 38 §9](../prd/38-maintenance-and-support.md#9-maintenance-cadence-after-v10)). Values are never recorded here; names, scopes and expiry dates are. The three tokens created on 2026-11-04 expire on **2027-11-03**; the rotation task is due in the last week of October 2027, together with the key restore drill (issue #5).

| Secret | Environment | Kind and scope | Created | Expires | State |
| --- | --- | --- | --- | --- | --- |
| `TAURI_SIGNING_PRIVATE_KEY` | `release` | Updater minisign private key (contents of the key file), key ID `B83A0AA7DD3EDF35` | 2026-11-04 | n/a (custody per `PR-REL-034`) | Maintainer: stored |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | `release` | Passphrase of the key above | 2026-11-04 | n/a | Maintainer: stored |
| `RELEASE_PLZ_TOKEN` | `automation` | Fine-grained PAT `tlilli-release-plz`: repository `bioedca/Tlilli`; Contents read/write, Pull requests read/write | 2026-11-04 | 2027-11-03 | Maintainer: stored |
| `PROJECT_TOKEN` | `automation` | Fine-grained PAT `tlilli-project`: repository `bioedca/Tlilli`; Issues read, Pull requests read; account permission Projects read/write | 2026-11-04 | 2027-11-03 | Maintainer: stored |
| `HOMEBREW_TAP_TOKEN` | `release` | Fine-grained PAT `tlilli-homebrew-tap`: repository `bioedca/homebrew-tlilli`; Contents read/write, Pull requests read/write | 2026-11-04 | 2027-11-03 | Maintainer: stored |
| `WINGET_TOKEN` | `release` | **Classic** PAT `tlilli-winget`, scope `public_repo` only (D-061) | — | — | Later (task 26, after forking `microsoft/winget-pkgs`) |
| crates.io | n/a | Trusted publishing (OIDC) per crate for `release-plz.yml`, environment `automation`; first publish of each crate is manual with a short-lived crates.io API token named `tlilli-<crate>-first-publish` (scopes `publish-new` + `publish-update`, 7-day expiry, revoked after use) | — | — | Later (v0.1 for `tlilli-core`; v0.2 for `tlilli-mcp`, `tlilli-cli`) |
| Codecov | n/a | No token: `codecov/codecov-action` with `use_oidc: true` and `id-token: write` (D-061), in the `rust-test` job of `ci.yml` | — | — | In use (task 20) |

## 6. Updater signing key (`PR-REL-034`, T-09)

- Generated offline by the maintainer on 2026-11-04 with `cargo tauri signer generate`.
- Key ID: `B83A0AA7DD3EDF35`.
- Custody: private key and passphrase as separate password-manager entries; one sealed offline copy held by the maintainer until a backup admin is named, then handed to them; the `release` environment secret is the only online copy. The private key file was deleted from the generating machine.
- Restore drill: issue #5, yearly, next due 2027-11-04; `yearly.yml` reopens it every 1 November.
- Public key, exactly as it stands in `src-tauri/tauri.conf.json` → `plugins.updater.pubkey` (wired by bootstrap task 14, issue #22; it is the base64 of the `.pub` file, not a path). The app's updater endpoint is `https://bioedca.github.io/Tlilli/updates/stable.json`; `src-tauri/tests/config.rs` fails if the configured key or endpoint drifts from this record or from `site_url` in `mkdocs.yml`:

```text
dW50cnVzdGVkIGNvbW1lbnQ6IG1pbmlzaWduIHB1YmxpYyBrZXk6IEI4M0EwQUE3REQzRURGMzUKUldRMTN6N2Rwd282dUJRZFBvZHBUSFhFT1p2c1VpZ2JMUWF6QWRxTWxJS3BuQ2hXUW5wVWpRcjEK
```

Decoded (minisign format, for manual verification with `minisign -V`):

```text
untrusted comment: minisign public key: B83A0AA7DD3EDF35
RWQ13z7dpwo6uBQdPodpTHXEOZvsUigbLQazAdqMlIKpnChWQnpUjQr1
```

## 7. Apps and integrations ([PRD 39 §5](../prd/39-github-configuration.md#5-apps-integrations-and-secrets-inventory))

| Integration | Required configuration | State |
| --- | --- | --- |
| Claude (GitHub App) | Installed on `Tlilli`; extended to the companion repositories | Observed on `Tlilli`; companion repositories: Maintainer |
| CodeRabbit | Installed; **Team plan** (one seat; the Open Source plan needs a popularity threshold the repository does not meet yet, D-062); automatic reviews disabled by `.coderabbit.yaml`; ledger threshold 1 request per hour repo-wide, the allowance CodeRabbit's replies report (D-087; 2 from 2026-11-07 under D-085, and before that 75% of the Team refill, 6) | Observed: status comments report "Plan: Team" and "Review skipped" on every PR since PR 3 |
| OpenAI Codex | Installed; Code review on; automatic reviews off (repository and personal default); reviews on `@codex review` | Maintainer, 2026-11-04; verified at the first `@codex review` |
| Greptile | Installed; one Base-tier seat (organization Campos Lab); repository connected. `greptile.json` on each PR's source branch overrides the dashboard (Greptile's precedence): labels `gate` and `review:deep` only, automatic review on the PR-open event (`autoReview: ["open"]`), drafts skipped, no re-review on push; marking a labelled Draft Ready starts the review once `greptile.json` is on `main`, and `@greptileai` is kept for a label added after Ready or a review that has not started 10 minutes after Ready (`PR-PRQ-002`); bot authors such as Dependabot are not excluded, so a gated Dependabot PR is reviewed like any other, Base effort, strictness 2, logic and syntax comments only, `docs/**`, root-level Markdown and the lockfiles ignored (Markdown under `skills/` and the crates is reviewed), custom instructions from PRD 32 §2. The dashboard default label `greptile-review` no longer applies. T-Rex environment configured by the maintainer: <https://app.greptile.com/trex/1dc51511-6709-44d3-a27a-b72072df82b7> | Maintainer, 2026-11-04 (seat, install, T-Rex environment). Observed 2026-11-04: an agent session reaches `api.greptile.com` with the CLI and `GREPTILE_API_KEY`; `greptile config --json` lists `greptile.json` as a source and resolves the labels above. The API key cannot read the T-Rex environment (`greptile environment` answers "API key invalid or revoked"; an OAuth admin sign-in is needed); on PR 66 (gated), nothing came from Greptile in the 8 minutes after it was marked Ready at 20:31 UTC; an `@greptileai` comment at 20:41 UTC got the 👀 reaction of `greptile-apps[bot]` within 10 seconds, and its review of e7707ff (confidence 5/5, no comments) two minutes later. PR 70, marked Ready at 22:11 UTC before `greptile.json` reached `main`, got no review. PR 71, the first labelled PR marked Ready after the file was on `main`, got one with no comment: Ready at 22:39 UTC, review at 22:42 UTC. PR 72 did the same on 2026-11-05: Ready at 00:41 UTC, review at 00:45 UTC. So the trigger follows `main`'s `greptile.json`, while the review settings come from the PR's branch |
| Codecov | App installed; OIDC uploads, no token | Maintainer, 2026-11-04; verified at the first coverage upload (task 20) |
| DCO | App installed; status check `DCO` | Observed: `DCO` success on PRs 6, 7 and 8 |
| Zenodo | GitHub integration switched on for `bioedca/Tlilli` | Maintainer, 2026-11-04; archives on the first published release |
| Dependabot | Alerts and security updates on; version updates via `dependabot.yml` (task 21) | Security updates observed; alerts Maintainer; version updates Later |

## 8. Rulesets ([PRD 39 §3](../prd/39-github-configuration.md#3-rulesets-exported-json-kept-in-docsdevgithub-settingsmd))

None exist (observed 2026-11-04). The `main` and `tags v*` rulesets are created after bootstrap tasks 19–21 provide the required checks; their exported JSON is pasted here (bootstrap task 27).

## 9. Project, milestones and labels ([PRD 36](../prd/36-issues-labels-and-projects.md))

- Project "Tlilli roadmap": Maintainer, 2026-11-04, created with the fields and views of PRD 36 §4 (`Gate` as a single select Yes/No, D-061). URL: <https://github.com/users/bioedca/projects/5> (project number 5; `project.yml` adds every new issue and PR to it, bootstrap task 23). Agent sessions cannot read or write Projects v2 (GraphQL is refused), so the `CodeRabbit requests` and `Greptile reviews` ledger fields are filled by the maintainer at triage from the agents' PR bodies and session reports until an agent-writable ledger exists.
- Milestones (Observed, created 2026-11-04 through the API, no due dates): 1 `0 Foundation`, 2 `v0.1 Black ink`, 3 `v0.2 Red ink`, 4 `v0.3 Ledger`, 5 `v0.4 Sweep and style`, 6 `v0.5 Beyond the article`, 7 `v1.0 Public`, 8 `post-1.0`.
- Labels: the full scheme of PRD 36 §2 (60 labels: 11 type, 12 area, 4 priority, 5 status, 8 phase, 13 control, 5 size, 2 community) was created through the API on 2026-11-04 ahead of `labels.yml` (task 17), which becomes the source of truth and prunes GitHub's defaults that are not in the scheme (`bug`, `documentation`, `duplicate`, `enhancement`, `invalid`, `question`, `wontfix`, `accessibility`).

## 10. Companion repositories ([PRD 39 §6](../prd/39-github-configuration.md#6-github-pro-perks-and-platform-extras-in-use-d-044))

| Repository | Purpose | State |
| --- | --- | --- |
| `bioedca/tlilli-release-rehearsal` (private) | Release workflow rehearsal with dummy secrets; environments `release` and `automation` mirrored | Maintainer, 2026-11-04 (not visible to this session) |
| `bioedca/homebrew-tlilli` (public) | Homebrew tap; cask skeleton and `brew audit` CI in task 7's PR | Maintainer, 2026-11-04 (not visible to this session) |
| Fork of `microsoft/winget-pkgs` | winget submissions | Later (task 26) |

## 11. Name clearance (D-035, R-07)

Not yet run. The maintainer scoped the trademark searches (USPTO, EUIPO, TMview, WIPO Global Brand Database; classes 9 and 42) as later agent work before `v0.1.0`, per D-035; issue #16 tracks it in milestone `v0.1 Black ink`. The verdict and screenshots are recorded there and as the closure of D-035 in the decision log. Package names observed free on 2026-11-04: `tlilli`, `tlilli-core`, `tlilli-mcp`, `tlilli-cli` on crates.io; `tlilli` on npm and PyPI.

## 12. Change log

| Date | Change | By |
| --- | --- | --- |
| 2026-11-04 | Page created from the bootstrap walkthrough; updater key generated and public key recorded; successor recorded as not yet designated; Sponsors request submitted; milestones 1–8 created; restore-drill issue #5 opened; DCO app observed installed; SHA-pinning setting enabled and `ci.yml` pinned (pull request 7); CodeRabbit plan recorded as Team | maintainer and agent |
| 2026-11-04 | Full refresh after runbook sessions A–F: observed states re-read through the API; maintainer-reported states for environments, tokens, Actions permissions, apps, Project and companion repositories; full label scheme created; remaining items: merge methods and branch-update suggestion (two clicks), Project URL | maintainer and agent |
| 2026-11-04 | Pro horizon (about two years), token expiry 2027-11-03 and the deferral of the trademark search to an agent task before v0.1.0 recorded from the maintainer's notes | maintainer and agent |
| 2026-11-04 | Merge methods observed rebase-only with branch-update suggestion on; Project URL recorded (projects/5) | maintainer and agent |
| 2026-11-04 | Updater public key (key ID `B83A0AA7DD3EDF35`) wired into `src-tauri/tauri.conf.json` with the `stable.json` endpoint on the docs site (bootstrap task 14) | agent |
| 2026-11-07 | Sponsors profile recorded as live; the repository page observed showing the Sponsor button | maintainer and agent |
| 2026-11-08 | CodeRabbit ledger threshold lowered to 1 request an hour (D-087), the allowance CodeRabbit reported on pull request 101 | maintainer and agent |
