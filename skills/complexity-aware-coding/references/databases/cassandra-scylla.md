# Apache Cassandra / ScyllaDB

- Queries must target a partition key; `ALLOW FILTERING` means a scan across partitions — O(n), avoid.
- Design one table per query pattern (denormalize); joins don't exist.
- Keep partitions bounded (roughly < 100MB / < 100k rows); use time buckets in the partition key for time-series.
- Secondary indexes query every node — use sparingly; prefer a separate lookup table.
- Tombstones from deletes/TTLs slow reads; avoid delete-heavy queue patterns.
- Logged/multi-partition batches are for atomicity, not speed — they increase coordinator load. Single-partition unlogged batches are fine.
- Paginate with paging state; set sensible fetch sizes.
