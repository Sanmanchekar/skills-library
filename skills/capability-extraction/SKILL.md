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

### 6. Persist to the audited repo + summarize to the terminal
- **Write** `.audit/capability/TODO.md` (mergeable, reconcilable) and `.audit/capability/shopping-list-YYYY-MM-DD.md` (immutable per-run snapshot). See "Persistent artifacts" section below.
- **Print** a dated terminal summary — severity breakdown, top-N by blast radius, diff vs prior run, files-written pointer, next actions. See "Terminal summary" section below.
- On re-runs, MERGE with the existing TODO.md — never clobber user check-offs or team notes.

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

## Persistent artifacts — write to `.audit/capability/`

The shopping list from Step 5 is the diagnosis. To make it actionable and reconcilable across re-runs, write TWO files into the audited repo:

```
<service-repo>/
└── .audit/
    └── capability/
        ├── TODO.md                              # canonical, mergeable, human-editable
        └── shopping-list-YYYY-MM-DD.md          # per-run snapshot, immutable
```

Both files SHOULD be **committed to git** — the migration plan is a first-class repo artifact, not scratch. `.audit/` is a shared namespace for audit outputs (this skill owns `capability/`; future audit skills may write to `.audit/security/`, `.audit/dependency/`, etc.).

### Behavior modes

- **Default** — write both files
- **`dry-run`** — print the terminal summary + shopping list, do NOT touch the filesystem. For preview before commit.
- **`regen-contract`** — re-derive the Consumer Contract sections from the fresh scan, overwriting user edits (default: preserve user-edited contracts)
- **`no-history`** — skip appending to the Audit history table (useful for CI / test runs)

If the user hasn't specified a mode, default to normal write.

### TODO.md schema

Human-editable AND machine-parseable. HTML comment markers anchor reconciliation.

```markdown
# Capability audit — TODO
<!-- capability-audit v1 -->
<!-- service: <service-name> -->
<!-- audit_run: <N> -->
<!-- last_audited_at: <UTC ISO 8601> -->
<!-- domain_statement: <one-sentence service purpose> -->

## Capability: notifications
<!-- capability_id: notifications -->
<!-- status: open -->
<!-- call_sites: <N> · providers: <list> -->
<!-- coupling: CRITICAL (<n>) · HIGH (<n>) · MEDIUM (<n>) · LOW (<n>) -->

### Migration todos
- [ ] `cap-notif-001` 🔴 **CRITICAL** — Move `ses.send_email` out of `transaction.atomic` at `payments/tasks.py:142` (SMTP timeout blocks payment commit)
- [ ] `cap-notif-002` 🟠 HIGH — Standardize opt-out check at `campaigns/emails.py:88` (currently missing — DPDPA risk)
- [x] `cap-notif-003` 🟠 HIGH — [resolved 2026-07-10 @alice] Retry loop at `refunds/tasks.py:12` normalized
- [ ] `cap-notif-004` 🟡 MEDIUM — Migrate `orders/notify.py:31` to `publish_notification(...)`

### Consumer contract
<!-- contract-start -->
_(preserved verbatim across re-runs unless `regen-contract` mode)_

- `publish_notification(...)` — async, fire-and-forget
- `send_otp_sync(...)` — sync, 3s timeout, delivery ack
- Delivery semantics: idempotent on our `idempotency_key`, ordered per `user_id`, 30s p95 SLA
- What we do NOT need this party to do: consent management, locale rendering, marketing bulk-blasts
<!-- contract-end -->

### Team notes
<!-- notes-start -->
_(preserved across re-runs — add decisions, deferrals, dependencies here)_
<!-- notes-end -->

---

## Capabilities kept local (out of scope for delegation)
<!-- kept-local-start -->
- Payment routing logic
- PG-response parsing
- Merchant settlement calculations
- Payment idempotency (financial — core competence, not cross-cutting)
<!-- kept-local-end -->

## Audit history
| Run | Date | Findings | Open | Resolved | Δ vs prior |
|---|---|---|---|---|---|
| 1 | 2026-07-08 | 47 | 47 | 0 | initial audit |
| 2 | 2026-07-12 | 51 | 46 | 3 | +4 new (webhooks/), −3 auto-resolved |
| 3 | 2026-07-15 | 49 | 43 | 6 | −2 auto-resolved (revenue_backend migrated) |
```

