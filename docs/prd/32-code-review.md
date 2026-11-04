# 32 · Code review

**Principle.** Automated review is the default; human review is reserved for the few paths where maintainer judgement is fundamental, and it is routed there through scoped gates. INTERSECT (Code Review, Making Good PRs): static analysis and CI handle style and common bugs so review can focus on design and behaviour; "GenAI can assist a review (summaries, first pass) but the human owns the merge decision" — here the human owns the merge decision on gated paths and has delegated it, by this PRD, to green automated evidence everywhere else.

## 1. The pipeline

```
 author agent                      GitHub PR (Draft)                              Ready → merge
 ┌──────────────┐   push   ┌─────────────────────────────────────────┐   ┌───────────────────┐
 │ self-review  │ ───────▶ │ Linux lane CI                           │   │ full matrix       │
 │ Codex local  │          │ ① Codex cloud round(s)  (@codex review) │ ─▶│ gate/maintainer   │
 │ rounds until │          │ ② CodeRabbit round      (@coderabbitai) │   │ (gated PRs only:  │
 │ clean        │          │ ③ Greptile deep review  (gated/label)   │   │  Greptile + human)│
 └──────────────┘          └─────────────────────────────────────────┘   └───────────────────┘
```

| Step | Lane | Trigger | Exit condition |
| --- | --- | --- | --- |
| 0 | **Self-review** | Before first push | `cargo fmt`, `clippy -D warnings`, `cargo nextest`, `biome check`, `vitest` pass; the author reads the full diff once (INTERSECT: self-review is "vastly better than nothing") |
| 0' | **Codex local** | Before push and after each local fix | `codex review --base origin/main` (or `codex exec review --base origin/main --json` for scripted loops) returns no findings. Repeat as many rounds as needed; Codex rounds are not the scarce resource (ChatGPT Pro, D-016). Record the round count in the PR body |
| 1 | **Codex cloud** | Author comments `@codex review` once Linux lane is green on the Draft | One review with zero unresolved findings. If the round produced code changes, run another `@codex review` after pushing. Low-severity findings may be closed with a written reason in the thread (D-018) |
| 2 | **CodeRabbit** | Author comments `@coderabbitai review` after step 1 is clean **and** the quota ledger allows it | All actionable findings fixed or declined with reason; threads resolved via `@coderabbitai resolve`. A second round only if the first caused code changes (D-019) |
| 3 | **Greptile deep review** | Automatic on PRs with the `gate` label; on demand with `review:deep` | Findings handled like CodeRabbit's; budget ≈ 15–20 per month (one paid seat, D-021) tracked in the triage ledger. Base tier with T-Rex runtime validation enabled where Greptile supports it |
| 4 | **Human gate** | PR has `gate` label and is Ready | Maintainer approval (review approval, or `gate:approved` label when the maintainer is the PR author of record) — see §5 |
| 5 | **Merge** | Author enables auto-merge at Ready | Auto-merge lands it (rebase) once the branch is up to date with `main` and all required checks pass |

Rules:

| ID | Rule |
| --- | --- |
| `PR-REV-001` | The pipeline order is fixed: Codex local → Codex cloud → CodeRabbit → (Greptile) → (human). A later lane is not invoked while an earlier lane has open findings, so each tool reviews code that already passed the cheaper one. |
| `PR-REV-002` | Every AI finding is answered in its thread: fixed (with SHA), declined (with reason) or escalated. Unanswered findings block Ready. |
| `PR-REV-003` | "Clean" for Codex means zero open findings of any severity after the author's replies; declining is allowed only for severity ≤ minor and must give a reason that a reader can check. |
| `PR-REV-004` | The author never edits or deletes a reviewer's comment; disagreement is written as a reply. |
| `PR-REV-005` | Reviewer configuration files are gated paths: `.coderabbit.yaml`, `AGENTS.md` (the `## Review guidelines` section), `greptile.json`, `.github/CODEOWNERS`, `.github/workflows/**`. Changing how review works is a maintainer decision. |
| `PR-REV-006` | Review feedback that reveals a missing test or doc is handled in the same PR unless it would exceed the size cap, in which case a follow-up issue is opened and linked before Ready. |

## 2. Lane configuration

