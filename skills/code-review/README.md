# AI Code Review Skill — Automated PR Review for Claude Code, Cursor, Copilot, Codex, Aider

> **Turn any AI coding agent into a rigorous code reviewer.** Severity-tagged findings, concrete fix suggestions as code blocks, no fluff. Works with Claude Code, Cursor, GitHub Copilot Chat, Codex CLI, Aider, Continue, Cline, Windsurf, Cody, Roo Code, Zed.

**Keywords**: ai code review, automated pr review, claude code review skill, cursor code review, github copilot code review, code review agent, pull request review automation

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- code-review
```

The installer asks which agent to target (Claude Code, Cursor, Copilot Chat, Codex, Aider, Continue, Cline, Windsurf, Cody, Roo Code, Zed, or all).

## What it does

- Reads the actual diff and file contents — never invents code
- Emits findings tagged **CRITICAL / HIGH / MEDIUM / LOW** with a clear severity rubric
- Every finding is anchored to `file:line` and includes a **ready-to-apply code block** as the suggested fix
- Sorts findings by severity so you can prioritize
- Covers correctness, security, performance, maintainability, stability

## When it triggers

- "Review this PR"
- "Review my changes"
- "Code review this"
- PR URL, PR number, branch name, or raw diff pasted in

## Example

```markdown
## Review — 2 findings

| # | Severity | File:Line | Title |
|---|----------|-----------|-------|
| 1 | CRITICAL | src/auth.py:42 | JWT signature not verified |
| 2 | HIGH | src/orders.py:118 | N+1 query in order list |
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [pr-description](../pr-description) — generate the PR description this reviewer will read
- [commit-message](../commit-message) — conventional commit messages
- [test-generation](../test-generation) — write the tests reviewers ask for
