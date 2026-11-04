# Explanation

Explanation pages are for understanding: why Tlilli works the way it does, what the alternatives were and what the design protects. They discuss and connect; they do not instruct (see [How-to guides](../how-to/index.md)) and they are not the specification (see [Requirements](../prd/README.md)).

PRD 35 §2 names the pages and `FR-10-020` requires the quadrant to be complete at v1.0:

- **Ink and provenance**: black ink, red ink, and why the manuscript remembers which was which (`INV-01`, the author holds the pen).
- **The turn protocol**: how an agent run starts, proceeds and ends ([11 FR v0.2](../prd/11-fr-v0.2-red-ink.md)).
- **Why there is no prompt box**: the editor has no chat; the agent works through the MCP server.
- **The trust boundary**: the MCP server is the only door for agents, and text from sources, PDFs and reviewers is untrusted input ([22 Security and threat model](../prd/22-security-and-threat-model.md)).
- **Architecture**: `tlilli-core` owns the document; the UI and the MCP server only emit events ([21 Architecture and tech stack](../prd/21-architecture-and-tech-stack.md)).
- **Span anchoring**: how suggestions stay attached to text that moves.
- **Local first**: nothing leaves the machine unless the author sends it.
- **Agent agnostic**: Claude Code, Codex, ChatGPT and any other MCP client.
- **[Built with agents](built-with-agents.md)** (`PR-DOC-014`): how the project uses AI agents and reviewers, what the human reviews, and the DCO stance.

Design decisions and their alternatives are recorded as ADRs (`docs/adr/`, bootstrap task 16, `PR-DOC-009`), which render as a separate section.