### Todo item format (stable, parseable, sortable)

```
- [ ] `cap-<capability>-<NNN>` <emoji> **<SEVERITY>** — <verb + file:line + why>
```

- **`cap-<capability>-<NNN>`** — stable id, zero-padded 3 digits, survives re-runs. `cap-notif-001` for the first notification finding; `cap-audit-013` for the 13th audit finding. Never re-use a retracted id — always monotonic per capability.
- **Severity emoji + word** — 🔴 CRITICAL · 🟠 HIGH · 🟡 MEDIUM · 🟢 LOW
- **Verb-first title** — Move / Migrate / Delete / Standardize / Extract — NEVER "look at" or "consider"
- **`file:line`** in backticks — reviewer can jump straight to it
- **Why in parens** — the specific coupling smell or duplication signal

### Reconciliation on re-run (the crux)

Before writing a new TODO.md, PARSE the existing one (if present). Extract every item's id, `[ ]`/`[x]` state, any inline tags (`#wontfix`), and preserved sections. Then apply this table per finding:

| Existing state | Fresh scan finding | Action |
|---|---|---|
| absent | new site found | add as `- [ ]` new item with next available `cap-<cap>-NNN` id |
| `[ ]` open | site still exists | keep verbatim (including user edits to description) |
| `[ ]` open | site GONE | flip to `[x]` with note `[auto-resolved YYYY-MM-DD — call site no longer present]` |
| `[x]` done | site GONE | keep as done, no change |
| `[x]` done | site STILL PRESENT | flag as ⚠️ **regression**: flip back to `[ ]`, prepend `⚠️ regressed — was marked done but call site reappeared` |
| `[x]` done with `#wontfix` | either | preserve verbatim — user's explicit decision |

Other reconciliation rules:

- **Team notes** — content between `<!-- notes-start -->` and `<!-- notes-end -->` is copied VERBATIM. Never modified.
- **Consumer contract** — content between `<!-- contract-start -->` and `<!-- contract-end -->` is preserved verbatim unless `regen-contract` mode was requested.
- **Kept-local block** — content between `<!-- kept-local-start -->` and `<!-- kept-local-end -->` is preserved (users may edit); appended to only if the fresh scan surfaces a new domain-fit capability.
- **Audit history** — append a new row per run with: run number, date, total findings, open count, resolved count, one-line Δ vs prior run. Never rewrite prior rows.
- **Todo ids** — monotonic per capability. If `cap-notif-003` was retracted (call site gone before ever being marked done), the NEXT new notification finding gets `cap-notif-004`, not `cap-notif-003`. Ids are never re-used.

### Per-run snapshot: `shopping-list-YYYY-MM-DD.md`

The full evidence packet from Step 5, exactly as it existed at that run. **Immutable — never modified.** Multiple snapshots accumulate over time. Filename includes the audit date. Filename format:

```
shopping-list-2026-07-15.md
shopping-list-2026-07-22.md
shopping-list-2026-08-01.md
```

If two audits happen on the same date, suffix with `-run<N>`: `shopping-list-2026-07-15-run2.md`.

Rationale: `git diff` on `TODO.md` shows what changed since the last commit, but the shopping-list snapshots let a reader see the FULL evidence as it stood at any past run, without needing to `git checkout` a prior commit.

---

## Terminal summary

In addition to writing files, PRINT a dated, structured summary to the terminal so the human sees the diagnosis + trend + next actions at a glance. The terminal is the fast dashboard; the files are the actionable ledger.

### Format

