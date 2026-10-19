---
name: feature-flag-rollout
description: Wrap a risky change in a feature flag and plan its rollout — picks the flag type (release / ops / experiment / permission), names it, defaults it off, adds a kill switch, defines a progressive ramp (1% → 5% → 25% → 50% → 100%) with gate metrics and hold times per step, sets a cleanup date and owner, and adds tests for both flag paths. Vendor-neutral (OpenFeature, LaunchDarkly, Unleash, Flagsmith, GrowthBook, or a config table). Blocks flag debt and nested-flag combinatorics. Triggered when the user says "put this behind a flag", "feature flag this", "plan the rollout", "gradual rollout", "canary this change", "kill switch", or "clean up old flags".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# feature-flag-rollout

## When to use

- User says: "put this behind a flag", "feature flag this", "plan the rollout", "ramp this to 10%", "kill switch", "dark launch"
- Change alters a hot path, a data write, a third-party call, pricing/money logic, or user-visible behaviour
- A design doc's rollout table needs concrete flag steps
- User asks to "clean up flags" or audit stale ones

## Flag types

| Type | Purpose | Lifetime | Default | Example |
|---|---|---|---|---|
| Release | Hide unfinished / risky code path | days–weeks, then delete | off | `orders.cancel-window` |
| Ops / kill switch | Turn off a dependency or expensive path under load | long-lived, documented | on (feature) / off (degrade) | `ops.payments-api.refunds-enabled` |
| Experiment | A/B test with measured outcome | until decision | control | `exp.checkout-one-page` |
| Permission | Entitlement per plan / tenant | permanent (it is product config) | off | `perm.bulk-export` |

## Steps

1. **Find the flag system** — Grep for an existing SDK/provider (`openfeature`, `launchdarkly`, `unleash`, `flagsmith`, `growthbook`, a `feature_flags` table). Use it; never add a second one.
2. **Choose the type** from the table above and name it `<area>.<feature>` (kebab-case, no `new-`/`v2` — those age badly).
3. **Default off, fail safe** — if the flag service is unreachable, evaluation returns the default, and the default is the old path.
4. **Wrap at one seam** — a single decision point near the entry (handler, use-case, job). Pass the result down; do not re-evaluate deep in the call stack.
5. **No nesting** — a flag check inside another flag's branch is forbidden. If two flags interact, make them one flag or document the full matrix and test every cell.
6. **Kill switch** — confirm the flag can be flipped off in production in < 1 minute without a deploy, and who is allowed to flip it.
7. **Write the ramp plan** — steps, targeting (internal → % of users, sticky by stable ID), gate metrics, hold time, rollback trigger.
8. **Test both paths** — unit/integration tests run with flag on AND off. Data written under the new path must be readable by the old path (rollback safety).
9. **Set cleanup** — owner + removal date (release flags ≤ 30 days after 100%). Add a ticket and a `TODO(flag-cleanup YYYY-MM-DD @owner)` at the seam.

## Default ramp

| Step | Audience | Hold | Gate metrics (vs control) | Rollback if |
|---|---|---|---|---|
| 0 | internal / staff accounts | 1 day | no new error types in logs | any new 5xx class |
| 1 | 1% | 1 hour+ | error rate, p95 latency | error rate > +0.5 pp or p95 > +20% |
| 2 | 5% | 4 hours | + business metric (conversion, success rate) | business metric down > 2% |
| 3 | 25% | 1 day | + downstream load (DB CPU, vendor 429s) | saturation alert fires |
| 4 | 50% | 1 day | all above | any gate fails |
| 5 | 100% | — | all above for 7 days | — then start cleanup |

Adjust thresholds to the service's SLOs; never ramp on a step whose gate metric has no dashboard.

## Output format

````markdown
## Flag plan — <flag-key>

| Field | Value |
|---|---|
| Type | release / ops / experiment / permission |
| Default | off (old path) |
| Fail mode | provider down → default |
| Seam | `<path:line>` |
| Kill switch | <how, who, time to effect> |
| Owner | @<handle> |
| Cleanup by | YYYY-MM-DD (ticket <link>) |

### Code
```<lang>
<the single flag check at the seam>
```

### Ramp
| Step | Audience | Hold | Gate metrics | Rollback if |

### Tests
- [ ] flag off → old behaviour (<test name>)
- [ ] flag on → new behaviour (<test name>)
- [ ] data written with flag on is readable with flag off
````

## Example

**Input**: "Route refund calls in orders-service through the new payments-api v2 client."

**Output (excerpt)**:

```python
# orders/refunds.py — single seam
if flags.is_enabled("orders.refunds-via-payments-v2", ctx=user_ctx, default=False):
    result = payments_v2.refund(order.id, amount_minor, idempotency_key=key)
else:
    result = payments_v1.refund(order.id, amount_minor)
# TODO(flag-cleanup 2026-12-15 @orders-team) remove v1 branch
```

| Step | Audience | Hold | Gate metrics | Rollback if |
|---|---|---|---|---|
| 1 | 1% of merchants (sticky by merchant_id) | 2 h | refund success rate, payments-api p95 | success rate < 99.5% |

## Rules

- NEVER default a release flag to on, and NEVER let a flag-service outage enable the new path
- NEVER nest flag checks — collapse or fully test the matrix
- NEVER evaluate the same flag at multiple layers — one seam, pass the decision down
- NEVER ramp past a step without the gate metric visible on a dashboard
- NEVER ship a release flag without an owner and a cleanup date
- ALWAYS test both paths, including old-path reads of new-path data
- ALWAYS bucket percentages by a stable ID so users don't flip between paths

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: build · **Agent**: `build`
- **Reads**: `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `deploy-plan` → `deploy-plan.md`
- **Comes after**: tech-design

This skill works on its own; the hand-offs above are suggestions. If the `lifecycle-router` skill is installed, record the step so the next skill can pick up the output: `route.py run record feature-flag-rollout --artifact deploy-plan=<path>`. If it is not installed, skip this and just name the next skill to the user.
<!-- lifecycle:end -->
