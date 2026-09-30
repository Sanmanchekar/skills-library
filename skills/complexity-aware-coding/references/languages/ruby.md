# Ruby

- `Array#include?`, `index`, `find`, `delete` are O(n). Use `Set` or `Hash` for repeated lookups.
- `arr += [x]` or `arr = arr + other` creates a new array each time (O(n²) in loops); use `<<` / `concat`.
- String `+=` allocates a new string; use `<<` on a mutable string or `Array#join`.
- `inject { |h, x| h.merge(...) }` copies the hash every iteration (O(n²)); use `each_with_object` or `merge!`.
- `map.flatten` → `flat_map`; `select.map` → `filter_map`; `sort_by` over `sort { }` for key-based sorts.
- `Enumerable#lazy` for large or infinite pipelines.
- `group_by`, `tally`, `index_by` (Rails) turn O(n²) searches into O(n).
- Memoize with `@x ||= ...` (careful with nil/false results).
- Rails/ActiveRecord specifics: see `frameworks/rails.md`.
