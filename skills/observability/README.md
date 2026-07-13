# Observability Skill — Grafana Dashboard & Prometheus Alert Generator for Claude Code

> **Turn a service directory into a golden-signals Grafana dashboard, SLO burn-rate alerts, and ready-to-run Loki queries.** RED for HTTP, USE for infra, saturation for queues — automatically.

**Keywords**: grafana dashboard generator, prometheus alerts generator, loki query generator, ai observability, slo burn rate alerts, red method dashboard, use method infra, opentelemetry dashboard, observability claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- observability
```

## What it does

- **Reads your service code** — routes, DB calls, external calls, queue consumers
- Picks the right signal set per component: **RED** for HTTP, **USE** for infra, saturation for queues
- Generates a **Grafana dashboard JSON** you can import
- Generates **SLO burn-rate alerts** — never threshold alerts on raw metrics
- Generates **Loki queries** labeled per common symptom (errors, slow requests, panics)
- Flags missing instrumentation instead of inventing metrics

## When it triggers

- "Build a dashboard for service X"
- "Add alerts"
- "Add observability"
- "Instrument this service"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [runbook](../runbook) — write the runbook the alerts link to
- [rca](../rca) — use the dashboards for post-incident investigation
- [iac-review](../iac-review) — Terraform / Helm config review
