# PHP

- Arrays are ordered hash maps: key lookup (`isset($a[$k])`, `array_key_exists`) is O(1), but `in_array` and `array_search` are O(n). For repeated membership checks, `array_flip` once then use `isset`.
- `array_merge` inside a loop → O(n²); append with `$arr[] = $x` or merge once at the end (`array_merge(...$chunks)`).
- `array_shift`/`array_unshift` are O(n) (reindexing); use `SplQueue` or an index pointer.
- `count()` is O(1); don't worry about it in loop conditions, but avoid recomputing expensive functions there.
- `array_unique` is O(n log n); use keys-as-set for O(n) dedupe.
- `usort` O(n log n).
- Use generators (`yield`) to stream large datasets/files with O(1) memory.
- String concatenation `.=` is fine; `implode` for joining arrays.
- Per-request lifecycle: expensive bootstrapping happens on every request — enable OPcache and cache configs/routes.
