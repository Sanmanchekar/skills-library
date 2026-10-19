---
name: deprecation
description: Safely deprecate and remove an API, endpoint, feature, feature flag, config key, or library function. Finds every caller and consumer (code search plus access logs and metrics), announces with a dated timeline, adds Deprecation and Sunset HTTP headers (RFC 9745 / RFC 8594) and runtime warnings, writes the migration guide, runs scheduled brownouts, enforces a usage-to-zero gate before removal, and produces the removal PR with a rollback plan. Stack-agnostic. Triggered when the user says "deprecate X", "sunset this endpoint", "remove the v1 API", "kill this feature flag", "delete this old function safely", "who still calls this", or "plan the removal of Y".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# deprecation

## When to use

- User says: "deprecate", "sunset", "remove v1", "kill this flag", "who still uses this"
- A [tech-debt-scan](../tech-debt-scan) routed a dead-code / old-API item here
- A replacement exists (v2 endpoint, new function, new config) and the old path must go
- A feature flag has been 100% on (or off) for > 30 days

## Phased flow

| Phase | Gate to exit | Typical duration (external API) | Internal-only |
|---|---|---|---|
| 1. Inventory | Every caller listed with owner | 1–3 days | hours |
| 2. Announce | Timeline published; consumers notified | — | — |
| 3. Signal | Headers + warnings + metrics live | 1 deploy | 1 deploy |
| 4. Migrate | Migration guide; consumers moving | 3–12 months | 1–4 weeks |
| 5. Brownout | Scheduled failures done, no surprises | 2–4 weeks before sunset | optional |
| 6. Usage-to-zero | 0 calls for the agreed quiet period | 14–30 days quiet | 7 days quiet |
| 7. Remove | Removal PR merged + rollback ready | 1 deploy | 1 deploy |

## Phase 1 — Inventory

```bash
# Code callers (this repo and, if available, org-wide code search)
git grep -nE '<symbol>|/v1/orders|ORDERS_LEGACY_MODE'
# Access logs — who calls the endpoint, by client id / user agent, last 30d
# (adapt to your log store)
# ($3 = the field holding client id / user agent in your log format)
grep '/v1/orders' access.log | awk '{print $3}' | sort | uniq -c | sort -rn
```
```promql
sum by (client_id) (increase(http_requests_total{route="/v1/orders"}[30d]))
```

| Target type | Where callers hide |
|---|---|
| HTTP endpoint | access logs, API gateway analytics, partner integrations, mobile apps on old versions |
| Library function | other repos, published package consumers, reflection / string dispatch |
| Feature flag | flag-service evaluations, tests, config files, both code branches |
| Config key | env files, Helm values, IaC, secret stores, docs |
| Event / topic field | every consumer group, data warehouse, analytics jobs |

## Phase 2 — Announce

- Changelog + docs + direct notice to every identified consumer owner
- Timeline with dates: deprecation date, brownout dates, sunset date
- Name the replacement and link the migration guide

## Phase 3 — Signal

```http
HTTP/1.1 200 OK
Deprecation: @1767225600
Sunset: Wed, 30 Jun 2027 00:00:00 GMT
Link: <https://docs.example.com/migrate/orders-v2>; rel="deprecation"; type="text/html"
```
- `Deprecation` (RFC 9745) — structured-field date when deprecation took effect
- `Sunset` (RFC 8594) — HTTP-date after which the resource may stop responding
- Code: language-native deprecation markers (`@Deprecated`, `warnings.warn(..., DeprecationWarning)`, `// Deprecated:` doc comment, JSDoc `@deprecated`) + one rate-limited log line per caller
- Metric: `deprecated_usage_total{target, caller}` — this drives phase 6

## Phase 4 — Migration guide

```markdown
## Migrating from <old> to <new>
| Old | New | Notes |
|---|---|---|
| GET /v1/orders?id=1 | GET /v2/orders/1 | `total` now in minor units |
Before/after code sample · behavioural differences · deadline · contact
```

## Phase 5 — Brownout

- Return `410 Gone` (or the target's failure mode) for short scheduled windows: e.g. 10 min, then 1 h, then 4 h, announced in advance
- Error body names the replacement and the guide URL
- Monitor who breaks; contact them directly

## Phase 6 — Usage-to-zero gate

- [ ] `deprecated_usage_total` = 0 for the full quiet period (excluding your own health checks)
- [ ] Every listed consumer confirmed migrated
- [ ] No traffic during last brownout from unknown callers
- [ ] Owner sign-off recorded

Non-zero usage after sunset date → extend, escalate to consumer owner; never remove blind.

## Phase 7 — Remove + rollback

- Removal PR deletes code, tests, docs, config, flag definitions, metrics, and dashboards for the target
- Endpoint: keep a stub returning `410 Gone` with guide link for one more cycle
- Rollback: the removal is a single revertable PR; DB/schema drops happen in a later, separate PR (see [db-migration](../db-migration))

## Example

Input: "Deprecate GET /v1/orders in orders-service; v2 exists."

Output (excerpt): Inventory finds 3 callers (web app, `billing-worker`, partner `acme` 4k req/day) → Deprecation/Sunset headers added → sunset 2027-06-30 → brownouts May 2027 → gate: 0 calls for 30 days → removal PR + 410 stub.

## Output format

```markdown
## Deprecation plan — <target>

### Target
- What: <endpoint / function / flag / config>   Replacement: <new>
- Owner: <team>   Sunset date: <YYYY-MM-DD>

### Consumers
| Consumer | Owner | Evidence (code ref / calls per day) | Migrated? |

### Timeline
| Date | Phase | Action |

### Signals added
- Headers / warnings / metric names

### Usage-to-zero gate
- [ ] ...

### Removal + rollback
- Removal PR scope · stub behaviour · revert procedure
```

## Rules

- NEVER remove anything with non-zero usage — the gate is data, not a calendar date
- NEVER rely on code search alone for endpoints — check access logs and metrics
- NEVER combine code removal and data/schema deletion in the same PR
- NEVER change behaviour of the deprecated path during deprecation — only add signals
- ALWAYS publish dates (deprecation, brownouts, sunset) and the replacement together
- ALWAYS add a usage metric before announcing — you cannot run the gate without it
- ALWAYS brown out before sunset for external consumers
- ALWAYS keep the removal a single revertable change

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: maintain · **Agent**: `maintain`
- **Reads**: `debt-register` (from `.lifecycle/<run>/` when present)
- **Writes**: `deploy-plan` → `deploy-plan.md`
- **Comes after**: tech-debt-scan
- **Hand off to**:
  - `deploy-plan` — always
  - `release-notes` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record deprecation --artifact deploy-plan=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
