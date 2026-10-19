---
name: incident-comms
description: Run communication during an active incident — assign roles (incident commander, comms lead), set internal update cadence by severity, and draft status-page updates (investigating / identified / monitoring / resolved), customer-facing notices, and exec/stakeholder summaries that follow strict language rules (no blame, no speculation, no internal jargon, always commit to a next-update time). Hands off to rca after resolution. Triggered when the user says "draft a status page update", "write the incident update", "what do we tell customers", "send an exec summary for this incident", "I'm comms lead for this incident", or "post an update in the incident channel".
---

# incident-comms

## When to use

- An incident is declared (any severity) and someone must communicate
- User says: "draft a status page update", "what do we tell customers", "exec summary", "next incident update"
- User pastes raw incident channel notes and wants them turned into an update
- The incident moves state (identified → monitoring → resolved)

Not for: triage decisions ([oncall-triage](../oncall-triage)) or the post-incident write-up ([rca](../rca)).

## Steps

1. **Confirm roles** — IC and comms lead are named people, not the same person for SEV-1 (see roles table).
2. **Gather facts** — impact (who, what, since when), current state, mitigation in progress. Mark each fact as `confirmed` or `suspected`; only `confirmed` goes external.
3. **Pick the audience** — internal channel, status page, direct customer notice, exec summary. Each gets its own draft.
4. **Pick the status-page state** from the state table.
5. **Draft from the template** for that state; run the language-rules checklist on every draft.
6. **Set next-update time** per the cadence table and put it in the message.
7. **Log each update** (time, audience, state) — this becomes the comms timeline for the RCA.
8. **On resolution** — post resolved notice, send exec summary, hand off to [rca](../rca) with the comms log.

## Roles

| Role | Owns | Does NOT |
|---|---|---|
| Incident commander (IC) | Decisions, priorities, severity, declaring resolved | Debug hands-on (SEV-1) or write external comms |
| Comms lead | All updates: internal, status page, customer, exec | Speculate on cause or promise fix times |
| Ops / tech lead | Investigation and mitigation | Talk to customers directly |
| Scribe (SEV-1) | Timestamped timeline in the channel | — |

## Cadence by severity

| Severity | Internal channel | Status page | Exec / stakeholders |
|---|---|---|---|
| SEV-1 | every 15 min | within 15 min of declare, then every 30 min | at declare, then hourly |
| SEV-2 | every 30 min | within 30 min if customer-visible, then hourly | at declare + resolve |
| SEV-3 | at state changes | usually none | none (weekly report) |

Missing an update time is worse than a "no new information" update — always post on schedule.

## Status-page states and templates

| State | Use when |
|---|---|
| Investigating | Impact confirmed, cause unknown |
| Identified | Cause known, fix or mitigation in progress |
| Monitoring | Fix applied, watching for recovery |
| Resolved | Metrics back to normal for an agreed soak (e.g. 30 min) |

```text
[Investigating] We are investigating elevated errors when <user action> in <product area>.
Some customers may <visible symptom>. Next update by <HH:MM TZ>.

[Identified] We have identified the cause of <symptom> and are applying a fix.
<Workaround if any>. Next update by <HH:MM TZ>.

[Monitoring] A fix has been applied and <symptom> is recovering. We are monitoring
to confirm full recovery. Next update by <HH:MM TZ>.

[Resolved] Between <start> and <end TZ>, some customers experienced <symptom>.
The issue is resolved. <Any customer action needed, or "No action is required.">
We will share a summary of what happened and what we are changing.
```

## Customer-facing language rules

| Rule | Bad | Good |
|---|---|---|
| No blame (vendors, teams, people) | "Our cloud provider failed" | "We experienced an infrastructure issue" |
| No speculation | "Likely a DB issue, fixed in 10 min" | "We are investigating the cause" |
| No internal jargon | "orders-service pods OOMKilled" | "Some orders could not be placed" |
| Describe user impact, not system state | "p99 latency 4s" | "Pages are loading slowly" |
| Always commit to next-update time | "We'll update soon" | "Next update by 14:30 UTC" |
| No ETA for fix unless IC confirms | "Fixed within the hour" | (omit) |
| Say "some customers" unless it's all | "All payments down" (when 8%) | "Some payments are failing" |
| Never disclose security details mid-incident | attacker vector | "We are investigating a security issue" (legal-approved) |

## Exec / stakeholder summary template

```markdown
**Incident**: <title> — SEV-<n> — <state>
**Impact**: <who / what / how many>, since <start TZ>
**Business impact**: <orders failed, revenue at risk, SLA exposure — numbers or "being quantified">
**Current status**: <one line>
**Next step**: <one line> — owner <name>
**Customer comms**: status page updated <time>; <n> enterprise customers contacted
**Next update**: <HH:MM TZ>
**Asks**: <decisions or help needed from leadership, or "none">
```

## Example

Input (channel notes): "checkout 502s since 13:40, ~12% of requests, bad deploy suspected, rolling back orders-service v4.2"

Output (status page):
```text
[Investigating] We are investigating errors affecting checkout. Some customers may be
unable to complete purchases. Next update by 14:15 UTC.
```
Output (internal): "13:58 SEV-2 — checkout 502s ~12% since 13:40. Rollback of orders-service v4.2 in progress (suspected, not confirmed). IC: @ana. Next update 14:15."

## Output format

```markdown
## Incident update — <title> — <HH:MM TZ>

### Internal (incident channel)
<severity, impact, confirmed facts, suspected cause labelled as suspected, actions, owner, next update>

### Status page — <state>
<customer-facing text from template>

### Exec summary
<template above>

### Language check
- [ ] No blame  - [ ] No speculation  - [ ] No jargon  - [ ] Next-update time  - [ ] No unconfirmed ETA

### Comms log
| Time | Audience | State | Link |
```

## Rules

- NEVER publish a suspected cause externally — only confirmed facts leave the incident channel
- NEVER name a vendor, team, or person as the cause in customer-facing text
- NEVER give a fix ETA unless the IC has explicitly confirmed it
- NEVER let the IC also be comms lead on a SEV-1
- NEVER mark Resolved before the agreed soak period passes
- ALWAYS include a next-update time, and always post by it — even with "no new information"
- ALWAYS describe user-visible impact, not internal system state
- ALWAYS get legal/security sign-off before external text on security or data incidents
- ALWAYS hand the comms log to [rca](../rca) after resolution

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: operate · **Agent**: `operate` · **Loop**: `incident`
- **Reads**: `triage` (from `.lifecycle/<run>/` when present)
- **Writes**: `timeline` → `timeline.md`
- **Comes after**: oncall-triage
- **Hand off to**:
  - `rca` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record incident-comms --artifact timeline=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
