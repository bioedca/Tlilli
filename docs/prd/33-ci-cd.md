# 33 · CI/CD

INTERSECT CI/CD rules adopted: separate CI from CD; CD triggers on tags, with `workflow_dispatch` for rehearsal; rely on exit codes and never mask failures; pin action versions; matrix with `fail-fast: false`; pin runner images instead of `-latest`; badges for `main`; artifacts between jobs; secrets only in GitHub Secrets with narrow permissions; docs are their own artifact; start small and iterate. Threat Assessment rules: least privilege, provenance, patching.

## 1. Workflow inventory

| Workflow file | Triggers | Purpose | Secrets |
| --- | --- | --- | --- |
| `ci.yml` | `pull_request` (all types incl. `ready_for_review`, `labeled`), `push` to `main` | Linux lane on every PR push; full matrix on Ready/`ci:full`/`main`; all required checks | none (Codecov upload by OIDC: `codecov/codecov-action` with `use_oidc: true`, `id-token: write` on the uploading jobs; skipped for Dependabot-authored PRs) |
| `gate.yml` | `pull_request_target` (no checkout of PR code), `workflow_run` of `gate-relay.yml` | `gate/maintainer` required commit status ([32](32-code-review.md) §5) | none (`GITHUB_TOKEN`: `contents: read`, `pull-requests: write`, `statuses: write`) |
| `gate-relay.yml` | `pull_request_review` | Relays review events to `gate.yml`; `permissions: {}`, no checkout | none |
| `labeler.yml` | `pull_request_target` | Path labels `area/*`, `gate`; size labels; `review:deep` for gated PRs | none |
| `commits.yml` | part of `ci.yml` (`commits` job) | commitlint on all PR commits and title; ≤ 10 commits; branch-name pattern; per-commit `cargo check` (≤ 10 commits) | none |
| `docs.yml` | `push` to `main` (paths `docs/**`, `mkdocs.yml`, `crates/**`), `workflow_dispatch`, `release: published` | Build MkDocs (`--strict`) + rustdoc; deploy to GitHub Pages; publish `updates/*.json` | none (Pages OIDC) |
| `codeql.yml` | `pull_request`, `push` to `main`, weekly cron | CodeQL for Rust, JavaScript/TypeScript and the workflows (`actions`) | none |
| `scorecard.yml` | weekly cron, `push` to `main` | OpenSSF Scorecard; publishes results and badge | none (OIDC) |
| `nightly.yml` | daily cron 03:17 UTC, `workflow_dispatch` | Fuzz targets (cargo-fuzz, 10 min each); Playwright full UI suite; LaTeX compile of exports in a TeX container; benchmarks (criterion) vs baseline; link check (lychee); `cargo deny check advisories` | none |
| `weekly.yml` | weekly cron Monday 05:23 UTC | cargo-mutants on `tlilli-core` (score to tracking issue); label-audit report (`docs:not-needed`, `size:override`, `needs-tests`); stale PR/branch sweep; review-budget ledger summary | none |
| `release-plz.yml` | `push` to `main`, `workflow_dispatch` | `release-plz release-pr` (opens/updates the release PR) and `release-plz release` (tags `vX.Y.Z` and publishes crates via trusted publishing when the release PR merged) | `RELEASE_PLZ_TOKEN` (environment `automation`; fine-grained PAT or GitHub App: contents+pull-requests write; needed so the tag push triggers `release.yml`), crates.io OIDC |
| `release.yml` | `push` tags `v*`, `workflow_dispatch` (rehearsal with `dry_run`) | tauri-action matrix → draft GitHub Release with bundles, `latest.json`, `.sig`; SBOM; checksums; attestations; size assertions | `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` (environment `release`) |
| `prerelease.yml` | `workflow_dispatch` (inputs: `version`, e.g. `0.3.0-beta.1`) | Same as `release.yml` from `main` HEAD with `tauri build --config '{"version":"<v>"}'`; prerelease flag; `beta.json` | `RELEASE_PLZ_TOKEN` (environment `automation`) for the tag push, which the `tags v*` ruleset allows for that identity; `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` (environment `release`) |
| `post-release.yml` | `release: published` | Homebrew cask bump PR, winget manifest PR, Flathub manifest PR (or confirm external-data-checker), docs `updates/stable.json`/`beta.json` update, Zenodo check, announcement Discussion draft | `HOMEBREW_TAP_TOKEN`, `WINGET_TOKEN` (environment `release`) |
| `labels-sync.yml` | `push` to `main` (path `.github/labels.yml`), `workflow_dispatch` | Sync labels from `.github/labels.yml` (create/update/prune) | none (`issues: write`) |
| `project.yml` | `issues` opened/reopened/labeled, `pull_request_target` opened (base-branch context, no checkout of PR code) | Add items to the Project; set Phase from milestone, Area from label | `PROJECT_TOKEN` (environment `automation`; fine-grained PAT with project write) |
| `dependabot-automerge.yml` | `pull_request` by `dependabot[bot]` | Enable auto-merge for grouped patch/minor updates after CI; majors left for triage; enabled with `GITHUB_TOKEN`, so its merges start no `push` workflows (D-075) | none |
| `protocol-ref.yml` | part of `ci.yml` (`protocol-ref/drift` job) | `cargo run -p tlilli-cli -- mcp schema --markdown docs/reference/mcp/` then `git diff --exit-code` | none |