### Codex (OpenAI) — adversarial correctness and security lane
- **Cloud:** the Codex GitHub app is installed on the repository with automatic reviews **off** (reviews are requested with `@codex review` so Draft pushes do not burn rounds and the order in `PR-REV-001` holds). Review rules live in `AGENTS.md` under `## Review guidelines` (root), the section Codex's GitHub integration reads from the `AGENTS.md` closest to each changed file, with nested files for `crates/tlilli-core/AGENTS.md` and `crates/tlilli-mcp/AGENTS.md`.
- **Local:** `codex review --base origin/main` in the authoring session; `--uncommitted` before committing; `codex exec review --base origin/main --json` for non-interactive loops.
- **Focus (in `## Review guidelines`):** violations of `INV-01..10`; event-log consistency and replay; span-ID stability; migrations; MCP guardrail bypasses; untrusted input handling and prompt-injection paths; `unsafe`, `unwrap`, panics in parsers; error handling; concurrency; secrets; test adequacy (would the tests fail without the change?); failing-first test present for bug fixes.
- **Not in scope:** formatting, naming taste, style already enforced by `rustfmt`/`clippy`/Biome.

### CodeRabbit — line-level review and PR summary lane
- `.coderabbit.yaml` (gated): `reviews.auto_review.enabled: false`; `reviews.auto_review.drafts: false`; `reviews.request_changes_workflow: true` (CodeRabbit posts "request changes" until its actionable threads resolve, which feeds the conversation-resolution requirement); `reviews.high_level_summary: true`; `reviews.poem: false`; `reviews.path_instructions` per crate (core: event sourcing and ID stability; mcp: guardrails and schema validation; ui: accessibility, keyboard paths, no state outside the store; skills: plain English, three Nahuatl terms, untrusted-text rule); `reviews.path_filters` excluding generated paths; `knowledge_base` on with this PRD and the ADRs as context; `tone_instructions`: "Critique code, not people. Prefer questions and 'we could'. Prefix nits with Nit:." (INTERSECT).
- **Plan and quota ledger (D-019, D-062):** CodeRabbit runs on the **Team plan** (one seat). The Open Source plan was not available at bootstrap because the repository does not yet meet CodeRabbit's popularity threshold; it is revisited when the repository qualifies. Every plan is rate-limited per developer on a rolling hour (Team: a standard refill of about 8 reviews per hour that steps down with recent volume, per CodeRabbit's rate-limit documentation), no quota API exists, and all agent requests count against the maintainer's seat. The ledger threshold is derived from the plan in force: 75% of the published hourly refill, rounded down (Team: **6** requests per 60 minutes repo-wide), recorded in `docs/dev/github-settings.md` and re-derived whenever the plan changes; Open Source figures MUST NOT be assumed. The authoring agent records every request as a ledger line in the PR body's `## Review pipeline` section (timestamp and running count for the hour) and in the Agent-session report; the maintainer mirrors those lines into the Project field `CodeRabbit requests` at triage, because agent sessions cannot reach Projects v2 (D-064). Before posting, the agent counts every request made across the repository in the last 60 minutes, on open PRs and on PRs merged or closed since, and MUST NOT post `@coderabbitai review` once the threshold was reached. On a rate-limit reply (text contains `rate limit`, with a wait time), the agent waits the stated time plus one minute, then retries once; a second limit schedules the request in an Agent-session report instead of retrying.
- **CLI:** `coderabbit review --plain --base origin/main` may be used locally for a pre-check; it counts against the same ledger.
- **Commands used:** `@coderabbitai review`, `@coderabbitai resolve`, `@coderabbitai summary` (regenerate the summary before Ready), `@coderabbitai pause`/`resume` are maintainer-only.

### Greptile — codebase-wide, deep review lane
- Installed as a GitHub app; dashboard configured to review only PRs carrying `gate` or `review:deep` (label trigger), Base tier, T-Rex runtime validation enabled when supported for the tier, strictness tuned to avoid nit floods; `greptile.json` (gated) holds custom instructions: architecture boundaries ([21](21-architecture-and-tech-stack.md) §4), the invariants, the threat register, "do not repeat findings already present in the PR".
- Budget ≈ 15–20 reviews per month (one paid seat, D-021). The triage ledger records each review; when 90% of the budget is used before day 20, `review:deep` requests are deferred to the next month and gated PRs rely on Codex, CodeRabbit and the maintainer.
- Agents MAY add `review:deep` when a PR touches cross-cutting behaviour without being gated (segmentation, export fidelity, UI state model) and MUST say why in the PR body.

