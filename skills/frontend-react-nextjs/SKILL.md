---
name: frontend-react-nextjs
description: Design or review a Next.js (App Router) frontend. Enforces Server Component defaults, correct `use client` boundary placement, streaming with Suspense, caching semantics (fetch cache, revalidateTag, revalidatePath), Server Actions patterns, and Core Web Vitals (LCP image priority, font swap, no CLS). Triggered when the user asks to design/review a Next.js page, route, component, server action, or layout.
---

# frontend-react-nextjs

## When to use

- Repo has `next` in package.json and an `app/` directory
- User asks: "review this Next.js page", "design a Next.js route", "how should I structure this component"

## Design checklist

### Server vs Client components
- **Server Components are the default** — do NOT add `'use client'` unless the component uses state, effects, browser APIs, or event handlers
- Push `'use client'` as **deep** as possible — a leaf that needs state is a client component; its parent stays server
- NEVER pass non-serializable props (functions, class instances) from server to client

### Data fetching
- Fetch in Server Components with plain `fetch()` — automatically deduped and cached
- Cache semantics:
  - `fetch(url)` — cached indefinitely (default)
  - `fetch(url, { cache: 'no-store' })` — always fresh
  - `fetch(url, { next: { revalidate: 60 } })` — ISR
  - `fetch(url, { next: { tags: ['orders'] } })` — tag-based invalidation via `revalidateTag('orders')`
- Never fetch in `useEffect` if you can fetch on the server

### Streaming
- Wrap slow sections in `<Suspense fallback={<Skeleton />}>` so the shell renders instantly
- Use `loading.tsx` for route-level streaming

### Server Actions
- Prefer Server Actions over API routes for mutations
- Every Server Action starts with `'use server'`
- Validate input with zod at the top of the action
- Call `revalidateTag` / `revalidatePath` after successful writes

### Routing conventions
- `app/orders/page.tsx` — page
- `app/orders/[id]/page.tsx` — dynamic route
- `app/orders/loading.tsx` — streaming fallback
- `app/orders/error.tsx` — error boundary
- `app/orders/not-found.tsx` — 404

### Images and fonts (Core Web Vitals)
- Use `next/image` — never raw `<img>` for content images
- Above-the-fold hero image: `priority`
- Explicit `width`/`height` — prevents CLS
- Fonts via `next/font` (`display: 'swap'`)

### Metadata / SEO
- Every route exports `metadata` OR `generateMetadata`
- Dynamic routes: `generateStaticParams` for prerender-at-build

### State
- Server state → `useSWR` or React Query (client) OR fetch on server (preferred)
- Client-only state → `useState` / `useReducer`
- URL state → `useSearchParams` — don't duplicate in local state

## Rules

- NEVER put `'use client'` at the root layout — it disables server-rendering for the whole tree
- NEVER read `cookies()` / `headers()` inside a component that isn't dynamic (forces the whole page dynamic — do it intentionally)
- NEVER call a Server Action from a Server Component — it's for client-triggered mutations
- ALWAYS validate Server Action input with zod
- ALWAYS specify `width` / `height` on `next/image`
