# Estimation Skill — Task Breakdown & T-Shirt Sizing for Claude Code, PMs

> **Break a spec into tasks with sizes, risks, dependencies, and an honest range.** Catches hidden work (migrations, tests, docs, observability, review cycles) — no more "we forgot the runbook".

**Keywords**: task estimation, t-shirt sizing, ai estimation, sprint planning, effort estimation, project sizing, ai product manager, estimation claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- estimation
```

## What it does

- **XS / S / M / L** T-shirt scale — **XL forbidden** (must split)
- Task breakdown checklist includes **the most-missed items**: migrations, tests, docs, observability, review cycles, runbook
- **Risk flags** per task — unknown API, external dep, novel architecture, blast radius, coordination
- **Best / likely / worst range** — never a single number
- Confidence-based range multipliers — 2×–4× for novel work
- **Assumptions list** — every assumption is a failure mode
- Blocks committing to "best case"

## When it triggers

- "Estimate this"
- "Size these tasks"
- "How long will X take"
- Spec + deadline shared

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [prd-writer](../prd-writer) — the spec you're estimating from
- [pr-description](../pr-description) — PR that ships each task
- [retro](../retro) — compare estimate vs actual after the work is done
