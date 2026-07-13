---
name: frontend-vue-nuxt
description: Design or review a Nuxt 3 (Vue 3) frontend. Enforces `<script setup>` + Composition API, composables in `composables/`, useFetch vs $fetch choice, server routes (`server/api/`), hydration correctness, SEO via useSeoMeta, and Core Web Vitals. Triggered when the user asks to design/review a Nuxt page, component, composable, or server route.
---

# frontend-vue-nuxt

## When to use

- Repo has `nuxt` in package.json
- User asks: "review this Nuxt page", "design a Nuxt route", "how should I structure this composable"

## Design checklist

### Component style
- **Composition API only** — `<script setup lang="ts">` — no Options API in new code
- Single-file components (`.vue`) — logic in `<script setup>`, template minimal
- Extract reusable logic into `composables/useX.ts`

### Data fetching
- **`useFetch`** for SSR-safe data loading in pages and components — dedupes across server/client
- **`$fetch`** for imperative calls (event handlers, mutations) — client or server
- **`useAsyncData`** for non-fetch async data (e.g., DB queries in server-only)
- Never call `fetch()` directly — always Nuxt's wrappers so caching + SSR hydration works

### Server routes
- Under `server/api/*.ts` — every file becomes an endpoint
- Use `defineEventHandler` — access `readBody`, `getQuery`, `getRouterParam`
- Validate input with `zod` or `valibot`
- Return plain objects — Nuxt serializes

### Hydration correctness
- Never render different content on server vs client without `<ClientOnly>` wrapper
- `useState('key', () => ...)` for shared reactive state — keys prevent duplicate creation across SSR/client
- Avoid `window`/`document` at setup top-level — guard with `if (process.client)` or `onMounted`

### Routing
- File-based: `pages/orders/[id].vue`
- Navigate with `<NuxtLink>` — never raw `<a>` for internal routes
- Middleware: `middleware/auth.ts` — declarative auth guards

### SEO / metadata
- `useSeoMeta({ title, description, ogImage })` on every page
- Dynamic OG images via `@nuxt/og-image`
- `useHead` for `<link rel="canonical">`, structured data

### Images and Core Web Vitals
- `<NuxtImg>` from `@nuxt/image` — auto-resize, lazy, format
- Above-the-fold: `preload`
- Explicit `width`/`height` — no CLS
- Fonts via `@nuxt/fonts` (`display: 'swap'`)

## Rules

- NEVER mix Options API and Composition API in new code
- NEVER call `useFetch` inside an event handler — it's SSR/setup only; use `$fetch` there
- NEVER access `window` / `document` at `<script setup>` top level
- ALWAYS give `useState('key', ...)` an explicit key — auto keys break SSR
- ALWAYS put SEO metadata on every page (`useSeoMeta`)
