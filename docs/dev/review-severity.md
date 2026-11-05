# Review severity

Human reviewers and the three AI review lanes all use one severity scale. This page maps each tool's labels onto it. [32 Code review](../prd/32-code-review.md) §6 is binding; this page carries the mapping and is updated when a tool renames its levels.

## The scale

| Severity | Examples | What the author does |
| --- | --- | --- |
| **Blocker** | data loss, an invariant violated (`INV-01..10`), a security hole, a broken build | Fix before Ready. The author may not decline it (`PR-REV-003`). If the author thinks it does not apply, they escalate it to the maintainer, and the PR waits for the answer (`PR-GIT-058`). |
| **Major** | a correctness bug, new behaviour without a test, contract drift between code and docs | Fix before Ready. A decline is escalated to the maintainer. |
| **Minor** | an edge case, unclear code, a performance smell | Fix it, or decline it with a reason a reader can check. |
| **Nit** | wording, ordering, an optional idiom | Acknowledge it; a fix is optional. |

Every finding gets an answer in its own thread: fixed (with the commit SHA), declined (with the reason), or escalated (`PR-REV-002`). The author never edits or deletes a reviewer's comment (`PR-REV-004`).

## Tool labels

| Severity | Codex | CodeRabbit | Greptile |
| --- | --- | --- | --- |
| Blocker | P0, P1, "critical" | Critical; a potential issue with a security tag | "critical" |
| Major | P2, "bug" | Major; a potential issue or refactor suggestion that affects correctness | "major", "important" |
| Minor | P3 | Minor; a refactor suggestion or verification | "minor" |
| Nit | "nit" | Nitpick | "nit", "style" |

How the labels appear on this repository's pull requests (November 2026):

- **Codex** heads each inline finding with a badge from P0 to P3. On pull request 74, a P1 claimed that `tlilli-cli` broke a filesystem rule in PRD 21 §4. P1 is a Blocker, so the author escalated it instead of declining it. The maintainer ruled that the rule covers `tlilli-core` only.
- **CodeRabbit** heads each inline finding with its severity (Critical, Major, Minor or Nitpick), a category such as "Functional Correctness", and an effort hint such as "Quick win". Use the severity word; the category and effort hint do not change the severity. Examples: the Major on pull request 74 (the regeneration script could delete another repository's pages) and the Minor on pull request 75 (an unreadable skill entry was skipped silently).
- **Greptile** has no finding on this repository yet; its reviews of pull requests 66 and 69 were clean. The mapping in the table above is from PRD 32 and will be checked against the first real finding.

## Signals that are not findings

- **CodeRabbit pre-merge checks.** A failed "Docstring Coverage" check comes with CodeRabbit's default threshold of 80%. The repository's rule on doc comments is `PR-DOC-015` ([35 Documentation](../prd/35-documentation.md)), which covers public items in `tlilli-core` and `tlilli-mcp`. When the check fails only on test functions, the author says so once in a PR comment, as on pull requests 74 and 75.
- **"Additional comments" and outside-the-diff remarks.** CodeRabbit sometimes lists remarks in the review body instead of as threads. They carry a severity like any other finding and are answered in one PR comment, because there is no thread to reply in.
- **Summaries, walkthroughs and "review skipped" notices** are context, not findings.

## Related pages

- [32 Code review](../prd/32-code-review.md): the pipeline, the lanes and the rules `PR-REV-001..015`.
- [Agent playbook](agent-playbook.md): how an agent session runs the pipeline.
- `## Review guidelines` in `AGENTS.md`: the review rules Codex reads, with the same severity table.
