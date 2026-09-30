# Amazon DynamoDB

- `GetItem`/`Query` on partition key: cost proportional to items read, independent of table size. `Scan`: reads the whole table — avoid in request paths.
- Filter expressions apply after reading: you still pay RCUs for filtered-out items. Design keys so the key condition does the filtering.
- Query/Scan return at most 1MB per page — paginate with `LastEvaluatedKey`.
- Hot partitions: skewed partition keys throttle; add high-cardinality keys or write sharding.
- Access-pattern-first design: model GSIs/LSIs per query; GSIs are eventually consistent and cost extra writes.
- Batch APIs: `BatchGetItem` (up to 100 items), `BatchWriteItem` (up to 25) — handle `UnprocessedItems` with backoff.
- Item size limit 400KB; large blobs belong in S3 with a pointer.
- Use `ProjectionExpression` to reduce read size; strongly consistent reads cost 2× RCUs.
