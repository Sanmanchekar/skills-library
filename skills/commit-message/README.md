# Commit Message Skill — Conventional Commits Generator for Claude Code, Cursor, Copilot

> **Generate Conventional Commits messages from your staged diff.** Auto-detects type, scope, and breaking changes — with a subject ≤72 chars in imperative present tense.

**Keywords**: conventional commits, ai commit message, git commit generator, semantic commits, breaking change detection, ai git, commit message claude code skill, cursor commit message

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- commit-message
```

## What it does

- **Reads the staged diff** and classifies as feat / fix / perf / refactor / docs / test / chore / build / ci / style / revert
- **Detects scope** from the file paths
- **Detects breaking changes** — removed/renamed public APIs, changed HTTP contracts, changed CLI flags — adds `!` + footer
- Subject **≤72 chars, imperative present, no trailing period**
- Body explains **WHY**, not WHAT (the diff shows WHAT)
- Blocks vague messages like "update code" / "fix bug"

## When it triggers

- "Write a commit message"
- "Commit this"
- Staged changes present

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [pr-description](../pr-description) — turn a commit range into a PR description
- [release-notes](../release-notes) — turn merged PRs into release notes
- [code-review](../code-review) — the reviewer who reads your commit
