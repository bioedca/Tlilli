"""Tests for scripts/tracking_issue.py (PR-CI-014): plan() directly, and main() against a stub gh."""

import datetime
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "tracking_issue.py"
SPEC = importlib.util.spec_from_file_location("tracking_issue", SCRIPT)
tracking = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracking)

JOB = "nightly/fuzz"
TODAY = datetime.date(2026, 11, 6)
URL = "https://github.com/o/r/actions/runs/1"
STUB = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[2:]  # after "api"
data = sys.stdin.read() if "--input" in args else ""
with open(os.environ["GH_LOG"], "a") as log:
    log.write(json.dumps({"args": args, "input": json.loads(data) if data else None}) + "\\n")
print(open(os.environ["GH_ISSUES"]).read() if "--paginate" in args else '{"number": 7}')
"""


def issue(state: str, since: str, labels: tuple[str, ...] = (), job: str = JOB) -> dict:
    return {"number": 3, "title": f"Tracking: {job}", "state": state, "user": tracking.BOT,
            "body": f"<!-- tracking job={job} red_since={since} -->\ntext", "labels": list(labels)}


class PlanTest(unittest.TestCase):
    def plan(self, current: dict | None, result: str, p1_first: bool = False) -> dict | None:
        return tracking.plan(JOB, current, result, TODAY, URL, p1_first)

    def test_a_first_red_run_opens_the_issue_without_p1(self) -> None:
        change = self.plan(None, "failure")
        self.assertEqual((change["state"], change["add_p1"]), ("open", False))
        self.assertTrue(change["body"].startswith(f"<!-- tracking job={JOB} red_since=2026-11-06 -->\n"))

    def test_the_third_red_day_adds_p1(self) -> None:
        self.assertFalse(self.plan(issue("open", "2026-11-05"), "failure")["add_p1"])
        change = self.plan(issue("open", "2026-11-04"), "failure")
        self.assertTrue(change["add_p1"])
        self.assertIn("red since 2026-11-04, day 3", change["comment"])
        self.assertIn("red_since=2026-11-04 ", change["body"])
        self.assertFalse(self.plan(issue("open", "2026-11-01", (tracking.P1,)), "failure")["add_p1"])
        self.assertTrue(self.plan(None, "failure", p1_first=True)["add_p1"])  # --p1: the first day

    def test_red_counts_from_today_when_the_issue_was_green_or_unreadable(self) -> None:
        cases = {"closed": issue("closed", "2026-10-01"), "bad date": issue("open", "2026-13-01"),
                 "another job": issue("open", "2026-10-01", job="nightly/links")}
        for name, current in cases.items():
            with self.subTest(name):
                change = self.plan(current, "failure")
                self.assertIn("red_since=2026-11-06 ", change["body"])
                self.assertFalse(change["add_p1"])

    def test_a_green_run_closes_the_issue_and_removes_p1(self) -> None:
        change = self.plan(issue("open", "2026-11-01", (tracking.P1,)), "success")
        self.assertEqual((change["state"], change["remove_p1"]), ("closed", True))
        self.assertEqual(change["comment"], f"Green on 2026-11-06: {URL}")
        self.assertIn("red_since=none ", change["body"])
        self.assertIsNone(self.plan(issue("closed", "none"), "success")["comment"])

    def test_nothing_to_record(self) -> None:
        for current, result in [(None, "success"), (None, "cancelled"), (issue("open", "x"), "skipped")]:
            with self.subTest(result):
                self.assertIsNone(self.plan(current, result))


class MainTest(unittest.TestCase):
    def run_main(self, issues: list[dict], *args: str) -> list[dict]:
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp, "gh")
            stub.write_text(STUB, encoding="utf-8")
            stub.chmod(0o755)
            Path(tmp, "issues").write_text("".join(json.dumps(i) + "\n" for i in issues))
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}", "GH_LOG": f"{tmp}/log",
                   "GH_ISSUES": f"{tmp}/issues", "GITHUB_REPOSITORY": "o/r",
                   "GITHUB_SERVER_URL": "https://github.com", "GITHUB_RUN_ID": "1"}
            subprocess.run([sys.executable, str(SCRIPT), *args], env=env, check=True,
                           capture_output=True)
            return [json.loads(line) for line in Path(tmp, "log").read_text().splitlines()]

    def test_creates_the_issue_and_ignores_one_that_someone_else_opened(self) -> None:
        forged = {**issue("open", "2026-01-01"), "user": "someone"}
        calls = self.run_main([forged], JOB, "failure", "--area", "docs", "--p1")
        self.assertEqual([c["args"][0] for c in calls], ["--paginate", "repos/o/r/issues"])
        self.assertEqual(calls[1]["input"]["labels"], ["type/task", "area/docs", tracking.P1])
        self.assertEqual(calls[1]["input"]["title"], f"Tracking: {JOB}")

    def test_updates_an_open_issue_adds_p1_and_comments(self) -> None:
        calls = self.run_main([issue("open", "2026-01-01")], JOB, "failure")
        self.assertEqual([c["args"][:3] for c in calls[1:]], [
            ["-X", "PATCH", "repos/o/r/issues/3"], ["repos/o/r/issues/3/labels", "--input", "-"],
            ["repos/o/r/issues/3/comments", "--input", "-"]])
        self.assertEqual(calls[1]["input"]["state"], "open")
        self.assertEqual(calls[2]["input"], {"labels": [tracking.P1]})
