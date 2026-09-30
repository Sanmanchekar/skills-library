# Caching — the time/space trade-off

Caching spends memory (space) to avoid recomputation or I/O (time). Apply it only when the numbers justify it.

## When a cache is worth it
- Same input requested repeatedly (high hit ratio expected).
- The computation/query is expensive relative to a cache lookup.
- Slightly stale results are acceptable, or invalidation is simple and reliable.
If the key space is effectively unique per request, a cache costs O(n) memory for ~0% hits — don't add it.

## Space rules (every cache must be bounded)
- In-process: `lru_cache(maxsize=N)`, Caffeine/Guava with `maximumSize`, `lru-cache` (Node) with `max`, `MemoryCache` with `SizeLimit`. Unbounded dicts/maps used as caches in web or worker processes are memory leaks.
- Redis/Memcached: TTL on every key + `maxmemory` + eviction policy (`allkeys-lru` / `allkeys-lfu` for pure caches).
- Estimate size: entries × average entry size. State it in the complexity note, e.g. "cache: O(active users) ≈ 50k × 2KB = 100MB".

## Time rules
- Cache lookup should be O(1) (hash keys); avoid caching huge blobs that cost O(size) to serialize/deserialize on every hit.
- Memoization turns overlapping-subproblem recursion from exponential to polynomial; the memo table's size is the new space cost (e.g., O(n·m) for a 2D DP — often reducible to O(m) by keeping only the previous row).
- Precomputation / lookup tables: O(n) build once, O(1) per query — good when queries ≫ updates.

## Correctness guardrails
- Cache stampede on hot keys (many misses at once) → single-flight/locking or early refresh.
- Never cache per-user data under a shared key; include tenant/user in the key.
- Don't cache financial state that must be read-your-writes consistent (balances, payment status) unless invalidation is transactional.
