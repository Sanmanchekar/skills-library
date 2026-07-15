# Debug Skill — Systematic Debugging Loop for Claude Code, Cursor, Copilot

> **Stop flailing with print statements. Debug the way engineers with 20 years of experience do it.** Reproduce → hypothesize → instrument (ONE probe) → read evidence → fix + regression test. Stack-agnostic — works for Python, Node, Go, Java, C++, Rust, Ruby, or any runtime.

**Keywords**: ai debugging, systematic debugging, debug method, hypothesis-driven debugging, print statement debugging, heisenbug, flaky test debugging, ai bug fix, debug claude code skill, cursor debug

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- debug
```

## What it does

- Enforces a **5-step loop**: reproduce → hypothesize (3+) → instrument (ONE probe) → read → fix + test
- **Stack-agnostic** — table of probe categories mapped to your runtime's native tools
- Requires **100% repro** before any hypothesis
- Requires **at least 3 hypotheses ranked** before touching code
- **One probe per iteration** — no scatter-shot debugging
- Every fix requires a **regression test** that fails before and passes after
- Named **anti-patterns table** to catch common bad habits
- Dedicated **heisenbug playbook** for bugs that vanish when observed

## When it triggers

- "Debug this" / "help me debug"
- "Why is X failing"
- Stack trace / test failure / unexpected output pasted
- Flaky or CI-only test failure

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [bug-repro](../bug-repro) — turn a bug report into a minimal reproduction
- [rca](../rca) — root-cause after the fix
- [test-generation](../test-generation) — regression tests
