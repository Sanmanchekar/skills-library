---
name: db-scoping
description: Audit a single service for the database tables it actually touches — via raw SQL, ORM models/queries, and shared-model imports — then classify each table as owned by this service vs. foreign (owned by another domain), and flag direct cross-domain reads/writes it should instead consume through the owning domain's API, read-model, or event stream. Produces a "data-dependency shopping list" (which domain-owning service each foreign table should come from, with the read-model this service actually needs) plus a full table inventory with coupling-smell evidence. Stack-agnostic (Django, SQLAlchemy, Prisma, TypeORM, Sequelize, ActiveRecord, GORM, JPA/Hibernate, Mongoose, raw SQL). Out of scope: how the owning service exposes the data, physical schema/index design, sharding mechanics. Triggered when the user says "what tables should this service NOT touch", "audit the DB scope", "data ownership audit", "which tables does X actually use", "bounded-context audit", "what data should this service own", or "db scoping".
---

# db-scoping

## The core reframe

A payments service should own payment tables. It should NOT be issuing `SELECT ... FROM students JOIN institutes` or `UPDATE lender_config SET ...`. Those tables belong to other domains. Reaching into them directly is the database-level version of implementing a capability you shouldn't own — except worse, because the coupling is invisible until the owning team alters a column and your service breaks at runtime with no compile-time signal.

