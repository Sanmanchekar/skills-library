# Performance Analysis Skill — Profiling & Bottleneck Fix for Claude Code, Cursor, Copilot

> **Stop guessing at performance. Measure, profile, categorize, fix, re-measure.** Detects N+1 queries, missing indexes, CPU hot loops, allocation storms, lock contention, and sync-in-async — stack-agnostic.

**Keywords**: performance analysis, ai profiling, n+1 query detection, slow query analysis, cpu profiler, flamegraph, memory leak analysis, lock contention, sync in async, perf claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- perf-analysis
```

## What it does

- Enforces a **5-step loop**: measure → profile → categorize → fix → re-measure
- Categorizes every bottleneck as **one of five shapes** — IO / CPU / memory / lock / sync-in-async
- Fix falls out of the shape — no more shotgun optimization
- **Stack-agnostic** tool table — points at your runtime's native profiler/tracer
- **80/20 checklist** — 5 quick wins to try first (N+1, missing index, serial-that-could-be-parallel, oversized payload, cache candidate)
- Blocks one-fix-at-a-time cheating — you must re-measure between changes

## When it triggers

- "This is slow" / "make X faster" / "profile this"
- Slow endpoint / slow query / slow test suite shared
- p99 latency alert

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [debug](../debug) — for correctness bugs (not perf)
- [observability](../observability) — dashboards to catch regressions
- [db-migration](../db-migration) — index changes as a proper migration
