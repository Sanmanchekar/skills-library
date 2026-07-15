# Onboarding Skill — Repo Walkthrough Generator for New Joiners

> **Onboard a new engineer onto any codebase in one guide.** What the repo is, stack, run in 5 minutes, the 5 files to read first, an end-to-end example, common workflows, landmines, who to ask.

**Keywords**: repo onboarding guide, developer onboarding, codebase walkthrough, ai onboarding, new joiner guide, ramp up new engineer, code tour generator, onboarding claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- onboarding
```

## What it does

- Reads **manifests + README + CI + top-level directories** — infers stack and shape
- Finds the **entry points** (web / CLI / library / monorepo packages)
- Traces **one end-to-end path** through the code — teaches the layout by example
- Extracts a **"5 files to read"** starting order — no more drowning in 500 files
- Documents **common workflows** ("add an endpoint", "add a migration") from patterns in the code
- **Landmines section** — global state, non-obvious naming, "do not touch" zones from git-blame
- Refuses to invent structure — says "ask the team" when the code doesn't tell

## When it triggers

- "Onboard me onto this repo"
- "Generate an onboarding guide"
- "Explain this codebase"
- "I'm new to this repo — where do I start"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [docs-writer](../docs-writer) — README + API docs from source
- [db-migration](../db-migration) — the migration-specific workflow onboarding links to
- [debug](../debug) — for when the new joiner hits their first bug
