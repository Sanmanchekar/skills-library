---
name: compliance-review
description: Map a code change against the compliance regimes India-fintech has to satisfy — PCI DSS (cardholder data), RBI (tokenization, data localization, KYC), NPCI (UPI PSP rules), NACH (mandate lifecycle), DPDPA (personal data), plus PA/PG guidelines. Emits severity-tagged findings referencing the specific mandate clause. Detects hardcoded PAN storage, missing tokenization, data leaving India (S3 buckets in us-east-1, CDNs, third-party SaaS), unmasked PAN in logs, mandate-lifecycle violations, and consent-collection gaps. Triggered when the user asks to "compliance review", "PCI check", "RBI check", "will this pass audit", or files touch card data / KYC docs / mandate flows / customer PII.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# compliance-review

## When to use

- User says: "compliance review", "PCI check", "RBI check", "will this pass audit", "is this compliant"
- Files touch: cardholder data (PAN / CVV / expiry), Aadhaar, PAN card number, bank account, mandate flows, KYC document uploads, log statements around PII
- Pre-audit self-check

## Coverage — India-fintech regimes

This skill maps against the regulations a payments company operating in India must satisfy. NOT legal advice — this is a **first-pass technical check** that reviewers should run before their compliance / infosec team.

| Regime | Scope |
|---|---|
| **PCI DSS v4.0** | Cardholder data storage / transmission / processing (PAN, CVV, expiry, track data) |
| **RBI Master Direction — Card Storage** | No storing of card data by merchants / aggregators after 2022 — tokenization mandatory |
| **RBI Data Localization (2018)** | Payment data of Indian residents must be stored ONLY in India |
| **RBI KYC Master Direction** | Customer identification, video KYC, PEP screening, ongoing due diligence |
| **NPCI UPI PSP Guidelines** | UPI flow rules, VPA handling, transaction limits, risk scoring |
| **NACH Procedural Guidelines** | Mandate registration → active → presented → paid/bounced/cancelled lifecycle; sponsor bank ratios |
| **DPDPA (Digital Personal Data Protection Act, 2023)** | Consent for PII, purpose limitation, retention, data-principal rights |
| **PA/PG Guidelines (2020, updated)** | Payment Aggregator / Payment Gateway license requirements — escrow, nodal accounts, reporting |

## Review checklist by regime

### PCI DSS — card data

- [ ] **Never store CVV.** Grep the codebase for `cvv`, `card_cvv`, `security_code` in DB models / logs. Any storage is a CRITICAL finding — CVV can NEVER be persisted per PCI DSS Req 3.2.
- [ ] **Never store full PAN.** After 2022 RBI directive, merchants must NOT store PAN. Card storage is delegated to a tokenization service (a licensed CoF-TR — Card-on-File Token Requestor / issuer).
- [ ] **Token, not PAN, on the wire.** Grep for card_number, pan_number, card.number in API bodies not going to the tokenization endpoint. If PAN is in a body going anywhere else, CRITICAL.
- [ ] **PAN masking in logs.** All log statements must mask PAN (`411111******1234` or last-4 only). Grep for logs that print card structs unmasked.
- [ ] **Key rotation.** If any key material exists (HSM keys, tokenization keys), rotation policy documented and automated.
- [ ] **Network segmentation.** Card-data-touching services live in a separate segment; grep infra config for shared VPCs or missing egress restrictions.
- [ ] **Access logging.** Every access to card-adjacent tables writes to an audit log (see [security-review](../security-review) for the technical audit-log pattern).

### RBI Data Localization

- [ ] **Storage in India.** S3 buckets, RDS instances, Redis clusters, backups holding Indian payment data must be in `ap-south-1` (Mumbai) or `ap-south-2` (Hyderabad). Grep Terraform/infra config for other regions.
- [ ] **CDN.** Cloudflare / CloudFront / Fastly cache payment data ONLY through Indian PoPs. Payment API responses should be `Cache-Control: private, no-store`.
- [ ] **Third-party SaaS.** If the code calls a SaaS (Datadog, Segment, Amplitude, Sentry) with payment data, that data leaves India. Either scrub before sending OR use the SaaS's India region.
- [ ] **Mirror-copy rule.** Non-India processing of Indian payment data requires that a copy is stored in India within 24h (RBI Aug 2022 clarification). This is rarely relied on — default is India-only.

