# 35 · Documentation

INTERSECT Documentation rules adopted: Diátaxis quadrants are not mixed; the README covers what/why, install, a quick example, license, citation, contribution; comment the why; documentation is version-controlled and built by CI from committed source (never committed HTML); less is more and good enough beats perfect; document as you go; user-test docs with a newcomer; GenAI drafts are reviewed for accuracy by a human who supplies the project context.

## 1. Site

| Item | Decision |
| --- | --- |
| Generator | MkDocs + Material for MkDocs; plugins: `search`, `mkdocs-redirects`, `mkdocs-git-revision-date-localized`, `mkdocs-glightbox`, `mike` (versioning, from v1.0); Python deps pinned with hashes in `docs/requirements.txt` |
| Hosting | GitHub Pages from `docs.yml` via `actions/deploy-pages` (OIDC); URL `https://bioedca.github.io/Tlilli/`; `site_url` set from day one; custom domain (candidate `tlilli.dev`; the Student Developer Pack's one-year free domain offers are an option for the first year) added with a `CNAME` once the trademark search clears (D-035) with redirects kept |
| Versioning | Single `latest` through 0.x. From v1.0: `mike` publishes `1.0`, `1.1`, … with aliases `latest` (newest stable) and `dev` (built from `main` on every merge); a version switcher in the header; old minors kept read-only |
| API docs | `cargo doc --workspace --no-deps` deployed under `/api/` of the same site; docs.rs builds happen automatically when crates publish |
| Updater manifests | `updates/stable.json` and `updates/beta.json` published by `post-release.yml` into the Pages site (consumed by the app, [37](37-releases-and-packaging.md)) |
| Build strictness | `mkdocs build --strict` (broken links and missing pages fail CI); `lychee` link check nightly for external links |
| Search | Material built-in; no third-party analytics (INV-08 applies to the site too: no trackers) |

## 2. Structure (Diátaxis)

```
docs/
  index.md                      front door: what Tlilli is, the ink metaphor, three links (tutorial, agents, download)
  tutorials/                    learning-oriented, one per gate milestone
    first-manuscript.md         v0.1: create workspace, import a draft, mark up, snapshot, export
    first-run-claude-code.md    v0.2: connect Claude Code, run the Run 7 scenario on the sample manuscript
    first-run-codex.md          v0.2
    verify-citations.md         v0.3
    style-and-sweep.md          v0.4
    reviewer-response.md        v0.5
  how-to/                       task-oriented
    install/{macos,windows,linux}.md   incl. the unsigned-binary steps and checksum/attestation verification
    agents/{claude-code,codex,chatgpt-tunnel}.md
    import-docx.md, export-latex.md, export-pdf.md, zotero.md, shared-pool.md, style-sheet.md,
    locked-spans.md, diagnostics.md, updater.md, uninstall.md
  reference/                    information-oriented, mostly generated
    mcp/{tools,resources,prompts}.md   GENERATED from the server schema (do not edit)
    schemas/*.json                     GENERATED JSON Schemas (canonical JSON, style sheet, tool inputs)
    cli.md                             GENERATED from clap (`tlilli --help` tree)
    workspace-format.md                folder layout, SQLite tables, migration list
    keyboard-shortcuts.md
    skills.md                          the skill pack, one section per skill (built from skills/)
    style-sheet-fields.md, request-tags.md, claim-link-statuses.md
  explanation/                  understanding-oriented
    ink-and-provenance.md, turn-protocol.md, why-no-prompt-box.md, trust-boundary.md,
    architecture.md, span-anchoring.md, local-first.md, agent-agnostic.md, built-with-agents.md
  project/                      the project itself
    roadmap.md (from docs/prd/40), changelog.md (CHANGELOG.md included), release-notes/,
    contributing.md (CONTRIBUTING.md included), code-of-conduct.md, security.md, support.md,
    governance.md, license.md, cite.md, status.md (nightly/weekly tracking)
  prd/                          this PRD (rendered as "Requirements")
  adr/                          ADRs (rendered as "Decisions"), index generated
  gates/                        gate scripts G1–G6 and filed reports (redacted)
  dev/                          developer docs: setup (laptop, cloud sandbox, Codespaces), ci.md, review-severity.md,
                                release-runbook.md, fixtures.md, debugging.md, agent-playbook.md
  assets/                       screenshots (generated at tags), diagrams (SVG), palette
```

## 3. Rules (PR-DOC-001 … 020)

| ID | Rule |
| --- | --- |
| `PR-DOC-001` | **Hard sync rule on contracts.** A PR that changes `crates/tlilli-mcp/src/{tools,resources,prompts}/**`, `skills/**`, `crates/tlilli-core/src/storage/**` (schema), `crates/tlilli-cli/src/**` (flags) or `src-tauri/tauri.conf.json` MUST change `docs/**` in the same PR, or carry `docs:not-needed` with a `Docs not needed because:` line. Enforced by `docs/contract-sync` (D-024). |
| `PR-DOC-002` | **Soft rule elsewhere.** Every other PR answers the Docs section of the PR template; AI reviewers flag user-visible behaviour without docs. |
| `PR-DOC-003` | **Generated reference is never hand-edited.** `docs/reference/mcp/**`, `docs/reference/schemas/**`, `docs/reference/cli.md` and `docs/reference/skills.md` are produced by `tlilli mcp schema --markdown`, `tlilli schema dump`, `tlilli --help-markdown` and `tlilli skills build --docs`; `protocol-ref/drift` fails on drift. Generated files carry a header comment saying so. |
| `PR-DOC-004` | Each tutorial is the written form of a gate test; it is re-run (by a newcomer or the maintainer following it literally) at that gate (INTERSECT: user-test docs). |
| `PR-DOC-005` | Diátaxis discipline: tutorials do not explain, how-tos do not teach, reference does not advise, explanation does not instruct. The reviewer rubric includes this check for docs PRs. |
| `PR-DOC-006` | README stays short: badges, one-paragraph what/why, install links per OS, 10-line quick start, agent setup pointer, screenshot, license, cite, contributing. Details live on the site (INTERSECT Packaging: README and docs index are separate audiences). |
| `PR-DOC-007` | Writing style: plain English; present tense; sentence-case headings; second person for how-tos; the three Nahuatl terms only; no marketing adjectives; every page states its audience in the first line when not obvious. A `vale` style check (`docs/.vale.ini`, Microsoft style subset) runs in `docs-build` as warnings in 0.x and errors from v1.0. |
| `PR-DOC-008` | Screenshots are generated by a Playwright script at each tag (`scripts/screenshots.ts`) into `docs/assets/screens/<version>/`, ≤ 300 KB each, with alt text; hand-made screenshots are not committed. |
| `PR-DOC-009` | ADRs follow MADR (`docs/adr/NNNN-title.md`); an ADR index page is generated; ADRs are gated and immutable once Accepted ([21](21-architecture-and-tech-stack.md) §6). |
| `PR-DOC-010` | `CHANGELOG.md` is generated by release-plz/git-cliff from Conventional Commits into Keep a Changelog groups (Added ← feat; Fixed ← fix; Changed ← refactor/perf; Deprecated ← commits with `deprecat` in the subject; Removed ← `!`/BREAKING with removal; Security ← commits scoped `security` or with `security:` footer; Docs and CI omitted from the user changelog). Hand edits are rejected by review. |
| `PR-DOC-011` | Release notes = the changelog section for the version + a "Highlights" paragraph + "Known issues" + "Verify your download" (checksums, attestation command) + "Upgrade notes" (migrations). Drafted by the release workflow, edited by the maintainer before publishing. |
| `PR-DOC-012` | Every user-facing error message has a docs anchor (`https://<site>/how-to/diagnostics/#E1234`) and the app links to it. |
| `PR-DOC-013` | Developer docs cover: laptop setup (three OSes), cloud sandbox notes, Codespaces, running CI locally, fixtures, debugging the event log, the agent playbook (how an agent session should proceed: issue → branch → tests → PR → review pipeline → report). |
| `PR-DOC-014` | `docs/explanation/built-with-agents.md` states how the project uses AI agents and reviewers, what the human reviews, and the DCO stance; it is updated with any change to the review lanes (INTERSECT: keep a record of how AI shaped the work). |
| `PR-DOC-015` | Rustdoc: every public item in `tlilli-core` and `tlilli-mcp` has a doc comment with an example where sensible; `#![warn(missing_docs)]` in both crates; `cargo doc` warnings fail CI. |
| `PR-DOC-016` | Skill sources are documentation too: each skill has frontmatter (`name`, `description`, `min_app_version`), a purpose paragraph, the procedure, examples, the refusal table and the untrusted-text rule; `tlilli skills build` validates frontmatter and produces per-client packages and `docs/reference/skills.md`. |
| `PR-DOC-017` | Docs PRs are ungated unless they touch `docs/prd/**`, `docs/adr/**`, `docs/gates/**` or the public-facing root files; they still pass the full review pipeline. |
| `PR-DOC-018` | A newcomer dry run of CONTRIBUTING and the laptop setup page is part of G6; findings become docs issues. |
| `PR-DOC-019` | External links are checked nightly (lychee) with an allow-list for rate-limited hosts; broken links open a docs issue. |
| `PR-DOC-020` | Translations are out of scope through v1.0; the site is English; manuscripts in other languages are documented under how-to/segmentation. |

## 4. Root project files (contents required)

| File | Must contain |
| --- | --- |
| `README.md` | per `PR-DOC-006` |
| `CONTRIBUTING.md` | pointer to this PRD's process sections; quick version of: fork/branch, conventional commits + DCO, PR template, review pipeline expectations, size cap, how to run CI locally, where to ask (Discussions) |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 with the maintainer's contact |
| `SECURITY.md` | per `PR-SEC-001` |
| `SUPPORT.md` | where to ask, what is supported ([38](38-maintenance-and-support.md)), how to produce diagnostics |
| `GOVERNANCE.md` | solo-maintainer model, decision process (this PRD + decision log), contributor → committer → maintainer ladder (dormant until needed), succession and secrets-recovery statement |
| `CITATION.cff` | title, authors, version (kept in step by the release PR), DOI (Zenodo concept DOI), license, repository |
| `LICENSE`, `skills/LICENSE`, `NOTICE` | Apache-2.0 text; MIT text for skills; NOTICE listing third-party notices and the Nahuatl naming note |
| `CHANGELOG.md` | generated (`PR-DOC-010`) |
| `AGENTS.md`, `CLAUDE.md` | agent context: layout, commands, rules, pointer to CONTRIBUTING and this PRD, `## Code Review Rules` (Codex) |
| `.github/FUNDING.yml` | GitHub Sponsors (`github: [bioedca]`) |
