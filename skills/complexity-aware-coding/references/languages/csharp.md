# C# / .NET

- `List<T>`: indexer O(1), `Add` amortized O(1), `Insert(0)`/`RemoveAt(0)`/`Contains`/`IndexOf` O(n). Set capacity when known.
- `HashSet<T>`/`Dictionary<K,V>`: O(1) average. Use `TryGetValue` instead of `ContainsKey` + indexer (two lookups).
- `SortedDictionary`/`SortedSet`: O(log n). `SortedList` inserts are O(n).
- `Queue<T>`, `Stack<T>`, `PriorityQueue<T,P>` (.NET 6+) for O(1)/O(log n) ops.
- LINQ is deferred: enumerating an `IEnumerable` twice re-executes the whole pipeline (and re-queries the DB for `IQueryable`). Materialize once with `ToList()` when reused.
- `.Count()` on `IEnumerable` is O(n); use `.Count`/`.Length` properties or `.Any()` for existence.
- `list.First(x => ...)` / `Where` inside a loop → O(n²); build a `Dictionary` / `ToLookup` first.
- String building in loops → `StringBuilder`; use `Span<T>`/`ReadOnlySpan<char>` to slice without allocating.
- `async`: avoid `.Result`/`.Wait()` (thread-pool starvation); bound parallelism with `Parallel.ForEachAsync(..., MaxDegreeOfParallelism)` or `SemaphoreSlim`.
- Large arrays (>85KB) go to the LOH; pool buffers with `ArrayPool<T>`.
