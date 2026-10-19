---
name: load-testing
description: Design a proactive load, stress, soak, or spike test before release — a workload model from the real traffic mix, a target RPS derived from the SLO plus headroom, a runnable k6 / Locust / Gatling / vegeta scenario scaffold, a ramp profile, pass/fail thresholds (p95/p99 latency, error rate, saturation), an environment-parity check, the coordinated-omission caveat, and a result report. Distinct from perf-analysis, which is reactive. Triggered when the user says "load test this", "will this handle Black Friday", "stress test the API", "soak test", "spike test", "how many RPS can we take", or "write a k6 script".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# load-testing

## When to use

- User says: "load test X", "stress test", "soak test", "spike test", "capacity test", "write a k6/Locust/Gatling script"
- Before a launch, a marketing event, a traffic migration, or a big infra change (new DB tier, new instance type)
- A new endpoint is expected to carry meaningful traffic and has never been tested under load
- NOT for "this is already slow in prod" — use [perf-analysis](../perf-analysis)

## Test types

| Type | Question it answers | Shape | Typical duration |
|---|---|---|---|
| Load | Do we meet the SLO at expected peak? | ramp → hold at target | 15–30 min hold |
| Stress | Where and how do we break? | step up past target until failure | until breakpoint |
| Spike | Do we survive a sudden burst (autoscaling lag)? | baseline → 5–10x in < 1 min → baseline | 10–20 min |
| Soak | Do leaks / pool exhaustion / disk growth appear over time? | hold at ~70–80% target | 4–24 h |

## Steps

1. **Read the code and config** — routes, handlers, downstream calls, connection-pool sizes, rate limits, autoscaling config, timeouts. Never script an endpoint you have not read.
2. **Build the workload model** from real traffic (access logs, APM, gateway metrics), not guesses:
   - Request mix per endpoint (% of traffic), read/write ratio, payload size distribution
   - Think time and session shape (login → browse → checkout), cache hit ratio, data cardinality (unique users/IDs)
   - If no prod data exists, mark every number `ASSUMED` and state the source of the assumption
3. **Derive the target rate**: `target_rps = observed_peak_rps × growth_factor × headroom` (headroom default 1.5–2x). Show the arithmetic.
4. **Set pass/fail thresholds** from the SLO — p95, p99, error rate, and saturation (CPU, memory, DB connections, queue depth, GC pause). Thresholds are decided BEFORE the run.
5. **Check environment parity** — fill the parity table (see output). Any gap > 2x in capacity invalidates absolute numbers; say so.
6. **Pick the tool** and scaffold the scenario:

   | Tool | Pick when | Model |
   |---|---|---|
   | k6 | JS/TS team, CI thresholds, HTTP/gRPC/WebSocket | open (arrival-rate executors) or closed |
   | Locust | Python team, complex stateful user flows | closed (users) by default |
   | Gatling | JVM team, high-throughput, rich reports | open injection profiles |
   | vegeta | single-endpoint constant-rate HTTP blast | open, constant rate |

7. **Use an open (arrival-rate) model** for user-facing APIs. Closed models (fixed VUs waiting on responses) hide latency — see coordinated omission below.
8. **Plan data and side effects** — seeded test accounts, idempotency keys, sandbox for payment/email/SMS providers, cleanup script. Never hit real third parties.
9. **Run** smoke (1–2 rps, 1 min) → ramp → hold. Watch server-side dashboards live, not just the load generator.
10. **Report** results against thresholds, name the first saturated resource, and list follow-ups.

## Coordinated omission (always state it)

- A closed-loop generator waits for slow responses before sending the next one, so it sends FEWER requests exactly when the system is slow — p99 looks better than reality.
- Fix: use arrival-rate executors (k6 `constant-arrival-rate` / `ramping-arrival-rate`, Gatling `constantUsersPerSec`, vegeta `-rate`) and enough pre-allocated VUs; flag any "dropped iterations".
- Also check the load generator itself is not CPU-bound (> 80% CPU invalidates the run).

