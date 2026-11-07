# Develop in Codespaces or a dev container

For contributors and agents who need a Linux environment with a display. The `.devcontainer/` folder describes a container with Rust, Node 22, pnpm, the Tauri 2 Linux prerequisites, `xvfb` and a small desktop that you reach in the browser through noVNC, so you can run the checks from `CLAUDE.md` and see the Tauri window without setting up a laptop. GitHub Codespaces builds it in the cloud; the VS Code Dev Containers extension or the `devcontainer` CLI builds it on any machine with Docker.

## Before you start

- **Machine size.** `hostRequirements` asks for 4 CPUs, 8 GB of memory and 32 GB of storage. Codespaces therefore offers the **4-core, 16 GB RAM, 32 GB storage** machine as the smallest choice; a local Docker host needs the same. A 4-core Codespace uses 4 core-hours per hour, so the 180 core-hours a month of GitHub Pro are 45 hours of work ([39 GitHub configuration §6](../prd/39-github-configuration.md#6-github-pro-perks-and-platform-extras-in-use-d-044)). Stop the Codespace when you finish.
- **For Codespaces:** a GitHub account with Codespaces quota and write access to the repository, or a fork.
- **For a local dev container:** Docker, and either VS Code with the Dev Containers extension or the CLI (`npm install -g @devcontainers/cli`).

## Open the repository

### In Codespaces

1. On the repository page, choose **Code**, then **Codespaces**, then **Create codespace on main**. To pick another branch or a larger machine, choose **New with options** instead.
2. Wait for the first start to finish. The terminal shows `Running the postCreateCommand` while `.devcontainer/post-create.sh` installs the apt packages and, when `ui/` and `Cargo.lock` exist, the project's packages. The editor is usable before that ends; the commands below are not.
3. This page opens in the editor when the Codespace starts.

### In a local dev container

1. Clone the repository and open the folder.
2. In VS Code, run **Dev Containers: Reopen in Container**. With the CLI, run `devcontainer up --workspace-folder .` and then `devcontainer exec --workspace-folder . bash` for a shell inside the container. The CLI has no port forwarding, so the configuration also publishes the noVNC port on the loopback interface of the Docker host (`appPort`); the desktop is then at <http://127.0.0.1:6080> on that machine and nowhere else.
3. Wait for the post-create step as above.

## Run the checks

The commands are the ones `CLAUDE.md` lists. Run them from the repository root inside the container.

```sh
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
pnpm -C ui install --frozen-lockfile
pnpm -C ui build
pnpm -C ui test
pnpm -C ui tauri build --debug --no-bundle
xvfb-run -a pnpm -C ui test:e2e:desktop
```

`xvfb-run` gives the desktop smoke suite a virtual display independent of the desktop, the way the cloud sandbox and CI run it. The suite has `tauri-driver`, which the container installs, start the debug app that `tauri build --debug` writes.

## See the Tauri window

1. In a terminal inside the container, start the app: `pnpm -C ui tauri dev`. `DISPLAY` is `:1`, so the window opens on the container's desktop, not in the editor.
2. Open the **Ports** view (in Codespaces the **Ports** tab next to the terminal; in VS Code the command **Ports: Focus on Ports View**). With the CLI there is no Ports view: open <http://127.0.0.1:6080> in a browser on the Docker host and skip the next step.
3. In the row labelled **noVNC desktop** (port 6080), click the globe icon. A browser tab opens on the noVNC page.
4. Click **Connect** and enter the password `vscode`.
5. The desktop appears with the Tauri window. Right-click the desktop background for the window manager's menu.

The same desktop shows any other graphical program you start from a terminal in the container.

## Build without bundling

```sh
pnpm -C ui tauri build --no-bundle
```

This compiles the Tauri shell the way CI does, without producing installers. Installers (AppImage, msi, dmg) come from GitHub Actions, not from the container.

## Verify the environment

```sh
echo "$DISPLAY"                            # :1
rustc --version && cargo clippy --version  # the stable toolchain, as rust-toolchain.toml selects
node --version                             # v22.x
pnpm --version                             # 10.28.0, the version ui/package.json names
pkg-config --modversion webkit2gtk-4.1     # prints a version: the Tauri prerequisites are installed
command -v xvfb-run                        # /usr/bin/xvfb-run
command -v tauri-driver                    # ~/.cargo/bin/tauri-driver
```

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| Port 6080 is missing from the **Ports** view | Choose **Forward a Port** in that view and enter `6080`. |
| With the CLI, <http://127.0.0.1:6080> does not answer | `docker ps` should list `127.0.0.1:6080->6080/tcp` for the container. `appPort` takes effect when the container is created, so run `devcontainer up --workspace-folder . --remove-existing-container` after changing the configuration. |
| The noVNC page shows **Failed to connect to server** | The desktop starts with the container. Run **Codespaces: Rebuild Container** (or **Dev Containers: Rebuild Container**) and reconnect. |
| A graphical program reports `cannot open display` | Run `echo "$DISPLAY"`. If it is empty, run `export DISPLAY=:1` in that terminal or open a new terminal. |
| The first start printed errors from `post-create.sh` | Run `bash .devcontainer/post-create.sh` again in a terminal; the script is idempotent. |
| Playwright reports that its browsers are not installed | Run `pnpm -C ui exec playwright install --with-deps chromium`. The post-create step does this only when `ui/` exists at creation time. |
| The disk is full | Run `cargo clean` and delete `ui/node_modules`, or create the Codespace with the 8-core machine, which has 64 GB of storage. |
| The Tauri window or Chromium crashes in a local container | The configuration passes `--shm-size=1g` to Docker. Raise it in `runArgs` if the crashes continue. |

The configuration itself is `.devcontainer/devcontainer.json`; each setting carries a comment that says why it is there.
