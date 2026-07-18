---
name: webhook-hardening
description: Review a webhook receiver for the full defensive stack — signature verification (HMAC timing-safe), timestamp replay window, dedup by provider event id, out-of-order handling, retry acceptance (return 2xx before doing async work), DLQ for unprocessable events, and provider-specific quirks (Stripe / Razorpay / Cashfree / PhonePe / GoCardless / Adyen). Emits severity-tagged findings that would prevent the "we processed the same event three times" or "an attacker forged a webhook" class of P0. Triggered when the user asks to "review this webhook", "harden webhook", "why did we process this webhook twice", or a file contains a webhook handler for a payment / notification provider.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# webhook-hardening

## When to use

- User says: "review this webhook", "harden this webhook", "why did we process the same webhook twice / miss a webhook / fail to verify a webhook signature"
- File contains a webhook handler (`/webhook/*`, `/callback/*`, `/notify/*`, `_webhook`, `receive_event`) for a payment / notification / storage provider
- Post-incident where the trigger was a webhook (duplicated processing, forged event, silent drop, out-of-order state machine)

## The 6-layer defense

Every webhook receiver MUST handle every layer. Missing any one is a finding.

```
1. Signature verification    — is this really the provider?
2. Timestamp window          — is this a fresh event (not a replayed old one)?
3. Dedup on provider event_id — have we already processed this?
4. Return 2xx FAST           — before doing async work; providers retry aggressively
5. Ordering + state machine  — events can arrive out of order; check terminal states
6. DLQ                       — unprocessable events go to a dead-letter queue for investigation
```

## Layer 1 — Signature verification

- [ ] The receiver verifies a signature/MAC on every request using the **shared secret from the provider**
- [ ] Uses a **timing-safe comparison** (`hmac.compare_digest`, `crypto.timingSafeEqual`, `MessageDigest.isEqual`) — NOT `==` (leaks the secret one byte at a time)
- [ ] The signature is computed over the **raw request body**, not the parsed JSON (parsing may reorder or normalize)
- [ ] Rejects with **401** on bad signature — no body inspection, no logging of payload details
- [ ] Secret is loaded from env / secret manager — NOT committed to source

Provider-specific:

| Provider | Header | Algorithm | Notes |
|---|---|---|---|
| Stripe | `Stripe-Signature` | HMAC-SHA256 | verify `v1=...` schemes; ignore future ones |
| Razorpay | `X-Razorpay-Signature` | HMAC-SHA256 | signed body |
| Cashfree | `x-webhook-signature` + `x-webhook-timestamp` | HMAC-SHA256 | signature over `timestamp + payload` |
| PhonePe | `X-VERIFY` | SHA256(base64(payload) + endpoint + salt) | different from most; endpoint IS in the signed material |
| GoCardless | `Webhook-Signature` | HMAC-SHA256 | |
| Adyen | HMAC in `notificationItems[].additionalData.hmacSignature` | HMAC-SHA256 over a specific field concat | Adyen's format is unusual — grep the docs before writing verifier |

## Layer 2 — Timestamp replay window

- [ ] The receiver rejects events where the timestamp is older than **5 minutes** (Stripe convention; adjust per provider)
- [ ] Rejects with 400 without processing — otherwise an attacker who captured an old valid webhook can replay it forever
- [ ] Timestamp source is the SIGNED field (part of the signature), not a client-controlled header

If the provider doesn't include a timestamp, replay is prevented only by dedup (Layer 3) — flag this as a lower-severity finding since the attack requires the signing key.

## Layer 3 — Dedup on provider event id

- [ ] The receiver reads `(provider_name, event_id)` from the payload BEFORE any state change
- [ ] Looks up in a dedup store (RDBMS unique index or Redis SETNX). If already seen → return 2xx immediately (idempotent)
- [ ] Storage retains dedup keys for ≥ **7 days** — providers may retry that long
- [ ] The dedup check + the state write are **atomic** — same race as idempotency review's Layer 3 (see [idempotency-review](../idempotency-review))

Storage row shape:
```
(provider, event_id, received_at, processed_at, response_status, response_body, error_reason?)
```

## Layer 4 — Return 2xx fast (avoid provider retries you don't want)

Providers retry on non-2xx. If your receiver does 5 seconds of work synchronously, a downstream blip means duplicate deliveries.

- [ ] The receiver enqueues the event to a job queue and returns 2xx within **< 500ms**
- [ ] Async worker does the real state change (with the same dedup key at worker level)
- [ ] Explicit: NEVER do direct DB writes to money-adjacent tables from the webhook thread — the connection may reset before 2xx is sent

Exception: for LOW-volume, LOW-latency handlers you can process synchronously — flag anything > 500ms as a HIGH finding.

## Layer 5 — Ordering + state machine

Providers do NOT guarantee ordering. `payment.captured` may arrive AFTER `payment.refunded`.

- [ ] The consumer applies events through a **state machine** that rejects impossible transitions
- [ ] Terminal states (`refunded`, `chargeback_won`, `settled`) do NOT accept further transitions — log + drop
- [ ] For out-of-order safe events (e.g., updates to a status field), use **`WHERE current_state IN (allowed_prior_states)` on the UPDATE** — never blind UPDATE
- [ ] For events that MUST arrive in order (rare), reconstruct from a monotonic sequence number in the payload

## Layer 6 — DLQ (dead-letter queue)

- [ ] Events that fail permanently (schema mismatch, unknown event type, terminal-state violation) go to a DLQ, NOT retried forever
- [ ] DLQ has a monitored dashboard + alert
- [ ] DLQ entries include the raw payload, receipt time, error, and the code path that rejected

## Handler-level correctness

- [ ] Handler is thread-safe — two workers can process two different events for the same entity concurrently (use row-level locks or optimistic concurrency)
- [ ] Handler is idempotent at the worker level too — retry-safe on transient failures (see [idempotency-review](../idempotency-review))
- [ ] Handler validates the JSON schema (Pydantic / zod / joi) — malformed events go to DLQ, not 500

## Output format

Same as [code-review](../code-review) — severity table + per-finding block. Severity guide:

| Severity | Meaning for webhooks |
|---|---|
| CRITICAL | No signature verification OR non-timing-safe compare OR sync processing of money events |
| HIGH | Missing dedup, missing timestamp check, no DLQ, or > 500ms sync work in the handler |
| MEDIUM | Missing state-machine transition guard, missing raw-body signature (verified against parsed JSON), retention < 7 days |
| LOW | Missing schema validation, undocumented provider, no monitored DLQ dashboard |

## Rules

- NEVER trust the `event_id` before the signature is verified — an attacker can pick any id
- NEVER `==` on HMACs — always timing-safe
- NEVER return 500 as a "please retry" signal for non-transient errors — that's what DLQ is for
- NEVER return 2xx after successful signature verification without also completing the dedup check — otherwise the same event can be enqueued twice
- ALWAYS parse the SIGNED body byte-for-byte — parsers can normalize whitespace and break the signature
- If the reviewed webhook is for a money event and any of Layers 1-3 is missing, treat as CRITICAL by default
