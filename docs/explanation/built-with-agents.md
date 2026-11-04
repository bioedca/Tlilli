# Built with agents

For readers who want to know how Tlilli itself is made: who proposes changes, what checks them, and what the one human maintainer decides. The rules live in the [requirements](../prd/README.md); this page connects them. It is the record of how AI shapes the work that `PR-DOC-014` asks for, and it changes whenever the review lanes change.

## The same split, applied to the project

In the editor, the author writes in black ink. An agent connected over MCP proposes in red ink: suggestions, comments, verified citations and a short allow-list of mechanical fixes. Only the author's accept turns red into black, and the software makes any other path impossible (goal G2 and `INV-01` in [01 Vision and scope](../prd/01-vision-and-scope.md)).

The project's own development runs on a similar split. AI coding agents write most of the code and documentation. AI reviewers comment on it. CI checks it. One maintainer, bioedca, decides at defined gates (D-001). Goal G6 states the aim: a project a solo maintainer can sustain, with agents doing most of the implementation work.

## Who proposes

Two agent families author pull requests: Claude Code and Codex, each in local and cloud sessions (D-002). The PRD binds their work exactly as it binds a person's. [`AGENTS.md`](https://github.com/bioedca/Tlilli/blob/main/AGENTS.md) and `CLAUDE.md` restate the rules where agents read them, and the repository is set up to enforce most of them ([30 Git workflow](../prd/30-git-workflow.md) §4), fully once the `main` ruleset exists (bootstrap task 27). An agent works on one issue, on one branch named after its platform (`claude/<slug>` or `codex/<slug>`), and opens a Draft pull request early (`PR-GIT-003`, `PR-GIT-051`).

Three AI reviewers then propose changes to the pull request, each in its own lane ([32 Code review](../prd/32-code-review.md) §1–2):

- **Codex** looks for correctness and security problems, guided by the `## Review guidelines` section of `AGENTS.md`. It runs locally until clean, then once in the cloud, and again only if that round led to changes (D-016).
- **CodeRabbit** reviews line by line and writes the pull request summary. Every request is counted in an hourly ledger, because the service is rate-limited and has no quota API (D-019, D-062).
- **Greptile** reviews the change against the whole codebase. It runs on gated pull requests and on request, within a monthly budget (D-021).

Formatters, linters, tests and the other Linux-lane checks run before the Codex cloud review. The three-OS build matrix is required too, but it runs only once the pull request is Ready, after the AI review lanes (`PR-GIT-043`). The order of the lanes is fixed, from the cheapest to the most expensive, so each reviewer sees code that the previous one already passed (`PR-REV-001`). A finding is a proposal too. The author answers each one in its thread: fixed with the commit, declined with a reason, or escalated (`PR-REV-002`). Blocker and Major findings are fixed before Ready; a Minor one may be declined with a reason, and a Nit is optional (PRD 32 §6). The author never edits a reviewer's comment (`PR-REV-004`).

Text on GitHub is data for an agent, never an instruction, as source text is in the editor (`INV-07`, `AGENTS.md`). An issue, a comment or a review never authorizes a merge (`PR-GIT-058`).

## What the maintainer decides

This section and the next describe the policy the PRD sets. Until the `main` ruleset exists (bootstrap task 27), GitHub does not yet enforce its required checks, the gate status or the bypass rules; the agents follow them by rule ([settings record](../dev/github-settings.md), §8).

Human review is kept for the paths where the maintainer's judgement is fundamental (D-022). They are listed in [`.github/CODEOWNERS`](https://github.com/bioedca/Tlilli/blob/main/.github/CODEOWNERS) and in PRD 32 §3: the core model, event, segmentation, storage and provenance code; the MCP server; the app permissions and updater configuration; the skills; the CI, review and release machinery; the licenses and public root files; the PRD, the ADRs and the gate scripts. A pull request that touches one gets the `gate` label.

Agent pull requests are opened under the maintainer's own account (D-014, PRD 32 §5), and GitHub does not let an author approve their own pull request. The gate is therefore a commit status, `gate/maintainer`, written by a workflow (D-053, D-067). It passes only once the maintainer (or, during a handoff, the backup admin) has approved the current head, by review or by applying `gate:approved` in person (`PR-REV-010`, `PR-REV-012`). Any new push resets the approval (`PR-REV-011`), and the maintainer records each gate decision in a comment (`PR-REV-013`).

