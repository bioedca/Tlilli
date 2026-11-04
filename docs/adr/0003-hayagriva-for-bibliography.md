# ADR-0003: `hayagriva` for citations and bibliography

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

A citation in Tlilli is a claim link, and the ledger stores sources as CSL-JSON: identifiers resolve to CSL-JSON through Crossref, NCBI E-utilities, the arXiv API and doi.org content negotiation (`FR-03-001`); Zotero exports arrive as CSL-JSON or BibTeX (`FR-05-040`); the ledger exports CSL-JSON with deterministic ordering (`FR-03-050`). The concept fixes the outputs: "CSL JSON is canonical. BibTeX export. The reference list renders in any CSL style for docx, LaTeX and PDF export. In-text markers are stored as `[@key]` and rendered numeric or author-year per the style sheet." The PRD turns this into requirements: BibTeX export with stable keys matching `[@key]` and Unicode preserved or escaped per setting (`FR-03-051`); Markdown export with a References section in the chosen CSL style, `apa`, `vancouver` and `nature` bundled, any `.csl` file loadable, numeric or author-year in-text rendering (`FR-03-052`); any CSL locale file with `en-US` as default and snapshot tests for `de-DE` and `es-ES` (`NFR-I18N-002`); docx, LaTeX (`.bib`) and Typst PDF exports carrying the same reference list (`FR-04-040..042`); a `citation_format` mechanical kind that re-renders markers (`FR-04-020`). The gate test opens the CSL-JSON in Zotero, compiles the BibTeX and renders references in two styles and one non-English locale ([PRD 40](../prd/40-roadmap-and-gates.md#gate-g3-v030-ledger), G3 step 4).

[PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) locks `hayagriva` (CSL styles and locales, maintained by Typst) for rendering and for BibTeX, and names `citeproc-rs` as the stalled alternative (D-054). The PDF path is `typst` + `typst-pdf` in-process, whose bibliography engine is `hayagriva`, so one engine serves the PDF and every other reference list ("one engine for PDF and reference lists"). The risk register carries R-17, "`hayagriva` lacks a needed CSL feature", with the mitigation already chosen: test styles against the CSL suite subset, fall back to post-processing or contribute upstream.

## Decision

**Canonical data.** CSL-JSON is the stored and exported truth for source metadata: the `sources` table holds one CSL-JSON document per source (ADR-0004), and `FR-03-050` exports it unchanged with deterministic key and item order. The ledger never depends on the engine's data model.

**Rendering engine.** `hayagriva` (crates.io release) renders in-text citations and reference lists for every output: Markdown (v0.3), docx, LaTeX and Typst PDF (v0.4). `tlilli-core::export` converts CSL-JSON to the engine's entry model at render time; the conversion is a pure function with snapshot tests and the single place that knows both models. The PDF export hands the same entries to Typst, so the PDF and the docx of one manuscript cite identically.

**Styles.** CSL 1.0 style files. `apa`, `vancouver` and `nature` ship as data files; the style sheet's citation-style field may name any user-supplied `.csl` (`FR-04-001`). Until the style sheet arrives in v0.4, the v0.3 Markdown export takes the style as an export option with `apa` as the default (`FR-03-052`). Styles are tested against a subset of the CSL test suite; a failure on a required style is the R-17 trigger.

**Locales.** CSL locale files; `en-US` is bundled and the default, and any locale file loads (`NFR-I18N-002`). The PRD does not say where the locale is chosen. The option taken: a locale field next to the citation style in the style sheet (v0.4), with an export option as the v0.3 interim, mirroring how the style itself is chosen. `de-DE` and `es-ES` are in the snapshot matrix (styles × locales, [PRD 34 §3](../prd/34-testing.md#3-what-to-test-by-component), Ledger).

**Markers and keys.** Span text stores `[@key]` with keys of the form `author-year-slug`, stable per source (`FR-03-011`). The renderer maps keys to CSL-JSON items, emits the numeric or author-year in-text form, and renders `[@missing:key]` for deleted sources with a warning. Re-rendering markers after a style change and renumbering references are mechanical edits with a reverse operation (`FR-04-020`, `citation_format`, `reference_renumber`).

**BibTeX.** Export through `hayagriva`'s BibTeX support; keys equal the `[@key]` keys so `\cite{key}` in the LaTeX export compiles against the exported `.bib` (`FR-03-051`, `FR-04-041`); Unicode is preserved or escaped per the export setting. Import of `.bib` files reuses the same support to produce CSL-JSON; this record decides that for the basic LaTeX import, which creates ledger stubs from the `.bib` (`FR-04-043`). If a `.bib` file carries fields the engine does not read, a small reader in `tlilli-core::import` fills the gap under recorded fixtures; that is an implementation change, not a new ADR, because it adds no native dependency. The Zotero import of `FR-05-040` is outside this record: its `.bib` files can use the same reader, but its CSL-JSON input and its attachment-path mapping with PDF copying need a separate decision before v0.5.

**Determinism.** Rendering is a pure function of (CSL-JSON, style, locale, marker list, output format). Outputs are snapshot-tested (`PR-TST-010`) and benchmarked within `NFR-PERF-008`.

## Consequences

### Positive

- One engine for every export: the PDF, docx, LaTeX and Markdown reference lists agree by construction.
- Pure Rust, in-process: no pandoc or citeproc-js sidecar, no JavaScript runtime (`PR-ARCH-004`, D-037).
- Maintained alongside Typst, which the PDF export already depends on; one dependency family to track.

### Negative

- CSL coverage may lag the reference implementation (citeproc-js); some journal styles may render with small deviations.
- The CSL-JSON → engine conversion can drop fields the engine does not model; those fields still round-trip through the CSL-JSON export but do not reach the rendered output.
- User-supplied `.csl` files that use rare CSL features are unsupported until the engine or a post-processing step covers them.

### Risks

- R-17: snapshot failures on a required style. Mitigation: the CSL test-suite subset in CI, post-processing of the rendered output, or an upstream contribution; a style the project cannot render is documented on the style-sheet page.
- Engine upgrades change rendered output: snapshots catch it (`PR-TST-010`); Dependabot groups the bump (`PR-MNT-010`).
- `.bib` dialects vary between exporters: recorded fixtures under `tests/fixtures/` catch reader regressions.

## Alternatives considered

- **`citeproc-rs`** ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions)). Rejected: development has stalled, so it fails the INTERSECT maintenance test (`PR-ARCH-003`).
- **citeproc-js through a JavaScript runtime or a pandoc sidecar.** Rejected: sidecars and bundled runtimes are forbidden by default (ADR-0005, `PR-ARCH-004`, D-037).
- **A hand-written formatter for the bundled styles only.** Rejected: the concept requires any CSL style, and `FR-03-052` requires any `.csl` file to load.
- **BibTeX as the canonical format.** Rejected: the concept and `FR-03-001` make CSL-JSON canonical; resolvers return it and Zotero opens it (G3).
- **Two engines (hayagriva for PDF, another for docx and Markdown).** Rejected: two renderers of one reference list would disagree in ways the author cannot see until submission.

## References

- Concept document: "Citation ledger" (Outputs), "Architecture" (References row).
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §3 (Citations, LaTeX, PDF), §5; [12](../prd/12-fr-v0.3-ledger.md) §12.1, §12.2, §12.6; [13](../prd/13-fr-v0.4-sweep-and-style.md) §13.1, §13.3, §13.5; [34](../prd/34-testing.md) §3 (Ledger); [40](../prd/40-roadmap-and-gates.md) G3 step 4.
- Requirements: `FR-03-001`, `FR-03-011`, `FR-03-050..052`, `FR-04-001`, `FR-04-020`, `FR-04-040..043`; `NFR-I18N-002`, `NFR-PERF-008`; `PR-ARCH-003`, `PR-ARCH-004`; `PR-TST-010`; `PR-MNT-010`. Context only, not decided here: `FR-05-040` ([PRD 14 §14.5](../prd/14-fr-v0.5-beyond-the-article.md#145-zotero-import)).
- Decisions and risks: D-037, D-054; R-17; ADR-0004, ADR-0005.
