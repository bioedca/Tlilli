# Fuzz targets

libFuzzer targets for `tlilli-core` and `tlilli-mcp`, run by `cargo-fuzz` (`docs/prd/34-testing.md` §1,
`PR-TST-013`). This directory is its own Cargo workspace and is excluded from the root workspace, so a
stable `cargo build --workspace` never compiles libFuzzer.

## Run

`cargo-fuzz` needs a nightly toolchain; the root `rust-toolchain.toml` pins stable, so pass `+nightly`.

```sh
cargo install cargo-fuzz --locked
rustup toolchain install nightly
cargo +nightly fuzz list                                    # from the repository root
cargo +nightly fuzz run roundtrip -- -max_total_time=600    # ten minutes, the nightly budget
```

Crash inputs land in `fuzz/artifacts/<target>/` (ignored by git). Reproduce one with
`cargo +nightly fuzz run <target> fuzz/artifacts/<target>/<file>`, then commit the reproducer as a
regression test in the owning crate and open a `priority/P1` issue (`PR-TST-013`).

## Compile check without nightly

The targets build (but cannot run) on stable, which is enough to keep them compiling in ordinary CI:

```sh
cargo check --manifest-path fuzz/Cargo.toml
```

## Adding a target

1. Add `fuzz_targets/<name>.rs` with a `fuzz_target!` body and a `[[bin]]` entry in `fuzz/Cargo.toml`
   (`test = false`, `doc = false`, `bench = false`).
2. Commit a seed corpus under `fuzz/corpus/<name>/`.
3. Add the target to the nightly fuzz job (`.github/workflows/nightly.yml`, bootstrap task 22).
