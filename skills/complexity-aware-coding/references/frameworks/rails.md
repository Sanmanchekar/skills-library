# Ruby on Rails / ActiveRecord

- N+1: `includes` (auto-choose), `preload` (separate queries), `eager_load` (LEFT JOIN). Enable `strict_loading` or use the Bullet gem to catch lazy loads.
- Batch iteration: `find_each` / `in_batches` (default 1000) instead of `.all.each` on large tables.
- `pluck(:id)` instead of `map(&:id)` (avoids instantiating models).
- `exists?` (LIMIT 1 query) vs `present?`/`any?` on an unloaded relation (may load records).
- `size` uses loaded records or COUNT; `length` loads all; `count` always queries.
- `counter_cache` for frequent association counts.
- Bulk writes: `insert_all` / `upsert_all` / `update_all` (skip callbacks — know the trade-off) instead of `save` per row.
- Add indexes on foreign keys and filtered columns in migrations.
- Views: collection rendering `render partial: ..., collection:` is faster than loops of `render`; fragment caching for expensive partials.
- Background jobs (Sidekiq/ActiveJob): pass IDs, batch large workloads.
