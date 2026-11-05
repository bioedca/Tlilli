# Running CI locally

`scripts/ci.sh` runs the commands of the CI jobs on your machine and stops at the first failure (`PR-CI-010`). Run it before you push, or before marking a pull request Ready. The jobs and their gates are defined in [33 CI/CD](../prd/33-ci-cd.md) §2; `scripts/ci.sh --help` prints the current list.

```bash
scripts/ci.sh all          # every job that runs in CI today, in CI order
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
| `docs-build` | `scripts/docs.sh` (`mkdocs build --strict`), then `cargo doc --workspace --no-deps` |
| `tauri/linux` | `pnpm -C ui install --frozen-lockfile`, then `pnpm -C ui tauri build --no-bundle` |
| `scripts` | the tests of `ci.sh` and `gen_fixtures.py` under `scripts/tests/` (not in `ci.yml` yet) |
| `rust` | an alias for `rust-lint` then `rust-test`, the `rust` job of today's `ci.yml` |
| `reuse` | `reuse lint` ([Licensing](licensing.md)); it runs only when named, until CI runs it |

Pending jobs are named but not run until the `ci.yml` rewrite (bootstrap task 20) adds them: `commits`, `size/limit`, `docs/contract-sync`, `protocol-ref/drift`, `workflows/zizmor` and `e2e/smoke`. `all` skips them, and naming one exits with status 2. The `build/*` matrix, which runs when a pull request is Ready, and the `codecov/patch/*` checks, which the Codecov service computes, are not mirrored.

## Related checks

- `scripts/gen_reference.sh --check` regenerates the reference pages under `docs/reference/` and fails when the committed pages differ (`PR-DOC-003`). It is the check that the `protocol-ref/drift` job will run.
- The lefthook hooks installed by `pnpm -C ui install` run rustfmt, clippy and Biome on the staged files at commit time, and commitlint on the message.
