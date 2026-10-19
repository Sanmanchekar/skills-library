---
name: slo-definition
description: Define SLIs, SLOs, and error budgets for a service starting from its user journeys. Produces an SLO spec with good/valid event definitions as concrete PromQL-style queries, targets, rolling windows, error-budget math, multi-window multi-burn-rate alert rules, and an error-budget policy. Stack-agnostic — works with Prometheus, Datadog, Cloud Monitoring, CloudWatch, or any metrics backend. Triggered when the user says "define SLOs for X", "what should our SLIs be", "set up error budgets", "add burn-rate alerts", "what availability target should we pick", or "our alerts are too noisy, alert on SLOs instead".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# slo-definition

## When to use

- User says: "define SLOs", "write SLIs for orders-service", "error budget", "burn-rate alerts"
- A service is going to production with no reliability target
- Alerts fire on CPU / memory / single-error thresholds instead of user pain
- Teams argue about "is this reliable enough?" with no shared number

## Steps

1. **List user journeys** — 3 to 5 critical ones (e.g. "place order", "view order history"). Read routes / handlers to find them. Skip internal admin paths.
2. **Pick SLI types per journey** from the menu below — usually 1–2 per journey, never more than 3.
3. **Write good/valid event queries** — read the code and existing metrics first; reuse metric names that exist. If a metric is missing, list it as an instrumentation prerequisite.
4. **Choose target** — from historical performance, not aspiration (see target table).
5. **Choose window** — rolling 28d (default; whole weeks) or 30d. Calendar windows only for contractual SLAs.
6. **Compute error budget** in events and in minutes.
7. **Write burn-rate alerts** — multi-window, multi-burn-rate (see table).
8. **Write error-budget policy** — what happens at 50%, 75%, 100% spent.
9. **Hand off** — dashboards and panel layout go to [observability](../observability); alert links go to a [runbook](../runbook).

## SLI menu

| SLI | Good event | Valid event | Fits |
|---|---|---|---|
| Availability | non-5xx response | all requests excluding health checks | request/response APIs |
| Latency | request served < threshold (e.g. 300ms) | all successful requests | user-facing reads/writes |
| Freshness | data updated within N minutes | all freshness probes / reads | pipelines, caches, search indexes |
| Correctness | output matches expected / reconciles | all checked outputs | billing, ledgers, ETL |
| Throughput | batch/job processed within deadline | all jobs scheduled | queues, batch workers |

Rules for SLI choice: measure as close to the user as possible (load balancer > app > DB). Exclude 4xx from bad events unless caused by the service (e.g. 429 from your own rate limiter counts as bad).

## Query templates (PromQL-style)

```promql
# Availability — ratio of good to valid
sum(rate(http_requests_total{service="orders-service", route!~"/health.*", code!~"5.."}[5m]))
/
sum(rate(http_requests_total{service="orders-service", route!~"/health.*"}[5m]))

# Latency — fraction under 300ms (histogram bucket must exist at 0.3)
sum(rate(http_request_duration_seconds_bucket{service="orders-service", le="0.3"}[5m]))
/
sum(rate(http_request_duration_seconds_count{service="orders-service"}[5m]))

# Freshness — fraction of probes where data age < 10 min
avg_over_time((time() - orders_index_last_updated_timestamp_seconds < bool 600)[5m:30s])

# Error ratio used by burn-rate alerts (1 - SLI) over window W
1 - (sum(rate(good_events[W])) / sum(rate(valid_events[W])))
```

## Target selection

| Situation | Target guidance |
|---|---|
| New service, no history | Start at 99.0–99.5%, revisit after 1 window |
| Has 28d history | Set just below observed (observed 99.93% → target 99.9%) |
| Depends on a 99.9% dependency (hard, no fallback) | Cannot exceed ~99.9%; target lower |
| Internal batch / async | 99% often enough; users tolerate delay |
| Each extra nine | ~10x cost; require a business reason |

