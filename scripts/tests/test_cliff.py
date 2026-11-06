"""Tests for cliff.toml (PR-DOC-010) on a throwaway repository; skipped without git-cliff."""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

CONFIG = Path(__file__).resolve().parent.parent.parent / "cliff.toml"
COMMITS = [
    "feat(core): add the event log",
    "v0.1.0",  # an entry that starts with "v" tags the commit before it
    "docs(docs): describe the deprecated flag",
    "fix(ci): repair the size check",
    "chore(deps): bump serde from 1.0.1 to 1.0.2",
    "chore(deps): bump openssl\n\nSecurity: RUSTSEC-2026-0001",
    "feat(mcp)!: remove the legacy list tool",
    "fix(cli): remove the raw alias\n\nBREAKING CHANGE: use --plain",
    "v0.2.0-beta.1",  # not stable: the commits before it go into 0.2.0
    "feat(cli): deprecate the raw flag",
    "perf(core): cache the style sheet",
    "build(repo): raise the MSRV to 1.98",
    "fix(core)!: change the event id format\n\nBREAKING CHANGE: ids are uuids",
    "chore(release): v0.2.0",
]
WANT = """## [0.2.0] - DATE

### Changed

- **core:** Cache the style sheet
- **repo:** Raise the MSRV to 1.98

### Deprecated

- **cli:** Deprecate the raw flag

### Removed

- **mcp:** **Breaking:** Remove the legacy list tool
- **cli:** **Breaking:** Remove the raw alias

### Fixed

- **core:** **Breaking:** Change the event id format

### Security

- **deps:** Bump openssl

## [0.1.0] - DATE

### Added

- **core:** Add the event log

[0.2.0]: https://github.com/bioedca/Tlilli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/bioedca/Tlilli/releases/tag/v0.1.0
"""


@unittest.skipUnless(shutil.which("git-cliff"), "git-cliff is not installed")
class CliffTest(unittest.TestCase):
    def test_groups_omissions_and_releases_follow_pr_doc_010(self) -> None:
        with tempfile.TemporaryDirectory() as repo:
            git = ["git", "-C", repo, "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run([*git, "init", "-q", "-b", "main"], check=True)
            for entry in COMMITS:
                step = ["tag"] if entry.startswith("v") else ["commit", "-q", "--allow-empty", "-m"]
                subprocess.run([*git, *step, entry], check=True)
            out = subprocess.run(["git-cliff", "--offline", "--config", str(CONFIG), "--tag",
                                  "v0.2.0", "--repository", repo], capture_output=True,
                                 text=True, check=True).stdout
        body = out[out.index("## [0.2.0]"):]
        date = body.split(" - ", 1)[1].split("\n", 1)[0]
        self.assertEqual(body, WANT.replace("DATE", date))
