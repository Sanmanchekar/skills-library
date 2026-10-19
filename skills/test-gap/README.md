# Test Gap Skill — Find Missing Tests & Coverage Gaps in a PR for Claude Code, Cursor, Copilot

> **Find the tests your diff is missing before you merge.** Maps changed functions and branches to existing tests, runs a coverage diff, ranks untested error paths and boundaries by risk, and emits failing-by-default test skeletons in your framework.

**Keywords**: missing tests finder, test coverage gaps, diff coverage, diff-cover, pr test coverage, untested branches, branch coverage analysis, test skeleton generator, pytest coverage diff, jest coverage, test gap claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- test-gap
```

## What it does

- Reads the **diff** and maps every changed function and branch to the tests that exercise it
- Runs a **coverage diff** when possible — diff-cover, coverage.py, c8 / nyc, `go test -coverprofile`, JaCoCo
- **Enumerates branches** explicitly — line coverage is treated as a floor, not proof
- Flags **"touched" tests** that execute code without asserting on its outcome
- **Ranks gaps by risk** — money, auth, error paths, and boundaries first
- Emits **failing-by-default skeletons** in your repo's framework and naming style
- Hands off to `test-generation` to fill the bodies

## When it triggers

- "What tests am I missing?"
- "Test gaps in this PR"
- "Is this diff covered?"
- "What should I test before merging?"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [test-generation](../test-generation) — fill the skeletons with real tests
- [code-review](../code-review) — the review that asks "where are the tests?"
- [e2e-testing](../e2e-testing) — gaps that need a user-flow test, not a unit test
- [bug-repro](../bug-repro) — turn a bug into the first failing test
