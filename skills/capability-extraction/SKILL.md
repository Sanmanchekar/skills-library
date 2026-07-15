---
name: capability-extraction
description: Audit a single service for capabilities it implements locally that don't belong to its domain — capabilities it should be CONSUMING from a centralized party (notification service, audit service, PDF service, file-upload service, feature-flag service, scheduling service, etc.). Produces a "shopping list" of centralized services this service NEEDS, with consumer-contract expectations and coupling-smell evidence. Out of scope: how the centralized service is built, which vendors it uses. Triggered when the user says "what should this service NOT own", "what centralized services does X need", "audit this service for dependencies it should declare", or "what doesn't belong in this service".
---

# capability-extraction

## The core reframe

A payments service is a payments service. It shouldn't be a notification service. It shouldn't be an audit service. It shouldn't be a PDF service. It should **depend on** those.

The goal is NOT to "extract" (that's the provider team's word — they build the centralized service). The goal is to identify **the dependencies this service should declare on centralized parties** so it can focus on its actual domain.

## Explicitly out of scope

This skill produces the **consumer's ask**. It does NOT design the provider:
- How the centralized notification service is built internally
- Which SMS / email / push vendor(s) it uses
- Whether it should be Kafka-based or REST-based (that's the provider's call, informed by all consumers)
- Team ownership of the new centralized service
- Cost/vendor negotiations

Those are downstream conversations owned by whoever builds the centralized service later. This skill just tells you: "here is what this specific service needs from that party."

## When to use

- User says: "what should this service NOT own?", "what centralized services does X need?", "audit this service for centralization opportunities", "what doesn't belong in this service"
- New service scoping — what dependencies should it declare from day one
- Post-incident: "the outage was caused by [notification code] failing in [payments] — should we own that here?"
- Quarterly architecture review of a specific service

## The argument

- **Required**: `service` — the single service (repo path or directory) to audit
- **Optional**: `capabilities` — restrict the audit to specific capabilities (default: sweep all canonical ones)

Canonical capabilities the skill knows how to detect:
- `notifications` (email, SMS, push, WhatsApp)
- `pdf-generation` (invoices, statements, tickets)
- `file-upload` (storage abstraction)
- `audit-log` (activity records, compliance trails)
- `feature-flags` (rollout gates)
- `scheduling` (crons, delayed jobs)

User-defined capabilities: ask for grep patterns; do NOT guess.

## Steps

### 1. Establish this service's domain (one sentence)
Read the top of `README.md`, the top-level directory names, and the main service class/module. Write ONE sentence: **"This service's real job is: X."**

Example: "This service's real job is to accept payment attempts, route them to PGs, reconcile responses, and settle merchants."

This sentence anchors every recommendation. If a capability doesn't serve this sentence, it's a candidate to delegate.

### 2. Sweep for capability signals within this service ONLY
For each capability (or the subset the user specified), grep the service using the detection tables below. Every hit is `path:line`.

Do NOT compare across services. This is a single-service audit.

### 3. For each capability with hits, produce the case
Each capability case has FIVE fields:

| Field | Content |
|---|---|
| **What's here now** | file:line inventory + which providers are in use |
| **Coupling smells** | in-transaction, request-blocking, no-idempotency, no-retry, inconsistent-consent, etc. |
| **Why it doesn't fit the domain** | one sentence tied back to step 1 |
| **What this service needs from a centralized party** | consumer-facing API surface — what would replace the local code |
| **Impact of delegating** | lines removed, coupling unblocked, dependencies dropped |

### 4. Rank
Order the capabilities by **value of delegating**, roughly = (coupling severity × frequency × domain-mismatch). Highest-value first.

### 5. Produce the shopping list
Output template below. The list is what the service team hands to architecture / platform / the team that will own the centralized service.

---

## Detection tables

Same as before — grep patterns per canonical capability. The tables tell you WHAT to look for; the reframe is that you're auditing ONE service, not comparing across many.

### notifications
| Signal | Patterns to grep |
|---|---|
| Provider SDKs | `boto3.client\('ses'\|'sns'\)`, `smtplib`, `sendgrid`, `twilio\.rest`, `msg91`, `karix`, `firebase_admin.messaging`, `nodemailer`, `whatsapp_business` |
| Direct-send calls | `send_email`, `send_sms`, `send_otp`, `send_notification`, `sendMessage`, `.send_transactional` |
| Template rendering | `render_to_string`, `Template\(`, `render_template`, HTML strings near a send |
| Retry wrapping | `for.*attempt`, `retry\(`, `tenacity`, `backoff`, `sleep.*attempt` around a send |
| Opt-out check | `unsubscribed`, `opted_out`, `consent`, `preferences` near a send |
| Coupling smell | send inside `atomic\|transaction\|@transaction`, or in a request handler with no `.delay\(\)\|enqueue` |

