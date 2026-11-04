# ADR-0005: Sidecar policy and the tunnel exception

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

Tlilli is one binary. The concept and the PRD choose Rust in-process for everything the app does ("one binary; reproducibility", D-037): Typst for PDF, pure-Rust PDF text extraction, `zip` + `quick-xml` for docx, `minijinja` for LaTeX. [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) names the sidecars this avoids: a pandoc sidecar for docx and LaTeX, the Typst CLI, and MuPDF (AGPL, incompatible). `PR-ARCH-004` states the rule: sidecars, external executables bundled with the app, are forbidden by default; an ADR may allow one if it states why no in-process option exists, pins the version, checksums the binary in CI and documents the fallback when it is missing; the v0.5 tunnel (cloudflared or ngrok) is the expected exception and uses the user's installed binary, never a bundled one. Native-code dependencies need their own ADR (`PR-ARCH-002`; ADR-0004 covers SQLite, and ADR-0007 decides `pdfium-render` at gate G3 if pure-Rust extraction falls short, R-16). Installers are budgeted at ≤ 40 MB (`NFR-PERF-010`), and without code signing every shipped executable is one more unsigned artifact for users to trust (D-026, T-12).

The ChatGPT connector needs the exception. OpenAI's custom connectors require a public HTTPS URL and cannot reach a localhost server, so the concept ships "a one-command tunnel (cloudflared or ngrok) guarded by the workspace token", with the caveat that write-capable connectors are limited to some plans (concept "ChatGPT caveats"; R-08, D-038). The PRD specifies it: Settings → Agents → ChatGPT offers a one-command tunnel using the user's installed `cloudflared` or `ngrok`, detected on PATH and never bundled, exposing the HTTP transport under the workspace token, showing the public URL, status, request log and a Stop button, and stopping with the app (`FR-05-050`); off by default, token on every request, URL and one-click stop visible, stops when the app quits (`NFR-SEC-006`); the plan matrix is re-checked at v0.5 start and stated in the product (`FR-05-052`). The threat register accepts T-04 ("anyone on the internet reaches the tunnel URL") with these mitigations plus a per-token rate limit and read-mostly documentation, and `PR-SEC-005` requires a threat review whenever a new trust boundary appears.

The app's own outbound traffic is limited to the allow-listed resolver hosts on author action, visible in Settings (`NFR-SEC-004`, `FR-03-062`, T-14); the Zotero local API host joins the list only while that feature is enabled (`FR-05-041`).

## Decision

**Default: no bundled external sidecars.** The rule is the one in `PR-ARCH-004`: external executables bundled with the app are forbidden by default, the Tauri bundle configuration lists no external binaries, the app downloads no executables, and in-process pure-Rust crates are the first and normal choice ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions), D-037). Three things are not sidecars and need no exception: the project's own binaries, `tlilli-mcp` and `tlilli`, which the Tauri shell may spawn for stdio clients because the in-app and standalone servers share one crate ([PRD 21 §1](../prd/21-architecture-and-tech-stack.md#1-system-shape), ADR-0001); opening links in the OS browser through the `opener` plugin, with a confirmation for non-https schemes ([PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component)); and tools that run only in CI (below). Any other executable the app launches, bundled or found on PATH, is an external sidecar for the purposes of this ADR, because it either moves data across the machine–network trust boundary ([PRD 22 §1](../prd/22-security-and-threat-model.md#1-assets-and-trust-boundaries)) or executes code the project did not build.

**Two classes, two bars.**

| Class | Allowed when | Conditions |
| --- | --- | --- |
| Bundled external executable | An ADR states why no in-process option exists | Version pinned; binary checksummed in CI; fallback when missing documented; license on the `deny.toml` allow-list (`PR-ARCH-003`); size counted against `NFR-PERF-010` (`PR-ARCH-004`) |
| User-installed external executable | An ADR names the feature and the threat rows it touches | Never bundled or downloaded by the app; detected on PATH only; off by default; started by an explicit author action; lifetime bound to the app's; what it does with the author's data stated on its settings page |

Nothing in the first class is approved by this ADR. One item in the second class is: the user-installed tunnel below remains the one approved external exception.

**The tunnel exception (v0.5).** `tlilli-app` may start the user's installed `cloudflared` or `ngrok` as a child process to publish the streamable HTTP transport (ADR-0002), under these conditions. They implement `FR-05-050`, `NFR-SEC-006` and T-04, and conditions 2 and 4 add the controls this ADR decides:

