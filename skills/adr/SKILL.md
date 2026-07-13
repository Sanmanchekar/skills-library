---
name: adr
description: Write an Architecture Decision Record (ADR / MADR format) capturing a technical decision — context, options considered, decision, consequences, and status. Numbered, dated, immutable. Triggered when the user asks to "write an ADR", "document this decision", or has just made an architectural choice.
---

# adr

## When to use

- User asks: "write an ADR for X", "document this decision"
- After a significant technical decision (framework choice, protocol, data model, boundary)
- Non-trivial refactor that constrains future choices

## Location

Store as `docs/adr/NNNN-slug.md` where `NNNN` is 4-digit sequential.

## Template (MADR-flavored)

```markdown
# ADR-0042 — Adopt Kafka for order events

- **Status**: Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](./XXXX-...)
- **Date**: 2026-07-14
- **Deciders**: @alice, @bob, @carol
- **Consulted**: @orders-team, @platform
- **Informed**: @all-eng

## Context

What forces are at play? What is the problem we're solving? 3-6 sentences.
Include the constraints (compliance, deadlines, existing infra) that filter the options.

## Options considered

### Option A — Kafka
- **Pros**: durable, replayable, ecosystem, ordering per partition
- **Cons**: ops overhead, cost, learning curve for team

### Option B — RabbitMQ
- **Pros**: simpler ops, existing infra, sufficient throughput
- **Cons**: no replay, weaker ordering guarantees

### Option C — Postgres LISTEN/NOTIFY
- **Pros**: no new infra, transactional with DB writes
- **Cons**: doesn't scale beyond ~10k msg/s, no persistence for offline consumers

## Decision

We adopt **Option A — Kafka** for order events.

## Rationale
1-3 paragraphs. Why did this option win? What tradeoff are we accepting?

## Consequences

### Positive
- Replay capability unblocks the analytics pipeline
- Per-partition ordering matches the domain (all events per order)

### Negative
- Ops burden: on-call rotation for Kafka
- +$X/month infra cost
- Team must learn Kafka semantics (idempotent producers, consumer groups)

### Neutral
- Requires a new CI job to spin up Kafka in integration tests

## Follow-ups
- [ ] Choose managed vs self-hosted (ADR-0043)
- [ ] Retention policy per topic (ADR-0044)
- [ ] Runbook for common Kafka failures (see [runbook](../runbook))
```

## Steps

1. **Find the next ADR number** — `ls docs/adr/ | sort | tail -1` (or start at 0001).
2. **Interview mode** if the user's input is thin — ask 3 questions before drafting:
   - What are you actually choosing between?
   - What constraints filter your options?
   - What happens if you don't decide?
3. **Fill EVERY section** — no empty "Consequences" ("we'll see"). If truly unknown, list follow-up ADRs.
4. **Options come first, then decision** — do NOT write the decision before enumerating alternatives. That's post-hoc rationalization.
5. **Consequences honest** — list the negatives. An ADR with no negatives is unsigned.

## Rules

- NEVER skip options — an ADR without alternatives is a diary entry
- NEVER edit an "Accepted" ADR — supersede it with a new one referencing the old
- NEVER handwave consequences — if you don't know, that's a follow-up ADR
- ALWAYS number sequentially, never reuse numbers
- ALWAYS date and list deciders — accountability is the point
