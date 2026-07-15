---
name: estimation
description: Break a spec / PRD / feature into tasks with T-shirt sizes (XS / S / M / L / XL), risk flags, dependencies, and an honest range (best / likely / worst). Detects hidden work (migrations, tests, docs, rollout, oncall handoff). Triggered when the user asks to "estimate this", "size these tasks", "how long will X take", or shares a spec with a deadline.
---

# estimation

## When to use

- User asks: "estimate this", "size these tasks", "how long will X take", "break this down"
- User shares a PRD, spec, or ticket that needs planning
- Sprint planning / roadmap conversation

## Steps

1. **Understand the ask** — read the spec / PRD. If it's thin, ask clarifying questions BEFORE estimating. A bad estimate on an unclear spec is worse than admitting you can't estimate yet.
2. **Break it down** into tasks (see rules below).
3. **Size** each task with the T-shirt scale.
4. **Flag risks** per task.
5. **Sequence** — identify dependencies and the critical path.
6. **Aggregate** into a best / likely / worst range at the feature level.
7. **List explicit assumptions** — every assumption is a risk when it turns out wrong.

## T-shirt scale

Scale to your team's velocity. These are rough anchors for a single mid-level engineer:

| Size | Effort | Example |
|---|---|---|
| **XS** | < 2 hours | small config change, simple bug fix, add a log line |
| **S** | ½ day | small function + tests, small UI tweak |
| **M** | 1-2 days | one new endpoint end-to-end, small refactor |
| **L** | 3-5 days | new subsystem, non-trivial migration, cross-cutting change |
| **XL** | 1-2 weeks | **too big, split it** — XL is a smell, not a size |
| **XXL** | > 2 weeks | absolutely split |

Anything **XL or larger MUST be split** before estimating. Large estimates hide unknowns.

## Task breakdown rules

For every feature, the task list MUST include (or explicitly exclude with reason):

- [ ] Design / spike (if approach is unclear)
- [ ] Backend implementation
- [ ] Frontend implementation
- [ ] Database migration (if data model changes)
- [ ] Tests — unit + integration + E2E for critical paths
- [ ] Documentation — API docs, README, ADR if architectural
- [ ] Feature flag / rollout wiring
- [ ] Observability — metrics + logs + alerts
- [ ] Runbook (if new operational surface)
- [ ] Deploy pipeline changes (if any)
- [ ] Code review + revision cycles (add 20-30% of implementation time)
- [ ] QA / manual testing
- [ ] Communication (announcement, docs update, training)

The most-missed items: migrations, docs, observability, review cycles.

## Risk flags (add to any task)

- 🟨 **Unknown API** — first time using a lib / service / API
- 🟥 **External dependency** — waiting on another team / vendor
- 🟥 **Novel architecture** — pattern not used in this codebase before
- 🟨 **High blast radius** — touches auth / payments / core data
- 🟨 **Requires coordination** — multi-service change, deploy order matters
- 🟥 **No prior art** — nobody on the team has done this

## Aggregation

Sum task sizes, then apply the range factor:

| Confidence | Best | Likely | Worst |
|---|---|---|---|
| Well-scoped, prior art exists | sum × 0.9 | sum × 1.2 | sum × 1.6 |
| Some unknowns | sum × 1.0 | sum × 1.5 | sum × 2.5 |
| Novel / lots of unknowns | sum × 1.2 | sum × 2.0 | sum × 4.0 |

If your worst is > 2× your likely, you have too much uncertainty — spike first.

## Output format

```markdown
# Estimate — <feature>

## Assumptions
- <assumption 1> — if wrong, add <impact>
- <assumption 2>

## Task breakdown
| # | Task | Size | Risk | Depends on |
|---|---|---|---|---|
| 1 | Design spike — session storage | S | 🟨 | — |
| 2 | Add sessions table + migration | M | 🟨 | 1 |
| 3 | Session middleware + JWT swap | M | 🟥 auth blast | 1, 2 |
| 4 | Feature flag rollout wiring | S | | 3 |
| 5 | Observability — session metrics | S | | 3 |
| 6 | Docs + runbook | S | | 3 |
| 7 | Code review cycles | M | | 3-6 |
| 8 | Manual QA | S | | 3-6 |

## Critical path
1 → 2 → 3 → (4, 5, 6 parallel) → 7 → 8

## Aggregate (in engineer-days)
- Sum of sizes: ~8 days
- Confidence: some unknowns (novel session store)
- **Best**: 8 days · **Likely**: 12 days · **Worst**: 20 days

## Risks
- Session store choice not yet decided (Redis vs Postgres). Spike (task 1) should resolve within 4 hours.
- Auth touching = high blast radius; will need thorough review + staged rollout.

## Not included
- Marketing / launch comms — separate track
- Analytics dashboards — followup ticket
```

## Rules

- NEVER give a single number — always a range
- NEVER estimate anything XL — split it first
- NEVER omit review / docs / tests / observability — those are the most-missed items
- NEVER commit to the "best" case — commit to "likely" and communicate "worst"
- ALWAYS list assumptions — they are the failure modes
- ALWAYS re-estimate after the first spike or after every major discovery
