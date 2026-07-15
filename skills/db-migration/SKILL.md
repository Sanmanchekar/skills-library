---
name: db-migration
description: Review or design a database schema migration (Postgres, MySQL, MongoDB) for safety at scale. Enforces backward compatibility (writer/reader deploy order), lock analysis (ACCESS EXCLUSIVE vs SHARE), online-safe patterns (add-column-then-backfill-then-constrain), and a written rollback plan. Triggered when the user asks to review a migration, write a migration for X, or has changes under `migrations/`, `alembic/versions/`, `db/migrate/`, `flyway/`, `liquibase/`, or files matching `V<n>__*.sql`.
---

# db-migration

## When to use

- File in `migrations/`, `alembic/versions/`, `db/migrate/`, `prisma/migrations/`, `flyway/`, `liquibase/`
- Filename matches `V<n>__*.sql`, `*_migration.py`, `*.changeset.xml`
- User asks: "review this migration", "write a migration for X", "is this migration safe"

## The one law

**Every migration must be safe to run WHILE OLD APP CODE IS STILL RUNNING.** Deploys are not atomic. Old and new code coexist for minutes to hours. A migration that requires new code to be live is a broken migration.

## Lock analysis (Postgres — most dangerous ops)

| Operation | Lock | Blocks | Safe on hot table? |
|---|---|---|---|
| `ALTER TABLE ADD COLUMN` (no default, nullable) | ACCESS EXCLUSIVE, brief | briefly blocks reads+writes | Yes (fast) |
| `ALTER TABLE ADD COLUMN ... DEFAULT <val>` (PG ≥11 non-volatile) | ACCESS EXCLUSIVE, brief | briefly blocks | Yes |
| `ALTER TABLE ADD COLUMN ... DEFAULT <volatile>` | ACCESS EXCLUSIVE + full rewrite | blocks reads+writes for the rewrite | NO — split |
| `ALTER TABLE SET NOT NULL` | ACCESS EXCLUSIVE + full scan | blocks | NO — validate constraint first |
| `ALTER TABLE ADD CONSTRAINT ... NOT VALID` | ACCESS EXCLUSIVE, brief | brief | Yes |
| `VALIDATE CONSTRAINT` | SHARE UPDATE EXCLUSIVE | reads/writes OK | Yes |
| `CREATE INDEX` | SHARE | blocks writes | NO on hot table |
| `CREATE INDEX CONCURRENTLY` | SHARE UPDATE EXCLUSIVE | reads/writes OK | Yes (slower, no txn) |
| `DROP INDEX` | ACCESS EXCLUSIVE | blocks | Use `DROP INDEX CONCURRENTLY` |
| `ALTER TABLE ALTER COLUMN TYPE` (compatible) | ACCESS EXCLUSIVE, brief | brief | Sometimes |
| `ALTER TABLE ALTER COLUMN TYPE` (rewrite) | ACCESS EXCLUSIVE + full rewrite | blocks | NO — split |

## Online-safe patterns (multi-PR sequence)

### Add a NOT NULL column with default
NOT: `ALTER TABLE t ADD COLUMN c INT NOT NULL DEFAULT 0` on a 100M-row table.

**Do this instead (3 PRs, 3 deploys):**
1. PR A: add nullable column, no default. Application writes both old and new column (dual-write).
2. PR B: backfill in batches. Then add `NOT VALID` NOT NULL check constraint. `VALIDATE` it.
3. PR C: drop the check constraint, add real `NOT NULL` (fast now — PG uses the validated constraint).

### Rename a column
NOT: `ALTER TABLE t RENAME COLUMN old TO new` — instant deploy skew death.

**Do this instead (5 PRs):**
1. Add `new` column
2. Dual-write both `old` and `new`
3. Backfill `new` from `old`
4. Switch reads to `new`
5. Stop writing `old`, drop `old`

### Drop a column
**Never drop synchronously with removing app references.** The old code still reads it.
1. Stop reading + writing the column in app code (ship + wait for full deploy)
2. Drop the column in a later migration

### Rename a table
Same pattern as column rename — new table + dual-write + backfill + switch reads + drop old.

### Add an index
Always `CREATE INDEX CONCURRENTLY`. Cannot run inside a transaction. Requires a separate migration file.

### Add a foreign key
1. Add FK as `NOT VALID`: `ALTER TABLE child ADD CONSTRAINT fk_x FOREIGN KEY (parent_id) REFERENCES parent(id) NOT VALID` (brief lock)
2. `ALTER TABLE child VALIDATE CONSTRAINT fk_x` (SHARE UPDATE EXCLUSIVE, no blocking)

## Statement timeout

Every migration runner must set `SET LOCAL statement_timeout = '5s'` (or `lock_timeout`) to prevent a stuck migration from taking down the DB.

## Review checklist (produce as findings)

| Check | Severity if violated |
|---|---|
| Backward-compatible with the previous release | CRITICAL |
| No `CREATE INDEX` without `CONCURRENTLY` on tables > 1M rows | CRITICAL |
| No `ALTER COLUMN TYPE` with rewrite on tables > 1M rows | CRITICAL |
| No `ADD COLUMN NOT NULL DEFAULT <volatile>` | CRITICAL |
| No `ALTER SET NOT NULL` without prior `ADD CHECK NOT VALID` + `VALIDATE` | HIGH |
| No `DROP COLUMN` while app still references it | CRITICAL |
| Rollback plan documented in migration file header | HIGH |
| `statement_timeout` / `lock_timeout` set | HIGH |
| Data migrations batched (< 5k rows/batch) with commit between batches | HIGH |
| No FK added without `NOT VALID` two-step | MEDIUM |

## Output format (design mode)

```markdown
# Migration — <name>

## Intent
One sentence: what changes, and why.

## Deploy order (multi-PR)
1. PR A (this one) — <what>
2. PR B — <what>, deployed after PR A rolled out to 100%
3. PR C — <cleanup>, deployed after PR B rolled out to 100%

## Lock analysis
- Statement 1: `ALTER TABLE ... ADD COLUMN` — ACCESS EXCLUSIVE, brief
- Statement 2: `CREATE INDEX CONCURRENTLY` — SHARE UPDATE EXCLUSIVE, ~15 min on 40M rows

## Rollback plan
- Reversible: yes / no (with reason)
- Steps: `DROP COLUMN x` (safe because unused after PR C is reverted)
- Data restore: not applicable / from backup <snapshot id>

## Estimated duration
- 40M row backfill in batches of 5k: ~20 min
- Blocking DDL: <100ms total
```

## Rules

- NEVER combine schema DDL and data backfill in the same migration
- NEVER use `NOT NULL` synchronously on a large existing column
- NEVER drop a column that the currently-deployed app version still references
- NEVER `CREATE INDEX` (without CONCURRENTLY) on a hot table
- ALWAYS document deploy order for multi-PR sequences
- ALWAYS include a rollback plan — "irreversible" is an answer, but must be stated
- ALWAYS set `statement_timeout` / `lock_timeout`
