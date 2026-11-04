# ADR-0008: The Tauri 2 dependency footprint of the desktop shell

- **Status:** Accepted 2026-11-04 (the maintainer's approval of pull request 69; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 14 ([PRD 42](../prd/42-bootstrap-backlog.md) row 14, issue 22), in answer to a review finding on pull request 69.

## Context

[PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) locks Tauri 2 as the shell and `tauri-plugin-updater` with minisign as the updater (D-049), and §2 places the shell in `src-tauri` as `tlilli-app`, a binary that is never published (ADR-0001). `PR-REL-030` wires the updater. The dependency policy of [PRD 21 §5](../prd/21-architecture-and-tech-stack.md#5-dependency-and-sidecar-policy-pr-arch) applies to these crates like any other:

- `PR-ARCH-002`: a dependency with native code (C or C++ builds, bundled binaries) or more than 200 transitive crates requires an ADR.
- `PR-ARCH-003`: licenses outside the allow-list in `deny.toml` need an ADR.
- `PR-CI-012` and `PR-MNT-011`: `cargo deny check` is to run on every pull request and nightly, with advisories set to deny; `deny.toml` asks every ignore entry for a reason.

Locking Tauri fixes the choice of shell but records neither its size nor its native code. ADR-0002 set the pattern for `rmcp`: the pull request that first adds a dependency reports the crate count and cites an ADR when the count is above 200. Pull request 69 adds Tauri, and this ADR is that record.

Measured on pull request 69 at `78a8f97` with the committed `Cargo.lock`, using `cargo tree -p tlilli-app --target <t> -e normal,build`. Each figure counts distinct name and version pairs, without `tlilli-app` itself:

| Target | Crates in the `tlilli-app` tree |
| --- | --- |
| `x86_64-unknown-linux-gnu` | 304 |
| `x86_64-apple-darwin`, `aarch64-apple-darwin` | 270 |
| `x86_64-pc-windows-msvc` | 262 |
| all targets | 430 |

`Cargo.lock` grows from 24 to 475 packages. Native code in that tree:

- on every target, `ring`, which compiles C and assembly with `cc` (the TLS of the updater's HTTP client: `reqwest` with rustls, the stack [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) also names for the resolvers);
- on Linux, the gtk-rs and WebKitGTK `-sys` bindings (GTK 3, WebKitGTK 4.1, JavaScriptCore, libsoup 3, and dbus through `libdbus-sys`), which link system libraries found with pkg-config and build no C of their own;
- on macOS, `objc2-exception-helper`, a small Objective-C file compiled with `cc`;
- on Windows, `embed-resource`, which compiles the resource script (icon, manifest) at build time.

`cargo deny check` on that head fails on three items, all from Tauri's Linux stack:

- **License.** `target-lexicon` 0.12.16 is `Apache-2.0 WITH LLVM-exception`, which is not on the allow-list. It is reached only as a build dependency: `cfg-expr` 0.15 → `system-deps` 6 → the build scripts of the gtk-rs `-sys` crates. It is not linked into the app.
- **RUSTSEC-2024-0370.** `proc-macro-error` 1.0.4 is unmaintained, and no patched version exists. It is a dependency of the `glib-macros` 0.18 procedural macros, so it runs inside the compiler at build time and ships no code.
- **RUSTSEC-2024-0429.** `glib` 0.18.5 is unsound: the `Iterator` and `DoubleEndedIterator` implementations of `glib::VariantStrIter` can dereference a null pointer. The fix is in `glib` 0.20.0 and later. Every Tauri 2 release, 2.12.5 included, runs its Linux backend (`tao`, `wry`, `muda`, `webkit2gtk` 2.0) on the gtk-rs 0.18 GTK 3 bindings, which require `glib` 0.18.

The older "gtk-rs GTK3 bindings - no longer maintained" advisories (RUSTSEC-2024-0410 to 0420) were withdrawn on 2026-08-14 and do not fire.

## Decision

**Accept Tauri 2's dependency tree for `tlilli-app` only.** This ADR is the record `PR-ARCH-002` requires for `tauri`, `tauri-build`, `tauri-plugin-updater` and the transitive crates they bring, including the native code listed above. The acceptance is scoped:

- **Other crates.** `tlilli-core`, `tlilli-mcp` and `tlilli-cli` do not depend on these crates and keep `PR-ARCH-002` as written: a dependency added there with native code or more than 200 transitive crates needs its own ADR, as `rmcp` has ADR-0002.
- **New dependencies of `tlilli-app`.** Further plugins, such as the `opener` plugin of [PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component), fall under `PR-ARCH-002` on their own. The pull request that adds one reports the crates and native code it adds beyond this tree.
- **Tauri versions.** Minor and patch updates within Tauri 2 stay covered. A Tauri major version is a new decision with a new ADR.

**License exception, crate-scoped.** `deny.toml` gains one `[[licenses.exceptions]]` entry that allows `Apache-2.0 WITH LLVM-exception` for `target-lexicon` only. The global allow-list of `PR-ARCH-003` is unchanged, so another crate under this license still fails the check. The LLVM exception only adds permissions to Apache-2.0: embedded object code may be redistributed without the attribution conditions, and GPLv2 compatibility is granted. It is therefore compatible with the app's own Apache-2.0 (D-003). The crate is build-time only.

**Two advisory ignores, each with an exit condition.** `deny.toml` gains two `ignore` entries whose `reason` cites this ADR:

- **RUSTSEC-2024-0370 (`proc-macro-error`, unmaintained).** Tolerable: it is a procedural-macro dependency that runs only at build time on gtk-rs macro input, and "unmaintained" reports no vulnerability. Exit: the Linux stack no longer uses `glib-macros` 0.18, that is, Tauri leaves gtk-rs 0.18.
- **RUSTSEC-2024-0429 (`glib` 0.18, unsound `VariantStrIter`).** Tolerable: only the iterator implementations of `VariantStrIter` are affected. At `c98948d`, no crate in the Linux tree other than `glib` references `VariantStrIter` or `Variant::array_iter_str`, the method that returns one (checked against the sources of all 304 crates). Tlilli code must not call them either. The macOS and Windows builds contain no `glib`. Exit: Tauri's Linux backend moves to `glib` 0.20 or later.

When an exit condition is met, `cargo deny` reports the ignore entry as unused. The pull request that brings the change (a Dependabot update or a Tauri upgrade) removes the entry. This ADR approves no other advisory: any other advisory in the tree still fails the check.

**Enforcement.** The exception and the ignores live in `deny.toml`, a gated path ([PRD 32 §3](../prd/32-code-review.md#3-human-review-scoped-gates)), so changing them needs the maintainer's approval. `cargo deny check` (advisories, licenses, bans, sources) runs on every pull request in the `rust-lint` job that bootstrap task 20 adds (`PR-CI-012`, [PRD 33 §2](../prd/33-ci-cd.md)), and `cargo deny check advisories` is to run nightly in `nightly.yml`, which bootstrap task 22 adds (`PR-MNT-011`). The graph covers the four release targets with all features, so platform-specific crates are checked as well. Neither workflow exists yet: until task 20 lands, authors run the check locally before a pull request, and until task 22 lands nothing checks for new advisories between pull requests.

**PRD.** No PRD text changes. The decision uses the ADR route that `PR-ARCH-002` and `PR-ARCH-003` provide, and the reasoned ignore entry that `deny.toml` already documents for `PR-CI-012`. No row is added under "PRD changes pending" in the [index](README.md).

## Consequences

### Positive

- The shell that [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) locks builds with the signed updater (`PR-REL-030`), and `cargo deny check` passes with every exception named, scoped and explained.
- The measured footprint is on record, so a later measurement shows how much it grew and where.

### Negative

- About 300 more crates compile on the Linux CI lane: the `rust` job took 295 s on pull request 69 at `78a8f97`.
- Linux builds need the WebKitGTK development packages ([PRD 33 §6](../prd/33-ci-cd.md)). Every target needs a C toolchain for `ring`, and macOS also needs one for `objc2-exception-helper`.
- The tree adds 17 duplicate-version warnings (bans: warn), and the binary size counts against `NFR-PERF-010`.

### Risks

- The gtk-rs 0.18 GTK 3 bindings are frozen, so a new `glib` 0.18 advisory may never get a patched 0.18 release. Once task 22 lands, the nightly advisory run (`PR-MNT-011`) raises it; before that, the next `cargo deny check` on a pull request does, and the answer is then a decision about the Tauri version, not another silent ignore.
- A Tauri minor or patch update can add a native-code crate that cargo-deny does not flag. Dependabot pull requests show the `Cargo.lock` diff to the reviewer, and the counts above are the baseline to re-measure against whenever the tree is questioned.

## Alternatives considered

- **Electron.** Rejected by [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions): larger, and no Rust in-process.
- **Tauri without `tauri-plugin-updater`, which removes `reqwest`, rustls and `ring`.** Rejected: D-049 and `PR-REL-030` require the plugin.
- **The updater's `native-tls` feature instead of rustls.** Not chosen: it links OpenSSL on Linux, which is also native code, and it departs from the rustls stack that the Resolvers row of [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) names.
- **Adding `Apache-2.0 WITH LLVM-exception` to the global allow-list.** Rejected: the allow-list is policy in `PR-ARCH-003`. A crate-scoped exception keeps the list as written and fails again if another crate brings the license.
- **Waiting for a Tauri release on `glib` 0.20 before adding the shell.** Rejected: no Tauri 2 release uses it, and Tauri 3 is in alpha (`3.0.0-alpha.5` on crates.io on 2026-11-04). An alpha shell fails the maintenance test of `PR-ARCH-003`, and Phase 0 needs the shell now (bootstrap task 14).
- **Excluding Linux from the cargo-deny graph.** Rejected: Linux is a release target ([PRD 37 §3](../prd/37-releases-and-packaging.md#3-artifacts-per-release)), and the graph exists to check every target's crates.

## References

- PRD: [21](../prd/21-architecture-and-tech-stack.md) §2, §3 (Shell, Updater, Resolvers), §5, §6; [22](../prd/22-security-and-threat-model.md) §3; [32](../prd/32-code-review.md) §3; [33](../prd/33-ci-cd.md) §2, §6; [37](../prd/37-releases-and-packaging.md) §3, §6; [38](../prd/38-maintenance-and-support.md); [42](../prd/42-bootstrap-backlog.md) rows 14 and 20.
- Requirements: `PR-ARCH-002`, `PR-ARCH-003`; `PR-CI-012`; `PR-MNT-011`; `PR-REL-030`; `NFR-PERF-010`.
- Decisions and threats: D-003, D-049; T-07; ADR-0001, ADR-0002.
- Advisories: RUSTSEC-2024-0370, RUSTSEC-2024-0429 (GHSA-wrw7-89jp-8q8g); withdrawn RUSTSEC-2024-0410 to RUSTSEC-2024-0420.
