---
name: runbook
description: Generate an incident runbook for a service, alert, or symptom. Covers symptoms, first-5-minutes triage checklist, mitigation commands (with copy-paste examples), rollback, escalation path, and post-incident actions. Triggered when the user asks to "write a runbook", "add a runbook for alert X", or "how should we respond to Y".
---

# runbook

## When to use

- User asks: "write a runbook for X", "runbook for alert Y", "how do we respond to Z"
- After an incident (see [rca](../rca)) — action items call for a runbook

## Runbook structure (STRICT — do NOT reorder)

```markdown
# Runbook — <alert or symptom name>

## Severity
SEV-1 (customer-facing outage) | SEV-2 (degraded) | SEV-3 (internal only)

## Symptoms
- User-visible: "checkout fails with error page"
- Metric: `http_server_errors_total{route="/checkout"} > 5%`
- Log: `ERROR` lines containing `stripe.error.APIConnectionError`

## Dashboards
- [Service overview](https://grafana.internal/d/orders-overview)
- [Stripe integration](https://grafana.internal/d/stripe-client)

## First 5 minutes (triage)
1. Confirm alert is real — check dashboard, not just email
2. Check status pages of dependencies (stripe.status.com, ...)
3. Check recent deploys — `kubectl rollout history deploy/orders`
4. Check error budget — is this a burst or sustained?

## Mitigation

### Option A — Rollback recent deploy (fastest)
` ` `bash
kubectl rollout undo deploy/orders --namespace=prod
` ` `
Wait 2 min, verify error rate drops.

### Option B — Circuit-break the failing dependency
` ` `bash
kubectl set env deploy/orders STRIPE_CIRCUIT_OPEN=true --namespace=prod
` ` `
Falls back to queued retries. Users see "payment pending" instead of error.

### Option C — Scale up (if saturation)
` ` `bash
kubectl scale deploy/orders --replicas=20 --namespace=prod
` ` `

## Rollback
If mitigation makes things worse:
` ` `bash
kubectl rollout undo deploy/orders --to-revision=<N-1>
` ` `

## Escalation
- L1 (0-15 min): oncall engineer
- L2 (15-30 min): @orders-team-lead
- L3 (>30 min or SEV-1): @vp-eng + start incident channel

## Post-incident
- File RCA in <template link>
- Update this runbook with anything new you learned
- Add regression test / alert if applicable
```

## Steps

1. **Identify the alert / symptom**. If the user gives an alert name, look up its expression to understand what's actually broken.
2. **Read the service** to find real commands (kubectl deploy names, env var names, feature flags).
3. **Fill each section** — DO NOT skip sections. Empty sections rot the runbook.
4. **Every mitigation MUST have a copy-pasteable command** — no "check the config" without saying where.

## Rules

- NEVER write a runbook without concrete commands — abstract advice is useless at 3am
- NEVER assume the reader knows the service — link to dashboards, name env vars in full
- NEVER omit the rollback section — if mitigation A worsens things, the runbook must tell you how to undo it
- ALWAYS mark the severity — determines escalation speed
- ALWAYS include the post-incident hook so the runbook improves over time
