# Tlilli — Concept & Definition

Nov 3, 2026 · @Eduardo

## Name: Tlilli

Tlilli (TLEE-lee) is the recommended name: Nahuatl for black ink, the author's ink in the codex tradition. In Nahuatl the paired phrase *in tlilli in tlapalli*, "the black ink, the red ink", stood for writing itself and the knowledge it carried; the sages were described as the ones who possessed the black and red ink.

The pairing is the product. Black ink is what the author wrote. Red ink (**Tlapalli**, tla-PAL-li) is what the agent proposes. Accepting a proposal turns red to black, and the manuscript remembers which was which, so provenance is built into the name rather than bolted on.

Nahuatl stays to three terms so the interface is learnable: **Tlilli** (the app), **Tlapalli** (the suggestion layer), **amoxtli** (a manuscript, literally a codex). Everything else is plain English.

| Candidate | Say it | Meaning | Why it fits | Collision check |
| --- | --- | --- | --- | --- |
| **Tlilli** (recommended) | TLEE-lee | black ink; with *tlapalli*, writing and knowledge | author's ink vs agent's red ink; provenance in the name | no software hit found; only phonetic neighbours ("Tilli", "Tili"), unrelated kids' and social apps |
| Tlacuilo | tla-KWEE-lo | scribe-painter of the codices | the Nahuatl "Scrivener"; names the author's role | a small iOS book-sharing app used it (App Store id 1557794923, no longer listed as of 2026-11-07); the word is common in Mexican cultural projects |
| Amoxtli | ah-MOSH-tli | book, codex | the manuscript as codex | not exhaustively checked; common in library and heritage projects |
| Amatl | AH-matl | bark paper the codices were painted on | short, brandable | taken: an MIT-licensed Go CLI that renders Markdown to documents ([pkg.go.dev](https://beta.pkg.go.dev/github.com/Bornholm/amatl)) |

Code names: repo `tlilli`, core crate `tlilli-core`, MCP server `tlilli-mcp`, skills `tlilli-*`, workspace folder `*.tlilli`. A trademark search is still open (see Open questions).

## Concept

Tlilli is a local desktop manuscript editor that turns any MCP-capable coding agent into a disciplined scientific co-editor: strict turns, every change anchored to a sentence, attributed to whoever wrote it, and reversible.

The app owns four things the agent needs and a chat window never has: the manuscript as structured, addressable text (sections, blocks, sentence spans with stable IDs); the citation ledger (sources, full text, claim links); the style sheet; and the run history. The agent connects over MCP, reads these as resources, pulls the queue of marked-up requests, and writes back through a narrow set of tools that can only produce suggestions, comments, verified citations and a short list of mechanical fixes. The author is the only one who holds black ink.

What it is not:

- Not a chat with a document attached. There is no prompt box; work is marked up in the text and sent as a batch.
- Not a model host. No API keys, no model picker. Whatever agent subscription the author already pays for does the thinking.
- Not a reference manager. It keeps a per-manuscript ledger and imports from PDFs, identifiers and, later, Zotero.
- Not a cloud service. Data stays in a local workspace folder; the agent's own network calls are the only traffic.

Document types on one engine: research article, reviewer response, cover letter. A workspace holds many manuscripts and an optional shared source pool. Open source from the first public release.

## Design principles

Each of the four pains you named maps to one rule the software enforces, not a guideline the agent is asked to follow.

| Pain today | Principle | In the product |
| --- | --- | --- |
| Lost context between pastes | The manuscript is the context | The agent reads the whole manuscript, style sheet and ledger as MCP resources; each request arrives with its anchor and section. Nothing is re-explained. |
| Re-explaining sources | Sources are objects, not strings | A source carries metadata, full text when available and claim links. The agent reads the supporting passage, not its memory of the paper. |
| Unrequested rewrites | Red ink only where asked | Write tools accept only targets inside the run's queue or a standing-check scope. Anything else the agent wants to say lands as a comment. Direct edits are a short allow-list. |
| No audit trail | Every run is a ledger entry | A run freezes the queue, snapshots the manuscript, logs every tool call and ends with a report. Rollback is one action. |
| (all four) | Author holds the pen | Suggestions become text only on accept; accepted text records its origin, run and agent. |
| (all four) | Agent-agnostic by contract | The MCP surface and the skill pack are the product. The app never prefers a model. |
| (all four) | Local-first | SQLite and files in one folder, no telemetry, works offline. |

## A working session

One cycle takes minutes: mark up, send, review. Here is Run 7 on the Introduction of a riboswitch paper.

1. **Author turn.** Select sentence 3 → `paraphrase`, note "too close to the review's wording". After paragraph 2, add an idea stub: *antiterminator forms only on uncharged tRNA; bridge to why kinetics matter — cite the 2019 structure; hedged; one sentence*. On paragraph 4, a comment with no tag: "reads like Results, move the mechanism detail?" Standing checks (citation verification, consistency sweep) are on for the Introduction.
2. **Send.** Tlilli opens Run 7: snapshot taken, queue frozen (3 requests + 2 checks), manuscript read-only until the run closes. Status chip: *agent's turn*.
3. **Agent turn** (in Claude Code, `/tlilli-run`). `run_claim` → `queue_list` → reads the Introduction, style sheet and ledger as resources. Paraphrase: `suggest_replace` with three alternatives that differ in strategy (restructure, change the verb, split in two), each with a one-line rationale. Stub: a ledger search finds the 2019 structure, `fulltext_search` pulls the passage, `suggest_replace` on the stub with two drafts, each carrying a claim link. Untagged comment: the agent reads it as a move request, answers with `suggest_move`, and says in a comment what it understood. Checks: `claim_link_set` marks one existing citation *partially supported* ("source reports a 10-fold reduction; sentence says 'abolishes'") and attaches a hedged alternative. `run_report` closes the turn.
4. **Review turn.** The review pane lists six items. Alternative B for the paraphrase, edited by one word, accepted → black ink, origin Run 7. Draft 1 for the stub accepted; its claim link is now verified. The move rejected with a redo comment, "keep it here, cut the last two sentences" → queued for Run 8. The hedge accepted. Run 7 closes; its diff and report stay in history.

## Domain model

Everything the agent can see or touch is one of these objects, and the third column is the pen rule: who may create it.

| Object | Holds | Created by |
| --- | --- | --- |
| Workspace | manuscripts, optional shared source pool, agent connections, settings | author |
| Manuscript | type (article, reviewer response, cover letter), sections, style sheet, ledger, runs, snapshots | author |
| Section | ordered blocks; role (Abstract, Introduction, Results, Discussion, Methods, Legends, custom) | author |
| Block | paragraph, idea stub, heading, figure, table, caption, equation; stable ID | author; agent only through an accepted suggestion |
| Span | one sentence inside a paragraph; stable ID preserved across edits by diff-anchoring | derived by the core |
| Request | a tagged action or free comment on a span, block, section, figure, source or suggestion; queued for the next run | author |
| Idea stub | notes, cite hint, tone hint, target length, level (sentence or paragraph) | author |
| Suggestion (red ink) | kind (replace, insert, delete, move), target, 1–3 alternatives, rationale, claim links, status (open, accepted, rejected, redo) | agent |
| Mechanical edit | an allow-listed direct change (citation format, first-use abbreviation, renumbering), logged and revertable per run | agent |
| Comment | body, kind (rationale, check, question), severity, target | both |
| Run | snapshot before and after, frozen queue, agent identity, tool-call log, report, status | app |
| Snapshot | immutable manuscript state; diffable | app |
| Source | identifier (DOI, PMID, arXiv, URL), CSL-JSON metadata, PDF, extracted full text, status (resolved, proposed, unresolved) | author; agent as *proposed* |
| Claim link | span ↔ source ↔ quoted passage + locator ↔ verification status ↔ run last checked | both |
| Style sheet | journal and limits, tense and person per section, abbreviations, terminology, citation style, auto-fix list, locked spans | author |
| Provenance mark | per span: author, agent-accepted (run, alternative, edited before accept), agent-mechanical, mixed | app |
| Figure asset | image files, panels, caption block, in-text references | author |

## Turn protocol

The run is the unit of trust: one open run per manuscript, every write inside it, everything it did kept.

&#91;embedded content: turn protocol · 4 states, 1 escape\]

The dashed path is the only way out mid-run: a cancel, or a run that passes its timeout (default 30 minutes without a heartbeat), rolls back mechanical edits and keeps any suggestions already written as open red ink.

**Rules**

- One open run per manuscript. The manuscript is read-only to the author while a run is open; comments typed during a run queue for the next one.
- Every write tool requires a claimed run and a target inside the frozen queue or a standing-check scope. Other targets are refused with the hint to use a comment.
- The run report, the full tool log and the before and after snapshots are kept and diffable.

| Agent action | Lands as | Author sees |
| --- | --- | --- |
| Content rewrite (paraphrase, tighten, expand, formalize, hedge, strengthen, stub to prose) | suggestion, 2–3 alternatives | side-by-side cards; pick, edit, accept or reject |
| Structural (split, merge, reorder, move, restructure) | suggestion, one proposal | before and after view of the affected blocks |
| New citation or new source | suggestion plus a ledger entry in *proposed* state | the sentence with its marker, the source card and the quoted passage |
| Verification result | comment with severity; any fix is a separate suggestion | a flag on the citation; rationale in the margin |
| Mechanical (citation format, first-use abbreviation, figure and reference renumbering, style-sheet auto-fixes) | direct edit, logged | a per-run list of mechanical changes; revert all or each |
| Anything outside the queue | comment only | a margin note, routable to the next run in one click |

## Author-side markup

Markup is the only way to talk to the agent: select, tag, optionally note, send. There is no prompt box.

| Level | Actions | Lands as |
| --- | --- | --- |
| Sentence | paraphrase, tighten, expand, formalize, split, merge, cite, hedge, strengthen | suggestion with alternatives (split and merge: one proposal) |
| Paragraph | fix flow, strengthen topic sentence, reorder sentences, cut to N words, expand a paragraph stub | suggestion |
| Section | restructure, check logic chain, check journal conventions, draft from outline | restructure and draft as suggestion; checks as comments |
| Document | consistency sweep (numbers in abstract vs results, abbreviations, tense, terminology, figure references, limits), citation verification | comments plus allow-listed mechanical edits |

**Idea stubs.** A stub is a dashed block holding what you want to say before you know how. Fields: notes (required), cite hint ("the 2019 cryo-EM structure", a DOI, or "find one"), tone (hedged, assertive, general reader), target length (one sentence, two, about N words), level. A paragraph stub takes an argument order ("X, then Y, then Z") and comes back as one sentence span per claim, each with its cite hint resolved or flagged. The stub stays in place until a draft is accepted, so rejecting every alternative loses nothing.

**Comments.**

- Free text with an optional tag. Tagged comments route as actions; untagged ones the agent interprets, and it must state its reading in the rationale.
- Targets: a span, block, section, figure, source, or a suggestion.
- A comment on a suggestion sets it to *redo*; the next run must answer it with a new alternative and keep the earlier ones.
- A span marked *do not touch* is read-only to the agent and shows as locked in the resources it reads.

**Keyboard.** Select → Cmd/Ctrl-K → tag (fuzzy) → optional note → Enter. Send is one key and shows the count of queued items.

## Citation ledger

A citation is a claim link: a sentence, a source, and the passage that supports it. The agent verifies links, not a bibliography.

**Sources.**

- Added by identifier (DOI, PMID, PMCID, arXiv): metadata resolved to CSL JSON through Crossref, PubMed and arXiv. Added by PDF drop: text extracted locally, DOI sniffed from the first pages, metadata resolved. Later: import from Zotero (Better BibTeX export or the local API).
- Full text kept locally when a PDF exists or open-access text is available (Europe PMC, Unpaywall). Paywalled papers need your PDF.
- Deduplicated by DOI; status resolved, proposed or unresolved. A workspace may hold a shared pool that manuscripts reference.

**Claim links** hold the quoted passage (at most two sentences), a locator (page or section), a verification status, the rationale and the run that last checked it.

| Status | Meaning | Agent's required follow-up |
| --- | --- | --- |
| supported | the passage states what the sentence asserts | none |
| partially supported | same direction, different strength or scope | comment + hedged alternative |
| unsupported | the passage is about something else | comment + search for a better source |
| contradicted | the passage says the opposite | comment at high severity; suggest removal or reversal |
| unverifiable | no full text available | comment asking for the PDF |

Verification runs as a standing check on touched sections every run, or on the whole manuscript on demand.

**New sources.** The agent searches the ledger first, then its own literature servers (PubMed, Semantic Scholar, Scite, bioRxiv) through the agent's MCP configuration; Tlilli ships the ledger, not search. A proposal must carry an identifier and a candidate passage, lands as *proposed*, and becomes a real source only when you accept the suggestion that uses it.

**Outputs.** CSL JSON is canonical. BibTeX export. The reference list renders in any CSL style (citeproc in the core) for docx, LaTeX and PDF export. In-text markers are stored as `[@key]` and rendered numeric or author-year per the style sheet.

## Figures, tables, methods, reviewer response, cover letter

Figures are blocks with assets, and the agent can see them.

- A figure block holds image files, panel labels, a caption block and the list of in-text references.
- Agent actions: write or revise captions (suggestion); check text–figure consistency as comments (every referenced panel exists, numbers in the text match the caption, figure order equals order of first mention), with renumbering as a mechanical edit; read the image through an MCP image resource to describe or verify it; propose a new order (suggestion).
- Tables: cells readable as a resource; the agent flags unit and decimal inconsistencies and caption mismatches.

**Methods from protocols.** A protocol file (Markdown, docx, PDF) imports into a Materials pane. A stub such as "methods: SEC-MALS as in protocol X" is drafted from the protocol text with a provenance link back to it. Checks: every method named in Results has a Methods paragraph; reagent and instrument names are consistent throughout.

**Reviewer response.** Reviewer text imports as comment blocks; each gets a response block and a link to the manuscript spans changed in reply. The agent drafts responses as suggestions and checks that every promised change exists in the manuscript.

**Cover letter.** A document type with the journal's style sheet, drafted as a suggestion from the abstract and a significance stub.

**Many manuscripts.** A workspace holds any number of manuscripts; a shared source pool is optional, and each manuscript's ledger references it.

## Style sheet and provenance

The style sheet is the standing instruction set; provenance is the ink record. Both are resources the agent reads every run.

**Style sheet, one per manuscript.**

| Field | Example | Enforcement |
| --- | --- | --- |
| Target journal and limits | abstract 150 words, main text 4,500, 60 references, 6 figures | sweep comments; live counters in the editor |
| Tense and person per section | Methods past passive; Results past; Discussion present | sweep comments |
| Abbreviations | define once; list of term → short form | first use auto-fixed if marked auto; otherwise a comment |
| Terminology | preferred and forbidden terms ("riboswitch", never "RNA switch") | suggestion inside a request; comment elsewhere |
| Hedging policy | claims stronger than "suggests" need a supported claim link | verification comments |
| Citation style | a CSL file; numeric or author-year | mechanical formatting |
| Auto-fix list | which mechanical kinds the agent may apply directly | server-side allow-list |
| Locked spans | text the agent may not touch | writes refused |

**Provenance ("ink").** Every span records one of: author (black); agent-accepted (red turned black, with run, alternative chosen and whether you edited it before accepting); agent-mechanical; or mixed, once you edit accepted text. A *show ink* toggle tints the manuscript by origin. Export produces a provenance summary per section (share of words that originated in a suggestion, runs, agent identities) and a draft AI-use disclosure paragraph you edit before submission.

## Architecture

A Tauri 2 desktop app with a Rust core that is the single source of truth; the MCP server is the only door, and the agent stands outside it.

&#91;embedded content: architecture · desktop app, MCP boundary, external agent\]

The UI and the MCP server both talk to the core through the same event API, so an author edit and an accepted suggestion are the same kind of change in the log. Literature search belongs to the agent's own MCP configuration, not to Tlilli.

| Layer | Choice | Why |
| --- | --- | --- |
| Shell | Tauri 2 | native window, small binary, Rust backend in-process; macOS, Windows, Linux |
| Core | `tlilli-core` crate: document model (ULID blocks and spans), append-only event log with materialized snapshots, ledger, style sheet, provenance, export | one source of truth; every change is an event, so runs, diffs and rollback cost nothing extra |
| Storage | one workspace folder: `workspace.sqlite` (rusqlite), `sources/` PDFs and extracted text, `figures/`, `exports/`; `tlilli export --canonical` writes JSON for git | local-first, portable, inspectable |
| Editor | ProseMirror in the webview with a schema mirroring blocks and spans; transactions map to core events; suggestions and comments drawn as decorations | mature structured editing; the view never owns the truth |
| MCP server | `tlilli-mcp` on the official Rust MCP SDK; stdio (launched per client) and streamable HTTP on localhost with a per-workspace token | Claude Code and Codex use either; HTTP is what a tunnel exposes for ChatGPT |
| Text processing | rule-based sentence segmentation seeded by the style sheet's abbreviation list; diff-anchored ID preservation; PDF text extraction; DOI sniffing | all local, no model needed |
| References | CSL JSON canonical; citeproc in Rust for rendering; BibTeX export | any journal style |
| Export | docx with comments (open suggestions as tracked changes later); LaTeX with a .bib; PDF through Typst | co-authors, submission, print |
| Import | docx paragraphs and comments; Markdown; basic LaTeX | start from an existing draft |

## MCP surface

The server exposes read resources, a small set of write tools that can only produce red ink, and prompts that carry the workflow to clients without skills. Every write needs a claimed run and a target inside the queue or the standing-check scope; anything else is refused with a hint to comment instead.

**Tools**

| Tool | Purpose |
| --- | --- |
| `run_claim(manuscript_id)` | take the open run; returns run id, snapshot id, queue summary and a style-sheet digest |
| `run_heartbeat(run_id)` | keep the run alive past the timeout while working |
| `run_report(run_id, summary, done[], skipped[], warnings[])` | close the agent turn |
| `manuscript_outline(manuscript_id)` | sections, blocks and spans with ids and first words |
| `read_blocks(ids[], with_annotations, with_provenance)` | text with span ids and locks |
| `queue_list(run_id)` | requests: target, tag, note, stub fields, status |
| `search_text(manuscript_id, query)` | find spans by text |
| `suggest_replace(run_id, request_id, target, alternatives[])` | 1–3 alternatives, each with text, rationale and claim links |
| `suggest_insert(run_id, request_id, after, alternatives[])` | a new sentence or block |
| `suggest_delete(run_id, request_id, target, rationale)` | removal as a proposal |
| `suggest_move(run_id, request_id, block_ids[], destination, rationale)` | a structural change |
| `comment_add(run_id, target, body, kind, severity)` | rationale, check result or question |
| `request_resolve(run_id, request_id, outcome, note)` | done, needs author, or skipped |
| `apply_mechanical(run_id, kind, changes[])` | allow-listed direct edits only; refused for any other kind |
| `source_resolve(identifier)` | metadata lookup and duplicate check; no write |
| `source_propose(run_id, identifier, reason, passage)` | ledger entry in proposed state |
| `fulltext_search(source_id or all, query)` | passages with locators |
| `claim_link_set(run_id, span_id, source_id, quote, locator, status, rationale)` | create or re-verify a link |
| `figure_check(run_id, manuscript_id)` | computed panel, number and order mismatches |

**Resources**

| URI | Content |
| --- | --- |
| `tlilli://manuscript/{id}` | canonical JSON of the whole manuscript |
| `tlilli://manuscript/{id}/section/{sid}` | Markdown with span-id markers |
| `tlilli://manuscript/{id}/style-sheet` | the style sheet |
| `tlilli://manuscript/{id}/ledger` | sources and claim links |
| `tlilli://source/{id}/fulltext` | extracted text, labelled untrusted |
| `tlilli://source/{id}/pdf` | the PDF |
| `tlilli://figure/{id}/image` | image content for vision-capable clients |
| `tlilli://run/{id}/queue` | the frozen queue |
| `tlilli://manuscript/{id}/history/{snapshot}` | a past state |

**Prompts.** `run`, `revise-section`, `verify-citations`, `consistency-sweep`, `draft-from-stubs`, `reviewer-response` mirror the skills, so a client that cannot install skills (ChatGPT) still gets the workflow.

**Guardrails enforced by the server, not by prompting.** Write tools require a claimed run; targets outside scope are refused; at most three alternatives; a rationale is required; mechanical edits are limited to the style sheet's allow-list; text from sources and reviewers is labelled untrusted in every resource; the connection token is per workspace and revocable.

## Skill pack and agent integration

One set of Markdown skill sources builds every client's package, so the agent learns the protocol once and `tlilli skills install --claude-code | --codex | --chatgpt` writes the right files.

| Skill | Teaches |
| --- | --- |
| `tlilli-run` | the whole turn: claim, read style sheet and queue, work each request, run standing checks, report |
| `tlilli-revise` | alternatives that differ in strategy, not synonyms; preserve voice and claim links; one-line rationale |
| `tlilli-stub` | expand stubs honoring cite, tone and length hints; one claim per sentence; flag unresolvable hints |
| `tlilli-cite` | ledger first, then the agent's own literature servers; never propose without an identifier and a passage |
| `tlilli-verify` | the five statuses, the comment format, the fix required for each status |
| `tlilli-sweep` | the consistency checklist and what is auto-fix versus comment |
| `tlilli-figures` | caption conventions, reading images, the consistency checks |
| `tlilli-response` | reviewer responses and cross-links to the spans that changed |
| `tlilli-style` | reading and applying the style sheet; treating source and reviewer text as data, not instructions |

| Agent | MCP connection | Skills | When |
| --- | --- | --- | --- |
| Claude Code | `claude mcp add tlilli -- tlilli-mcp stdio`, or `.mcp.json`; HTTP also works | SKILL.md folders in `.claude/skills/` or `~/.claude/skills/`; `/tlilli-run` | v0.2 |
| Codex CLI | `[mcp_servers.tlilli]` in `~/.codex/config.toml`, stdio | a generated `AGENTS.md` section, plus the skills folder where Codex supports one | v0.2 |
| ChatGPT (web and desktop) | Developer-mode custom connector; needs a public HTTPS URL, so Tlilli ships a one-command tunnel (cloudflared or ngrok) guarded by the workspace token | MCP prompts carry the workflow; no skill install | v0.5, with the caveats below |

**ChatGPT caveats**, from OpenAI's current connector rules: a custom MCP server must be reachable over public HTTPS and cannot be a localhost server ([Boomi setup guide](https://help.boomi.com/docs/Atomsphere/Platform/Connect_chatgpt_setup), [InfoQ](https://www.infoq.com/news/2025/10/chat-gpt-mcp)), and write-capable custom connectors are limited to Business, Enterprise and Education plans, with Plus and Pro restricted to read-only connectors ([Boomi setup guide](https://help.boomi.com/docs/Atomsphere/Platform/Connect_chatgpt_setup)). Re-check the plan matrix when v0.5 starts; it has moved several times.

## Roadmap

Six phases, each closed by a gate you can test on your own manuscript; no dates until v0.1 ships and the pace is known.

&#91;embedded content: roadmap · 6 phases, a gate on each\]

The diamonds are the gates: a phase ends when its test passes on a real manuscript, not when its features are merged.

- **v0.1 Black ink.** Tauri app, document model with stable IDs, sections, blocks, spans, comments with tags, idea stubs, snapshots, Markdown and basic docx import. No agent yet.
- **v0.2 Red ink.** `tlilli-mcp` over stdio and HTTP, run lifecycle, the `suggest_*` tools, review pane, redo comments, run log, provenance marks; `tlilli-run`, `tlilli-revise`, `tlilli-stub`; Claude Code and Codex CLI.
- **v0.3 Ledger.** Sources by DOI, PMID and PDF, full text, claim links, the verification pass, proposed sources, `tlilli-cite` and `tlilli-verify`, CSL JSON and BibTeX export.
- **v0.4 Sweep and style.** Style sheet, consistency sweep, mechanical auto-fixes, figures (captions, consistency, image resource), docx with comments, LaTeX, PDF through Typst.
- **v0.5 Beyond the article.** Methods from protocols, reviewer response, cover letter, shared source pool, Zotero import, ChatGPT connector through the guarded tunnel plus MCP prompts.
- **v1.0 Public.** Installers for macOS, Windows and Linux, documentation site, `tlilli skills install`, a sample manuscript, license and contribution guide.

## Open questions and risks

The calls below are mine; each is reversible until its phase starts.

| Question or risk | Why it matters | Current call |
| --- | --- | --- |
| Manuscript read-only while a run is open | Strict turns need a coherent snapshot; a run that takes 20 minutes locks you out | Accept it; runs are scoped and short, comments typed during a run queue for the next one. Revisit if runs routinely exceed 10 minutes |
| Span IDs surviving heavy author edits | Comments, claim links and provenance all hang on span IDs | Diff-anchored re-segmentation in the core, tested on real revision histories before v0.2 |
| Two document models (Rust truth, ProseMirror view) | Drift between them corrupts anchors | Rust is the only truth; the editor emits transactions that map 1:1 to core events; no state lives only in the view |
| ChatGPT reachability and plan limits | Public HTTPS required; write tools need Business, Enterprise or Education plans | Ship a guarded tunnel; document ChatGPT as read-mostly on individual plans until OpenAI changes the matrix |
| Full text for claim-level verification | Paywalled papers have no text to check against | Status *unverifiable* plus a comment asking for the PDF; Europe PMC and Unpaywall first |
| docx fidelity for co-authors | Tracked changes (w:ins / w:del) are a large effort | v0.4 exports comments; tracked changes for open suggestions later |
| Prompt injection through sources and reviewer text | Full text and reviewer comments are untrusted input the agent reads | Resources labelled untrusted; skills say so; write tools cannot reach outside scope regardless |
| Name clearance | Open source needs a name nobody else owns | Run a trademark search on "Tlilli" in software classes before the first public tag |
| License | Shapes contributions and reuse | Open: Apache-2.0 for the app, MIT for the skill pack is one option |
| Local models | Some users will want no cloud at all | Out of scope for the app; any MCP client with a local model already works |
