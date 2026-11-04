# 22 · Security and threat model

Method: INTERSECT Threat Assessment ("Who might do what bad thing to whom?"): ideate threats including accidents, organize, evaluate by likelihood and impact, summarize, then choose mitigations by benefit against cost. Re-run at each gate; the table below is the v0.x baseline.

## 1. Assets and trust boundaries

| Asset | Where | Who must not reach it |
| --- | --- | --- |
| Author text and provenance | `workspace.sqlite`, exports | Agents (write), anyone remote |
| Unpublished results, figures, protocols | `figures/`, `sources/`, manuscript | Anyone remote; AI services the author did not choose |
| Source PDFs and full text (often licensed) | `sources/` | Redistribution |
| Workspace MCP token | SQLite `settings`, shown once in UI | Any process other than the author's agent and, in v0.5, the user-installed tunnel program (T-16) |
| Updater private key (minisign) | Maintainer offline backup + sealed offline copy held by the backup admin once named + GitHub Actions secret | Everyone else |
| Release pipeline tokens (release-plz, project, tap, winget) | GitHub Actions `release` environment | Workflows outside the environment, forks |
| Repository history and `main` | GitHub | Unreviewed changes |

Trust boundaries: (1) the user's machine vs the network; (2) the Tlilli process vs the agent process, mediated only by the MCP server; (3) the app vs the content it parses (PDFs, docx, reviewer text); (4) the repository vs its contributors and CI; (5) the app vs the user-installed tunnel program (v0.5), which sees the workspace token and every tunnelled request and response and keeps its own connection to its provider, outside `NFR-SEC-004` (D-065, T-16).

## 2. Threat register

| ID | Who | Does what | To whom / what | Likelihood | Impact | Mitigations (requirement) |
| --- | --- | --- | --- | --- | --- | --- |
| T-01 | A source PDF or reviewer comment containing instructions | Prompt-injects the agent into rewriting, deleting or exfiltrating text | Author text; privacy | High (accidental or deliberate) | High | Resources label content untrusted (`INV-07`, `NFR-SEC-003`); write tools cannot reach outside scope regardless of agent intent (`INV-03`); skills instruct agents to treat such text as data; the author reviews every suggestion before it becomes text (`INV-01`) |
| T-02 | A misbehaving or buggy agent | Floods the manuscript with suggestions, deletes content, loops on tools | Manuscript quality, run time | Medium | Medium | ≤ 3 alternatives per suggestion; rationale required; one open run; heartbeat timeout rolls back mechanical edits; per-run tool-call budget (configurable, default 500 calls) with refusal beyond it (`FR-02-0xx`) |
| T-03 | Another local process or browser page | Connects to the MCP HTTP port and reads or writes the manuscript | Confidentiality, integrity | Medium | High | Bind 127.0.0.1 only; 256-bit bearer token required; token revocable; CORS denied; no browser-origin requests accepted (`NFR-SEC-001`) |
| T-04 | Anyone on the internet | Reaches the ChatGPT tunnel URL | Everything in the workspace | Medium when tunnel on | High | Tunnel off by default; token on every request; URL and stop button visible; stops with the app; rate limit per token; documented as read-mostly until plan limits allow writes (`NFR-SEC-006`); the tunnel program's own provider connection is outside `NFR-SEC-004` and disclosed while it runs (D-065); the program itself is T-16 |
| T-05 | A crafted PDF or docx | Crashes or exploits the parser | Availability; possibly code execution | Medium | High | Pure-Rust parsers; memory and time limits; parse on a separate thread with panic isolation; fuzzing nightly (`NFR-SEC-005`) |
| T-06 | The author (accident) | Loses work through crash, bad migration, synced-folder conflict | Data | Medium | High | Append-only log with hash chain; WAL; pre-migration backups; recovery on startup; sync warning (`NFR-REL-001..003`, `NFR-PRIV-004`) |
| T-07 | A compromised dependency (crates.io, npm) | Supply-chain code execution in the app or CI | Users; secrets | Low–Medium | High | `cargo-deny` advisories and sources; `pnpm audit`; Dependabot grouped updates; lockfiles committed; CodeQL; Scorecard; actions pinned to SHAs; `zizmor` on workflows ([33](33-ci-cd.md)) |
| T-08 | A malicious pull request (fork) | Steals secrets or publishes a release through CI | Secrets, users | Low | High | Fork PR workflows need approval; secrets only in the `release` environment with a required reviewer; `permissions: read-all` default; release only on tags created by the release token; no bypass on `main` |
| T-09 | Loss of the updater private key | No further updates can be delivered to installed apps | Users | Low | High | Key generated offline, stored encrypted in two places (maintainer password manager + sealed offline copy held by the backup admin once named); passphrase separate; documented in GOVERNANCE.md; test restore yearly |
| T-10 | Theft of the updater private key or release token | Malicious update signed as genuine | Users | Low | Critical | Secrets in environment with required reviewer; 2FA on the account; audit log review in triage; rotation runbook; attestations let users verify build origin |
| T-11 | An agent-authored commit | Introduces a vulnerability or license-incompatible code | Codebase | Medium | Medium | Codex adversarial lane, CodeRabbit, Greptile on gated paths, CodeQL, `cargo-deny` licenses, human gate on security-relevant paths ([32](32-code-review.md)) |
| T-12 | Unsigned binaries | Users bypass OS warnings habitually; a fake "Tlilli" could be spread | Users' trust | Medium | Medium | Checksums + Sigstore attestations verifiable with `gh attestation verify`; one canonical download page; name clearance; Homebrew/winget/Flathub channels reduce random downloads ([37](37-releases-and-packaging.md)) |
| T-13 | Logs or diagnostics bundles | Leak manuscript text or secrets to a public issue | Privacy | Medium | Medium | Redaction by default; never log text at `info`; bug form reminds to check (`NFR-PRIV-003`, `NFR-SEC-008`) |
| T-14 | Resolver services | Learn what the author is citing | Privacy (low sensitivity) | High | Low | Author-initiated only; allow-list; no identifiers beyond optional polite-pool email (`NFR-SEC-004`, `NFR-PRIV-005`) |
| T-15 | The maintainer becomes unavailable | Project cannot release or rotate secrets | Users, contributors | Low | High | Two controls in `GOVERNANCE.md` ([38](38-maintenance-and-support.md) §8): for ordinary absence, a **backup admin** (trusted collaborator with admin rights, named before v1.0) who is an allowed reviewer of the `release` environment, holds one of the two offline updater-key copies, and after the stated absence thresholds activates the handoff state (`HANDOFF_ACTIVE`, which is what lets the gate check accept their approvals), replaces the environment secrets with tokens from their own account and runs releases from the runbook; for death or permanent incapacity, the **GitHub account successor** (an ownership-transfer control GitHub applies on an authorized request; a successor cannot log in or act during a temporary absence). Secrets inventory; runbook with a handoff section |
| T-16 | A program on PATH named `cloudflared` or `ngrok` that is not the author's copy (earlier on PATH, replaced or tampered with) | Reads or forwards the workspace bearer token and every tunnelled request and response | Everything in the workspace | Low, tunnel on only | High | Tunnel off by default and started by the author; before the file first runs the app shows its absolute path and SHA-256 and asks the author to confirm, then records the version, and asks again on any path, hash or version change; execution is bound to the hashed copy (a sealed memfd started with `fexecve` on Linux, an app-held copy elsewhere); the window for a process running as the author's own account is accepted, since it can already read the token; the Agents panel states the exposure; no provider allow-listing (D-065); rotate the token after any doubt (`NFR-SEC-001`, `NFR-SEC-006`, D-072, ADR-0005) |

