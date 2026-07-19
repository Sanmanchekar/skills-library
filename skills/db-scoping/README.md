# DB Scoping Skill — Audit One Service for the Tables It Should NOT Touch

> **Which database tables does this service actually own, and which is it borrowing by direct SQL?** Audits a single service for every table it touches — via raw SQL, ORM models/queries, and shared-model imports — then classifies each as **owned** vs. **foreign** (owned by another domain) and flags direct cross-domain reads/writes it should instead consume through the owning domain's API, read-model, or event stream. Produces a **data-dependency shopping list** grouped by owning domain, a full **table inventory**, a **mergeable `.audit/db-scoping/TODO.md`**, and a **dated terminal summary** so boundary-cleanup progress is trackable across re-runs. Stack-agnostic. **Out of scope**: how the owner exposes the data, physical schema/index/shard design.

**Keywords**: database ownership audit, bounded context audit, data boundary audit, which tables does a service use, cross-domain table access, foreign key coupling audit, shared database anti-pattern, monolith to microservices data split, single service db scope, table inventory generator, cross-context join detector, two-writer problem, ambient schema access, read-model dependency, event-carried state transfer, strangler pattern database, db scoping claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- db-scoping
```

## What it does

- **Service-centric, table-level** — you point at ONE service; the skill tells you which tables don't belong to it
- Establishes the service's **owned-data statement** in one sentence first — every classification anchors back to it
- Builds a **full table inventory** — resolves raw SQL, ORM models (Django, SQLAlchemy, Prisma, TypeORM, Sequelize, ActiveRecord, GORM, JPA/Hibernate, Mongoose, Ecto), and shared-model imports down to **physical table names** with read/write access
- **Classifies every table** into one bucket: `owned` · `foreign-read` · `foreign-write` · `shared-reference` · `ambient`
- **Infers ownership** from migration evidence (who runs `CREATE TABLE`) + write-asymmetry + naming — always tagged `inferred` and listed under "Confirm with architecture," never adjudicated
- For each foreign table, produces a **5-field case**: what's here, coupling smells, why it's out of scope, consumer's data ask, impact of delegating
- **Consumer's data ask** = the read-model / API / event the service wants from the owning domain — not the owner's storage design
- **Ranks by dependency risk** — `foreign-write` and `cross-domain-txn` always above `foreign-read` (a second writer and shared transactional fate are the real hazards)
- **Detects the shared all-tables models anti-pattern** — quantifies "imports N tables, queries M, N−M unused ambient surface" and tells you to narrow the import (least privilege)
- **Writes two files** into the audited repo: a mergeable `TODO.md` and a per-run immutable `data-dependencies-YYYY-MM-DD.md` snapshot
- **Prints a dated terminal summary** — classification breakdown, top-N by risk, diff vs prior run, files-written pointer, next actions
- **Reconciles across re-runs** — preserves check-offs, team notes, `#wontfix` tags, confirmed-ownership edits; detects regressions (direct access reappeared); auto-resolves items whose access is gone
- Ends with **"owned tables to keep"** so the audit is scope discipline, not hollowing-out
- Explicitly **out of scope**: the owner's transport (API vs event vs replica), physical schema/index/shard design, whether the DB should be physically split

## Coupling smells it flags

| Smell | Meaning | Severity |
|---|---|---|
| `foreign-write` | Service writes a table another domain owns — two-writer problem | 🔴 CRITICAL |
| `cross-domain-txn` | A foreign write shares a DB transaction with an owned write — shared transactional fate | 🔴 CRITICAL |
| `cross-context-join` | A single SQL JOIN spans an owned and a foreign table — couples both schemas | 🟠 HIGH |
| `ambient-schema-import` | Service imports an all-tables shared models module — no bounded context | 🟠 HIGH |
| `foreign-column-read` | SELECTs specific columns of a foreign table — silent break on owner schema change | 🟠 HIGH |
| `foreign-fk` | FK / relationship constraint into a foreign table — blocks independent deploy/shard | 🟡 MEDIUM |
| `shared-reference-read` | Direct read of a central config/lookup table | 🟡 MEDIUM |
| `ambient-unused` | Table reachable via import but never queried — dead access surface | 🟢 LOW |

