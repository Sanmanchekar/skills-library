---
name: complexity-aware-coding
description: Apply time and space complexity (Big O) analysis whenever writing, reviewing, or refactoring code. Use for ANY code-writing task touching loops, collections, lookups, sorting, recursion, database queries (raw SQL or any ORM), caching, batch jobs, background workers, API pagination, or data processing — even if the user never says "performance", "Big O", or "optimization". Also use when reviewing PRs, debugging slow endpoints or timeouts, or when the user asks about scalability, complexity, or memory usage. Produces a one-line complexity note per change, names the growing n and its expected scale, flags hidden O(n²) and N+1 query patterns, and enforces bounds on user-controlled input sizes. Ships a Python AST scanner (`scripts/complexity_scan.py`) plus per-language, per-framework, and per-database reference sheets loaded on demand.
---

# Complexity-Aware Coding

Goal: code that stays correct and fast as input grows — without over-engineering code where n is small.

## When to use

- Any time you write, review, or refactor code that loops, sorts, searches, recurses, or queries a database — no performance keyword required
- User asks: "is this scalable?", "what's the complexity?", "why is this slow?", "will this handle 100x traffic?"
- Reviewing a PR that adds a list endpoint, a batch job, a background task, or a nested loop
- Debugging a slow endpoint, a timeout, a memory climb, or a worker OOM
- Adding a cache, a pagination parameter, a bulk endpoint, or a user-supplied batch size
- Code touching an ORM inside a loop (the N+1 shape)

Skip the deep analysis when n is provably small (fixed config, < ~100 items, cold one-off script) — say so in one line and prefer the readable solution.

## Method

