# Laravel / Eloquent

- N+1: eager load with `with()`, `load()` after the fact, `withCount()` for counts. Call `Model::preventLazyLoading()` in non-production to catch lazy loads.
- Large tables: `chunk()` / `chunkById()` (safe when updating rows), `lazy()`, or `cursor()` (one model in memory at a time).
- `exists()` instead of `count() > 0`; `pluck()` for single columns; `select()` only needed columns.
- Bulk writes: `insert()`, `upsert()`, query-builder `update()` instead of `create()`/`save()` per row (note: these skip model events).
- Collections (`Collection::contains`, `where`, `firstWhere`) are in-memory O(n) — don't filter in PHP what SQL can filter; use `keyBy()` for O(1) lookups.
- Queue heavy work (Horizon/SQS); batch jobs with `Bus::batch`.
- Cache configs/routes/views in production (`php artisan optimize`).
