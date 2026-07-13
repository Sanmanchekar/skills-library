# Nuxt 3 Skill — Vue Best Practices for Claude Code, Cursor, Copilot

> **Design and review Nuxt 3 (Vue 3) apps like a senior frontend engineer.** Composition API, useFetch vs $fetch, server routes, hydration correctness, SEO — enforced by your AI coding agent.

**Keywords**: nuxt 3 best practices, vue 3 composition api, nuxt useFetch, nuxt server routes, vue seo, useSeoMeta, nuxt hydration, nuxt image, nuxt claude code skill, cursor vue

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- frontend-vue-nuxt
```

## What it does

- Enforces `<script setup>` + Composition API — blocks Options API drift in new code
- Picks the right fetch primitive (**useFetch** in setup, **$fetch** in handlers)
- Catches hydration mismatches (raw `window`/`document` at setup top level)
- Requires `useSeoMeta` on every page
- Enforces `<NuxtImg>` with explicit width/height (no CLS)
- Standardizes server routes with input validation

## When it triggers

- Repo has `nuxt` in package.json
- "Review this Nuxt page" / "design a route" / "review this composable"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [frontend-react-nextjs](../frontend-react-nextjs) — Next.js equivalent
- [api-design-node-express](../api-design-node-express) — Node backend
- [e2e-testing](../e2e-testing) — Playwright tests for Nuxt apps
