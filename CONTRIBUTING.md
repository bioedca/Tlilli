# Contributing to Tlilli

Thank you for considering a contribution. Tlilli is pre-alpha (Phase 0): one maintainer, bioedca, and AI coding agents that do most of the implementation work under the process in the [product requirements document](docs/prd/README.md) (PRD). The rules below are the short version; the PRD sections they summarize are binding for people and agents alike. External code contributions are welcome from v1.0; until then, bug reports and questions are the most useful thing you can send.

## Before you start

- Read the [README](README.md) and the [concept document](Tlilli%20-%20Concept%20%26%20Definition.md). The invariants in [PRD 01 §5](docs/prd/01-vision-and-scope.md) (the author holds the pen, every change is an event, untrusted text is labelled) are not negotiable.
- One problem per issue. Bugs, features and tasks use the issue forms ([PRD 36 §1](docs/prd/36-issues-labels-and-projects.md)); blank issues are off. Security problems never go through issues: see [SECURITY.md](SECURITY.md).
- Questions go to GitHub Discussions once they open (v0.2); until then, use the **Question** form in the [issue chooser](https://github.com/bioedca/Tlilli/issues/new/choose), which labels the issue `type/question` (blank issues are off). Documentation gaps go through the **Documentation** form. There is no chat or email support ([SUPPORT.md](SUPPORT.md)).
- Pick an issue, or open one, before writing code. A PR without an issue is allowed only for a small `chore` or `docs` change that says why.

## Workflow ([PRD 30](docs/prd/30-git-workflow.md) and [31](docs/prd/31-pull-requests.md))

1. **Fork and branch.** Branch from current `origin/main`: `git fetch origin main && git switch -c <type>/<issue>-<slug> origin/main`, with `type` one of `feat fix docs chore refactor perf test ci build`; lower-case, hyphens, at most 60 characters. Agents use their platform prefix (`claude/<slug>`, `codex/<slug>`). One branch, one PR, one issue.
2. **Commit.** Conventional Commits 1.0: `type(scope): subject` with the scope from the closed list `core mcp cli tauri ui skills docs prd ci release deps repo fixtures`; imperative subject, lower-case first letter, no trailing period, at most 72 characters; the body says what and why. Every commit is signed off (`git commit -s`) under the Developer Certificate of Origin 1.1, and the sign-off must match the author; there is no CLA. Each commit builds on its own. Squash fix-ups before review (`git commit --fixup <sha>`, then `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash origin/main`); at most 10 commits per PR.
3. **Stay current by rebasing** (`git pull --rebase origin main`), never by merging `main` into your branch; force-push only your own branch and only with `--force-with-lease`.
4. **Open a draft PR early** so the work survives interruptions. The body follows the template ([PRD 31 §3](docs/prd/31-pull-requests.md)): Summary with `Closes #<issue>`, Requirements (the `FR`, `NFR` or `PR` IDs), Changes, Testing, Docs, Review pipeline, Checklist. Write it for someone who was not there.
5. **Size.** At most 400 changed hand-written lines; lockfiles, snapshots, generated reference pages and fixtures do not count. Larger work is split by design into a stack of PRs (label `stacked`, each naming its base) or a sequence of issues. Exceeding the cap needs the `size:override` label and a `Size override: <reason>` line in the body.
6. **Tests and docs.** Bug fixes ship a failing-first test; features ship their tests in the same PR; AI-written tests are named in the body. A change to the MCP tools, resources or prompts, the skills, the storage schema, the CLI flags or `tauri.conf.json` changes `docs/` in the same PR ([PRD 35](docs/prd/35-documentation.md), `PR-DOC-001`).

## Review pipeline ([PRD 32](docs/prd/32-code-review.md))

Automated review is the default; the maintainer reviews only gated paths.

1. Self-review: run the checks below and read your whole diff once.
2. On the draft, once the Linux lane is green, comment `@codex review` and repeat until Codex reports no open findings; then `@coderabbitai review`. Answer every finding in its thread (fixed with the SHA, declined with a reason, or escalated) and resolve a thread only after answering.
3. Mark the PR **Ready for review** only when CI is green, the AI rounds are clean, the commits are squashed and rebased, and the body is complete. Ready triggers the full three-OS matrix and, for gated paths, Greptile and the maintainer.
4. Gated paths (the core model, event log, storage and provenance code, the MCP server, `skills/`, `.github/`, the licenses and the public root files, the PRD and ADRs) carry the `gate` label and merge only with the maintainer's approval. Everything else merges automatically once the branch is up to date with `main` and every required check passes; the author enables auto-merge at Ready.

## Running the checks locally

The Cargo workspace (pull request #45) and the UI package (pull request #50) are landing in Phase 0, and the `ci.yml` rewrite (bootstrap task 20) wires these commands into CI; until then, run the ones whose manifest exists in your checkout. Until `scripts/ci.sh` exists (bootstrap task 15), these are the commands CI runs:

```sh
cargo fmt --all --check
cargo clippy --workspace --all-targets -- -D warnings
cargo test --workspace
pnpm -C ui install --frozen-lockfile && pnpm -C ui build && pnpm -C ui test && pnpm -C ui lint
pip install reuse && reuse lint
```

`pnpm -C ui install` also installs the git hooks (`lefthook`): formatting, lint and commit-message checks on commit, the tests of the changed crates on push. Setup pages for a laptop, the cloud sandbox and Codespaces land under `docs/dev/`.

## Licensing of contributions

By signing off you certify the DCO. Your contribution is licensed under the license of the files you touch: Apache-2.0 for the application and the crates, MIT for `skills/`. New Rust and TypeScript files start with the two SPDX header lines; everything else is declared in `REUSE.toml`. Details: [docs/dev/licensing.md](docs/dev/licensing.md).

## Conduct

Everyone interacting with the project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
