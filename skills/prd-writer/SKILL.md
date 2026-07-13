---
name: prd-writer
description: Turn a rough product ask into a structured Product Requirements Document. Extracts problem, target users, jobs-to-be-done, in-scope / out-of-scope, success metrics, open questions, and rollout plan. Triggered when the user asks to write a PRD, spec, or product brief, or shares a rough feature idea.
---

# prd-writer

## When to use

- User asks: "write a PRD", "spec this out", "turn this into a doc"
- User shares a rough feature idea, Slack thread, or customer request

## PRD structure (STRICT order)

```markdown
# PRD — <feature name>

**Author**: <name> · **Status**: Draft · **Last updated**: 2026-07-14

## 1. Problem
Who has the problem, what is it, and why now. 2-4 sentences MAX.

## 2. Target user
- Primary persona: <role>, <company size>, <workflow context>
- Job-to-be-done: "When I <situation>, I want to <motivation>, so I can <outcome>"

## 3. Success metrics
Leading + lagging. Every metric MUST have a target and a time window.

| Metric | Baseline | Target | Window |
|---|---|---|---|
| % of new users completing X | 42% | 60% | 30 days post-launch |
| Support tickets tagged Y | 18/wk | <5/wk | 60 days |

## 4. Scope

### In scope
- Bullet 1
- Bullet 2

### Explicitly OUT of scope
- What we are NOT doing (and often, why not — link to a followup)

## 5. User experience
Numbered walkthrough of the primary flow. Include the 1-2 key screens as ASCII sketches or references.

## 6. Requirements
Functional + non-functional. Use MoSCoW (Must / Should / Could / Won't).

## 7. Open questions
Every open question has an owner and a due date. Unowned questions rot.

| Q | Owner | Due |
|---|---|---|
| Do we need to support offline mode? | @alice | 2026-07-20 |

## 8. Rollout plan
- Launch gate: <criteria>
- % rollout: 5% → 25% → 100%
- Kill switch: <feature flag name>
- Rollback plan: <how to disable>

## 9. Risks
- Risk / mitigation pairs. Any risk without a mitigation is unmitigated risk.

## 10. Timeline
- Design: <dates>
- Engineering: <dates>
- Beta: <dates>
- GA: <date>
```

## Steps

1. **Interview mode**. If the input is thin, ask 3-5 sharpening questions BEFORE drafting:
   - Who exactly hurts today, and how?
   - What's the smallest thing that would prove this is worth doing?
   - What are we explicitly NOT doing?
2. **Fill every section**. Empty sections signal "we haven't thought about it" — flag them as open questions instead.
3. **Concrete metrics only**. "Improve engagement" is NOT a metric. "Increase D7 retention from 30% to 40% in 60 days" is.
4. **Every "Should" and "Could" should have a "why not Must"** — forces the author to commit or drop.

## Rules

- NEVER write a PRD without a target metric — you can't ship what you can't measure
- NEVER skip "explicitly out of scope" — scope creep starts with omitted exclusions
- NEVER leave open questions unowned
- If the input is too thin, ASK questions before drafting — a bad PRD wastes eng time