### Static and automated checks that precede all lanes
`rustfmt`, `clippy` (pedantic subset, `-D warnings`), `cargo-deny`, Biome, `cargo nextest`, Vitest, Playwright, insta snapshots, `zizmor`, commitlint, DCO, size, docs-sync and protocol-drift checks ([33](33-ci-cd.md)). INTERSECT: "don't argue style; let a formatter or style guide decide."

## 3. Human review: scoped gates

The maintainer reviews only PRs that touch **gated paths**. Everything else merges on automated evidence.

| Gated path (CODEOWNERS) | Why maintainer judgement is fundamental |
| --- | --- |
| `crates/tlilli-core/src/model/**`, `src/event/**`, `src/segment/**`, `src/provenance/**` | The source of truth: ID stability, event semantics and provenance define the product's trust claims |
| `crates/tlilli-core/src/storage/**`, `migrations/**`, workspace folder layout | Users' data durability and forward compatibility |
| `crates/tlilli-mcp/**` | The only door for agents: the pen rule and prompt-injection defences live here |
| `src-tauri/tauri.conf.json`, `src-tauri/capabilities/**` | App permissions and updater configuration |
| `skills/**` | The behaviour contract agents learn; MIT-licensed public text |
| `.github/**`, `.coderabbit.yaml`, `greptile.json`, `AGENTS.md`, `CLAUDE.md`, `deny.toml`, `release-plz.toml`, `cliff.toml`, `codecov.yml` | Supply chain, CI, review and release machinery |
| `LICENSE*`, `NOTICE`, `SECURITY.md`, `GOVERNANCE.md`, `CITATION.cff`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md` | The project's word to the public |
| `docs/prd/**`, `docs/adr/**`, `docs/gates/**` | Requirements and decisions |
| `tests/fixtures/LICENSES.md` | Licensing of vendored texts |

`.github/CODEOWNERS` lists these paths with owners `@bioedca` and, once named, the backup admin ([38](38-maintenance-and-support.md) §8), so the backup admin can be a gate authority; the check accepts their approval only while the handoff state is active (`HANDOFF_ACTIVE`, `PR-REV-010`), never on the strength of the CODEOWNERS entry alone. The entry and the check land in the same PR (bootstrap task 19), so there is no window in which the backup admin's approval counts unchecked. A team replaces the user list only if the project ever moves to an organization. The path labeler applies `gate` when any changed file matches.

## 4. Human review checklist (used at gates)

Google's checklist as cited by INTERSECT, plus Tlilli-specific items:
1. **Design:** fits the architecture boundaries and the invariants; no new coupling across crates; ADR present where required.
2. **Functionality:** does what the issue asks; edge cases (empty manuscript, locked spans, concurrent clients, cancelled runs).
3. **Tests:** would fail without the change; property tests for invariants; failing-first test for bugs; AI-written tests were read by the author (PR body).
4. **Naming, comments, style:** names say what; comments say why; formatter decides the rest.
5. **Docs:** contract changes documented; generated reference regenerated; changelog by commit types.
6. **Pen rule and scope:** no path lets an agent write author text; refusals have tests.
7. **Compatibility:** schema migration reversible or documented; MCP schema change additive or deprecated properly.
8. **Security:** untrusted envelopes intact; no new network host; limits on parsers; secrets absent.
9. **Accessibility (UI):** keyboard path, ARIA, non-colour cues.
Pace: ≤ 500 lines per hour, ≤ 60 minutes per sitting (INTERSECT); gated PRs are therefore also capped at 400 lines.

## 5. The gate mechanism (`gate/maintainer` required check)

Problem: agent PRs are opened and committed under the maintainer's own GitHub identity (D-014), and GitHub does not let a PR author approve their own PR. So "require 1 approval from code owners" cannot express the gate. Solution: a required commit status written by `gate.yml` (D-067).

| ID | Rule |
| --- | --- |
| `PR-REV-010` | `gate.yml` writes the verdict as the commit status `gate/maintainer` on the PR's head commit, `pending` first so that a crashed run blocks the merge; the `main` ruleset (bootstrap task 27) requires that status context, not a check run. It runs on `pull_request_target` (`opened`, `synchronize`, `reopened`, `ready_for_review`, `edited`, `labeled`, `unlabeled`) without checking out PR code, and on `workflow_run` of `gate-relay.yml`, a no-permission workflow on `pull_request_review` (`submitted`, `edited`, `dismissed`) that only relays review events to the trusted copy. It **passes** when the PR touches no CODEOWNERS path (as CODEOWNERS stands on the base branch), or when a **gate authority** has approved the current head after the last reset (the newest base change or force-push, else the PR's creation), by review or by the `gate:approved` label with its approval record (`PR-REV-011`). Gate authorities are: the maintainer (`@bioedca`) always, and the backup admin (login in the variable `BACKUP_ADMIN`) only while the repository Actions variable `HANDOFF_ACTIVE` is `true` ([38](38-maintenance-and-support.md) §8). An approval or label from anyone else, or from the backup admin while the variable is `false`, is ignored and named in the failure message. Otherwise it **fails** with a message naming the gated files. |
| `PR-REV-011` | Any new push invalidates approval: a review counts only on the commit it approved, and the label only with the approval record its `labeled` run writes on that head (the commit status `gate/approval-record`, naming the authority and the base), so a new head has neither. A base change or a force-push voids every earlier approval, also on a restored former head. The workflow removes a stale `gate:approved` with a comment ("gate approval reset by new commits", or the base-change or force-push reason); stale review approvals are dismissed by the ruleset setting "dismiss stale reviews". Known limits: D-068. |
| `PR-REV-012` | Only a gate authority (`PR-REV-010`) may apply `gate:approved`: the maintainer, or the backup admin while `HANDOFF_ACTIVE` is `true`. The label counts only when applied in person: the workflow verifies the label event's actor against that set and the variable, refuses a label applied through a GitHub App (an agent session acting as the maintainer, D-070), and removes the label with a comment otherwise. |
| `PR-REV-013` | The maintainer records the gate decision in a PR comment (two lines minimum: what was checked, any follow-up issue). This is the audit trail INTERSECT asks for from a human reviewer. |
| `PR-REV-014` | `gate` is applied by the path labeler from `.github/labeler.yml` mirroring CODEOWNERS; the labeler runs on `pull_request_target` with read-only permissions and no checkout of PR code. |
| `PR-REV-015` | If a co-maintainer joins (GOVERNANCE), approvals move to ordinary code-owner reviews and `gate:approved` is retired by a decision entry. |

Residual risk: the ruleset rule "Require workflows to pass" is unavailable on a personal account, so a same-repository PR that edits a workflow could post a forged `gate/maintainer` status or silence the relay; the gate guards against mistakes, not an adversarial workflow change (D-069).

## 6. Severity taxonomy and mapping

| Tlilli severity | Must the author act? | Codex | CodeRabbit | Greptile |
| --- | --- | --- | --- | --- |
| **Blocker** (data loss, invariant violation, security, build break) | Fix before Ready; no decline | P0/P1, "critical" | "critical", "potential issue" with security tag | "critical" |
| **Major** (correctness bug, missing test for new behaviour, contract drift) | Fix before Ready | P2, "bug" | "potential issue", "refactor suggestion" with correctness impact | "major"/"important" |
| **Minor** (edge case, clarity, performance smell) | Fix or decline with reason | P3 | "refactor suggestion", "verification" | "minor" |
| **Nit** (wording, ordering, optional idiom) | Acknowledge; optional | "nit" | "nitpick" | "nit"/"style" |

Mapping is maintained in `docs/dev/review-severity.md` and updated when a tool renames its levels.

## 7. Review metrics (reported monthly in the triage issue)

Rounds per PR per lane; findings per lane split by severity and by outcome (fixed, declined, false positive); time from Draft to Ready and Ready to merged; share of PRs merged with zero human intervention (target ≥ 80%); gate turnaround (target ≤ 48 h); Greptile and CodeRabbit budget use. Lanes are retuned quarterly from these numbers (`path_instructions`, `## Review guidelines`, Greptile strictness); the retuning is itself a gated PR.

## 8. Review etiquette (both directions, from INTERSECT Code Review)

Critique the code, not the person; avoid "you"; explain reasoning and alternatives; ask questions; give feedback, not commands; label severity; praise good work; improve, do not perfect; never argue style; handle stalemates by escalating to the maintainer (`needs-maintainer`) or agreeing to disagree in writing.
