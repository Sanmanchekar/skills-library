# Capability Extraction Skill — Evidence-Backed Argument for a Shared Service

> **Anyone can say "centralize it." This skill produces the contract and the migration order.** Scans your repo/services for a cross-cutting capability implemented locally and repeatedly (notifications, PDF generation, file upload, audit log, feature flags, scheduling), inventories every call site, quantifies duplication and coupling smells, then hands you a wire contract and a strangler-pattern migration sequenced by risk × ownership.

**Keywords**: capability extraction, extract microservice, strangler pattern, notification service extraction, audit log service, centralize cross-cutting concerns, shared service argument, ai microservice extraction, event contract design, kafka topic design, sync vs async decision, capability extraction claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- capability-extraction
```

## What it does

- **Capability as an argument** — one skill covers `notifications`, `pdf-generation`, `file-upload`, `audit-log`, `feature-flags`, `scheduling`, and any user-defined capability (asks for grep patterns if not canonical)
- **Detection tables per capability** — grep patterns for provider SDKs, direct-send calls, template rendering, retry loops, opt-out checks
- **Coupling smell classification** — in-transaction, request-path, no-idempotency (this is the actual signal, not just duplication)
- **Evidence packet output** with file:line inventory reviewers can verify — no vibes-based recommendations
- **Contract design** — transport decision table, sync-vs-async decision tree, event schema with mandatory fields (`event_id`, `idempotency_key`, `tenant_id`, versioned event type)
- **Strangler-pattern migration** in 5 phases, sequenced by coupling severity × owner availability

## Why it exists

The high-value output is the last four lines of the packet: **contract, transport, sync/async rationale, migration order**. Anyone can spot duplication. What's expensive to produce is a schema concrete enough to build against and a rollout order that de-risks the highest-blast-radius site first.

## When it triggers

- "Extract X into a service"
- "Centralize Y"
- "Argue for a notification / audit / PDF service"
- "We have too many places doing Z"
- Monorepo / multi-repo audit before writing an ADR

## Example evidence packet (excerpt)

```
Capability: notifications
Found in: 6 services, 23 call sites, 4 providers
Duplicated: template rendering (4x), retry logic (5x),
            opt-out checks (2x — inconsistent)
Blast radius: SMTP timeout blocks payment commit in
            payments_backend/payments/tasks.py:142

Recommendation: extract notification-service
Contract:  Kafka topic `notification.requested.v1`
Sync vs async: async default; sync only for OTP
            (caller needs delivery ack)
Migration:  strangler — new sends via topic,
            backfill 23 call sites by service (5 phases)
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [adr](../adr) — the extraction ADR the packet feeds into
- [refactor](../refactor) — mechanical steps within a single service during backfill
- [db-migration](../db-migration) — strangler pattern for schema shares the same shape
- [observability](../observability) — dashboards the new service will need on day one
