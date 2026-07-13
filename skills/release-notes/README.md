# Release Notes Skill — Changelog Generator for Claude Code, Cursor, Copilot

> **Generate user-facing release notes from merged PRs or commits.** Grouped by impact (Breaking / New / Improved / Fixed / Security / Deprecated) — not "refactored X" or raw commit subjects.

**Keywords**: release notes generator, changelog generator, ai release notes, semantic versioning, user-facing changelog, product changelog, ai product manager, release notes claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- release-notes
```

## What it does

- **Reads the PR/commit range** and translates to user-facing language
- **Groups by impact** (Breaking → New → Improved → Fixed → Security → Deprecated)
- **Skips internal noise** — refactors, chores, doc-only, CI-only unless developer-audience
- Enforces **past-tense active-voice** one-line entries
- Breaking changes come with a **migration step**
- Never pastes raw commit subjects

## When it triggers

- "Release notes for vX"
- "Changelog since Y"
- "What shipped this week"
- CI tag-push automation

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [commit-message](../commit-message) — good commits make good release notes
- [pr-description](../pr-description) — PR descriptions the release note grabs from
- [prd-writer](../prd-writer) — features from PRD to release note
