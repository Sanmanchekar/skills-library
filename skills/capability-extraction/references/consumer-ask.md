# Writing the consumer's ask

Read this file when Step 3 needs to produce field 4 (What this service needs from a centralized party).

Frame from THIS service's perspective — what API surface does this service want to CALL? Do NOT specify transport (Kafka vs REST vs gRPC) — that's the provider's decision informed by all consumers, not this service's ask.

## Template

```markdown
### What this service needs

**As a consumer**, this service needs to be able to:

- `<verb> <capability action>` — <when we call it, what we send, what we expect back>

**Delivery-semantics we need**:
- Async (fire-and-forget) for: <list of use cases>
- Sync (with response) for: <list of use cases, e.g., OTP where the caller is blocked>

**Guarantees we need**:
- Idempotency — we will send the same request more than once (retries, redelivery)
- Ordering — <yes, per user_id> OR <no, not needed>
- Delivery SLA — <e.g., "within 30s of publish for transactional email">

**Data we would send** (illustrative — provider may adapt):
` ` `json
{
  "template_id": "payment_success",
  "recipient_ref": { "user_id": "..." },
  "variables": { "amount": 12500, "order_id": "..." },
  "priority": "normal"
}
` ` `

**What we do NOT need this party to do**:
- <e.g., "manage user preferences — that's a separate consent service">
- <e.g., "render templates in our locale-specific format — we'll pass fully-resolved copy">
```

The point: this service is stating its needs, not designing the provider.

## Rules

- ALWAYS include "What we do NOT need this party to do" — scope control
- NEVER specify transport (Kafka / REST / gRPC) — that's the provider's call
- NEVER pick vendors — that's the provider's call
- Data payload is ILLUSTRATIVE — provider may adapt field names in the final contract
