---
name: deploy-plan
description: Produce a per-change deployment plan — deploy order across services, database, and config (expand → migrate → contract), env vars / secrets / infra prerequisites, rollout strategy (rolling, blue-green, canary) with promotion gates and the metrics that decide them, a pre-deploy checklist, post-deploy verification commands with expected output, a rollback plan with time-to-rollback and data-compatibility notes, and blast radius. Never invents values — every unknown is flagged "⚠️ ACTION REQUIRED" with who to ask. Triggered when the user says "deploy plan", "how do we roll this out", "rollout plan", "plan the release of this PR", "canary plan", or "what's the deploy order".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# deploy-plan

## When to use

- User says: "deploy plan", "rollout plan", "how should we ship this", "canary plan", "what order do we deploy in"
- A change spans more than one deployable (service + DB migration, API + consumer, config + code)
- A change touches schema, queues/topics, secrets, feature flags, or infra
- NOT for customer-facing changelogs — use [release-notes](../release-notes)

## Steps

1. **Read the change** — diff, migrations, Helm/k8s/Terraform/compose files, CI/CD config, env/config loaders, feature-flag calls. List every deployable it touches.
2. **Inventory prerequisites** — new env vars, secrets, infra (topics, buckets, queues, DNS, IAM, firewall/egress rules), third-party config, feature flags. Value known from the repo → cite file:line. Not in the repo → `⚠️ ACTION REQUIRED`.
3. **Order the deploy** with expand → migrate → contract:

   | Phase | What ships | Must be true before next phase |
   |---|---|---|
   | 0. Prereqs | secrets, infra, flags (OFF) | resources exist, verified |
   | 1. Expand | additive schema (new nullable column / table / index CONCURRENTLY), new topics | old code still works |
   | 2. Deploy code | writers dual-write / read both shapes; consumers before producers for new message shapes | new code healthy on old + new data |
   | 3. Migrate | backfill in batches, flip flag progressively | backfill verified, error budget intact |
   | 4. Contract | drop old column/field/endpoint — a SEPARATE later release | no reader of old shape remains |

4. **Choose the strategy**:

   | Strategy | Pick when | Rollback speed |
   |---|---|---|
   | Rolling | stateless, backward-compatible, low risk | minutes (redeploy previous) |
   | Blue-green | need instant cutover/rollback, capacity for 2x | seconds (switch traffic) |
   | Canary | user-facing, risky logic, good metrics | seconds–minutes (shift weight to 0) |
   | Feature flag (dark launch) | logic risk independent of deploy | seconds (flag OFF) |

5. **Define promotion gates** — each canary step has a duration and numeric pass criteria compared against the baseline (error rate, p99, saturation, business metric).
6. **Write verification** — copy-pasteable commands with the exact expected output, for each phase.
7. **Write rollback** — per phase: the command, time-to-rollback, and whether data written by the new version is readable by the old version. Mark irreversible steps explicitly.
8. **State blast radius** — which users, tenants, regions, and downstream services are affected if it goes wrong, and the max impact during the canary window.

## Example — input → output

Input: "PR adds `orders.refund_reason` column, `orders-service` writes it, `reports-worker` reads it. New env var `REFUND_WEBHOOK_URL`."

````markdown
## Deploy order
| # | Phase | Action | Verify | Rollback |
|---|---|---|---|---|
| 0 | Prereq | Create secret `REFUND_WEBHOOK_URL` in staging + prod | `kubectl get secret orders-env -o jsonpath='{.data.REFUND_WEBHOOK_URL}'` → non-empty | delete secret |
| 1 | Expand | Run migration `0042_add_refund_reason` (nullable, no default) | `\d orders` shows `refund_reason text` | migration down (safe: column unused) |
| 2 | Deploy | `reports-worker` first (tolerates NULL) | logs: no `KeyError refund_reason` for 10 min | `kubectl rollout undo deploy/reports-worker` |
| 3 | Deploy | `orders-service` canary 5% → 25% → 100% | gates below | shift canary weight to 0 |

⚠️ ACTION REQUIRED — prod value for `REFUND_WEBHOOK_URL` is not in the repo. Ask: payments-api owners / platform team.
````

## Output format

````markdown
# Deploy plan — <change / PR title>

**Deployables**: <service-a>, <service-b>, <db>, <config>
**Strategy**: <rolling | blue-green | canary | flag> — why: <one line>
**Window**: <proposed> · **Owner**: <name or ⚠️ ACTION REQUIRED>

## Prerequisites
| Item | Type | Value / source | Status |
|---|---|---|---|
| REFUND_WEBHOOK_URL | secret | ⚠️ ACTION REQUIRED — ask <team> | missing |
| orders.refund-requested | topic | infra/topics.tf:12 | in PR |

## Pre-deploy checklist
- [ ] CI green on the exact SHA being deployed
- [ ] Migrations reviewed for locks / long-running ops
- [ ] Flags created and OFF in target env
- [ ] Dashboards open: <links or ⚠️ ACTION REQUIRED>
- [ ] On-call aware; rollback owner named

## Deploy order
| # | Phase | Action (command) | Verify (command → expected) | Rollback (command, TTR) |
|---|---|---|---|---|

## Promotion gates (canary)
| Step | Traffic | Hold | Pass if (vs baseline) | Abort if |
|---|---|---|---|---|
| 1 | 5% | 15 min | 5xx ≤ baseline + 0.1pp, p99 ≤ 1.2× baseline | any gate breached |

## Post-deploy verification
` ` `bash
curl -s https://<host>/healthz   # expect: {"status":"ok","version":"<sha>"}
` ` `

## Rollback plan
| Phase | Command | Time-to-rollback | Data compatibility |
|---|---|---|---|
| Contract (drop column) | — | IRREVERSIBLE | restore from backup only |

## Blast radius
- Users / tenants / regions: <...>
- Downstream services: <...>
- Max impact during canary: <% of traffic × duration>

## Open items
- ⚠️ ACTION REQUIRED — <item> — ask <who>
````

## Rules

- NEVER invent a value, hostname, secret, dashboard URL, or owner — flag `⚠️ ACTION REQUIRED` with who to ask
- NEVER ship a destructive schema change (drop/rename/type-narrow) in the same release as the code that stops using it
- NEVER deploy a producer of a new message shape before its consumers can read it
- NEVER write a verification step without the expected output
- NEVER write a rollback step without time-to-rollback and a data-compatibility note
- ALWAYS mark irreversible steps as IRREVERSIBLE and require a backup/restore path
- ALWAYS give canary gates numeric thresholds against a baseline — "looks fine" is not a gate
- ALWAYS cite file:line for every value taken from the repo

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: ship · **Agent**: `ship` · **Loop**: `rollout`
- **Reads**: `pr`, `findings`, `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `deploy-plan` → `deploy-plan.md`
- **Comes after**: code-review, db-migration, deprecation, production-readiness
- **Hand off to**:
  - `observability` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record deploy-plan --artifact deploy-plan=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
