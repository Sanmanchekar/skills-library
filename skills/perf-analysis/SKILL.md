---
name: perf-analysis
description: Analyze performance of a service, endpoint, or code path. Stack-agnostic loop — measure first (never guess), find the hot path via profiling, categorize the bottleneck (CPU / IO / DB / allocation / lock contention), then apply the smallest fix. Detects N+1 queries, missing indexes, chatty RPCs, sync-in-async, unbounded allocations, and cache misses. Triggered when the user says "this is slow", "make X faster", "profile this", or shares a slow endpoint / query / test.
---

# perf-analysis

## When to use

- User says: "this is slow", "make X faster", "profile this", "why is Y taking N seconds"
- User shares a slow endpoint, slow query, slow test suite, or a p99 latency alert

## The loop

```
1. MEASURE — establish a number (latency, throughput, memory). No number = no optimization.
2. PROFILE — find the hot path with a sampling profiler, tracing, or query log. Do NOT guess.
3. CATEGORIZE — the bottleneck is one of five shapes (below).
4. FIX — apply the smallest change that removes the bottleneck.
5. RE-MEASURE — confirm the number moved. If not, undo the change.
```

## The five bottleneck shapes

Every performance problem is (usually) one of these:

### 1. IO-bound (DB / RPC / disk)
Signal: profiler shows most time in wait states, network syscalls, or DB drivers.

Diagnoses:
- **N+1 queries** — loop calling the DB once per item. Fix with join / batch load / dataloader
- **Missing index** — check the query plan (EXPLAIN / EXPLAIN ANALYZE). Look for sequential scans on WHERE / JOIN columns
- **Chatty RPC** — many round-trips where one batch call would do
- **No connection pooling** — new TCP + TLS handshake per call
- **Serialized upstream calls** — parallelize with concurrent primitives (goroutines, asyncio.gather, Promise.all, threads)

### 2. CPU-bound
Signal: profiler shows time in your code, not in wait states. CPU at 100%.

Diagnoses:
- **Quadratic algorithm** (nested loops over the same data) — rethink data structures (hash lookup vs list scan)
- **Expensive serialization** — JSON encode/decode of large payloads; consider streaming or a binary format
- **Regex compiled per call** — hoist compile outside the loop
- **Hashing / crypto on every request** — cache the result

### 3. Memory / allocation
Signal: high GC pauses, growing RSS, or profiler shows allocator dominating.

Diagnoses:
- **Loading entire result set into memory** — stream / paginate
- **Boxing / autoboxing** in hot loops — use primitive collections where the language provides them
- **String concatenation in a loop** — use a builder / join
- **Closure captures** creating a garbage object per iteration

### 4. Lock / concurrency contention
Signal: many threads/goroutines, low CPU, throughput plateau. Profiler shows time in lock acquire.

Diagnoses:
- **Global lock on a hot path** — narrow the critical section
- **Lock held during IO** — release before the IO call
- **False sharing** (cache-line bouncing) — pad hot structs
- **Coarse-grained lock where per-key would do** — shard by key

### 5. Sync-in-async
Signal: async runtime with poor throughput despite low CPU.

Diagnoses:
- **Blocking call inside an async handler** — offload to a worker pool
- **Missing `await` / `.await`** — coroutine never awaited, running sequentially
- **Async lock held across await boundary** — turn into sync where possible or refactor

## Measurement toolbox (by need)

| Need | Category of tool | Runtime-agnostic notes |
|---|---|---|
| "How slow is it end-to-end?" | benchmark harness | your language's benchmark framework, or `hyperfine` for CLI, `wrk`/`k6`/`vegeta` for HTTP |
| "Where in code does time go?" | sampling profiler | flamegraph tools per runtime (perf, py-spy, async-profiler, pprof, node --prof, Instruments) |
| "Where in the DB does time go?" | query log + EXPLAIN | slow query log threshold ~100ms; ORM's query timing hook |
| "What allocates?" | heap profiler | your runtime's heap snapshot + differential comparison |
| "What locks contend?" | lock profiler / thread dump | JVM async-profiler lock mode, Go's `-mutexprofile`, `perf lock` |
| "What does the whole request touch?" | distributed tracing | OpenTelemetry — spans across service boundaries |

## The 80/20 checklist (start here, in this order)

1. Is there an obvious N+1? (Grep loop bodies for query calls, or check the ORM's query log for repeated identical shapes)
2. Does the slowest query have an index? (EXPLAIN on the top query in the slow log)
3. Are serial upstream calls that could be parallel?
4. Is the payload absurdly large? (Are you returning fields nobody uses?)
5. Is there a cache candidate? (Idempotent + hot + tolerable staleness)

## Output format

```markdown
# Perf analysis — <endpoint / query / code path>

## Baseline
- p50: 420ms · p95: 1.8s · p99: 3.2s
- Throughput: 45 req/s single-node
- Measured with: <tool>, <workload>

## Hot path
Profile shows 74% of wall time in `OrderService.list()`, of which 63% is DB.

## Bottleneck shape
IO-bound — N+1 on `Order.items` (one SELECT per order for 50 orders in the response).

## Fix
Add `prefetch_related('items')` (or equivalent) so 50 SELECTs become 2.

## Expected after
- p95 ~200ms (based on removing 48 round-trips × ~30ms each)

## Re-measure
- p50: 65ms · p95: 190ms · p99: 340ms ✓
```

## Rules

- NEVER optimize without a baseline number — you can't tell if you improved anything
- NEVER guess the hot path — profile
- NEVER apply more than one fix at a time before re-measuring — you won't know which one worked
- NEVER trade code clarity for perf without a measured win of ≥20%
- ALWAYS re-measure after every change
- ALWAYS look for the SHAPE first (IO / CPU / memory / lock / sync-in-async) — the fix falls out of the shape
