# Refactor Skill — Safe Behavior-Preserving Restructure for Claude Code, Cursor, Copilot

> **Refactor without regressions.** Tests before touching code, one mechanical step per commit, no feature creep, no "while I'm here" cleanup. Stack-agnostic.

**Keywords**: safe refactor, ai refactor, characterization tests, behavior preserving refactor, extract method, rename refactor, decompose god class, refactor claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- refactor
```

## What it does

- Enforces **"structure changes, behavior doesn't"** — if behavior changes, it's a rewrite
- Requires **behavior baseline** BEFORE touching code (existing tests or characterization tests you write first)
- Named **mechanical patterns table** — rename / extract / inline / move / split / merge
- **One pattern per commit** — reviewers can tell what changed
- Blocks feature + refactor in the same PR
- Blocks abstractions for hypothetical reuse (rule of three)
- If tests go red mid-refactor: `git reset --hard`, try smaller — no "fix forward"

## When it triggers

- "Refactor this" / "clean up X"
- "Extract this into Y"
- "Split this file"
- Pre-work for a feature the messy area is blocking

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [test-generation](../test-generation) — characterization tests before you refactor
- [code-review](../code-review) — reviewer who catches refactor + feature drift
- [commit-message](../commit-message) — one-refactor-per-commit messages
