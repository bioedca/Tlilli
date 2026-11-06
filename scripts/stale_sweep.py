#!/usr/bin/env python3
"""The weekly stale sweep of pull requests and branches (PR-PRQ-005, PR-GIT-004, D-084).

An open PR older than 7 days gets status/stale and one comment; after 21 days without a push,
comment or review other than the sweep's own, it is closed with a comment naming its branch. Ready
gated PRs, Dependabot's PRs and the release-plz PR are exempt. Branches older than 7 days with no
open PR are listed, never deleted. Prints a one-line JSON summary for weekly_report.py.
Usage: stale_sweep.py [--dry-run]   (in a full clone: branch dates come from refs/remotes/origin)
"""

import argparse
import datetime
import json
import os
import subprocess
import sys

from tracking_issue import BOT, gh

STALE = "status/stale"
MARK = "<!-- stale-sweep -->"  # on the sweep's own comments, which are no activity
AGE = datetime.timedelta(days=7)
IDLE = datetime.timedelta(days=21)
when = datetime.datetime.fromisoformat


def lines(text: str) -> list[dict]:
    return [json.loads(line) for line in filter(str.strip, text.splitlines())]


def exempt(pr: dict) -> bool:
    """A Ready gated PR waits on the maintainer; closing a Dependabot PR makes Dependabot skip
    that version; the release-plz PR stays open until the next release."""
    return (("gate" in pr["labels"] and not pr["draft"]) or pr["user"] == "dependabot[bot]"
            or pr["head"].startswith("release-plz-"))


def active(pr: dict, pushed: str, comments: list[dict], reviews: list[dict]) -> datetime.datetime:
    """The PR's last activity: its opening, last push, or a comment or review not by the sweep."""
    times = [when(pr["created_at"]), when(pushed)]
    times += [when(c["created_at"]) for c in comments
              if not (c["user"] == BOT and MARK in (c["body"] or ""))]
    return max(times + [when(r["submitted_at"]) for r in reviews if r["submitted_at"]])


def plan(pr: dict, last: datetime.datetime, now: datetime.datetime) -> str | None:
    """What the sweep does to one open PR: close it, mark it, or nothing."""
    if exempt(pr):
        return None
    if now - last >= IDLE:
        return "close"
    if now - when(pr["created_at"]) >= AGE and STALE not in pr["labels"]:
        return "mark"
    return None


def branches(refs: list[list[str]], prs: list[dict], now: datetime.datetime) -> list[dict]:
    """Branches whose last commit is over 7 days old and that have no open PR, oldest first."""
    newest = {pr["head"]: pr for pr in sorted(prs, key=lambda pr: pr["number"])}
    busy = {pr["head"] for pr in prs if pr["state"] == "open"}  # any open PR, not just the newest
    old = []
    for name, date in refs:
        pr = newest.get(name)
        if name in ("HEAD", "main") or name in busy or now - when(date) < AGE:
            continue
        old.append({"name": name, "date": date[:10], "pr": pr["number"] if pr else None,
                    "merged": bool(pr and pr["merged_at"])})
    return sorted(old, key=lambda branch: branch["date"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--dry-run", action="store_true", help="report the plan, change nothing")
    dry = parser.parse_args().dry_run
    repo = os.environ["GITHUB_REPOSITORY"]
    now = datetime.datetime.now(datetime.UTC)
    prs = [pr for pr in lines(gh("--paginate", f"repos/{repo}/pulls?state=all&per_page=100", "--jq",
                                 ".[] | {number, state, draft, merged_at, created_at, user: "
                                 ".user.login, head: .head.ref, sha: .head.sha, head_repo: "
                                 ".head.repo.full_name, labels: [.labels[].name]}"))
           if pr["head_repo"] == repo]
    refs = [line.split(" ", 1) for line in subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:lstrip=3) %(committerdate:iso-strict)",
         "refs/remotes/origin"], capture_output=True, text=True, check=True).stdout.splitlines()]
    marked, closed = [], []
    for pr in (pr for pr in prs if pr["state"] == "open"):
        n = pr["number"]
        # GitHub makes a commit's first check suite when the commit is pushed, so that dates the
        # last push even when the commit itself is older; without one, the commit date stands.
        suites = gh("--paginate", f"repos/{repo}/commits/{pr['sha']}/check-suites?per_page=100",
                    "--jq", ".check_suites[].created_at").split()
        pushed = min(suites, default=None) or gh(f"repos/{repo}/commits/{pr['sha']}", "--jq",
                                                  ".commit.committer.date").strip()
        comments = [c for path in (f"issues/{n}/comments", f"pulls/{n}/comments")  # threads too
                    for c in lines(gh("--paginate", f"repos/{repo}/{path}?per_page=100", "--jq",
                                      ".[] | {user: .user.login, created_at, body}"))]
        reviews = lines(gh("--paginate", f"repos/{repo}/pulls/{n}/reviews?per_page=100", "--jq",
                           ".[] | {submitted_at}"))
        action = plan(pr, active(pr, pushed, comments, reviews), now)
        if action == "mark":
            marked.append(n)
            if not dry:
                gh(f"repos/{repo}/issues/{n}/labels", payload={"labels": [STALE]})
                gh(f"repos/{repo}/issues/{n}/comments", payload={"body": (
                    f"{MARK}\nThis pull request is more than 7 days old (`PR-GIT-004`), so the "
                    f"weekly sweep marked it `{STALE}`. After 21 days without a push, comment or "
                    "review it is closed (`PR-PRQ-005`, D-084).")})
        elif action == "close":
            closed.append({"number": n, "branch": pr["head"]})
            if not dry:
                gh(f"repos/{repo}/issues/{n}/comments", payload={"body": (
                    f"{MARK}\nClosed by the weekly sweep after 21 days without a push, comment or "
                    f"review (`PR-PRQ-005`, D-084). The branch `{pr['head']}` stays: reopen this "
                    "pull request, or open a new one from it, to go on.")})
                gh("-X", "PATCH", f"repos/{repo}/pulls/{n}", payload={"state": "closed"})
        print(f"#{n}: {action or 'nothing'}", file=sys.stderr)
    print(json.dumps({"marked": marked, "closed": closed, "branches": branches(refs, prs, now)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
