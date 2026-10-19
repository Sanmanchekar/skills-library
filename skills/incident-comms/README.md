# Incident Communication Skill — Status Page Updates & Exec Summaries for Claude Code, Cursor, Copilot

> **Say the right thing, on time, during an outage.** Incident roles, update cadence by severity, status-page templates, customer-safe language, and exec summaries.

**Keywords**: incident communication, status page update template, incident comms, outage notification, incident commander, exec incident summary, customer incident message, sre skill, incident comms claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- incident-comms
```

## What it does

- Assigns **roles** — incident commander, comms lead, ops lead, scribe
- Sets **update cadence by severity** for internal channel, status page, and execs
- Drafts **status-page updates** for every state: investigating, identified, monitoring, resolved
- Enforces **customer-facing language rules** — no blame, no speculation, no internal jargon, always a next-update time
- Produces an **exec / stakeholder summary** with impact, status, next step, and asks
- Keeps a **comms log** and hands it to the RCA after resolution

## When it triggers

- "Draft a status page update"
- "What do we tell customers?"
- "Send an exec summary for this incident"
- "I'm comms lead — write the next update"

## Example

Channel notes "checkout 502s since 13:40, ~12%, rolling back" → status page: "We are investigating errors affecting checkout. Some customers may be unable to complete purchases. Next update by 14:15 UTC." — plus a matching internal update and exec summary.

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [oncall-triage](../oncall-triage) — severity and mitigation decisions
- [runbook](../runbook) — the mitigation steps being executed
- [rca](../rca) — post-incident analysis that consumes the comms log
- [retro](../retro) — team retrospective after the incident
