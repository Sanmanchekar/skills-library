# Deploy Plan Skill — Rollout, Canary & Rollback Plan Generator for Claude Code, Cursor, Copilot

> **Every risky change gets a written rollout plan.** Deploy order (expand → migrate → contract), prerequisites, canary promotion gates, verification commands with expected output, and a rollback plan with time-to-rollback — no invented values.

**Keywords**: deployment plan, rollout plan, canary deployment, blue green deployment, rolling deploy, expand and contract migration, zero downtime deploy, rollback plan, promotion gates, deploy checklist, release runbook, blast radius, deploy plan claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- deploy-plan
```

## What it does

- Reads the diff, migrations, and infra config to list **every deployable** the change touches
- Orders the deploy with **expand → migrate → contract** so old and new code coexist safely
- Inventories **env vars, secrets, topics, IAM, flags** — citing file:line for every known value
- Picks a **rollout strategy** (rolling / blue-green / canary / flag) and defines **numeric promotion gates**
- Writes **post-deploy verification commands with expected output**
- Writes a **rollback plan** per phase with **time-to-rollback** and **data-compatibility** notes; marks irreversible steps
- States the **blast radius**
- **Never invents values** — unknowns become `⚠️ ACTION REQUIRED` with who to ask

## When it triggers

- "Deploy plan for this PR" / "rollout plan"
- "How do we ship this safely?" / "canary plan"
- "What order do we deploy these services in?"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [db-migration](../db-migration) — safe migrations for the expand/contract phases
- [release-notes](../release-notes) — the user-facing changelog for the same release
- [runbook](../runbook) — what on-call does if the rollout goes wrong
- [production-readiness](../production-readiness) — go/no-go gate before the first launch
- [iac-review](../iac-review) — review the infra prerequisites
