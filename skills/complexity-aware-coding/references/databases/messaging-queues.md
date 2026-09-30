# Message Brokers & Queues: Kafka/Redpanda, RabbitMQ, SQS, Celery

- Throughput scales with parallelism: Kafka consumer parallelism is capped by partition count; plan partitions for peak load.
- Per-message DB writes cap throughput at DB latency × messages. Batch-consume and bulk-write (e.g., `max.poll.records`, SQS `ReceiveMessage` up to 10, `SendMessageBatch`).
- Keep messages small; pass IDs/pointers (S3 key) instead of large payloads.
- Idempotent consumers (dedupe keys) so retries don't multiply work.
- Monitor consumer lag / queue depth; lag growth means processing is O(slower) than arrival rate.
- Celery: chunk large fan-outs (`chunks`, `group` with batched IDs), set `prefetch_multiplier` appropriately for long tasks, avoid one task per row for millions of rows, and avoid waiting on subtasks inside tasks.
- RabbitMQ: set prefetch (`basic.qos`), avoid huge unacked backlogs, use lazy/quorum queues for long queues.
