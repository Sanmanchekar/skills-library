# Python

- `list`: append/pop() end O(1) amortized; `insert(0)`, `pop(0)`, `remove`, `index`, `in` are O(n). Use `collections.deque` for queues.
- `dict`/`set`: O(1) average lookup/insert/delete. Convert lists to sets before repeated membership checks.
- Strings are immutable: `s += x` in a loop can be O(n²); use `"".join(parts)`.
- Slicing (`a[1:]`) copies — O(k) time and space. Avoid in recursion; pass indices.
- `sorted()`/`.sort()` are O(n log n) (Timsort, fast on partially sorted data). Use `key=` rather than `cmp_to_key`.
- `heapq.nlargest/nsmallest` for top-k; `bisect` for sorted inserts/search.
- Generators and `itertools` keep memory O(1) for pipelines; list comprehensions materialize everything.
- `functools.lru_cache(maxsize=...)` / `cache` for memoization — bound it in long-running processes.
- `collections.Counter`, `defaultdict` avoid repeated lookups and branching.
- CPU-bound hot loops: prefer NumPy/pandas vectorization (C-speed) over Python loops; avoid `df.iterrows()` / `df.apply` row-wise when a vectorized op exists.
- GIL: threads don't parallelize CPU work; use `multiprocessing`/process pools. Threads/asyncio are fine for I/O.
- asyncio: never call blocking I/O inside `async def`; use `asyncio.gather` with a `Semaphore` to bound concurrency.
- Recursion limit ~1000 by default; convert deep recursion to iteration.
