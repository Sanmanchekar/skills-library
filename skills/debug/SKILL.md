---
name: debug
description: Systematic debugging loop — hypothesize the cause, instrument to prove it, narrow the surface, repeat. Blocks random print-statement flailing. Stack-agnostic — the loop applies to Python, Node, Go, Java, C++, Rust, Ruby, and any runtime. Handles crashes, hangs, wrong output, flaky tests, and heisenbugs. Triggered when the user says "debug this", "why is X failing", "help me figure out this bug", or pastes a stack trace / test failure.
---

# debug

## When to use

- User says: "debug this", "help me debug", "why is X happening", "why is this failing"
- User pastes a stack trace, test failure, or unexpected output
- Test is flaky, intermittent, or fails only in CI

## The loop (do NOT skip steps)

```
┌─────────────────────────────────────────────────────────┐
│ 1. Reproduce reliably (goal: 100% repro rate)           │
│ 2. Hypothesize (list 3+ possible causes, ranked)        │
│ 3. Instrument (add ONE targeted probe to prove or       │
│    disprove the top hypothesis)                         │
│ 4. Run again — did the evidence confirm or deny?        │
│ 5. If confirmed: apply fix + regression test. If denied:│
│    remove the probe, go to next hypothesis              │
└─────────────────────────────────────────────────────────┘
```

## Step 1 — Reproduce

If you can't reliably reproduce, you can't debug. Before ANY hypothesis, get to a 100% or near-100% repro.

- Exact command / URL / payload that triggers it
- Exact environment (branch, deps version, DB seed, OS, runtime version)
- If flaky: what's the frequency? What changes between runs?

If repro rate is < 100%: something in the input space is varying. Find what.

## Step 2 — Hypothesize

**List at least 3 hypotheses before writing any code.** Rank by prior probability (what changed recently? which layer is most brittle?).

Example: "user gets 500 on POST /orders"
| Rank | Hypothesis | Evidence would look like |
|---|---|---|
| 1 | DB constraint violation on new column | logs show integrity/constraint error on `orders.status` |
| 2 | Downstream API timeout | logs show timeout / connection error from the client |
| 3 | Auth middleware misconfigured for this route | logs show 401 before 500, or user_id is null |

## Step 3 — Instrument

**Add exactly ONE targeted probe per iteration.** Not five prints scattered around — one probe at the specific boundary the top hypothesis predicts.

Pick the tool by the *shape* of the bug, then use whatever your runtime provides:

| Bug shape | Probe category | Runtime-agnostic examples |
|---|---|---|
| Wrong value in a variable | log the value at that line, OR set an interactive breakpoint | your language's debugger (pdb / node inspect / delve / gdb / lldb / rdbg / byebug / jdb) |
| Wrong control flow | log at each branch entry | one log line per `if`/`else` branch |
| DB / RPC issue | log the exact query/URL + response | enable your ORM's query log; capture request/response of the RPC client |
| Hang / deadlock | thread / goroutine / task dump | send the runtime's dump signal (SIGQUIT for JVM/Go), or use an in-process profiler |
| CPU spike | sampling profiler | your runtime's flamegraph tool (perf / py-spy / async-profiler / pprof / node --prof) |
| Memory leak | heap snapshot + diff | take two snapshots minutes apart, diff top allocators |
| Flaky test | rerun many times with verbose logging | your runner's repeat flag; log inside the flaky assertion |
| CI-only failure | diff CI env vs local | runtime version, timezone, locale, DB engine, worker count, filesystem case sensitivity |

**Rule of thumb**: the probe should be so targeted that a single run tells you "hypothesis confirmed" or "hypothesis denied" — no ambiguity.

## Step 4 — Read the evidence honestly

- **Confirmed** → you know the cause. Go to step 5.
- **Denied** → hypothesis is wrong. **Remove the probe.** Don't leave debug logs in the codebase. Go back to step 2 with the next hypothesis.
- **Ambiguous** → your probe wasn't targeted enough. Add a more specific one.

## Step 5 — Fix + regression test

- Apply the fix
- Write a test that FAILS before the fix and PASSES after — this test guards the same bug from reappearing
- Remove ALL debug instrumentation — grep the diff for stray debug prints, log statements, breakpoints, or TODO markers before committing

## Common anti-patterns

| Anti-pattern | Correction |
|---|---|
| "Let me just try changing this and see" | Hypothesis first. What do you expect to change and why? |
| Adding 10 print statements at once | ONE probe per iteration |
| Fixing the symptom without a hypothesis | You'll fix the symptom, ship a subtler bug |
| Assuming the bug is somewhere obvious | Assume it's in code you haven't read yet — read it |
| Trusting the stack trace's top frame | The bug is often several frames up, in the caller |
| "It's flaky, let me retry it" (in CI) | Flakiness is a bug. Root-cause the flake |
| Reading the code and inferring behavior | Actually run it. Behavior beats belief |

## Heisenbug playbook

Bug goes away when you look at it? Common causes:
- **Timing**: adding a log slows the code enough to hide a race condition
- **Optimizer**: bug only reproduces at higher optimization levels
- **Memory layout**: uninitialized memory, dangling pointer, use-after-free
- **Environment**: locale, timezone, hash seed, filesystem case sensitivity
- **Test order**: a previous test polluted global state
- **Concurrency**: works single-threaded, breaks under parallelism (or vice versa)

Approach: keep the observation minimally invasive (sampling profiler, external tracing) rather than in-process logs that alter timing.

## Rules

- NEVER change code before forming a hypothesis
- NEVER add more than one probe per iteration
- NEVER leave debug prints / breakpoints / TODOs in the fix commit
- NEVER declare a bug fixed without a regression test
- ALWAYS explain why the fix works — "changed X and it works now" is not an explanation
