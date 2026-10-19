# SLO Definition Skill — SLIs, Error Budgets & Burn-Rate Alerts for Claude Code, Cursor, Copilot

> **Turn user journeys into real SLOs.** Good/valid event queries, targets from history, error-budget math, multi-window multi-burn-rate alerts, and an error-budget policy with teeth.

**Keywords**: slo definition, sli examples, error budget calculator, burn rate alerts, multi-window multi-burn-rate, promql slo, sre skill, ai slo generator, slo claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- slo-definition
```

## What it does

- Starts from **3–5 user journeys**, not from whatever metrics happen to exist
- **SLI menu** — availability, latency, freshness, correctness, throughput — with good/valid event definitions
- Writes **concrete PromQL-style queries** for every SLI, plus missing-instrumentation prerequisites
- **Target selection** from historical data and dependency ceilings — no aspirational nines
- **Error-budget math** for rolling 28d / 30d windows, in minutes and events
- **Multi-window multi-burn-rate alerts** (14.4x 1h+5m, 6x 6h+30m page; 3x / 1x ticket) with recording rules
- **Error-budget policy** — what happens at 50%, 75%, 100% spent

## When it triggers

- "Define SLOs for X"
- "What should our SLIs be?"
- "Set up error budgets / burn-rate alerts"
- "Our alerts are too noisy — alert on SLOs instead"

## Example

"Define SLOs for payments-api" → create-charge availability 99.9% / 28d (40.3 min budget), latency 95% < 800ms, fast-burn page rule, and a prerequisite to add the `le="0.8"` histogram bucket.

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [observability](../observability) — dashboards and panels for the SLOs
- [runbook](../runbook) — runbooks the burn-rate alerts link to
- [oncall-triage](../oncall-triage) — what to do when a burn-rate page fires
- [rca](../rca) — postmortems when the budget is blown
