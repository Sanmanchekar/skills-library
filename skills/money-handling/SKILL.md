---
name: money-handling
description: Review code that touches money for representation correctness — integer minor units (paise/cents), ISO 4217 currency codes, precision-safe arithmetic, correct rounding (banker's / largest-remainder for split allocation), FX rate freeze at transaction time, and precision-safe serialization (JSON floats lose paise). Language-specific patterns (Python Decimal, JS BigInt / dinero.js, Java BigDecimal, Go int64 minor units). Emits severity-tagged findings preventing rupee/cent drift, rounding disputes, and float-precision bugs. Triggered when the user asks to "review money handling", "check currency arithmetic", "why is our reconciliation off by a paise", or files touch `amount`, `price`, `fee`, `tax`, `discount`, `fx`, `total`.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# money-handling

## When to use

- User says: "review money handling", "check currency arithmetic", "why is X off by a paise / cent", "review the pricing / fee / tax code"
- Files touch identifiers: `amount`, `price`, `fee`, `tax`, `discount`, `total`, `fx_rate`, `commission`, `refund_amount`
- Post-incident where the discrepancy was a fraction of a currency unit

## The one law

> **Money is stored as an integer in the smallest unit of the currency. Ever.**

- INR → paise (`₹123.45` → `12345` as `int`)
- USD → cents
- JPY → yen (already the smallest unit; scale is 0)
- BHD → 3 decimal places (fils; `1 BHD` = `1000` fils)

Floats are FORBIDDEN for money. `0.1 + 0.2 = 0.30000000000000004`. That paise, aggregated across a settlement batch, becomes a reconciliation break.

## The 8 checks

### 1. Representation
- [ ] The database column is `BIGINT` / `INT8` (not `DECIMAL`, not `FLOAT`, not `DOUBLE`)
- [ ] The programming type is:
  - Python: `int` OR `decimal.Decimal` (never `float`)
  - JavaScript / TypeScript: `bigint` OR a library (`dinero.js`, `currency.js`) — NEVER `number` for currency
  - Java / Kotlin: `BigDecimal` (with explicit `MathContext`) OR `long` for minor units
  - Go: `int64` for minor units OR `github.com/shopspring/decimal`
  - Ruby: `BigDecimal` OR `Money` gem
- [ ] JSON serialization does NOT convert to float. Python `json.dumps(Decimal(...))` fails by default — good; forcing `float(x)` is a bug. Use string wire format if precision > int64.

### 2. Currency code (ISO 4217)
- [ ] Every amount travels with an ISO 4217 currency code (`INR`, `USD`, `EUR`, `JPY`, ...) — never bare "amount = 100"
- [ ] Storage schema stores `amount BIGINT NOT NULL, currency CHAR(3) NOT NULL` together
- [ ] Currency scale (decimal places) is looked up from a table — JPY has 0, INR/USD have 2, KWD/BHD/JOD have 3

### 3. Arithmetic
- [ ] All arithmetic is on integer minor units OR Decimals with EXPLICIT precision — never on strings, never on floats
- [ ] Comparisons: `amount == other_amount` on Decimal requires same scale (`0.10` != `0.1` for some libs); use dedicated equals
- [ ] Cross-currency arithmetic is FORBIDDEN unless a same-timestamp FX rate is applied

### 4. Rounding
- [ ] Every rounding is explicit (`ROUND_HALF_EVEN` = banker's, `ROUND_HALF_UP`, etc.) — never rely on language default
- [ ] Banker's rounding (`HALF_EVEN`) preferred for financial reporting — reduces cumulative bias
- [ ] `HALF_UP` acceptable for user-facing display of taxes/fees (users expect ".5 → up")
- [ ] Document WHICH mode this codebase uses in one place — mixing modes causes the "off by a paise" reports

### 5. Split allocation (the trap)
Given a total of ₹100.00, split among 3 payees: not `33.33 × 3 = 99.99`. Use **largest-remainder allocation**:

```
₹100.00 → 10000 paise
Base share = 10000 / 3 = 3333 paise (with 1 remainder)
Round-robin distribute the remainder: 3334 + 3333 + 3333 = 10000 ✓
```

- [ ] Every fee-split, revenue-share, refund-split, discount-across-line-items uses largest-remainder OR equivalent — the sum of parts EQUALS the whole
- [ ] Order of distribution is deterministic (sort by id) — otherwise re-runs produce different splits

### 6. FX (foreign exchange)
- [ ] The FX rate used for a transaction is **frozen at capture time** and stored WITH the transaction (`fx_rate`, `fx_rate_captured_at`)
- [ ] Refunds and adjustments use the ORIGINAL fx_rate — not today's rate
- [ ] Storage: both the amount in the transaction currency AND the amount in the settlement currency — computing on demand from a stale rate is a bug
- [ ] Rate source is a single, authoritative provider — mixing sources causes tiny drift

### 7. Tax and fee composition
- [ ] Order of operations is documented: does GST apply to (price + convenience_fee) or just price? Both are legal; the code must match the invoice.
- [ ] Rounding happens at ONE agreed layer (usually the line-item total) — rounding after every intermediate multiplication accumulates error
- [ ] Fee/tax amounts are ALSO stored as integer minor units, not derived on read (an invoice from 6 months ago must produce the same numbers today)

### 8. Serialization + display
- [ ] Wire format: send as `{ "amount": 12345, "currency": "INR" }` — integer minor units + code
- [ ] Never send `"amount": "123.45"` on the wire without a clear scale rule
- [ ] Display formatting: use the platform's locale-aware currency formatter (`Intl.NumberFormat`, `Babel`, `NumberFormat.getCurrencyInstance`) — NOT hand-rolled string concatenation
- [ ] Locale awareness: `1,00,000.00` (INR grouping) vs `100,000.00` (US grouping) vs `100.000,00` (EU grouping)

## Output format

Same as [code-review](../code-review) — severity table + per-finding block. Severity guide:

| Severity | Meaning for money |
|---|---|
| CRITICAL | Float used for money storage or arithmetic; missing currency code on a money value; wrong FX rate applied on refund |
| HIGH | Split allocation loses paise; rounding mode not explicit; DB column is DECIMAL(10,2) with implicit truncation |
| MEDIUM | Comparison relies on default equality; JSON round-trip may lose precision (undocumented) |
| LOW | Display formatting hand-rolled; locale not applied |

## Rules

- NEVER float. Not for storage, not for arithmetic, not for API bodies.
- NEVER apply today's FX rate to an old transaction (refunds, adjustments)
- NEVER divide amounts without a plan for the remainder — largest-remainder allocation or explicit rounding rule
- ALWAYS store currency code with every amount — pair them in the same row / same struct
- ALWAYS make rounding mode explicit and consistent across the codebase
- ALWAYS store the FX rate WITH the transaction that used it — never derive on read
- If the reviewed code touches invoicing, taxes, or settlement, treat float usage as CRITICAL by default — even without evidence of an incident yet
