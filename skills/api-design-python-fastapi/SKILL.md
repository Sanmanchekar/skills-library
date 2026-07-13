---
name: api-design-python-fastapi
description: Design or review a REST API written in Python with FastAPI. Enforces Pydantic v2 request/response models, dependency injection for auth and DB sessions, async patterns, structured error envelope via exception handlers, middleware ordering, idempotency, and SQLAlchemy async session rules. Triggered when the user asks to design/review a FastAPI endpoint, router, or dependency.
---

# api-design-python-fastapi

## When to use

- File imports `fastapi` or repo has `fastapi` in requirements
- User asks: "design a FastAPI endpoint", "review this FastAPI route", "how should I structure this FastAPI app"

## Design checklist

### Structure
- Routers per resource in `app/api/v1/`, mounted with prefix `/api/v1`
- One `main.py` wires middleware + routers only — no business logic there
- Config via `pydantic-settings` — never `os.environ` scattered through code

### Request / response models
- Pydantic v2 `BaseModel` for every request and response — never dict
- Separate `CreateOrderRequest`, `OrderResponse`, `OrderDB` (internal) models
- Use `response_model=` on every route — enforces the contract at runtime

```python
class CreateOrderRequest(BaseModel):
    customer_id: UUID
    items: list[Item] = Field(min_length=1)

@router.post("/orders", response_model=OrderResponse, status_code=201)
async def create_order(body: CreateOrderRequest, db: AsyncSession = Depends(get_db)):
    ...
```

### Dependency injection
- Auth: `current_user: User = Depends(get_current_user)`
- DB: `db: AsyncSession = Depends(get_db)` — never module-level session
- Request-scoped values (tenant, request ID) via dependencies

### Async rules
- If any DB call is async, the whole handler MUST be `async def`
- NEVER call sync blocking code (requests.get, time.sleep, sync SQLAlchemy) inside `async def` — use `httpx.AsyncClient`, `asyncio.sleep`, async SQLAlchemy
- Wrap CPU-heavy work in `run_in_threadpool`

### Middleware order
1. `CORSMiddleware` (with explicit `allow_origins`)
2. Request ID injection
3. Structured logging (structlog / loguru)
4. Rate limit (slowapi)
5. Auth (usually via Depends, not middleware)

### Error envelope
Register an exception handler that emits:
```json
{
  "error": {"code": "ORDER_NOT_FOUND", "message": "...", "details": []},
  "request_id": "req_abc123"
}
```
Map `HTTPException`, `RequestValidationError`, and your domain exceptions.

### Idempotency
- Mutating endpoints accept `Idempotency-Key` header via dependency
- Cache `key → response` in Redis with ≥24h TTL

### SQLAlchemy async
- Use `AsyncSession` — every DB call `await`ed
- Transactions: `async with db.begin(): ...`
- Never use `session.query()` (sync API) — use `select()`

### Pagination
- Cursor-based (`?cursor=<opaque>&limit=50`) for growing lists
- Cap `limit` at 100

## Rules

- NEVER return a Pydantic model with secret fields (password, token) — build a response model
- NEVER catch `Exception` broadly and re-raise as 500 — let FastAPI's exception handler map it
- NEVER share an `AsyncSession` across requests
- ALWAYS use `response_model` — it doubles as documentation and runtime filter
