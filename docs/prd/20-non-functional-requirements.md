# 20 · Non-functional requirements

Each NFR names the phase from which it applies, how it is verified, and where it is enforced. Performance numbers are measured on the reference machine (a 2020-class laptop: 4 cores, 16 GB RAM, SSD) with the reference manuscript (12,000 words, 6 figures, 80 sources) unless stated. Benchmarks run nightly with `criterion` and fail on a 20% regression against the stored baseline ([34 Testing](34-testing.md)).

## Performance (NFR-PERF)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-PERF-001` | Opening a workspace and rendering the reference manuscript MUST take ≤ 2 s cold, ≤ 500 ms warm | v0.1 | criterion bench + e2e timer |
| `NFR-PERF-002` | Typing latency (keystroke → event committed → view updated) MUST stay ≤ 16 ms at p95 on the reference manuscript | v0.1 | Playwright trace + core bench |
| `NFR-PERF-003` | Re-segmentation after an edit to one paragraph MUST complete in ≤ 5 ms; whole-manuscript re-segmentation ≤ 200 ms | v0.1 | criterion |
| `NFR-PERF-004` | Snapshot creation ≤ 100 ms; diff between two snapshots of the reference manuscript ≤ 1 s | v0.1 | criterion |
| `NFR-PERF-005` | MCP `run_claim`, `queue_list`, `manuscript_outline` MUST respond in ≤ 200 ms; whole-manuscript resource read ≤ 500 ms; section read ≤ 100 ms | v0.2 | contract tests with timing |
| `NFR-PERF-006` | Full-text search over 80 sources (≈ 2 M characters) MUST return in ≤ 300 ms (SQLite FTS5) | v0.3 | criterion |
| `NFR-PERF-007` | PDF text extraction for a 15-page article ≤ 5 s; DOI sniffing ≤ 200 ms after extraction | v0.3 | bench on fixtures |
| `NFR-PERF-008` | Exports: Markdown ≤ 1 s, docx ≤ 3 s, LaTeX ≤ 1 s, PDF through Typst ≤ 10 s for the reference manuscript | v0.4 | bench |
| `NFR-PERF-009` | Idle CPU of the app MUST be ≈ 0%; idle memory ≤ 400 MB with the reference manuscript open | v0.1 | manual at gate, measured |
| `NFR-PERF-010` | Installer size SHOULD be ≤ 40 MB per platform excluding optional components; the AppImage ≤ 90 MB | v1.0 | release job asserts sizes |

## Reliability and data safety (NFR-REL)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-REL-001` | The event log is append-only in SQLite with WAL and synchronous=NORMAL; a crash or power loss MUST lose at most the last uncommitted transaction (≤ 1 s of typing) | v0.1 | kill-9 test harness; property test on recovery |
| `NFR-REL-002` | On startup the core MUST verify log integrity (hash chain per event) and rebuild materialized snapshots if they disagree with the log | v0.1 | unit + corrupted-fixture tests |
| `NFR-REL-003` | Every schema migration MUST back up `workspace.sqlite` to `backups/<timestamp>-pre-<version>.sqlite` before running and MUST be reversible or documented as one-way in the release notes | v0.1 | migration tests both directions |
| `NFR-REL-004` | A run that passes its timeout (30 min without heartbeat, configurable) or is cancelled MUST roll back mechanical edits and keep suggestions as open red ink; the manuscript MUST become editable within 1 s | v0.2 | state-machine tests; e2e |
| `NFR-REL-005` | The MCP server MUST survive client disconnects, malformed JSON-RPC and concurrent clients without corrupting state; a crashed server MUST NOT leave a run claimed (claims expire with the heartbeat) | v0.2 | fuzzing; chaos test |
| `NFR-REL-006` | Imports MUST never fail silently: unsupported constructs are reported in an import report and preserved as raw blocks where possible | v0.1 | snapshot tests on fixtures |
| `NFR-REL-007` | Autosave is continuous (every event persisted); there is no "save" action and no unsaved state older than NFR-REL-001 allows | v0.1 | design review; e2e |
| `NFR-REL-008` | `tlilli export --canonical` and re-import MUST round-trip the manuscript, ledger, style sheet and provenance without loss (byte-identical canonical JSON after normalization) | v0.1 (manuscript), v0.3 (ledger), v0.4 (style) | property test |

