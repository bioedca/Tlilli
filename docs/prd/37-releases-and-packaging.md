# 37 · Releases and packaging

INTERSECT Packaging rules adopted: one version source; SemVer as an abbreviated changelog with deprecation cycles; Keep a Changelog; publish from CI on a `vX.Y.Z` tag through a GitHub Release; rehearse publishing on a test target first; Zenodo DOI and `CITATION.cff`; validate artifacts before upload.

## 1. Versioning (PR-REL-001 … 008)

| ID | Rule |
| --- | --- |
| `PR-REL-001` | SemVer 2.0. During 0.x each roadmap phase is a minor (`v0.1.0` … `v0.5.0`); patches (`v0.3.1`) fix gate findings and bugs; pre-releases `v0.X.0-beta.N` feed the beta channel. `v1.0.0` is the public release. After 1.0: minors add features (breaking changes only in majors with a deprecation cycle of at least one minor); patches fix. |
| `PR-REL-002` | **One version source:** `[workspace.package] version` in the root `Cargo.toml`; every crate uses `version.workspace = true`; `src-tauri/tauri.conf.json` omits `version` so Tauri reads the shell crate's Cargo version; `ui/package.json` is `private: true` and carries no meaningful version. `CITATION.cff` `version` is updated in the release PR by a script. |
| `PR-REL-003` | Breaking changes are declared in commits (`!`, `BREAKING CHANGE:` footer), labelled `breaking-change` on the PR, documented under "Upgrade notes", and in 0.x may occur in minors; the workspace schema and canonical JSON schema versions bump with them. |
| `PR-REL-004` | Deprecations: a tool, resource, flag or format is marked deprecated (tool description, docs, changelog) for at least one minor before removal; the app logs a warning when a deprecated path is used. |
| `PR-REL-005` | Rust API of `tlilli-core`: `cargo-semver-checks` runs in the release PR from v1.0 and blocks an incorrect bump. |
| `PR-REL-006` | Tags are annotated `v<version>`, created only by release-plz (stable) or `prerelease.yml` (beta) under the release token; the tag ruleset forbids update and deletion (`PR-GIT-030`). |
| `PR-REL-007` | Skill pack version = app version; `tlilli skills install --check` reports mismatches (`NFR-COMPAT-004`). |
| `PR-REL-008` | MSRV bumps are minor-level changes noted in the changelog (`rust-version`). |

## 2. Release flow (stable)

```
commits on main ──▶ release-plz keeps "chore(release): vX.Y.Z" PR updated (versions, CHANGELOG, CITATION.cff)
                ──▶ maintainer approves (gate) ──▶ auto-merge lands it once the branch is up to date and checks pass
                ──▶ release-plz creates tag vX.Y.Z, publishes crates (trusted publishing)
                ──▶ release.yml: build matrix → DRAFT GitHub Release (bundles, latest.json, .sig)
                                  + SBOM + SHA256SUMS + attestations + verify job
                ──▶ maintainer edits notes, clicks Publish (last manual gate)
                ──▶ post-release.yml: Homebrew, winget, Flathub, updates/stable.json, Zenodo, announcement
```

**release-plz configuration (`release-plz.toml`, gated):**

```toml
[workspace]
changelog_update = true
changelog_config = "cliff.toml"          # Keep a Changelog groups mapped from commit types
git_release_enable = false               # tauri-action creates the GitHub Release
git_tag_enable = true
git_tag_name = "v{{ version }}"          # one tag for the whole workspace
pr_name = "chore(release): v{{ version }}"
pr_labels = ["release", "gate"]
pr_draft = false
semver_check = false                     # true for tlilli-core from v1.0
dependencies_update = false              # Dependabot owns dependency bumps
publish_timeout = "20m"
release_always = false                   # release only when the release PR merges

[[package]]
name = "tlilli-core"
version_group = "tlilli"
publish = true

[[package]]
name = "tlilli-mcp"
version_group = "tlilli"
publish = false  # until v0.2 (PR-REL-024)

[[package]]
name = "tlilli-cli"
version_group = "tlilli"
publish = false  # until v0.2 (PR-REL-024)

[[package]]
name = "tlilli-app"       # src-tauri
version_group = "tlilli"
publish = false

[[package]]
name = "tlilli-fuzz"
release = false
```

`tlilli-mcp` and `tlilli-cli` publish from v0.2 (`PR-REL-024`). Until then their manifests carry `publish = false` and the entries above match; one gated PR removes both flags before the v0.2 release PR is cut, because release-plz builds the release PR from `main` (ADR-0001, D-077).

