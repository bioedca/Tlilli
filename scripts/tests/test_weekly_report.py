"""Tests for scripts/weekly_report.py (D-084): its sections, and main() against a stub gh."""

import datetime
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))  # weekly_report imports tracking_issue
SPEC = importlib.util.spec_from_file_location("weekly_report", SCRIPTS / "weekly_report.py")
weekly = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(weekly)

UTC = datetime.UTC
NOW = datetime.datetime(2026, 11, 9, 5, 30, tzinfo=UTC)
WEEK = NOW - datetime.timedelta(days=7)
MONTH = datetime.datetime(2026, 11, 1, tzinfo=UTC)
RECENT = (datetime.datetime.now(UTC) - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
STUB = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[2:]  # after "api"
data = sys.stdin.read() if "--input" in args else ""
with open(os.environ["GH_LOG"], "a") as log:
    log.write(json.dumps({"args": args, "input": json.loads(data) if data else None}) + "\\n")
path = next(a for a in args if a.startswith("repos/"))
sys.exit(1) if os.environ.get("GH_FAIL") and path.endswith(os.environ["GH_FAIL"]) else None
name = "pulls" if "/pulls?" in path else "comments" if "/comments?" in path else "issues"
print(open(os.environ["GH_DATA"] + name).read() if "?" in path else '{"number": 7}')
"""


def pr(number: int, labels: tuple[str, ...], body: str = "", updated: str = "2026-11-05T10:00:00Z",
       merged: bool = True) -> dict:
    return {"number": number, "state": "closed" if merged else "open", "body": body,
            "merged_at": "2026-11-05T10:00:00Z" if merged else None, "updated_at": updated,
            "labels": list(labels)}


def comment(body: str, at: str, user: str = "bioedca", kind: str = "User") -> dict:
    return {"user": user, "user_type": kind, "created_at": at, "updated_at": at, "body": body}


class SectionTest(unittest.TestCase):
    def test_the_mutation_score_counts_timeouts_as_caught_and_names_the_missed(self) -> None:
        text = weekly.mutation(json.dumps({"caught": 5, "missed": 3, "timeout": 1, "unviable": 2,
                                           "missed_names": ["a.rs:1:1: replace || with &&"]}),
                               "success")
        self.assertIn("Score 66%: 5 caught, 1 timed out, 3 missed, 2 unviable", text)
        self.assertIn("- `a.rs:1:1: replace || with &&`\n- 2 more in the `mutants-out` artifact",
                      text)
        self.assertIn("none (no viable mutant)", weekly.mutation(json.dumps(
            {"caught": 0, "missed": 0, "timeout": 0, "unviable": 4}), "success"))
        self.assertIn("ended `failure`", weekly.mutation("", "failure"))

    def test_the_audit_lists_each_label_with_its_reason_line(self) -> None:
        prs = [pr(9, ("size:override", "needs-tests"), "x\nSize override:  big | `@team` table \n",
                  merged=False),
               pr(8, ("docs:not-needed",), "Docs not needed because:\n"),
               pr(7, ("size:override",), "Size override: old", updated="2026-11-01T00:00:00Z"),
               pr(6, ("size/S",))]
        self.assertEqual(weekly.audit(prs, WEEK).splitlines()[2:], [
            "| #9 | open | `size:override` | `big \\| '@team' table` |",
            "| #9 | open | `needs-tests` |  |",
            "| #8 | merged | `docs:not-needed` | no reason line |"])
        self.assertIn("No pull request", weekly.audit(prs[2:], WEEK))

    def test_the_sweep_section_lists_its_actions_and_old_branches(self) -> None:
        old = [{"name": f"claude/b{n}", "date": "2026-10-01", "pr": n or None, "merged": n % 2 == 1}
               for n in range(32)]
        text = weekly.sweep(json.dumps({"marked": [7, 8], "closed": [
            {"number": 6, "branch": "claude/`x`"}], "branches": old}), "success")
        self.assertIn("- Marked `status/stale`: #7, #8.", text)
        self.assertIn("- Closed after 21 days without activity: #6 (branch `claude/'x'`).", text)
        self.assertIn("no open pull request: 32 (none is deleted):", text)
        self.assertIn("  - `claude/b0`, last commit 2026-10-01, no pull request\n"
                      "  - `claude/b1`, last commit 2026-10-01, #1 merged\n"
                      "  - `claude/b2`, last commit 2026-10-01, #2 closed", text)
        self.assertTrue(text.endswith("  - 2 more"))
        empty = weekly.sweep(json.dumps({"marked": [], "closed": [], "branches": []}), "success")
        self.assertIn("none.\n- Closed after 21 days without activity: none.", empty)
        self.assertIn("ended `skipped`", weekly.sweep("", "skipped"))

    def test_pull_requests_are_read_page_by_page_until_one_predates_the_week(self) -> None:
        full = "".join(json.dumps(pr(n, ())) + "\n" for n in range(weekly.PAGE))
        old = json.dumps(pr(1, (), updated="2026-10-01T00:00:00Z"))
        with mock.patch.object(weekly, "gh", side_effect=[full, full, old]) as gh:
            self.assertEqual(len(weekly.pulls("o/r", WEEK)), 2 * weekly.PAGE + 1)
        self.assertEqual([c.args[0][-7:] for c in gh.call_args_list],
                         ["&page=1", "&page=2", "&page=3"])

    def test_the_budgets_count_requests_by_people_and_the_busiest_hour(self) -> None:
        comments = [
            comment("@coderabbitai review", "2026-11-06T07:00:00Z"),
            comment("Round 2.\n@coderabbitai full review", "2026-11-06T07:50:00Z"),
            comment("@CodeRabbitAI review", "2026-11-06T08:10:00Z"),
            comment("@coderabbitai resolve", "2026-11-06T09:30:00Z"),  # every command counts
            comment("Thanks, @coderabbitai review is done", "2026-11-06T07:20:00Z"),  # prose
            comment("@coderabbitai review", "2026-11-06T07:30:00Z", "coderabbitai[bot]", "Bot"),
            comment("@coderabbitai review", "2026-11-01T07:00:00Z"),  # before the week
            comment("<!-- greptile_summary -->\nReviews (2)", "2026-11-03T09:00:00Z",
                    "greptile-apps[bot]", "Bot"),
            comment("<!-- greptile_summary -->\n", "2026-11-04T09:00:00Z", "greptile-apps[bot]",
                    "Bot"),
            comment("<!-- greptile_summary -->\nReviews (5)", "2026-10-30T09:00:00Z",
                    "greptile-apps[bot]", "Bot")]
        text = weekly.budget(comments, WEEK, MONTH, NOW)
        self.assertIn("4 requests since 2026-11-02, at most 2 in one hour (from 2026-11-06 07:00 "
                      "UTC); the budget is 30 a week and 1 an hour", text)
        self.assertNotIn("are used", text)
        week = [comment("@coderabbitai review", f"2026-11-0{3 + i // 10}T{10 + i % 10}:00:00Z")
                for i in range(30)]
        self.assertIn("The week's 30 CodeRabbit requests are used",
                      weekly.budget(week, WEEK, MONTH, NOW))
        self.assertIn("- Greptile: 3 reviews in November 2026", text)
        self.assertNotIn("90%", text)
        many = [{**comments[7], "body": "<!-- greptile_summary -->\nReviews (18)"}]
        self.assertIn("90% of 20 is used before day 20", weekly.budget(many, WEEK, MONTH, NOW))

    def test_a_command_in_a_review_thread_counts_against_the_week(self) -> None:
        def rows(items: list[dict]) -> str:
            return "".join(json.dumps(c) + "\n" for c in items)
        top = [comment("@coderabbitai review", f"2026-11-0{3 + i // 10}T{10 + i % 10}:00:00Z")
               for i in range(29)]
        thread = [comment("@coderabbitai is this still needed?", "2026-11-06T12:00:00Z")]
        with mock.patch.object(weekly, "gh", side_effect=[rows(top), rows(thread)]) as gh:
            found = weekly.fetch_comments("o/r", "2026-11-01T00:00:00Z")
        self.assertEqual([c.args[1].split("?")[0] for c in gh.call_args_list],
                         ["repos/o/r/issues/comments", "repos/o/r/pulls/comments"])
        self.assertIn("The week's 30 CodeRabbit requests are used",
                      weekly.budget(found, WEEK, MONTH, NOW))


class MainTest(unittest.TestCase):
    def run_main(self, issues: list[dict], fail: str = "") -> list[dict]:
        with tempfile.TemporaryDirectory() as tmp:
            stub = Path(tmp, "gh")
            stub.write_text(STUB, encoding="utf-8")
            stub.chmod(0o755)
            data = {"pulls": [pr(5, ("size:override",), "Size override: x", updated=RECENT)],
                    "issues": issues,
                    "comments": [comment("@coderabbitai review", "2026-11-06T07:00:00Z")]}
            for name, rows in data.items():
                Path(tmp, f"data-{name}").write_text("".join(json.dumps(r) + "\n" for r in rows))
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}", "GH_LOG": f"{tmp}/log",
                   "GH_DATA": f"{tmp}/data-", "GITHUB_REPOSITORY": "o/r", "GITHUB_RUN_ID": "10",
                   "GITHUB_SERVER_URL": "https://github.com", "GITHUB_STEP_SUMMARY": f"{tmp}/sum",
                   "MUTANTS": '{"caught": 1, "missed": 1, "timeout": 0, "unviable": 0}',
                   "MUTANTS_RESULT": "success", "GH_FAIL": fail}  # main() reads the real clock
            done = subprocess.run([sys.executable, str(SCRIPTS / "weekly_report.py")], env=env,
                                  capture_output=True, check=False)
            self.assertEqual(done.returncode != 0, bool(fail), done.stderr)
            self.assertIn("Score 50%", Path(tmp, "sum").read_text())
            calls = [json.loads(line) for line in Path(tmp, "log").read_text().splitlines()]
            self.assertIn("/pulls/comments?since=", calls[2]["args"][1])  # review threads too
            self.assertIn("creator=github-actions%5Bbot%5D", calls[3]["args"][1])  # not by label
            return calls[4:]

    @staticmethod
    def issue(number: int, run: int, user="github-actions[bot]", state="open") -> dict:
        return {"number": number, "title": "Weekly report", "state": state, "user": user,
                "body": f"<!-- weekly-report run={run} -->\nold", "labels": []}

    def test_creates_the_issue_with_its_labels_and_comments_the_report(self) -> None:
        calls = self.run_main([self.issue(2, 1, user="someone")])
        self.assertEqual([c["args"][0] for c in calls],
                         ["repos/o/r/issues", "repos/o/r/issues/7/comments"])
        self.assertEqual(calls[0]["input"]["labels"], ["type/task", "area/ci"])
        self.assertTrue(calls[0]["input"]["body"].startswith("<!-- weekly-report run=10 -->\n"))
        self.assertIn("| #5 | merged | `size:override` | `x` |", calls[1]["input"]["body"])
        self.assertTrue(calls[1]["input"]["body"].startswith("## "))

    def test_replaces_the_body_of_the_oldest_issue_and_reopens_it(self) -> None:
        calls = self.run_main([self.issue(3, 9, state="closed"), self.issue(4, 9)])
        self.assertEqual([c["args"][:3] for c in calls], [
            ["repos/o/r/issues/3/comments", "--input", "-"], ["-X", "PATCH", "repos/o/r/issues/3"]])
        self.assertEqual(calls[1]["input"]["state"], "open")

    def test_a_failed_comment_leaves_last_weeks_body_in_place(self) -> None:
        calls = self.run_main([self.issue(3, 9)], fail="/comments")
        self.assertEqual([c["args"][0] for c in calls], ["repos/o/r/issues/3/comments"])

    def test_a_run_older_than_the_last_report_changes_nothing(self) -> None:
        self.assertEqual(self.run_main([self.issue(3, 11)]), [])


if __name__ == "__main__":
    unittest.main()
