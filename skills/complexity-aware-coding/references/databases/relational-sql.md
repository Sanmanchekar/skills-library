# Relational Databases: PostgreSQL, MySQL/MariaDB, SQL Server, Oracle, SQLite

## Core cost model
- B-tree index lookup: O(log n). Full table scan: O(n). A query's real cost = rows examined, not rows returned.
- Always verify with plans: PostgreSQL `EXPLAIN (ANALYZE, BUFFERS)`, MySQL `EXPLAIN ANALYZE` (8.0.18+), SQL Server actual execution plan / `SET STATISTICS IO ON`, Oracle `EXPLAIN PLAN` + `DBMS_XPLAN`, SQLite `EXPLAIN QUERY PLAN`.

## Indexing
- Index columns used in `WHERE`, `JOIN`, `ORDER BY`. Composite indexes follow the leftmost-prefix rule: put equality columns first, then range/sort columns.
- Covering indexes avoid table lookups: PostgreSQL/SQL Server `INCLUDE (...)`; in MySQL InnoDB, secondary indexes already contain the primary key.
- Index killers: functions on the column (`WHERE DATE(created_at) = ...` → use a range, or an expression/functional index), leading wildcards (`LIKE '%x'`), implicit type casts (string column compared to number), `OR` across different columns (consider `UNION`).
- Every index slows writes and uses space — don't index everything.
- PostgreSQL extras: partial indexes (`WHERE status = 'pending'`), GIN for `jsonb`/arrays/full-text, BRIN for huge append-only time-series.
- MySQL InnoDB clusters rows by primary key: random UUIDv4 PKs cause page splits and bloated indexes — prefer auto-increment or time-ordered IDs (UUIDv7/ULID).

## Query patterns
- `OFFSET n` scans and discards n rows (O(n)) → keyset pagination: `WHERE (created_at, id) > (:c, :i) ORDER BY created_at, id LIMIT 50`.
- `SELECT *` fetches unneeded columns and prevents covering-index plans.
- Correlated subqueries can execute per row — rewrite as JOINs or window functions.
- `NOT IN (subquery)` with NULLs gives wrong results and poor plans — use `NOT EXISTS`.
- Exact `COUNT(*)` on large tables is expensive (especially PostgreSQL MVCC); use estimates or cached counters where acceptable.
- Join algorithms: nested loop (good when inner side is indexed and small), hash join O(n+m), merge join (sorted inputs). Missing indexes on join keys → nested-loop scans O(n·m).
- `DISTINCT`/`GROUP BY`/`ORDER BY` on unindexed columns cause sorts O(n log n) and possible disk spills.

## Writes & locking
- Batch inserts (multi-row `INSERT`, `COPY` in PostgreSQL, `LOAD DATA` in MySQL, `SqlBulkCopy` in SQL Server).
- Large `UPDATE`/`DELETE`: chunk by primary key ranges to avoid long locks, replication lag, and huge undo/WAL.
- Keep transactions short; long transactions block vacuum (PostgreSQL) and hold locks.
- Schema changes on big tables: use online tools (`pt-online-schema-change`, `gh-ost`, PostgreSQL `CREATE INDEX CONCURRENTLY`).

## Scale
- Connection pools sized to DB capacity (PgBouncer, RDS Proxy, HikariCP).
- Read replicas for read-heavy workloads (mind replication lag).
- Partition very large tables (by time or tenant) so queries prune partitions.
