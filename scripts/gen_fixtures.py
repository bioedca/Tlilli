#!/usr/bin/env python3
"""Generate the synthetic test fixtures under tests/fixtures/ (PR-TST-016, D-027).

Skeleton from bootstrap task 15. CATALOGUE names every kind of fixture the tests use (PRD 34): its
place, origin and license, which tests/fixtures/LICENSES.md records file by file. Only the
generated kinds that have a generator are produced here.

Determinism: the output depends on the seed and on this file alone. Each kind draws from its own
random.Random, seeded with the seed and the kind's name, so a new kind leaves the others unchanged,
and only Random.random() is called, the one method whose sequence Python keeps across versions.
Nothing reads the clock, the environment, the locale or a directory listing, and files are written
as UTF-8 bytes with LF line endings: one seed gives byte-identical files everywhere.
"""

from __future__ import annotations

import argparse
import hashlib
import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "tests" / "fixtures"
# The committed fixtures are generated with this seed; changing it changes every generated file.
DEFAULT_SEED = 1


class Rng:
    """Seeded choices built on Random.random() alone, for the guarantee above."""

    def __init__(self, seed: int, kind: str) -> None:
        self._random = random.Random(f"tlilli-fixtures/{seed}/{kind}")

    def below(self, n: int) -> int:
        """An integer in [0, n)."""
        return min(int(self._random.random() * n), n - 1)

    def between(self, low: int, high: int) -> int:
        """An integer in [low, high], both ends included."""
        return low + self.below(high - low + 1)

    def pick(self, items: Sequence[str]) -> str:
        return items[self.below(len(items))]


# Synthetic manuscripts. A starting set of the hazards segmentation and anchoring meet in real
# manuscripts (abbreviations, decimals, citations, figure references, non-ASCII units); the tests
# that consume these files grow the word lists. English only for now: Spanish and German arrive
# with the segmentation corpus (PRD 34 §3). Every name and citation key is fictional.
MANUSCRIPTS = 3
SECTIONS = ("Introduction", "Methods", "Results", "Discussion")
TOPICS = ("enzyme kinetics", "soil microbiota", "protein folding", "leaf development",
          "cell migration")
SUBJECTS = ("The assay", "Each sample", "The control group", "The reporter strain", "Our model",
            "The second cohort", "Treatment with compound A")
VERBS = ("increased", "reduced", "did not change", "predicted", "doubled", "stabilized")
OBJECTS = ("the binding affinity", "expression of the reporter", "the growth rate",
           "the response time", "the error rate", "colony size")
TAILS = ("", "", "in all three replicates", "after 24 h at 37 °C", "(Fig. 2)", "(see Table 1)",
         "as Doe et al. reported [@doe2021]", "by 3.5-fold (p < 0.01)", "e.g. in the second batch",
         "relative to the baseline of Roe and Poe [@roe2019; @poe2020]")


def sentence(rng: Rng) -> str:
    tail = rng.pick(TAILS)
    words = [rng.pick(SUBJECTS), rng.pick(VERBS), rng.pick(OBJECTS)] + ([tail] if tail else [])
    return " ".join(words) + "."


def paragraph(rng: Rng) -> str:
    return " ".join(sentence(rng) for _ in range(rng.between(3, 5)))


def gen_manuscripts(rng: Rng, seed: int) -> dict[str, str]:
    files = {}
    for number in range(1, MANUSCRIPTS + 1):
        lines = [
            (f"<!-- Synthetic fixture from scripts/gen_fixtures.py, seed {seed}. "
             "Regenerate it; do not edit by hand. -->"),
            "",
            f"# Synthetic study {number:03}: {rng.pick(OBJECTS)} in {rng.pick(TOPICS)}",
            "",
            "## Abstract",
            "",
            paragraph(rng),
        ]
        for section in SECTIONS:
            lines += ["", f"## {section}"]
            for _ in range(rng.between(2, 3)):
                lines += ["", paragraph(rng)]
        files[f"manuscripts/synthetic-en-{number:03}.md"] = "\n".join(lines) + "\n"
    return files


