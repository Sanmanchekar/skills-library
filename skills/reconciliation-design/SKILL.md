---
name: reconciliation-design
description: Design or review a reconciliation engine that matches records across systems — PG statements vs internal transactions, bank statements vs settlement records, refund initiations vs PG confirmations, mandate presentations vs bank responses. Enforces stable match keys, time-window tolerance (T+1 / T+2), break categorization (settlement delay, refund crossing period, chargeback, amount mismatch, missing on one side), idempotent recon runs, and audit-preserving break resolution. Fintech-focused (payment gateways, bank statements, ledger books). Triggered when the user asks to "design reconciliation", "review recon engine", "our recon has breaks we can't explain", or files touch `reconcile`, `settlement`, `ledger`, or bank statement / PG report ingestion.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# reconciliation-design

## When to use

- User says: "design reconciliation", "review recon", "our reconciliation has unexplained breaks", "why doesn't our ledger match the PG report"
- Files touch: `reconcile`, `reconciliation`, `settlement`, `ledger`, `statement`, `mis_report`, `payout_batch`
- Post-incident: settlement short by ₹X and nobody knows where it went

## The core problem

Reconciliation answers: **for every unit of money we tracked internally, does the external system agree it exists, has the same amount, and moved when we said it did?**

Three sources, three roles:

| Source | Role | Truth on... |
|---|---|---|
| Internal ledger / transactions DB | What we THINK happened | Order intent, refund intent, settlement expectation |
| PG statement / bank statement | What the counterparty says happened | Actual money movement |
| Bank account | What ACTUALLY happened | Ultimate ground truth |

A reconciliation engine matches records across two (or three) sources and categorizes every non-match into a known break type. **Unknown breaks are bugs** — a mature recon system has zero "misc" buckets.

## Steps (design mode)

### 1. Define the match unit
Not "match statements" — **match transactions**. One row on each side is one unit.

The atomic match unit varies:
- Card payment recon: one **transaction id**
- UPI recon: one **UPI reference id** (RRN)
- Settlement recon: one **settlement batch id** (many transactions rolled up)
- Refund recon: one **refund id**
- Bank ledger recon: one **UTR / bank txn reference**

Design MUST state which unit this recon is matching.

### 2. Choose stable match keys (in priority order)
Match on the STRONGEST key you can. Weaker keys are fallback.

| Priority | Key | Uniqueness |
|---|---|---|
| 1 | Provider-supplied transaction id (RRN, PG txn id, UTR) | Should be globally unique per provider |
| 2 | Our reference id sent at initiation (`merchant_txn_id`, `order_id`) | Unique in our namespace |
| 3 | Amount + timestamp + last-4-digits (composite) | Weak — used only when both primary keys missing |
| 4 | Fuzzy match with user judgment | For breaks only — NEVER auto-close a fuzzy match |

- [ ] Recon does NOT rely on amount-only matching — collisions happen (two ₹99 charges same minute)

### 3. Define time windows
Money settles later than it's initiated. Recon must be tolerant of this lag.

| Instrument | Typical settlement | Reconcile after |
|---|---|---|
| UPI (P2M) | T+0 or T+1 | T+2 |
| Card (domestic) | T+1 or T+2 | T+3 |
| Card (international) | T+3 to T+7 | T+8 |
| Netbanking | T+1 | T+2 |
| NACH debit | T+2 | T+3 |
| Wallet | T+0 | T+1 |
| RTGS / IMPS | Same day | T+1 |

- [ ] The recon engine expects a transaction to have settled within its window; anything within-window that hasn't settled is `pending-in-window`, not `break-missing`
- [ ] Beyond the window, unsettled becomes a break

### 4. Categorize every break (the zero-unknown-buckets rule)

Every non-match must resolve to a known type. Design the taxonomy up front:

