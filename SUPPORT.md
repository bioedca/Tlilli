# Support

Tlilli is pre-alpha (Phase 0): there is no release to install yet, and one maintainer with AI agents runs the project. The commitments below are honest targets, not a service-level agreement ([PRD 38](docs/prd/38-maintenance-and-support.md)).

## Where to ask

| Need | Channel |
| --- | --- |
| A question about using Tlilli or connecting an agent | GitHub Discussions, Q&A category, once Discussions open at v0.2; until then the **Question** form in the [issue chooser](https://github.com/bioedca/Tlilli/issues/new/choose), which labels the issue `type/question` (blank issues are off) |
| A gap, error or unclear page in the documentation | The **Documentation** form in the issue chooser |
| A bug | The bug report form under Issues; one problem per issue |
| A feature, or a change to the agent protocol or a skill | The feature, protocol-change or skill-change form |
| A security problem | Never an issue: see [SECURITY.md](SECURITY.md) |

There is no email or chat support (`PR-MNT-006`).

## What is supported

| Area | Policy |
| --- | --- |
| Releases | 0.x: only the latest 0.x release; fixes ship as the next patch or minor, no backports. From v1.0: the latest minor receives all fixes; security fixes are backported to the previous minor for 90 days after the newer minor's release |
| Operating systems | macOS 13+, Windows 10 22H2+ and Windows 11, Ubuntu 22.04+ (glibc 2.35+) and equivalent distributions; the floor rises only in a minor, with a changelog entry and a one-minor warning in the app |
| Agents | Claude Code and Codex CLI, current stable releases; ChatGPT per the plan matrix documented at v0.5; other MCP clients should work, with the contract tests as the reference |
| Workspace formats | Every schema version ever released opens and migrates forward |
| Downloads | Unsigned binaries verified by checksums and attestations ([PRD 37 §4](docs/prd/37-releases-and-packaging.md)); the install pages document the operating-system prompts |

## Response targets

| Item | Target |
| --- | --- |
| New issue triaged (labels, priority, milestone) | within 7 days (weekly triage) |
| Security report acknowledged | within 7 days |
| `priority/P0` (data loss, invariant violation, high-severity security) | fix PR within 7 days of confirmation; patch release on merge |
| `priority/P1` | fixed within the current phase or minor |
| `priority/P2`, `priority/P3` | best effort; re-evaluated at each gate |

## Producing diagnostics

From v0.1 the app keeps everything local and sends nothing automatically (D-033):

- **Copy diagnostics** in Settings produces a redacted bundle (versions, OS, log tail, schema version, run summaries) in one click. Redaction removes manuscript text, source full text and paths under your home directory, and you see the bundle before copying. Attach it to the bug form.
- **Logs** are JSON lines in `<workspace>/logs/`, rotated daily and kept 14 days; they never contain manuscript text at the default level.
- **Crash reports** are written to `<workspace>/crashes/<timestamp>.txt`; the next launch offers to open the bug form with the report.
- The maintainer never asks for your manuscript. If a reproduction needs a document, use a fixture manuscript or a canonical export you have redacted, shared through a private channel you choose.
