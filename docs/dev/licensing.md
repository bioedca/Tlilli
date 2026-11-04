# Licensing policy

For contributors and agents who add or change files in the repository. The decision is D-003 in the [decision log](../prd/41-risks-and-decision-log.md); the dependency rule is `PR-ARCH-003` in [PRD 21](../prd/21-architecture-and-tech-stack.md).

## Which license applies where

| Part of the repository | License | Where the text lives |
| --- | --- | --- |
| The application (`src-tauri`), the crates (`crates/*`), the UI (`ui`), scripts, documentation and configuration | Apache-2.0 | [`LICENSE`](https://github.com/bioedca/Tlilli/blob/main/LICENSE), [`NOTICE`](https://github.com/bioedca/Tlilli/blob/main/NOTICE) |
| Skill sources under `skills/` and the per-client packages built from them | MIT | [`skills/LICENSE`](https://github.com/bioedca/Tlilli/blob/main/skills/LICENSE) |
| Canonical license texts, one per SPDX identifier, for the REUSE tooling | as named | `LICENSES/Apache-2.0.txt`, `LICENSES/MIT.txt` |
| Vendored test fixtures (open-access papers, D-027) | per fixture; CC-BY or CC0 only | `tests/fixtures/LICENSES.md` plus one `[[annotations]]` table per paper in `REUSE.toml` |

Why two licenses: the Apache License carries an explicit patent grant, which matters for an application and for crates that others build on; the skills are instruction text that people and agents should be able to copy into their own setups with the fewest conditions, so they are MIT. Both licenses are on the project's own allow-list, so the split never makes a dependency incompatible.

`LICENSE`, `skills/LICENSE`, `NOTICE` and `LICENSES/` are gated paths ([PRD 32 §3](../prd/32-code-review.md)): a change to any of them needs the maintainer's approval, and a change of license is a new decision-log entry.

## Declaring the license of a file (REUSE)

The repository follows the [REUSE specification 3.3](https://reuse.software/spec-3.3/): every file has a copyright holder and an SPDX license identifier, declared in one of two ways.

1. **SPDX header, required in Rust and TypeScript sources.** Every new `.rs`, `.ts` and `.tsx` file outside `skills/` starts with:

   <!-- REUSE-IgnoreStart -->
   ```rust
   // SPDX-FileCopyrightText: 2026 bioedca
   // SPDX-License-Identifier: Apache-2.0
   ```

   A `.rs`, `.ts` or `.tsx` file under `skills/` (the package builder, for example) carries the same two lines with the MIT identifier:

   ```rust
   // SPDX-FileCopyrightText: 2026 bioedca
   // SPDX-License-Identifier: MIT
   ```
   <!-- REUSE-IgnoreEnd -->

   TypeScript uses `//` as Rust does. `REUSE.toml` deliberately matches none of these extensions anywhere, under `.github/` and `skills/` included, so a source file without a header fails `reuse lint`. (The two examples above sit between `REUSE-IgnoreStart` and `REUSE-IgnoreEnd` markers so that `reuse` does not read them as this page's own license.)

2. **`REUSE.toml`, for everything else.** Markdown, TOML, JSON, YAML, CFF, shell scripts, text files, lockfiles, `.gitignore`, `NOTICE`, `.github/CODEOWNERS` and the Python scripts under `scripts/` are declared by path globs in [`REUSE.toml`](https://github.com/bioedca/Tlilli/blob/main/REUSE.toml): Apache-2.0 for the repository, MIT for the same header-less kinds under `skills/`. The globs name file kinds, never whole directories, so no source file is licensed by accident. When a file of a new kind arrives (a new extension, a file without one), add its glob or path to the Apache-2.0 table, and to the MIT table if it can appear under `skills/`; files that redistribute someone else's work get their own table with the right holder and identifier.

Copyright lines: the maintainer is the only human committer through v1.0, so the default holder is `2026 bioedca`. Contributors keep the copyright in their contributions (DCO, no CLA, `PR-GIT-022`); a contributor who wants to be named adds a second `SPDX-FileCopyrightText` line to the headers of the files they change. The year is the year of first publication of the file and is not updated afterwards.

## Checking

- Locally: `scripts/ci.sh reuse` (it installs the pinned `reuse` release into `.cache/`), or `pip install reuse && reuse lint` from the repository root. The run must end with "your project is compliant with version 3.3 of the REUSE Specification". `reuse lint --json` lists the files that lack information.
- In CI: a `reuse lint` step is wired into the Linux lane when `ci.yml` is rewritten by bootstrap task 20 (`uses: fsfe/reuse-action` is not on the `PR-CI-019` allow-list, so the job installs `reuse` with `pip` and runs it directly).
- Dependencies: `cargo deny check licenses` on every PR against the allow-list in `deny.toml` (bootstrap task 12): Apache-2.0, MIT, BSD-2-Clause, BSD-3-Clause, ISC, Zlib, MPL-2.0, Unicode-3.0, CC0-1.0. Anything else needs an ADR (`PR-ARCH-003`). npm dependencies of the UI follow the same allow-list.
- Fixtures: `tests/fixtures/LICENSES.md` is a gated path; only CC-BY and CC0 papers with their DOI are vendored (R-23).

## Third-party notices

`NOTICE` carries the attribution notices the Apache License asks redistributors to keep: the project's own copyright line, the license split, the list of redistributed third-party works (none yet) and the note on the three Nahuatl words the product uses. Add an entry to `NOTICE` whenever third-party code or text is copied into the repository rather than pulled in as a dependency; vendored test fixtures are the exception, recorded in `tests/fixtures/LICENSES.md`, which `NOTICE` names.
