# E2E Testing Skill — Playwright Test Generation for Claude Code, Cursor, Copilot

> **Generate stable, non-flaky Playwright end-to-end tests from any feature spec or user flow.** Stack-agnostic — works with Next.js, Nuxt, Django, Rails, or plain HTML. Role-based locators, network mocking, web-first assertions.

**Keywords**: playwright test generation, e2e testing ai, playwright best practices, ai e2e tests, stable playwright selectors, playwright role locators, ai qa automation, playwright claude code skill, cursor playwright

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- e2e-testing
```

## What it does

- Prefers **role/label/testid** locators — blocks brittle CSS selectors
- Uses **web-first assertions** (`expect(locator).toBeVisible()`) — no `waitForTimeout`
- **Mocks the network** at `page.route()` — no dependency on a live backend
- Generates happy path + validation error + server error + empty state — not just the happy path
- Flags missing `data-testid` attributes BEFORE writing tests over brittle selectors

## When it triggers

- "Write E2E tests for X"
- "Test this flow"
- "Generate Playwright tests"
- User story / feature spec pasted

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [test-generation](../test-generation) — unit + integration tests
- [bug-repro](../bug-repro) — turn a bug report into a failing test
- [frontend-react-nextjs](../frontend-react-nextjs) / [frontend-vue-nuxt](../frontend-vue-nuxt) — the apps under test
