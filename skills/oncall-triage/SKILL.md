---
name: oncall-triage
description: Alert-to-action decision tree for an on-call engineer. Takes an alert / page / customer report and drives it through severity classification, first-response checklist, mitigation vs investigate decision, and escalation triggers. Triggered when the user says "I got paged for X", "triage this alert", "on-call for Y just fired", or shares an alert body.
---

# oncall-triage

## When to use

- User shares an alert body, PagerDuty incident, or customer report
- User says: "I just got paged", "triage this", "on-call for X fired"
- On-call handoff / shift start

## The decision tree

```
Alert fires
  │
  ├─ 1. Is this real? (dashboard confirms, not just email)
  │     ├─ No  → suppress + file "flaky alert" ticket
  │     └─ Yes → continue
  │
  ├─ 2. Classify severity (see table)
  │     ├─ SEV-1 → declare incident, page L2, start channel
  │     ├─ SEV-2 → notify team, work in on-call channel
  │     └─ SEV-3 → track, fix in normal hours
  │
  ├─ 3. What changed? (recent deploy / config / feature flag / dep incident)
  │     └─ If a recent change is suspect → rollback FIRST, investigate after
  │
  ├─ 4. Consult the runbook (see [runbook](../runbook))
  │     ├─ Runbook exists → execute mitigation
  │     └─ Runbook missing → time-box investigation (15 min for SEV-2, 5 min for SEV-1)
  │
  ├─ 5. Mitigate vs investigate
  │     ├─ Mitigate first if: users impacted, revenue impacted, SLO burning
  │     └─ Investigate first if: no user impact, internal service only
  │
  └─ 6. Escalate when: (see table)
```

## Severity classification

| Severity | Criteria | Response time |
|---|---|---|
| **SEV-1** | Customer-facing outage · data loss · security breach · > 5% error rate · > 5% revenue impact | Immediate; page L2 within 15 min if not resolved |
| **SEV-2** | Degraded service · workaround exists · > 1% error rate · single-tenant impact | 30 min |
| **SEV-3** | Internal only · no user impact · non-urgent | Next business day |

Downgrade only after evidence — never downgrade to justify going back to sleep.

## First 5 minutes (any severity)

1. **Confirm real** — dashboard, not just the alert email. Alerts can lie.
2. **Snapshot the state** — take a screenshot of the graph at the moment of triage (for the postmortem)
3. **Check status pages** — of your major dependencies (Stripe, AWS, GitHub, etc.)
4. **Check recent deploys** — the change window is your #1 suspect
5. **Post in the on-call channel** — "I've picked up alert X, starting triage" (so someone else doesn't duplicate)

## Mitigate vs investigate

Always mitigate BEFORE investigating when users are impacted.

**Mitigation options (in preference order)**:
1. Rollback — the last change is your prime suspect. Rolling back is often 1 command.
2. Circuit-break — disable the failing dependency; degrade gracefully.
3. Scale out — if saturation, more replicas.
4. Feature flag off — kill the new code path without a full deploy.
5. Rate limit / shed load — protect the majority by rejecting the excess.

Mitigation buys you time to investigate calmly.

## Escalation triggers

Escalate to L2 / team lead / VP when:

| Trigger | Escalate to |
|---|---|
| SEV-1 unresolved after 15 min | Team lead |
| SEV-1 unresolved after 30 min | VP Eng / on-call executive |
| You are blocked (need access, another team, vendor) | Person who can unblock |
| You are the sole responder for > 45 min | Anyone — you'll make mistakes tired |
| Root cause is outside your team's ownership | The owning team's on-call |

## Handing off

If your shift ends mid-incident:
1. Post a **status snapshot** in the channel: what's happening, what's been tried, what's next
2. Pair with the incoming on-call for 5 min before you leave
3. Do NOT go silent — always announce the handoff

## Output format

```markdown
## Triage — <alert name>

### Alert
- Fired at: 10:03Z
- Threshold: error rate > 5% for 5 min on /checkout
- Current value: 8.2%

### Severity
SEV-2 — checkout degraded but workaround exists (users can retry)

### First-5-min findings
- Dashboard confirms: yes
- Status pages: Stripe green, AWS green
- Recent deploys: orders v2.14.1 deployed 10:00Z
- Suspicion: correlation between deploy and error start (3 min after)

### Action plan
1. Rollback orders to v2.14.0 (2 min) — Option A from [runbook](link)
2. Verify error rate drops within 5 min of rollback
3. If not: try circuit-break on stripe client (Option B)
4. If still not: escalate to @team-lead

### Post-mitigation
- File RCA once mitigated (see [rca](../rca))
- Update runbook with anything learned
```

## Rules

- NEVER investigate before mitigating when users are impacted
- NEVER dismiss an alert without evidence — "seems flaky" is not evidence
- NEVER escalate without a status snapshot — the escalation target needs context
- NEVER work alone for > 45 min on a SEV-1 — ask for a partner
- ALWAYS post in the channel that you've picked up the alert
- ALWAYS snapshot dashboards during triage — needed for postmortem
- ALWAYS pair on handoff — silent handoffs cause double-mitigations