@dataclass(frozen=True)
class Kind:
    name: str
    path: str  # under tests/fixtures/; empty when the kind is never committed
    origin: str  # generated, vendored, recorded or private
    license: str
    contents: str
    generate: Callable[[Rng, int], dict[str, str]] | None = None
    note: str = ""


# PR-TST-016 names the first four kinds; PRD 34 §1 and §3 name the recorded ones.
CATALOGUE = (
    Kind("manuscripts", "manuscripts/", "generated", "Apache-2.0",
         "synthetic manuscripts in Markdown for segmentation, anchoring and import/export tests",
         generate=gen_manuscripts),
    Kind("revisions", "revisions/", "generated", "Apache-2.0",
         "revision corpora: scripted edit series over the synthetic manuscripts",
         note="generator pending until the core edit events exist, v0.1"),
    Kind("papers", "papers/", "vendored", "CC-BY or CC0, per paper",
         "open-access papers, each with a row in LICENSES.md and a table in REUSE.toml"),
    Kind("histories", "", "private", "the maintainer's",
         "the maintainer's own revision histories (tlilli export --canonical); used locally "
         "and at gates, never committed"),
    Kind("transcripts", "transcripts/", "recorded", "Apache-2.0",
         "golden JSON-RPC transcripts written by the MCP contract tests"),
    Kind("http", "http/", "recorded", "per host, in LICENSES.md",
         "resolver responses recorded and redacted by a dev script (PR-TST-006)"),
    Kind("db", "db/", "recorded", "Apache-2.0",
         "one storage database per released schema version (ADR-0004)"),
)


def print_catalogue() -> None:
    for kind in CATALOGUE:
        where = f"tests/fixtures/{kind.path}" if kind.path else "(not committed)"
        print(f"{kind.name:<12} {where:<28} {kind.origin:<10} {kind.license}")
        print(f"{'':<12} {kind.contents}" + (f" ({kind.note})" if kind.note else ""))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the synthetic fixtures under tests/fixtures/ from a seed "
        "(PR-TST-016). The same seed gives byte-identical files.",
        epilog="Licenses and provenance of every fixture: tests/fixtures/LICENSES.md.",
    )
    parser.add_argument("kinds", nargs="*", metavar="KIND",
                        help="kinds to generate (default: every kind with a generator; see --list)")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED,
                        help=f"seed for every generator (default: {DEFAULT_SEED})")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT,
                        help="directory to write into (default: tests/fixtures)")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="print each file with its size and SHA-256 digest; write nothing")
    parser.add_argument("--list", action="store_true", help="print the fixture catalogue and exit")
    args = parser.parse_args(argv)

    if args.list:
        print_catalogue()
        return 0

    by_name = {kind.name: kind for kind in CATALOGUE}
    names = args.kinds or [kind.name for kind in CATALOGUE if kind.generate]
    for name in names:
        if name not in by_name:
            parser.error(f"unknown kind {name!r} (see --list)")
        if by_name[name].generate is None:
            kind = by_name[name]
            parser.error(f"{name} is not generated by this script ({kind.note or kind.origin})")

    action = "would write" if args.dry_run else "wrote"
    for name in names:
        kind = by_name[name]
        assert kind.generate is not None
        files = kind.generate(Rng(args.seed, name), args.seed)
        for rel, text in sorted(files.items()):
            data = text.encode("utf-8")
            if not args.dry_run:
                path = args.out / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            print(f"{action} {rel}  {len(data)} bytes  sha256 {hashlib.sha256(data).hexdigest()}")
    pending = [kind.name for kind in CATALOGUE if kind.origin == "generated" and not kind.generate]
    if pending and not args.kinds:
        print(f"no generator yet: {', '.join(pending)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
