# Release runbook

This runbook takes a release from tag to published, and says how someone else takes over the project when the maintainer is away or gone. It is written to be followed literally: Gate G6 includes a dry run that follows this page step by step ([38 Maintenance and support](../prd/38-maintenance-and-support.md) §8).

The binding sources are [37 Releases and packaging](../prd/37-releases-and-packaging.md), [38](../prd/38-maintenance-and-support.md) §8 and the secrets inventory in [39 GitHub configuration](../prd/39-github-configuration.md) §5.

!!! note "Status"
    The release workflows (`release-plz.yml`, `release.yml`, `prerelease.yml`, `post-release.yml`) arrive with bootstrap tasks 24 to 26. Until they land, this page describes the process they implement, and steps 3 to 5 cannot be run yet.

## Cutting a release

1. **Check that the release is ready.**
    - For a `.0` release: the gate report is filed.
    - For a patch: the fix list is confirmed.
    - `main` is green.
    - release-plz opens the release pull request only for changes to the crates. A release of changes under `ui/`, `skills/` or `docs/` alone starts with a pull request that raises `[workspace.package] version` in `Cargo.toml` (D-081).
2. **Review the release pull request** (`chore(release): vX.Y.Z`, opened by release-plz).
    - Check the versions, the groups in `CHANGELOG.md`, `CITATION.cff` and the migration notes.
    - The release commit is authored by the `RELEASE_PLZ_TOKEN` user without a sign-off, so the `DCO` check fails on it. Open that check and choose **Set DCO to pass**, again after each update of the pull request (D-081).
    - Approve the gate. Auto-merge lands the pull request once the branch is up to date and the checks pass (`PR-PRQ-010`).
3. **Watch the publishing workflows.**
    - `release-plz.yml` creates the tag, using `RELEASE_PLZ_TOKEN` from the `automation` environment, and publishes the crates through crates.io trusted publishing, so no crates.io token is stored.
    - `release.yml` builds the draft release, and its `verify` job must pass.
4. **Edit the draft release notes** (Highlights, Known issues, Upgrade notes, Verify your download), then publish.
5. **Confirm that `post-release.yml` finished every step:**
    - the Homebrew tap pull request is merged;
    - the winget pull request is opened;
    - from v1.0, the Flathub checker pull request is opened;
    - `updates/stable.json` is live;
    - the Zenodo DOI is minted;
    - the announcement Discussion is posted.
6. **Install from each channel** on one machine, once that channel serves the new version (a winget or Flathub pull request has to merge and propagate first). Run the smoke journey, and file an issue for anything that is off.
7. **For a `.0` release only:**
    - create the next milestone and move the deferred items to it;
    - re-baseline the status line of the PRD.

### Rehearsing workflow changes

Every change to `release-plz.yml`, `release.yml`, `prerelease.yml` or `post-release.yml` is first run in the private companion repository `bioedca/tlilli-release-rehearsal`, with dummy keys and `dry_run=true`. It lands on `main` only after that run passes ([39](../prd/39-github-configuration.md) §6). The companion repository is disposable: it holds only copies of the workflows and dummy secrets.

## Handoff: the maintainer is unreachable

The backup admin covers ordinary unavailability ([38](../prd/38-maintenance-and-support.md) §8, `GOVERNANCE.md`). Before v1.0 the backup admin:

- is admin on the repository;
- is listed in `.github/CODEOWNERS`;
- is an allowed reviewer of the `release` environment;
- holds one of the two offline copies of the updater key.

### After one month without the maintainer

1. Set the repository Actions variable `HANDOFF_ACTIVE` to `true`. Only from then on does the gate check count the backup admin's approvals (`PR-REV-010`).
2. Open a pinned `type/task` issue that announces the handoff and its start date.
3. Triage issues and merge pull requests as the maintainer would.

### After six months: take over maintenance

The release tokens are personal access tokens on the maintainer's account. Nobody can revoke another account's tokens, so the backup admin replaces them. The maintainer's tokens then have no remaining use and expire at their yearly rotation date. In this order:

1. Make sure you are an admin collaborator on `bioedca/homebrew-tlilli`, `bioedca/tlilli-release-rehearsal` and the maintainer's `winget-pkgs` fork. This was granted when you were named, so the tokens you issue can reach those repositories.
2. From your own account, issue replacement tokens with the scopes in [39](../prd/39-github-configuration.md) §5:
    - `RELEASE_PLZ_TOKEN`, `PROJECT_TOKEN` and `HOMEBREW_TAP_TOKEN` are fine-grained tokens;
    - `WINGET_TOKEN` is a classic token with the single scope `public_repo` (D-061).
3. Replace each secret in the `automation` environment (`RELEASE_PLZ_TOKEN`, `PROJECT_TOKEN`) and in the `release` environment (`HOMEBREW_TAP_TOKEN`, `WINGET_TOKEN`).
    - `TAURI_SIGNING_PRIVATE_KEY` and its password are not tokens, and stay as they are.
4. Re-register the Codecov and Zenodo integrations under your account.
5. Record every change, with dates and expiry dates, in [the GitHub settings record](github-settings.md).
6. Release from this runbook.

### When the maintainer returns

1. The maintainer sets `HANDOFF_ACTIVE` back to `false` and closes the handoff issue. Both changes show in the settings audit log and in the issue.
2. The maintainer revokes their own old tokens.

## Death or permanent incapacity

This path is separate from the ordinary handoff above. It relies on the GitHub account successor that the maintainer designated (Settings → Account → Successor settings). Steps, in order ([38](../prd/38-maintenance-and-support.md) §8):

1. **The backup admin sets `HANDOFF_ACTIVE=true`** and keeps the project running while the successor process takes its weeks. The backup admin is already admin on every repository.
2. **The designated successor files GitHub's authorized request.** GitHub transfers the public repositories to them: `bioedca/Tlilli`, `bioedca/homebrew-tlilli` and the `winget-pkgs` fork.
3. **The private `bioedca/tlilli-release-rehearsal` cannot be transferred** and is treated as disposable. The new owner recreates it from `main`.
4. **The new owner rebuilds what is tied to an account:**
    - the `release` and `automation` environments and their secrets, from the inventory in [39](../prd/39-github-configuration.md) §5, with tokens from their own account;
    - the updater key, restored from the backup admin's sealed copy;
    - the GitHub Apps (CodeRabbit, Greptile, Codex, Codecov, DCO) and the crates.io trusted publisher re-authorized, and the Zenodo webhook re-registered;
    - GitHub Pages and the custom domain, re-pointed.
5. **The Homebrew, winget and Flathub manifests keep working**, because they reference the transferred repository.
6. **The new owner designates a new backup admin and a new successor**, and records everything in [the GitHub settings record](github-settings.md).
