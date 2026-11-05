#!/usr/bin/env python3
"""Keep CITATION.cff in step with the workspace version (PR-REL-002, PRD 37 §8).

Sets the top-level `version` of CITATION.cff to `[workspace.package] version` in Cargo.toml and
its `date-released` to the release date, changing only those two lines. The release workflow runs
it on the release pull request's branch after release-plz has bumped the version. Bad input exits 2.

    scripts/citation_version.py                    update CITATION.cff, dated today (UTC)
    scripts/citation_version.py --date 2026-11-05  update it with that date
    scripts/citation_version.py --check            exit 1 if its version differs from Cargo.toml
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# The versions release-plz writes: MAJOR.MINOR.PATCH with an optional pre-release (PR-REL-001).
SEMVER = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?")


class InputError(Exception):
    pass


def workspace_version(cargo_toml: Path) -> str:
    with cargo_toml.open("rb") as f:
        version = tomllib.load(f).get("workspace", {}).get("package", {}).get("version")
    if not isinstance(version, str) or not SEMVER.fullmatch(version):
        raise InputError(f"{cargo_toml}: no MAJOR.MINOR.PATCH [workspace.package] version")
    return version


def key_lines(lines: list[str], key: str) -> list[int]:
    """Indexes of the top-level `key:` lines; nested keys are indented and do not match."""
    return [i for i, line in enumerate(lines) if re.match(rf"{re.escape(key)}:(\s|$)", line)]


def cff_version(lines: list[str]) -> tuple[int, str]:
    found = key_lines(lines, "version")
    if len(found) != 1:
        raise InputError(f"CITATION.cff: want one top-level version line, found {len(found)}")
    value = lines[found[0]].split(":", 1)[1].split(" #", 1)[0].strip().strip("'\"")
    return found[0], value


def update(text: str, version: str, date: str) -> str:
    lines = text.splitlines(keepends=True)
    at, _ = cff_version(lines)
    dated = key_lines(lines, "date-released")
    if len(dated) > 1:
        raise InputError(f"CITATION.cff: {len(dated)} date-released lines")
    lines[at] = f"version: {version}\n"
    # Quoted, so that YAML reads a string, which is the type the CFF schema asks for.
    date_line = f'date-released: "{date}"\n'
    if dated:
        lines[dated[0]] = date_line
    else:
        lines.insert(at + 1, date_line)
    return "".join(lines)


def release_date(value: str | None) -> str:
    if value is None:
        return datetime.datetime.now(datetime.UTC).date().isoformat()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        pass
    raise InputError(f"--date {value}: not a YYYY-MM-DD date")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--date", help="the release date, YYYY-MM-DD (default: today, UTC)")
    mode.add_argument("--check", action="store_true", help="only compare the versions")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    cff = args.root / "CITATION.cff"
    try:
        version = workspace_version(args.root / "Cargo.toml")
        text = cff.read_text(encoding="utf-8")
        if args.check:
            _, current = cff_version(text.splitlines(keepends=True))
            if current != version:
                print(f"CITATION.cff has version {current}, Cargo.toml {version}", file=sys.stderr)
                return 1
            print(f"CITATION.cff is at version {version}")
            return 0
        date = release_date(args.date)
        cff.write_text(update(text, version, date), encoding="utf-8", newline="\n")
    except (InputError, OSError, tomllib.TOMLDecodeError) as err:
        print(f"citation_version.py: {err}", file=sys.stderr)
        return 2
    print(f"CITATION.cff: version {version}, date-released {date}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
