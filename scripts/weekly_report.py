#!/usr/bin/env python3
"""Write the `Weekly report` issue of weekly.yml for the Monday triage (PRD 33 §1, D-084).

The mutation score of tlilli-core, the week's audited labels and the review budgets: each run
replaces the body and adds the same report as a comment, so past weeks stay readable.
Environment: MUTANTS (the mutants job's JSON summary, empty if it did not finish), MUTANTS_RESULT.
"""

import datetime
import json
import os
import re
import sys

from tracking_issue import find, gh

TITLE = "Weekly report"
MARK = re.compile(r"<!-- weekly-report run=(\d+) -->")
AUDITED = ("docs:not-needed", "size:override", "needs-tests")
REASONS = {"docs:not-needed": "Docs not needed because", "size:override": "Size override"}
REQUEST = re.compile(r"^\s*@coderabbitai (full )?review\b", re.IGNORECASE | re.MULTILINE)
HOURLY_CAP = 6  # CodeRabbit requests in any 60 minutes, across the repository (D-062)
GREPTILE_BUDGET = 20  # reviews a month, the top of D-021's 15 to 20
PAGE = 100
when = datetime.datetime.fromisoformat  # reads GitHub's `...Z` stamps since Python 3.11


def quote(text: str) -> str:
    """Text from a pull request as a code span, so a mention or Markdown in it does nothing."""
    return "`" + " ".join(text.replace("`", "'").split()) + "`"


def reason(body: str | None, key: str) -> str | None:
    """The value of the body's first `<key>: <value>` line, as scripts/pr_checks.sh reads it."""
    for line in (body or "").splitlines():
        if line.startswith(f"{key}:") and line[len(key) + 1:].strip():
            return line[len(key) + 1:].strip()
    return None


def mutation(summary: str, result: str) -> str:
    if result != "success" or not summary:
        return f"Not measured: the `mutants` job ended `{result or 'unknown'}`; see its issue."
    data = json.loads(summary)
    killed = data["caught"] + data["timeout"]  # a mutant that hangs the tests is caught by them
    tested = killed + data["missed"]
    score = f"{100 * killed // tested}%" if tested else "none (no viable mutant)"
    lines = [(f"Score {score}: {data['caught']} caught, {data['timeout']} timed out, "
              f"{data['missed']} missed, {data['unviable']} unviable. The target is 70% by v0.4.")]
    names = data.get("missed_names") or []
    if names:
        lines += ["", "Missed (those in `model`, `event` and `segment` become test issues):"]
        lines += [f"- {quote(name)}" for name in names]
        if data["missed"] > len(names):
            lines.append(f"- {data['missed'] - len(names)} more in the `mutants-out` artifact")
    return "\n".join(lines)


def audit(prs: list[dict], since: datetime.datetime) -> str:
    """One row for each audited label on a pull request updated since the last report."""
    rows = []
    for pr in (pr for pr in prs if when(pr["updated_at"]) >= since):
        state = "merged" if pr["merged_at"] else pr["state"]
        for label in (label for label in AUDITED if label in pr["labels"]):
            why = reason(pr["body"], REASONS[label]) if label in REASONS else None
            text = quote(why).replace("|", "\\|") if why else ("no reason line" if label in REASONS
                                                                else "")
            rows.append(f"| #{pr['number']} | {state} | `{label}` | {text} |")
    if not rows:
        return "No pull request updated this week has an audited label."
    table = ["| Pull request | State | Label | Reason |", "| --- | --- | --- | --- |", *rows]
    if len(prs) >= PAGE and when(prs[-1]["updated_at"]) >= since:
        table += ["", f"Only the {PAGE} most recently updated pull requests were read."]
    return "\n".join(table)


