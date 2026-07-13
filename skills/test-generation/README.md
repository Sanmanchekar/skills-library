# Test Generation Skill — Unit & Integration Tests for Claude Code, Cursor, Copilot

> **Generate real, edge-case-aware unit and integration tests from any source file.** Auto-detects pytest, jest, vitest, go test, rspec, or JUnit and matches your repo's conventions.

**Keywords**: ai test generation, unit test generator, pytest test generation, jest test generation, vitest ai, go test generator, ai tdd, table-driven tests, edge case coverage, test generation claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- test-generation
```

## What it does

- **Auto-detects** the test framework in your repo and matches its conventions
- Builds a **case matrix** (happy / boundary / null / type-edge / error / integration) before writing tests
- Uses **table-driven / parametrized** tests when the shape repeats
- Enforces **AAA structure** (Arrange, Act, Assert)
- Blocks tautological tests and private-state assertions
- Uses **sentence-style test names** for readable failures

## When it triggers

- "Write tests for X"
- "Add tests to Y"
- "What tests should this have"
- Function / class pasted with test request

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [e2e-testing](../e2e-testing) — Playwright E2E for user flows
- [bug-repro](../bug-repro) — turn a bug report into a failing test
- [code-review](../code-review) — reviewers who ask for tests
