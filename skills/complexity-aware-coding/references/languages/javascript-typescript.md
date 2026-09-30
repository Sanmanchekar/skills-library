# JavaScript / TypeScript (Node.js & browser)

- `Array.includes/indexOf/find/filter` are O(n). Inside another loop → O(n²). Use `Set`/`Map` for lookups.
- `shift/unshift/splice` are O(n); use an index pointer or a deque implementation for queues.
- Spreading in reducers is O(n²): `arr.reduce((acc, x) => [...acc, x], [])` or `({...acc, [k]: v})` copies every iteration. Mutate the accumulator or use `push`/`Map`.
- `Array.sort` is O(n log n) and mutates in place; `toSorted()` copies.
- Chained `.map().filter().reduce()` creates intermediate arrays — fine for small n; use a single loop for large n.
- `Object` as a map: use `Map` for frequent add/delete and non-string keys; avoid `delete` on hot objects (deoptimizes).
- `JSON.parse/stringify` on large payloads is O(size) and blocks the event loop; stream (e.g., `stream-json`) for big data.
- `await` inside a `for` loop runs sequentially (sum of latencies). Use `Promise.all` — with a concurrency limit (`p-limit`) for large n to avoid overwhelming DBs/APIs.
- Node's event loop is single-threaded: CPU-heavy work (hashing, big sorts, image processing) blocks every request. Move to `worker_threads` or a queue.
- Use streams for files/HTTP bodies to keep memory O(chunk).
- TypeScript types add no runtime cost, but runtime validators (zod, class-validator) are O(payload) per call — validate at boundaries, not repeatedly.
