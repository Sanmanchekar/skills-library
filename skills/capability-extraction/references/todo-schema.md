# TODO.md schema + JSON state block

Read this file when Step 6 needs to write `.audit/capability/TODO.md` — either fresh or reconciled with an existing file.

## File layout

```
<service-repo>/
└── .audit/
    └── capability/
        ├── TODO.md                              # canonical, mergeable, human-editable
        └── shopping-list-YYYY-MM-DD.md          # per-run snapshot, immutable (uses references/shopping-list-template.md)
```

`.audit/` is a shared namespace for audit outputs. Suggest the team commit `.audit/` to git — this is the migration source of truth.

## TODO.md structure

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
- PG-response parsing and reconciliation
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

## Todo item format (stable, parseable, sortable)

```
- [ ] `cap-<capability>-<NNN>` <emoji> **<SEVERITY>** — <verb + file:line + why>
```

- **`cap-<capability>-<NNN>`** — stable id, zero-padded 3 digits, survives re-runs. `cap-notif-001` for the first notification finding; `cap-audit-013` for the 13th audit finding. Never re-use a retracted id — always monotonic per capability.
- **Severity emoji + word** — 🔴 CRITICAL · 🟠 HIGH · 🟡 MEDIUM · 🟢 LOW
- **Verb-first title** — Move / Migrate / Delete / Standardize / Extract — NEVER "look at" or "consider"
- **`file:line`** in backticks — reviewer can jump straight to it
- **Why in parens** — the specific coupling smell or duplication signal

## Machine-readable state block (canonical for LLMs / tools)

Append a fenced JSON state block at the bottom of TODO.md, hidden inside `<details>`. **JSON is canonical** for prior-run values; **markdown checkboxes** are the human interface and win for the latest human toggle.

```markdown
---

<details>
<summary>Machine-readable state (regenerated on each run — do not edit)</summary>

<!-- capability-audit-state-start -->
` ` `json
{
  "version": 1,
  "service": "payments-service",
  "audit_run": 3,
  "last_audited_at": "2026-07-15T14:30:00Z",
  "domain_statement": "process payment transactions, route to PGs, settle merchants",
  "capabilities": {
    "notifications": {
      "status": "open",
      "recommended_service": "notification-service",
      "call_sites": 12,
      "providers": ["SES", "msg91", "Twilio", "SendGrid"],
      "coupling_counts": { "critical": 1, "high": 5, "medium": 4, "low": 2 },
      "todos": [
        {
          "id": "cap-notif-001",
          "status": "open",
          "severity": "critical",
          "file": "payments/tasks.py",
          "line": 142,
          "title": "Move ses.send_email out of transaction.atomic",
          "reason": "SMTP timeout blocks payment commit",
          "created_run": 1,
          "resolved_at": null,
          "resolved_by": null,
          "history": [
            { "run": 1, "status": "open", "date": "2026-07-08", "by": null, "note": "initial finding" }
          ]
        }
      ],
      "consumer_contract": {
        "async_apis": ["publish_notification(template_id, recipient_ref, variables, priority)"],
        "sync_apis": ["send_otp_sync(recipient, template_id, variables) -> {delivered, message_id}"],
        "delivery_semantics": { "idempotent_key_field": "idempotency_key", "ordering": "per recipient_ref.user_id", "sla_p95_ms": 30000 },
        "out_of_scope": ["consent management", "locale-specific rendering", "marketing bulk-blasts"]
      }
    }
  },
  "kept_local": ["PG routing logic", "PG-response parsing and reconciliation", "merchant settlement calculations", "payment-specific idempotency"],
  "history": [
    { "run": 1, "date": "2026-07-08", "findings": 47, "open": 47, "resolved": 0, "wontfix": 0, "diff": "initial" },
    { "run": 2, "date": "2026-07-12", "findings": 51, "open": 46, "resolved": 3, "wontfix": 2, "diff": "+4 new (webhooks/), -3 auto-resolved" },
    { "run": 3, "date": "2026-07-15", "findings": 49, "open": 43, "resolved": 6, "wontfix": 0, "diff": "-2 auto-resolved (revenue_backend migrated)" }
  ]
}
` ` `
<!-- capability-audit-state-end -->

</details>
```

### Fixed status enums (never invent new values)

- Item `status`: `open` · `resolved` · `wontfix` · `retracted` · `regressed`
- Capability `status`: `open` · `in-progress` · `delegated` · `not-applicable`
- Item `severity`: `critical` · `high` · `medium` · `low`

## Rules for the JSON block

- ALWAYS regenerate the JSON on every run — it's derived from the merged state
- NEVER prompt the user to edit JSON directly — the markdown IS the human interface
- ALWAYS use the fixed enums above
- ALWAYS keep the block markers exact: `<!-- capability-audit-state-start -->` and `<!-- capability-audit-state-end -->` — tools grep these
- ALWAYS wrap the JSON in ` ```json ` fence
- ALWAYS hide the block inside `<details>` so humans see the markdown checkbox view by default
