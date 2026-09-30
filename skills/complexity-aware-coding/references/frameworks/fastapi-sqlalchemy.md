# FastAPI / Flask + SQLAlchemy

- Relationship default is lazy `select` → accessing a relation per row is N+1. Use `selectinload` (collections, 2 queries) or `joinedload` (many-to-one) in the query.
- Set `lazy="raise"` on relationships to fail fast on accidental lazy loads.
- Bulk writes: `session.add_all` + single commit, or `insert().values([...])` / `session.execute(insert(Model), rows)`; avoid commit per row.
- Stream large results: `execution_options(yield_per=1000)` / `.yield_per()`; select only needed columns.
- Pagination: keyset (`WHERE id > :last ORDER BY id LIMIT n`) for large tables instead of OFFSET.
- FastAPI async: never call sync DB drivers or blocking I/O in `async def` routes (blocks the event loop); use async drivers or plain `def` routes (run in threadpool).
- Pydantic validation/serialization is O(payload) — paginate large responses; `response_model` on huge lists is costly.
- Background tasks for heavy work belong in a real queue (Celery/RQ/Arq), not `BackgroundTasks`, when n is large.
