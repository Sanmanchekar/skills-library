---
name: rca
description: Orchestrate a root-cause analysis for an incident, bug, or outage. Runs phased investigation — symptom capture, timeline reconstruction, hypothesis generation, evidence gathering, root cause identification, contributing factors, action items. Triggered when the user says "rca", "root cause", "what caused this", "postmortem", or shares an error / stack trace / incident report.
---

# rca

## When to use

- User asks: "root cause of X", "why did this fail", "postmortem for incident Y"
- User pastes a stack trace, error log, or incident timeline
- After a production outage or customer-reported bug

## Phased flow (do NOT skip phases)

### Phase 1 — Symptom capture
- What was observed? (user-visible behavior, error message, metric drop)
- Where? (service, region, user segment)
- When? (start time, duration, resolved yet?)
- Blast radius (how many users / requests / dollars)

### Phase 2 — Timeline
Reconstruct in absolute UTC. Include: deploys, config changes, first alert, escalations, mitigations.

```
2026-07-14 10:03Z — deploy v2.14.1 (commit abc123)
2026-07-14 10:07Z — error rate on /checkout jumps 0.1% → 8%
2026-07-14 10:12Z — pager fired (SLO burn)
```

### Phase 3 — Hypothesis generation
List 3–5 candidate causes. For each: what would we expect to see if true?

### Phase 4 — Evidence gathering
For each hypothesis, name the specific artifact that would confirm/deny it (log line, metric, code path, git blame). Read those artifacts. Do NOT speculate — check.

### Phase 5 — Root cause + contributing factors
- **Root cause**: the single change / condition that, absent, would have prevented the incident
- **Contributing factors**: the pre-existing conditions that made the root cause harmful (missing test, weak monitor, no circuit breaker)

### Phase 6 — Action items
Output as a table. Every item has an owner and a class.

| # | Action | Class | Owner |
|---|---|---|---|
| 1 | Add integration test for path X | prevent | @alice |
| 2 | Add alert on metric Y | detect | @bob |
| 3 | Add runbook for symptom Z | respond | @carol |

Classes: **prevent** (stops it recurring) · **detect** (catches faster next time) · **respond** (mitigates faster next time).

## Output format

```markdown
# RCA — <incident title>

**Date**: 2026-07-14 · **Duration**: 47 min · **Severity**: SEV-2 · **Blast radius**: ~1,200 users

## Summary
1–3 sentences a non-engineer can read.

## Timeline
...

## Root cause
Single sentence.

## Contributing factors
- ...

## Action items
| # | Action | Class | Owner |
```

## Rules

- Never end the RCA at "human error". Find the systemic gap that let the human error cause an outage.
- Every root cause claim MUST cite a specific artifact (log, metric, commit). No hand-waving.
- Action items MUST have owners — unowned actions rot.
- Do NOT skip phases. Even if the cause is "obvious", the timeline and evidence phases surface contributing factors.
