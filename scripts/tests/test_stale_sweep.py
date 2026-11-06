"""Tests for scripts/stale_sweep.py (PR-PRQ-005, D-084): its rules, and main() against a stub gh."""

import datetime
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))  # stale_sweep imports tracking_issue
SPEC = importlib.util.spec_from_file_location("stale_sweep", SCRIPTS / "stale_sweep.py")
sweep = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sweep)

NOW = datetime.datetime.now(datetime.UTC)  # main() reads the real clock
STUB = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[2:]  # after "api"
data = sys.stdin.read() if "--input" in args else ""
with open(os.environ["GH_LOG"], "a") as log:
    log.write(json.dumps({"args": args, "input": json.loads(data) if data else None}) + "\\n")
path = next(a for a in args if a.startswith("repos/")).split("?")[0]
print("{}" if data else json.load(open(os.environ["GH_DATA"])).get(path, ""))
"""


def ago(days: float) -> str:
    return (NOW - datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")


def pr(number: int, age: float, labels: tuple[str, ...] = (), draft: bool = True,
       user: str = "bioedca", head: str = "", state: str = "open") -> dict:
    return {"number": number, "state": state, "draft": draft, "merged_at": None,
            "created_at": ago(age), "user": user, "head": head or f"claude/b{number}",
            "sha": f"s{number}",
            "head_repo": "o/r", "labels": list(labels)}


class RuleTest(unittest.TestCase):
    def test_plan_marks_at_7_days_closes_at_21_idle_and_skips_the_exempt(self) -> None:
        plan = sweep.plan
        self.assertIsNone(plan(pr(1, 6), NOW, NOW, False))
        self.assertEqual(plan(pr(1, 8), NOW, NOW, False), "mark")
        self.assertIsNone(plan(pr(1, 8, (sweep.STALE,)), NOW, NOW, True))
        self.assertEqual(plan(pr(1, 8, (sweep.STALE,)), NOW, NOW, False), "mark")  # no comment
        self.assertEqual(plan(pr(1, 8), NOW, NOW, True), "mark")  # no label
        self.assertEqual(plan(pr(1, 30, (sweep.STALE,)), NOW - sweep.IDLE, NOW, True), "close")
        self.assertEqual(plan(pr(1, 30, ("gate",)), NOW - sweep.IDLE, NOW, False), "close")  # Draft
        for kept in (pr(1, 30, ("gate",), draft=False), pr(1, 30, user="dependabot[bot]"),
                     pr(1, 30, head="release-plz-2026-11-06")):
            self.assertIsNone(plan(kept, NOW - sweep.IDLE, NOW, False))

    def test_activity_leaves_out_only_the_sweeps_own_comments(self) -> None:
        mine = {"user": sweep.BOT, "created_at": ago(1), "body": f"{sweep.MARK}\nmarked"}
        other = {"user": "coderabbitai[bot]", "created_at": ago(3), "body": "skipped"}
        self.assertEqual(sweep.active(pr(1, 30), ago(25), [mine], []), sweep.when(ago(25)))
        review = {"submitted_at": ago(9)}
        self.assertEqual(sweep.active(pr(1, 30), ago(25), [mine, other], [review]),
                         sweep.when(ago(3)))
        self.assertEqual(sweep.active(pr(1, 2), ago(40), [], []), sweep.when(ago(2)))  # opened late

    def test_branches_lists_old_ones_without_an_open_pr_and_never_main(self) -> None:
        refs = [["main", ago(30)], ["HEAD", ago(30)], ["claude/open", ago(20)],
                ["claude/merged", ago(10)], ["claude/new", ago(2)], ["claude/none", ago(15)]]
        prs = [pr(1, 20, head="claude/open"), {**pr(2, 12, head="claude/merged", state="closed"),
                                               "merged_at": ago(11)}]
        self.assertEqual(sweep.branches(refs, prs, NOW), [
            {"name": "claude/none", "date": ago(15)[:10], "pr": None, "merged": False},
            {"name": "claude/merged", "date": ago(10)[:10], "pr": 2, "merged": True}])
        reopened = [pr(1, 20, head="claude/none"), pr(2, 12, head="claude/none", state="closed")]
        self.assertEqual(sweep.branches(refs[5:], reopened, NOW), [])  # #1 is open again


class MainTest(unittest.TestCase):
    def run_main(self, *args: str, extra: dict | None = None,
                 prs: list[dict] | None = None) -> tuple[dict, list[dict]]:
        prs = prs or [pr(1, 8), pr(2, 40, (sweep.STALE,)), pr(3, 40, user="dependabot[bot]"),
                      {**pr(4, 40), "head_repo": "fork/r"}]  # a fork's PR is not this repository's
        data = {"repos/o/r/pulls": "".join(json.dumps(p) + "\n" for p in prs)}
        for n in (1, 2, 3):  # no check suite or force-push: the commit date stands for the push
            data |= {f"repos/o/r/pulls/{n}/{path}": "" for path in ("comments", "reviews")}
            data |= {f"repos/o/r/commits/s{n}": ago(30), f"repos/o/r/issues/{n}/comments": "",
                     f"repos/o/r/commits/s{n}/check-suites": "",
                     f"repos/o/r/issues/{n}/timeline": ""}
        data |= extra or {}
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "gh").write_text(STUB, encoding="utf-8")
            Path(tmp, "gh").chmod(0o755)
            Path(tmp, "data").write_text(json.dumps(data), encoding="utf-8")
            git = ["git", "-C", tmp, "-c", "user.name=t", "-c", "user.email=t@example.com"]
            subprocess.run([*git, "init", "-q"], check=True)
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", "x"], check=True,
                           env={**os.environ, "GIT_COMMITTER_DATE": ago(9)})
            for branch in ("gone", "b1", "b2"):  # #1 stays open; #2 is closed by this run
                subprocess.run([*git, "update-ref", f"refs/remotes/origin/claude/{branch}", "HEAD"],
                               check=True)
            env = {**os.environ, "PATH": f"{tmp}:{os.environ['PATH']}", "GH_LOG": f"{tmp}/log",
                   "GH_DATA": f"{tmp}/data", "GITHUB_REPOSITORY": "o/r"}
            out = subprocess.run([sys.executable, str(SCRIPTS / "stale_sweep.py"), *args], cwd=tmp,
                                 env=env, check=True, capture_output=True, text=True).stdout
            calls = [json.loads(line) for line in Path(tmp, "log").read_text().splitlines()]
        return json.loads(out), [c for c in calls if c["input"] is not None]

    def test_marks_the_old_pr_closes_the_idle_one_and_lists_the_old_branch(self) -> None:
        summary, writes = self.run_main()
        self.assertEqual(summary["marked"], [1])
        self.assertEqual(summary["closed"], [{"number": 2, "branch": "claude/b2"}])
        self.assertEqual([b["name"] for b in summary["branches"]], ["claude/b2", "claude/gone"])
        paths = [w["args"][2] if w["args"][0] == "-X" else w["args"][0] for w in writes]
        self.assertEqual(paths, [
            "repos/o/r/issues/1/labels", "repos/o/r/issues/1/comments",
            "repos/o/r/issues/2/comments", "repos/o/r/pulls/2"])
        self.assertEqual(writes[0]["input"], {"labels": [sweep.STALE]})
        self.assertIn("`claude/b2` stays", writes[2]["input"]["body"])
        self.assertEqual(writes[3]["input"], {"state": "closed"})

    def test_a_late_push_a_force_push_a_reopen_or_a_thread_reply_keeps_the_pr_open(self) -> None:
        reply = json.dumps({"user": "bioedca", "created_at": ago(2), "body": "a reply"})
        for extra in ({"repos/o/r/commits/s2/check-suites": f"{ago(1)}\n{ago(3)}"},
                      {"repos/o/r/commits/s2/check-suites": ago(30),  # a force-push or a reopen
                       "repos/o/r/issues/2/timeline": ago(1)},
                      {"repos/o/r/pulls/2/comments": reply}):
            summary, _ = self.run_main("--dry-run", extra=extra)
            self.assertEqual(summary["closed"], [], extra)

    def test_a_half_done_mark_is_finished_and_a_whole_one_left_alone(self) -> None:
        note = json.dumps({"user": sweep.BOT, "created_at": ago(1), "body": f"{sweep.MARKED}\n"})
        for labels, comments, want in (((sweep.STALE,), "", ["repos/o/r/issues/1/comments"]),
                                       ((), note, ["repos/o/r/issues/1/labels"]),
                                       ((sweep.STALE,), note, [])):
            summary, writes = self.run_main(prs=[pr(1, 8, labels)],
                                            extra={"repos/o/r/issues/1/comments": comments})
            self.assertEqual(summary["marked"], [1] if want else [])
            self.assertEqual([w["args"][0] for w in writes], want)

    def test_a_dry_run_changes_nothing(self) -> None:
        summary, writes = self.run_main("--dry-run")
        self.assertEqual((summary["marked"], len(summary["closed"]), writes), ([1], 1, []))


if __name__ == "__main__":
    unittest.main()
