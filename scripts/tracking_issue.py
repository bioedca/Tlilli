#!/usr/bin/env python3
"""Keep the one tracking issue of a nightly or weekly job (PR-CI-014).

A red run opens or reopens the job's issue and comments; a green run closes it. The body's first
line records the day the job turned red: the third red day adds priority/P1, or the first with --p1.
Only issues that github-actions[bot] opened count, so nobody else's issue can stand in for one.
Usage: tracking_issue.py JOB RESULT [--area ci|docs] [--p1]   (RESULT: a job's needs.<id>.result)
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys

BOT = "github-actions[bot]"
P1 = "priority/P1"
MARK = re.compile(r"<!-- tracking job=(\S+) red_since=(\S+) -->")


def red_since(issue: dict | None, job: str) -> datetime.date | None:
    """The day an open issue's job turned red, or None when it is green or unreadable."""
    if issue is None or issue["state"] != "open":
        return None
    first = (issue.get("body") or "").split("\n", 1)[0]
    match = MARK.fullmatch(first)
    if not match or match.group(1) != job:
        return None
    try:
        return datetime.date.fromisoformat(match.group(2))
    except ValueError:
        return None


def render(job: str, since: datetime.date | None, today: datetime.date, result: str, url: str) -> str:
    red = f"Red since {since}." if since else "Green."
    return (f"<!-- tracking job={job} red_since={since or 'none'} -->\n"
            f"Tracking issue of the `{job}` job (`PR-CI-014`), kept by `scripts/tracking_issue.py`: "
            "a red run opens it and comments, a green run closes it, and a third red day in a row "
            f"adds `{P1}`. Leave the first line as it is.\n\n"
            f"Last run: {today}, {result}, {url}. {red}\n")


def plan(job: str, issue: dict | None, result: str, today: datetime.date, url: str,
         p1_first: bool) -> dict | None:
    """What one run changes: body, state, comment, and the P1 label to add or remove."""
    if result not in ("success", "failure") or (result == "success" and issue is None):
        return None  # cancelled or skipped runs say nothing; a green job needs no issue
    labels = set(issue["labels"]) if issue else set()
    if result == "success":
        return {"body": render(job, None, today, result, url), "state": "closed",
                "comment": f"Green on {today}: {url}" if issue["state"] == "open" else None,
                "add_p1": False, "remove_p1": P1 in labels}
    since = red_since(issue, job) or today
    days = (today - since).days + 1
    note = f" (red since {since}, day {days})" if days > 1 else ""
    return {"body": render(job, since, today, result, url), "state": "open",
            "comment": f"Red on {today}: {url}{note}",
            "add_p1": (p1_first or days >= 3) and P1 not in labels, "remove_p1": False}


def gh(*args: str, payload: dict | None = None) -> str:
    cmd = ["gh", "api", *args] + (["--input", "-"] if payload is not None else [])
    data = json.dumps(payload) if payload is not None else None
    return subprocess.run(cmd, input=data, capture_output=True, text=True, check=True).stdout


def find(repo: str, title: str) -> dict | None:
    """The oldest issue with this title that the bot opened, open or closed."""
    text = gh("--paginate", f"repos/{repo}/issues?state=all&labels=type/task&sort=created"
              "&direction=asc&per_page=100", "--jq", '.[] | select(.pull_request == null) | '
              '{number, title, state, body, user: .user.login, labels: [.labels[].name]}')
    for line in filter(str.strip, text.splitlines()):
        issue = json.loads(line)
        if issue["user"] == BOT and issue["title"] == title:
            return issue
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("job")
    parser.add_argument("result")
    parser.add_argument("--area", choices=["ci", "docs"], default="ci")
    parser.add_argument("--p1", action="store_true", help="priority/P1 on the first red run")
    args = parser.parse_args()
    repo = os.environ["GITHUB_REPOSITORY"]
    url = f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    title = f"Tracking: {args.job}"
    today = datetime.datetime.now(datetime.UTC).date()
    issue = find(repo, title)
    change = plan(args.job, issue, args.result, today, url, args.p1)
    if change is None:
        print(f"{title}: {args.result}, nothing to record")
        return 0
    if issue is None:
        labels = ["type/task", f"area/{args.area}"] + ([P1] if change["add_p1"] else [])
        number = json.loads(gh(f"repos/{repo}/issues", payload={
            "title": title, "body": change["body"], "labels": labels}))["number"]
    else:
        number = issue["number"]
        edit = {"body": change["body"], "state": change["state"]}
        if change["state"] == "closed":
            edit["state_reason"] = "completed"
        gh("-X", "PATCH", f"repos/{repo}/issues/{number}", payload=edit)
        if change["add_p1"]:
            gh(f"repos/{repo}/issues/{number}/labels", payload={"labels": [P1]})
        if change["remove_p1"]:
            gh("-X", "DELETE", f"repos/{repo}/issues/{number}/labels/priority%2FP1")
    if change["comment"] and issue is not None:  # a new issue's body already names the run
        gh(f"repos/{repo}/issues/{number}/comments", payload={"body": change["comment"]})
    print(f"{title}: {args.result}, issue #{number} {change['state']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
