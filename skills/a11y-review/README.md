# Accessibility Review Skill — WCAG 2.2 AA Audit with axe-core & Screen Readers for Claude Code, Cursor, Copilot

> **Ship UI everyone can use.** Reviews frontend changes against WCAG 2.2 AA — semantics, ARIA, keyboard, focus, labels, contrast, forms, live regions — with axe-core, Playwright, and a manual screen-reader checklist. Every finding cites the success criterion and comes with a fix.

**Keywords**: accessibility review, a11y audit, wcag 2.2 aa, wcag checklist, axe-core, @axe-core/playwright, eslint-plugin-jsx-a11y, screen reader testing, nvda voiceover, keyboard navigation, focus management, color contrast, aria best practices, accessibility claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- a11y-review
```

## What it does

- Walks a **16-row WCAG 2.2 AA checklist** — semantics, ARIA, keyboard, focus order, visible focus, labels, contrast, motion, forms, alt text, live regions, target size, reflow
- Enforces the **first rule of ARIA** — native elements before roles
- Runs **automated checks** with eslint-plugin-jsx-a11y and **axe-core via Playwright**
- Adds a **manual screen-reader checklist** (NVDA, VoiceOver, TalkBack) and says what was assumed vs. run
- Emits **severity-tagged findings** (CRITICAL / HIGH / MEDIUM / LOW) with **WCAG SC IDs** and ready-to-apply code fixes
- Recommends an **axe regression test** per fixed page

## When it triggers

- "Accessibility review" / "a11y check" / "is this WCAG compliant?"
- "Check this for screen readers" / "audit keyboard navigation"
- A PR touching components, forms, modals, or design tokens

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [frontend-react-nextjs](../frontend-react-nextjs) — build accessible components from the start
- [frontend-vue-nuxt](../frontend-vue-nuxt) — same, for Vue / Nuxt
- [e2e-testing](../e2e-testing) — host the axe checks in your Playwright suite
- [code-review](../code-review) — general correctness review alongside a11y