Evaluation at baseline: highest likelihood × impact are T-01, T-03, T-06, T-07; they receive engineering effort in v0.1–v0.2. T-04, T-12 and T-16 are accepted with documented mitigations because of the no-signing and ChatGPT constraints.

## 3. Security requirements by component

**MCP server (`tlilli-mcp`)**
- Guardrails are enforced server-side, never by prompting: run claim required; target scope check; alternative cap; rationale required; mechanical allow-list from the style sheet; untrusted envelopes; per-run call budget.
- Authentication: stdio transport trusts the parent process; HTTP transport requires `Authorization: Bearer <token>`; token comparison is constant-time; failed attempts are logged and rate-limited (10 per minute).
- Every tool and resource input is schema-validated; strings are length-limited; IDs are validated as ULIDs before any lookup.

**Core**
- No `unsafe`; no `unwrap` outside tests; all parsers run with limits; all file writes go through a temp-file-and-rename path.

**App shell**
- Tauri capabilities are minimal per window; the webview cannot open arbitrary URLs (links open in the OS browser through the `opener` plugin with a confirmation for non-https schemes); no remote content loaded into the webview; CSP set and tested.

**Repository and CI** — see [33](33-ci-cd.md) §7 and [39](39-github-configuration.md).

## 4. Vulnerability disclosure (PR-SEC)

| ID | Rule |
| --- | --- |
| `PR-SEC-001` | `SECURITY.md` at the repo root states: report privately through GitHub private vulnerability reporting; acknowledgement within 7 days; fix or mitigation target 30 days for high, 90 days for others; coordinated disclosure with a GitHub Security Advisory and CVE requested through GitHub. |
| `PR-SEC-002` | Security fixes are released as patch versions on the latest minor and backported to the previous minor within the 90-day support window ([38](38-maintenance-and-support.md)). |
| `PR-SEC-003` | Advisories name the affected versions, the fix version, and the workaround; release notes carry a `Security` section (Keep a Changelog). |
| `PR-SEC-004` | Security issues are never discussed in public issues until the advisory is published; a `type/security` label marks the public follow-up issue afterwards. |
| `PR-SEC-005` | The threat register is reviewed at every gate and whenever a new trust boundary appears (tunnel, Zotero API, new resolver). |
