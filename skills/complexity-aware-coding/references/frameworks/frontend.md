# Frontend: React / Next.js / Vue / Angular

- Rendering cost ≈ (number of components re-rendered) × (work per render). Keep expensive computations out of render.
- O(n²) in render: `items.map(i => others.find(o => o.id === i.otherId))` — precompute a `Map` with `useMemo`/`computed`.
- Long lists (>~200 rows): virtualize (react-window, TanStack Virtual, vue-virtual-scroller, Angular CDK virtual scroll).
- Stable keys on list items (`key` / `:key` / `track`), never array index for reorderable lists.
- React: `useMemo`/`useCallback`/`React.memo` for expensive derivations and props to memoized children; avoid storing derived state; split contexts so updates don't re-render the whole tree.
- Vue: prefer `computed` over methods in templates; avoid deep watchers on large objects; `shallowRef` for big immutable data.
- Angular: `OnPush` change detection; `trackBy`/`track` in loops; pure pipes instead of template method calls.
- Debounce/throttle input-driven work (search, resize, scroll).
- Paginate or infinite-scroll server data; never fetch unbounded lists.
- Next.js/SSR: avoid waterfalls (parallelize fetches), cache server data, watch bundle size (code-split heavy libraries).
