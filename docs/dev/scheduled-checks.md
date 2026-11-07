# Scheduled checks

`.github/workflows/nightly.yml` runs on `main` every day at 03:17 UTC, and on demand from the Actions tab. It holds the checks that are too slow for every pull request, or that can turn red with no change to the repository ([33 CI/CD](../prd/33-ci-cd.md) §1). `.github/workflows/weekly.yml` runs every Monday at 05:23 UTC, before the weekly triage, and on demand.

| Job | Runs | Locally | When red |
| --- | --- | --- | --- |
| `fuzz` | Each target in `fuzz/` for ten minutes (`PR-TST-013`) | `cargo +nightly fuzz run <target> -- -max_total_time=600` ([fuzz/README.md](https://github.com/bioedca/Tlilli/blob/main/fuzz/README.md)) | `priority/P1` at once; the crash inputs are kept for 7 days as the `fuzz-artifacts` artifact |
| `playwright` | The whole browser suite; pull requests run only its `@smoke` tests (PRD 34 §1) | `pnpm -C ui exec playwright test` | The `playwright-report` artifact, kept for 7 days |
| `links` | lychee on the Markdown files, external links only (`PR-DOC-019`) | `lychee --config lychee.toml './**/*.md'` | The issue is labelled `area/docs` |
| `advisories` | `cargo deny check advisories`, because the advisory database changes every day (`PR-MNT-011`) | `cargo deny check advisories` | `priority/P1` at once |
| `bench` | A skeleton for the criterion benchmarks, which will fail at a 20% regression from their stored baselines (`PR-TST-014`). It passes while there is no benchmark; the first one makes it fail until that comparison is wired | `cargo bench` | — |
| `latex` | A skeleton for the LaTeX compile of exports in a TeX container, until the LaTeX export lands in v0.4 (PRD 34 §3) | — | — |

## Weekly checks

| Job | Runs | Locally |
| --- | --- | --- |
| `mutants` | cargo-mutants 27.1.0 on `tlilli-core` (`PR-TST-012`). Missed mutants do not fail the job; the run fails only when it cannot finish, for example when the tests fail with no mutation. The `mutants-out` artifact keeps the details for 7 days | `cargo mutants --package tlilli-core` |
| `sweep` | The stale sweep (`PR-PRQ-005`, D-084). An open pull request older than 7 days gets `status/stale` and one comment. A marked one with no push, comment or review other than the sweep's own for 21 days is closed, with a comment naming its branch; an idle one never marked is marked first, so each is warned on an earlier run. Reopening it starts the 21 days again. Ready gated pull requests, Dependabot's and the release-plz pull request are exempt. No branch is deleted | `git fetch --prune origin`, then `GITHUB_REPOSITORY=bioedca/Tlilli scripts/stale_sweep.py --dry-run`, in a full clone whose `origin` is `bioedca/Tlilli` (the branch dates come from its remote-tracking refs) |

Then the `report` job writes the `Weekly report` issue. Each run replaces its body with the new report and adds the same report as a comment, so past weeks stay readable; the issue stays open, and the run's summary page shows the report too. It has four sections (D-084):

- **The mutation score of `tlilli-core`**: caught mutants and those that timed out, out of all the viable ones. The target is 70% by v0.4. Up to 20 missed mutants are named; those in `model`, `event` and `segment` become test issues.
- **The audited labels**: each pull request updated in the past 7 days that has `docs:not-needed`, `size:override` or `needs-tests`, with its `Docs not needed because:` or `Size override:` line (`PR-PRQ-031`). The maintainer may revert any of them.
- **The stale sweep**: the pull requests it marked and closed, and the branches whose last commit is over 7 days old and that have no open pull request, each with its last pull request. Up to 30 are listed.
- **The review budgets**: the `@coderabbitai review` requests of the past 7 days and the most in any one hour, against the 2 an hour of D-085; and the Greptile reviews of the month, against 15 to 20 (D-021), with a warning when 18 are used before day 20 (R-11). A request counts when a person writes it at the start of a line. The Greptile count also includes earlier reviews of a pull request that Greptile reviewed this month, because it reads the summary comment's `Reviews (N)`.

## Tracking issues

After the jobs, each workflow's `report` job runs `scripts/tracking_issue.py`. It keeps one issue per job, titled `Tracking: nightly/<job>` or `Tracking: weekly/<job>` and labelled `type/task` and `area/ci`, or `area/docs` for `links` (`PR-CI-014`):

- A red run opens the issue, or reopens it, and adds a comment that links the run. The body always shows the last run.
- On the third red day in a row the issue gets `priority/P1`. For a weekly job that is the second red week.
- A green run closes the issue and removes `priority/P1`. A cancelled or skipped job changes nothing, and so does a run older than the last one recorded, which finished late, as a re-run of an older run can. Runs never overlap: a new run waits for the one before it (D-083).
- Only issues that `github-actions[bot]` opened count; if two runs at once opened two, the newer is closed. Leave the first line of the body as it is: it records the day the job turned red and the last run.

## Yearly reminder

`.github/workflows/yearly.yml` reopens issue #5, the updater-key restore drill, every 1 November at 06:41 UTC. It comments that the drill is due that week (`PR-REL-034`, T-09).

## Links that cannot be checked

A host that rate-limits robots or blocks them goes in `exclude` in `lychee.toml`, with its reason, in a pull request (`PR-DOC-019`). A `429` response counts as a working link. lychee does not check links in code spans or code blocks, so placeholders such as `https://<site>/` can stay there.

## Not yet in the workflow

The criterion benchmarks against their stored baselines, which fail at a 20% regression (`PR-TST-014`); the property tests at 10,000 cases (PRD 34 §1); the compile check on the beta toolchain (`PR-MNT-013`); the LaTeX compile of exports (v0.4) and the docx check in LibreOffice (PRD 34 §3).