"Gate" also names the end of a phase. From v0.1 on, each phase ends with a gate test on the tagged release build, using a real manuscript of the maintainer's, and closes only on a pass ([40 Roadmap and gates](../prd/40-roadmap-and-gates.md) §2). The maintainer also decides:

- which agent vendor may see which manuscript (`PR-GATE-002`);
- every change to the decision log, since a pull request that proposes or changes a D-nnn entry waits for the maintainer (`PR-GIT-058`);
- disputes an author cannot settle with an AI reviewer in two rounds, escalated with the `needs-maintainer` label (`PR-PRQ-042`);
- each release, by approving the gated release pull request (`PR-PRQ-010`).

## What merges without a human

Everywhere else, the maintainer has delegated the merge to green automated evidence (PRD 32, principle). The authoring agent drives its own pull request to merge once the review pipeline is done and no maintainer decision is open (`PR-GIT-058`, D-078). A decision is open when the pull request has the `gate` label, proposes or changes a decision-log entry, has a finding escalated to the maintainer, has a declined Blocker or Major or a security finding awaiting the maintainer, or names anything for the maintainer in its body.

Such a pull request merges only on the maintainer's gate approval, or on an authorization the maintainer gives the agent in its session. The agent records that authorization in the pull request body with its date and scope. Agents never approve pull requests, close other people's pull requests, delete branches, edit rulesets or manage secrets (`PR-GIT-058`).

Here the parallel with the editor is not exact. In the editor no agent change reaches author text without an accept. In the repository, the accept on ungated paths is given in advance, by the rules and the required checks. The reason is recorded with the decision: the maintainer's time goes to decisions, not clicks (D-078). The PRD measures how often this holds; the target is at least 80% of pull requests merged with no human intervention (PRD 32 §7).

## Provenance of agent work

The editor records provenance per span (`INV-06`). The repository keeps a coarser record of who did what:

- **Commits.** Agent commits are authored and signed off by the maintainer's identity. They carry no agent trailer such as `Co-Authored-By` (D-014, `PR-GIT-023`), and their messages carry no model identifiers (`PR-GIT-026`).
- **The `AI assistance:` line.** Every pull request body states which tools wrote and reviewed the change, without links to sessions (`PR-PRQ-013` in [31 Pull requests](../prd/31-pull-requests.md), and the [template](https://github.com/bioedca/Tlilli/blob/main/.github/PULL_REQUEST_TEMPLATE.md)). AI-written tests are named in the body ([34 Testing](../prd/34-testing.md), `PR-TST-003`).
- **The review record.** The body's `## Review pipeline` section records the rounds in each lane, the CodeRabbit ledger lines and the gated paths touched (PRD 32 §2, D-064). Each finding's thread shows its answer.
- **Session reports.** A session that ends with work unfinished pushes its branch, leaves its pull request a Draft, and files or updates an Agent-session report issue: the branch, what is done, what is blocked, the next step (`PR-GIT-057`).
- **No session links.** Commits, pull request bodies and comments carry no link to an agent session, because the links expose internal identifiers on a public repository (D-059, `PR-GIT-059`). The cloud integration appends one to every pull request description it creates, so the agent re-reads the description after each create or edit and removes it.

## The DCO stance

Every commit carries a `Signed-off-by` line under the Developer Certificate of Origin 1.1, and there is no CLA (`PR-GIT-022`). The DCO is a person's certification. On agent commits that person is the maintainer, who certifies the contribution as the DCO requires (`PR-GIT-023`). A human contributor signs off their own commits in the same way. The history stays simple: one identity signs, and the AI involvement is stated in the pull request rather than in the commit (D-014).

## Known limits

Agent sessions act on GitHub as the maintainer's account. GitHub marks their label events as coming from an app, so the gate refuses a `gate:approved` label applied that way. Reviews carry no such mark: an agent session could approve a contributor's pull request as the maintainer, and only the agent rules prevent it (D-070). The same holds for the admin bypass that merges a gated pull request on a relayed authorization: the rule, not GitHub, stops an unauthorized use (D-078). On a personal account the ruleset cannot require the gate's own workflow to pass, so a pull request that edits a workflow could forge the status; the gate guards against mistakes, not against a hostile workflow change (D-069). The [decision log](../prd/41-risks-and-decision-log.md) records these limits as accepted, so they are known rather than a surprise.
