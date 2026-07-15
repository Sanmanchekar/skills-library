# On-Call Triage Skill — Alert-to-Action Decision Tree for SRE / DevOps

> **Alert fires at 3am. Now what?** Structured decision tree — confirm real, classify severity, check what changed, mitigate before investigate, escalate on time.

**Keywords**: oncall triage, alert triage, sre on call, pagerduty response, incident classification, sev1 sev2 sev3, ai oncall assistant, oncall triage claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- oncall-triage
```

## What it does

- **Decision tree** from alert to action — no freezing at 3am
- **Severity classification table** — SEV-1 / SEV-2 / SEV-3 with concrete criteria
- **First 5 minutes checklist** — confirm real, snapshot state, check status pages, check recent deploys, post in channel
- **Mitigate before investigate** when users are impacted — rollback / circuit-break / scale / flag-off / rate-limit
- **Escalation triggers** with clear time thresholds
- **Handoff protocol** — no silent handoffs

## When it triggers

- Alert body / PagerDuty incident / customer report pasted
- "I just got paged for X"
- "Triage this alert"
- On-call handoff / shift start

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [runbook](../runbook) — the mitigation steps the triage links to
- [rca](../rca) — post-incident root cause
- [log-analysis](../log-analysis) — for the investigate phase
