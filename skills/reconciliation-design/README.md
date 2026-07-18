# Reconciliation Design Skill — Match · Categorize · Post to Ledger

> **Zero unknown-bucket recon.** Design or review a reconciliation engine — internal vs PG vs bank — with stable match keys, per-instrument time windows (UPI T+2, card T+3, netbanking T+2, NACH T+3, intl-card T+8), a named break taxonomy, idempotent runs, and ledger-integrated resolution.

**Keywords**: reconciliation design, payment reconciliation, ledger reconciliation, pg statement reconciliation, bank statement reconciliation, settlement reconciliation, recon engine design, break categorization, break aging, match key priority, UPI recon T+2, NACH recon, chargeback recon, fintech ledger, double-entry accounting, reconciliation review, recon claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- reconciliation-design
```

## What it does

- Defines the **match unit** explicitly (transaction / RRN / UTR / settlement batch) — no vague "match statements"
- Priority-ordered **match keys**: provider id > our reference > composite (amount + ts + last-4) > fuzzy (human-only)
- Per-instrument **time windows** built in — UPI T+2, card T+3, intl-card T+8, NACH T+3, RTGS/IMPS T+1
- **Break taxonomy** with 9 named types + resolution actions — no "misc" bucket in production
- **Idempotent runs** — re-run against the same slice returns the same result; ingestion dedupes by file hash
- **Ledger integration** — resolved amount-mismatches become double-entry postings
- **Immutable resolutions** — reopening creates a new record, doesn't overwrite
- Aging + escalation rules per break type (refunds strictest at 72h)

## When it triggers

- "Design reconciliation" / "review recon engine"
- "Our reconciliation has unexplained breaks"
- "Why doesn't our ledger match the PG report?"
- Files touch: `reconcile`, `settlement`, `ledger`, `statement`, `mis_report`, `payout_batch`

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [money-handling](../money-handling) — amount mismatches often trace back to precision or rounding
- [idempotency-review](../idempotency-review) — `duplicate-internal` breaks originate here
- [webhook-hardening](../webhook-hardening) — `missing-in-internal` breaks originate from lost webhooks
- [compliance-review](../compliance-review) — audit trail + resolution immutability are compliance requirements
- [rca](../rca) — root-cause a recurring break class
