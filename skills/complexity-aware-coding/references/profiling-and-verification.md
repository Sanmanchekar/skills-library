# Profiling & Verification — prove the complexity claim

Big O predicts growth; measurement confirms it and exposes constant factors. After an optimization, verify with at least one of: a query-count assertion, a scaling benchmark, or a profile.

## 1. Scaling test (any language)
Run the function at n, 10n, 100n and compare times:
- ~10× per step → O(n) · ~13× → O(n log n) · ~100× → O(n²).
- Watch memory the same way (peak RSS / allocations) for space complexity.

## 2. Query-count guards (most valuable for backends)
| Stack | Tool |
|---|---|
| Django | `assertNumQueries(n)`, `CaptureQueriesContext`, django-silk, nplusone |
| SQLAlchemy | `event.listen(engine, "before_cursor_execute", ...)` counter; `lazy="raise"` |
| Rails | Bullet gem, `strict_loading`, `ActiveSupport::Notifications` query counter |
| Spring/Hibernate | `hibernate.generate_statistics=true`, datasource-proxy / `QueryCountHolder` |
| Laravel | `Model::preventLazyLoading()`, `DB::enableQueryLog()`, Debugbar/Telescope |
| EF Core | `LogTo`, interceptors counting commands |
| Prisma/TypeORM | query event logging (`log: ['query']`) |
| GORM | `Logger` in debug mode |

Write a test asserting the query count stays constant as rows grow (1 row vs 50 rows → same count). That test catches N+1 regressions permanently.

## 3. Profilers
| Language | CPU | Memory |
|---|---|---|
| Python | py-spy (prod-safe, sampling), cProfile + snakeviz, pyinstrument | tracemalloc, memray |
| JS/Node | `node --prof`, `--cpu-prof`, clinic.js (doctor/flame), Chrome DevTools | heap snapshots, clinic heapprofiler |
| Java/Kotlin | JFR + JDK Mission Control, async-profiler | JFR allocation profiling, heap dumps (Eclipse MAT) |
| Go | `pprof` (cpu), `go test -bench -benchmem` | `pprof` heap/allocs |
| C#/.NET | dotnet-trace, dotnet-counters, BenchmarkDotNet | dotnet-gcdump, dotMemory |
| C++ | perf, Valgrind callgrind, Google Benchmark | heaptrack, Valgrind massif |
| Rust | cargo flamegraph, criterion | dhat, heaptrack |
| PHP | Xdebug profiler, Blackfire, SPX | Blackfire memory |
| Ruby | stackprof, rbspy, benchmark-ips | memory_profiler, derailed_benchmarks |
| Frontend | React DevTools Profiler, Chrome Performance panel, Lighthouse | Chrome Memory panel |

## 4. Database verification
Use EXPLAIN plans (see `databases/relational-sql.md`) and slow-query logs (MySQL slow log, `pg_stat_statements`, MongoDB profiler, Redis `SLOWLOG`) to confirm index use and rows examined.

## 5. Static linters that catch complexity smells
- Python: `scripts/complexity_scan.py` (bundled), Ruff `PERF` rules (e.g., PERF401 manual list comprehension), Pylint.
- JS/TS: eslint `no-await-in-loop`, sonarjs rules.
- Java: SpotBugs (performance category), PMD, SonarQube.
- Go: `staticcheck`, `prealloc` linter, `golangci-lint`.
- C#: Roslyn analyzers CA18xx (performance rules).
- Rust: `clippy::perf` lints.
- Ruby: rubocop-performance. PHP: PHPStan/Psalm.
