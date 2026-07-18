---
name: api-design-go-gin
description: Design or review a REST API written in Go with the Gin framework. Enforces idempotency keys, request validation via go-playground/validator, structured error envelope, middleware ordering (recover → logger → cors → auth → ratelimit), context propagation, and gorm/sqlx pattern rules. Triggered when the user asks to design/review a Go+Gin endpoint, handler, or router.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# api-design-go-gin

## When to use

- File imports `github.com/gin-gonic/gin`
- User asks: "design an endpoint in Go", "review this Gin handler", "how should I structure this Go API"
- Repo has `main.go` + `go.mod` referencing `gin-gonic/gin`

## Design checklist

### Routing
- Group routes by version: `v1 := r.Group("/api/v1")`
- Use lowercase, hyphenated paths: `/orders/:id/line-items`
- Method choice: `GET` (safe+idempotent) · `POST` (create) · `PUT` (full replace, idempotent) · `PATCH` (partial) · `DELETE` (idempotent)

### Middleware order (top to bottom)
1. `gin.Recovery()` — catch panics FIRST
2. Request ID injection (`X-Request-ID`)
3. Structured logger with request ID
4. CORS
5. Auth (JWT / session)
6. Rate limit (per-user, per-IP fallback)
7. Handler

### Request validation
- Bind + validate with `c.ShouldBindJSON(&req)` — struct tags: `binding:"required,email,max=255"`
- Return 400 with field-level errors on validation failure

### Idempotency
- Mutating endpoints (POST/PUT/PATCH) accept `Idempotency-Key` header
- Store `key → response` in Redis with TTL ≥ 24h
- Repeat request with same key returns the cached response

### Error envelope
```json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "human-readable",
    "details": [{"field": "order_id", "issue": "not_found"}]
  },
  "request_id": "req_abc123"
}
```

### Context propagation
- Every DB / RPC call takes `c.Request.Context()`
- Set request-scoped timeout: `ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)`

### DB layer
- Use `gorm.WithContext(ctx)` or `sqlx.QueryContext(ctx, ...)` — no context-less calls
- Transactions via `db.Transaction(func(tx *gorm.DB) error { ... })`
- Never use `SELECT *`
- Index every column in a WHERE / JOIN / ORDER BY

### Pagination
- Cursor-based (`?cursor=<opaque>&limit=50`) — not offset — for lists that grow
- Cap `limit` at 100

## Output format (design mode)

```markdown
# <Endpoint name>

## Contract
- Method: POST
- Path: /api/v1/orders
- Auth: Bearer JWT

## Request
` ` `go
type CreateOrderRequest struct {
    CustomerID string `json:"customer_id" binding:"required,uuid"`
    Items      []Item `json:"items" binding:"required,min=1,dive"`
}
` ` `

## Handler skeleton
` ` `go
func CreateOrder(c *gin.Context) { ... }
` ` `

## Errors
| Code | HTTP | When |
|---|---|---|
| VALIDATION_FAILED | 400 | bind/validate error |
| CUSTOMER_NOT_FOUND | 404 | ... |
```

## Rules

- NEVER use `panic()` in handlers — return an error, let `gin.Recovery()` handle unexpected
- NEVER use `context.Background()` inside a handler — propagate `c.Request.Context()`
- NEVER return raw DB errors to clients — map them to your error codes
- ALWAYS validate at the edge (binding tags), never trust downstream layers to catch bad input
