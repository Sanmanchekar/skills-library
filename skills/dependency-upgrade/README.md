# Dependency Upgrade Skill — Version Bump Migration Planner for Claude Code, Cursor

> **Plan a Python 3.8 → 3.12, Node 18 → 22, Django 4 → 5, or Next.js major upgrade without breaking prod.** Reads changelogs, categorizes breaking changes, produces a hit list, sequences the PRs, and hands you a rollout plan.

**Keywords**: dependency upgrade, ai dep upgrade, python 3.12 migration, node lts upgrade, django major upgrade, framework migration, breaking change triage, cve fix, dependabot pr review, dependency upgrade claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- dependency-upgrade
```

## What it does

- **3-question triage** — Why now? What target? What risk budget?
- Categorizes each breaking change: **removed / renamed / default-changed / behavior-changed / deprecated**
- Produces a **hit list** — file:line for every affected call site, not "we might use this"
- **Sequences PRs** — deprecations first, then bump, then behavior changes, then cleanup
- Reference cards for the common jumps: **Python 3.x, Node LTS, framework majors, transitive CVE**
- Rollout plan (staging → canary → 100%) with rollback via lockfile revert

## When it triggers

- "Upgrade Python 3.8 → 3.12" / "bump Django to 5" / "upgrade Node 18 → 22"
- Dependabot / Renovate PR shared
- Security scanner flagged a CVE

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [security-review](../security-review) — the CVE that started the upgrade
- [test-generation](../test-generation) — regression tests for behavior changes
- [pr-description](../pr-description) — describe the multi-PR upgrade sequence
