# Tlilli

Tlilli is a local-first desktop editor for scientific manuscripts. The author writes in black ink. An external agent, connected over the Model Context Protocol (MCP), proposes in red ink: suggestions, comments and a short list of allow-listed mechanical edits. The author decides what turns from red to black, and the manuscript remembers which was which.

The name is Nahuatl for black ink. The documentation uses three Nahuatl terms and no others: **Tlilli** (the application), **Tlapalli** (the red-ink suggestion layer) and **amoxtli** (a manuscript). Everything else is plain English.

!!! note "Status: pre-alpha"
    Tlilli is in Phase 0 (foundation). There is no release and nothing to install yet. The phases, their exit criteria and the gate tests are in [40 Roadmap and gates](prd/40-roadmap-and-gates.md).

## Documentation

The site follows [Diátaxis](https://diataxis.fr/): every page is one of four kinds and the kinds are not mixed (`PR-DOC-005`). The front-door links promised by PRD 35 §2 (first tutorial, agent setup, download) appear here as their pages land.

| Section | Kind | Answers |
| --- | --- | --- |
| [Tutorials](tutorials/index.md) | Learning | "Take me through my first manuscript, step by step." |
| [How-to guides](how-to/index.md) | Tasks | "How do I install, connect an agent, export, verify a download?" |
| [Reference](reference/index.md) | Information | "What exactly does this tool, schema, command or shortcut do?" |
| [Explanation](explanation/index.md) | Understanding | "Why two inks, why no prompt box, where is the trust boundary?" |

## For contributors and agents

- [Requirements](prd/README.md): the product requirements document (PRD). Every issue, pull request and gate cites it.
- [Developer documentation](dev/index.md): setup, running CI locally, review severity, release runbook, agent playbook, and the GitHub settings record.
- [Gate scripts](gates/index.md): the acceptance script of each phase, G0 to G6, followed literally at its gate (PRD 40 §3).
- [API documentation](https://bioedca.github.io/Tlilli/api/): rustdoc for the Rust crates, built with `cargo doc --workspace --no-deps` and published under `/api/` (PRD 35 §1).
- [Source repository](https://github.com/bioedca/Tlilli) on GitHub.
