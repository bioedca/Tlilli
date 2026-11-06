# Scheduled checks

`.github/workflows/nightly.yml` runs on `main` every day at 03:17 UTC, and on demand from the Actions tab. It holds the checks that are too slow for every pull request, or that can turn red with no change to the repository ([33 CI/CD](../prd/33-ci-cd.md) §1). `weekly.yml` follows in part 2 of bootstrap task 22.

| Job | Runs | Locally | When red |
| --- | --- | --- | --- |
| `fuzz` | Each target in `fuzz/` for ten minutes (`PR-TST-013`) | `cargo +nightly fuzz run <target> -- -max_total_time=600` ([fuzz/README.md](https://github.com/bioedca/Tlilli/blob/main/fuzz/README.md)) | `priority/P1` at once; the crash inputs are kept for 7 days as the `fuzz-artifacts` artifact |
| `playwright` | The whole browser suite; pull requests run only its `@smoke` tests (PRD 34 §1) | `pnpm -C ui exec playwright test` | The `playwright-report` artifact, kept for 7 days |
| `links` | lychee on the Markdown files, external links only (`PR-DOC-019`) | `lychee --config lychee.toml './**/*.md'` | The issue is labelled `area/docs` |
| `advisories` | `cargo deny check advisories`, because the advisory database changes every day (`PR-MNT-011`) | `cargo deny check advisories` | `priority/P1` at once |

## Tracking issues

After the four jobs, the `report` job runs `scripts/tracking_issue.py`. It keeps one issue per job, titled `Tracking: nightly/<job>` and labelled `type/task` and `area/ci`, or `area/docs` for `links` (`PR-CI-014`):

- A red run opens the issue, or reopens it, and adds a comment that links the run. The body always shows the last run.
- On the third red day in a row the issue gets `priority/P1`.
- A green run closes the issue and removes `priority/P1`. A cancelled or skipped job changes nothing, and so does a run older than the last one recorded, which finished late, as a re-run of an older run can. Runs never overlap: a new run waits for the one before it (D-083).
- Only issues that `github-actions[bot]` opened count; if two runs at once opened two, the newer is closed. Leave the first line of the body as it is: it records the day the job turned red and the last run.

## Links that cannot be checked

A host that rate-limits robots or blocks them goes in `exclude` in `lychee.toml`, with its reason, in a pull request (`PR-DOC-019`). A `429` response counts as a working link. lychee does not check links in code spans or code blocks, so placeholders such as `https://<site>/` can stay there.

## Not yet in the workflow

The criterion benchmarks against their stored baselines, which fail at a 20% regression (`PR-TST-014`); the property tests at 10,000 cases (PRD 34 §1); the compile check on the beta toolchain (`PR-MNT-013`); the LaTeX compile of exports (v0.4) and the docx check in LibreOffice (PRD 34 §3).