## Security (NFR-SEC) — details in [22](22-security-and-threat-model.md)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-SEC-001` | The MCP HTTP transport MUST bind to 127.0.0.1 only and MUST require a per-workspace bearer token, generated with 256 bits of entropy, shown once, revocable and rotatable from the UI | v0.2 | contract tests; port scan test |
| `NFR-SEC-002` | Every tool input MUST be validated against its JSON schema before reaching the core; oversized payloads (> 1 MB per call) are rejected | v0.2 | fuzzing; unit |
| `NFR-SEC-003` | Text from sources, PDFs and reviewer comments MUST be delivered inside an envelope that marks it `untrusted: true` and MUST never be interpolated into app-generated instructions | v0.2 | contract tests on resource envelopes |
| `NFR-SEC-004` | The app MUST make outbound requests only to the allow-listed resolver hosts (Crossref, PubMed/NCBI, arXiv, Europe PMC, Unpaywall, DOI.org, Zotero local API) and only on author action; the list is visible in Settings | v0.3 | network allow-list test with a recording proxy |
| `NFR-SEC-005` | PDFs are parsed with memory and time limits (≤ 512 MB, ≤ 60 s) in a separate thread; parser panics MUST NOT crash the app | v0.3 | fuzzing; malformed fixtures |
| `NFR-SEC-006` | The tunnel feature (v0.5) MUST be off by default, MUST require the workspace token on every request, MUST display the public URL and a one-click stop, and MUST stop when the app quits | v0.5 | e2e; manual |
| `NFR-SEC-007` | Release artifacts MUST ship with SHA-256 checksums and Sigstore build-provenance attestations verifiable with `gh attestation verify`; the updater MUST reject unsigned or wrongly signed manifests (minisign) | v0.2 (updater), v1.0 (all) | release workflow asserts; manual verify at gate |
| `NFR-SEC-008` | No secret, token or key is ever written to logs, diagnostics bundles, canonical exports or the repository | v0.1 | secret-scanning CI; log redaction tests |

## Privacy (NFR-PRIV)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-PRIV-001` | No telemetry, analytics, crash upload or update ping beyond the explicit updater check the user enables | v0.1 | network allow-list test; code review |
| `NFR-PRIV-002` | The updater check sends only the platform, architecture and current version in the URL; no identifiers | v0.2 | contract test on request |
| `NFR-PRIV-003` | Diagnostics bundles redact manuscript text, source full text and file paths under the home directory; redaction is on by default and visible before copying | v0.1 | unit tests on redactor; manual |
| `NFR-PRIV-004` | Workspace folders are portable: moving or syncing the folder (Dropbox, iCloud) MUST not break it, with a documented warning about concurrent writers | v0.1 | e2e |
| `NFR-PRIV-005` | Resolver requests MUST carry a generic User-Agent (`tlilli/<version> (+https://tlilli site)`) and the Crossref polite-pool mailto only if the author enters an email in Settings | v0.3 | unit |

