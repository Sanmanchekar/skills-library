# Webhook Hardening Skill — Signature Verify · Dedup · Replay Guard · DLQ

> **The 6-layer defensive stack for any webhook receiver.** Timing-safe signature verification, timestamp replay window, event-id dedup, 2xx-fast + async worker, state-machine ordering, dead-letter queue — with provider quirks (Stripe / Razorpay / Cashfree / PhonePe / GoCardless / Adyen).

**Keywords**: webhook security, webhook signature verification, HMAC timing-safe compare, webhook dedup, webhook replay attack, webhook DLQ, stripe webhook, razorpay webhook, cashfree webhook, phonepe webhook, adyen webhook, webhook hardening review, fintech webhook, webhook idempotency, webhook state machine, webhook hardening claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- webhook-hardening
```

## What it does

- **6 layers, every layer required**: signature → timestamp → dedup → 2xx-fast → ordering → DLQ
- Catches `==` on HMACs (timing attack), signature verification against parsed JSON (bypass via whitespace), and sync processing on webhook thread (retries pile up)
- Provider-specific quirks in one table: Stripe's `v1=...` scheme, Cashfree's signed timestamp, PhonePe's SHA256(base64+endpoint+salt), Adyen's per-item HMAC
- Dedup rules identical shape to [idempotency-review](../idempotency-review) — `(provider, event_id)`, atomic check-and-write, ≥ 7 day retention
- State-machine transition guards for out-of-order arrivals (`payment.refunded` before `payment.captured`)
- DLQ required for permanent-failure events — no retry-forever

## When it triggers

- "Review this webhook" / "harden this webhook"
- "Why did we process the same webhook twice / miss one / fail signature verification"
- File contains a webhook handler for a payment / notification provider
- Post-incident where a webhook was the trigger

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [idempotency-review](../idempotency-review) — the receiver dedup shares the same primitives
- [security-review](../security-review) — general OWASP diff review
- [rca](../rca) — root-cause a webhook-triggered outage
- [runbook](../runbook) — runbook for DLQ backlog alerts
