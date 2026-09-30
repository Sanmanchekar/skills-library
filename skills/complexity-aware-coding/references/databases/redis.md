# Redis / Valkey / KeyDB

Redis executes commands on a single thread: one O(n) command on a big key blocks every client.

| Command | Complexity |
|---|---|
| GET/SET/INCR/HGET/HSET/SADD/SISMEMBER/EXPIRE | O(1) |
| MGET/MSET | O(n keys) |
| HGETALL/SMEMBERS/HKEYS/LRANGE 0 -1 | O(n) — dangerous on big keys |
| LPUSH/RPUSH/LPOP/RPOP | O(1) |
| LINDEX/LSET/LREM | O(n) |
| ZADD/ZREM/ZRANK | O(log n) |
| ZRANGE/ZRANGEBYSCORE | O(log n + m returned) |
| KEYS pattern | O(total keys) — never in production |
| DEL of a big collection | O(elements) — use UNLINK (async) |

- Iterate with `SCAN`/`HSCAN`/`SSCAN`/`ZSCAN` instead of `KEYS`/`HGETALL`/`SMEMBERS` on large keys.
- Avoid big keys (millions of fields/members); shard into multiple keys.
- Pipelining or `MGET` to cut round trips (network RTT usually dominates O(1) commands).
- Always set TTLs on cache keys; configure `maxmemory-policy`.
- Lua scripts and `MULTI/EXEC` block while running — keep them O(small).
- Detect issues: `redis-cli --bigkeys`, `SLOWLOG GET`, `LATENCY DOCTOR`.
- Distributed locks/rate limiting: use O(1) primitives (`SET NX PX`, `INCR` + `EXPIRE`, sorted-set sliding windows trimmed with `ZREMRANGEBYSCORE`).