## Persistent output (writes to the audited repo)

Two files under `.audit/db-scoping/`:

```
<service-repo>/
└── .audit/
    └── db-scoping/
        ├── TODO.md                              # canonical, mergeable, human-editable
        └── data-dependencies-YYYY-MM-DD.md      # per-run snapshot, immutable
```

Same `.audit/` namespace convention as [capability-extraction](../capability-extraction) — tool-generated audit artifacts, namespaced so multiple audit skills stay tidy. **Commit it.** The TODO is the data-boundary source of truth — teammates check items off in PRs, reviewers see the diff, `git blame` shows who closed each cross-domain dependency.

### TODO.md structure

Human-editable checkboxes; machine-parseable via HTML-comment markers; keyed by **owning domain** and carrying the table inventory:

```markdown
# DB scoping audit — TODO
<!-- db-scoping-audit v1 -->
<!-- service: payments-service -->
<!-- audit_run: 1 -->
<!-- owned_data_statement: owns payment orders, transactions, settlements, webhooks -->

## Table inventory
<!-- inventory-start -->
| Table | Access | Classification | Owner (inferred) | Evidence |
|---|---|---|---|---|
| payment_orders | RW | owned | this-service | migrations/0003:12 |
| customers | R | foreign-read | identity | order_helper.py:88 |
| user_profile | RW | foreign-write | identity | webhook_helper.py:210 |
<!-- inventory-end -->

## Domain: identity
### Migration todos
- [ ] `dbdep-identity-001` 🔴 **CRITICAL** — Stop writing `user_profile.last_paid_at` at `webhook_helper.py:210`; emit `payment.captured` and let identity write (two-writer + cross-domain-txn)
- [ ] `dbdep-identity-002` 🟠 HIGH — Replace `payment_orders JOIN customers` with `get_institute(id)` at `order_helper.py:88` (cross-context join)
- [x] `dbdep-identity-003` 🟠 HIGH — [resolved 2026-07-20 @alice] Removed direct `customers` read in reports

### Consumer ask
<!-- contract-start -->
- get_institute(id) -> {name, settlement_account, status} — point-lookup, eventual freshness OK
- record_payment(student_id, order_id, paid_at) — owner performs the write; we emit an event
<!-- contract-end -->
```

### Reconciliation across re-runs — safe to re-run any time

| Prior state | New scan | Action |
|---|---|---|
| absent | new foreign access | new `[ ]` item added |
| `[ ]` open | still present | kept verbatim |
| `[ ]` open | access gone | auto-flipped to `[x]` with resolution date |
| `[x]` done | access gone | kept as done |
| `[x]` done | access returned | ⚠️ regression flagged |
| user-tagged `#wontfix` | either | preserved verbatim |

Team notes, consumer ask, owned-tables, ambient-surface, and confirm-ownership blocks are preserved verbatim. Pass `regen-contract` to force re-derivation of the consumer ask; `dry-run` to preview without writing.

### Machine-readable state (LLM- and tool-friendly)

The bottom of `TODO.md` includes a **fenced JSON state block** hidden inside `<details>` — markdown checkboxes are the human view; JSON is the deterministic source of truth for automation. Fixed enums so LLMs never guess:

- Item status: `open` / `resolved` / `wontfix` / `retracted` / `regressed`
- Domain status: `open` / `in-progress` / `delegated` / `not-applicable`
- Classification: `owned` / `foreign-read` / `foreign-write` / `shared-reference` / `ambient`
- Severity: `critical` / `high` / `medium` / `low`

**Precedence on re-run**: JSON wins for prior-run values (severity, table, file/line, history, inferred/confirmed ownership); markdown wins for the latest human toggle.

## Terminal summary (dated, on every run)

