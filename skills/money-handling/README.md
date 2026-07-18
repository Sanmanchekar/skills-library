# Money Handling Review Skill — Integer Minor Units · Rounding · FX Freeze

> **Floats are forbidden for money.** Reviews currency representation, arithmetic, rounding modes (banker's / largest-remainder allocation), FX rate freeze at capture time, and precision-safe serialization. Prevents the "off by a paise" reconciliation break, the cross-currency drift, and the double-tax discount trap.

**Keywords**: money handling review, currency arithmetic, integer minor units, paise cents, ISO 4217, banker's rounding, largest remainder allocation, FX freeze, decimal vs float, python decimal, javascript bigint dinero, java bigdecimal, go int64 minor units, fintech precision, split allocation, tax composition, money handling claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- money-handling
```

## What it does

- Enforces **integer minor units in storage** (BIGINT paise/cents) — flags DECIMAL/FLOAT/DOUBLE money columns
- Language-specific type checks: Python `int`/`Decimal`, JS `bigint`/dinero.js, Java `BigDecimal`, Go `int64`/decimal, Ruby `Money`
- Requires **ISO 4217 currency code** paired with every amount — no bare "amount = 100"
- Catches implicit rounding — every rounding must be an EXPLICIT mode (`HALF_EVEN`/banker's for reporting, `HALF_UP` for user-facing)
- **Largest-remainder allocation** rule — 100.00 split 3 ways sums to 100.00, not 99.99
- **FX freeze**: rate at capture time is stored with the transaction; refunds use the original rate
- Serialization: wire format is `{"amount": 12345, "currency": "INR"}` — never `"123.45"` without a scale rule
- Locale-aware display via platform formatter, not hand-rolled string concat

## When it triggers

- "Review money handling" / "check currency arithmetic"
- "Why is our reconciliation off by a paise / cent?"
- Files touch: `amount`, `price`, `fee`, `tax`, `discount`, `total`, `fx_rate`, `commission`, `refund_amount`
- Post-incident where the discrepancy was a fraction of a currency unit

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [reconciliation-design](../reconciliation-design) — money bugs surface first in reconciliation breaks
- [idempotency-review](../idempotency-review) — pair for the "double credit" family of bugs
- [compliance-review](../compliance-review) — regulator-facing invoices have strict rounding + FX rules
- [code-review](../code-review) — general PR review
