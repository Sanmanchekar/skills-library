# PRD Writer Skill — Product Requirements Document Generator for Claude Code, Cursor

> **Turn a rough Slack thread or customer ask into a rigorous PRD.** Problem, target user, success metrics, explicit out-of-scope, MoSCoW requirements, open questions with owners, and a rollout plan.

**Keywords**: prd writer, product requirements document, ai prd generator, product spec generator, jobs to be done template, moscow prioritization, ai product manager, prd claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- prd-writer
```

## What it does

- Enforces a **strict PRD section order** — problem, user, metrics, scope, UX, requirements, open questions, rollout, risks, timeline
- Requires **explicit "out of scope"** — scope creep starts with omitted exclusions
- Blocks vague metrics — every metric has a target AND a time window
- Every open question has an **owner and due date**
- **Interview mode**: asks sharpening questions when input is too thin
- Uses **MoSCoW** so priorities are forced, not implied

## When it triggers

- "Write a PRD"
- "Spec this out"
- "Turn this into a doc"
- Rough feature idea / Slack thread / customer request pasted

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [release-notes](../release-notes) — write the release notes when it ships
- [adr](../adr) — architecture decisions the PRD forces
- [pr-description](../pr-description) — engineering PRs that trace back to the PRD
