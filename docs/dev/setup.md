# Setup

This page covers the tools Tlilli needs on a laptop running Linux, macOS or Windows, notes for the cloud sandbox that agent sessions use, and where to find Codespaces. The workflow itself is in [`CONTRIBUTING.md`](https://github.com/bioedca/Tlilli/blob/main/CONTRIBUTING.md) and [30 Git workflow](../prd/30-git-workflow.md) §5.

Clone your own copy. Never share a clone or work in a folder that a sync service mirrors.

## Every platform

| Tool | Version | Notes |
| --- | --- | --- |
| Rust, through [rustup](https://rustup.rs/) | stable, at least the MSRV in `Cargo.toml` (`rust-version`) | `rust-toolchain.toml` selects stable with `rustfmt` and `clippy`, so rustup installs them on first use |
| `cargo-nextest` | the version in `ci.yml` | `cargo install cargo-nextest --locked`; runs the tests in `scripts/ci.sh rust-test` |
| `cargo-deny` | the version in `ci.yml` | `cargo install cargo-deny --locked`; runs the dependency checks in `scripts/ci.sh rust-lint` |
| Node.js | 22 | |
| pnpm | the version in `ui/package.json` (`packageManager`) | `corepack enable` provides it |
| Python | 3 | for `scripts/docs.sh`, which builds its hash-pinned toolchain in `.cache/`, and for `scripts/gen_fixtures.py` and the scripts' tests |
| Git | any recent | commit with `git commit -s` (DCO, `PR-GIT-023`) |

Then, from the repository root:

```bash
pnpm -C ui install --frozen-lockfile
```

This installs the UI packages and the lefthook git hooks. On commit, when Rust files are staged, rustfmt and clippy check the whole workspace; Biome checks only the staged UI files; commitlint checks the message. CI runs rustfmt, clippy and Biome in full; commitlint joins CI with the `commits` job (bootstrap task 20). `scripts/ci.sh all` runs the CI jobs locally ([Running CI locally](ci.md)).

## Linux (Ubuntu 24.04)

Install the Tauri 2 prerequisites. This is the list in `.devcontainer/post-create.sh`; `ci.yml` installs the same packages except `pkg-config`, which the runner image already has:

```bash
sudo apt-get install -y libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev pkg-config
```

For the desktop end-to-end tests (the `tauri-driver` smoke suite, whose `ui` script has not landed yet), also install `xvfb` and `webkit2gtk-driver`, and run them under a virtual display with `xvfb-run -a`. The browser suite, `pnpm -C ui test:e2e`, runs headless and needs neither.

## macOS

Install the Xcode Command Line Tools with `xcode-select --install`. Tauri uses the system WebKit, so the build needs nothing else.

`scripts/docs.sh`, and with it `scripts/ci.sh docs-build`, calls `sha256sum`. If `command -v sha256sum` finds nothing, install GNU coreutils with Homebrew (`brew install coreutils`), which provides it.

## Windows

Install the Microsoft C++ Build Tools with the "Desktop development with C++" workload. Tauri uses WebView2, which Windows 10 (version 1803 and later) and Windows 11 already include.

## Cloud sandbox (agent sessions)

Claude Code cloud sessions run on Ubuntu 24.04 with no display. `CLAUDE.md` holds the notes that agents read; in short:

- At session start, `scripts/install_pkgs.sh` installs the UI packages and fetches the crates. It skips the work when the lockfiles, `ui/package.json` and the script itself have not changed since the last successful run. When `cargo-nextest` is missing, the script builds it in the background, with the output in `.cache/cargo-nextest.log`.
- Use `pnpm -C ui tauri build --no-bundle` for the Tauri compile check, and `xvfb-run -a` for WebDriver tests. Do not start `tauri dev`.
- Playwright cannot download browsers there. Point the browser tests at the preinstalled Chromium:

    ```bash
    TLILLI_PW_CHROMIUM=/opt/pw-browsers/chromium pnpm -C ui test:e2e
    ```

- From the shell, GitHub is reached through REST (`gh api`), because `gh pr` and `gh issue` need GraphQL and are refused. The GitHub MCP tools cover the GraphQL operations, such as marking a pull request Ready. The [agent playbook](agent-playbook.md) lists the routes.

## Codespaces and dev containers

`.devcontainer/` sets up all of the above in a container, with a browser view of the Tauri window. See [Develop in Codespaces or a dev container](../how-to/codespaces.md).
