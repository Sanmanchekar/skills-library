---
name: capability-extraction
description: Scan a repo or set of services for a cross-cutting capability implemented locally and repeatedly (notifications, pdf-generation, file-upload, audit-log, feature-flags, scheduling, or user-supplied). Produces an evidence packet — inventory of call sites, duplication signals, coupling smells, blast radius — and ends with a proposed contract (transport, sync/async, event schema) and a strangler-pattern migration order. The capability name is passed as an argument. Triggered when the user says "extract X into a service", "centralize Y", "argue for a Z service", or "we have too many places doing W".
---

# capability-extraction

## When to use

- User says: "extract X into a service", "centralize Y", "we have too many places sending emails/uploading files/logging audits", "argue for a notification service"
- Monorepo or multi-repo audit — cross-cutting capability suspected
- Pre-work before writing an ADR to spin up a shared service

## The argument

`capability` — the cross-cutting concern to extract. Canonical values:
- `notifications` (email, SMS, push, WhatsApp)
- `pdf-generation`
- `file-upload` (storage abstraction)
- `audit-log`
- `feature-flags`
- `scheduling` (crons, delayed jobs, recurring tasks)

**Also supports user-defined capabilities** — the flow is the same, only the detection patterns change. Ask the user for their grep patterns if the capability isn't in the canonical set.

## The output is NOT "you should centralize this"

The output IS an **evidence packet** with a proposed contract and migration order. "Centralize it" is the easy conclusion; the value is:
- Inventory the reader can verify (file:line references, not vibes)
- A wire contract concrete enough to build against
- A migration order sequenced by risk × ownership

## Steps

### 1. Detect
Use the capability's detection table (below). For each pattern, grep across all services in scope. Record every hit with `service:path:line`.

### 2. Classify each hit
For every call site, tag it with:
- **Provider** (SES / Twilio / SendGrid / SMTP / ...)
- **Sync context** — is this on the request path? inside a DB transaction? in a background job?
- **Duplication signal** — template rendering nearby? retry loop wrapping the call? opt-out check?
- **Coupling smell** — does a failure here break unrelated business logic?

### 3. Aggregate
Count call sites by service and provider. Count each duplication signal by frequency. Rank coupling smells by severity (blast radius: does a slow send block a payment commit?).

### 4. Design the contract
- **Transport** decision (table below)
- **Sync vs async** decision (tree below)
- **Event schema** with mandatory + optional fields
- **Idempotency** — how the consumer dedupes
- **Ordering** — do consumers need it? (partition key)

### 5. Migration order (strangler pattern)
- Write path: new sends emit to the new topic/endpoint. Consumer service handles delivery.
- Backfill: convert existing call sites in priority order (highest coupling smell first, or by owner availability).
- Cleanup: remove local sender + retry logic + template code once all call sites are migrated.

### 6. Produce the evidence packet
Format below. The packet MUST end with the contract + migration order. Without those, the skill has failed.

---

## Detection tables (per canonical capability)

### notifications
| Signal | Patterns to grep |
|---|---|
| Provider SDKs | `boto3.client\('ses'\|'sns'\)`, `smtplib`, `sendgrid`, `twilio\.rest`, `msg91`, `karix`, `firebase_admin.messaging`, `nodemailer`, `SES\.`, `SNS\.`, `whatsapp_business` |
| Direct-send call | `send_email`, `send_sms`, `send_notification`, `sendMessage`, `send_push`, `Client\.send`, `.send_transactional`, `mail\.send` |
| Template rendering near call | `render_to_string`, `Template\(`, `render_template`, `Handlebars`, `Jinja`, HTML strings concatenated near a send call |
| Retry loop wrapping | `for.*attempt`, `retry\(`, `tenacity`, `backoff`, `sleep\(.*attempt`, `while` around a send call |
| Opt-out check | `unsubscribed`, `opted_out`, `consent`, `preferences\.` near a send call — flag INCONSISTENT if not present at every site |
| Coupling smell | send call inside `atomic\|transaction\|@transaction` block; send inside a request handler with no `.delay\(\)\|enqueue\|async` |

