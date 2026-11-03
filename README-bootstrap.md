# Tlilli repo bootstrap

Unpack at the repository root. Files and what they do:

| File | Purpose |
| --- | --- |
| `CLAUDE.md` | Project instructions Claude Code loads in every session (local and cloud) |
| `.claude/settings.json` | SessionStart hook that runs `scripts/install_pkgs.sh`; permission allow-list for the build tools |
| `scripts/install_pkgs.sh` | Cloud-only dependency install, skipped when lockfiles are unchanged |
| `.mcp.json` | Registers `tlilli-mcp` over stdio so the session can dogfood the server. Until the crate exists, Claude Code reports the server as failed to connect and carries on; add the file at v0.2 if the noise bothers you |
| `.cargo/config.toml` | git fetches via system git; smaller dev debug info |
| `rust-toolchain.toml` | stable toolchain with rustfmt and clippy |
| `.github/workflows/ci.yml` | fmt, clippy, tests, UI build on Ubuntu 24.04 with Tauri prerequisites. Adjust paths once the workspace layout is real |
| `.gitignore` | Rust, Node, Tauri, local caches and workspaces |

The cloud environment itself (network access, variables, secrets, setup script) is configured in the
claude.ai/code environment dialog, not in the repo. See the "Tlilli — Cloud environment setup" doc.
