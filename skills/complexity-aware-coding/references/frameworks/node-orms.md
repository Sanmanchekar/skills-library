# Node.js: Express / NestJS / Prisma / TypeORM / Sequelize / Mongoose

- General: never `await` a DB call inside a loop over n items. Fetch with `IN (...)`/`where: { id: { in: ids } }` once and map in memory.
- Prisma: use `include`/`select` for relations; `createMany`/`updateMany` for bulk; cursor-based pagination (`cursor` + `take`) for large tables; `select` only needed fields.
- TypeORM: `relations` or `leftJoinAndSelect` for eager loading; `insert().values([...])` for bulk; `.stream()` for large reads; avoid `lazy: true` relations in loops.
- Sequelize: `include` for eager loading; `bulkCreate`; `raw: true` for read-heavy paths; avoid `findAll` without `limit` on large tables.
- Mongoose: `.lean()` for reads (plain objects, much less memory); `populate` issues one extra query per path (not per doc) but pulls full docs — use `select`; `.cursor()` for streaming; `bulkWrite` / `insertMany`.
- GraphQL (Apollo, NestJS): resolvers cause N+1 per field — use DataLoader to batch; enforce query depth/complexity limits.
- NestJS/Express: keep CPU-heavy work off the request thread (BullMQ queue or worker_threads); validate payload size limits.
