# Load Testing Skill — k6, Locust, Gatling Load & Stress Test Design for Claude Code, Cursor, Copilot

> **Know your breaking point before your users find it.** Workload model from real traffic, target RPS from SLO + headroom, a runnable k6 / Locust / Gatling / vegeta scaffold, and pass/fail thresholds decided before the run.

**Keywords**: load testing, stress testing, soak test, spike test, k6 script generator, locust load test, gatling simulation, vegeta, capacity planning, rps target, p99 latency threshold, coordinated omission, ai load testing skill, load test claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- load-testing
```

## What it does

- Picks the right test type — **load, stress, spike, or soak** — for the question you are asking
- Builds a **workload model** from real traffic mix (endpoints, read/write ratio, payloads); flags anything unsourced as `ASSUMED`
- Derives the **target RPS** from observed peak × growth × headroom, with the arithmetic shown
- Sets **pass/fail thresholds** from your SLO — p95, p99, error rate, saturation — before the run
- Scaffolds a runnable **k6 / Locust / Gatling / vegeta** scenario with a ramp profile
- Enforces an **open arrival-rate model** and calls out the **coordinated-omission** trap
- Checks **environment parity** and reports the **first saturated resource**

## When it triggers

- "Load test this endpoint" / "will this survive the sale?"
- "Stress test the API" / "soak test overnight" / "spike test"
- "Write a k6 script" / "how many RPS can we handle?"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [perf-analysis](../perf-analysis) — reactive profiling once you find the bottleneck
- [observability](../observability) — the dashboards you watch during the run
- [production-readiness](../production-readiness) — load test evidence feeds the go/no-go gate
- [deploy-plan](../deploy-plan) — ship the capacity change safely
