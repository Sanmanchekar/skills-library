# Lifecycle Router — Invoke the Right AI Coding Skill at the Right Time, for Claude Code, Cursor, Copilot

> **Stop remembering which skill to run.** The router reads your prompt, your diff, or a lifecycle event (commit, PR, deploy, alert, bug report), picks the skills that apply, hands each one the previous skill's output, and stops loops before they run away.

**Keywords**: ai skill router, claude code skills orchestration, agent workflow sdlc, development lifecycle automation, ai pr reviewer fan-out, claude code hooks, agentic loop guardrails, skill invocation workflow, cursor rules router

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- lifecycle-router
```

The whole lifecycle, with Claude Code subagents and hooks:

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- --bundle all --agent claude-code --with-hooks
```

## What it does

- **Prompts → skills**: matches intents, file globs, added diff lines and lifecycle events against every skill's triggers, then ranks the matches and says why each one matched
- **Agents**: one `lifecycle-<phase>` subagent per phase (plan, build, verify, ship, operate, learn, maintain), each dispatching only its own skills
- **Loops**: `loop tick` enforces a hard iteration cap, a stall stop (the metric isn't improving) and human checkpoints for the review, debug, perf, incident and rollout loops
- **Graph**: `next` evaluates edge conditions (always, path match, content match, artifact present, findings severity, or a question for a human)
- **Reviewer fan-out**: on a PR, runs every specialist reviewer the diff triggers (security, idempotency, money, migration, IaC, a11y…), most specific first, with `code-review` last
- **Hand-off contract**: artifacts live in `.lifecycle/<run>/`, with a shared `findings.json` schema so reviewers dedupe instead of repeating each other
- **Hooks**: Claude Code (prompt, `git commit`, `gh pr create`, deploy commands, file edits), a git `pre-commit` hook, and a GitHub Action that keeps one sticky PR comment. All of them only hint and never block
- **Stdlib-only Python** — no dependencies at runtime

## When it triggers

- "Which skill should I use?" / "What's next?"
- Multi-step work that spans several skills
- Before a commit, PR, or deploy
- When an alert fires or a bug report comes in

## Example

```text
$ route.py route --prompt "make this refund endpoint safe to retry" --git
phase: verify · agent: lifecycle-verify · loop: review
  1. idempotency-review  (score 5: prompt matches /safe to retry/; 1 file(s) match, e.g. src/payments/refund.py)
  2. money-handling  (score 2: diff adds /\b(amount|...)\b/)
next after idempotency-review:
  - commit-message [ready] always
```

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

The router script and git/CI hooks work with any agent. Subagents and in-session hooks are Claude Code only.

## Related skills

- [code-review](../code-review) — the general reviewer at the end of every fan-out
- [complexity-aware-coding](../complexity-aware-coding) — the build-phase entry point
- [oncall-triage](../oncall-triage) — the operate-phase entry point
- [tech-debt-scan](../tech-debt-scan) — the maintain-phase entry point