def budget(comments: list[dict], week: datetime.datetime, month: datetime.datetime,
           now: datetime.datetime) -> str:
    asks = sorted(when(c["created_at"]) for c in comments if c["user_type"] != "Bot"
                  and when(c["created_at"]) >= week and REQUEST.search(c["body"] or ""))
    peak, start = 0, None
    for i, first in enumerate(asks):
        count = sum(1 for t in asks[i:] if t < first + datetime.timedelta(hours=1))
        if count > peak:
            peak, start = count, first
    busiest = f", at most {peak} in one hour (from {start:%Y-%m-%d %H:%M} UTC)" if start else ""
    reviews = 0
    for c in comments:
        if (c["user"] == "greptile-apps[bot]" and when(c["updated_at"]) >= month
                and "<!-- greptile_summary -->" in (c["body"] or "")):
            count = re.search(r"Reviews \((\d+)\)", c["body"])
            reviews += int(count.group(1)) if count else 1
    lines = [(f"- CodeRabbit: {len(asks)} requests since {week:%Y-%m-%d}{busiest}; the threshold "
              f"is {HOURLY_CAP} an hour (D-062). Local `coderabbit review` runs count too but do "
              "not show here."),
             (f"- Greptile: {reviews} reviews in {month:%B %Y}, against a budget of 15 to "
              f"{GREPTILE_BUDGET} (D-021). The count includes earlier reviews of a pull request "
              "that Greptile also reviewed this month.")]
    if reviews >= GREPTILE_BUDGET * 0.9 and now.day < 20:
        lines.append(f"- 90% of {GREPTILE_BUDGET} is used before day 20: `review:deep` requests "
                     "wait for next month (R-11).")
    return "\n".join(lines)


def render(run: int, url: str, today: datetime.date,
           sections: list[tuple[str, str]]) -> tuple[str, str]:
    """The issue body and the comment, which is the same report without the header."""
    report = f"## {today} ([run]({url}))\n\n" + "\n\n".join(
        f"### {title}\n\n{text}" for title, text in sections) + "\n"
    header = (f"<!-- weekly-report run={run} -->\nThe report of `weekly.yml` for the Monday triage "
              "(D-084): each run replaces this body and adds the same report as a comment. Leave "
              "the first line as it is.\n\n")
    return header + report, report


def lines(text: str) -> list[dict]:
    return [json.loads(line) for line in filter(str.strip, text.splitlines())]


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    run = int(os.environ["GITHUB_RUN_ID"])  # run ids grow, so they order the runs
    url = f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/runs/{run}"
    now = datetime.datetime.now(datetime.UTC)
    week = now - datetime.timedelta(days=7)
    month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prs = lines(gh(f"repos/{repo}/pulls?state=all&sort=updated&direction=desc&per_page={PAGE}",
                   "--jq", ".[] | {number, state, merged_at, updated_at, body, "
                   "labels: [.labels[].name]}"))
    since = min(week, month).strftime("%Y-%m-%dT%H:%M:%SZ")  # filters on updated_at
    comments = lines(gh("--paginate", f"repos/{repo}/issues/comments?since={since}&per_page=100",
                        "--jq", ".[] | {user: .user.login, user_type: .user.type, created_at, "
                        "updated_at, body}"))
    body, report = render(run, url, now.date(), [
        ("Mutation score of `tlilli-core` (`PR-TST-012`)",
         mutation(os.environ.get("MUTANTS", ""), os.environ.get("MUTANTS_RESULT", ""))),
        (f"Audited labels since {week:%Y-%m-%d} (`PR-PRQ-031`)", audit(prs, week)),
        ("Review budgets", budget(comments, week, month, now))])
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(report)
    issue = (find(repo, TITLE) or [None])[0]  # the oldest; runs never overlap (D-083)
    last = MARK.match((issue or {}).get("body") or "")
    if last and int(last.group(1)) > run:
        print(f"{TITLE}: a newer run has reported already")  # an older run re-run late
        return 0
    if issue is None:
        number = json.loads(gh(f"repos/{repo}/issues", payload={
            "title": TITLE, "body": body, "labels": ["type/task", "area/ci"]}))["number"]
    else:
        number = issue["number"]
        gh("-X", "PATCH", f"repos/{repo}/issues/{number}", payload={"body": body, "state": "open"})
    gh(f"repos/{repo}/issues/{number}/comments", payload={"body": report})
    print(f"{TITLE}: issue #{number}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
