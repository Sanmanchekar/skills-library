# RCA / Root Cause Analysis Skill — Incident Postmortem Generator for AI Coding Agents

> **Turn an outage into a real RCA — not just "the bug was fixed".** Six-phase investigation (symptom → timeline → hypotheses → evidence → root cause → action items) so your AI agent stops hand-waving at "human error".

**Keywords**: root cause analysis, rca automation, incident postmortem generator, ai postmortem, sre skill, blameless postmortem, incident timeline, contributing factors, action item generator

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- rca
```

## What it does

- Enforces a **six-phase investigation** — no short-circuiting to "the fix"
- Reconstructs an absolute-UTC timeline of deploys, alerts, and mitigations
- Forces every root-cause claim to cite a specific artifact (log, metric, commit)
- Separates **root cause** from **contributing factors** — the systemic gaps that let the root cause become an outage
- Emits action items classified as **prevent / detect / respond**, each with an owner

## When it triggers

- "RCA for incident X"
- "Root cause of Y"
- "Write the postmortem"
- Pasted stack trace + timeline

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [runbook](../runbook) — generate the runbook the action items called for
- [observability](../observability) — build the dashboards the "detect" action items called for
- [code-review](../code-review) — catch the class of bug before it ships next time
