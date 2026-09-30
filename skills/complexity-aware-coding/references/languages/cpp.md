# C++

- `std::vector`: `push_back` amortized O(1); `reserve(n)` to avoid reallocations; insert/erase not at end O(n). Erase-remove idiom (or `std::erase_if`, C++20) for bulk removal in O(n) instead of repeated `erase` (O(n²)).
- `std::deque` for O(1) push/pop at both ends.
- `std::list`: O(1) splice/insert given iterator, but poor cache locality — usually slower than vector in practice.
- `std::map/set`: O(log n), ordered. `std::unordered_map/set`: O(1) average; call `reserve` for known sizes; poor hash → O(n) worst.
- `std::find` on containers is O(n); use the container's own `find`/`contains` (C++20) for maps/sets.
- `std::sort` O(n log n); `std::nth_element` O(n) average for k-th element; `std::partial_sort` for top-k.
- Pass large objects by `const&`; return by value (RVO/move); use `std::move` to avoid copies; `emplace_back` to construct in place.
- Avoid `std::endl` in hot output loops (flushes each time); use `'\n'`.
- Cache locality often dominates Big O constants: prefer contiguous memory (struct-of-arrays for hot numeric loops).
- `std::shared_ptr` copies cost atomic refcount ops; prefer `unique_ptr` or references.
