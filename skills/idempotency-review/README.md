# Idempotency Review Skill — Prevent Double-Charge / Triple-Refund on Retry

> **The bug that becomes a P0 the moment a mobile radio flakes.** Reviews mutating endpoints, webhook consumers, and background jobs for idempotency correctness — missing keys, non-atomic check-and-write races, wrong scoping, cached-response bugs. Stack-agnostic, fintech-primed (payments, refunds, payouts, mandates).

**Keywords**: idempotency review, api idempotency, idempotency key, exactly-once semantics, replay safety, double charge prevention, triple refund bug, payment idempotency, stripe idempotency, razorpay idempotency, webhook dedup, at least once vs exactly once, fintech api review, idempotency claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- idempotency-review
```

## What it does

- Catches the **three killer failure modes**: no key, non-atomic check-and-write, cached-response bug
- Distinguishes correct patterns (`INSERT ... ON CONFLICT`, `SETNX`, advisory lock) from the classic race-window bug
- Enforces **scoping** — `(tenant, key)` — so keys from different accounts never collide
- Flags in-memory dedup (loses on process restart), server-generated keys (defeats the point), and retention windows < 24h
- Dedicated **refund section** — the triple-refund class of P0 gets its own scope rules
- Applies to background jobs and webhook consumers, not just HTTP endpoints
- Every finding includes a concrete replay-flow example so the fix invariant is visible

## When it triggers

- "Review idempotency" / "check idempotency" / "make this safe to retry"
- "Why did we double-charge / double-refund / duplicate the booking?"
- File is a mutating endpoint on `/payments/*`, `/refunds/*`, `/payouts/*`, `/mandates/*`, `/orders/*`, `/bookings/*`
- Webhook consumer or background job that writes to money-adjacent tables

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [webhook-hardening](../webhook-hardening) — webhook consumer needs its own dedup rules
- [money-handling](../money-handling) — integer minor units and rounding
- [reconciliation-design](../reconciliation-design) — a broken idempotency guarantee shows up as reconciliation breaks
- [security-review](../security-review) — general OWASP diff review
- [code-review](../code-review) — general PR review