The goal is NOT to "carve up the database" (that's a platform/architecture decision informed by every service). The goal is to identify **the data dependencies this service should declare on the domains that own that data** — so it stops treating another team's tables as its own local storage and instead consumes them through an owned interface (API, read-model, or event stream).

Owning a table means: you define its migrations, you are the only writer, and its schema changes are your call. Everything else this service touches is borrowed — and borrowed-by-direct-SQL is the coupling this audit surfaces.

## Explicitly out of scope

This skill produces the **consumer's data ask**. It does NOT design the provider:
- How the owning domain exposes the data (REST vs gRPC vs event stream vs read replica) — the owner's call, informed by all consumers
- Physical schema design, index choices, partitioning, or sharding mechanics
- Whether the org should split the monolith DB at all (that's an architecture decision)
- Which team owns which table in the org chart (this skill *infers* ownership and flags it for confirmation — it does not adjudicate)
- Query performance tuning (N+1, missing indexes) unless the fix is "stop reading this foreign table" — use a perf skill for pure performance work

## When to use

- User says: "what tables should this service NOT touch?", "audit the DB scope", "data ownership audit", "which tables does X actually use?", "bounded-context audit", "what data should this service own?"
- New service scoping — what data dependencies it should declare from day one vs. what it should own
- Monolith-to-services planning — establishing each service's data boundary before a split
- Post-incident: "the outage happened because [payments] read a column [profile] renamed" — should we depend on that table directly?
- A service imports a giant shared/generated models module (an "all-tables" file) — establish which of those hundreds of tables it actually uses, and of those, which are foreign

## The argument

- **Required**: `service` — the single service (repo path or directory) to audit
- **Optional**: `domain_map` — a mapping of table-name patterns → owning domain (e.g., `student* → identity`, `lender* → lending`). If not supplied, the skill infers ownership from migration evidence + naming, marks every inference `inferred`, and asks the user to confirm the domain map before finalizing when ownership is ambiguous.
- **Optional**: `tables` — restrict the audit to specific tables (default: every table the service touches)

## Table classifications (the heart of the audit)

Every table the service touches lands in exactly one bucket:

| Classification | Definition | Verdict |
|---|---|---|
| `owned` | This service creates it in its own migrations, is the sole writer, name sits in its domain | **KEEP** — this is the service's job |
| `foreign-write` | Service issues INSERT/UPDATE/DELETE on a table it did not create | 🔴 **worst** — two-writer problem; delegate the write to the owner |
| `foreign-read` | Service SELECTs/JOINs a table it did not create and does not write | 🟠 delegate to the owner's read-model/API |
| `shared-reference` | Read-only central lookup/config (currencies, PG config, lender master) owned centrally | 🟡 acceptable via a reference service / cached replica; flag, low priority |
| `ambient` | Reachable through an imported all-tables models module but never actually queried | 🟢 dead access surface — remove from imports (least privilege) |

### How to infer ownership in a single-service audit

You cannot see the other services, so infer ownership from evidence, weakest claim to strongest:

1. **Migration evidence (strongest)** — if the service's own migrations `CREATE TABLE`/`CreateModel`/`create_table` it, that's a strong `owned` signal. A table queried with **no** local migration touching it is likely foreign.
2. **Write asymmetry** — writing a table you created ⇒ owned. Writing a table you did NOT create ⇒ `foreign-write` (the red flag). Reading only ⇒ at most `foreign-read`.
3. **Domain-name mapping** — apply `domain_map` if given; else use naming heuristics (prefixes/roots) and mark `inferred`.
4. **Shared models module** — a large generated models file exposing the whole DB (e.g. a single `*_models.py`, `schema.prisma` with hundreds of models, one `models/index.ts`) means the service has *ambient* access to everything. Only the subset it actually queries counts; of that subset, anything it doesn't own is a real dependency, the rest is `ambient`.

Always tag inferred ownership as `inferred: true` and list it under "Confirm with architecture" — mirror the discipline of not adjudicating org ownership yourself. If ownership is ambiguous and no `domain_map` was given, ASK the user before finalizing (a wrong owner makes every recommendation wrong).

## Steps

### 1. Establish this service's domain + owned-data statement (one sentence)
Read the top of `README.md`, top-level directories, the migrations folder, and the main models module. Write ONE sentence: **"This service owns: X data; its job is: Y."**

Example: "This service owns payment orders, PG transactions, settlements, and webhook records; its job is to route payments to gateways and reconcile them." This anchors every classification — any table outside "owns X" that is written directly is a red flag.

### 2. Build the table inventory (this service ONLY)
Sweep the service using the detection tables below. For every table, record:

`table | access (R / W / RW) | how detected (raw-sql | orm-model | orm-query | import-only) | evidence path:line`

Resolve ORM models to physical table names before de-duping (two model classes may map to one table; a raw query and an ORM query may hit the same table). Do NOT compare across services — single-service audit.

### 3. Classify + find migration/ownership evidence
For each inventoried table:
- Grep the service's migrations for a CREATE/ALTER of it → sets/strengthens `owned`.
- Apply the write-asymmetry + domain-name rules → assign one classification bucket.
- Record whether ownership is `inferred` or `evidenced` (local migration found).

### 4. For each foreign table (or group), produce the case
Each case has FIVE fields:

| Field | Content |
|---|---|
| **What's here now** | access pattern + evidence file:line + inferred owning domain |
| **Coupling smells** | foreign-write, cross-domain-txn, cross-context-join, ambient-schema-import, foreign-column-read, foreign-fk, etc. |
| **Why it's out of scope** | one sentence tied back to step 1's owned-data statement |
| **What this service needs (consumer's ask)** | the read-model / API / event the service wants from the owning domain instead of the direct table access |
| **Impact of delegating** | joins removed, two-writer hazards closed, ambient surface shrunk, deploy/shard coupling broken |

### 5. Rank
Order by **risk of the direct dependency**, roughly = (write? × cross-domain-txn? × schema-fragility × frequency). `foreign-write` and `cross-domain-txn` always rank above `foreign-read`. Highest-risk first.

### 6. Produce the shopping list
Group foreign tables by **owning domain** (the party this service would depend on) and emit the output template below. This is what the service team hands to architecture / the domain-owning teams.

### 7. Persist + summarize
- **Write** `.audit/db-scoping/TODO.md` (mergeable, reconcilable) and `.audit/db-scoping/data-dependencies-YYYY-MM-DD.md` (immutable per-run snapshot).
- **Print** a dated terminal summary — classification breakdown, top-N by risk, diff vs prior run, files-written pointer, next actions.
- On re-runs, MERGE with existing TODO.md — never clobber user check-offs, `#wontfix` tags, confirmed-ownership notes, or team notes.

---

## Detection tables

The tables tell you WHAT to look for. You're auditing ONE service and resolving everything to **physical table names**.

### Raw SQL (any language — string literals + `.sql` files)
| Signal | Patterns to grep | Access |
|---|---|---|
| Read | `FROM\s+[\`"'\[]?(\w+)`, `JOIN\s+[\`"'\[]?(\w+)` | R |
| Insert | `INSERT\s+INTO\s+[\`"'\[]?(\w+)`, `INTO\s+(\w+)\s*\(` | W |
| Update | `UPDATE\s+[\`"'\[]?(\w+)\s+SET` | W |
| Delete | `DELETE\s+FROM\s+[\`"'\[]?(\w+)` | W |
| Upsert | `ON\s+CONFLICT`, `ON\s+DUPLICATE\s+KEY`, `MERGE\s+INTO\s+(\w+)`, `REPLACE\s+INTO\s+(\w+)` | W |
| Exec entry points | `cursor.execute`, `session.execute(text(`, `db.query`, `conn.exec`, `.raw(`, `knex.raw`, `sequelize.query` | (parse the SQL) |

### ORM model → physical table (declaration = potential ownership; query = access)
| Stack | Model declaration | Physical table name source | Query/write verbs |
|---|---|---|---|
| Django | `class X(models.Model)` | `Meta.db_table` else `<applabel>_<classname_lower>` | `.objects.filter/get/all` (R); `.save/.create/.update/.delete/.bulk_create` (W) |
| SQLAlchemy (declarative) | `class X(Base)` | `__tablename__` | `session.query/select` (R); `session.add/.merge/.delete`, `Model()` + commit (W) |
| SQLAlchemy (core) | `Table('name', metadata, …)` | first arg | `.select()` (R); `.insert()/.update()/.delete()` (W) |
| Prisma | `model X {` in `schema.prisma` | `@@map("name")` else model name | `.findMany/.findUnique` (R); `.create/.update/.upsert/.delete` (W) |
| TypeORM | `@Entity('name')` / `@Entity({name:…})` | arg | `.find/.findOne/QueryBuilder` (R); `.save/.insert/.update/.delete` (W) |
| Sequelize | `sequelize.define('name'`, `@Table` | `tableName` else pluralized model | `.findAll/.findByPk` (R); `.create/.update/.destroy` (W) |
| ActiveRecord (Rails) | `class X < ApplicationRecord` | `self.table_name=` else `pluralize(X)` | `.where/.find` (R); `.save/.create/.update/.destroy` (W) |
| GORM (Go) | struct + `func (X) TableName()` | return value else `pluralize(snake(X))` | `.Find/.First` (R); `.Create/.Save/.Update/.Delete` (W) |
| JPA/Hibernate | `@Entity` + `@Table(name=…)` | `@Table.name` else class name | `find/JPQL/criteria` (R); `persist/merge/remove` (W) |
| Mongoose (Mongo) | `mongoose.model('X', schema)` | collection = pluralized `X` | `.find` (R); `.create/.updateOne/.deleteOne` (W) |
| Ecto (Elixir) | `schema "name"` | arg | `Repo.all/.get` (R); `Repo.insert/.update/.delete` (W) |

### Migrations (ownership evidence — who CREATEs the table)
| Stack | Signal |
|---|---|
| Any SQL | `CREATE TABLE`, `ALTER TABLE`, `V<n>__*.sql` (Flyway), Liquibase changesets |
| Django | `migrations/` dir, `migrations.CreateModel`, `AlterField` |
| Alembic | `alembic/versions/`, `op.create_table` |
| Rails | `db/migrate/`, `create_table` |
| Prisma | `prisma/migrations/`, `CREATE TABLE` in `migration.sql` |
| TypeORM | `@migration`, `queryRunner.createTable` |

### Shared / generated all-tables models module (the ambient-access anti-pattern)
| Signal | Patterns to grep |
|---|---|
| Giant generated models file | a single models file far larger than the service's own tables (e.g. `sqlacodegen`/`inspectdb` output); count declared tables vs. tables the service actually queries |
| Broad import | `from <shared_models> import *`, `import { * } from './models'`, one module re-exporting hundreds of entities |
| Signal to compute | `declared_tables` (in the module) − `queried_tables` (actually used) = ambient surface to shed |

### Cross-context coupling smells (severity)
| Smell | Detect | Severity |
|---|---|---|
| `foreign-write` | INSERT/UPDATE/DELETE/upsert on a table with no local migration + outside owned domain | 🔴 CRITICAL |
| `cross-domain-txn` | a foreign write (or read-for-update) inside the same `transaction`/`atomic`/`BEGIN…COMMIT` as an owned write | 🔴 CRITICAL |
| `cross-context-join` | a single SQL `JOIN` (or ORM relation traversal) between an owned table and a foreign table | 🟠 HIGH |
| `ambient-schema-import` | service imports an all-tables shared models module (no bounded context) | 🟠 HIGH |
| `foreign-column-read` | SELECT of specific columns of a foreign table (silent break when owner alters schema) | 🟠 HIGH |
| `foreign-fk` | FK / ORM relationship constraint pointing at a foreign table (hard DB coupling; blocks independent deploy/shard) | 🟡 MEDIUM |
| `shared-reference-read` | direct read of a central config/reference table | 🟡 MEDIUM |
| `ambient-unused` | table reachable via import but never queried | 🟢 LOW |

---

## Writing the "consumer's data ask" (step 4, field 4)

The most important field. Frame from THIS service's perspective — what interface does it want from the owning domain, instead of the raw table. Do NOT specify the transport (REST/gRPC/event/replica) — that's the owner's decision informed by all consumers.

```markdown
### What this service needs

**As a consumer**, this service needs to <read | be notified about> <foreign data> WITHOUT touching `<table>` directly:

- `get_<entity>(<id>) -> { <only the fields we actually use> }` — <when we call it, what we key on>

**Access pattern we need**:
- <point-lookup by id> / <batch by ids (list the call sites that loop)> / <filtered list>

**Freshness we need**:
- <strong — must reflect the latest write> OR <eventual — seconds of lag OK> OR <daily snapshot OK>

**If a write is involved** (foreign-write cases):
- We currently write `<table>` at `<file:line>` to <effect>. We need `<owner>` to expose `<command(...)>` so the owner performs that write — we stop being a second writer.

**What we do NOT need from this party**:
- <the full row — we only read N of M columns>
- <write access — read-only is enough>
- <joins performed on our side — the owner can pre-join and hand us a projection>
```

The point: this service states the *data* it needs and the *shape* it needs it in — it does not design the owner's storage.

---

## Output — the data-dependency shopping list

```markdown
# DB scoping audit — <service name>

**Scanned at**: <UTC> · Run #<N>
**Service**: <path>
**This service owns**: <one sentence — owned-data statement>

## Table inventory
| Table | Access | Classification | Owner (inferred) | Evidence |
|---|---|---|---|---|
| dt_payment_order | RW | owned (evidenced) | this-service | migrations/0003_…:12 |
| institutes | R | foreign-read | identity/institute | cashfree/…/order_helper.py:88 |
| lender_config | R | shared-reference | lending | …:142 |
| student_profile | RW | foreign-write | identity | …/webhook_helper.py:210 |
| ledger_entry | — | ambient (unused) | finance | imported via master_models, never queried |

**Totals**: <N> tables touched · <owned> owned · <fr> foreign-read · <fw> foreign-write · <sr> shared-reference · <amb> ambient

## Summary
This service touches N tables it does not own. Ranked by dependency risk:

1. <table/domain> — <foreign-write> · <cross-domain-txn>
2. <table/domain> — <foreign-read> · <cross-context-join>
3. ...

Delegating these would remove ~X cross-context joins, close Y two-writer hazards, and shrink the ambient schema surface from Z tables to the M this service owns.

## Shopping list (grouped by owning domain)

### 1. Needs: read access to `identity`-service (stop touching `institutes`, `student_profile`)

**What's here now**
- `institutes` — foreign-read, 6 sites: `cashfree/…/order_helper.py:88`, … (joins to `dt_payment_order` to get `settlement_account`, `name`)
- `student_profile` — foreign-WRITE, 2 sites: `…/webhook_helper.py:210` sets `last_paid_at` after a payment

**Coupling smells**
- 🔴 CRITICAL `foreign-write` — `…/webhook_helper.py:210` `UPDATE student_profile SET last_paid_at=…`. Two writers on identity's table; an identity schema change silently breaks payments, and identity's invariants aren't enforced here.
- 🔴 CRITICAL `cross-domain-txn` — that write sits inside the same `atomic()` as the `dt_payment_order` update; an identity-side lock/timeout now rolls back a payment.
- 🟠 HIGH `cross-context-join` — `SELECT … FROM dt_payment_order JOIN institutes …` couples the two schemas' query plans; neither domain can be split/sharded independently.

**Why it's out of scope**
This service owns payments data. `institutes` and `student_profile` are identity's records; payments borrowing them by direct SQL means every identity schema change is a payments incident.

**What this service needs (consumer's ask)**

As a consumer, this service needs to read institute settlement details WITHOUT joining `institutes`:
- `get_institute(institute_id) -> { name, settlement_account, status }` — point-lookup, we key on the id already on the order
- `get_institutes(ids[]) -> [...]` — batch, for report rows (we loop today → N+1 waiting to happen)

For the write: we currently stamp `student_profile.last_paid_at`. We need identity to expose:
- `record_payment(student_id, order_id, paid_at)` — identity performs its own write; we emit a `payment.captured` event and stop writing their table.

Access pattern: point-lookup by id (hot path) + batch by ids (reports).
Freshness: eventual (seconds) is fine for settlement metadata; the write is fire-and-forget.

What we do NOT need this party to do:
- Hand us the full institute row — we read 3 of ~40 columns
- Let us keep write access to `student_profile` — read-only + an event is enough

**Impact of delegating**
- Closes 2 two-writer hazards and 1 cross-domain transaction (payment atomicity no longer coupled to identity locks)
- Removes 6 cross-context joins → payments and identity can be split/sharded independently
- Drops payments' read of 37 columns it never uses (smaller blast radius on identity schema changes)

---

### 2. Needs: reference access to `lending`-service (`lender_config`, `lender_rate`)
... (same shape — usually shared-reference, lower severity)

---

## What this service should keep (owned data)
Tables that DO belong to this service and stay local:
- `dt_payment_order`, `dt_transaction`, `settlement_*`, `*_webhook` — created in this service's migrations, sole writer, core domain
- Payment idempotency / dedup tables — financial correctness, core competence

## Ambient surface to shed (least privilege)
The service imports a shared all-tables models module exposing <declared> tables but queries only <queried>. The <declared − queried> unused tables are ambient access with no purpose — narrow the import so the service can only reach what it owns + its declared dependencies.

## Confirm with architecture (inferred ownership)
These ownership calls are **inferred**, not evidenced by a local migration — confirm before acting:
- `institutes` → assumed identity/institute domain
- `lender_config` → assumed lending domain
- ...

## What's out of scope for this audit
- How each owning domain exposes the data (API vs event vs replica) — their call, informed by all consumers
- Physical schema/index/partition/shard design
- Whether the shared database should be physically split at all (architecture decision)

## Next step
Hand this list to architecture + the owning-domain teams. They'll confirm ownership, decide how to expose the data, and come back with the interface to migrate to.
```

---

## Persistent artifacts — write to `.audit/db-scoping/`

```
<service-repo>/
└── .audit/
    └── db-scoping/
        ├── TODO.md                                 # canonical, mergeable, human-editable
        └── data-dependencies-YYYY-MM-DD.md         # per-run snapshot, immutable
```

Both SHOULD be committed to git — the data-boundary plan is a first-class repo artifact. `.audit/` is the shared audit namespace (this skill owns `db-scoping/`; `capability/` and others live beside it).

### Behavior modes
- **Default** — write both files
- **`dry-run`** — print the terminal summary + shopping list, do NOT touch the filesystem
- **`regen-contract`** — re-derive the Consumer Ask sections from the fresh scan, overwriting user edits (default: preserve them)
- **`no-history`** — skip appending to the Audit history table

### TODO.md schema

Human-editable AND machine-parseable. HTML-comment markers anchor reconciliation. Mirror the capability-audit layout, but keyed by **owning domain** and carrying the table inventory.

```markdown
# DB scoping audit — TODO
<!-- db-scoping-audit v1 -->
<!-- service: <service-name> -->
<!-- audit_run: <N> -->
<!-- last_audited_at: <UTC ISO 8601> -->
<!-- owned_data_statement: <one sentence> -->

## Table inventory
<!-- inventory-start -->
| Table | Access | Classification | Owner (inferred) | Evidence |
|---|---|---|---|---|
| dt_payment_order | RW | owned | this-service | migrations/0003:12 |
| institutes | R | foreign-read | identity | order_helper.py:88 |
<!-- inventory-end -->

## Domain: identity
<!-- domain_id: identity -->
<!-- status: open -->
<!-- tables: institutes (R), student_profile (RW) -->
<!-- coupling: CRITICAL (2) · HIGH (1) · MEDIUM (0) · LOW (0) -->

### Migration todos
- [ ] `dbdep-identity-001` 🔴 **CRITICAL** — Stop writing `student_profile.last_paid_at` at `…/webhook_helper.py:210`; emit `payment.captured` and let identity write (two-writer + cross-domain-txn)
- [ ] `dbdep-identity-002` 🟠 HIGH — Replace `dt_payment_order JOIN institutes` with `get_institute(id)` at `…/order_helper.py:88` (cross-context join)
- [x] `dbdep-identity-003` 🟠 HIGH — [resolved 2026-07-20 @alice] Removed direct `institutes` read in reports

### Consumer ask
<!-- contract-start -->
_(preserved verbatim across re-runs unless `regen-contract`)_
- `get_institute(id) -> {name, settlement_account, status}` — point-lookup, eventual freshness OK
- `record_payment(student_id, order_id, paid_at)` — owner performs the write; we emit an event
- Do NOT need: full row, write access to student_profile
<!-- contract-end -->

### Team notes
<!-- notes-start -->
<!-- notes-end -->

---

## Owned tables (out of scope for delegation)
<!-- owned-start -->
- dt_payment_order, dt_transaction, settlement_* — sole writer, created in local migrations
<!-- owned-end -->

## Ambient surface to shed
<!-- ambient-start -->
- Imports shared models exposing <N> tables; queries <M>. Narrow the import to owned + declared deps.
<!-- ambient-end -->

## Confirm ownership (inferred)
<!-- confirm-start -->
- institutes → identity (inferred)
- lender_config → lending (inferred)
<!-- confirm-end -->

## Audit history
| Run | Date | Tables touched | Owned | Foreign | Ambient | Open todos | Δ vs prior |
|---|---|---|---|---|---|---|---|
| 1 | 2026-07-17 | 24 | 15 | 6 | 3 | 5 | initial audit |
```

### Todo item format
```
- [ ] `dbdep-<domain>-<NNN>` <emoji> **<SEVERITY>** — <verb + table + file:line + why>
```
- **`dbdep-<domain>-<NNN>`** — stable id, zero-padded 3 digits, monotonic per domain, never re-used
- **Severity emoji + word** — 🔴 CRITICAL · 🟠 HIGH · 🟡 MEDIUM · 🟢 LOW
- **Verb-first** — Stop / Replace / Delegate / Narrow / Remove — never "look at" or "consider"
- **`file:line`** in backticks + **why in parens** (the specific smell)

### Reconciliation on re-run
Before writing a new TODO.md, PARSE the existing one. Apply per todo:

| Existing state | Fresh scan | Action |
|---|---|---|
| absent | new foreign access found | add `- [ ]` with next `dbdep-<domain>-NNN` |
| `[ ]` open | access still present | keep verbatim (incl. user edits) |
| `[ ]` open | access GONE | flip to `[x]` + note `[auto-resolved YYYY-MM-DD — access no longer present]` |
| `[x]` done | access GONE | keep done |
| `[x]` done | access STILL present | ⚠️ **regression** — flip to `[ ]`, prepend `⚠️ regressed — direct access reappeared` |
| `[x]` done `#wontfix` | either | preserve verbatim (explicit decision) |

- **Team notes** (`<!-- notes-start/end -->`), **Consumer ask** (`<!-- contract-start/end -->` unless `regen-contract`), **Owned** / **Ambient** / **Confirm-ownership** blocks — preserved verbatim; append-only where the fresh scan adds items.
- **Confirmed ownership** — if a user edited an inferred `institutes → identity` line to remove `(inferred)` or add `#confirmed`, honor it as evidenced on future runs; do not revert to `inferred`.
- **Audit history** — append one row per run; never rewrite prior rows.
- **Todo ids** — monotonic per domain; never re-used.

### Machine-readable state block (canonical for tools)

Append a fenced JSON block at the bottom of TODO.md, hidden in `<details>`, bracketed by `<!-- db-scoping-state-start -->` / `<!-- db-scoping-state-end -->`. JSON is canonical for prior-run values; markdown checkboxes are the human view, regenerated from JSON on each write.

```json
{
  "version": 1,
  "service": "<service-name>",
  "audit_run": 1,
  "last_audited_at": "2026-07-17T00:00:00Z",
  "owned_data_statement": "owns payment orders, transactions, settlements, webhooks",
  "inventory": [
    { "table": "dt_payment_order", "access": "RW", "classification": "owned", "owner": "this-service", "inferred": false, "evidence": "migrations/0003:12" },
    { "table": "institutes", "access": "R", "classification": "foreign-read", "owner": "identity", "inferred": true, "evidence": "cashfree/…/order_helper.py:88" },
    { "table": "student_profile", "access": "RW", "classification": "foreign-write", "owner": "identity", "inferred": true, "evidence": "…/webhook_helper.py:210" }
  ],
  "domains": {
    "identity": {
      "status": "open",
      "tables": ["institutes", "student_profile"],
      "coupling_counts": { "critical": 2, "high": 1, "medium": 0, "low": 0 },
      "todos": [
        {
          "id": "dbdep-identity-001",
          "status": "open",
          "severity": "critical",
          "table": "student_profile",
          "access": "W",
          "smell": "foreign-write",
          "file": "…/webhook_helper.py",
          "line": 210,
          "title": "Stop writing student_profile; emit event, let identity write",
          "reason": "two-writer + cross-domain-txn couples payment atomicity to identity",
          "created_run": 1,
          "resolved_at": null,
          "resolved_by": null,
          "history": [ { "run": 1, "status": "open", "date": "2026-07-17", "by": null, "note": "initial finding" } ]
        }
      ],
      "consumer_ask": {
        "read_apis": ["get_institute(id) -> {name, settlement_account, status}"],
        "write_delegations": ["record_payment(student_id, order_id, paid_at)"],
        "access_pattern": "point-lookup + batch by ids",
        "freshness": "eventual",
        "out_of_scope": ["full row", "write access to student_profile"]
      }
    }
  },
  "owned_tables": ["dt_payment_order", "dt_transaction", "settlement_batch"],
  "ambient": { "declared": 521, "queried": 24, "unused": 497, "module": "master_models.py" },
  "confirm_ownership": [ { "table": "institutes", "assumed_owner": "identity" } ],
  "history": [
    { "run": 1, "date": "2026-07-17", "tables_touched": 24, "owned": 15, "foreign": 6, "ambient": 3, "open_todos": 5, "diff": "initial" }
  ]
}
```

**Status vocabulary** (fixed enums):
- Item `status`: `open` · `resolved` · `wontfix` · `retracted` · `regressed`
- Domain `status`: `open` · `in-progress` · `delegated` · `not-applicable`
- Severity: `critical` · `high` · `medium` · `low`
- Classification: `owned` · `foreign-read` · `foreign-write` · `shared-reference` · `ambient`
- Access: `R` · `W` · `RW` · `—` (ambient/unused)

**Reconciliation with JSON canonical**: extract JSON via markers; scan markdown checkboxes for user toggles; apply the 6-case table; update JSON (append to `history[]` per touched todo); regenerate markdown from merged JSON, preserving the `notes`/`contract`/`owned`/`ambient`/`confirm` blocks verbatim. JSON wins for prior-run values; markdown wins for the latest human toggle. If JSON is missing/corrupt, fall back to markdown parsing and print a `⚠️ warning: JSON state block missing/corrupt` line.

### Per-run snapshot: `data-dependencies-YYYY-MM-DD.md`
The full evidence packet from step 6, immutable. Same-date collisions suffix `-run<N>`. Lets a reader see the full evidence as it stood at any past run without `git checkout`.

---

## Terminal summary

```
╭─ DB scoping audit — <service-name> ─────────────────────────────────╮
│  Run #<N> · <UTC> · <actor>                                         │
│  Owns: <one-sentence owned-data statement>                          │
╰──────────────────────────────────────────────────────────────────────╯

Inventory
  <N> tables touched · <owned> owned · <fr> foreign-read · <fw> foreign-write · <sr> shared-ref · <amb> ambient
  Ambient surface: imports <declared> tables, queries <queried> → <unused> unused
  Δ vs Run #<N-1>: <one-line diff>

By owning domain
  🔴 <n>  🟠 <n>  🟡 <n>   <domain>   <tables: list>   <N> open   (R/W)
  ...

Top 5 by dependency risk
  <emoji> <dbdep-id>   <table>   <file:line>   <one-line smell (foreign-write / cross-domain-txn / join)>
  ...

Recent runs (last 3)
  #<N>    today       <touched> tables  <foreign> foreign  <open> open
  ...

Regressions (direct access reappeared)
  ⚠️ <dbdep-id>  <table>  <file:line>
  (omit block if none)

Files written
  .audit/db-scoping/TODO.md                          (updated: +<N> new, −<N> auto-resolved)
  .audit/db-scoping/data-dependencies-<date>.md      (new snapshot)

Next
  1. Review .audit/db-scoping/TODO.md
  2. Fix <top CRITICAL id> (<severity>) — <foreign-write is the priority>
  3. Confirm inferred ownership with architecture, then hand each domain its consumer ask
```

Width-adaptive: <100 cols drop the box header (use `===`); <80 cols drop the emoji-count row; piped/non-TTY drop ANSI colors (box-drawing chars are safe).

The **`dbdep-<domain>-NNN`** id is the join key across terminal, TODO.md, and snapshot — keep run number, timestamp, ids, severity emojis, domain slug, and owned-data statement identical across all three surfaces.

---

## Rules

- ALWAYS resolve ORM models to **physical table names** before classifying — a model class is not a table; two classes can map to one table.
- ALWAYS state the service's **owned-data** in one sentence FIRST — it anchors every classification.
- ALWAYS classify each touched table into exactly one bucket (`owned` / `foreign-read` / `foreign-write` / `shared-reference` / `ambient`).
- ALWAYS rank `foreign-write` and `cross-domain-txn` above `foreign-read` — a second writer and shared transactional fate are the real hazards.
- ALWAYS frame the ask from the CONSUMER's side — the read-model/API/event the service wants, NOT the owner's storage or transport.
- ALWAYS separate what the service NEEDS from what it does NOT need the owner to provide (column scope, write access).
- ALWAYS include impact of delegating (joins removed, two-writer hazards closed, ambient surface shrunk, deploy/shard coupling broken).
- ALWAYS include "owned tables to keep" — the audit is scope discipline, not hollowing the service out.
- ALWAYS mark inferred ownership `inferred` and list it under "Confirm with architecture" — never adjudicate org ownership yourself.
- NEVER prescribe the owner's transport (API/event/replica) or physical schema/index/shard design — that's the owner's/architecture's call.
- NEVER extend the audit across multiple services — SINGLE-service audit.
- If ownership is ambiguous and no `domain_map` was supplied and it's not obvious from migrations/naming, ASK the user before finalizing — a wrong owner makes every recommendation wrong.

### Persistence rules
- ALWAYS write `.audit/db-scoping/TODO.md` + `.audit/db-scoping/data-dependencies-<date>.md` unless `dry-run`.
- ALWAYS reconcile with existing TODO.md — never clobber check-offs, `#wontfix`, confirmed-ownership edits, or team notes.
- NEVER modify content between `<!-- notes-start/end -->`; nor `<!-- contract-start/end -->` unless `regen-contract`.
- NEVER re-use a retracted todo id — monotonic per domain.
- ALWAYS append an Audit history row (unless `no-history`).
- ALWAYS keep the same ids / emojis / domain slugs / run number across terminal, TODO.md, and snapshot.
- If `.audit/db-scoping/` doesn't exist, create it. Suggest the team commit it — this is the data-boundary source of truth.

### Machine-readable state rules
- ALWAYS append the fenced JSON block inside `<details>`, bracketed by `<!-- db-scoping-state-start/end -->`; regenerate it every run.
- ALWAYS use the fixed enums for status / classification / access / severity.
- ALWAYS treat JSON as canonical for prior-run values (severity, table, file, line, reason, created_run, history, inferred/confirmed ownership); markdown wins for the latest human toggle.
- If the JSON block is malformed/missing, fall back to markdown parsing and add a `⚠️ warning` line to the terminal summary.
- NEVER prompt the user to edit JSON — the markdown IS the human interface.
```
