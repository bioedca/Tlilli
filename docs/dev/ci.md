# Running CI locally

`scripts/ci.sh` runs the commands of the CI jobs on your machine and stops at the first failure (`PR-CI-010`). Run it before you push, or before marking a pull request Ready. The jobs and their gates are defined in [33 CI/CD](../prd/33-ci-cd.md) §2; `scripts/ci.sh --help` prints the current list.

```bash
scripts/ci.sh all          # the CI jobs in CI order, then scripts; reuse only when named
scripts/ci.sh rust-test    # one job
scripts/ci.sh rust ui      # several jobs, in the order given
```

The script installs no toolchain: it expects rustup, cargo-nextest, cargo-deny, pnpm, Node 22 and Python 3 on `PATH` ([Setup](setup.md)). A Rust or UI job is skipped when `Cargo.toml` or `ui/package.json` is missing.

## Jobs

| Job | Runs |
| --- | --- |
| `rust-lint` | `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo deny check`, then `cargo doc --workspace --no-deps` with warnings denied |
| `rust-test` | `cargo nextest run --workspace --all-features` (which includes the drift test of the generated reference pages), the same for `tlilli-core` with `--no-default-features`, then `cargo test --doc --workspace` |
| `ui` | `pnpm -C ui install --frozen-lockfile`, then `exec biome ci .`, `typecheck`, `exec vitest run --coverage`, `build` and the Playwright smoke subset, `exec playwright test --grep @smoke` (it needs a Chromium; see [Setup](setup.md)) |
| `docs-build` | `scripts/docs.sh` (`mkdocs build --strict`), then, when `Cargo.toml` exists, `scripts/api_docs.sh`: `cargo doc --workspace --no-deps` into `site/api` with a page that lists the crates |
| `tauri/linux` | `pnpm -C ui install --frozen-lockfile`, then `pnpm -C ui tauri build --no-bundle` |
| `scripts` | the tests of `ci.sh` and `gen_fixtures.py` under `scripts/tests/` (not in `ci.yml` yet) |
| `rust` | an alias for `rust-lint` then `rust-test` |
| `reuse` | `reuse lint` ([Licensing](licensing.md)); it runs only when named, until CI runs it |

Pending jobs are named but not run until the rest of the `ci.yml` rewrite (bootstrap task 20) adds them: `commits`, `size/limit`, `docs/contract-sync`, `protocol-ref/drift`, `workflows/zizmor` and `e2e/smoke`. `all` skips them, and naming one exits with status 2. Not mirrored: the `build/*` matrix, which runs when a pull request is Ready; the coverage uploads to Codecov, of the nextest runs, which `rust-test` puts through `cargo llvm-cov` in CI, and of the Vitest report that `ui` writes locally too; and the `codecov/patch/*` checks, which the Codecov service computes.

## Related checks

- `scripts/gen_reference.sh --check` generates the reference pages into a temporary directory, compares them with `docs/reference/` and fails when they differ (`PR-DOC-003`); it changes nothing. Without `--check`, the script replaces the committed pages. The pending `protocol-ref/drift` job covers `docs/reference/mcp/` and the schemas ([33 CI/CD](../prd/33-ci-cd.md) §2); `--check` also compares `cli.md` and `skills.md`.
- The lefthook hooks installed by `pnpm -C ui install` run at commit time. When Rust files are staged, `cargo fmt --all --check` and `cargo clippy` check the whole workspace; Biome checks only the staged UI files; commitlint checks the message.