## Usability and accessibility (NFR-USE)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-USE-001` | Every action in the editor and review pane MUST be reachable by keyboard; the markup flow is Select → Cmd/Ctrl-K → tag (fuzzy) → note → Enter; Send is one key and shows the queued count | v0.1 | Playwright keyboard-only suite |
| `NFR-USE-002` | The UI MUST meet WCAG 2.1 AA: contrast ≥ 4.5:1 for text, visible focus, ARIA roles and labels on panes, cards and status chips, screen-reader announcements for run state changes | v0.1 | axe-core in Playwright; manual VoiceOver/NVDA pass at gates |
| `NFR-USE-003` | Ink colour (black, red, mechanical, mixed) MUST have a non-colour cue (underline style or margin glyph) and a high-contrast theme | v0.2 | visual snapshot; a11y audit |
| `NFR-USE-004` | The UI language is English through v1.0; all strings are externalized (ICU message format) so that localization is a translation task, not a code change | v0.1 | lint rule: no literal UI strings |
| `NFR-USE-005` | Manuscript text may be in any language; sentence segmentation is rule-based for English and best-effort elsewhere, with a per-manuscript segmentation override | v0.1 | fixtures in English, Spanish, German |
| `NFR-USE-006` | Error messages MUST say what happened, what the user can do, and never show a stack trace by default; technical detail lives behind "Details" | v0.1 | UX copy review; snapshot |
| `NFR-USE-007` | Dark and light themes following the OS, with the ink palette validated in both | v0.1 | visual snapshots |

## Portability and platforms (NFR-PORT)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-PORT-001` | Supported: macOS 13+ (arm64, x86_64), Windows 10 22H2+ and 11 (x86_64), Ubuntu 22.04+ / glibc 2.35+ (x86_64). Linux arm64 is best-effort (built, not gate-tested) | v0.1 | release matrix; gate on each OS |
| `NFR-PORT-002` | The workspace folder format is OS-independent; a workspace created on one OS opens on another | v0.1 | cross-OS fixture test in CI |
| `NFR-PORT-003` | The MCP server runs as the in-app server, and as a standalone binary (`tlilli-mcp`) installable with `cargo install` or `cargo binstall`, sharing the same core and workspace | v0.2 | contract tests against both |
| `NFR-PORT-004` | Paths, line endings and Unicode normalization (NFC) are handled identically on all OSes; file names in the workspace avoid characters illegal on Windows | v0.1 | unit tests |

## Compatibility and evolution (NFR-COMPAT)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-COMPAT-001` | The workspace schema carries a version; the app opens any workspace of an equal or lower schema version and migrates forward; opening a newer workspace is refused with a clear message | v0.1 | migration tests |
| `NFR-COMPAT-002` | The canonical JSON export carries a `$schema` URL and version; schemas are published on the docs site and validated in CI | v0.1 | JSON Schema validation in tests |
| `NFR-COMPAT-003` | MCP tool and resource schemas are versioned with the app; within a major version tools are only added or extended; deprecations are announced one minor before removal and marked in the tool description | v0.2 | contract snapshot tests fail on unannounced change |
| `NFR-COMPAT-004` | Skill pack and app versions are released together; a skill declares the minimum app version it needs | v0.2 | unit |
| `NFR-COMPAT-005` | Public Rust API of `tlilli-core` follows SemVer after 1.0; `cargo-semver-checks` runs in the release PR | v1.0 | CI |

## Observability (NFR-OBS)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-OBS-001` | Structured logs (`tracing`, JSON lines) to `<workspace>/logs/`, rotated daily, kept 14 days, level configurable; default `info`, never logging manuscript text at `info` or above | v0.1 | unit; log audit |
| `NFR-OBS-002` | Every run stores its complete tool-call log (request, response, timing, outcome) in the database and exposes it in the run history view and as the `tlilli://run/{id}/log` resource | v0.2 | contract test |
| `NFR-OBS-003` | A crash writes a report file (`crashes/<timestamp>.txt`: version, OS, panic message, redacted backtrace) and the next launch offers to open the bug-report form with it attached by hand | v0.1 | panic-injection test |
| `NFR-OBS-004` | "Copy diagnostics" in Settings produces a redacted bundle (versions, OS, log tail, schema version, run summaries) in one click | v0.1 | e2e |

## Internationalization (NFR-I18N)

| ID | Requirement | From | Verification |
| --- | --- | --- | --- |
| `NFR-I18N-001` | Unicode throughout: NFC normalization on input, grapheme-aware cursoring, right-to-left text displayed correctly even though UI chrome is left-to-right | v0.1 | fixtures |
| `NFR-I18N-002` | Citation rendering supports any CSL locale file; default `en-US` | v0.3 | snapshot tests with `de-DE`, `es-ES` |
