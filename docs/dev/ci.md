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
| `size/limit` | `scripts/pr_checks.sh size`: the hand-written changed lines of the commits since `origin/main` against the cap of 400, and the file-size caps |
| `docs/contract-sync` | `scripts/pr_checks.sh contract-sync`: a change to a contract path also changes `docs/` |
| `tauri/linux` | `pnpm -C ui install --frozen-lockfile`, then `pnpm -C ui tauri build --no-bundle` |
| `scripts` | the tests of `ci.sh`, `api_docs.sh`, `pr_checks.sh` and `gen_fixtures.py` under `scripts/tests/` (not in `ci.yml` yet) |
| `rust` | an alias for `rust-lint` then `rust-test` |
| `reuse` | `reuse lint` ([Licensing](licensing.md)); it runs only when named, until CI runs it |

Pending jobs are named but not run until the rest of the `ci.yml` rewrite (bootstrap task 20) adds them: `commits`, `protocol-ref/drift`, `workflows/zizmor` and `e2e/smoke`. `all` skips them, and naming one exits with status 2. Not mirrored:

- the `build/*` matrix, which runs when a pull request is Ready;
- the Rust coverage: CI runs the nextest commands of `rust-test` under `cargo llvm-cov`, and the local job runs them without it;
- the uploads to Codecov, of that Rust report and of the Vitest report (the local `ui` job writes the Vitest report to `ui/coverage/` but uploads nothing);
- the `codecov/patch/*` checks, which the Codecov service computes.

## The diff checks

`size/limit` and `docs/contract-sync` read the pull request's diff, so locally they compare your committed work with `origin/main`; uncommitted changes do not count. In CI they also read the pull request's labels and description, which `PR_LABELS` (comma-separated) and `PR_BODY` stand in for locally; `scripts/pr_checks.sh --help` lists the variables.

- `size/limit` counts additions and deletions outside the lockfiles, `*.snap`, `docs/reference/mcp/`, `tests/fixtures/`, images and binary files, and outside `CHANGELOG.md` on a `release-plz-*` branch (`PR-PRQ-020`). Above 400 it fails unless the pull request has the `size:override` label and a `Size override: <reason>` line (`PR-PRQ-021`). It also fails on a file over 2 MiB, or on more than 50 MiB in `tests/fixtures/` or in `docs/assets/` (`PR-GIT-031`).
- `docs/contract-sync` fails when a contract path changes without a change under `docs/`, unless the pull request has the `docs:not-needed` label and a `Docs not needed because: <reason>` line (`PR-DOC-001`). The contract paths are `crates/tlilli-mcp/src/{tools,resources,prompts}/`, `skills/`, `crates/tlilli-core/src/storage/`, `crates/tlilli-cli/src/` and `src-tauri/tauri.conf.json`.
- Write the reason line first, then add the label: adding or removing a label re-runs CI, editing the description does not.

## Related checks

- `scripts/gen_reference.sh --check` generates the reference pages into a temporary directory, compares them with `docs/reference/` and fails when they differ (`PR-DOC-003`); it changes nothing. Without `--check`, the script replaces the committed pages. The pending `protocol-ref/drift` job covers `docs/reference/mcp/` and the schemas ([33 CI/CD](../prd/33-ci-cd.md) §2); `--check` also compares `cli.md` and `skills.md`.
- The lefthook hooks installed by `pnpm -C ui install` run at commit time. When Rust files are staged, `cargo fmt --all --check` and `cargo clippy` check the whole workspace; Biome checks only the staged UI files; commitlint checks the message.
