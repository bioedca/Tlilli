// Conventional Commits rules for Tlilli (docs/prd/30-git-workflow.md, PR-GIT-020 and PR-GIT-021).
// Used by the lefthook commit-msg hook and by the CI `commits` job (docs/prd/33-ci-cd.md).
// Self-contained on purpose: the repository root has no node_modules to resolve a shared preset from.

const types = [
  "feat",
  "fix",
  "docs",
  "style",
  "refactor",
  "perf",
  "test",
  "build",
  "ci",
  "chore",
  "revert",
];

// Closed list; adding a scope is a PRD change.
const scopes = [
  "core",
  "mcp",
  "cli",
  "tauri",
  "ui",
  "skills",
  "docs",
  "prd",
  "ci",
  "release",
  "deps",
  "repo",
  "fixtures",
];

// Dependabot's grouped titles run past 72 characters, so its commits and titles are linted without the
// header cap (D-082). scripts/pr_checks.sh sets this for Dependabot's pull requests only.
const dependabot = process.env.TLILLI_COMMITLINT_DEPENDABOT === "1";

export default {
  // commitlint splits a scope on `/`, `\\` and `,` before scope-enum runs, so `core/ui` would pass as
  // two listed scopes. PR-GIT-020 allows exactly one scope from the closed list.
  plugins: [
    {
      rules: {
        "scope-single": ({ scope }) => [
          !scope || !/[/\\,]/.test(scope),
          `use exactly one scope from the closed list, not "${scope}"`,
        ],
      },
    },
  ],
  // The default parser does not know the `!` breaking-change marker of Conventional Commits 1.0.
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w*)(?:\((.*)\))?!?: (.*)$/,
      headerCorrespondence: ["type", "scope", "subject"],
    },
  },
  rules: {
    "type-enum": [2, "always", types],
    "type-case": [2, "always", "lower-case"],
    "type-empty": [2, "never"],
    "scope-enum": [2, "always", scopes],
    "scope-single": [2, "always"],
    "scope-case": [2, "always", "lower-case"],
    "scope-empty": [2, "never"],
    "subject-empty": [2, "never"],
    // Lower-case first letter: reject the capitalised styles.
    "subject-case": [2, "never", ["sentence-case", "start-case", "pascal-case", "upper-case"]],
    "subject-full-stop": [2, "never", "."],
    "header-max-length": dependabot ? [0] : [2, "always", 72],
    "body-leading-blank": [2, "always"],
    // PR-GIT-021 asks for a 72-column body; a warning keeps long URLs from blocking a commit.
    "body-max-line-length": [1, "always", 72],
    "footer-leading-blank": [2, "always"],
    "footer-max-line-length": [2, "always", 100],
  },
};
