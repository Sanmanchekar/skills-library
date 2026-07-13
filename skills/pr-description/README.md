# PR Description Skill — Pull Request Description Generator for Claude Code, Cursor

> **Generate PR descriptions that reviewers actually read.** Summary, test plan checkboxes, screenshots, risk table, rollback plan, and links to PRD / issue / runbook.

**Keywords**: pr description generator, pull request template, ai pr description, github pr generator, test plan generator, ai code review prep, pr description claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- pr-description
```

## What it does

- **Detects change class** (feature / bugfix / refactor / migration / revert) — different classes need different sections
- Test plan is a **checkbox list** the author actually ticks
- Requires a **Risk section** for DB/auth/payments/infra changes
- Requires a **Rollback plan** for migrations
- **Links** to PRD, issue, runbook when the branch or commits reference them
- Screenshots section auto-added for UI changes

## When it triggers

- "Write a PR description"
- "Open a PR for this"
- `gh pr create` flow

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [commit-message](../commit-message) — good commits make PR generation easier
- [code-review](../code-review) — the reviewer who reads it
- [release-notes](../release-notes) — merged PRs become release notes
