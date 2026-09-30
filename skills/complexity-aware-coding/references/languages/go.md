# Go

- Slices: `append` amortized O(1); preallocate with `make([]T, 0, n)` when size is known to avoid repeated growth.
- Sub-slicing shares the backing array — a small slice of a huge array keeps the whole array alive (memory leak). `copy` into a new slice if retained.
- Removing from the front/middle is O(n); for order-insensitive removal swap with last.
- `slices.Contains` / linear search is O(n); use `map[K]struct{}` as a set.
- Maps: O(1) average; pre-size with `make(map[K]V, n)`; iteration order is random — sort keys if order matters. Maps never shrink; recreate after deleting most entries.
- Strings are immutable: build with `strings.Builder` (call `Grow` if size known).
- `sort.Slice`/`slices.Sort` O(n log n).
- Goroutines are cheap but not free: bound concurrency with worker pools, `errgroup.SetLimit`, or buffered-channel semaphores. Unbounded goroutine fan-out over n items can exhaust memory and downstream connections.
- Pass large structs by pointer to avoid copies; beware pointer-heavy structures increasing GC work.
- `defer` inside loops accumulates until the function returns (e.g., unclosed files/rows) — wrap the loop body in a function.
- `database/sql`: always `rows.Close()`; configure `SetMaxOpenConns`/`SetMaxIdleConns`.
- GORM: `Preload` / `Joins` to avoid N+1, `CreateInBatches`, `FindInBatches`.
- Profile with `pprof` and benchmark with `testing.B` (`-benchmem`).
