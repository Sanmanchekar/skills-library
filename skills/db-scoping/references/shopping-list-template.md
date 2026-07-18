# Data-dependency shopping list template — db-scoping

Read this file when Step 6 needs to produce the evidence packet.

Also used verbatim as the body of the per-run `.audit/db-scoping/data-dependencies-YYYY-MM-DD.md` snapshot.

```markdown
# DB scoping audit — <service name>

**Scanned at**: <UTC> · Run #<N>
**Service**: <path>
**This service owns**: <one sentence — owned-data statement>

## Table inventory
| Table | Access | Classification | Owner (inferred) | Evidence |
|---|---|---|---|---|
| payment_orders | RW | owned (evidenced) | this-service | migrations/0003_…:12 |
| institutes | R | foreign-read | identity/institute | cashfree/…/order_helper.py:88 |
| provider_config | R | shared-reference | lending | …:142 |
| user_profile | RW | foreign-write | identity | …/webhook_helper.py:210 |
| ledger_entry | — | ambient (unused) | finance | imported via master_models, never queried |

**Totals**: <N> tables touched · <owned> owned · <fr> foreign-read · <fw> foreign-write · <sr> shared-reference · <amb> ambient

## Summary
This service touches N tables it does not own. Ranked by dependency risk:

1. <table/domain> — <foreign-write> · <cross-domain-txn>
2. <table/domain> — <foreign-read> · <cross-context-join>
3. ...

Delegating these would remove ~X cross-context joins, close Y two-writer hazards, and shrink the ambient schema surface from Z tables to the M this service owns.

## Shopping list (grouped by owning domain)

### 1. Needs: read access to `<domain>`-service (stop touching `<foreign-tables>`)

**What's here now**
- `<table>` — <access>, N sites: `<file:line>`, … (<detail: joins, key access pattern>)
- `<table>` — <access>, M sites: `<file:line>` (<detail>)

**Coupling smells**
- 🔴 CRITICAL `foreign-write` — `<file:line>` `UPDATE <table> SET …`. <impact: two writers, invariants unenforced, silent breaks on owner schema change>
- 🔴 CRITICAL `cross-domain-txn` — that write sits inside the same `atomic()` as the <owned-table> update; <owner>-side lock/timeout now rolls back a <this-service action>.
- 🟠 HIGH `cross-context-join` — `SELECT … FROM <owned> JOIN <foreign> …` couples the two schemas' query plans; neither domain can be split/sharded independently.

**Why it's out of scope**
<One sentence anchored to this service's owned-data statement.>

**What this service needs (consumer's ask)**
<See references/consumer-ask.md — use that template>

**Impact of delegating**
- Closes N two-writer hazards and M cross-domain transactions
- Removes X cross-context joins → domains can be split/sharded independently
- Drops read of Y columns never used (smaller blast radius on owner schema changes)

---

### 2. Needs: reference access to `<domain>`-service (`<config-tables>`)
... (same shape — usually shared-reference, lower severity)

---

## What this service should keep (owned data)

Tables that DO belong to this service and stay local:
- `<table1>`, `<table2>` — created in this service's migrations, sole writer, core domain
- <idempotency/dedup tables> — <core competence rationale>

## Ambient surface to shed (least privilege)

The service imports a shared all-tables models module exposing <declared> tables but queries only <queried>. The <declared − queried> unused tables are ambient access with no purpose — narrow the import so the service can only reach what it owns + its declared dependencies.

## Confirm with architecture (inferred ownership)

These ownership calls are **inferred**, not evidenced by a local migration — confirm before acting:
- `<table>` → assumed <domain>
- `<table>` → assumed <domain>
- ...

## What's out of scope for this audit
- How each owning domain exposes the data (API vs event vs replica) — their call, informed by all consumers
- Physical schema/index/partition/shard design
- Whether the shared database should be physically split at all (architecture decision)

## Next step
Hand this list to architecture + the owning-domain teams. They'll confirm ownership, decide how to expose the data, and come back with the interface to migrate to.
```
