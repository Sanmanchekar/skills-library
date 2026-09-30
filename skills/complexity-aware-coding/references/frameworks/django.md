# Database & ORM Complexity (Django/DRF focus)

In web backends, the dominant cost is usually **number of queries × query cost**, not CPU loops. Treat each query as an expensive operation.

## N+1 queries
```python
# BAD: 1 + n queries
for order in Order.objects.all():
    print(order.customer.name)

# GOOD: 1 query (FK/OneToOne) or 2 queries (reverse FK/M2M)
Order.objects.select_related("customer")
Customer.objects.prefetch_related("orders")
```
DRF serializers with nested fields → set `select_related`/`prefetch_related` in the viewset's `get_queryset()`.

## Query cost
- Filters/ordering on unindexed columns → full table scan, O(n) per query. Add indexes (`Meta.indexes`, `db_index=True`) for frequently filtered/sorted fields; composite indexes follow leftmost-prefix order.
- `LIKE '%term%'` can't use a B-tree index.
- `OFFSET` pagination is O(offset) — use cursor/keyset pagination (`CursorPagination` in DRF) for large tables.
- `.count()` on huge tables is expensive; avoid on every request.
- `len(queryset)` loads all rows; use `.count()` or `.exists()` as appropriate.

## Writes
- Loop of `.save()` → n queries. Use `bulk_create`, `bulk_update` (with `batch_size`), or `.update()` for set-based changes.
- Use `F()` expressions for atomic increments instead of read-modify-write.

## Memory
- `.iterator(chunk_size=...)` for large querysets to avoid loading all rows.
- `.only()` / `.values()` / `.values_list()` to fetch just needed columns.

## Background jobs (Celery)
- Don't enqueue one task per row for large n without batching — chunk IDs (e.g., 500–1000 per task).
- Pass IDs, not full objects, in task payloads.
- Process in bounded chunks so memory stays O(chunk) and a failure retries a small unit.

## Verification
- Use `django.test.utils.CaptureQueriesContext` or `assertNumQueries` in tests to lock in query counts.
- Use `EXPLAIN` (`queryset.explain()`) to confirm index usage for new hot queries.
