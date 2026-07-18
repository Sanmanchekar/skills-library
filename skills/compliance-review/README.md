# Compliance Review Skill — PCI DSS · RBI · NPCI · NACH · DPDPA · PA/PG

> **India-fintech compliance first-pass in one skill.** Maps a code change against every regime a payments company operating in India must satisfy. Catches PAN storage, CVV persistence (never allowed), data leaving India (`us-east-1` buckets, non-India SaaS), unmasked PAN in logs, mandate-lifecycle drift, and consent-collection gaps.

**Keywords**: pci dss review, rbi compliance review, npci upi guidelines, nach mandate compliance, dpdpa review, india fintech compliance, payment aggregator compliance, tokenization mandate, card storage forbidden, data localization india, pan masking logs, cvv never store, india payments audit, ap-south-1 payment data, compliance review claude code skill, indian fintech seo

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- compliance-review
```

## What it does

- **7 regimes mapped**: PCI DSS v4.0, RBI Master Direction on Card Storage, RBI Data Localization (2018), RBI KYC, NPCI UPI PSP, NACH Procedural Guidelines, DPDPA (2023), PA/PG (2020+)
- Catches **CVV storage anywhere** — CRITICAL, never permitted regardless of controls
- Catches **PAN storage** by non-CoF-TR merchants — banned after RBI's 2022 directive
- Flags **data leaving India** — S3 not in `ap-south-1/2`, non-India SaaS calls (Datadog / Segment / Sentry / Amplitude)
- Flags **PAN / CVV / Aadhaar / VPA in logs** — masking miss is the most common finding
- **NACH mandate state machine** completeness check — bounce codes must map to NPCI's official list
- **DPDPA gaps**: missing consent-per-purpose, missing data-principal endpoints, missing 72h breach notification
- Every finding cites the **specific regime clause** — not "it's not compliant"
- Explicit: NOT legal advice — first-pass technical check before infosec / compliance team review

## When it triggers

- "Compliance review" / "PCI check" / "RBI check"
- "Will this pass audit?"
- Files touch: cardholder data (PAN / CVV / expiry), Aadhaar, KYC docs, mandate flows, customer PII
- Pre-audit self-check

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [security-review](../security-review) — OWASP-level generic security review
- [iac-review](../iac-review) — infra-side data localization (region checks)
- [reconciliation-design](../reconciliation-design) — audit-trail immutability is a PA/PG requirement
- [webhook-hardening](../webhook-hardening) — signature verification is part of the PA/PG audit
- [db-scoping](../db-scoping) — access-control audit for card-adjacent tables