### pdf-generation
| Signal | Patterns to grep |
|---|---|
| Libs | `wkhtmltopdf`, `pdfkit`, `weasyprint`, `reportlab`, `puppeteer`, `chromium`, `pdf-lib`, `iText` |
| Direct calls | `.generate_pdf`, `to_pdf`, `render_pdf`, `page\.pdf\(` |
| Templates + temp files | HTML template loaded, then `NamedTemporaryFile`, `mktemp`, `/tmp/.*\.pdf`, then upload |
| Coupling smell | PDF gen in request handler (blocking CPU); PDF gen in DB transaction |

### file-upload
| Signal | Patterns to grep |
|---|---|
| Storage SDKs | `boto3\.client\('s3'\)`, `google\.cloud\.storage`, `azure\.storage\.blob`, `cloudinary`, `MinioClient` |
| MIME / size validation | `content_type`, `mimetypes`, `python-magic`, extension allowlists |
| Signed URL logic | `generate_presigned_url`, `getSignedUrl` with hardcoded expiries |
| Coupling smell | upload in request handler; missing size cap; missing content-type validation |

### audit-log
| Signal | Patterns to grep |
|---|---|
| Direct writes | `AuditLog\.create`, `db\.insert.*audit`, `.log_action`, `record_activity` |
| Ad-hoc field naming | `user_id` vs `actor_id` vs `who` used inconsistently across the same service |
| Same-transaction | audit insert inside same DB transaction as business write |
| Coupling smell | audit write inside a transaction; audit failure would roll back business write |

### feature-flags
| Signal | Patterns to grep |
|---|---|
| SaaS SDKs | `launchdarkly`, `unleash`, `growthbook`, `statsig`, `split\.io`, `flagsmith` |
| Home-grown | `is_enabled\(`, `feature_flag\(`, `Feature\.`, config-file-based flags |
| Env-var flags | `os\.environ\.get\(.*FLAG` |
| Hardcoded percentages | `random\(\) < 0\.1`, `user_id % 10 == 0` |
| Coupling smell | flag decision inside a hot loop with no caching; multiple flag systems in one service |

### scheduling
| Signal | Patterns to grep |
|---|---|
| Libs | `celery.*beat`, `sidekiq.*scheduler`, `apscheduler`, `node-cron`, `bull.*repeat`, `@Scheduled`, `airflow\.DAG` |
| Cron in code + k8s | crontab strings in source AND in `k8s/*.yaml` for the same service |
| Ad-hoc timers | `setInterval\(`, `while True.*sleep`, `Thread.*sleep.*loop` |
| Coupling smell | scheduled job with no leader election on a multi-replica deployment |

---

## Writing the "consumer's ask" (step 3, field 4)

This is the most important field. Frame from THIS service's perspective — what API surface does this service want to call?

Use the shape below. Do NOT specify transport (Kafka vs REST vs gRPC) — that's the provider's decision informed by all consumers, not this service's ask.

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

---

## Output — the shopping list