1. Off by default; started from Settings → Agents → ChatGPT by one action; never at launch.
2. Detection by PATH lookup only: no fixed paths, no download, no version pin, because the binary is the user's. The resolved program is a trust boundary: it sees the workspace bearer token and every tunnelled request and response. On first use the app resolves the absolute path and, without executing anything, copies the file into storage the app controls, computing the SHA-256 of the bytes as it copies them; it shows the path and hash and asks the author to confirm, and only then runs the version command and records the path, hash and version. Before every later start it re-resolves the path and makes and hashes a fresh copy before executing anything; it asks for confirmation if the path or hash differs from the record, and once more before the tunnel opens if the reported version differs. Execution is bound to the hashed bytes, not to the path: the version command and the tunnel both run from the copy. On Linux the copy is a sealed `memfd` (`memfd_create` with `MFD_ALLOW_SEALING`, then the write, grow, shrink and seal seals) started with `fexecve`, so nothing can change it between hash and start. On macOS and Windows, and on Linux where memfd execution is disabled (`vm.memfd_noexec`), the copy is a file in the app's per-user data folder that only the author's account can write, and on Windows the app holds it open with a share mode that denies writing and deletion until the child has started. Either way an account that can write the PATH location but not the author's files (a shared `/usr/local/bin` or package-manager prefix, a group-writable directory) cannot swap what runs after the hash. The remaining time-of-check-to-time-of-use window, a process running under the author's own account replacing the copy between hash and start where the OS offers no sealed execution, is an accepted risk: such a process can already read the workspace token from `workspace.sqlite` ([PRD 22 §1](../prd/22-security-and-threat-model.md#1-assets-and-trust-boundaries)), so a tighter binding would not protect the token from it. The Agents panel states the risk in plain words: the tunnel program receives the workspace token and everything sent through the tunnel, so it must be a copy the author installed and trusts. When no binary is found the page says how to install one and that the connector is unavailable until then; that message is the documented fallback.
3. The tunnel forwards to the HTTP transport bound to `127.0.0.1`; the server never changes its bind address. Every request through the tunnel needs the workspace bearer token, checked by the same constant-time comparison, failed-attempt limit (10 per minute) and `Origin` refusal as local HTTP ([PRD 22 §3](../prd/22-security-and-threat-model.md#3-security-requirements-by-component), `NFR-SEC-001`). A per-token request rate limit applies to tunnelled traffic (T-04); the PRD fixes no number, so the v0.5 PR sets one, tests it and states it on the connector page.
4. The public URL, connection status, a request log and a Stop button are visible while the tunnel runs. Lifetime: (a) when the author stops the tunnel or quits the app normally, the app terminates the child process; (b) the tunnel forwards only to the in-process MCP HTTP listener of `tlilli-app`, so if the app crashes or is killed the listener dies with it and the public URL reaches nothing, even if the tunnel process lingers; (c) the app records the child's PID and start time, and at the next launch, before the MCP listener starts, it terminates a surviving process that matches both (the start time guards against PID reuse); on Windows the app can also place the child in a Job Object with kill-on-close, so the OS ends it with the app; (d) a machine power loss ends both processes. The v0.5 tests, with a local HTTPS stand-in for the provider (`FR-05-050` verification), cover normal quit; an app crash or kill followed by the next-launch cleanup; and the listener's death leaving the public URL reaching nothing. The manual G5 step verifies normal quit with ChatGPT.
5. The connector page states the ChatGPT plan matrix and labels the connector read-mostly where write-capable connectors are not available (`FR-05-052`, D-038).
6. `NFR-SEC-004`'s allow-list and the recording-proxy test cover the application's own HTTP client, and both keep holding while the tunnel runs: the app itself opens no connection to the tunnel provider. The tunnel binary's connection to its provider is that process's traffic, started by the author's action, disclosed in the Agents panel while the tunnel runs, and recorded as decision D-065 (pull request 52). The v0.5 verification runs the recording-proxy test with the tunnel off and, with it on, asserts that the app's own requests still reach only allow-listed hosts and that the only other connecting process is the tunnel binary. Threat row T-04 is re-reviewed at G5 (`PR-SEC-005`).

**Future sidecars.** Each needs its own ADR under the bars above, opened as a `gate`-labelled issue. Tools that run only in CI (LibreOffice headless for the docx repair check, a TeX container for `latexmk`; [PRD 34 §3](../prd/34-testing.md#3-what-to-test-by-component), [PRD 33 §1](../prd/33-ci-cd.md#1-workflow-inventory)) are not sidecars: the app never launches them.

## Consequences

### Positive

- The project's own binaries are the only executables shipped: checksums and attestations cover everything users run (D-026, `NFR-SEC-007`).
- Installer size and reproducibility are protected (`NFR-PERF-010`, D-037), and there is no third-party binary provenance to track.
- ChatGPT users reach their own machine without Tlilli hosting anything (non-goal "not a cloud service", `INV-08`).

### Negative

- ChatGPT users install `cloudflared` or `ngrok` themselves and accept that provider's terms.
- The connector depends on two external CLIs whose flags and output the app parses; a provider change can break tunnel start until a patch release.
- Confirming the tunnel program on first use and after every update of it adds a step for ChatGPT users, and every start copies the program (tens of MB) before running it.
- PDF text extraction stays pure Rust until ADR-0007 decides otherwise; quality on difficult PDFs may lag tools that bundle a renderer (R-16).

### Risks

- T-04 remains accepted, not removed: a leaked token plus a running tunnel exposes the workspace. The mitigations are the ones listed; the author sees the URL and can stop the tunnel and rotate the token.
- An author forgets a running tunnel: stop-with-app and the next-launch cleanup bound the window to the app's lifetime, and the status stays visible in the Agents panel.
- A program named `cloudflared` or `ngrok` that is not the author's copy (earlier on PATH, replaced or tampered with) would see the token and all tunnelled traffic; the token does not protect against it. The path-and-hash confirmation in condition 2 makes any change visible before the file runs, running the hashed copy keeps a later swap of the file from taking effect, and the Agents panel states the risk; the same-account window that condition 2 accepts remains. This boundary is not yet a row in the threat register ([PRD 22 §2](../prd/22-security-and-threat-model.md#2-threat-register)); adding one is part of the threat review `PR-SEC-005` requires when the tunnel appears.

## Alternatives considered

- **Bundle `cloudflared` or `ngrok`.** Rejected by `PR-ARCH-004` and D-037; it would also ship a third-party binary under the zero-signing posture (T-12) and break the size budget.
- **Implement a tunnel client in-process.** Rejected: the providers' protocols are theirs to change; the PRD names their CLIs, not their protocols.
- **A Tlilli-hosted relay.** Rejected: "not a cloud service" ([PRD 01 §3](../prd/01-vision-and-scope.md#3-non-goals-explicitly-out-of-scope)), `INV-08`, `NFR-PRIV-001`.
- **No ChatGPT support.** Rejected: the concept and `FR-05-050` ship the connector at v0.5, read-mostly where plans require.
- **Sidecars for export (pandoc, Typst CLI) or PDF (MuPDF).** Rejected in [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions): in-process crates exist, and MuPDF's license is incompatible.

## References

- Concept document: "What it is not", "Architecture", "Skill pack and agent integration" (ChatGPT row and caveats).
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §1, §3, §5 (`PR-ARCH-002..004`), §6; [22](../prd/22-security-and-threat-model.md) §1–§3; [14](../prd/14-fr-v0.5-beyond-the-article.md) §14.6; [20](../prd/20-non-functional-requirements.md) NFR-SEC, `NFR-PERF-010`; [40](../prd/40-roadmap-and-gates.md) §1 (v0.5 deliverable "tunnel ADR exception"), G5 step 5.
- Requirements: `INV-08`; `FR-03-062`, `FR-05-041`, `FR-05-050..052`; `NFR-SEC-001`, `NFR-SEC-004`, `NFR-SEC-006`, `NFR-SEC-007`; `NFR-PERF-010`; `NFR-PRIV-001`; `PR-ARCH-002`, `PR-ARCH-003`, `PR-ARCH-004`; `PR-SEC-005`.
- Decisions, risks, threats: D-026, D-037, D-038, D-065 (pull request 52); R-08, R-16; T-03, T-04, T-12, T-14; ADR-0001, ADR-0002, ADR-0004, ADR-0007 (reserved).