### RBI — Tokenization (Card-on-File)

- [ ] Any Card-on-File flow (saving a card for future use) MUST use a token issued by a CoF-TR — the actual PAN never touches the merchant.
- [ ] Grep for saved_card, stored_card, card_on_file — every one should reference a token id, not a PAN.
- [ ] Token → PAN detokenization only via the tokenization service; the merchant service never has PAN in memory.

### NPCI — UPI

- [ ] Transaction limits enforced client-side AND server-side (₹1,00,000 P2P per day; product-specific ceilings differ).
- [ ] VPA (`user@handle`) is treated as PII — masking in logs applied.
- [ ] Retry semantics comply with NPCI: same UPI txn id on retry, no auto-retry beyond N attempts.
- [ ] Refund flow uses UPI credit push, not a separate debit — grep for the refund code path.

### NACH — Mandate lifecycle

- [ ] Mandate state machine covers ALL transitions: `initiated → pending-signature → active → paused → cancelled` and `presented → paid | bounced`.
- [ ] Bounce reason codes map to NACH's official list (not a homegrown enum).
- [ ] Sponsor bank ratio limits enforced — mandate registrations per sponsor bank per day are capped.
- [ ] Cancellation confirmation stored — user cancellations MUST be reflected within N days.

### DPDPA (Personal Data Protection)

- [ ] Consent captured explicitly, with purpose, before PII is collected. Grep for `terms_accepted`, `consent_given` — check whether it's tied to specific purposes.
- [ ] Retention: PII older than the retention period is deleted / anonymized. Grep for cron jobs or backfill scripts implementing this.
- [ ] Data-principal rights: is there an endpoint for "get my data" / "delete my data" / "correct my data"? If not, that's a DPDPA gap.
- [ ] Consent is granular. "Accept everything" for marketing + payments together is not compliant — separate consents.
- [ ] Data breach notification: is there a documented flow to notify the Data Protection Board and affected users within 72 hours?

### PA/PG — Escrow and nodal

- [ ] Merchant funds sit in a nodal account, not the PA's operating account.
- [ ] Settlement to merchants happens per the PA's committed schedule (T+1 typical).
- [ ] Reserve holdbacks for chargeback risk are documented.
- [ ] Reports to RBI (monthly transaction volumes, complaints, refunds) are generated and archived.

## Output format

Same as [code-review](../code-review) — severity table + per-finding block with a citation:

```markdown
## Compliance review — <N> findings

| # | Regime | Severity | File:Line | Title |
|---|--------|----------|-----------|-------|
| 1 | PCI DSS 3.2 | CRITICAL | src/checkout/save_card.py:42 | Storing full PAN in payment_methods |

### 1. CRITICAL — PCI DSS 3.2 — src/checkout/save_card.py:42 — Storing full PAN
**Regime**: PCI DSS v4.0 Requirement 3.2 · RBI Master Direction on Card Storage (Sep 2021)

**Problem**: `payment_methods.card_number` stores the full PAN. Both PCI DSS 3.2 and the RBI directive forbid merchant storage of PAN — tokenization via a CoF-TR is mandatory.

**Fix**: Route saved-card flows through the tokenization service:
` ` `python
token = cof_token_service.tokenize(pan)  # PAN never persisted locally
payment_methods.token_id = token.id
` ` `
```

## Rules

- NEVER claim "compliant" without a specific citation — every finding must reference the regime clause
- NEVER treat this as legal advice — this skill is a technical first-pass; a compliance / infosec review must follow
- NEVER flag things not required by any Indian regime — if a US-only regulation applies (e.g. HIPAA), say so and note it's out of scope for this India-focused skill
- ALWAYS check whether a Non-India cloud region hosts payment data — data localization is the most common trap
- ALWAYS check log statements for PAN, CVV, Aadhaar, VPA — masking is a common miss
- ALWAYS distinguish "storing PAN" (banned) from "processing PAN transiently for a single transaction" (allowed under PCI DSS with proper controls)
- If the reviewed code stores CVV under any circumstance, it's a CRITICAL finding regardless of intent — CVV can NEVER be persisted
