# Rust

- `Vec`: push amortized O(1); `Vec::with_capacity(n)`; `remove(0)`/`insert(0)` O(n); `swap_remove` O(1) when order doesn't matter; `retain` for O(n) bulk removal.
- `VecDeque` for queues; `BinaryHeap` for priority queues / top-k.
- `HashMap/HashSet` O(1) average (SipHash default is DoS-resistant but slower; `ahash`/`FxHash` for trusted keys in hot paths). `BTreeMap` O(log n), ordered.
- `vec.contains(&x)` is O(n); use a set for repeated lookups.
- Iterators are lazy and zero-cost; avoid unnecessary `.collect()` into intermediate `Vec`s between steps.
- `.clone()` inside loops on `String`/`Vec` is an O(size) allocation — borrow (`&str`, `&[T]`) or use `Rc`/`Arc` for shared ownership.
- Build strings with `String::with_capacity` + `push_str`, or `write!`.
- `entry()` API avoids double lookups on maps.
- Async (Tokio): don't block the runtime (use `spawn_blocking` for CPU/blocking work); bound concurrency with `buffer_unordered(n)` or `Semaphore`.
- Benchmark with `criterion`; profile with `cargo flamegraph`.
