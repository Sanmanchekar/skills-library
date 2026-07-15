# DB Migration Skill — Safe Schema Change Review for Claude Code, Cursor, Copilot

> **Ship database migrations without locking prod.** Backward-compat analysis, lock-level review, online-safe patterns (add → backfill → constrain), and a written rollback plan — for Postgres, MySQL, and Prisma.

**Keywords**: database migration review, safe schema change, postgres migration, alembic migration, prisma migration, zero downtime migration, concurrent index creation, lock analysis, add column not null, rename column safely, db migration claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- db-migration
```

## What it does

- Enforces **"safe while old app code is still running"** — deploys aren't atomic
- Full **lock analysis table** (ACCESS EXCLUSIVE, SHARE, SHARE UPDATE EXCLUSIVE) per operation
- Prescribes **online-safe patterns** — add column → backfill → constrain; rename via dual-write
- Requires `CREATE INDEX CONCURRENTLY` on tables > 1M rows
- Requires `statement_timeout` / `lock_timeout` on every migration
- Requires a **written rollback plan** — "irreversible" is a valid answer, but must be stated
- Splits schema DDL from data backfill (never combined)

## When it triggers

- Files in `migrations/`, `alembic/versions/`, `db/migrate/`, `prisma/migrations/`
- Filenames matching `V<n>__*.sql`, `*_migration.py`
- "Review this migration" / "write a migration for X" / "is this migration safe"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — application-code PR review
- [rca](../rca) — post-incident when a migration went wrong
- [runbook](../runbook) — migration runbook + rollback procedure
