# Production Readiness Review Skill — Go/No-Go Launch Checklist & Scorecard for Claude Code, Cursor, Copilot

> **Launch with evidence, not vibes.** A 27-item production readiness review graded pass / partial / fail / n-a from what is actually in the repo — with a scorecard, a blocking-items list, and a GO / CONDITIONAL GO / NO-GO verdict.

**Keywords**: production readiness review, prr checklist, launch checklist, go no-go review, service readiness, operational readiness, sre checklist, slo, health probes, observability checklist, backup and disaster recovery, security scanning, on-call ownership, production readiness claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- production-readiness
```

## What it does

- Checks **27 items** across testing, observability, SLOs, runbook, ownership, health probes, graceful shutdown, capacity, resilience, backups/DR, migrations, security scanning, secrets, dependencies, deploy, and docs
- Grades each **PASS / PARTIAL / FAIL / N/A / UNVERIFIED** with **file:line evidence** — no evidence means FAIL
- Separates **blocking** from **advisory** items
- Outputs a **scorecard**, a **blocking-items list** with concrete fixes, and a **GO / CONDITIONAL GO / NO-GO** verdict
- Flags anything outside the repo (pager tool, cloud console) as **UNVERIFIED** for a human to confirm
- Never invents owners or dashboards — unknowns are `⚠️ ACTION REQUIRED`

## When it triggers

- "Production readiness review" / "PRR"
- "Are we ready to launch?" / "go/no-go"
- "Launch checklist for this service"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [observability](../observability) — fix the logs / metrics / alerts gaps
- [runbook](../runbook) — write the missing runbook
- [security-review](../security-review) — deeper security pass on blocking items
- [load-testing](../load-testing) — evidence for the capacity items
- [deploy-plan](../deploy-plan) — the rollout plan once you're a GO
