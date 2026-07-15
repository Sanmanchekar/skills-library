# Capability Extraction Skill — Audit One Service for Dependencies It Should Declare

> **What does this service NOT belong owning?** Audits a single service (e.g. `gq_direct_payments_backend`) for cross-cutting capabilities it implements locally that should be delegated to centralized parties — notifications, audit log, PDF generation, file upload, feature flags, scheduling. Produces a shopping list of centralized services this service NEEDS, with the consumer's ask and coupling-smell evidence. **Out of scope**: how those centralized services get built, which vendors they use.

**Keywords**: service scope audit, single service capability audit, centralized service dependencies, consumer contract design, notification service dependency, audit service dependency, pdf service dependency, service domain focus, coupling smell audit, capability extraction claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- capability-extraction
```

## What it does

- **Service-centric**, not capability-centric — you point at ONE service; the skill tells you which capabilities don't belong there
- Establishes the service's **domain statement** in one sentence first — every recommendation anchors back to it
- Sweeps for **6 canonical capabilities** (notifications, pdf-generation, file-upload, audit-log, feature-flags, scheduling) with per-capability grep tables
- For each capability found, produces a **5-field case**: what's here, coupling smells, why it doesn't fit, consumer's ask, impact of delegating
- **Consumer's ask** = API surface this service wants to CALL — not the provider's design
- Ends with a **"what this service should keep"** section so the audit is scope discipline, not hollowing-out
- Explicitly **out of scope**: transport choice for the centralized service, vendors, team ownership — those are the provider's decisions informed by ALL consumers

## Why this framing

A payments service is a payments service. Notification delivery, compliance auditing, PDF generation, and file storage are not payments' domain. Owning them locally couples payment atomicity to unrelated failure modes (SMTP timeout blocks a payment commit; audit write inside the transaction rolls back the business write).

The skill produces the **consumer's ask** — a concrete statement of "here's what we need from a centralized party." Building that party, choosing vendors, deciding transport — that's a downstream conversation owned by whoever builds it.

## When it triggers

- "What should this service NOT own?"
- "What centralized services does gq_direct_payments_backend need?"
- "Audit this service for dependencies it should declare"
- "What doesn't belong in this service"
- New-service scoping — declaring dependencies from day one
- Post-incident when the root cause was a cross-cutting concern owned locally

## Example shopping list (excerpt)

```
Service: gq_direct_payments_backend
Real job: accept payments, route to PGs, reconcile, settle merchants.

1. Needs: notification-service
   - CRITICAL: payments/tasks.py:142 has ses.send_email inside
     transaction.atomic — SMTP timeout blocks payment commit
   - Consumer's ask: publish_notification(async, fire-and-forget)
                    + send_otp_sync(3s timeout, delivery ack)
   - Impact of delegating: -600 lines, unblocks payment atomicity

2. Needs: audit-service
   - 28 sites; 14 inside payment transactions (rollback risk)
   - Consumer's ask: record_audit_event(async, at-least-once, dedupe)
   - Impact: standardizes fields; drops local audit_log table

3. Needs: document-service (PDF)
   ...

What this service should keep:
   - PG routing, response parsing, settlement calc, payment-idempotency

Out of scope for this audit:
   - How notification-service gets built · vendor choice ·
     whether it already exists elsewhere in the org
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [adr](../adr) — the "we're declaring dependency on X" architecture decision the shopping list feeds into
- [onboarding](../onboarding) — the service's domain statement often surfaces during onboarding
- [refactor](../refactor) — mechanical steps to swap local code for a provider client once the centralized service exists
- [db-migration](../db-migration) — strangler-pattern skill for the DB side of removing local audit_log tables
