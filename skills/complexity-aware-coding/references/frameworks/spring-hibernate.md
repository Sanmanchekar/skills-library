# Spring Boot / JPA / Hibernate

- Defaults: `@ManyToOne`/`@OneToOne` are EAGER; set them to `FetchType.LAZY`. Collections are LAZY.
- N+1: `JOIN FETCH` in JPQL, `@EntityGraph`, or `@BatchSize` / `hibernate.default_batch_fetch_size` (loads lazy relations in IN-batches).
- Fetch-joining a collection with pagination triggers in-memory pagination (Hibernate warns: "firstResult/maxResults specified with collection fetch; applying in memory") — fetch IDs page first, then fetch entities by IDs.
- Fetching multiple collections in one query causes cartesian products (`MultipleBagFetchException` for Lists) — split queries.
- `Page<T>` runs an extra COUNT query; use `Slice<T>` when total count isn't needed.
- Batch inserts: set `hibernate.jdbc.batch_size`, `order_inserts=true`; IDENTITY ID generation disables insert batching — use SEQUENCE where supported.
- Large reads: DTO projections instead of entities; `Stream<T>` with fetch size or `ScrollableResults`; clear the persistence context periodically in batch loops (`entityManager.clear()`), otherwise memory grows O(n).
- `@Transactional(readOnly = true)` for reads (skips dirty checking).
- Disable `spring.jpa.open-in-view` to avoid lazy loads in the web layer.
- `@Modifying` bulk JPQL updates instead of loading and saving each entity.
