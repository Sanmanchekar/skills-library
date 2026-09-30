# Swift

- `Array`: append amortized O(1); `reserveCapacity`; `insert(at: 0)`/`removeFirst` O(n); `contains` O(n).
- Copy-on-write: arrays/dicts/strings copy when mutated while shared — mutating a copy inside a loop can trigger O(n) copies each iteration.
- `Set`/`Dictionary` O(1) average; types must be `Hashable`.
- `String` is not random-access: `count` and index offsets are O(n). Convert to `Array(string)` or use `utf8` views for index-heavy algorithms.
- `lazy` sequences to avoid intermediate arrays in map/filter chains.
- Use value types thoughtfully; large structs passed around copy (unless optimized); use `inout` for in-place mutation.
- UI (SwiftUI): expensive work in `body` re-runs on every state change; use `List`/`LazyVStack` for long lists.
