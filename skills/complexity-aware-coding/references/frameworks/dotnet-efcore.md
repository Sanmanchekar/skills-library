# ASP.NET Core / Entity Framework Core

- N+1: `Include`/`ThenInclude` or projections (`Select` into DTOs). Avoid lazy-loading proxies in loops.
- Multiple collection `Include`s cause cartesian explosion — use `AsSplitQuery()`.
- `AsNoTracking()` for read-only queries (less memory and CPU).
- Keep filters on `IQueryable` so they translate to SQL; calling `ToList()`/`AsEnumerable()` before `Where` pulls the whole table into memory.
- Bulk: `ExecuteUpdate`/`ExecuteDelete` (EF Core 7+) instead of load-modify-save; `AddRange` + one `SaveChanges` batches inserts.
- Stream large results with `AsAsyncEnumerable()`.
- Pagination: keyset (`Where(x => x.Id > lastId).Take(n)`) over `Skip` for deep pages.
- Compiled queries (`EF.CompileAsyncQuery`) for very hot queries.
- Log generated SQL (`LogTo`) to verify query count and shape.
