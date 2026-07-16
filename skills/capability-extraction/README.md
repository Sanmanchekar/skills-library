# Capability Extraction Skill — Audit One Service for Dependencies It Should Declare

> **What does this service NOT belong owning?** Audits a single service (e.g. `gq_direct_payments_backend`) for cross-cutting capabilities it implements locally that should be delegated to centralized parties — notifications, audit log, PDF generation, file upload, feature flags, scheduling. Produces a shopping list of centralized services this service NEEDS, plus a **mergeable TODO.md checked into `.audit/capability/`** and a **dated terminal summary** so migration progress is trackable across re-runs. **Out of scope**: how those centralized services get built, which vendors they use.

**Keywords**: service scope audit, single service capability audit, centralized service dependencies, consumer contract design, notification service dependency, audit service dependency, pdf service dependency, service domain focus, coupling smell audit, migration checklist generator, dated audit report, reconcilable todo list, git-tracked audit trail, strangler-pattern tracker, capability extraction claude code skill

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
- **Writes two files** into the audited repo (see "Persistent output" below): a mergeable `TODO.md` you check items off in PRs and a per-run immutable `shopping-list-YYYY-MM-DD.md` snapshot
- **Prints a dated terminal summary** — severity breakdown, top-N by blast radius, diff vs prior run, files-written pointer, next actions
- **Reconciles across re-runs** — preserves check-offs, team notes, `#wontfix` tags; detects regressions (was done, back to open); auto-resolves items whose call sites are gone
- Ends with a **"what this service should keep"** section so the audit is scope discipline, not hollowing-out
- Explicitly **out of scope**: transport choice for the centralized service, vendors, team ownership — those are the provider's decisions informed by ALL consumers

## Persistent output (writes to the audited repo)

Two files under `.audit/capability/`:

```
<service-repo>/
└── .audit/
    └── capability/
        ├── TODO.md                              # canonical, mergeable, human-editable
        └── shopping-list-YYYY-MM-DD.md          # per-run snapshot, immutable
```

**Why `.audit/`?** Dotfolder = tool-generated meta artifacts (same convention as `.github/`, `.cursor/`). Namespaced so future audit skills (security-review, dependency-upgrade, etc.) can write to `.audit/security/`, `.audit/dependency/` and stay tidy. Doesn't collide with `docs/` (which most repos overload with mixed content).

**Commit it.** The TODO is the migration source of truth — teammates check items off in PRs, reviewers see the diff, `git blame` shows who resolved what and when.

### TODO.md structure

Human-editable with checkboxes; machine-parseable via HTML comment markers:

```markdown
# Capability audit — TODO
<!-- capability-audit v1 -->
<!-- service: gq_direct_payments_backend -->
<!-- audit_run: 3 -->
<!-- last_audited_at: 2026-07-15T14:30:00Z -->

## Capability: notifications
<!-- capability_id: notifications -->

### Migration todos
- [ ] `cap-notif-001` 🔴 **CRITICAL** — Move `ses.send_email` out of `transaction.atomic` at `payments/tasks.py:142` (SMTP timeout blocks payment commit)
- [ ] `cap-notif-002` 🟠 HIGH — Standardize opt-out check at `campaigns/emails.py:88` (missing — DPDPA risk)
- [x] `cap-notif-003` 🟠 HIGH — [resolved 2026-07-10 @alice] Retry loop at `refunds/tasks.py:12` normalized

### Consumer contract
<!-- contract-start -->
- publish_notification(...) — async, fire-and-forget
- send_otp_sync(...) — sync, 3s timeout
- ...
<!-- contract-end -->

### Team notes
<!-- notes-start -->
(preserved verbatim across re-runs)
<!-- notes-end -->

## Audit history
| Run | Date | Findings | Open | Resolved | Δ vs prior |
|---|---|---|---|---|---|
| 1 | 2026-07-08 | 47 | 47 | 0 | initial |
| 2 | 2026-07-12 | 51 | 46 | 3 | +4 new, −3 auto-resolved |
| 3 | 2026-07-15 | 49 | 43 | 6 | −2 auto-resolved (revenue_backend migrated) |
```

### Reconciliation across re-runs — safe to re-run any time

| Prior state | New scan | Action |
|---|---|---|
| absent | new site | new `[ ]` item added |
| `[ ]` open | still there | kept verbatim |
| `[ ]` open | site gone | auto-flipped to `[x]` with resolution date |
| `[x]` done | site gone | kept as done |
| `[x]` done | site returned | ⚠️ regression flagged |
| user-tagged `#wontfix` | either | preserved verbatim |

Team notes (`<!-- notes-start -->`), consumer contract (`<!-- contract-start -->`), and kept-local section are preserved verbatim. Pass `regen-contract` mode to force re-derivation of contracts.

## Terminal summary (dated, on every run)

```
╭─ Capability audit — gq_direct_payments_backend ─────────────────────╮
│  Run #3 · 2026-07-15 14:30 UTC · Sanmanchekar                       │
│  Domain: process payment transactions, route to PGs, settle merchants│
╰──────────────────────────────────────────────────────────────────────╯

Summary
  3 capabilities recommended for delegation
  49 total findings · 43 open · 6 resolved · 0 wontfix
  Δ vs Run #2: −2 auto-resolved (revenue_backend migrated) · +4 new

By capability
  🔴 1  🟠 5  🟡 4  🟢 2   notifications     12 sites → 8 open   → notification-service
  🔴 0  🟠 14 🟡 10 🟢 4   audit-log         28 sites → 26 open  → audit-service
  🔴 0  🟠 1  🟡 2  🟢 0   pdf-generation    3 sites → 3 open    → document-service

Top 5 by blast radius
  🔴 cap-notif-001   payments/tasks.py:142      SMTP timeout blocks payment commit
  🟠 cap-audit-004   webhooks/pg.py:88          audit write inside payment transaction
  🟠 cap-notif-002   campaigns/emails.py:88     missing opt-out (DPDPA)
  ...

Regressions (was done, back to open)
  ⚠️ cap-notif-007  orders/notify.py:31  fix reverted in commit abc123

Files written
  .audit/capability/TODO.md                     (updated: +4 new, −2 auto-resolved, 1 regression)
  .audit/capability/shopping-list-2026-07-15.md (new snapshot)

Next
  1. Review .audit/capability/TODO.md
  2. Prioritize cap-notif-001 (CRITICAL) this sprint
  3. Hand the notification-service consumer contract to @platform for scoping
```

**Terminal and TODO.md share the same todo IDs** (`cap-notif-001`), severity emojis (🔴🟠🟡🟢), capability slugs, and run number — copy any ID from the terminal, ⌘F in the TODO.md, jump to full context.

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
