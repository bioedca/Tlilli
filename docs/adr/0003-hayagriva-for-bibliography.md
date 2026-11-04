# ADR-0003: `hayagriva` for citations and bibliography

- **Status:** Proposed (the maintainer's merge of the pull request records acceptance; see the [index](README.md))
- **Date:** 2026-11-04
- **Deciders:** bioedca (maintainer). Drafted by Claude Code (cloud), bootstrap task 16 ([PRD 42](../prd/42-bootstrap-backlog.md) row 16).

## Context

A citation in Tlilli is a claim link, and the ledger stores sources as CSL-JSON: identifiers resolve to CSL-JSON through Crossref, NCBI E-utilities, the arXiv API and doi.org content negotiation (`FR-03-001`); Zotero exports arrive as CSL-JSON or BibTeX (`FR-05-040`); the ledger exports CSL-JSON with deterministic ordering (`FR-03-050`). The concept fixes the outputs: "CSL JSON is canonical. BibTeX export. The reference list renders in any CSL style for docx, LaTeX and PDF export. In-text markers are stored as `[@key]` and rendered numeric or author-year per the style sheet." The PRD turns this into requirements: BibTeX export with stable keys matching `[@key]` and Unicode preserved or escaped per setting (`FR-03-051`); Markdown export with a References section in the chosen CSL style, `apa`, `vancouver` and `nature` bundled, any `.csl` file loadable, numeric or author-year in-text rendering (`FR-03-052`); any CSL locale file with `en-US` as default and snapshot tests for `de-DE` and `es-ES` (`NFR-I18N-002`); docx, LaTeX (`.bib`) and Typst PDF exports carrying the same reference list (`FR-04-040..042`); a `citation_format` mechanical kind that re-renders markers (`FR-04-020`). The gate test opens the CSL-JSON in Zotero, compiles the BibTeX and renders references in two styles and one non-English locale ([PRD 40](../prd/40-roadmap-and-gates.md#gate-g3-v030-ledger), G3 step 4).

[PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) locks `hayagriva` (CSL styles and locales, maintained by Typst) for rendering and for BibTeX, and names `citeproc-rs` as the stalled alternative (D-054). The PDF path is `typst` + `typst-pdf` in-process, whose bibliography engine is `hayagriva`, so one engine serves the PDF and every other reference list ("one engine for PDF and reference lists"). The risk register carries R-17, "`hayagriva` lacks a needed CSL feature", with the mitigation already chosen: test styles against the CSL suite subset, fall back to post-processing or contribute upstream.

## Decision

**Canonical data.** CSL-JSON is the stored and exported truth for source metadata: the `sources` table holds one CSL-JSON document per source (ADR-0004), and `FR-03-050` exports it unchanged with deterministic key and item order. The ledger never depends on the engine's data model.

**Rendering engine.** `hayagriva` 0.10.1, the current crates.io release, with its default features (`biblatex`, `archive`), renders in-text citations and reference lists for Markdown (v0.3), docx and Typst PDF (v0.4). The LaTeX export (v0.4) is the exception: it writes `\cite{key}` and a `.bib` (BibTeX, below), and the reference list that `latexmk -pdf` prints is formatted by the bibliography backend and style the LaTeX template names, not by `hayagriva` (`FR-04-041`). This record does not decide the default article template's backend (BibTeX or Biber), its bibliography style, or whether a CSL style maps to a LaTeX one; the template work for `FR-04-041` decides them before v0.4, and until then the LaTeX reference list is not claimed to match the others. `tlilli-core::export` converts CSL-JSON to the engine's entry model at render time; the conversion is a pure function with snapshot tests and the single place that knows both models. The PDF export hands the same entries to Typst, so the PDF and the docx of one manuscript cite identically. Later releases arrive through Dependabot and pass the same snapshot tests (`PR-MNT-010`).

**Styles.** CSL 1.0 style files. `apa`, `vancouver` and `nature` ship as data files; the style sheet's citation-style field may name any user-supplied `.csl` (`FR-04-001`). Until the style sheet arrives in v0.4, the v0.3 Markdown export takes the style as an export option with `apa` as the default (`FR-03-052`). Styles are tested against a subset of the CSL test suite; a failure on a required style is the R-17 trigger.

**Style and locale licenses.** The CSL styles and locales are data under CC-BY-SA-3.0, a license outside the `deny.toml` allow-list of `PR-ARCH-003`, and this record is the ADR that rule asks for. The `archive` feature compiles the CSL project's styles and locales into `hayagriva` (its `styles.cbor.rkyv`; CC-BY-SA-3.0 per the crate's README and NOTICE), and the `apa`, `vancouver`, `nature` and `en-US` files Tlilli ships come from the same project under the same license. Tlilli redistributes them unmodified, with their attribution (the `StyleInfo` of each archived style, the `info` element of each shipped file) and the license text in the third-party notices and the REUSE annotations; a style Tlilli changes is published under CC-BY-SA-3.0. The styles are data the engine reads at run time, and Tlilli's code is not an adaptation of them, so the code's own license is unchanged.

**Locales.** CSL locale files; `en-US` is bundled and the default, and any locale file loads (`NFR-I18N-002`). The PRD does not say where the locale is chosen. The option taken: a locale field next to the citation style in the style sheet (v0.4), with an export option as the v0.3 interim, mirroring how the style itself is chosen. `de-DE` and `es-ES` are in the snapshot matrix (styles × locales, [PRD 34 §3](../prd/34-testing.md#3-what-to-test-by-component), Ledger).

**Markers and keys.** Span text stores `[@key]` with keys of the form `author-year-slug`, stable per source (`FR-03-011`). The renderer maps keys to CSL-JSON items, emits the numeric or author-year in-text form, and renders `[@missing:key]` for deleted sources with a warning. Re-rendering markers after a style change and renumbering references are mechanical edits with a reverse operation (`FR-04-020`, `citation_format`, `reference_renumber`).

**BibTeX.** `hayagriva` 0.10.1 reads BibTeX and BibLaTeX into its own `Entry` model (`io::from_biblatex_str`, `io::from_biblatex`) but writes neither: its `io` module writes only its YAML format, and its README lists YAML-to-BibLaTeX conversion as planned work. It has no conversion between `Entry` and CSL-JSON either: its non-default `csl-json` feature lets the CSL processor read CSL-JSON items for rendering, but converts nothing. Both directions therefore have a Tlilli-owned part. *Export:* `tlilli-core::export` maps each cited CSL-JSON item to a BibTeX entry and writes the file with the BibTeX writer of the `biblatex` crate (`Bibliography::write_bibtex`). `tlilli-core` declares `biblatex = "0.12"` as a direct dependency: `hayagriva` does not re-export the crate, and its README asks users who need `biblatex` types to depend on it themselves. `hayagriva` 0.10.1 already depends on `biblatex` 0.12.0 through its default `biblatex` feature, so Cargo resolves both requirements to one package; the direct dependency adds a manifest line, not a crate to the build. `biblatex` is pure Rust, MIT OR Apache-2.0 and maintained by Typst (0.12.0, June 2026), so it needs no ADR of its own (`PR-ARCH-002`, `PR-ARCH-003`). Keys equal the `[@key]` keys so `\cite{key}` in the LaTeX export compiles against the exported `.bib` (`FR-03-051`, `FR-04-041`); the mapping preserves or escapes Unicode per the export setting. *Import:* a `.bib` file is parsed with `biblatex::Bibliography::parse` and turned into `hayagriva` entries with `io::from_biblatex` (the two steps `io::from_biblatex_str` combines), and `tlilli-core::import` converts those entries to CSL-JSON; this record decides that for the basic LaTeX import, which creates ledger stubs from the `.bib` (`FR-04-043`). Fields the engine does not carry into `Entry` are read from the parsed `biblatex` entries by the same module under recorded fixtures; that is an implementation change, not a new ADR, because it adds no native dependency. Both mappings are pure functions with fixture tests; if a later `hayagriva` release ships a BibTeX writer or a CSL-JSON conversion, adopting it is an implementation change checked by the same fixtures. [PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions) (Citations row: "BibTeX export via `hayagriva`'s BibTeX support") and `FR-04-041` ("`.bib` from hayagriva") assume a writer that 0.10.1 does not have. The PRD round-3 amendment (issue 55) corrects that wording and adds the `D-nnn` entry; it is listed under [PRD changes pending](README.md#prd-changes-pending), and this record is not marked Accepted before it has merged. The Zotero import of `FR-05-040` is outside this record: its `.bib` files can take the same import path, but its CSL-JSON input and its attachment-path mapping with PDF copying need a separate decision before v0.5.

**Determinism.** Rendering is a pure function of (CSL-JSON, style, locale, marker list, output format). Outputs are snapshot-tested (`PR-TST-010`) and benchmarked within `NFR-PERF-008`.

## Consequences

### Positive

- One engine for the PDF, docx and Markdown exports: their reference lists agree by construction.
- Pure Rust, in-process: no pandoc or citeproc-js sidecar, no JavaScript runtime (`PR-ARCH-004`, D-037).
- Maintained alongside Typst, which the PDF export already depends on; one dependency family to track.

### Negative

- CSL coverage may lag the reference implementation (citeproc-js); some journal styles may render with small deviations.
- The CSL-JSON → engine conversion can drop fields the engine does not model; those fields still round-trip through the CSL-JSON export but do not reach the rendered output.
- User-supplied `.csl` files that use rare CSL features are unsupported until the engine or a post-processing step covers them.
- The LaTeX reference list is formatted by the template's bibliography backend, not by the engine, so it can differ from the other exports until the `FR-04-041` template work decides the style.
- The engine provides neither BibTeX field mapping, so Tlilli owns two (CSL-JSON to BibTeX for export, `Entry` to CSL-JSON for import), and their fixtures must cover every entry type the ledger stores.

### Risks

- R-17: snapshot failures on a required style. Mitigation: the CSL test-suite subset in CI, post-processing of the rendered output, or an upstream contribution; a style the project cannot render is documented on the style-sheet page.
- Engine upgrades change rendered output: snapshots catch it (`PR-TST-010`); Dependabot groups the bump (`PR-MNT-010`).
- `.bib` dialects vary between exporters: recorded fixtures under `tests/fixtures/` catch reader regressions.

## Alternatives considered

- **`citeproc-rs`** ([PRD 21 §3](../prd/21-architecture-and-tech-stack.md#3-technology-decisions)). Rejected: development has stalled, so it fails the INTERSECT maintenance test (`PR-ARCH-003`).
- **citeproc-js through a JavaScript runtime or a pandoc sidecar.** Rejected: sidecars and bundled runtimes are forbidden by default (ADR-0005, `PR-ARCH-004`, D-037).
- **A hand-written formatter for the bundled styles only.** Rejected: the concept requires any CSL style, and `FR-03-052` requires any `.csl` file to load.
- **BibTeX as the canonical format.** Rejected: the concept and `FR-03-001` make CSL-JSON canonical; resolvers return it and Zotero opens it (G3).
- **Two engines (hayagriva for PDF, another for docx and Markdown).** Rejected: two renderers of one reference list would disagree in ways the author cannot see until submission. The LaTeX export is the one exception (Rendering engine, above), because a LaTeX submission is compiled with the journal template's own bibliography setup.

## References

- Concept document: "Citation ledger" (Outputs), "Architecture" (References row).
- PRD: [21](../prd/21-architecture-and-tech-stack.md) §3 (Citations, LaTeX, PDF), §5; [12](../prd/12-fr-v0.3-ledger.md) §12.1, §12.2, §12.6; [13](../prd/13-fr-v0.4-sweep-and-style.md) §13.1, §13.3, §13.5; [34](../prd/34-testing.md) §3 (Ledger); [40](../prd/40-roadmap-and-gates.md) G3 step 4.
- Requirements: `FR-03-001`, `FR-03-011`, `FR-03-050..052`, `FR-04-001`, `FR-04-020`, `FR-04-040..042`; `FR-04-043` (basic LaTeX import only); `NFR-I18N-002`, `NFR-PERF-008`; `PR-ARCH-003`, `PR-ARCH-004`; `PR-TST-010`; `PR-MNT-010`. Context only, not decided here: `FR-05-040` ([PRD 14 §14.5](../prd/14-fr-v0.5-beyond-the-article.md#145-zotero-import)).
- Decisions and risks: D-037, D-054; R-17; ADR-0004, ADR-0005.
