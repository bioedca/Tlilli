# 34 · Testing

INTERSECT Testing rules adopted: testing is a design tool (write the test first; red–green–refactor); tests are code and follow the same design rules; parameterize instead of copy-paste; property-based tests for invariants; mock only at boundaries (network, filesystem, time, randomness); characterization tests before refactoring legacy code; reproduce every bug with a failing test before touching the implementation; test the public interface; coverage shows execution, not correctness; "you cannot outsource trust to a statistical model" — every AI-written test is read, understood and run by the human-accountable author.

## 1. Test layers

| Layer | Where | Tooling | Runs | Purpose |
| --- | --- | --- | --- | --- |
| Unit | `crates/*/src/**` (`#[cfg(test)]`) and `crates/*/tests/` | `cargo nextest`, `proptest`, `insta`, `rstest` (parameterized), `assert_cmd` (CLI) | every PR | Pure logic: segmentation, anchoring, events, guardrails, export writers |
| Property | `crates/tlilli-core/tests/prop_*.rs`, `crates/tlilli-mcp/tests/prop_*.rs` | `proptest` with saved regressions (`proptest-regressions/` committed) | every PR (256 cases), nightly (10,000 cases) | Invariants `INV-01..10`; replay; anchoring; apply/revert identity |
| Snapshot | `crates/tlilli-core/tests/snap_*.rs` | `insta` (`.snap` committed; `cargo insta review` locally) | every PR | Export formats (Markdown, docx XML parts, LaTeX, Typst source, CSL output, canonical JSON), import reports, MCP schemas, error messages |
| Contract | `crates/tlilli-mcp/tests/contract/**` | rmcp client against an in-process server; golden JSON-RPC transcripts under `tests/fixtures/transcripts/` | every PR | Every tool and resource: success and each refusal; schema snapshots; timing (`NFR-PERF-005`) |
| UI unit/integration | `ui/src/**/*.test.tsx` | Vitest + Testing Library; core mocked by a typed fake implementing the command interface | every PR | Components, store, keyboard flows, a11y (axe) |
| Browser E2E | `ui/e2e/**` | Playwright against the web UI with the mocked core (`pnpm -C ui test:e2e`) | smoke subset every PR; full nightly | User journeys end to end in the view; visual snapshots; keyboard-only suite; axe audits |
| Desktop smoke | `ui/e2e-desktop/**` (D-086) | `tauri-driver` + WebDriver under `xvfb-run` (Linux), `pnpm -C ui test:e2e:desktop` | every PR | The shell wires up: open workspace, type, send a run, cancel, accept a suggestion (from v0.2 with a fake agent) |
| Fuzz | `fuzz/fuzz_targets/*.rs` | `cargo-fuzz` (libFuzzer) with corpora committed | nightly, 10 min per target | Markdown/docx/LaTeX importers, PDF text extraction, DOI sniffing, MCP tool inputs, JSON-RPC framing |
| Mutation | `tlilli-core` | `cargo-mutants` | weekly | Test-suite strength; score tracked |
| Benchmarks | `crates/*/benches/*.rs` | `criterion` with stored baselines in `benches/baseline/` | nightly | NFR-PERF regressions (fail at +20%) |
| Gate | `docs/gates/G*.md` | Manual script on the release build with a real manuscript | per phase | Product-level acceptance |

## 2. Rules (PR-TST-001 … 020)

