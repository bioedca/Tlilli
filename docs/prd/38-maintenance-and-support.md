# 38 · Maintenance and support

Covers the post-release life of every version from v0.1 and the long-term policy from v1.0: what is supported, for how long, how fixes flow, how security is handled, how formats and protocols evolve, and how the project survives its single maintainer.

## 1. Support matrix (PR-MNT-001 … 006)

| ID | Rule |
| --- | --- |
| `PR-MNT-001` | **0.x:** only the latest 0.x release is supported; fixes ship as the next patch or minor; no backports. |
| `PR-MNT-002` | **From v1.0:** the latest minor receives all fixes. **Security fixes** are backported to the previous minor for **90 days** after the newer minor's release (the only reason a `release/<major>.<minor>` branch exists, `PR-GIT-009`). Nothing older is supported. |
| `PR-MNT-003` | **OS floor:** macOS 13+, Windows 10 22H2+ and 11, Ubuntu 22.04+ (glibc 2.35+) and equivalent distros; raised only in a minor with a changelog entry and a one-minor warning in the app ("your OS will stop receiving updates after 1.x"). |
| `PR-MNT-004` | **Agents:** Claude Code and Codex CLI current stable releases are supported; ChatGPT per the plan matrix documented at v0.5; other MCP clients are "should work" with the contract tests as the reference. |
| `PR-MNT-005` | **Workspace formats:** every schema version ever released opens and migrates forward (`NFR-COMPAT-001`); migrations from versions older than two majors may be dropped with a documented migration tool. |
| `PR-MNT-006` | **Support channels:** Discussions Q&A for questions; issues for bugs and requests; no email or chat support. `SUPPORT.md` states this and how to produce diagnostics. |

## 2. Response targets (not SLAs; a solo maintainer's honest commitments)

| Item | Target |
| --- | --- |
| New issue triaged (labels, priority, milestone) | within 7 days (weekly triage) |
| Security report acknowledged | within 7 days (`PR-SEC-001`) |
| `priority/P0` (data loss, invariant violation, security high) | fix PR within 7 days of confirmation; patch release on merge |
| `priority/P1` | fixed within the current phase/minor |
| `priority/P2`, `P3` | best effort; re-evaluated at each gate |
| Gate decisions on PRs | within 48 h (metric in [32](32-code-review.md) §7) |

## 3. Security response (summary of [22](22-security-and-threat-model.md) §4)

Private vulnerability reporting → triage → fix on `main` → patch release → backport within the 90-day window → GitHub Security Advisory with CVE → public `type/security` follow-up issue. The threat register is re-reviewed at each gate and when a trust boundary changes.

## 4. Dependency hygiene (PR-MNT-010 … 014)

| ID | Rule |
| --- | --- |
| `PR-MNT-010` | Dependabot grouped weekly PRs for `cargo` (the root workspace; `fuzz/`, its own Cargo workspace, gets no version updates), `npm`, `github-actions`, `pip` (docs) and `devcontainers`, proposing only releases at least 7 days old (cooldown); the patch and minor group auto-merges after CI only for entries that PR CI builds and tests (cargo `/`, npm `/ui`; pip `/docs` once a required check builds the docs); majors and the other entries wait for triage; security advisories open ungrouped PRs immediately, without the cooldown, and these never auto-merge (D-074). |
| `PR-MNT-011` | `cargo deny check advisories` blocks PRs and runs nightly on `main`; a new advisory on `main` opens a `priority/P1` issue automatically. |
| `PR-MNT-012` | Unmaintained dependencies (no release in 18 months, open critical issues) are listed quarterly; replacement or fork decisions go through an ADR (`PR-ARCH-002`). |
| `PR-MNT-013` | Toolchain: MSRV bumps to the current stable at each minor; `rust-toolchain.toml` pins `stable`; CI also compiles on `beta` nightly as an early warning (not required). |
| `PR-MNT-014` | Runner images and pinned actions reviewed quarterly (`PR-CI-002`). |

## 5. Protocol, skill and format evolution (PR-MNT-020 … 024)

| ID | Rule |
| --- | --- |
| `PR-MNT-020` | **MCP:** tools and resources are added or extended additively within a major; a deprecated tool stays for at least one minor, is marked `deprecated` in its description and the docs, logs a warning server-side, and is listed under "Deprecated" in the changelog; removal is a breaking change. |
| `PR-MNT-021` | **Skills:** behaviour changes to skills are `type/skill` issues (gated); each release ships the matching skill pack; `tlilli skills install --check` surfaces drift to users. |
| `PR-MNT-022` | **Canonical JSON and style-sheet schemas:** versioned; new fields optional; readers ignore unknown fields; removals are major. |
| `PR-MNT-023` | **Workspace schema:** migrations numbered, forward-only, backed up before running (`NFR-REL-003`), tested against fixture databases from every released version. |
| `PR-MNT-024` | **CLI:** flags are never repurposed; removed flags print a pointer to the replacement for one minor. |

## 6. Diagnostics and user-reported problems