1. **Identify n.** Name what grows: rows in a table, items in a list, users, webhook events, file size. If nothing grows meaningfully (n < ~100, fixed config), prefer the most readable solution and move on.
2. **Estimate expected scale.** Ask or infer: today's size and 10x/100x growth. A per-request path handling 1M rows is different from a one-off script.
3. **Analyze before finalizing.** For each non-trivial function, determine time and space complexity. Count nested iterations, including hidden ones (see below).
4. **Optimize only where it matters.** Fix anything worse than O(n log n) on a growing n in a hot path. Leave cold paths readable.
5. **Verify.** For Python, run `python scripts/complexity_scan.py <changed files or dir>` and resolve HIGH findings (it's heuristic — dismiss false positives with a reason). For DB code, add a query-count assertion. For claimed big wins, run a quick n / 10n / 100n scaling check. See `references/profiling-and-verification.md` for tools in every stack.
6. **Report briefly.** After the code, add a short complexity note:
   ```
   Complexity: time O(n log n) (sort dominates), space O(n) (lookup dict).
   Scales to: ~1M items in-memory; beyond that, stream/chunk.
   ```
   If you chose a slower but simpler approach deliberately, say why.

## Hidden complexity to always check

- `x in list` / `list.index()` / `list.remove()` inside a loop → O(n²). Use `set`/`dict` for O(1) lookup.
- String concatenation in a loop (`s += ...`) → use `"".join()`.
- `list.pop(0)` / `insert(0, ...)` → O(n); use `collections.deque`.
- Sorting inside a loop; repeated `sorted()` / `max()` on the same data.
- Regex with nested quantifiers on user input (ReDoS) and unbounded user-controlled sizes (page size, batch size, payload).
- Recursion without memoization on overlapping subproblems (exponential); also watch recursion depth.
- Copying/slicing large lists (`arr[1:]`) in loops or recursion → hidden O(n) each time.
- Loading everything into memory when streaming/generators/chunking would keep space O(1) or O(chunk).
- **Database calls inside loops (N+1)** — the most common real-world O(n) → O(n) queries problem. See the framework and database references below.

## Common fixes (pattern → replacement)

| Slow pattern | Better approach | Result |
|---|---|---|
| Nested loop to match two lists | Build dict on one side, iterate the other | O(n·m) → O(n+m) |
| Check duplicates by nested loop | `set` | O(n²) → O(n) |
| Repeated search in sorted data | `bisect` / binary search | O(n) → O(log n) per query |
| Top-k from large list | `heapq.nlargest(k, ...)` | O(n log n) → O(n log k) |
| Sliding window sums recomputed | Running sum / two pointers | O(n·k) → O(n) |
| Repeated subproblems | Memoization / DP table | exponential → polynomial |
| Full load of large dataset | Generator / iterator / chunked reads | space O(n) → O(1)/O(chunk) |

## Bound every input

Complexity is only safe if n is bounded. Enforce maximums on user-controlled sizes: page size, batch size, bulk-request items, upload/payload size, recursion depth, regex input length. Paginate every list endpoint — never return unbounded collections.

## Space complexity rules

- State auxiliary space separately from input size.
- Prefer generators/iterators for pipelines over large data.
- Caches and memo tables must be bounded (`functools.lru_cache(maxsize=...)`, Redis TTLs) in long-running processes (web workers, background workers). Caching trades space for time — see `references/caching-tradeoffs.md` before adding one.

## Rules

- **Always name n and the hot-path assumption** before quoting a complexity — "O(n) where n = order lines per invoice, ~50 today" beats a bare "O(n)".
- **Never claim a complexity you haven't traced.** Include the cost of library calls, ORM lazy loads, and DB queries — a "O(n)" loop that queries per iteration is O(n) *round trips*, and that is the number that matters.
- **Never leave a user-controlled size unbounded.** No cap = no complexity guarantee.
- **Never add an unbounded in-process cache** in a web or worker process — that is a memory leak, not an optimization.
- Don't micro-optimize at the cost of readability when n is small or the code is cold.
- Don't replace a clear O(n log n) with a clever O(n) unless the constant factors and scale justify it.
- Don't assert an improvement without verification — a query-count assertion, a scaling benchmark, or a profile.
- Read only the reference files matching the code in front of you; don't load the whole set.

## References — read only the files relevant to the current code

Always useful: `references/data-structures.md` (operation costs, algorithm costs, ReDoS/unbounded-input risks).
Verification: `references/profiling-and-verification.md` (scaling tests, query-count guards, profilers and linters per language).
Caching decisions: `references/caching-tradeoffs.md`.
Script: `scripts/complexity_scan.py` — AST scanner for Python (N+1 ORM calls, list lookups in loops, `pop(0)`, string `+=`, await/HTTP in loops, unbounded caches, ReDoS regexes). `--strict` exits 1 on HIGH findings for CI/pre-commit.

| If the code involves… | Read |
|---|---|
| Python | `references/languages/python.md` |
| JavaScript / TypeScript / Node | `references/languages/javascript-typescript.md` |
| Java / Kotlin | `references/languages/java-kotlin.md` |
| Go | `references/languages/go.md` |
| C# / .NET | `references/languages/csharp.md` |
| C++ | `references/languages/cpp.md` |
| Rust | `references/languages/rust.md` |
| PHP | `references/languages/php.md` |
| Ruby | `references/languages/ruby.md` |
| Swift | `references/languages/swift.md` |
| Django / DRF | `references/frameworks/django.md` |
| FastAPI / Flask / SQLAlchemy | `references/frameworks/fastapi-sqlalchemy.md` |
| Rails / ActiveRecord | `references/frameworks/rails.md` |
| Spring Boot / JPA / Hibernate | `references/frameworks/spring-hibernate.md` |
| Laravel / Eloquent | `references/frameworks/laravel.md` |
| Express / NestJS / Prisma / TypeORM / Sequelize / Mongoose / GraphQL | `references/frameworks/node-orms.md` |
| ASP.NET Core / EF Core | `references/frameworks/dotnet-efcore.md` |
| React / Next.js / Vue / Angular | `references/frameworks/frontend.md` |
| PostgreSQL / MySQL / MariaDB / SQL Server / Oracle / SQLite / raw SQL | `references/databases/relational-sql.md` |
| MongoDB | `references/databases/mongodb.md` |
| Redis / Valkey | `references/databases/redis.md` |
| DynamoDB | `references/databases/dynamodb.md` |
| Cassandra / ScyllaDB | `references/databases/cassandra-scylla.md` |
| Elasticsearch / OpenSearch | `references/databases/elasticsearch-opensearch.md` |
| Kafka / Redpanda / RabbitMQ / SQS / Celery | `references/databases/messaging-queues.md` |

Code usually spans several rows (e.g., Django + MySQL + Redis + Celery) — read each matching file. For languages/tools not listed, apply the general rules above and the cheatsheet.
