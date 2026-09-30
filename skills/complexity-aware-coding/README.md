# Complexity-Aware Coding Skill — Big O Analysis for Claude Code, Cursor, Copilot, Aider

> **Every function you write gets a time and space complexity note — before it ships.** Names the growing `n`, estimates 10x/100x scale, catches hidden O(n²) and N+1 query patterns, bounds user-controlled input sizes, and verifies the claim with a query-count assertion or a scaling benchmark. Ships a Python AST scanner and per-language / per-framework / per-database reference sheets loaded on demand.

**Keywords**: big o analysis, time complexity, space complexity, algorithmic complexity review, n+1 query detector, o(n^2) detector, performance code review ai, scalability review, redos detector, unbounded input, pagination limits, memory leak cache, complexity linter python, ast performance scanner, orm n+1 django sqlalchemy prisma, complexity aware coding claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- complexity-aware-coding
```

## What it does

- **Forces you to name `n`** — "rows per invoice", "webhook events per batch", "users in tenant" — before any complexity is quoted. A bare `O(n)` with no `n` is rejected
- **Estimates expected scale** (today, 10x, 100x) so a per-request path and a one-off script get different treatment
- **Emits a complexity note after every change** — one line, time + space + "scales to", with the reason the dominant term dominates
- **Proportionate, not dogmatic** — when `n < ~100` or the path is cold, the skill says so and picks the readable solution instead of optimizing
- **Catches hidden quadratics** — `x in list` inside a loop, `list.pop(0)`, `s += ...` in a loop, slicing in recursion, `sorted()` re-run per iteration, un-memoized overlapping recursion
- **Catches N+1 at the ORM layer** — the most common real-world O(n)-round-trips bug, with per-framework fixes (Django, SQLAlchemy, ActiveRecord, Hibernate, Eloquent, Prisma, TypeORM, Sequelize, Mongoose, EF Core, GORM)
- **Treats unbounded input as a bug** — page size, batch size, bulk items, payload size, recursion depth, regex input length. No cap means no complexity guarantee
- **Flags algorithmic-complexity attacks** — ReDoS (nested quantifiers on user input), hash flooding, unbounded payloads
- **Bounds every cache** — `lru_cache(maxsize=...)`, Redis TTL + `maxmemory` + eviction policy. An unbounded in-process dict used as a cache is called what it is: a memory leak
- **Requires verification, not vibes** — a query-count assertion, an n/10n/100n scaling check, or a profile before an improvement is claimed
- **Ships a scanner** — `scripts/complexity_scan.py`, a Python AST pass with `--strict` for CI/pre-commit
- **Lazy-loads references** — 10 language sheets, 9 framework sheets, 7 database sheets; the agent reads only the rows matching the code in front of it

## The bundled scanner

```bash
python scripts/complexity_scan.py src/            # report findings
python scripts/complexity_scan.py src/ --strict   # exit 1 on HIGH — CI / pre-commit gate
```

Pure-stdlib AST pass, no dependencies. Detects ORM/HTTP calls inside loops, `in list` membership tests inside loops, `pop(0)` / `insert(0, …)`, string `+=` accumulation, `await` in a loop, unbounded `lru_cache`, and ReDoS-shaped regexes. Heuristic by design — findings are meant to be triaged, and a dismissal needs a stated reason.

## Reference sheets (loaded on demand)

| Area | Files |
|---|---|
| Core | `data-structures.md` (operation + algorithm cost tables, growth intuition, complexity attacks) · `caching-tradeoffs.md` · `profiling-and-verification.md` |
| Languages | Python · JavaScript/TypeScript · Java/Kotlin · Go · C#/.NET · C++ · Rust · PHP · Ruby · Swift |
| Frameworks | Django/DRF · FastAPI/Flask/SQLAlchemy · Rails · Spring/Hibernate · Laravel · Express/NestJS/Prisma/TypeORM/Sequelize/Mongoose · ASP.NET Core/EF Core · React/Next/Vue/Angular |
| Databases | PostgreSQL/MySQL/SQL Server/Oracle/SQLite · MongoDB · Redis/Valkey · DynamoDB · Cassandra/ScyllaDB · Elasticsearch/OpenSearch · Kafka/RabbitMQ/SQS/Celery |

Real code spans several rows at once (Django + MySQL + Redis + a queue) — the skill reads each matching sheet, not the whole set.

## When it triggers

- Any code-writing or refactoring task with loops, collections, lookups, sorting, recursion, or DB queries — **no performance keyword needed**
- "Is this scalable?" · "What's the complexity of this?" · "Why is this endpoint slow?" · "Will this survive 100x?"
- Reviewing a PR that adds a list endpoint, a batch job, a background task, or a nested loop
- Debugging a timeout, a memory climb, or a worker OOM
- Adding a cache, a pagination parameter, a bulk endpoint, or a user-supplied batch size

## Example

**Input** — the agent is asked to flag orders whose customers are inactive:

```python
def flag_inactive(orders):
    out = []
    for o in orders:
        customer = Customer.objects.get(id=o.customer_id)   # query per order
        if customer.status in [c.id for c in inactive_states()]:  # list scan per order
            out.append(o)
    return out
```

**Output** — rewritten plus the mandatory note:

```python
def flag_inactive(orders):
    inactive = {c.id for c in inactive_states()}            # built once, O(1) lookup
    customers = Customer.objects.filter(
        id__in=[o.customer_id for o in orders]
    ).in_bulk()                                             # one query
    return [o for o in orders
            if customers[o.customer_id].status in inactive]
```

```
Complexity: time O(n) (single pass; 2 queries total, not n+1), space O(n) (customer map).
Scales to: ~50k orders per call; beyond that, chunk the id__in batch (DB param limits).
Verified: assertNumQueries(2) holds at 1 row and at 500 rows.
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [perf-analysis](../perf-analysis) — measure-first profiling loop for a system that is *already* slow; this skill is the pre-commit discipline that prevents getting there
- [code-review](../code-review) — general PR review; pair them when the diff adds loops or queries
- [db-migration](../db-migration) — the index that makes the query plan match the complexity you claimed
- [api-design-python-django](../api-design-python-django) · [api-design-python-fastapi](../api-design-python-fastapi) · [api-design-node-express](../api-design-node-express) · [api-design-go-gin](../api-design-go-gin) — where the pagination and batch-size caps actually get enforced
- [refactor](../refactor) — mechanical, behavior-preserving steps to swap a quadratic implementation for a linear one
- [test-generation](../test-generation) — generate the query-count and scaling tests this skill demands as verification
