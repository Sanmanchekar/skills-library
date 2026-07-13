---
name: observability
description: Generate Grafana dashboards, Prometheus alert rules, and Loki queries from service code. Reads a service's routes, DB calls, and background jobs to produce a golden-signals dashboard (RED for HTTP, USE for infra, saturation for queues) plus SLO-based alerts and per-symptom log queries. Triggered when the user asks to "add observability", "build a dashboard for X", "add alerts", or "instrument this service".
---

# observability

## When to use

- User asks: "build a dashboard for service X", "add alerts", "add observability", "instrument this"
- User points at a service directory or a specific endpoint

## Steps

1. **Read the service**. Enumerate:
   - HTTP routes (method, path, handler)
   - DB calls (SELECT / INSERT / UPDATE — flag N+1 hotspots)
   - External HTTP / RPC calls (third-party APIs, other services)
   - Background jobs / queue consumers
   - Existing instrumentation (OpenTelemetry, Prometheus client libs, logger)

2. **Pick the signals**:

   | Component | Signal set | Rationale |
   |---|---|---|
   | HTTP endpoint | **RED** — Rate, Errors, Duration (p50/p95/p99) | user-facing latency + error budget |
   | External call | Rate + error rate + duration + timeout count | catch upstream degradation |
   | DB | Query rate + slow query count + pool saturation | detect leaks / hot queries |
   | Queue consumer | Enqueue rate, consume rate, lag, DLQ depth | catch backup / slow consumers |
   | Cache | Hit rate + eviction rate | tune size, catch key explosion |
   | Infra (pod / host) | **USE** — Utilization, Saturation, Errors (CPU, mem, FD, disk) | capacity planning |

3. **Build the Grafana dashboard JSON** — one row per component, panels in order: Rate, Errors, Duration, Saturation.

4. **Generate PromQL** for each panel — use the actual metric names the service exposes (or the OTel-standard equivalents: `http_server_request_duration_seconds`, `db_client_operation_duration_seconds`).

5. **Generate SLO-based alerts** — burn-rate alerts (fast + slow window) not threshold alerts:
   ```yaml
   - alert: HTTPErrorBudgetBurnFast
     expr: |
       (
         sum(rate(http_server_requests_total{status=~"5.."}[5m]))
         / sum(rate(http_server_requests_total[5m]))
       ) > (14.4 * 0.001)  # 14.4× burn of 99.9% SLO in 5m window
     for: 2m
     labels: { severity: page }
   ```

6. **Generate Loki queries** for the common symptoms — errors by endpoint, slow requests, panics:
   ```logql
   {service="orders"} |= "level=error" | json | line_format "{{.request_id}} {{.msg}}"
   ```

## Output artifacts

- `dashboard.json` — importable Grafana JSON
- `alerts.yml` — Prometheus alerting rules
- `loki-queries.md` — labeled LogQL snippets for the runbook

## Rules

- NEVER build a threshold alert on a raw metric — use burn-rate against an SLO
- NEVER use `histogram_quantile(0.99, sum(rate(...))[1m])` — use ≥5m window, otherwise p99 is noise
- NEVER include panels for metrics the service doesn't emit — flag them as "add instrumentation" instead
- ALWAYS include the RED trio for every HTTP endpoint
- ALWAYS attach unit + description to every panel
