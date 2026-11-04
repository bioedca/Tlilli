"""Tests for scripts/gen_fixtures.py (PR-TST-016): run it as a subprocess, writing only into
temporary directories. Run with `python3 -B -m unittest discover -s scripts/tests`.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "gen_fixtures.py"


def gen(*args: str) -> subprocess.CompletedProcess[str]:
    # Each subprocess gets its own random PYTHONHASHSEED, so the comparisons below also show that
    # the output does not depend on hash order.
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, check=False)


def files_under(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


class GenFixturesTest(unittest.TestCase):
    def generate(self, seed: int) -> dict[str, bytes]:
        with tempfile.TemporaryDirectory() as out:
            result = gen("--seed", str(seed), "--out", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            return files_under(Path(out))

    def test_same_seed_gives_byte_identical_files(self) -> None:
        first = self.generate(7)
        self.assertIn("manuscripts/synthetic-en-001.md", first)
        self.assertEqual(first, self.generate(7))

    def test_other_seed_gives_other_content_under_the_same_names(self) -> None:
        first, other = self.generate(7), self.generate(8)
        self.assertEqual(first.keys(), other.keys())
        # The first line names the seed; the text below it must differ too.
        for name in first:
            self.assertNotEqual(first[name].split(b"\n", 1)[1], other[name].split(b"\n", 1)[1])

    def test_dry_run_writes_nothing_and_reports_the_digests_it_would_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dry = gen("--dry-run", "--seed", "7", "--out", str(Path(tmp) / "dry"))
            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertEqual(list(Path(tmp).iterdir()), [])
            wet = gen("--seed", "7", "--out", str(Path(tmp) / "wet"))
            self.assertEqual(wet.returncode, 0, wet.stderr)
        self.assertIn("would write manuscripts/", dry.stdout)
        self.assertEqual(dry.stdout.replace("would write", "wrote"), wet.stdout)

    def test_kinds_without_a_generator_and_unknown_kinds_exit_2(self) -> None:
        for kind in ("papers", "revisions", "no-such-kind"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as out:
                result = gen(kind, "--out", out)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(list(Path(out).iterdir()), [])

    def test_list_prints_every_kind(self) -> None:
        result = gen("--list")
        self.assertEqual(result.returncode, 0, result.stderr)
        kinds = ("manuscripts", "revisions", "papers", "histories", "transcripts", "http", "db")
        for kind in kinds:
            self.assertIn(kind, result.stdout)


if __name__ == "__main__":
    unittest.main()
