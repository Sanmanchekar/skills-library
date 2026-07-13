# Runbook Skill — Incident Runbook Generator for Claude Code, Cursor, Copilot

> **Generate incident runbooks that actually work at 3am.** Symptoms, first-5-minutes triage, copy-paste mitigation commands, rollback, escalation path.

**Keywords**: runbook generator, incident runbook, sre runbook, oncall runbook, ai runbook, ai sre skill, kubernetes rollback runbook, on-call playbook, runbook claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- runbook
```

## What it does

- Follows a **strict section order** so runbooks are scannable at 3am
- **Every mitigation includes a copy-paste command** — no abstract advice
- Requires a **rollback section** — if mitigation makes it worse, how do you undo
- Standardizes **escalation path** with time thresholds
- Includes a **post-incident hook** so the runbook improves after every use

## When it triggers

- "Write a runbook for X"
- "Runbook for alert Y"
- "How do we respond to Z"
- After an RCA — action items called for a runbook

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [rca](../rca) — feeds action items that become runbooks
- [observability](../observability) — dashboards the runbook links to
- [iac-review](../iac-review) — infra config the mitigation commands touch