`cliff.toml` maps commit types to Keep a Changelog headings ([35](35-documentation.md) `PR-DOC-010`), links issues and PRs, and omits `ci`, `chore(deps)`, `docs` from the user-facing changelog while keeping them in the GitHub release "Full changelog" link.

**`release.yml` jobs**

| Job | Runner | Does |
| --- | --- | --- |
| `build` (matrix) | `macos-15` ×2 targets, `windows-2025`, `ubuntu-24.04` | `tauri-apps/tauri-action` with `tagName: v__VERSION__`, `releaseName: Tlilli v__VERSION__`, `releaseDraft: true`, `prerelease: false`, `uploadUpdaterJson: true`, `releaseAssetNamePattern: tlilli-[version]-[platform]-[arch].[ext]`, `args: --target <t>`; env `TAURI_SIGNING_PRIVATE_KEY`, `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` from environment `release`; `retryAttempts: 2` |
| `sbom` | `ubuntu-24.04` | `anchore/sbom-action` on the workspace (Cargo + npm) → `sbom.spdx.json` attached to the draft release |
| `checksums` | `ubuntu-24.04` | download all assets, write `SHA256SUMS`, attach |
| `attest` | `ubuntu-24.04` (`id-token: write`, `attestations: write`) | `actions/attest` build provenance for every asset and the SBOM (Sigstore public-good; SLSA Build L2; L3 when moved to a reusable workflow) |
| `verify` | `ubuntu-24.04` | `gh release download`, `sha256sum -c SHA256SUMS`, `gh attestation verify <asset> --repo bioedca/Tlilli` for each asset, size assertions (`NFR-PERF-010`), `latest.json` schema check; fails the run (release stays draft) on any error |

**Beta channel (`prerelease.yml`):** `workflow_dispatch` with `version` input (`0.4.0-beta.2`); builds `main` HEAD with `tauri build --config '{"version":"0.4.0-beta.2"}'` (overrides the app version without touching Cargo), tags `v0.4.0-beta.2` on that commit, creates a **prerelease** draft, same sbom/checksums/attest/verify jobs; `post-release.yml` updates `updates/beta.json` only. Beta builds are never promoted; the stable release is always rebuilt from the release PR.

## 3. Artifacts (per release)

| Platform | Files | Updater artifact |
| --- | --- | --- |
| macOS arm64 / x86_64 | `tlilli-<v>-macos-aarch64.dmg`, `tlilli-<v>-macos-x86_64.dmg` | `tlilli-<v>-macos-<arch>.app.tar.gz` + `.sig` |
| Windows x86_64 | `tlilli-<v>-windows-x86_64.msi`, `tlilli-<v>-windows-x86_64-setup.exe` (NSIS) | the same files + `.sig` |
| Linux x86_64 | `tlilli-<v>-linux-x86_64.AppImage`, `.deb`, `.rpm` | AppImage + `.sig` (deb/rpm are not updatable by the updater; documented) |
| All | `SHA256SUMS`, `sbom.spdx.json`, `latest.json`, attestations (in the Sigstore log, verified with `gh attestation verify`), source archives (GitHub) | — |

Linux arm64 is built as `experimental` (not required, not gate-tested) from v0.4.

## 4. Trust posture with zero signing budget (D-026)

No Apple Developer ID, no notarization, no Windows Authenticode certificate can be afforded. The project therefore:

1. **Signs updates** with the Tauri updater's minisign key (free; `cargo tauri signer generate -w ~/.tauri/tlilli.key`; public key in `tauri.conf.json`; private key only in the `release` environment, the maintainer's password manager, and the sealed offline copy held by the backup admin once named, T-09).
2. **Attests provenance** of every asset with GitHub artifact attestations (free for public repos; Sigstore public-good; transparency log). Users verify with `gh attestation verify tlilli-<v>-<platform>.<ext> --repo bioedca/Tlilli`.
3. **Publishes checksums** (`SHA256SUMS`) and shows them on the download page.
4. **Documents the OS prompts honestly:** macOS Gatekeeper ("App is damaged / cannot be opened": right-click → Open, or `xattr -dr com.apple.quarantine /Applications/Tlilli.app`); Windows SmartScreen ("More info → Run anyway"); Linux AppImage `chmod +x`. The app never tells users to disable security settings globally.
5. **Reduces random downloads** by publishing through package channels (Homebrew, winget, Flathub) that point at the GitHub Release.
6. **Keeps the door open:** SignPath Foundation offers free Windows code signing to qualifying open-source projects; applying is a v1.0 `Could` item with no budget assumption. Apple notarization becomes a line item if GitHub Sponsors income covers USD 99/year. Both are recorded as optional in the decision log, not planned.

## 5. Distribution channels (PR-REL-020 … 026)

