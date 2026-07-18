---
name: api-design-node-express
description: Design or review a REST API written in Node.js with Express. Enforces async error handling (express-async-errors or explicit try/catch), zod/joi validation, structured error envelope, middleware ordering (helmet → cors → body → logger → rate-limit → auth), no unhandled promise rejections, and Prisma/Knex query patterns. Triggered when the user asks to design/review an Express route, handler, or router.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# api-design-node-express

## When to use

- Repo has `express` in package.json dependencies
- User asks: "design an endpoint in Node", "review this Express handler", "how should I structure this Express API"

## Design checklist

### Middleware order (top to bottom)
1. `helmet()` — security headers FIRST
2. `cors({ origin: ALLOWED })` — never `origin: '*'` for auth'd APIs
3. `express.json({ limit: '1mb' })` — cap body size
4. Request ID middleware (`X-Request-ID`)
5. Structured logger (pino / winston) with request ID
6. `express-rate-limit`
7. Auth (JWT / session)
8. Router

### Routing
- Version prefix: `app.use('/api/v1', v1Router)`
- Lowercase, hyphenated paths: `/orders/:id/line-items`
- Use `express.Router()` per resource, not one giant file

### Async error handling
- Import `express-async-errors` at the top of your entry file, OR wrap every async handler in try/catch — never rely on the framework to catch a rejected promise
- Define a final error middleware `(err, req, res, next)` that emits the standard envelope

### Validation
- Use `zod` (preferred) or `joi` — schema at route entry
- Return 400 with field-level errors on failure

```js
const CreateOrder = z.object({
  customerId: z.string().uuid(),
  items: z.array(Item).min(1),
});
router.post('/orders', async (req, res) => {
  const body = CreateOrder.parse(req.body); // throws ZodError → 400
  ...
});
```

### Idempotency
- Mutating endpoints accept `Idempotency-Key` header
- Cache `key → response` in Redis with ≥24h TTL

### Error envelope
```json
{
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "human-readable",
    "details": [{"field": "orderId", "issue": "not_found"}]
  },
  "requestId": "req_abc123"
}
```

### DB layer (Prisma / Knex)
- Prisma: always `select` explicit fields — never fetch whole rows unnecessarily
- Wrap multi-step writes in `prisma.$transaction`
- Knex: parameterize — no string concatenation into SQL
- Index every column in WHERE / JOIN / ORDER BY

### Pagination
- Cursor-based (`?cursor=<opaque>&limit=50`) for growing lists
- Cap `limit` at 100

## Rules

- NEVER swallow errors with `.catch(() => {})`
- NEVER return raw DB / ORM errors to clients — map to error codes
- NEVER `res.send(user)` on a User with password fields — use an explicit `select`
- ALWAYS `await` async DB calls (missing await = unhandled rejection)
- ALWAYS set `app.disable('x-powered-by')`
