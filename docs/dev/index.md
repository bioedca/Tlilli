# Developer documentation

For contributors and for the agents that work on Tlilli. `PR-DOC-013` sets what this section covers; the pages arrive with bootstrap tasks 30 to 32.

| Page | Contents | Arrives with |
| --- | --- | --- |
| [GitHub settings record](github-settings.md) | What is set on the account and the repository, by whom and when, diffed against [39 GitHub configuration](../prd/39-github-configuration.md) at every gate | published |
| Setup | Laptop setup on macOS, Windows and Linux; cloud sandbox notes; Codespaces (`.devcontainer/`) | tasks 30 and 31 |
| Running CI locally | `scripts/ci.sh` and what each lane checks ([33 CI/CD](../prd/33-ci-cd.md)) | task 30 |
| Review severity | The scale human and AI reviewers use ([32 Code review](../prd/32-code-review.md)) | task 30 |
| [Release runbook](release-runbook.md) | From tag to published release, step by step, and the handoff and successor paths ([37 Releases and packaging](../prd/37-releases-and-packaging.md), [38](../prd/38-maintenance-and-support.md) §8) | published |
| Fixtures | The synthetic manuscripts and vendored papers under `tests/fixtures/` | task 30 |
| Agent playbook | How an agent session proceeds: issue, branch, tests, PR, review pipeline, report | task 30 |
| Debugging | Reading the event log and the ledger | with the event log |

Gate scripts `G0` to `G6` (`docs/gates/`, task 30) and the ADRs (`docs/adr/`, task 16) are separate sections of the site. The root files `CLAUDE.md` and `AGENTS.md` carry the short version of these rules for agents.

To build this site locally run `scripts/docs.sh` (strict build) or `scripts/docs.sh serve` (live preview); the same build runs in `.github/workflows/docs.yml`.
