# Security policy

Tlilli is a local-first desktop application: the manuscript, its sources and the workspace token stay on the author's machine unless the author sends them somewhere, and the MCP server is the only door for agents. A weakness in that boundary (the pen rule, the untrusted-text labelling, the localhost token, the parsers, the updater, the release pipeline) is a security issue. The threat model is [PRD 22](docs/prd/22-security-and-threat-model.md).

## Reporting a vulnerability

Report privately through **GitHub private vulnerability reporting**: open the repository's [Security tab](https://github.com/bioedca/Tlilli/security) and choose "Report a vulnerability" ([direct link](https://github.com/bioedca/Tlilli/security/advisories/new)). The report reaches the maintainer only.

Do not open a public issue, pull request or discussion for a security problem, and do not use the issue forms (`PR-SEC-004`, `PR-ISS-006`). A redacted diagnostics bundle helps; your manuscript is never needed.

## What to expect

| Step | Target |
| --- | --- |
| Acknowledgement | within 7 days |
| Fix or mitigation, high severity (data loss, author text changed by an agent, the local server reachable without its token, key or token exposure) | 30 days |
| Fix or mitigation, other severities | 90 days |
| Disclosure | coordinated with the reporter; a GitHub Security Advisory is published with the fix and a CVE is requested through GitHub |

These are a solo maintainer's commitments, not a service-level agreement ([PRD 38 §2](docs/prd/38-maintenance-and-support.md)). Advisories name the affected versions, the fix version and the workaround; release notes carry a "Security" section. After the advisory is published, a public issue labelled `type/security` tracks any follow-up.

## Supported versions

| Version | Supported |
| --- | --- |
| Pre-alpha (no release yet) | Reports against `main` are welcome; there is nothing to patch |
| 0.x (from v0.1.0) | Only the latest 0.x release; fixes ship as the next patch or minor, no backports |
| 1.x and later | The latest minor receives all fixes; security fixes are backported to the previous minor for 90 days after the newer minor's release |

## Scope notes

- Prompt injection through source PDFs and reviewer text is a known threat (T-01): Tlilli labels that text untrusted and the write tools cannot reach outside the run's scope. A way for injected text to change author text, or to make a tool write outside its scope, is a high-severity report.
- The ChatGPT tunnel (v0.5) exposes the local server over HTTPS behind the workspace token by design; a tunnel report is in scope when the token can be bypassed.
- Downloads are not code-signed (D-026). Verify them with the published checksums and `gh attestation verify <asset> --repo bioedca/Tlilli`; a mismatch is a security report.
