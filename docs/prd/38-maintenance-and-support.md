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
| `PR-MNT-010` | Dependabot grouped weekly PRs for `cargo`, `npm`, `github-actions`, `pip` (docs); patch and minor groups auto-merge after CI; majors wait for triage; security advisories open ungrouped PRs immediately. |
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
| Single maintainer | `GOVERNANCE.md` names a succession plan: if the maintainer is unresponsive for 6 months, a named backup owner (to be designated before v1.0) may assume org ownership; the organization has two owners from v1.0 (the second is a trusted account that holds no day-to-day role). |
| Secrets | Inventory in [39](39-github-configuration.md) §5; updater key custody per `PR-REL-034`; release token is a fine-grained PAT or GitHub App owned by the organization, rotated yearly. |
| Knowledge | This PRD, the ADRs, the release runbook and the agent playbook are sufficient for a new maintainer to cut a release in one day; G6 includes a dry run by following the runbook literally. |
| Infrastructure | Everything is in the repository or GitHub settings exported to `docs/dev/github-settings.md` (rulesets as JSON, label file, app list); no personal machines hold unique state except the offline key copies. |

## 9. Maintenance cadence after v1.0

- Minor releases roughly every two months when features are ready; patches on demand.
- Weekly triage continues; monthly metrics; quarterly retune; yearly: key restore drill, secret rotation, PRD and threat-register review, dependency and license audit.
