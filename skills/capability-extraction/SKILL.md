---
name: capability-extraction
description: Audit a single service for cross-cutting BEHAVIORS it implements locally that don't belong to its domain — notifications, PDF generation, file upload, audit log, feature flags, scheduling — capabilities it should be CONSUMING from a centralized party. Produces a "shopping list" of centralized services with consumer-contract expectations, plus a mergeable `.audit/capability/TODO.md` and dated terminal summary. NOT for data/table ownership questions — for those, use the `db-scoping` skill. Out of scope: how the centralized service is built, which vendors it uses. Triggered when the user says "what BEHAVIORS should this service NOT own", "what centralized services does X need", "audit this service for cross-cutting dependencies it should declare", or "what shared services does X consume".
---

# capability-extraction

## Which audit skill to use

Two audits look similar; they answer different questions. Pick correctly:

| If the question is about... | Use |
|---|---|
| **Behaviors / cross-cutting services** (sending notifications, generating PDFs, uploading files, writing audit logs, feature-flag reads, cron/scheduled jobs) | **capability-extraction** (this skill) |
| **Data / tables / DB ownership** (which tables this service reads/writes, cross-domain foreign-table access, bounded-context violations at the data layer) | **db-scoping** |

If someone says "audit this service" without specifying, ASK — do they mean behavioral capabilities or data ownership.

## The core reframe

A payments service is a payments service. It shouldn't be a notification service. It shouldn't be an audit-log service. It shouldn't be a PDF service. It should **depend on** those.

The goal is NOT to "extract" (that's the provider team's word — they build the centralized service). The goal is to identify **the dependencies this service should declare on centralized parties** so it can focus on its actual domain.

## Explicitly out of scope

This skill produces the **consumer's ask**. It does NOT design the provider:
- How the centralized service is built internally
- Which vendor(s) it uses
- Transport (Kafka vs REST vs gRPC) — that's the provider's call informed by all consumers
- Team ownership of the new centralized service
- Cost/vendor negotiations

## When to use

- User says: "what should this service NOT own (behaviorally)?", "what centralized services does X consume?", "audit for cross-cutting dependencies", "what behaviors don't belong in this service"
- New service scoping — what dependencies should it declare from day one
- Post-incident: "the outage was caused by [notification code] failing in [payments] — should we own that here?"
- Quarterly architecture review of a specific service's behavioral scope

## The argument

- **Required**: `service` — the single service (repo path or directory) to audit
- **Optional**: `capabilities` — restrict the audit to specific capabilities (default: sweep all canonical ones)
- **Optional**: `mode` — `dry-run` / `regen-contract` / `no-history` (see references/reconciliation.md)

**Canonical capabilities** (with detection tables in `references/detection-tables.md`):
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

This sentence anchors every recommendation. If a capability doesn't serve this sentence, it's a candidate to delegate.

If the domain isn't obvious and the user hasn't told you, ASK before continuing.

### 2. Sweep for capability signals within this service ONLY
Read **`references/detection-tables.md`** for grep patterns per capability. Record every hit as `path:line`.

This is a SINGLE-service audit — do NOT compare across services.

### 3. For each capability with hits, produce the case
Each capability case has FIVE fields:

| Field | Content |
|---|---|
| **What's here now** | file:line inventory + which providers are in use |
| **Coupling smells** | in-transaction, request-blocking, no-idempotency, no-retry, inconsistent-consent, etc. |
| **Why it doesn't fit the domain** | one sentence tied back to step 1 |
| **What this service needs from a centralized party** | consumer-facing API surface (see `references/consumer-ask.md`) |
| **Impact of delegating** | lines removed, coupling unblocked, dependencies dropped |

### 4. Rank
Order the capabilities by **value of delegating**, roughly = (coupling severity × frequency × domain-mismatch). Highest-value first.

### 5. Produce the shopping list
Use **`references/shopping-list-template.md`** as the output body. This is what the service team hands to architecture / platform / the team that will own the centralized service.

