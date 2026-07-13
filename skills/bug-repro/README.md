# Bug Repro Skill — Minimal Reproduction Generator for Claude Code, Cursor, Copilot

> **Turn a vague bug report into a minimal reproduction and a failing test.** Structured extraction (observed / expected / environment / trigger), affected code path identification, and a test that fails on main.

**Keywords**: bug reproduction, minimal repro generator, ai bug repro, failing test generator, bug triage, customer bug repro, ai qa, repro claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- bug-repro
```

## What it does

- Extracts **observed / expected / environment / trigger / frequency** from any raw report
- **Reduces to minimum** — strips unrelated setup, shrinks payloads, cuts unnecessary steps
- Identifies the affected code path by **reading the relevant file**, not guessing
- Produces a **failing test** — a repro without a test is a description
- Says "cannot repro" honestly when the info is incomplete, and asks for what's missing

## When it triggers

- Bug report / support ticket / customer message pasted
- Stack trace + "reproduce this"
- "Why is X happening" without a repro

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [test-generation](../test-generation) — expand the failing test into a suite
- [rca](../rca) — after repro, root-cause the class of bug
- [code-review](../code-review) — catch it next time
