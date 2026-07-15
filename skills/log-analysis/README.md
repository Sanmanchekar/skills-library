# Log Analysis Skill — Timeline Correlation for Claude Code, Cursor, Copilot

> **Turn raw logs into an incident timeline.** Parses JSON / plaintext / logfmt, joins across services by request_id, extracts retries and cascades, and surfaces the smallest set of lines that explains what happened.

**Keywords**: log analysis, log correlation, incident timeline, request id trace, retry storm detection, cascade failure, ai log parser, log analysis claude code skill, loki elasticsearch analysis

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- log-analysis
```

## What it does

- Auto-detects format (**JSON, plaintext, logfmt**) — normalizes to a common shape
- Normalizes all timestamps to **UTC**
- Correlates by `request_id` / `trace_id` — falls back to `(user_id, endpoint, ts window)` when absent
- Detects **retry storms, cascades, latency spikes, error bursts, missing correlations, log floods**
- Ranks request_ids by severity + latency + retry count
- Emits a **UTC-ordered timeline** with observations and suggested next steps
- Separates observations (from the logs) from inferences (its own reasoning)

## When it triggers

- Raw logs pasted with "what happened"
- "Correlate logs for X"
- "Trace request Y through the logs"
- "Build a timeline from these logs"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [rca](../rca) — feeds the timeline into the RCA
- [observability](../observability) — dashboards for the metrics the logs corroborate
- [runbook](../runbook) — link the timeline signals to a runbook