Everything a fork PR triggers runs with `permissions: read-all` and no secrets; privileged workflows use `pull_request_target` without checking out PR code, or run only on `main`/tags.

## 2. `ci.yml` in detail

```yaml
name: ci
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review, labeled]
  push:
    branches: [main]
concurrency:
  group: ci-${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
permissions: read-all
env:
  CARGO_TERM_COLOR: always
  RUSTFLAGS: -D warnings
```

| Job (check name) | Runner | Steps | Required | Runs on Drafts |
| --- | --- | --- | --- | --- |
| `rust-lint` | `ubuntu-24.04` | `rustup` from `rust-toolchain.toml`; `Swatinem/rust-cache`; `cargo fmt --all --check`; `cargo clippy --workspace --all-targets --all-features -- -D warnings`; `cargo deny check` (advisories, licenses, bans, sources); `cargo doc --no-deps` with `RUSTDOCFLAGS=-D warnings` | yes | yes |
| `rust-test` | `ubuntu-24.04` | Tauri Linux prerequisites (apt); `cargo nextest run --workspace --all-features` and `--no-default-features` for core; `cargo llvm-cov nextest --workspace --lcov` → Codecov with flags `tlilli-core`, `tlilli-mcp`, `tlilli-cli`, `app`; `cargo test --doc` | yes | yes |
| `ui` | `ubuntu-24.04` | pnpm (frozen lockfile); `biome ci .`; `pnpm -C ui typecheck`; `vitest run --coverage`; `pnpm -C ui build`; Playwright UI suite against the mocked core (smoke subset on Drafts, full in nightly); upload coverage flag `ui` | yes | yes |
| `docs-build` | `ubuntu-24.04` | `pip install -r docs/requirements.txt` (pinned hashes); `mkdocs build --strict`; `cargo doc --workspace --no-deps` to `site/api`; upload `site/` artifact | yes | yes |
| `commits` | `ubuntu-24.04` | commitlint (config `commitlint.config.mjs`, scopes list) on `${{ github.event.pull_request.base.sha }}..HEAD` and on the PR title; count ≤ 10; branch-name regex; PR template sections present; per-commit `cargo check --workspace` when ≤ 10 commits; no merge commits | yes | yes |
| `size/limit` | `ubuntu-24.04` | compute hand-written changed lines with exclusions ([31](31-pull-requests.md) §2); fail > 400 without `size:override` + reason line; apply `size/*` label (via `labeler.yml`); file-size caps (2 MB, 50 MB per dir) | yes | yes |
| `docs/contract-sync` | `ubuntu-24.04` | if changed files match contract globs (`crates/tlilli-mcp/src/{tools,resources,prompts}/**`, `skills/**`, `crates/tlilli-core/src/storage/**`, `crates/tlilli-cli/src/**`, `src-tauri/tauri.conf.json`) then require a change under `docs/**` or label `docs:not-needed` + reason line | yes | yes |
| `protocol-ref/drift` | `ubuntu-24.04` | regenerate `docs/reference/mcp/` and `docs/reference/schemas/*.json`; `git diff --exit-code` | yes | yes |
| `workflows/zizmor` | `ubuntu-24.04` | `zizmor .github/workflows` (pinned-SHA, template injection, dangerous triggers, credential persistence) at `--min-severity low`; `actionlint` | yes | yes |
| `tauri/linux` | `ubuntu-24.04` | `pnpm -C ui tauri build --no-bundle` (compile check of the full app) | yes | yes |
| `e2e/smoke` | `ubuntu-24.04` | `xvfb-run -a pnpm -C ui test:e2e:desktop` (tauri-driver smoke suite; `test:e2e` is the Playwright browser suite, D-077; ≤ 10 min, 1 retry allowed) | yes | yes |
| `build/macos-arm64`, `build/macos-x86_64`, `build/windows`, `build/linux-bundle` | `macos-15` (both targets), `windows-2025`, `ubuntu-24.04` | `pnpm -C ui tauri build --target <t>` (bundles), upload artifacts (7-day retention); `cargo nextest run --workspace` on macOS and Windows | yes | only if `ready_for_review`, `ci:full` or `push` |
| `codecov/patch/tlilli-core`, `codecov/patch/tlilli-mcp` | Codecov | patch coverage ≥ 80% per flag (`codecov.yml`); project coverage informational | yes | yes |