| ID | Rule |
| --- | --- |
| `PR-TST-001` | **Bug fixes ship a failing-first regression test** in the same PR; the PR body names the test. A fix without one is blocked by review (`needs-tests`). |
| `PR-TST-002` | **Features ship their tests in the same PR**; splitting tests into a follow-up is not allowed (D-028). |
| `PR-TST-003` | **AI-written tests are named in the PR body** ("AI-written tests reviewed and run by the author"); the author has read each one and can say what behaviour it pins. Agents MUST NOT write post-hoc tests that merely encode current behaviour of untested code; such code is refactored under characterization tests first. |
| `PR-TST-004` | The `needs-tests` label (automation applies it when `src/**` changes without `tests/**`, `*.test.*`, `#[cfg(test)]` or `.snap` changes; authors may apply it with a reason) blocks auto-merge until tests land or the maintainer removes it. |
| `PR-TST-005` | Invariants have property tests, not example tests: `replay(log) == state`; `concat(spans) == paragraph`; anchoring stability under random edit sequences; no tool-call sequence changes author text; apply∘revert = identity for mechanical edits; run state machine accepts exactly the legal transitions. |
| `PR-TST-006` | Tests touch no network, no real time and no randomness without seeds: resolvers are tested against recorded HTTP fixtures (`tests/fixtures/http/*.json`, recorded by a dev script, redacted); time is injected (`Clock` trait); `proptest` seeds are stored on failure. |
| `PR-TST-007` | Mock only at boundaries. Needing to fake more than one internal layer to test a function is a design finding, not a testing task (INTERSECT). |
| `PR-TST-008` | Tests assert on public interfaces (core API, MCP messages, UI behaviour), not private structure, so refactors do not churn tests. |
| `PR-TST-009` | Flaky tests are fixed or deleted within 48 h; no `#[ignore]` without an issue link and expiry date; retries only for `e2e/smoke` (1). |
| `PR-TST-010` | Snapshot changes are reviewed as diffs in the PR; a snapshot update without an explanation in the PR body is a review finding. |
| `PR-TST-011` | Coverage: Codecov patch ≥ 80% on `tlilli-core` and `tlilli-mcp` (required); project coverage reported; a drop > 2% on `main` opens a tracking issue. Coverage is a floor, not a goal (INTERSECT). |
| `PR-TST-012` | Mutation score on `tlilli-core` is reported weekly; target ≥ 70% by v0.4; survivors in `model`, `event`, `segment` are triaged into test issues. |
| `PR-TST-013` | Every fuzz target has a seed corpus and a 10-minute nightly budget; crashes become `priority/P1` issues with the reproducer committed as a regression test. |
| `PR-TST-014` | Benchmarks fail nightly at a 20% regression against the stored baseline; baselines are updated only in a PR that explains the change. |
| `PR-TST-015` | Test code follows the same style rules as production code (clippy on `--all-targets`, Biome on test files), is DRY through fixtures and parameterization, and uses the AAA structure (arrange, act, assert). |
| `PR-TST-016` | Fixtures policy: synthetic manuscripts generated by `scripts/gen_fixtures.py` (seeded) plus a small set of CC-BY/CC0 open-access papers vendored under `tests/fixtures/papers/` with `LICENSES.md` naming source, DOI, license and attribution; no other third-party text is committed (D-027). Revision corpora are scripted edit series over synthetic manuscripts plus the maintainer's own revision histories exported with `tlilli export --canonical` (private, used locally and at gates, not committed). |
| `PR-TST-017` | Contract transcripts are the compatibility test for agents: a new tool or field adds transcripts; a changed response shape without a deprecation entry fails `protocol-ref/drift` and the snapshot. |
| `PR-TST-018` | Tests run identically locally (`scripts/ci.sh rust-test`) and in CI; the cloud sandbox runs the Linux lane. |
| `PR-TST-019` | Skills are tested by **scenario replays**: a scripted MCP client (`tests/scenarios/*.yaml`) drives the server through the Run 7 scenario and asserts the guardrails; skill wording quality is assessed with a rubric at gates by running two real agents. |
| `PR-TST-020` | Accessibility tests (`axe-core` in Playwright) run on every PR for every page and fail on WCAG AA violations; a keyboard-only Playwright suite covers the markup, send, review and accept flows (`NFR-USE-001..002`). |

## 3. What to test, by component

**Core**
- Segmentation: fixture corpus (English, Spanish, German), abbreviation seeding, overrides, concatenation property.
- Anchoring: similarity threshold edge cases; moves; splits/merges; tombstones; corpus metric ≥ 99% (gate).
- Event log: append, hash chain, truncated/tampered logs, replay equality, snapshot dedupe, restore-creates-events.
- Storage: migrations up/down on fixture databases from every released schema version (kept in `tests/fixtures/db/`), WAL crash harness (kill-9 during writes), WAL checkpoint test with a long-lived reader in a second process, commit-failure fault injection (each commit step fails for every event type; nothing is confirmed; the reloaded state equals replay), cross-OS path handling.
- Runs: full state machine, timeout, cancel, rollback with conflicts.
- Provenance: marks under every edit kind; `mixed` rules; export summary numbers.
- Ledger: identifier normalization, dedupe, CSL rendering snapshots (styles × locales), quote verification (`quote_not_found`).
- Import/export: snapshot round-trips; docx opened by a headless LibreOffice in nightly to check for repair (`soffice --headless --convert-to pdf`).

**MCP server**
- Each tool: success transcript; each refusal (`not_claimed`, `out_of_scope`, `locked`, `too_many_alternatives`, `missing_rationale`, `budget_exceeded`, `quote_not_found`, `kind_not_allowed`).
- Auth: 401 without token; constant-time compare; revocation disconnects; rate limit on failures.
- Transport: malformed JSON-RPC, oversized payloads, concurrent clients, disconnect mid-run (claim expires).
- Resources: untrusted envelope present on fulltext/pdf/reviewer resources; templates listed.
- Prompts: text equals skill bodies (build-time test).

**UI**
- Store never holds state the core did not send (fault-injection test).
- Markup palette: fuzzy tag search, keyboard commits, counts; locked span rendering.
- Review pane: cards, alternatives, edit-before-accept, redo, resolve; announcements for run state.
- Visual snapshots in light/dark/high-contrast for ink rendering.

**Shell**
- Smoke journeys; crash dialog on injected panic; updater request shape.

## 4. Test data and privacy

Fixture manuscripts are synthetic or CC-licensed; no unpublished data is ever committed. Gate tests use the maintainer's real manuscript locally; the gate report redacts text and records metrics only (INTERSECT GenAI guidance on unpublished data applies to the agents used in gates too: the maintainer decides which manuscript is acceptable to expose to a given agent vendor).

## 5. Agent TDD workflow (INTERSECT "Co-Authoring with LLMs")

1. The issue (human or agent-drafted, maintainer-triaged) states the acceptance criteria and names the FR.
2. The agent writes the test interface first: test names and signatures that express the acceptance criteria; property statements for invariants.
3. The agent fills in cases (parameterized, edge cases, property strategies) and runs them red.
4. The agent writes the minimal implementation to green, then refactors under the tests.
5. The PR body lists the tests, marks them AI-written, and the author confirms they were read and run.
6. Reviewers (Codex lane first) check that the tests would fail without the change (mutation spot-check: `cargo mutants --file <changed file>` on request).
