# TODO.md schema + JSON state block — db-scoping

Read this file when Step 7 needs to write `.audit/db-scoping/TODO.md` — either fresh or reconciled with an existing file.

## File layout

```
<service-repo>/
└── .audit/
    └── db-scoping/
        ├── TODO.md                                 # canonical, mergeable, human-editable
        └── data-dependencies-YYYY-MM-DD.md         # per-run snapshot, immutable
```

`.audit/` is a shared audit namespace. Suggest the team commit `.audit/` to git — this is the data-boundary source of truth.

## TODO.md structure

```markdown
# DB scoping audit — TODO
<!-- db-scoping-audit v1 -->
<!-- service: <service-name> -->
<!-- audit_run: <N> -->
<!-- last_audited_at: <UTC ISO 8601> -->
<!-- owned_data_statement: <one sentence> -->

## Table inventory
<!-- inventory-start -->
| Table | Access | Classification | Owner (inferred) | Evidence |
|---|---|---|---|---|
| payment_orders | RW | owned | this-service | migrations/0003:12 |
| institutes | R | foreign-read | identity | order_helper.py:88 |
<!-- inventory-end -->

## Domain: identity
<!-- domain_id: identity -->
<!-- status: open -->
<!-- tables: institutes (R), user_profile (RW) -->
<!-- coupling: CRITICAL (2) · HIGH (1) · MEDIUM (0) · LOW (0) -->

### Migration todos
- [ ] `dbdep-identity-001` 🔴 **CRITICAL** — Stop writing `user_profile.last_paid_at` at `…/webhook_helper.py:210`; emit `payment.captured` and let identity write (two-writer + cross-domain-txn)
- [ ] `dbdep-identity-002` 🟠 HIGH — Replace `payment_orders JOIN institutes` with `get_institute(id)` at `…/order_helper.py:88` (cross-context join)
- [x] `dbdep-identity-003` 🟠 HIGH — [resolved 2026-07-20 @alice] Removed direct `institutes` read in reports

### Consumer ask
<!-- contract-start -->
_(preserved verbatim across re-runs unless `regen-contract`)_
- `get_institute(id) -> {name, settlement_account, status}` — point-lookup, eventual freshness OK
- `record_payment(student_id, order_id, paid_at)` — owner performs the write; we emit an event
- Do NOT need: full row, write access to user_profile
<!-- contract-end -->

### Team notes
<!-- notes-start -->
<!-- notes-end -->

---

## Owned tables (out of scope for delegation)
<!-- owned-start -->
- payment_orders, transactions, settlement_* — sole writer, created in local migrations
<!-- owned-end -->

## Ambient surface to shed
<!-- ambient-start -->
- Imports shared models exposing <N> tables; queries <M>. Narrow the import to owned + declared deps.
<!-- ambient-end -->

## Confirm ownership (inferred)
<!-- confirm-start -->
- institutes → identity (inferred)
- provider_config → lending (inferred)
<!-- confirm-end -->

## Audit history
| Run | Date | Tables touched | Owned | Foreign | Ambient | Open todos | Δ vs prior |
|---|---|---|---|---|---|---|---|
| 1 | 2026-07-17 | 24 | 15 | 6 | 3 | 5 | initial audit |
```

## Todo item format

```
- [ ] `dbdep-<domain>-<NNN>` <emoji> **<SEVERITY>** — <verb + table + file:line + why>
```

- **`dbdep-<domain>-<NNN>`** — stable id, zero-padded 3 digits, monotonic per domain, never re-used
- **Severity emoji + word** — 🔴 CRITICAL · 🟠 HIGH · 🟡 MEDIUM · 🟢 LOW
- **Verb-first** — Stop / Replace / Delegate / Narrow / Remove — never "look at" or "consider"
- **`file:line`** in backticks + **why in parens** (the specific smell)

## Machine-readable state block (canonical for LLMs / tools)

Append a fenced JSON block at the bottom of TODO.md, hidden in `<details>`, bracketed by `<!-- db-scoping-state-start -->` / `<!-- db-scoping-state-end -->`. JSON is canonical for prior-run values; markdown checkboxes are the human view, regenerated from JSON on each write.

```markdown
---

<details>
<summary>Machine-readable state (regenerated on each run — do not edit)</summary>

<!-- db-scoping-state-start -->
` ` `json
{
  "version": 1,
  "service": "<service-name>",
  "audit_run": 1,
  "last_audited_at": "2026-07-17T00:00:00Z",
  "owned_data_statement": "owns payment orders, transactions, settlements, webhooks",
  "inventory": [
    { "table": "payment_orders", "access": "RW", "classification": "owned", "owner": "this-service", "inferred": false, "evidence": "migrations/0003:12" },
    { "table": "institutes", "access": "R", "classification": "foreign-read", "owner": "identity", "inferred": true, "evidence": "cashfree/…/order_helper.py:88" },
    { "table": "user_profile", "access": "RW", "classification": "foreign-write", "owner": "identity", "inferred": true, "evidence": "…/webhook_helper.py:210" }
  ],
  "domains": {
    "identity": {
      "status": "open",
      "tables": ["institutes", "user_profile"],
      "coupling_counts": { "critical": 2, "high": 1, "medium": 0, "low": 0 },
      "todos": [
        {
          "id": "dbdep-identity-001",
          "status": "open",
          "severity": "critical",
          "table": "user_profile",
          "access": "W",
          "smell": "foreign-write",
          "file": "…/webhook_helper.py",
          "line": 210,
          "title": "Stop writing user_profile; emit event, let identity write",
          "reason": "two-writer + cross-domain-txn couples payment atomicity to identity",
          "created_run": 1,
          "resolved_at": null,
          "resolved_by": null,
          "history": [ { "run": 1, "status": "open", "date": "2026-07-17", "by": null, "note": "initial finding" } ]
        }
      ],
      "consumer_ask": {
        "read_apis": ["get_institute(id) -> {name, settlement_account, status}"],
        "write_delegations": ["record_payment(student_id, order_id, paid_at)"],
        "access_pattern": "point-lookup + batch by ids",
        "freshness": "eventual",
        "out_of_scope": ["full row", "write access to user_profile"]
      }
    }
  },
  "owned_tables": ["payment_orders", "transactions", "settlements"],
  "ambient": { "declared": 521, "queried": 24, "unused": 497, "module": "all_models.py" },
  "confirm_ownership": [ { "table": "institutes", "assumed_owner": "identity" } ],
  "history": [
    { "run": 1, "date": "2026-07-17", "tables_touched": 24, "owned": 15, "foreign": 6, "ambient": 3, "open_todos": 5, "diff": "initial" }
  ]
}
` ` `
<!-- db-scoping-state-end -->

</details>
```

### Fixed status enums (never invent new values)

- Item `status`: `open` · `resolved` · `wontfix` · `retracted` · `regressed`
- Domain `status`: `open` · `in-progress` · `delegated` · `not-applicable`
- Severity: `critical` · `high` · `medium` · `low`
- Classification: `owned` · `foreign-read` · `foreign-write` · `shared-reference` · `ambient`
- Access: `R` · `W` · `RW` · `—` (ambient/unused)

## Rules for the JSON block

- ALWAYS regenerate the JSON on every run — derived from merged state
- NEVER prompt the user to edit JSON directly — the markdown IS the human interface
- ALWAYS use the fixed enums above
- ALWAYS keep the block markers exact: `<!-- db-scoping-state-start -->` and `<!-- db-scoping-state-end -->` — tools grep these
- ALWAYS wrap JSON in ` ```json ` fence
- ALWAYS hide the block inside `<details>` so humans see the markdown checkbox view by default