```
╭─ DB scoping audit — payments-service ─────────────────────╮
│  Run #1 · 2026-07-17 UTC · Sanmanchekar                             │
│  Owns: payment orders, transactions, settlements, webhooks          │
╰──────────────────────────────────────────────────────────────────────╯

Inventory
  24 tables touched · 15 owned · 6 foreign-read · 2 foreign-write · 1 shared-ref
  Ambient surface: imports 521 tables (all_models.py), queries 24 → 497 unused
  Δ vs Run #0: initial audit

By owning domain
  🔴 2  🟠 1        identity   customers(R), user_profile(RW)   3 open
  🟡 1             lending    provider_config(R)                     1 open

Top 5 by dependency risk
  🔴 dbdep-identity-001   user_profile   webhook_helper.py:210   foreign-write + cross-domain-txn
  🟠 dbdep-identity-002   customers        order_helper.py:88      cross-context-join
  ...

Files written
  .audit/db-scoping/TODO.md                          (new: 5 todos, run #1)
  .audit/db-scoping/data-dependencies-2026-07-17.md  (new snapshot)

Next
  1. Review .audit/db-scoping/TODO.md
  2. Fix dbdep-identity-001 (CRITICAL) — stop the foreign write first
  3. Confirm inferred ownership with architecture, then hand each domain its consumer ask
```

**Terminal and TODO.md share the same todo IDs** (`dbdep-identity-001`), severity emojis, domain slugs, and run number — copy any ID, ⌘F in the TODO.md, jump to full context.

## Why this framing

Owning a table means you define its migrations, you're the sole writer, and schema changes are your call. Everything a service reaches into by direct SQL is *borrowed* — and borrowed-by-direct-query is invisible coupling that breaks at runtime when the owning team renames a column, with no compile-time signal. A `SELECT ... FROM users JOIN customers` in a payments service, or an `UPDATE provider_config`, is the database-level version of implementing a capability you shouldn't own — except worse, because it fails silently.

The skill produces the **consumer's data ask** — "here's the read-model / event / command we need from the domain that owns this table." How that domain exposes it, and whether the physical DB ever gets split, is a downstream architecture conversation.

## When it triggers

- "What tables should this service NOT touch?"
- "Audit the DB scope of payments-service"
- "Data ownership audit"
- "Which tables does this service actually use?"
- "Bounded-context audit"
- "What data should this service own?"
- Monolith-to-services planning — establishing each service's data boundary before a split
- A service imports a giant shared/generated models module and you need to know what it actually uses
- Post-incident when the root cause was a foreign schema change breaking a direct table read

## Example shopping list (excerpt)

```
Service: payments-service
Owns: payment orders, PG transactions, settlements, webhooks.

Table inventory: 24 touched — 15 owned, 6 foreign-read, 2 foreign-write, 1 shared-ref
Ambient: imports all_models.py (521 tables), queries 24 → 497 unused

1. Needs: read access to identity-service (stop touching customers, user_profile)
   - CRITICAL: webhook_helper.py:210 UPDATEs user_profile inside the same
     atomic() as the payment write — two writers + shared transactional fate
   - HIGH: payment_orders JOIN customers couples both schemas
   - Consumer's ask: get_institute(id) -> {name, settlement_account, status}
                    + record_payment(student_id, order_id, paid_at) (owner writes)
   - Impact: closes 2 two-writer hazards, removes 6 cross-context joins

2. Needs: reference access to lending-service (provider_config)
   ...

Owned tables to keep:
   - payment_orders, transactions, settlements_*, *_webhook, idempotency tables

Ambient surface to shed:
   - Narrow master_models import from 521 tables to owned + declared deps

Confirm ownership (inferred):
   - customers → identity · provider_config → lending
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [capability-extraction](../capability-extraction) — the behavior-level sibling: capabilities this service should delegate, not tables
- [db-migration](../db-migration) — safe schema-change review for the tables this service actually owns
- [adr](../adr) — the "we're declaring a data dependency on domain X" architecture decision the shopping list feeds into
- [refactor](../refactor) — mechanical steps to swap a direct table read for a read-model client once the owner exposes it
- [perf-analysis](../perf-analysis) — for pure query performance (N+1, indexes) when the fix is *not* "stop reading this table"
