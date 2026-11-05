"""Tests for scripts/citation_version.py (PR-REL-002): run it as a subprocess on copies of
Cargo.toml and CITATION.cff in temporary directories, and once with --check on the repository's
own files. Run with `python3 -B -m unittest discover -s scripts/tests`.
"""

import datetime
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "citation_version.py"

CARGO = '[workspace]\nmembers = []\n\n[workspace.package]\nversion = "{}"\nedition = "2024"\n'
CFF = """# A comment that stays.
cff-version: 1.2.0
title: Tlilli
version: 0.0.0
license: Apache-2.0
references:
  - type: software
    title: A dependency
    version: 9.9.9
"""


def run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True, check=False)


class CitationVersionTest(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.write("0.4.0", CFF)

    def write(self, version: str, cff: str) -> None:
        (self.root / "Cargo.toml").write_text(CARGO.format(version), encoding="utf-8")
        (self.root / "CITATION.cff").write_text(cff, encoding="utf-8")

    def cff(self) -> str:
        return (self.root / "CITATION.cff").read_text(encoding="utf-8")

    def test_sets_the_version_and_adds_the_date_after_it(self) -> None:
        result = run(self.root, "--date", "2026-11-05")
        self.assertEqual(result.returncode, 0, result.stderr)
        want = CFF.replace("version: 0.0.0\n", 'version: 0.4.0\ndate-released: "2026-11-05"\n')
        self.assertEqual(self.cff(), want)

    def test_a_second_run_replaces_the_date(self) -> None:
        run(self.root, "--date", "2026-11-05")
        self.write("0.4.1", self.cff())
        self.assertEqual(run(self.root, "--date", "2026-12-01").returncode, 0)
        want = CFF.replace("version: 0.0.0\n", 'version: 0.4.1\ndate-released: "2026-12-01"\n')
        self.assertEqual(self.cff(), want)

    def test_dates_today_in_utc_by_default(self) -> None:
        self.assertEqual(run(self.root).returncode, 0)
        today = datetime.datetime.now(datetime.UTC).date()
        line = next(x for x in self.cff().splitlines() if x.startswith("date-released:"))
        self.assertIn(line[16:-1], {str(today), str(today - datetime.timedelta(days=1))})

    def test_check_reports_whether_the_versions_match(self) -> None:
        result = run(self.root, "--check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("version 0.0.0, Cargo.toml 0.4.0", result.stderr)
        run(self.root, "--date", "2026-11-05")
        self.assertEqual(run(self.root, "--check").returncode, 0)

    def test_bad_input_exits_2_and_changes_nothing(self) -> None:
        cases = {
            "a date that is not YYYY-MM-DD": ("0.4.0", CFF, "2026-13-01"),
            "a date without dashes": ("0.4.0", CFF, "20261105"),
            "a version that is not MAJOR.MINOR.PATCH": ("0.4", CFF, "2026-11-05"),
            "no top-level version line": ("0.4.0", CFF.replace("version: 0.0.0\n", ""), "2026-11-05"),
            "two top-level version lines": ("0.4.0", CFF + "version: 1.0.0\n", "2026-11-05"),
        }
        for name, (version, cff, date) in cases.items():
            with self.subTest(name):
                self.write(version, cff)
                result = run(self.root, "--date", date)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(self.cff(), cff)

    def test_the_repository_files_are_in_step(self) -> None:
        result = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