## Example — input → output

Input: "Load test `orders-service` before the holiday sale. Peak last year was 400 rps, SLO p99 < 800 ms, errors < 0.5%."

```javascript
// k6 scaffold — orders-service holiday load test
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  scenarios: {
    holiday_peak: {
      executor: 'ramping-arrival-rate',   // open model: avoids coordinated omission
      startRate: 50, timeUnit: '1s',
      preAllocatedVUs: 300, maxVUs: 1500,
      stages: [
        { target: 1200, duration: '10m' }, // 400 × 1.5 growth × 2 headroom
        { target: 1200, duration: '20m' }, // hold
        { target: 0,    duration: '2m' },
      ],
    },
  },
  thresholds: {
    'http_req_duration{name:create_order}': ['p(95)<400', 'p(99)<800'],
    'http_req_failed': ['rate<0.005'],
    'dropped_iterations': ['count<1'],
  },
};

const BASE = __ENV.BASE_URL; // staging URL, never prod by default

export default function () {
  const r = Math.random();
  if (r < 0.70) {        // 70% browse
    http.get(`${BASE}/v1/products?page=1`, { tags: { name: 'list_products' } });
  } else if (r < 0.95) { // 25% view order
    http.get(`${BASE}/v1/orders/${__VU}-${__ITER % 50}`, { tags: { name: 'get_order' } });
  } else {               // 5% create order
    const res = http.post(`${BASE}/v1/orders`, JSON.stringify({ sku: 'TEST-SKU', qty: 1 }), {
      headers: { 'Content-Type': 'application/json', 'Idempotency-Key': `${__VU}-${__ITER}` },
      tags: { name: 'create_order' },
    });
    check(res, { 'created': (x) => x.status === 201 });
  }
}
```

## Output format

````markdown
# Load test plan — <service> — <test type>

## Workload model
| Endpoint | % of traffic | Payload | Source |
|---|---|---|---|
| GET /v1/products | 70% | 2 KB | gateway logs, 2024-11-29 peak hour |

## Target
observed peak <X> rps × growth <g> × headroom <h> = **<target> rps**

## Thresholds (decided before the run)
| Metric | Pass | Fail |
|---|---|---|
| p95 / p99 latency | < 400 / < 800 ms | otherwise |
| Error rate | < 0.5% | ≥ 0.5% |
| Saturation | CPU < 75%, DB pool < 80%, no queue growth | otherwise |

## Environment parity
| Dimension | Prod | Test env | Gap / impact |
|---|---|---|---|
| Instance size × count | | | |
| DB tier + data volume | | | |
| Caches warm? | | | |
| Downstreams (real / stubbed) | | | |

## Ramp profile
<stages table or ASCII chart>

## Results
| Metric | Threshold | Observed | Verdict |
|---|---|---|---|

**First saturated resource**: <e.g. DB connection pool at 950 rps>
**Breakpoint** (stress only): <rps> — failure mode: <timeouts / 5xx / OOM>
**Caveats**: coordinated omission handled? generator CPU? parity gaps?

## Follow-ups
- [ ] <action> — owner
````

## Rules

- NEVER run against production unless the user explicitly asks and names a window — default target is staging/perf env
- NEVER set thresholds after seeing results — they come from the SLO, before the run
- NEVER report only averages — always p95 and p99, plus error rate
- NEVER invent a traffic mix silently — label every unsourced number `ASSUMED`
- NEVER let tests call real payment, email, or SMS providers — stub or sandbox them
- ALWAYS use an open arrival-rate model for user-facing traffic and state the coordinated-omission caveat
- ALWAYS name the first saturated resource — "it got slow" is not a result
- ALWAYS check generator health (CPU, dropped iterations) before trusting numbers

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: verify · **Agent**: `verify`
- **Reads**: `slo`, `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `tests` → `tests.md`
- **Comes after**: complexity-aware-coding, perf-analysis, pr-description
- **Hand off to**:
  - `production-readiness` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record load-testing --artifact tests=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