| ID | Channel | Rule |
| --- | --- | --- |
| `PR-REL-020` | GitHub Releases | Canonical. Every other channel points here. Draft → maintainer publish. Release notes per `PR-DOC-011`. |
| `PR-REL-021` | Homebrew | Own tap `bioedca/homebrew-tlilli` (used as `brew tap bioedca/tlilli`), cask `tlilli` (unsigned app: cask includes the `--no-quarantine` note in caveats); `post-release.yml` opens a bump PR in the tap with new version and sha256; the tap repo has its own minimal CI (`brew audit --cask`). |
| `PR-REL-022` | winget | Manifest `Tlilli.Tlilli` in `microsoft/winget-pkgs` via `vedantmgoyal9/winget-releaser` from `post-release.yml` (installer URLs + hashes for `.msi`); unsigned installers are accepted; SmartScreen note in docs. |
| `PR-REL-023` | Flathub | App id `io.github.bioedca.Tlilli` (Flathub's convention for GitHub-hosted projects without a verified domain; changes to a domain-based id only after D-035 and a Flathub rename request); manifest in the Flathub repo built from the release source tarball (Rust and Node offline sources generated with `flatpak-cargo-generator` and `flatpak-node-generator`); updates by Flathub's external-data-checker PRs, reviewed by the maintainer. Added at v1.0. |
| `PR-REL-024` | crates.io | `tlilli-core`, `tlilli-mcp`, `tlilli-cli` published by release-plz with trusted publishing (OIDC, `rust-lang/crates-io-auth-action`); `cargo install tlilli-mcp` / `tlilli-cli`; `cargo binstall` metadata points at the GitHub Release binaries for `tlilli-mcp` and `tlilli`. From v0.2 (mcp, cli) and v0.1 (core). |
| `PR-REL-025` | Docs site | `updates/stable.json` and `updates/beta.json` (updater endpoints) and the download page with checksums and verify instructions, updated by `post-release.yml`. |
| `PR-REL-026` | Not maintained by the project | AUR, Chocolatey, Scoop, Nix: community-maintained if at all; README lists them as unofficial. |

## 6. Updater (PR-REL-030 … 034)

| ID | Rule |
| --- | --- |
| `PR-REL-030` | `tauri-plugin-updater` with `bundle.createUpdaterArtifacts: true`; endpoints `https://<site>/updates/stable.json` (default) and `beta.json` (opt-in); `windows.installMode: passive`; capability `updater:default`. |
| `PR-REL-031` | Check on launch is **opt-in** (default off); manual "Check for updates" always available; the request carries only target, arch and current version (`NFR-PRIV-002`). |
| `PR-REL-032` | Release notes are shown before install; install is one click; the app relaunches; Linux deb/rpm users are told to use their package manager. |
| `PR-REL-033` | The manifests are generated from tauri-action's `latest.json` by `post-release.yml` and validated (every platform entry complete; signature present) before upload, because Tauri rejects the whole file on one malformed entry. |
| `PR-REL-034` | Key custody: generated offline by the maintainer; stored in a password manager and a sealed offline copy held by the backup admin once named; passphrase separate; the GitHub secret is the only online copy; a yearly restore drill is a `type/task` issue (T-09). |

## 7. Release runbook (`docs/dev/release-runbook.md`, summary)

1. Confirm the gate report (for `.0` releases) or the fix list (for patches) and that `main` is green.
2. Review the release PR: versions, `CHANGELOG.md` groups, `CITATION.cff`, migration notes; approve the gate; auto-merge lands it once the branch is up to date and the checks pass.
3. Watch `release-plz.yml` create the tag and publish crates; watch `release.yml` produce the draft and pass `verify`.
4. Edit the draft notes (Highlights, Known issues, Upgrade notes, Verify your download); publish.
5. Confirm `post-release.yml`: tap PR merged, winget PR opened, Flathub checker PR (v1.0+), `updates/stable.json` live, Zenodo DOI minted, announcement Discussion posted.
6. Install from each channel on one machine; run the smoke journey; file issues for anything off.
7. For `.0` releases: create the next milestone, move deferred items, re-baseline the PRD status line.

Rehearsal: every change to `release-plz.yml`, `release.yml`, `prerelease.yml` or `post-release.yml` is first run in the private companion repository with dummy keys and `dry_run=true` ([39](39-github-configuration.md) §6).

## 8. Citation and archiving

- Zenodo GitHub integration archives every published release; the concept DOI is in `CITATION.cff` and README; versioned DOIs appear in release notes.
- `CITATION.cff` is validated in CI (`cffconvert --validate`) and its `version`/`date-released` updated by the release PR script.
- A JOSS submission is a post-1.0 `Could` item (requires OSI license, docs, tests: all satisfied by this PRD).
