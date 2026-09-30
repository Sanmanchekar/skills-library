# Elasticsearch / OpenSearch

- Deep pagination: `from + size` is limited by `index.max_result_window` (10,000 default) and gets costlier with depth. Use `search_after` with a point-in-time (PIT) for deep or export pagination.
- Leading wildcards (`*term`) and unanchored regex scan the term dictionary — use n-gram/wildcard field types instead.
- Use `keyword` fields for exact match, sorting, and aggregations; `text` for full-text.
- Put non-scoring conditions in `filter` context (cacheable, no scoring cost).
- High-cardinality `terms` aggregations are memory-heavy; use `composite` aggregations to paginate buckets.
- Script queries/sorts run per document — avoid on large indexes; precompute fields at index time.
- Index with the `_bulk` API (batch sizes of a few MB); tune `refresh_interval` during large loads.
- Avoid mapping explosion (dynamic keys from user data) — use `flattened` type or strict mappings.
