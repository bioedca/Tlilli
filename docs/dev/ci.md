# Running CI locally

`scripts/ci.sh` runs the commands of the CI jobs on your machine and stops at the first failure (`PR-CI-010`). Run it before you push, or before marking a pull request Ready. The jobs and their gates are defined in [33 CI/CD](../prd/33-ci-cd.md) §2; `scripts/ci.sh --help` prints the current list.

```bash
scripts/ci.sh all          # the CI jobs in CI order, then scripts; reuse only when named
scripts/ci.sh rust-test    # one job
scripts/ci.sh rust ui      # several jobs, in the order given
```

The script installs no toolchain: it expects rustup, pnpm, Node 22 and Python 3 on `PATH` ([Setup](setup.md)). A Rust or UI job is skipped when `Cargo.toml` or `ui/package.json` is missing, as in `ci.yml`.

## Jobs

| Job | Runs |
| --- | --- |
| `rust-lint` | `cargo fmt --all --check`, then `cargo clippy --workspace --all-targets -- -D warnings` |
| `rust-test` | `cargo test --workspace`, which includes the drift test of the generated reference pages |
| `ui` | `pnpm -C ui install --frozen-lockfile`, then `lint`, `typecheck`, `test` and `build` |
| `docs-build` | `scripts/docs.sh` (`mkdocs build --strict`), then `cargo doc --workspace --no-deps` when `Cargo.toml` exists |
| `tauri/linux` | `pnpm -C ui install --frozen-lockfile`, then `pnpm -C ui tauri build --no-bundle` |
| `scripts` | the tests of `ci.sh` and `gen_fixtures.py` under `scripts/tests/` (not in `ci.yml` yet) |
| `rust` | an alias for `rust-lint` then `rust-test`, the `rust` job of today's `ci.yml` |
| `reuse` | `reuse lint` ([Licensing](licensing.md)); it runs only when named, until CI runs it |

Pending jobs are named but not run until the `ci.yml` rewrite (bootstrap task 20) adds them: `commits`, `size/limit`, `docs/contract-sync`, `protocol-ref/drift`, `workflows/zizmor` and `e2e/smoke`. `all` skips them, and naming one exits with status 2. The `build/*` matrix, which runs when a pull request is Ready, and the `codecov/patch/*` checks, which the Codecov service computes, are not mirrored.

## Related checks

- `scripts/gen_reference.sh --check` generates the reference pages into a temporary directory, compares them with `docs/reference/` and fails when they differ (`PR-DOC-003`); it changes nothing. Without `--check`, the script replaces the committed pages. It is the check that the `protocol-ref/drift` job will run.
- The lefthook hooks installed by `pnpm -C ui install` run at commit time. When Rust files are staged, `cargo fmt --all --check` and `cargo clippy` check the whole workspace; Biome checks only the staged UI files; commitlint checks the message.