### pdf-generation
| Signal | Patterns to grep |
|---|---|
| Libs | `wkhtmltopdf`, `pdfkit`, `weasyprint`, `reportlab`, `puppeteer`, `chromium`, `pdf-lib`, `iText`, `PDFDocument`, `HTMLDoc` |
| Direct-gen call | `.generate_pdf`, `to_pdf`, `render_pdf`, `PDFKit\.`, `page\.pdf\(`, `pdf\.write` |
| Template rendering near | HTML string concatenation, `render_to_string.*html`, template file loading near the PDF call |
| Temp file + upload | `NamedTemporaryFile`, `mktemp`, `/tmp/.*\.pdf`, followed by `s3\.upload_file\|put_object\|storage\.upload` |
| Coupling smell | PDF generation in request handler (blocking, high-CPU); PDF gen in DB transaction |

### file-upload
| Signal | Patterns to grep |
|---|---|
| Storage SDKs | `boto3\.client\('s3'\)`, `s3\.upload`, `google\.cloud\.storage`, `azure\.storage\.blob`, `cloudinary`, `MinioClient`, `AmazonS3Client` |
| MIME / size validation | `content_type`, `mimetypes`, `python-magic`, ad-hoc extension allowlists |
| Virus scan hook | `clamav`, `virustotal`, missing at some sites — inconsistency signal |
| Signed-URL logic | `generate_presigned_url`, `getSignedUrl`, hardcoded expiry values |
| Coupling smell | upload in request handler (long body reads); no size cap; missing content-type validation |

### audit-log
| Signal | Patterns to grep |
|---|---|
| Direct writes | `AuditLog\.create`, `db\.insert.*audit`, `AuditEvent\(`, `.log_action`, `record_activity` |
| Ad-hoc formats | Different field names across services (`user_id` vs `actor_id` vs `who`), missing correlation IDs |
| Same-transaction | Audit insert inside the same DB transaction as the business write — flags atomicity coupling |
| Missing fields | grep for audit inserts without `tenant_id`, `request_id`, or `timestamp` |
| Coupling smell | audit write in a transaction; audit failure would roll back the business write |

### feature-flags
| Signal | Patterns to grep |
|---|---|
| SaaS SDKs | `launchdarkly`, `unleash`, `growthbook`, `statsig`, `split\.io`, `optimizely`, `flagsmith` |
| Home-grown | `is_enabled\(`, `feature_flag\(`, `Feature\.`, config-file-based flags mixed with SDK-based |
| Env-var flags | `os\.environ\.get\(.*FLAG` — signals ad-hoc rollout |
| Hardcoded percentages | `random\(\) < 0\.1`, `user_id % 10 == 0` — signals ad-hoc rollout |
| Default handling | flag reads without a default arg — inconsistency signal |
| Coupling smell | multiple flag systems coexisting; flag decision inside a hot loop with no caching |