```markdown
# Capability audit — <service name>

**Scanned at**: <UTC>
**Service**: <path>
**This service's real job**: <one sentence — the domain statement>

## Summary
This service currently owns N capabilities that don't fit its domain. Ranked by value of delegating:

1. <capability> — <coupling severity> · <hit count>
2. <capability> — ...
3. ...

Delegating these to centralized parties would remove ~X lines of code and unblock Y coupling smells.

## Shopping list

### 1. Needs: centralized `notification-service`

**What's here now**
- 12 sites; providers: SES (7), msg91 (3), Twilio (2)
- Sample: `payments/tasks.py:142`, `webhooks/pg_callback.py:88`, `otp/views.py:45`, ...

**Coupling smells**
- CRITICAL: `payments/tasks.py:142` — `ses.send_email` runs inside `transaction.atomic()` around the payment write. SMTP timeout → payment commit fails → user charged, no record.
- HIGH: 5 sites have their own retry loops with different backoff (2 exponential, 2 fixed, 1 none).
- HIGH: opt-out check present in 4 sites, MISSING in 8 (regulatory: DPDPA / TRAI DND exposure).
- MEDIUM: 4 different template-rendering approaches within this one service.

**Why it doesn't fit the domain**
Payments' job is to process transactions and settle merchants. Emitting communications is a separate concern; owning it here couples payment atomicity to SMTP/SMS availability.

**What this service needs (consumer's ask)**

As a consumer, `<service>` needs to:
- `publish_notification(template_id, recipient_ref, variables, priority)` — fire-and-forget, for confirmations, receipts, status updates
- `send_otp_sync(recipient, template_id, variables) → { delivered, message_id }` — sync with response, for OTP flows where the user is blocked on the screen (timeout ≤3s, we'll fall back to SMS if primary channel fails)

Delivery semantics:
- Async default for all transactional confirmations
- Sync only for OTP

Guarantees needed:
- Idempotency on `idempotency_key` we supply (`{service}:{entity_id}:{action}`) — we WILL retry on unclear failures
- Ordering per `recipient_ref.user_id` — a user's payment-success email must not arrive before their payment-initiated email
- SLA: transactional publish → delivered within 30s p95

Data we would send:
` ` `json
{
  "template_id": "payment_success",
  "recipient_ref": { "user_id": "..." },
  "channel_preference": ["email", "sms"],
  "variables": { "amount": 12500, "order_id": "...", "merchant_name": "..." },
  "priority": "high"
}
` ` `

What we do NOT need this party to do:
- Manage user consent / opt-out (consent should live in a separate identity/consent service; the notification service consults it)
- Render locale-specific copy — we'll pass a template_id and let the service resolve
- Handle marketing bulk-blasts — different SLA, different consent model, separate concern

**Impact of delegating**
- Removes ~600 lines from this service (retry loops, template rendering, provider adapters)
- Drops direct dependencies: `boto3-ses`, `msg91-python`, `twilio`
- Unblocks the CRITICAL coupling in `payments/tasks.py:142` — payment atomicity no longer coupled to SMTP
- Eliminates the DPDPA/DND consent inconsistency (consent lives in the notification service, not scattered here)

---

### 2. Needs: centralized `audit-service`

**What's here now**
- 28 sites; direct writes to a local `audit_log` table via `AuditLog.create(...)`
- Field naming inconsistent: `user_id` (18 sites), `actor_id` (7 sites), `who` (3 sites)

**Coupling smells**
- 14 sites write audit rows INSIDE the same `transaction.atomic()` as the business write — audit failure would roll back the payment
- Zero sites include a `request_id` for cross-service correlation
- Compliance auditors currently can't answer "who did X in the last 90 days across all services" without joining across N per-service audit tables

**Why it doesn't fit the domain**
Payments should record its business writes. Building an org-wide compliance/audit trail is not payments' problem — it's a compliance concern that needs a uniform schema across every service.

**What this service needs (consumer's ask)**

As a consumer, `<service>` needs to:
- `record_audit_event(actor, action, target, changes, request_id)` — async, fire-and-forget

Delivery semantics:
- Async only
- At-least-once is fine (audit events dedupe on `event_id` at the provider)

Guarantees needed:
- Durable (audit events cannot be lost — needed for compliance)
- Ordering per `target.id` for reconstruction of change history
- SLA: not latency-sensitive; ≤5min for delivery is fine

Data we would send:
` ` `json
{
  "actor": { "type": "user", "id": "..." },
  "action": "payment.captured",
  "target": { "type": "payment", "id": "..." },
  "changes": { "before": { "status": "pending" }, "after": { "status": "captured" } },
  "request_id": "req_abc",
  "occurred_at": "2026-07-15T10:00:00Z"
}
` ` `

What we do NOT need this party to do:
- Enforce retention policies (compliance team defines those centrally)
- Provide a UI (that's a separate compliance-portal concern)

**Impact of delegating**
- Removes the local `audit_log` table (drops schema, migrations, indexes)
- Removes 14 coupling smells where audit write was in the payment transaction
- Standardizes fields — compliance can now query one place

---

### 3. Needs: centralized `document-service` (PDF generation)
... (same shape)

---

## What this service should keep

Capabilities that DO fit the domain and should stay local:
- Payment routing logic
- PG-response parsing and reconciliation
- Merchant settlement calculations
- Payment-specific retry/idempotency (payments are financial; this is core competence, not cross-cutting)

## What's out of scope for this audit
- How the centralized `notification-service` / `audit-service` / `document-service` are built (their design is their team's problem, informed by ALL consumers, not just this one)
- Vendor selection (SES vs SendGrid, wkhtmltopdf vs Puppeteer, etc.)
- Whether any of these centralized services already exist in some form elsewhere in the org (that's a discovery question for architecture)
- Team ownership of the new centralized services

## Next step
Hand this shopping list to architecture / platform. They'll:
- Check if any of these centralized services already exist
- If not, sequence their creation
- Come back to this service team with the actual provider API to migrate to
```

---

## Rules

- NEVER prescribe the transport / vendor / internal design of the centralized service — that's the provider's job
- NEVER extend the audit across multiple services — this is a SINGLE-service audit
- ALWAYS state this service's domain in one sentence FIRST — it anchors every recommendation
- ALWAYS frame needs from the CONSUMER's perspective — API surface this service wants to call
- ALWAYS separate what this service NEEDS from what it does NOT need the party to do (scope control)
- ALWAYS include impact of delegating (lines removed, coupling unblocked, deps dropped) — makes the case concrete
- ALWAYS include "what this service should keep" — the audit is about scope discipline, not about hollowing out the service
- If the user hasn't told you the service's domain and it's not obvious from README, ASK before writing the audit — a wrong domain statement makes every recommendation wrong
