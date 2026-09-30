# MongoDB

- `explain("executionStats")`: look for `IXSCAN` vs `COLLSCAN`, and `totalDocsExamined` ≈ `nReturned`.
- Compound index order: ESR rule — Equality fields, then Sort fields, then Range fields.
- `skip()` pagination is O(skip); use range queries on an indexed field (`_id > lastId`).
- Unbounded arrays inside documents grow document size (16MB limit) and make updates expensive; use a separate collection or bucket pattern.
- `$lookup` does a query per input document unless `foreignField` is indexed; prefer embedding for data read together.
- Aggregations: put `$match` and `$project` early, `$sort` on indexed fields; stages have a 100MB memory limit (`allowDiskUse` spills to disk — slow).
- Unanchored or case-insensitive regex can't use indexes efficiently; use text/Atlas Search indexes.
- Bulk operations: `bulkWrite`, `insertMany` (ordered: false for throughput).
- Large `$in` lists are fine with an index but each element is a seek — batch reasonably.
- Projection to return only needed fields; use `.lean()` in Mongoose.