Draft gating of the matrix: `if: github.event_name != 'pull_request' || github.event.pull_request.draft == false || contains(github.event.pull_request.labels.*.name, 'ci:full')`. Because these checks are required, a Draft cannot merge (`PR-GIT-043`).

Caching: `Swatinem/rust-cache@<sha>` keyed by lockfile and toolchain; pnpm store cache; `sccache` optional (`SCCACHE_GHA_ENABLED`). Timeouts: every job sets `timeout-minutes` (lint 15, test 30, ui 20, matrix 45, e2e 20).

## 3. Rules (PR-CI-001 … 020)

| ID | Rule |
| --- | --- |
| `PR-CI-001` | Every third-party action is pinned to a full commit SHA with a version comment (`uses: actions/checkout@<sha> # v4.2.2`); Dependabot (`github-actions` ecosystem) keeps SHAs current; `zizmor` fails on unpinned uses. |
| `PR-CI-002` | Runner images are pinned (`ubuntu-24.04`, `macos-15`, `windows-2025`) and reviewed quarterly; never `-latest` (INTERSECT). |
| `PR-CI-003` | Least privilege: the workflow-level `permissions` block is `{}` (preferred, zizmor-clean under every persona) or `read-all` where every job needs read access; each job then declares exactly the scopes it needs (`contents: write` for release upload, `pull-requests: write` for labels, `issues: write` for label sync, `id-token: write` for attestations/Pages/crates.io/Codecov OIDC, `pages: write` for Pages deploys). A job that only runs a token-bearing action declares `permissions: {}` (D-064). |
| `PR-CI-004` | No `|| true`, `continue-on-error` or `exit 0` to hide failures except on explicitly experimental matrix entries, which are labelled `experimental` and not required (INTERSECT: never hack exit codes). |
| `PR-CI-005` | `fail-fast: false` on all matrices so one platform failure does not hide another. |
| `PR-CI-006` | Workflows never checkout untrusted PR code in a privileged context (`pull_request_target` jobs do not run `actions/checkout` of the PR head). |
| `PR-CI-007` | Secrets exist only in two environments, plus Dependabot secrets where needed. `release` (required reviewers: the maintainer and the backup admin once named; deployment branches/tags: `v*` tags and `main`) holds the signing keys and the packaging tokens. `automation` (no reviewer; deployment branch: `main` only) holds `RELEASE_PLZ_TOKEN` and `PROJECT_TOKEN`, and the `release-plz.yml`, `prerelease.yml` tag-push and `project.yml` jobs declare it. There are no repository-level secrets. A `pull_request` workflow cannot satisfy either environment's branch policy, so no secret is readable from PR workflows. |
| `PR-CI-008` | Fork PRs require maintainer approval before workflows run (repository setting "Require approval for all outside collaborators"). |
| `PR-CI-009` | A required check that fails after a rebase onto new `main` blocks auto-merge; the author fixes and pushes. Flaky checks are fixed within 48 h or the flaky test is deleted; retries are allowed only for `e2e/smoke` (1 retry). |
| `PR-CI-010` | CI is reproducible locally: `scripts/ci.sh <job>` runs the same commands; `lefthook` pre-commit runs the fast subset. |
| `PR-CI-011` | Coverage: `cargo-llvm-cov` + Codecov with per-crate flags; patch ≥ 80% on `tlilli-core` and `tlilli-mcp` is required; UI and shell are measured, not gated (D-023). |
| `PR-CI-012` | Supply chain: `cargo deny check` on every PR (advisories: deny; licenses: allow-list; bans: duplicates warn, wildcard versions deny; sources: crates.io only); `pnpm audit --audit-level high`; CodeQL weekly and on PRs; Scorecard weekly; Dependabot grouped weekly for cargo, npm, github-actions, pip (docs) and devcontainers (`PR-MNT-010`). |
| `PR-CI-013` | Generated outputs committed in the repo (protocol reference, schemas, insta snapshots) are verified by regenerate-and-diff jobs. |
| `PR-CI-014` | Nightly and weekly jobs open or update a single tracking issue per job (`type/task`, `area/ci`) instead of failing silently; a red nightly for 3 days becomes `priority/P1`. |
| `PR-CI-015` | Every workflow has `concurrency` to cancel superseded PR runs and never cancels `main` or tag runs; only in analysis-only workflows (CodeQL, Scorecard) may a newer pending `main` run replace an older pending one, because it analyses a later commit and nothing is lost (D-077). |
| `PR-CI-016` | Build artifacts from PR runs are kept 7 days; release artifacts are release assets, not workflow artifacts; SBOMs are attached to releases. |
| `PR-CI-017` | Badges in README: CI (`main`), Codecov, Scorecard, latest release, license, DOI. |
| `PR-CI-018` | Workflow changes are gated and are first rehearsed in the private companion repository ([39](39-github-configuration.md) §6) when they touch release or secrets. |
| `PR-CI-019` | Actions used (initial allow-list for the repository's "Allow select actions" setting): `actions/*`, `github/codeql-action`, `ossf/scorecard-action`, `dtolnay/rust-toolchain`, `Swatinem/rust-cache`, `taiki-e/install-action`, `pnpm/action-setup`, `tauri-apps/tauri-action`, `release-plz/action`, `rust-lang/crates-io-auth-action`, `codecov/codecov-action`, `anchore/sbom-action`, `actions/attest`, `zizmorcore/zizmor-action`, `wagoid/commitlint-github-action`, `actions/labeler`, `EndBug/label-sync`, `actions/add-to-project`, `dependabot/fetch-metadata`, `vedantmgoyal9/winget-releaser`, `lycheeverse/lychee-action`. Adding one is a gated change. |
| `PR-CI-020` | The DCO check is the `dco` GitHub App (probot) with default settings (sign-off must match author); no remediation commits. |

## 4. CD: release path (summary; details in [37](37-releases-and-packaging.md))

1. `release-plz.yml` on `main`: maintains the release PR (`chore(release): vX.Y.Z`, label `release`, gated).
2. Maintainer approves and auto-merge lands the release PR.
3. `release-plz.yml` runs again, sees the merged version bump, creates and pushes annotated tag `vX.Y.Z` with `RELEASE_PLZ_TOKEN`, publishes `tlilli-core`, `tlilli-mcp`, `tlilli-cli` to crates.io via trusted publishing.
4. `release.yml` on the tag: matrix build with tauri-action → **draft** GitHub Release with bundles, `latest.json`, `.sig` files; `sbom` job attaches `sbom.spdx.json`; `checksums` job attaches `SHA256SUMS`; `attest` job signs provenance for every asset with `actions/attest` (Sigstore public-good, SLSA Build L2); `verify` job downloads the assets and runs `gh attestation verify` and size assertions.
5. Maintainer reviews the draft notes and clicks **Publish** (the last manual gate, D-025).
6. `post-release.yml` on `release: published`: Homebrew, winget, Flathub, `updates/stable.json`, Zenodo confirmation, announcement draft; `docs.yml` deploys versioned docs (post-1.0).

Rehearsal: the same workflows run in the private companion repository with `workflow_dispatch` `dry_run=true` before any change to them lands here (INTERSECT: test publishing on a test index first).

## 5. Status badges and visibility

README shows: `ci` on `main`, Codecov, Scorecard, latest release, Zenodo DOI, license. The docs site has a "Project status" page listing the last nightly and weekly results from their tracking issues.

## 6. Environment and runner notes

- Linux jobs install Tauri prerequisites: `libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev patchelf xdg-utils`.
- Windows jobs need no extra packages; NSIS and WiX are fetched by the Tauri CLI.
- macOS jobs add targets `aarch64-apple-darwin` and `x86_64-apple-darwin`; no signing identity is configured (unsigned builds, D-026).
- The cloud development sandbox mirrors the Linux lane; `scripts/ci.sh` is what agents run before pushing.

## 7. Security of the pipeline (from the threat register)

T-07, T-08, T-10 mitigations are implemented in this file: pinned SHAs, `zizmor`, read-all permissions, environment-scoped secrets with required reviewer, fork approval, no PR-code checkout in privileged jobs, attestations and SBOMs, Dependabot, CodeQL, Scorecard, `cargo-deny`.