## Error budget math

| Target | Budget | Per 28d (minutes) | Per 30d (minutes) |
|---|---|---|---|
| 99% | 1% | 403.2 | 432 |
| 99.5% | 0.5% | 201.6 | 216 |
| 99.9% | 0.1% | 40.3 | 43.2 |
| 99.95% | 0.05% | 20.2 | 21.6 |
| 99.99% | 0.01% | 4.0 | 4.3 |

Event form: `budget_events = (1 - target) × valid_events_in_window`. Burn rate = `observed_error_ratio / (1 - target)`.

## Burn-rate alerts (multi-window, multi-burn-rate)

| Severity | Burn rate | Long window | Short window | Budget consumed at fire | Action |
|---|---|---|---|---|---|
| Page | 14.4x | 1h | 5m | 2% | page on-call |
| Page | 6x | 6h | 30m | 5% | page on-call |
| Ticket | 3x | 1d | 2h | 10% | ticket, next business day |
| Ticket | 1x | 3d | 6h | 10% | ticket, review in standup |

Both windows must exceed the threshold — the short window makes the alert reset quickly once fixed.

```yaml
- alert: OrdersAvailabilityFastBurn
  expr: |
    (error_ratio:orders:rate1h > (14.4 * 0.001)) and (error_ratio:orders:rate5m > (14.4 * 0.001))
    or
    (error_ratio:orders:rate6h > (6 * 0.001)) and (error_ratio:orders:rate30m > (6 * 0.001))
  labels: { severity: page, slo: orders-availability }
  annotations: { runbook_url: "<runbook link>" }
```

Precompute `error_ratio:*:rateW` as recording rules — never compute 6h/1d windows in the alert expression.

## Error-budget policy

| Budget spent (rolling window) | Action |
|---|---|
| < 50% | Ship normally |
| 50–75% | Reliability work enters sprint; risky launches need sign-off |
| 75–100% | Feature freeze for this service except reliability fixes |
| > 100% | Freeze + mandatory [rca](../rca) for top budget consumers; resume when back under 100% |
| Single incident > 20% of budget | Postmortem required regardless of total |

## Example

Input: "Define SLOs for payments-api; it handles POST /charges and GET /charges/{id}."

Output (excerpt):
- Journey "create charge": availability 99.9% / 28d (budget 40.3 min), latency 95% < 800ms
- Journey "read charge": availability 99.95%, latency 99% < 200ms
- Prerequisite: add histogram bucket `le="0.8"` to `http_request_duration_seconds`

## Output format

```markdown
## SLO spec — <service>

### Journeys
| Journey | Routes | Why it matters |

### SLOs
| SLO | SLI type | Good event query | Valid event query | Target | Window | Budget |

### Error budget
- Target 99.9% over 28d → 40.3 min / 0.1% of valid events

### Alerts
| Name | Burn rate | Windows | Severity | Runbook |

### Error-budget policy
| Spent | Action |

### Prerequisites
- [ ] Missing metrics / buckets / recording rules

### Hand-off
- Dashboards → observability skill
```

## Rules

- NEVER set a target higher than the weakest hard dependency allows
- NEVER pick a target without looking at historical data when it exists
- NEVER alert on a single-window threshold — always pair long + short windows
- NEVER count client errors (4xx) as bad unless the service caused them
- ALWAYS write good/valid as explicit queries — "99.9% uptime" with no query is not an SLO
- ALWAYS exclude health checks and synthetic traffic from valid events (or track them separately)
- ALWAYS attach an error-budget policy — an SLO with no consequence is a dashboard
- ALWAYS limit to the 3–5 journeys users actually feel

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: operate · **Agent**: `operate`
- **Reads**: `prd`, `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `slo` → `slo.md`
- **Comes after**: prd-writer
- **Hand off to**:
  - `observability` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record slo-definition --artifact slo=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
