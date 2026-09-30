# Java / Kotlin (JVM)

## Java
- `ArrayList`: get O(1), add at end amortized O(1), `add(0,x)`/`remove(0)` O(n), `contains` O(n). Pre-size with `new ArrayList<>(n)`.
- `LinkedList`: `get(i)` is O(n) — avoid indexed loops over it; prefer `ArrayDeque` for queues/stacks.
- `HashMap/HashSet`: O(1) average; since Java 8 heavily-colliding buckets become trees (O(log n) worst). Implement `hashCode`/`equals` correctly; pre-size for large maps.
- `TreeMap/TreeSet`: O(log n), ordered, range queries (`subMap`, `ceilingKey`).
- `PriorityQueue`: O(log n) offer/poll; `remove(Object)` is O(n).
- String concatenation in loops → `StringBuilder`.
- Boxing (`List<Integer>`, `Map<Long,...>`) adds allocation and GC pressure; use primitive arrays or specialized collections (Eclipse Collections, fastutil) for large numeric data.
- Streams: `sorted()`, `distinct()`, `collect` materialize; parallel streams only for large CPU-bound work on the common pool, never for blocking I/O.
- `synchronized` / coarse locks serialize throughput; prefer `ConcurrentHashMap`, bounded `ExecutorService` pools, or virtual threads (Java 21+) for I/O concurrency.

## Kotlin
- Collection ops (`map`, `filter`) are eager and allocate intermediate lists; use `asSequence()` for long chains on large data.
- `list + element` / `list += element` on read-only lists creates a new list (O(n)) → O(n²) in loops; use `MutableList.add` or `buildList`.
- `in` on `List` is O(n); use `Set`/`HashSet`.
- Coroutines: bound parallelism (`Dispatchers.IO.limitedParallelism(n)`, `Semaphore`); don't block inside coroutines.
