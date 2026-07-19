---
name: db-scoping
description: Audit a single service for the database TABLES it touches — via raw SQL, ORM models/queries, and shared-model imports — then classify each as owned vs foreign (owned by another domain), and flag direct cross-domain reads/writes that should instead consume the owning domain's API, read-model, or event stream. Produces a data-dependency shopping list plus a mergeable `.audit/db-scoping/TODO.md` and dated terminal summary. Stack-agnostic (Django, SQLAlchemy, Prisma, TypeORM, Sequelize, ActiveRecord, GORM, JPA/Hibernate, Mongoose, raw SQL). NOT for behavior/cross-cutting-services audits (notifications / PDF / audit-log / feature flags / scheduling) — for those, use the `capability-extraction` skill. Out of scope: how the owning service exposes the data, physical schema/index design, sharding mechanics. Triggered when the user says "what TABLES should this service NOT touch", "audit the DB scope", "data ownership audit", "which tables does X actually use", "bounded-context audit", or "db scoping".
---

# db-scoping

## Which audit skill to use

Two audits look similar; they answer different questions. Pick correctly:

| If the question is about... | Use |
|---|---|
| **Data / tables / DB ownership** (which tables this service reads/writes, cross-domain foreign-table access, bounded-context violations at the data layer) | **db-scoping** (this skill) |
| **Behaviors / cross-cutting services** (sending notifications, generating PDFs, uploading files, writing audit logs, feature-flag reads, cron/scheduled jobs) | **capability-extraction** |

If someone says "audit this service" without specifying, ASK — do they mean data ownership or behavioral capabilities.

## The core reframe

A payments service should own payment tables. It should NOT be issuing `SELECT ... FROM users JOIN customers` or `UPDATE provider_config SET ...`. Those tables belong to other domains. Reaching into them directly is the database-level version of implementing a capability you shouldn't own — except worse, because the coupling is invisible until the owning team alters a column and your service breaks at runtime with no compile-time signal.

