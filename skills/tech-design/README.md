# Tech Design Doc Skill — Technical Design Document & RFC Writer for Claude Code, Cursor, Copilot

> **Write technical design docs and RFCs grounded in your actual code.** Goals, non-goals, data model, APIs, sequence diagrams, alternatives, rollout, risks — and a list of decisions that need their own ADR.

**Keywords**: technical design document, design doc template, tech spec generator, engineering rfc, software design doc ai, system design document, design doc claude code skill, tdd template

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- tech-design
```

## What it does

- Bridges **PRD → design → ADR** — the "how" layer between product intent and frozen decisions
- **Grounds current state in code** — cites `path:line` instead of describing the system from memory
- Forces **goals and non-goals**, with measurable goals
- Produces **components, data model, APIs, and a mermaid sequence diagram** for the main and failure flows
- Requires **at least 2 alternatives** scored on the same criteria
- **Rollout & migration table** where every step has a flag/gate and a rollback
- **Risks, observability, open questions** — each with owner and date
- **Flags ADR candidates** — hard-to-reverse decisions get pulled out for their own record

## When it triggers

- "Write a design doc for X"
- "Tech spec / RFC for this feature"
- "How should we build this?"
- A PRD handed over with a request for the engineering plan

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [prd-writer](../prd-writer) — the PRD this design implements
- [adr](../adr) — record each flagged decision
- [api-contract](../api-contract) — contract-first detail for the APIs section
- [threat-model](../threat-model) — design-time security pass on the proposal
- [feature-flag-rollout](../feature-flag-rollout) — plan the flagged rollout steps
- [db-migration](../db-migration) — safe migrations for the data model changes
- [estimation](../estimation) — size the work once the design is approved