| Break type | Definition | Action |
|---|---|---|
| `missing-in-external` | We have it; PG doesn't | Investigate — could be initiation-failed but marked success internally, OR pending beyond window |
| `missing-in-internal` | PG has it; we don't | Investigate — could be webhook missed, OR duplicate at PG |
| `amount-mismatch` | Both have it; amounts differ | Common cause: fee / TDS / convenience fee applied by one side and not the other. Resolve via composition rule (see [money-handling](../money-handling)) |
| `status-mismatch` | Both have it; states disagree (we say success, PG says failure) | Trust PG for terminal states; investigate webhook race |
| `date-out-of-window` | Both have it; but on different reconciliation days | Straddle: initiation on day N, settlement on day N+1. Track and roll into next day's recon |
| `chargeback` | External shows a refund/dispute we didn't initiate | Flow into a chargeback pipeline; don't treat as a plain break |
| `settlement-delay` | PG statement shows txn in an unexpected settlement batch | Track and reconcile in the correct batch's window |
| `duplicate-external` | PG shows the SAME id twice | PG bug — flag and quarantine; NEVER auto-credit |
| `duplicate-internal` | We have TWO records for the same PG id | Idempotency bug on our side — link to [idempotency-review](../idempotency-review) |

- [ ] Every break carries: type, amount, direction, references (both sides), first-seen date, last-checked date, current status (`open`/`under-investigation`/`resolved`/`waived`), and — critically — the ORIGINAL match candidates it was compared against

### 5. Idempotent recon runs
Recon should be safe to re-run against the same data with the same result.

- [ ] Each run has a `run_id` and processes a `(source, date)` slice
- [ ] Match rows have a `matched_by_run_id` — re-running the same slice re-computes matches; matches don't multiply
- [ ] Break records have STABLE ids computed from the source refs — re-running doesn't create new break records for the same underlying discrepancy
- [ ] Ingestion of the same statement file twice is safe (dedupe by file hash)

### 6. Preserve audit trail
Once a break is resolved, its resolution IS a first-class record.

- [ ] Every resolution records: who resolved, when, why (dropdown of resolution codes), any adjusting journal entry
- [ ] Resolutions are IMMUTABLE — reopening creates a NEW resolution record, doesn't overwrite
- [ ] "Waiving" a break (e.g., ₹0.01 rounding difference) requires a policy citing max-per-day auto-waive limits

### 7. Ledger integration
Reconciliation without ledger adjustments is a report. Reconciliation WITH ledger is an accounting system.

- [ ] Every resolved amount-mismatch creates a **posting** in the internal ledger (double-entry) — one to reflect the discovered difference, one to the appropriate P&L account
- [ ] Postings reference the break they resolved — audit can trace ledger entry → break → source rows
- [ ] Ledger balance = source-of-truth internal balance; recon posts corrections; drift becomes visible next-day

### 8. Break-aging + escalation
- [ ] Breaks aged > N days escalate (email / Slack / oncall) — decide N per break type; refunds strictest (72h)
- [ ] Dashboard shows: total open, count by type, aging buckets, resolution rate this week

## Output format (design mode)

```markdown
# Reconciliation design — <name>

## Match unit
<one sentence: what a "row" is>

## Sources
- Internal: <table + query>
- External: <provider statement + ingestion path>
- (Optional) Ground truth: <bank statement>

## Match keys
1. <primary key>
2. <fallback>
3. ...

## Time window
- Initiation → settlement expected: T+<N>
- Recon runs at: T+<N+1>
- Straddle handling: ...

## Break taxonomy
| Type | Detection | Auto-action | Escalation age |
|---|---|---|---|

## Ledger integration
- Which posting rules fire on which resolution codes
- Adjusting account map

## Idempotency
- Run id + slice
- Statement dedup by file hash
- Stable break ids
```

## Rules

- NEVER auto-close a fuzzy match without human sign-off — the moment a machine decides "close enough" is when quiet drift begins
- NEVER trust amount-only matching — always require at least one strong id
- NEVER have a "misc" or "unknown" break bucket in production — every break must categorize to a named type
- NEVER overwrite a resolution — create a new record
- ALWAYS state the time window per instrument up front — "T+1" is not universal
- ALWAYS produce ledger postings for resolved amount-mismatches, not just close them
- ALWAYS make recon runs idempotent — re-running against the same slice must produce the same output
- If the reviewed recon has a "misc" bucket or an amount-only match rule, treat as HIGH severity — that's where audit findings come from
