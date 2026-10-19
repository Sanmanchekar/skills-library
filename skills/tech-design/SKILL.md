---
name: tech-design
description: Write a technical design doc (TDD / design doc / RFC) that sits between the PRD and the ADRs — goals and non-goals, current state, proposed design (components, data model, APIs, sequence diagram), alternatives considered, rollout and migration plan, risks, observability, and open questions. Reads the existing code to ground the "current state" section, and flags every decision that deserves its own ADR. Triggered when the user says "write a design doc", "tech spec for X", "RFC for this feature", "how should we build this", or hands over a PRD and asks for the engineering plan.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# tech-design

## When to use

- User says: "write a design doc", "tech spec for X", "RFC", "engineering design", "how should we build this"
- User hands over a PRD / ticket and asks for the implementation plan before coding
- Change touches 2+ services, a shared data model, a public API, or needs a migration
- Skip for a single-file change with no new interface — a good PR description is enough

## Where it fits

```
prd-writer (what + why)  →  tech-design (how)  →  adr (one decision, frozen)  →  code
```

## Steps

1. **Collect inputs** — PRD / ticket, constraints (deadline, compliance, budget, SLOs), the repos involved. If thin, ask 3 questions first:
   - What does success look like, measurably?
   - What is explicitly out of scope?
   - What existing system does this replace or extend?
2. **Ground current state in code** — Grep/Read the modules, schemas, routes, and queues that will change. Cite `path:line`. Never describe current state from memory.
3. **Write goals and non-goals** — goals are measurable; non-goals name tempting adjacent work you are NOT doing.
4. **Draft the proposed design** — components, data model, API surface, one sequence diagram for the main flow and one for the main failure.
5. **List at least 2 alternatives** — including "do nothing" or "extend the existing thing". Score them on the same criteria as the proposal.
6. **Plan rollout and migration** — flags, backfill, dual-write/read, ordering of deploys, rollback point for each step.
7. **Risks and observability** — each risk gets likelihood, impact, mitigation. Each new path gets a metric, a log, and an alert.
8. **Flag ADR candidates** — any decision that is hard to reverse, constrains future teams, or picks between real alternatives → mark `ADR-needed`.
9. **Open questions** — each with an owner and a decide-by date. Unknowns go here, not into vague prose.

## ADR-worthiness test

| Signal | ADR-needed? |
|---|---|
| Choosing a datastore, queue, protocol, or framework | Yes |
| New service boundary or ownership change | Yes |
| Public API shape or versioning policy | Yes |
| Irreversible data migration | Yes |
| Library choice inside one module, easily swapped | No |
| Naming, folder layout, internal helper shape | No |

## Output format

````markdown
# Design — <feature name>

- **Status**: Draft | In review | Approved | Superseded
- **Author**: @<handle>  **Reviewers**: @<handle>, @<handle>
- **PRD**: <link>  **Date**: YYYY-MM-DD

## 1. Goals
- G1: <measurable outcome>
## 2. Non-goals
- NG1: <adjacent work explicitly excluded>
## 3. Current state
<what exists today, with `path:line` citations>
## 4. Proposed design
### 4.1 Components
| Component | Responsibility | New / changed |
### 4.2 Data model
<tables / fields / indexes, with nullability and ownership>
### 4.3 APIs
<endpoint or message, request, response, errors — or link to api-contract output>
### 4.4 Sequence
```mermaid
sequenceDiagram
```
## 5. Alternatives considered
| Option | Pros | Cons | Why not |
## 6. Rollout & migration
| Step | Action | Flag / gate | Rollback |
## 7. Risks
| Risk | Likelihood | Impact | Mitigation |
## 8. Observability
| Signal | Name | Alert threshold |
## 9. ADR candidates
- [ ] ADR-needed: <decision> — <why it is hard to reverse>
## 10. Open questions
| Question | Owner | Decide by |
````

## Example

**Input**: "PRD: let customers cancel an order within 30 minutes of placing it. orders-service + payments-api."

**Output (excerpt)**:

```markdown
## 1. Goals
- G1: 95% of eligible cancellations complete in < 2 s end to end
## 2. Non-goals
- NG1: partial cancellation of line items
## 3. Current state
- `orders-service/app/orders/models.py:41` — `status` enum has no CANCELLED state
- `payments-api/src/refunds.ts:88` — refund endpoint exists, not idempotent
## 6. Rollout & migration
| Step | Action | Flag / gate | Rollback |
|---|---|---|---|
| 1 | Add CANCELLED to enum (additive migration) | none | leave in place |
| 2 | Ship cancel endpoint behind `orders.cancel-window` | 1% → 100% | flag off |
## 9. ADR candidates
- [ ] ADR-needed: saga (orders → payments) vs synchronous refund call — sets the pattern for all future compensations
## 10. Open questions
| Question | Owner | Decide by |
|---|---|---|
| Refund if payment is still pending capture? | @payments-lead | 2026-11-01 |
```

## Rules

- NEVER describe current state without reading the code — cite `path:line`
- NEVER skip non-goals — scope creep starts where non-goals are missing
- NEVER present one option — at least 2 alternatives, scored on the same criteria
- NEVER leave a rollout step without a rollback
- ALWAYS mark irreversible or cross-team decisions `ADR-needed` instead of burying them in prose
- ALWAYS give every open question an owner and a date
- ALWAYS hand API detail to `api-contract` and abuse cases to `threat-model` rather than inlining a half-version

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: plan · **Agent**: `plan` · **Loop**: `design`
- **Reads**: `prd` (from `.lifecycle/<run>/` when present)
- **Writes**: `design` → `design.md`
- **Comes after**: capability-extraction, db-scoping, prd-writer
- **Hand off to**:
  - `threat-model` — if: _Does the design add a trust boundary, auth path, or new external input?_
  - `adr` — if: _Did the design make a hard-to-reverse choice between real alternatives?_
  - `api-contract` — if: _Does the design add or change an API?_
  - `feature-flag-rollout` — if: _Is the change risky enough to ship dark behind a flag?_
  - `estimation` — always
  - `reconciliation-design` — if: _Does the design move money between systems whose records must agree?_

When the step is done, record it so the next skill can pick up the output:
`route.py run record tech-design --artifact design=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