- Local structured logs, crash files and the redacted "Copy diagnostics" bundle (`NFR-OBS-001..004`, `NFR-PRIV-003`); nothing is sent automatically, ever (D-033).
- The bug form asks for the bundle and the app's "Report a bug" opens the form with version and OS prefilled.
- Reproductions use fixture manuscripts where possible; a user's manuscript is never requested, only a canonical export the user has redacted, and only through a private channel they choose.

## 7. Deprecation and end of life

- 0.x releases reach end of life when the next 0.x ships (`PR-MNT-001`).
- A major version reaches end of life 90 days after the next major's `.0` release for security fixes and immediately for other fixes; the download page marks EOL versions.
- Features are removed only after a deprecation cycle and with an upgrade note; data formats are never removed without a migration path.

## 8. Continuity (bus factor)

| Item | Mitigation |
| --- | --- |
| Single maintainer | `GOVERNANCE.md` names two controls. **Backup admin** (ordinary unavailability): before v1.0 a trusted collaborator is given admin rights on the repository, is listed in `.github/CODEOWNERS`, is added as an allowed reviewer of the `release` environment, holds one of the two offline copies of the updater key, and holds no day-to-day role. **Handoff state:** the gate check honours the backup admin's approvals only while the repository Actions variable `HANDOFF_ACTIVE` is `true` (`PR-REV-010`). If the maintainer is unreachable for 1 month, the backup admin sets the variable to `true`, opens a pinned `type/task` issue announcing the handoff and its start date, and triages and merges; after 6 months they assume maintenance under this PRD: install their own tokens (Secrets row) and release from the runbook. The maintainer, on return, sets the variable back to `false` and closes the issue; both changes are visible in the settings audit log and the issue. **Account successor** (death or permanent incapacity): the maintainer designates a GitHub account successor (Settings → Account → Successor settings); GitHub transfers the public repositories to them on an authorized request. The successor control does not cover temporary absence, which is why the backup admin exists; the Death or incapacity row gives the full sequence. |
| Secrets | Inventory in [39](39-github-configuration.md) §5; updater key custody per `PR-REL-034` (two offline copies: maintainer and backup admin). The release and automation tokens are PATs on the maintainer's account, rotated yearly (a GitHub App if a second maintainer joins): `RELEASE_PLZ_TOKEN`, `PROJECT_TOKEN` and `HOMEBREW_TAP_TOKEN` are fine-grained; `WINGET_TOKEN` is a classic PAT with the single scope `public_repo`, because `winget-releaser` opens pull requests on `microsoft/winget-pkgs`, which the maintainer does not own, and fine-grained PATs cannot do that (D-061). **Handoff:** the backup admin, as repository admin and `release` environment reviewer, and as an admin collaborator on `bioedca/homebrew-tlilli`, `bioedca/tlilli-release-rehearsal` and the maintainer's `winget-pkgs` fork (granted when they are named, so the tokens they issue can reach those repositories), **replaces** each secret in the `automation` and `release` environments with a token issued from their own account, re-registers the Codecov and Zenodo integrations under their account, and records the change in `docs/dev/github-settings.md`. Nobody can revoke another account's PATs: the maintainer's tokens simply have no remaining use once replaced, expire at their yearly rotation date, and are revoked by the maintainer on return (or disappear with the account in the death path). The runbook's handoff section lists these steps in order. |
| Death or incapacity | Ordered runbook, separate from the ordinary-absence path: (1) the backup admin, already admin on every repository, sets `HANDOFF_ACTIVE=true` and keeps the project running while the successor process takes its weeks; (2) the designated successor files GitHub's authorized request; GitHub transfers the **public** repositories (`bioedca/Tlilli`, `bioedca/homebrew-tlilli`, the `winget-pkgs` fork) to them; (3) the private `bioedca/tlilli-release-rehearsal` repository is not transferable and is treated as disposable: it holds only workflow copies and dummy secrets and is recreated under the new owner from `main`; (4) the new owner recreates the `release` and `automation` environments and their secrets from the inventory in [39](39-github-configuration.md) §5 with tokens from their own account, restores the updater key from the backup admin's sealed copy, re-authorizes the GitHub Apps (CodeRabbit, Greptile, Codex, Codecov, DCO, Zenodo) and the crates.io trusted publisher, and re-points Pages and the custom domain; (5) Homebrew, winget and Flathub manifests keep working because they reference the transferred repository; (6) the new owner designates a new backup admin and successor and records everything in `docs/dev/github-settings.md`. |
| Knowledge | This PRD, the ADRs, the release runbook and the agent playbook are sufficient for a new maintainer to cut a release in one day; G6 includes a dry run by following the runbook literally. |
| Infrastructure | Everything is in the repository or GitHub settings exported to `docs/dev/github-settings.md` (rulesets as JSON, label file, app list); no personal machines hold unique state except the offline key copies. |

## 9. Maintenance cadence after v1.0

- Minor releases roughly every two months when features are ready; patches on demand.
- Weekly triage continues; monthly metrics; quarterly retune; yearly: key restore drill, secret rotation, PRD and threat-register review, dependency and license audit.
