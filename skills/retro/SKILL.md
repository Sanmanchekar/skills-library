---
name: retro
description: Facilitate a sprint or incident retrospective. Structures the discussion (what went well / what didn't / what to change), extracts specific action items with owners and dates, blocks vague "we should" statements, and produces a written summary. Blameless by design. Triggered when the user says "run a retro", "post-incident retro", "sprint retro", or "we need to debrief X".
---

# retro

## When to use

- User says: "run a retro", "sprint retro", "post-incident retro", "we need to debrief X"
- End of a sprint, project, quarter, or incident
- After a launch (successful OR failed)

## The blameless principle

**Behavior is a function of system + incentives, not of individuals.** The question is never "who did this" — it is "why did our system make this the reasonable thing to do." If a retro produces a person-blame outcome, the retro failed.

## Structure

### Round 1 — What went well (10 min)
Every participant contributes ≥1 item.

Anchor with specifics: what did we ship, what problem got easier, what habit became routine, what tool paid off.

Not: "vibes were good", "we tried hard". Not falsifiable.

### Round 2 — What didn't go well (15 min)
Every participant contributes ≥1 item. Focus on **facts and effects**, not blame.

Format: "**When** X happened, **the effect was** Y." (e.g., "When the migration went out on Friday, we spent Saturday firefighting.")

### Round 3 — Themes (10 min)
Cluster the items into 3-5 themes. Themes are more actionable than individual complaints.

Example themes:
- "Deploy timing" (Friday deploys, no soak time)
- "Test coverage" (tests didn't catch X, Y, Z)
- "Cross-team dependencies" (blocked on Team A twice, Team B once)

### Round 4 — Actions (15 min)
For each theme with the most weight, propose 1-2 concrete actions.

**Every action MUST have**:
- A **verb** — "Add / Change / Remove / Document / Automate"
- A **specific artifact** — not "improve communication", but "add a #deploys channel post-deploy digest"
- An **owner** — a name, not "the team"
- A **due date** — an actual date, not "next quarter"

**Every action MUST NOT be**:
- Vague ("we should communicate better")
- Un-ownable ("everyone should code review more thoroughly")
- Un-dated ("eventually we'll fix this")

## Post-incident retro variant

For an incident retro, add these rounds AFTER the timeline is reconstructed (see [rca](../rca)):

- **What went well in the response?** — mitigation was fast, runbook helped, escalation worked
- **What could have detected this sooner?** — missing alert, weak dashboard, unclear symptoms
- **What could have prevented this?** — missing test, missing review, missing constraint
- **What could make the next one faster to fix?** — runbook gap, feature flag missing, rollback slow

Each of the four maps to a `detect / prevent / respond` action category.

## Facilitation rules

- **Time-box** every round. Timers, not vibes.
- **Everyone speaks.** If someone's quiet, ask them directly.
- **No blame.** If a comment names a person, redirect to system: "What made this the easy path?"
- **No solutioning in Round 2.** Fixes belong in Round 4. Cutting Round 2 short to "fix it" swallows the diagnosis.
- **Write it down** live. Retro without notes = retro that never happened.

## Output format

```markdown
# Retro — <sprint / incident / project>

**Date**: 2026-07-15 · **Attendees**: @alice @bob @carol · **Facilitator**: @dan

## What went well
- Shipped the auth migration in 3 days (estimated 5)
- New CI cache cut build time from 12 min → 4 min
- Runbook for Stripe outages worked exactly as written

## What didn't go well
- Friday deploy of orders v2.14.1 caused Saturday firefight (~4h)
- 3 tests were flaky and got merged around instead of fixed
- Blocked 2 days waiting on Team Platform for VPC change

## Themes
1. **Deploy timing** — 2 items
2. **Test hygiene** — 1 item, but recurring across sprints
3. **Cross-team dependencies** — 1 item, high impact

## Actions
| # | Action | Owner | Due |
|---|---|---|---|
| 1 | Add "no deploys after Thursday" rule to CI merge gate | @dan | 2026-07-22 |
| 2 | File tickets for the 3 flaky tests; block PRs on them | @alice | 2026-07-18 |
| 3 | Publish quarterly capacity ask to Team Platform | @bob | 2026-07-31 |

## Actions carried over from previous retro
- [x] Add runbook for Stripe outages (completed — used this sprint)
- [ ] Add integration test for order-webhook idempotency (moved to next sprint)

## Next retro
- 2026-07-29
- Review status of actions 1-3
```

## Rules

- NEVER let the retro end without written actions with owner + date
- NEVER allow person-blame — always redirect to system incentives
- NEVER skip "what went well" — recognition is fuel, absence rots morale
- NEVER solutionize in the "what didn't go well" round — cluster first, solve later
- ALWAYS revisit prior-retro actions at the start of the next retro — otherwise actions rot
- ALWAYS keep the doc in a searchable place — retro history is your team's memory
