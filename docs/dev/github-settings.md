# GitHub settings record

The settings the project relies on that cannot be expressed as files in the repository: account, repository and Actions settings, environments, secrets and tokens, apps, rulesets, the roadmap Project and milestones. The target values come from [PRD 39](../prd/39-github-configuration.md); this page records what is actually set, by whom and when, and is diffed against the target at every gate ([PRD 39 §7](../prd/39-github-configuration.md#7-audit-checklist-run-at-each-gate)). Agents update this page from the maintainer's notes; the maintainer owns the settings themselves.

Status legend: **Done** (verified), **Pending** (maintainer action outstanding), **Later** (scheduled for a later task or phase), **Observed** (read through the API without change).

Last full review: 2026-11-04 (bootstrap, before Phase 0 issues were opened).

## 1. Account (`bioedca`, D-057)

| Setting | Target | State |
| --- | --- | --- |
| Owner | Personal account; no organization | Done |
| Two-factor authentication | Enabled | Pending confirmation by the maintainer |
| Account successor | Designated in Settings → Account → Successor settings | **Not yet designated** (2026-11-04): no GitHub account the maintainer trusts with this yet. Revisit before v1.0; Gate G6 requires GOVERNANCE to name a successor and a backup admin |
| Backup admin | Admin collaborator before v1.0 ([PRD 38 §8](../prd/38-maintenance-and-support.md#8-continuity-bus-factor)) | Later (before v1.0); the same person can be the successor |
| GitHub Pro (Student Developer Pack) | Active; re-verification date recorded here | Pending: date to record |
| Sponsors profile | Personal Sponsors profile; `FUNDING.yml` points to it | **Request submitted 2026-11-04**, awaiting GitHub approval; `FUNDING.yml` (bootstrap task 10) waits for it |

## 2. Repository settings (`bioedca/Tlilli`)

Observed through the API on 2026-11-04; the target column is [PRD 39 §2](../prd/39-github-configuration.md#2-repository-settings).

| Setting | Target | State |
| --- | --- | --- |
| Visibility | Public | Done |
| Default branch | `main` | Done |
| Merge methods | Rebase only | Pending: merge commits and squash still allowed |
| Always suggest updating PR branches | On | Pending |
| Allow auto-merge | On | Pending (observed off) |
| Automatically delete head branches | On | Pending (observed off) |
| Wiki | Off | Pending (observed on) |
| Discussions | Off until v0.2 | Done (off) |
| Projects | On | Done |
| Issues | On | Done |
| Description | Set | Done |
| Website | Docs site URL once deployed (task 28) | Later |
| Topics | `scientific-writing`, `manuscript`, `mcp`, `model-context-protocol`, `tauri`, `rust`, `local-first`, `citations`, `agents` | Pending (observed none) |
| Code review limits | Limit to users explicitly granted access | Pending |
| Dependabot alerts, security updates, grouped security updates | On | Pending confirmation |
| Secret scanning and push protection | On | Done (per PRD; confirm at G0) |
| Private vulnerability reporting | On | Pending |
| Code scanning | Via `codeql.yml` (task 21); **default setup off** | Later |
| Pages source | GitHub Actions | Pending |

## 3. Actions settings

| Setting | Target | State |
| --- | --- | --- |
| Actions permissions | Allow `bioedca` plus select actions: GitHub-created, Marketplace verified creators, and the allow-list in `PR-CI-019` | Pending |
| Require actions to be pinned to a full-length commit SHA | **On, after bootstrap task 20** merges. The PRD requires SHA-pinned actions (D-050), but the bootstrap `ci.yml` still references `actions/checkout@v4`, `dtolnay/rust-toolchain@stable`, `Swatinem/rust-cache@v2`, `pnpm/action-setup@v4` and `actions/setup-node@v4` by tag, so enabling the setting now would stop every run | Later (task 20) |
| Fork pull request workflows | Require approval for all external contributors | Pending |
| Default workflow permissions | Read repository contents and packages | Pending |
| Allow GitHub Actions to create and approve pull requests | Off | Pending |

## 4. Environments and variables (`PR-CI-007`, D-060)

| Item | Target | State |
| --- | --- | --- |
| Environment `release` | Required reviewer `bioedca` (backup admin once named); admin bypass off; deployment refs: branch `main`, tag `v*`; wait timer 0 | Pending |
| Environment `automation` | No reviewer; deployment ref: branch `main` | Pending |
| Repository variable `HANDOFF_ACTIVE` | `false` | Pending |
| Repository-level secrets | None | Done (none exist) |

## 5. Secrets and tokens inventory

All tokens are issued by the maintainer's account and rotated yearly ([PRD 38 §9](../prd/38-maintenance-and-support.md#9-maintenance-cadence-after-v10)). Values are never recorded here; names, scopes and expiry dates are.

| Secret | Environment | Kind and scope | Created | Expires | State |
| --- | --- | --- | --- | --- | --- |
| `TAURI_SIGNING_PRIVATE_KEY` | `release` | Updater minisign private key (contents of the key file), key ID `B83A0AA7DD3EDF35` | key generated 2026-11-04 | n/a (key custody per `PR-REL-034`) | Pending upload to the environment |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | `release` | Passphrase of the key above | 2026-11-04 | n/a | Pending upload |
| `RELEASE_PLZ_TOKEN` | `automation` | Fine-grained PAT `tlilli-release-plz`: repository `bioedca/Tlilli`; Contents read/write, Pull requests read/write | — | — | Pending |
| `PROJECT_TOKEN` | `automation` | Fine-grained PAT `tlilli-project`: repository `bioedca/Tlilli`; Issues read, Pull requests read; account permission Projects read/write | — | — | Pending (after the Project exists) |
| `HOMEBREW_TAP_TOKEN` | `release` | Fine-grained PAT `tlilli-homebrew-tap`: repository `bioedca/homebrew-tlilli`; Contents read/write, Pull requests read/write | — | — | Later (after the tap repository exists, task 7) |
| `WINGET_TOKEN` | `release` | **Classic** PAT `tlilli-winget`, scope `public_repo` only (a fine-grained token cannot open pull requests on `microsoft/winget-pkgs`, which the maintainer does not own) | — | — | Later (task 26, after forking `microsoft/winget-pkgs`) |
| crates.io | n/a | Trusted publishing (OIDC) per crate for `release-plz.yml`, environment `automation`; the first publish of each crate is manual with a short-lived crates.io API token named `tlilli-<crate>-first-publish` (scopes `publish-new` + `publish-update`, 7-day expiry, revoked after use) | — | — | Later (v0.1 for `tlilli-core`; v0.2 for `tlilli-mcp`, `tlilli-cli`) |
| Codecov | n/a | No token: `codecov/codecov-action` with `use_oidc: true` and `id-token: write` | — | — | Later (task 20) |

## 6. Updater signing key (`PR-REL-034`, T-09)

- Generated offline by the maintainer on 2026-11-04 with `cargo tauri signer generate`.
- Key ID: `B83A0AA7DD3EDF35`.
- Custody: private key and passphrase as separate password-manager entries; one sealed offline copy held by the maintainer until a backup admin is named, then handed to them; the `release` environment secret is the only online copy. The private key file was deleted from the generating machine.
- Restore drill: issue #5, yearly, next due 2027-11-04.
- Public key, exactly as it goes into `tauri.conf.json` → `plugins.updater.pubkey` (bootstrap task 14; it is the base64 of the `.pub` file, not a path):

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
| Claude (GitHub App) | Installed on `Tlilli`; extend to the companion repositories when agents work there | Done |
| CodeRabbit | Installed; Open Source plan; automatic reviews disabled by `.coderabbit.yaml` | Done (reviewed PRs 1–3; "Review skipped" on PR 3 after the config landed) |
| OpenAI Codex | Installed; Code review on; **Automatic reviews off** (repository and personal default) | Pending |
| Greptile | Installed; one Base-tier seat; triggers only labels `gate` and `review:deep`; trigger on updates off; T-Rex when offered | Pending. T-Rex environment: configure once a buildable workspace exists (tasks 12–14); the cloud sandbox cannot reach `api.greptile.com` or `app.greptile.com` under the current network policy |
| Codecov | App installed; OIDC uploads, no token | Pending |
| DCO | App installed; status check `DCO` | Done (check `DCO` reported success on PR 6, 2026-11-04) |
| Zenodo | GitHub integration switched on for `bioedca/Tlilli` | Pending |
| Dependabot | Alerts and security updates on; version updates via `dependabot.yml` (task 21) | Pending |

## 8. Rulesets ([PRD 39 §3](../prd/39-github-configuration.md#3-rulesets-exported-json-kept-in-docsdevgithub-settingsmd))

None exist yet (observed 2026-11-04). The `main` and `tags v*` rulesets are created after bootstrap tasks 19–21 provide the required checks; their exported JSON is pasted here (bootstrap task 27).

## 9. Project and milestones ([PRD 36 §3–4](../prd/36-issues-labels-and-projects.md#3-milestones))

- Project "Tlilli roadmap": Pending (fields and views per PRD 36 §4; the `Gate` field is a single select Yes/No because Projects has no checkbox type).
- Milestones created 2026-11-04 through the API, no due dates: 1 `0 Foundation`, 2 `v0.1 Black ink`, 3 `v0.2 Red ink`, 4 `v0.3 Ledger`, 5 `v0.4 Sweep and style`, 6 `v0.5 Beyond the article`, 7 `v1.0 Public`, 8 `post-1.0`. Descriptions link to the gate sections of [PRD 40](../prd/40-roadmap-and-gates.md).
- Labels: GitHub's ten defaults plus `type/task`, `area/release`, `priority/P2`, `phase/post-1.0`, created 2026-11-04 for issue #5 ahead of `labels.yml` (task 17), which will reconcile colours and descriptions and prune the defaults.

## 10. Companion repositories ([PRD 39 §6](../prd/39-github-configuration.md#6-github-pro-perks-and-platform-extras-in-use-d-044))

| Repository | Purpose | State |
| --- | --- | --- |
| `bioedca/tlilli-release-rehearsal` (private) | Release workflow rehearsal with dummy secrets | Pending |
| `bioedca/homebrew-tlilli` (public) | Homebrew tap | Pending |
| Fork of `microsoft/winget-pkgs` | winget submissions | Later (task 26) |

## 11. Change log

| Date | Change | By |
| --- | --- | --- |
| 2026-11-04 | Page created from the bootstrap walkthrough; updater key generated and public key recorded; successor recorded as not yet designated; Sponsors request submitted; milestones 1–8 and four labels created; restore-drill issue #5 opened; DCO app observed installed | maintainer and agent |