The goal is NOT to "carve up the database" (that's a platform/architecture decision informed by every service). The goal is to identify **the data dependencies this service should declare on the domains that own that data** — so it stops treating another team's tables as its own local storage and instead consumes them through an owned interface (API, read-model, or event stream).

Owning a table means: you define its migrations, you are the only writer, and its schema changes are your call. Everything else this service touches is borrowed — and borrowed-by-direct-SQL is the coupling this audit surfaces.

## Explicitly out of scope

This skill produces the **consumer's data ask**. It does NOT design the provider:
- How the owning domain exposes the data (REST vs gRPC vs event stream vs read replica) — the owner's call, informed by all consumers
- Physical schema design, index choices, partitioning, or sharding mechanics
- Whether the org should split the monolith DB at all (that's an architecture decision)
- Which team owns which table in the org chart (this skill *infers* ownership and flags it for confirmation — it does not adjudicate)
- Query performance tuning (N+1, missing indexes) unless the fix is "stop reading this foreign table" — use `perf-analysis` for pure performance work

## When to use

- User says: "what tables should this service NOT touch?", "audit the DB scope", "data ownership audit", "which tables does X actually use?", "bounded-context audit", "what data should this service own?"
- New service scoping — data dependencies to declare from day one vs. what to own
- Monolith-to-services planning — establishing each service's data boundary before a split
- Post-incident: "the outage happened because [payments] read a column [profile] renamed" — should we depend on that table directly?
- A service imports a giant shared/generated models module (an "all-tables" file) — establish which of those hundreds of tables it actually uses, and of those, which are foreign

## The argument

- **Required**: `service` — the single service (repo path or directory) to audit
- **Optional**: `domain_map` — a mapping of table-name patterns → owning domain (e.g., `user_* → identity`, `provider_* → lending`). If not supplied, the skill infers ownership from migration evidence + naming and marks every inference `inferred`.
- **Optional**: `tables` — restrict the audit to specific tables (default: every table the service touches)
- **Optional**: `mode` — `dry-run` / `regen-contract` / `no-history` (see `references/reconciliation.md`)

## Table classifications

Every touched table lands in exactly one bucket:

| Classification | Definition | Verdict |
|---|---|---|
| `owned` | This service creates it in its own migrations, is the sole writer, name sits in its domain | **KEEP** — this is the service's job |
| `foreign-write` | Service issues INSERT/UPDATE/DELETE on a table it did not create | 🔴 **worst** — two-writer problem; delegate the write to the owner |
| `foreign-read` | Service SELECTs/JOINs a table it did not create and does not write | 🟠 delegate to the owner's read-model/API |
| `shared-reference` | Read-only central lookup/config (currencies, PG config, lender master) owned centrally | 🟡 acceptable via a reference service / cached replica; flag, low priority |
| `ambient` | Reachable through an imported all-tables models module but never actually queried | 🟢 dead access surface — remove from imports (least privilege) |

## Steps

### 1. Establish this service's owned-data statement (one sentence)
Read the top of `README.md`, top-level directories, the migrations folder, and the main models module. Write ONE sentence: **"This service owns: X data; its job is: Y."**

If it isn't obvious and the user hasn't told you, ASK before continuing — a wrong owned-data statement makes every classification wrong.

### 2. Build the table inventory (this service ONLY)
Sweep the service using **`references/detection-tables.md`**. For every table, record:

`table | access (R / W / RW) | how detected (raw-sql | orm-model | orm-query | import-only) | evidence path:line`

Resolve ORM models to physical table names before de-duping. Do NOT compare across services.

### 3. Classify + find ownership evidence
For each inventoried table:
- Grep the service's migrations for a CREATE/ALTER → sets/strengthens `owned`
- Apply the write-asymmetry + domain-name rules → assign one classification bucket
- Record whether ownership is `inferred` or `evidenced` (local migration found)

See `references/detection-tables.md` → "Ownership inference" for the inference rules.

### 4. For each foreign table (or group), produce the case
Five fields:

| Field | Content |
|---|---|
| **What's here now** | access pattern + evidence file:line + inferred owning domain |
| **Coupling smells** | foreign-write, cross-domain-txn, cross-context-join, ambient-schema-import, foreign-column-read, foreign-fk, etc. |
| **Why it's out of scope** | one sentence tied back to step 1's owned-data statement |
| **What this service needs (consumer's ask)** | see `references/consumer-ask.md` |
| **Impact of delegating** | joins removed, two-writer hazards closed, ambient surface shrunk, deploy/shard coupling broken |

### 5. Rank
Order by **risk of the direct dependency**, roughly = (write? × cross-domain-txn? × schema-fragility × frequency). `foreign-write` and `cross-domain-txn` always rank above `foreign-read`. Highest-risk first.

### 6. Produce the shopping list
Use **`references/shopping-list-template.md`** as the output body. Group foreign tables by **owning domain**. This is what the service team hands to architecture + the owning-domain teams.

### 7. Persist + summarize
- **Write** `.audit/db-scoping/TODO.md` (mergeable — schema in `references/todo-schema.md`) and `.audit/db-scoping/data-dependencies-YYYY-MM-DD.md` (the shopping list from Step 6, immutable snapshot)
- **Print** a dated terminal summary — format in `references/terminal-summary.md`
- On re-runs, MERGE with the existing TODO.md — never clobber. Follow the 6-case table in `references/reconciliation.md`
- Skip file writes if the user requested `dry-run` mode

## Rules

- ALWAYS resolve ORM models to **physical table names** before classifying — a model class is not a table; two classes can map to one table
- ALWAYS state the service's **owned-data** in one sentence FIRST — it anchors every classification
- ALWAYS classify each touched table into exactly one bucket (`owned` / `foreign-read` / `foreign-write` / `shared-reference` / `ambient`)
- ALWAYS rank `foreign-write` and `cross-domain-txn` above `foreign-read` — a second writer and shared transactional fate are the real hazards
- ALWAYS frame the ask from the CONSUMER's side — the read-model/API/event the service wants, NOT the owner's storage or transport
- ALWAYS separate what the service NEEDS from what it does NOT need the owner to provide (column scope, write access)
- ALWAYS include impact of delegating (joins removed, two-writer hazards closed, ambient surface shrunk, deploy/shard coupling broken)
- ALWAYS include "owned tables to keep" — the audit is scope discipline, not hollowing the service out
- ALWAYS mark inferred ownership `inferred` and list it under "Confirm with architecture" — never adjudicate org ownership yourself
- NEVER prescribe the owner's transport (API/event/replica) or physical schema/index/shard design — that's the owner's/architecture's call
- NEVER extend the audit across multiple services — SINGLE-service audit
- NEVER audit behaviors/cross-cutting-services here — that's `capability-extraction`'s job
- If ownership is ambiguous and no `domain_map` was supplied, ASK the user before finalizing

### Persistence rules
- ALWAYS write `.audit/db-scoping/TODO.md` + `.audit/db-scoping/data-dependencies-<date>.md` unless `dry-run`
- ALWAYS reconcile with existing TODO.md — never clobber check-offs, `#wontfix`, confirmed-ownership edits, or team notes
- NEVER modify content between `<!-- notes-start/end -->`; nor `<!-- contract-start/end -->` unless `regen-contract`
- NEVER re-use a retracted todo id — monotonic per domain
- ALWAYS append an Audit history row (unless `no-history`)
- ALWAYS keep the same ids / emojis / domain slugs / run number across terminal, TODO.md, and snapshot
- If `.audit/db-scoping/` doesn't exist, create it. Suggest the team commit it — this is the data-boundary source of truth

### Machine-readable state rules
- ALWAYS append the fenced JSON block inside `<details>`, bracketed by `<!-- db-scoping-state-start/end -->`; regenerate every run
- ALWAYS use the fixed enums (item/domain status, severity, classification, access)
- JSON is canonical for prior-run values; markdown wins for the latest human toggle
- If the JSON block is malformed/missing, fall back to markdown parsing and add a `⚠️ warning` line to the terminal summary
- NEVER prompt the user to edit JSON — the markdown IS the human interface

## References (load on demand)

- `references/detection-tables.md` — raw-SQL, ORM, migration, and shared-model detection patterns; ownership inference rules (Steps 2–3)
- `references/consumer-ask.md` — template for the consumer's data-ask statement (Step 4, field 4)
- `references/shopping-list-template.md` — full evidence-packet body (Step 6)
- `references/todo-schema.md` — TODO.md structure + JSON state block schema (Step 7)
- `references/reconciliation.md` — 6-case merge table + preservation rules for re-runs (Step 7)
- `references/terminal-summary.md` — dated summary format + width-adaptive rules (Step 7)