### 6. Persist to the audited repo + summarize to the terminal
- **Write** `.audit/capability/TODO.md` (mergeable, reconcilable — schema in `references/todo-schema.md`) and `.audit/capability/shopping-list-YYYY-MM-DD.md` (the shopping list from Step 5, immutable snapshot)
- **Print** a dated terminal summary — format in `references/terminal-summary.md`
- On re-runs, MERGE with the existing TODO.md — never clobber. Follow the 6-case table in `references/reconciliation.md`
- Skip file writes if the user requested `dry-run` mode

## Rules

- NEVER prescribe the transport / vendor / internal design of the centralized service — that's the provider's job
- NEVER extend the audit across multiple services — this is a SINGLE-service audit
- NEVER audit data/table ownership here — that's `db-scoping`'s job
- ALWAYS state this service's domain in one sentence FIRST — it anchors every recommendation
- ALWAYS frame needs from the CONSUMER's perspective — API surface this service wants to call
- ALWAYS separate what this service NEEDS from what it does NOT need the party to do (scope control)
- ALWAYS include impact of delegating (lines removed, coupling unblocked, deps dropped) — makes the case concrete
- ALWAYS include "what this service should keep" — the audit is about scope discipline, not hollowing-out
- If the user hasn't told you the service's domain and it's not obvious from README, ASK before writing the audit — a wrong domain statement makes every recommendation wrong

### Persistence rules

- ALWAYS write `.audit/capability/TODO.md` and `.audit/capability/shopping-list-<date>.md` unless the user requested `dry-run`
- ALWAYS reconcile with existing TODO.md — never clobber user check-offs, tags (`#wontfix`), or team notes
- NEVER modify content between `<!-- notes-start -->` and `<!-- notes-end -->`
- NEVER modify content between `<!-- contract-start -->` and `<!-- contract-end -->` unless `regen-contract` mode was requested
- NEVER re-use a retracted todo id — monotonic per capability
- ALWAYS append a new row to the Audit history table (unless `no-history` mode)
- ALWAYS use the SAME todo IDs / emojis / capability slugs / run number in the terminal, TODO.md, and shopping-list snapshot — no divergence
- If `.audit/capability/` doesn't exist, create it. Suggest the team commit it — this is the migration source of truth.

### Machine-readable state rules

- ALWAYS append the fenced JSON state block to the bottom of TODO.md (schema in `references/todo-schema.md`)
- ALWAYS regenerate the JSON on every run
- ALWAYS use the fixed status enums (item: `open`/`resolved`/`wontfix`/`retracted`/`regressed`; capability: `open`/`in-progress`/`delegated`/`not-applicable`; severity: `critical`/`high`/`medium`/`low`)
- JSON is canonical for prior-run values; markdown wins for latest human toggle
- If JSON is malformed, fall back to markdown parse with a `⚠️` warning line in the terminal summary
- NEVER prompt the user to edit JSON — the markdown IS the human interface

### Terminal-summary rules

- ALWAYS start the terminal output with a UTC-timestamped header including run number, actor, and the domain statement
- ALWAYS show the diff vs prior run when a prior run exists
- ALWAYS surface regressions (⚠️) as their own block when present
- ALWAYS end with "Files written" and "Next" blocks
- Width-adaptive fallbacks per `references/terminal-summary.md`

## References (load on demand)

- `references/detection-tables.md` — grep patterns per capability (Step 2)
- `references/consumer-ask.md` — template for the consumer's API-surface statement (Step 3, field 4)
- `references/shopping-list-template.md` — full evidence-packet body (Step 5)
- `references/todo-schema.md` — TODO.md structure + JSON state block schema (Step 6)
- `references/reconciliation.md` — 6-case merge table + preservation rules for re-runs (Step 6)
- `references/terminal-summary.md` — dated summary format + width-adaptive rules (Step 6)