```
╭─ Capability audit — <service-name> ─────────────────────────────────╮
│  Run #<N> · <UTC timestamp> · <actor>                               │
│  Domain: <one-sentence domain statement>                            │
╰──────────────────────────────────────────────────────────────────────╯

Summary
  <N> capabilities recommended for delegation
  <N> total findings · <N> open · <N> resolved · <N> wontfix
  Δ vs Run #<N-1>: <one-line diff>

By capability
  🔴 <n>  🟠 <n>  🟡 <n>  🟢 <n>   <capability>   <N> sites → <N> open   → <recommended-service>
  ...

Top 5 by blast radius
  <emoji> <cap-id>   <file:line>   <one-line coupling smell>
  ...

Recent runs (last 3)
  #<N>    today       <findings>  <open>  <resolved>  (<diff summary>)
  #<N-1>  <days> ago  <findings>  <open>  <resolved>  (<diff summary>)
  #<N-2>  <days> ago  <findings>  <open>  <resolved>  (<diff summary>)

Regressions (was done, back to open)
  ⚠️ <cap-id>  <file:line>  <one-line why>
  ...
  (omit this whole block if no regressions this run)

Files written
  .audit/capability/TODO.md                     (updated: +<N> new, −<N> auto-resolved, <N> regression)
  .audit/capability/shopping-list-<date>.md     (new snapshot)
  (In dry-run mode: "Would write" instead of "Files written")

Next
  1. Review .audit/capability/TODO.md
  2. Prioritize <top CRITICAL id> (<severity>) this sprint
  3. Hand the <capability>-service consumer contract to <owner> for scoping
```

### Width-adaptive rendering

- If terminal is < 100 cols: drop the box-drawing header, use `===` separators instead
- If terminal is < 80 cols: drop the emoji-count row in "By capability", keep only the count line
- If output is being piped (`| grep`, `| less`, non-TTY): drop all ANSI colors, use plain text; box-drawing chars are safe (they're just Unicode)

### Marriage between terminal + TODO.md + snapshots

The **todo id** (`cap-notif-001`) is the join key. Every axis is kept consistent across all three surfaces:

| Property | Terminal | TODO.md | shopping-list-*.md |
|---|---|---|---|
| Run number | `Run #3` header | `<!-- audit_run: 3 -->` marker | Referenced in the snapshot body |
| Timestamp | UTC in header | `<!-- last_audited_at: ... -->` | Filename date |
| Todo IDs | Shown in Top-N + Regressions | Each item labeled `cap-notif-001` | Referenced in the recommendation body |
| Severity emojis | 🔴🟠🟡🟢 | Same on every item | Same in coupling breakdown |
| Capability slug | `notifications` | Heading `## Capability: notifications` | Same slug |
| Domain statement | Header | `<!-- domain_statement: ... -->` | First paragraph |

The user's workflow this enables:

1. Run skill → terminal shows severity + top 5 + trend
2. Copy an ID like `cap-notif-001` → open `.audit/capability/TODO.md`, search the ID → see full context + suggested action
3. Migrate the call site → check `[x]` in the TODO
4. Commit the code fix + the TODO edit in the SAME PR → reviewer sees both
5. Re-run next sprint → terminal shows `−1 auto-resolved`, prior work preserved
6. Need the exact evidence packet from 3 weeks ago? → open `.audit/capability/shopping-list-2026-06-25.md`

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

### Persistence rules

- ALWAYS write `.audit/capability/TODO.md` and `.audit/capability/shopping-list-<date>.md` unless the user requested `dry-run`
- ALWAYS reconcile with existing TODO.md — never clobber user check-offs, tags (`#wontfix`), or team notes
- NEVER modify content between `<!-- notes-start -->` and `<!-- notes-end -->`
- NEVER modify content between `<!-- contract-start -->` and `<!-- contract-end -->` unless `regen-contract` mode was requested
- NEVER re-use a retracted todo id — monotonic per capability
- ALWAYS append a new row to the Audit history table (unless `no-history` mode)
- ALWAYS use the SAME todo IDs / emojis / capability slugs / run number in the terminal, TODO.md, and shopping-list snapshot — no divergence
- If `.audit/capability/` doesn't exist, create it. Suggest the team commit it — this is the migration source of truth, not scratch state.

### Terminal-summary rules

- ALWAYS start the terminal output with a UTC-timestamped header including run number, actor, and the domain statement
- ALWAYS show the diff vs prior run when a prior run exists (`Δ vs Run #N`)
- ALWAYS surface regressions (⚠️) as their own block when present — they matter more than raw open counts
- ALWAYS end with the "Files written" block so the user knows where the details live
- ALWAYS end with a "Next" block naming the highest-severity open item by id
- If output is being piped or the terminal is narrow, use the width-adaptive fallbacks — never print box-drawing that will visually break on 60-col terminals
