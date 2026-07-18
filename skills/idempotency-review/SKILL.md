---
name: idempotency-review
description: Review idempotency correctness on mutating endpoints, background jobs, webhook consumers, and refund/payout flows. Detects missing Idempotency-Key handling, non-idempotent DB writes, unsafe retry loops, replay windows too short, and race conditions between concurrent requests with the same key. Stack-agnostic. Emits findings that would prevent the "triple-refund on retry" class of P0. Triggered when the user asks to "check idempotency", "review idempotency", "why did we double-charge / double-refund", "make this endpoint safe to retry", or shares a payment / refund / payout / booking handler.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# idempotency-review

## When to use

- User says: "review idempotency", "check idempotency", "make this safe to retry", "why did we double-charge/double-refund/duplicate booking?"
- File is a mutating endpoint on `/payments/*`, `/refunds/*`, `/payouts/*`, `/orders/*`, `/mandates/*`, `/bookings/*`, or a webhook consumer / background job that writes to money-adjacent tables
- Post-incident when the root cause is "the client retried and we processed twice"

## The core invariant

> **Same request, sent twice, must produce one effect.**

Concretely: for every mutating operation, there must exist a **key** the client (or upstream) provides, and the server must record "I've seen this key before → return the cached result" atomically with the state change. If the record is missing OR the check-and-write isn't atomic, you have a race.

## The three failure modes to catch

| # | Failure mode | What it looks like |
|---|---|---|
| 1 | **No key** | `POST /refunds` accepts nothing that uniquely identifies "this refund attempt" — client retry ⇒ new refund |
| 2 | **Key present, write not atomic** | check `if key exists → return`; then perform state change; then insert the key — race window between check and insert |
| 3 | **Key stored, but not the response** | second request with same key returns 400 "duplicate" instead of the original 200 response — client thinks the operation failed and retries with a NEW key ⇒ double effect |

## Review checklist (produce as findings)

### On the API surface

- [ ] Every mutating endpoint (POST/PUT/PATCH/DELETE) accepts an `Idempotency-Key` header OR carries a natural key in the body (e.g., `client_reference_id` on Stripe, `merchant_order_id` on Razorpay)
- [ ] Key format is validated: length ≤ some bound, non-empty, opaque to server (don't parse business meaning from it)
- [ ] Missing key on a mutating endpoint is **rejected with 400** in production — silent generation of a random key on the server side defeats the point
- [ ] Key is scoped correctly. `Idempotency-Key: abc` should NOT collide with `abc` from a different tenant / user / account. Store as `(scope, key) → response`.

### On the storage

- [ ] Key + response are stored in a **durable** store (RDBMS or Redis with `AOF`/persistence) — not in-memory
- [ ] Storage row includes: `key`, `scope`, `request_hash`, `response_body`, `response_status`, `created_at`, `expires_at`
- [ ] `request_hash` is set — if a second request arrives with the same key but a **different body**, that's a client bug; return `409` or the original response, but never process it as new
- [ ] Retention ≥ 24h. Client retry backoff can span 20+ minutes; 24h is the minimum safe. For refunds, prefer 7 days.

### On concurrency (the atomic check-and-write)

The killer bug lives here. The check-then-write pattern is fine ONLY if the storage guarantees atomicity for that pair.

**Correct patterns**:
- **DB unique index** on `(scope, key)` + INSERT ... ON CONFLICT DO NOTHING → the winning INSERT proceeds; the losing INSERT returns "duplicate" and reads the winning row's response.
- **Redis SETNX** on `key:<scope>:<key>` with a TTL and a value that includes "in progress" → resolve to either the completed response or a 409 while in-progress.
- **DB advisory lock** on hash(key) held for the request duration + row check.

**Incorrect** (bug):
- `SELECT ... WHERE key = ?` → `if not found: INSERT + do work` → race window between SELECT and INSERT (two concurrent requests with the same key both see "not found", both do work).

### On what happens during "in progress"

Two requests arrive with the same key. First is still processing. Second arrives:
- **Wrong**: assume the first succeeded and return a cached response that hasn't been written yet ⇒ client thinks done, side effect not finished
- **Wrong**: process the second in parallel ⇒ two effects
- **Right**: return `409 Conflict` with `Retry-After: <n>` OR block briefly (bounded — 1-3s) waiting for the first to finish, then return its response. Never process concurrently.

### On error handling (the trap)

- [ ] The response cached under the key includes **the outcome AS-IS**, error responses included. If the operation failed 500, retries with the same key return the SAME 500 (not "duplicate"). This lets the client's retry policy work correctly.
- [ ] But: if the state change was **partially** applied before the 500, that's a transactional integrity bug, not idempotency — fix that separately with `SAVEPOINT` / transactional outbox.
- [ ] Distinguish "you already did this" (2xx from cache) from "we haven't seen this key" (2xx after processing). Prefer identical response bodies; add a header like `Idempotent-Replayed: true` if the caller needs to distinguish.

### On background jobs & webhook consumers

Jobs and webhook consumers retry too. Apply the same rules:
- [ ] Every job that writes derives a key from `(job_type, business_id)` (e.g., `settle_payment:payment_123`) — replay is safe
- [ ] Webhook consumers dedupe on `(provider, event_id)` — see [webhook-hardening](../webhook-hardening) for the full webhook checklist

### On refunds specifically (the triple-refund case)

Refunds are the worst class of bug because money moves and users notice:
- [ ] Refund key MUST be scoped to `(payment_id, refund_reason, amount)` — a partial refund and a full refund on the same payment are different operations; both need distinct keys, but a retry of the SAME refund must dedupe
- [ ] `initiate_refund` must succeed idempotently even when the upstream PG call succeeded but our DB write failed — store the key + PG's refund_id BEFORE calling the PG; on retry, look up first and skip the PG call
- [ ] Webhook confirming the refund also dedupes on `(provider, event_id)` AND on the refund's terminal state — a settled refund cannot be "re-settled"

## Output format

Same as [code-review](../code-review) — severity table + per-finding block with problem, impact, and a ready-to-apply code snippet. Severity guide:

| Severity | Meaning for idempotency |
|---|---|
| CRITICAL | Money-moving endpoint has no key OR non-atomic check-and-write |
| HIGH | Key present but scope wrong, or retention < 24h |
| MEDIUM | Cached response format bug (e.g., returns 400 on replay instead of the original 200) |
| LOW | Missing `Idempotent-Replayed` header, or missing `request_hash` sanity check |

## Rules

- NEVER accept "our client won't retry" as a defense — networks, load balancers, and mobile radios retry without the client knowing
- NEVER server-generate the idempotency key silently — reject with 400 on the mutating endpoints
- NEVER use in-memory dedup for keys — a process restart erases it
- ALWAYS cite the specific pattern: `INSERT ... ON CONFLICT`, `SETNX`, `advisory lock` — abstract "make it atomic" isn't actionable
- ALWAYS include a retry-flow example in the fix: `client sends → we receive → we look up → we (do or skip) → we respond` — makes the invariant visible
- If the reviewed endpoint touches money, treat missing idempotency as CRITICAL by default — even without evidence of an incident yet
