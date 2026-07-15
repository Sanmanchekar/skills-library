# Docs Writer Skill — README & API Reference Generator for Claude Code, Cursor

> **Generate accurate docs from source, never from imagination.** README, API reference, module docs — strict templates, runnable examples cribbed from tests, and no marketing fluff.

**Keywords**: readme generator, api docs generator, ai documentation, docstring generator, module docs, package readme, ai technical writer, docs writer claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- docs-writer
```

## What it does

- **Reads the code** — refuses to document functions it hasn't read
- **Steals usage from tests** — tests show how the API is actually used
- Three doc types with **strict templates**: README, API reference, module overview
- **Runnable examples** — no `...` placeholders, complete imports
- Blocks marketing language ("blazing fast") and unbenchmarked comparative claims
- Blocks "coming soon" — docs describe what exists
- Distinguishes **public API from internals** — internals don't need reference docs

## When it triggers

- "Write docs for X"
- "Generate a README"
- "Document this module"
- "API reference for Y"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [onboarding](../onboarding) — repo walkthrough for new joiners
- [release-notes](../release-notes) — what changed since last version
- [adr](../adr) — architecture decisions that inform the docs
