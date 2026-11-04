# Governance

## Model

Tlilli has one maintainer, bioedca, who holds the merge rights and makes the decisions, and AI coding agents (Claude Code, Codex) that do most of the implementation and review work under the rules in the [product requirements document](docs/prd/README.md) (PRD). Human review is reserved for the gated paths listed in [PRD 32 §3](docs/prd/32-code-review.md); everything else merges on automated evidence. This is the model through v1.0 (D-001), and the repository stays on the maintainer's personal account (D-057).

## How decisions are made

- The PRD is the single tracking source. Anything the project does differently is recorded as a dated entry in the [decision log](docs/prd/41-risks-and-decision-log.md) before or with the change, and the PRD text is updated in the same pull request.
- Architecture decisions are ADRs under `docs/adr/` (MADR format), gated, and immutable once accepted.
- Phases end at gates: a phase closes when its test passes on a real manuscript on the tagged release build ([PRD 40](docs/prd/40-roadmap-and-gates.md)), not when its features are merged.
- Proposals arrive as issues (feature, protocol-change or skill-change forms) and are decided at the weekly triage or at a gate; the maintainer records the reasoning in the issue or in the decision log.
- `docs/prd/**`, `docs/adr/**`, `docs/gates/**`, the licenses and the public root files are gated paths: changing the rules is a maintainer decision.

## Roles

| Role | Who | Rights | How you get there |
| --- | --- | --- | --- |
| Contributor | Anyone who opens an issue or a pull request | Fork, branch, PR; the same automated review as everyone else | Follow [CONTRIBUTING.md](CONTRIBUTING.md) |
| Committer | Nobody yet | Branches in the repository; triage labels | Sustained contributions after v1.0; invited by the maintainer and recorded in the decision log |
| Maintainer | bioedca | Merge rights, gate approvals, releases, settings, secrets | Invitation by the current maintainer, recorded in the decision log. A second maintainer retires the `gate:approved` mechanism in favour of code-owner reviews (`PR-REV-015`) |
| Backup admin | Not yet named (before v1.0) | Repository admin, used only during a handoff; see Continuity | Named by the maintainer and recorded in `docs/dev/github-settings.md` |

The ladder is dormant until a second human is needed.

## Continuity

Two controls cover the single-maintainer risk (R-18, T-15; [PRD 38 §8](docs/prd/38-maintenance-and-support.md)).

**Backup admin, for ordinary unavailability.** Before v1.0 the maintainer gives a trusted collaborator admin rights on the repository, lists them in `.github/CODEOWNERS`, adds them as an allowed reviewer of the `release` environment and hands them one of the two sealed offline copies of the updater signing key. They hold no day-to-day role, and their gate approvals count only while the repository Actions variable `HANDOFF_ACTIVE` is `true`.

- If the maintainer is unreachable for **1 month**, the backup admin sets `HANDOFF_ACTIVE` to `true`, opens a pinned `type/task` issue announcing the handoff and its start date, and triages and merges.
- After **6 months** they assume maintenance under the PRD: they replace each secret in the `automation` and `release` environments with a token issued from their own account (nobody can revoke another account's tokens; the maintainer's expire at their yearly rotation), re-register the Codecov and Zenodo integrations under their account, record the change in `docs/dev/github-settings.md`, and release from the runbook.
- On return, the maintainer sets the variable back to `false` and closes the issue. Both changes are visible in the settings audit log and in the issue.

**Account successor, for death or permanent incapacity.** The maintainer designates a GitHub account successor (Settings, Account, Successor settings). On an authorized request GitHub transfers the public repositories (`bioedca/Tlilli`, `bioedca/homebrew-tlilli`, the `winget-pkgs` fork) to the successor. A successor cannot log in or act during a temporary absence, which is why the backup admin exists. The runbook, in order: (1) the backup admin sets `HANDOFF_ACTIVE` to `true` and keeps the project running while the successor process takes its weeks; (2) the successor files GitHub's request and receives the public repositories; (3) the private rehearsal repository is disposable and is recreated from `main`; (4) the new owner recreates the `release` and `automation` environments and their secrets from the inventory in [PRD 39 §5](docs/prd/39-github-configuration.md) with tokens from their own account, restores the updater key from the backup admin's sealed copy, re-authorizes the GitHub Apps and the crates.io trusted publisher, and re-points Pages and the custom domain; (5) Homebrew, winget and Flathub manifests keep working because they reference the transferred repository; (6) the new owner names a new backup admin and successor and records everything in `docs/dev/github-settings.md`.

Status on 2026-11-04: neither a backup admin nor an account successor is named yet; Gate G6 (v1.0) requires both, and the same person may hold both roles.

## Secrets and recovery

- No secret lives in the repository or in environment variables. Release secrets live in two GitHub Actions environments: `release` (signing key and packaging tokens, with a required reviewer) and `automation` (release and project tokens, `main` only). The inventory, with scopes and expiry dates and never values, is in [`docs/dev/github-settings.md`](docs/dev/github-settings.md).
- The updater signing key was generated offline. The private key and its passphrase are separate password-manager entries; one sealed offline copy is held by the maintainer until the backup admin is named; the `release` environment secret is the only online copy; a yearly restore drill is tracked as an issue. Loss of the key means no further updates reach installed apps (T-09); theft means rotation under the runbook and an advisory (T-10).
- Tokens are personal access tokens of the maintainer, rotated yearly; a GitHub App replaces them if a second maintainer joins.
- Everything else the project needs is in the repository or exported to `docs/dev/github-settings.md`; no personal machine holds unique state except the offline key copies. The PRD, the ADRs, the release runbook and the agent playbook are meant to let a new maintainer cut a release in one day, and Gate G6 includes that dry run.
