# Next.js App Router Skill — React Best Practices for Claude Code, Cursor, Copilot

> **Design and review Next.js 14/15 App Router apps like a senior frontend engineer.** Server Components, streaming with Suspense, cache tags, Server Actions, and Core Web Vitals — enforced by your AI coding agent.

**Keywords**: next.js app router best practices, react server components, next.js streaming, server actions, next.js caching, revalidateTag, core web vitals, next/image, next/font, react code review, next.js claude code skill, cursor next.js

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- frontend-react-nextjs
```

## What it does

- Blocks unnecessary `'use client'` — pushes it as deep as possible
- Enforces correct **fetch cache semantics** (`no-store`, `revalidate`, `tags`)
- Requires **Suspense boundaries** on slow sections for streaming
- Standardizes **Server Actions** (zod validation, `revalidateTag`/`revalidatePath`)
- Enforces `next/image` with `width`/`height` (no CLS) and `next/font` with `display: 'swap'`
- Requires `metadata` / `generateMetadata` on every route (SEO)

## When it triggers

- Repo has `next` + `app/` directory
- "Review this Next.js page" / "design a route" / "review this component"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [frontend-vue-nuxt](../frontend-vue-nuxt) — Nuxt equivalent
- [api-design-node-express](../api-design-node-express) — Node backend for a Next.js frontend
- [e2e-testing](../e2e-testing) — Playwright tests for your Next.js app
