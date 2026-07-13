# ADR Skill — Architecture Decision Record Generator for Claude Code, Cursor, Copilot

> **Write ADRs (MADR format) that survive a re-org.** Numbered, dated, immutable — with context, options, decision, and honest consequences.

**Keywords**: architecture decision record, adr generator, madr template, ai adr, technical decision doc, ai architecture skill, adr claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- adr
```

## What it does

- Follows the **MADR format** — status, deciders, context, options, decision, consequences, follow-ups
- **Forces alternatives** — no ADR without at least 2 options considered
- Blocks post-hoc rationalization — options come before decision
- Requires honest **negative consequences** — an ADR with no negatives is unsigned
- Numbered `NNNN-slug.md`, immutable — new decisions supersede rather than edit
- **Interview mode** for thin inputs — asks sharpening questions first

## When it triggers

- "Write an ADR for X"
- "Document this decision"
- After a significant technical choice

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [prd-writer](../prd-writer) — PRD forces ADR-level decisions
- [pr-description](../pr-description) — the PR that implements the ADR
- [runbook](../runbook) — runbook for the choice you just made