### scheduling
| Signal | Patterns to grep |
|---|---|
| Libs / systems | `celery.*beat`, `cron`, `sidekiq.*scheduler`, `apscheduler`, `node-cron`, `bull.*repeat`, `Kubernetes CronJob`, `@Scheduled`, `airflow\.DAG` |
| Config locations | crontabs in code AND in `k8s/*.yaml` AND in an infra repo — visibility fragmented |
| Ad-hoc timers | `setInterval\(`, `Thread.*sleep.*loop`, `while True.*sleep` — hidden schedules |
| Duplicate runs | same cron in two services (fan-out that shouldn't be) |
| Coupling smell | scheduled job that writes to DB with no leader election; multi-replica services running the same schedule N times |

## Contract design

### Transport decision table

| Requirement | Transport | Notes |
|---|---|---|
| Fire-and-forget, high volume, decoupled consumers | **Kafka / Redpanda / Kinesis topic** | Consumers can be added later without changes to producers |
| Fire-and-forget, low volume, no replay needed | **SQS / SNS / Pub/Sub** | Simpler ops than Kafka |
| Caller needs immediate ack (OTP, sync workflow) | **gRPC or HTTP REST** | Sync; producer waits for consumer's response |
| Delayed / scheduled delivery | **Queue with delay** (SQS delay, Redis sorted set, Temporal, Sidekiq) | |
| Ordered per-entity (e.g., all events for one user) | **Kafka partitioned by entity_id** | Partition key is the entity |

### Sync vs async decision tree

```
Does the caller need to know the outcome of the capability call
before proceeding?
├─ No → ASYNC (default). Fire-and-forget via topic/queue.
├─ Yes, but eventual consistency is fine
│    (e.g., "was the email queued")
│    → ASYNC with ack topic OR sync HTTP returning "accepted" (202).
└─ Yes, strict — the outcome affects the caller's decision
     (e.g., OTP where user is waiting on the screen; PDF that's
     inlined in the response)
     → SYNC. Use gRPC / REST. Set strict timeout + fallback.
```

**Default is async.** Sync couples caller latency and availability to the capability service. Only choose sync when the caller genuinely can't proceed without the answer.

### Event schema — mandatory fields

Every event MUST include:
- `event_id` — UUID, unique per event
- `event_type` — e.g., `notification.requested.v1`
- `emitted_at` — ISO 8601 UTC
- `tenant_id` — for multi-tenant systems
- `idempotency_key` — for consumer dedup (often `{source_service}:{source_entity}:{action}`)
- `source` — `{service_name, version}` that produced the event
- `payload` — capability-specific body

Capability-specific `payload` shapes:

**notifications**
```json
{
  "template_id": "order_confirmation_v2",
  "channel": "email|sms|push|whatsapp",
  "recipient_ref": { "user_id": "..." },
  "locale": "en-IN",
  "variables": { "order_id": "...", "amount": 12500 },
  "priority": "normal|high|critical"
}
```

**pdf-generation**
```json
{
  "template_id": "invoice_v3",
  "output_ref": { "bucket": "invoices", "key": "..." },
  "variables": { "invoice_id": "...", "line_items": [...] },
  "callback_topic": "pdf.generated.v1"
}
```

**audit-log**
```json
{
  "actor": { "type": "user|system", "id": "..." },
  "action": "order.created",
  "target": { "type": "order", "id": "..." },
  "request_id": "req_abc",
  "changes": { "before": {...}, "after": {...} }
}
```

**file-upload**
```json
{
  "storage_key": "uploads/2026/07/abc.jpg",
  "content_type": "image/jpeg",
  "size_bytes": 123456,
  "owner_ref": { "user_id": "..." },
  "checksum": { "sha256": "..." }
}
```

**feature-flags** (evaluation request, if sync)
```json
{
  "flag_key": "checkout_v2",
  "context": { "user_id": "...", "tenant_id": "...", "attrs": {...} }
}
```

**scheduling**
```json
{
  "schedule_id": "invoice.monthly",
  "cron": "0 3 1 * *",
  "target": { "topic": "invoicing.run.v1", "payload_template": {...} },
  "owner": "billing-team"
}
```

### Idempotency

Consumers dedupe on `idempotency_key` for a rolling window (24h default). Recommend Redis SET with EX.

### Versioning

Event type includes a version suffix (`.v1`). Never mutate a v1 schema; introduce `.v2` alongside and migrate consumers.

---

## Migration order (strangler pattern)

### Phase 1 — Stand up the new service (2 weeks)
- Publish the contract (schema registry entry / OpenAPI / proto)
- Deploy consumer service to prod, connected to topic, no producers yet
- Add smoke test that a manually-published event is delivered end-to-end

### Phase 2 — Dual-path the highest-risk site (1 week)
- Pick the call site with the WORST coupling smell (e.g., send-in-transaction blocking a payment commit)
- New code: publish to topic
- Old code: still runs (dual send — accept temporary double delivery, or use idempotency to swallow duplicates)
- Verify consumer delivers correctly under real traffic

### Phase 3 — Cut over the risky site
- Remove the old direct send from that one site
- Old code is now strangled; the topic is the source of truth for this site

### Phase 4 — Backfill remaining sites
- Sequence by owner availability + coupling severity
- Each backfill = one PR: replace direct call with `publish(topic, event)`
- Delete the local retry/template/opt-out code that becomes redundant

### Phase 5 — Cleanup
- Remove the provider SDK from services that no longer use it
- Remove dead template files
- Update service READMEs

### Rollout risk table (fill in during recommendation)

| Site | Owner | Coupling severity | Recommended phase |
|---|---|---|---|
| payments_backend/tasks.py:142 | @payments | CRITICAL — blocks payment commit | Phase 2 (first) |
| orders_backend/emails.py:88 | @orders | HIGH — 3 retries block worker | Phase 4 (early) |
| ... | | | |

---

## Output — the evidence packet

```markdown
# Capability extraction — <capability>

**Scope**: <repos / services scanned>
**Scanned at**: <UTC timestamp>

## Summary
- Capability: <name>
- Found in: N services, M call sites, P providers
- Recommendation: extract `<capability>-service` — <one-line why>

## Inventory
| # | Service | File:Line | Provider | Context | Coupling smell |
|---|---|---|---|---|---|
| 1 | payments_backend | payments/tasks.py:142 | SES | in-transaction | CRITICAL — SMTP timeout blocks payment commit |
| 2 | orders_backend | emails/order.py:88 | SendGrid | request handler | HIGH — 8s worst-case blocks response |
| ... | | | | | |

## Duplication signals
- Template rendering — duplicated in 4 services (`orders_backend`, `payments_backend`, `refunds_backend`, `notifications_worker`)
- Retry logic — 5 different implementations (exponential in 2, fixed sleep in 2, none in 1)
- Opt-out checks — present in 2 services, MISSING in 4 (regulatory risk)
- Provider fan-out — 4 providers used inconsistently (SES for transactional, SendGrid for marketing, msg91 for SMS, Twilio for SMS in one service)

## Blast radius (top 3)
1. `payments_backend/tasks.py:142` — SMTP timeout blocks payment commit. Estimated user-visible failures: ~120/day at current volume.
2. `orders_backend/emails/order.py:88` — 8s send blocks HTTP response, causing p99 spike on `/orders`.
3. Missing opt-out in `marketing_backend/*` — regulatory exposure (CAN-SPAM / DPDPA equivalent).

## Recommendation: extract `notification-service`

### Contract
- **Transport**: Kafka topic `notification.requested.v1` (async default)
- **Sync path** (OTP only): gRPC `NotificationService.SendSync` with 3s timeout + SMS fallback
- **Event schema**:
  ` ` `json
  {
    "event_id": "uuid",
    "event_type": "notification.requested.v1",
    "emitted_at": "2026-07-15T10:00:00Z",
    "tenant_id": "...",
    "idempotency_key": "orders_backend:order_12345:confirmation",
    "source": { "service": "orders_backend", "version": "2.14.1" },
    "payload": {
      "template_id": "order_confirmation_v2",
      "channel": "email",
      "recipient_ref": { "user_id": "..." },
      "locale": "en-IN",
      "variables": { "order_id": "...", "amount": 12500 },
      "priority": "normal"
    }
  }
  ` ` `
- **Idempotency**: consumer dedupes on `idempotency_key` for 24h (Redis SET EX)
- **Ordering**: partitioned by `recipient_ref.user_id` (all messages to one user land in order)

### Migration order
| Phase | Site | Owner | Why this order |
|---|---|---|---|
| 2 | payments_backend/tasks.py:142 | @payments | CRITICAL coupling — must remove first |
| 4a | orders_backend/emails/order.py:88 | @orders | HIGH latency impact |
| 4b | refunds_backend/notify.py:31 | @payments | Same team as phase 2, batch |
| 4c | marketing_backend/campaigns.py:* (11 sites) | @growth | Grouped by module owner |
| 4d | admin_backend/alerts.py:22 | @platform | Low volume, easy |

### Non-goals for this extraction
- Not building a template editor UI in v1 (templates stay in git; add UI later)
- Not migrating marketing bulk-blast in v1 (different SLA; separate service)
- Not changing provider mix (SES/SendGrid/msg91/Twilio all supported — service picks per channel)

### Follow-ups (ADRs to write)
- ADR: choice of Kafka vs SQS for notification topic
- ADR: template storage (git vs Contentful vs custom)
- ADR: sync path for OTP — gRPC vs REST
```

---

## Rules

- NEVER recommend extraction based only on "we have N call sites" — the recommendation MUST cite coupling smells (blast radius), not just duplication
- NEVER produce the packet without file:line inventory — reviewers need to verify
- NEVER hand-wave the contract — the packet MUST include event schema, transport choice, sync/async rationale
- NEVER prescribe a migration all-at-once — always strangler with phases and per-site owner
- ALWAYS default the transport to async unless the caller genuinely cannot proceed without the outcome
- ALWAYS include `idempotency_key` in the event schema — consumers WILL see duplicates
- ALWAYS version the event type (`.v1`) — evolving schemas without versions breaks consumers silently
- If the user asks about a capability NOT in the canonical set, ask for their grep patterns before scanning — do not guess
