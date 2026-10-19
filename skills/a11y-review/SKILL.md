---
name: a11y-review
description: Review frontend changes for accessibility against WCAG 2.2 AA — semantic HTML, roles and ARIA (first rule of ARIA), keyboard operability, focus order and visible focus, accessible names and labels, color contrast, motion, forms and error messaging, alt text, and live regions. Runs automated checks (axe-core, Playwright with @axe-core/playwright, eslint-plugin-jsx-a11y) plus a manual screen-reader checklist, and produces severity-tagged findings with WCAG success-criterion IDs and ready-to-apply fixes. Triggered when the user says "accessibility review", "a11y check", "is this WCAG compliant", "check this for screen readers", "audit keyboard navigation", or passes a UI diff for review.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# a11y-review

## When to use

- User says: "a11y review", "accessibility check", "WCAG audit", "screen reader check", "keyboard navigation audit"
- A PR touches components, templates, CSS, or design tokens (`.tsx/.jsx/.vue/.svelte/.html/.css`)
- New forms, modals, menus, tabs, carousels, toasts, or custom widgets
- A design-system color or spacing token changes (contrast and target-size risk)

## Severity

| Severity | Meaning |
|---|---|
| CRITICAL | Blocks a task entirely for some users (keyboard trap, unlabeled submit, inaccessible modal) |
| HIGH | Task possible but very hard (no visible focus, contrast < 3:1 on body text, errors not announced) |
| MEDIUM | Degraded experience (wrong heading order, redundant ARIA, missing autocomplete) |
| LOW | Best practice / polish (missing `lang` on inline foreign text, verbose alt) |

## Review checklist

| # | Area | Check | WCAG 2.2 SC |
|---|---|---|---|
| 1 | Semantics | Native elements first: `<button>`, `<a href>`, `<nav>`, `<main>`, `<h1-h6>`, `<ul>`, `<table>` — no clickable `<div>` | 1.3.1, 4.1.2 |
| 2 | ARIA | **First rule of ARIA**: don't use ARIA if a native element does it. No `role` that contradicts the element; required states (`aria-expanded`, `aria-selected`) kept in sync | 4.1.2 |
| 3 | Keyboard | Every interactive element reachable and operable with Tab / Shift+Tab / Enter / Space / Esc / arrows; no keyboard trap | 2.1.1, 2.1.2 |
| 4 | Focus order | DOM order matches visual order; no positive `tabindex`; focus moves into modals and returns to trigger on close | 2.4.3 |
| 5 | Visible focus | `:focus-visible` style present, not removed with `outline: none`; focused element not hidden by sticky headers | 2.4.7, 2.4.11 |
| 6 | Names & labels | Every control has an accessible name; `<label for>` or `aria-labelledby`; icon-only buttons have `aria-label`; visible label text included in the name | 1.3.1, 2.5.3, 4.1.2 |
| 7 | Contrast | Text ≥ 4.5:1 (≥ 3:1 for ≥ 24px / 18.66px bold); UI components and focus indicators ≥ 3:1 | 1.4.3, 1.4.11 |
| 8 | Color alone | Errors, status, links not conveyed by color only | 1.4.1 |
| 9 | Motion | Respect `prefers-reduced-motion`; auto-playing content > 5s can be paused; nothing flashes > 3/s | 2.2.2, 2.3.1, 2.3.3 |
| 10 | Forms & errors | Errors identified in text, linked via `aria-describedby`, `aria-invalid` set, focus moved to first error or summary; `autocomplete` on personal fields; no re-entry of known data | 3.3.1, 3.3.2, 3.3.3, 1.3.5, 3.3.7 |
| 11 | Images | Meaningful `<img>` has descriptive `alt`; decorative has `alt=""`; SVG icons `aria-hidden="true"` when labeled elsewhere | 1.1.1 |
| 12 | Live regions | Async status (toasts, "saved", search result counts) uses `role="status"` / `aria-live="polite"`; errors `role="alert"`; region exists in DOM before content changes | 4.1.3 |
| 13 | Structure | One `<h1>`, no skipped heading levels, landmarks present, skip link, page `<title>` and `lang` | 1.3.1, 2.4.1, 2.4.2, 3.1.1 |
| 14 | Targets | Pointer targets ≥ 24×24 CSS px or adequately spaced; drag actions have a single-pointer alternative | 2.5.8, 2.5.7 |
| 15 | Reflow & zoom | Usable at 320px width and 200% text zoom without horizontal scroll or clipped content | 1.4.4, 1.4.10 |
| 16 | Auth | No cognitive test (puzzle, transcription) without an alternative; paste allowed in password/OTP fields | 3.3.8 |

## Steps

1. **Scope** — list changed UI files from the diff; read each file fully (never review a component from its name).
2. **Run automated checks** where the repo supports them:
   - `npx eslint --ext .jsx,.tsx <files>` with `eslint-plugin-jsx-a11y` (or `eslint-plugin-vuejs-accessibility`)
   - Playwright + `@axe-core/playwright`: `new AxeBuilder({ page }).withTags(['wcag2a','wcag2aa','wcag21aa','wcag22aa']).analyze()`
   - If neither exists, recommend adding the Playwright axe test (see example) — don't skip the manual pass.
3. **Walk the review checklist** row by row against each changed component. Automated tools catch ~30–40% of issues; rows 3, 4, 6, 10, 12 need reading the code.
4. **Manual screen-reader pass** (state which combos were assumed vs. actually run):
   - [ ] NVDA + Firefox/Chrome (Windows), VoiceOver + Safari (macOS/iOS), TalkBack + Chrome (Android)
   - [ ] Tab through the flow: every stop announces name, role, state
   - [ ] Open/close each modal/menu: focus moves in, Esc closes, focus returns
   - [ ] Submit an invalid form: error is announced and reachable
   - [ ] Trigger each async update: live region announces once, not repeatedly
5. **Emit findings** — severity, file:line, WCAG SC ID, problem, who is affected, fix as a ready-to-apply code block.

## Example — input → output

Input:
```tsx
<div className="icon-btn" onClick={onDelete}><TrashIcon /></div>
```

Output:
```markdown
### [CRITICAL] Icon-only delete control is not keyboard operable or named — WCAG 2.1.1, 4.1.2
**File**: src/components/CartRow.tsx:31
**Problem**: `<div onClick>` is not focusable, has no role, and no accessible name.
**Affected**: keyboard users, screen-reader users, voice-control users.
**Fix**:
` ` `tsx
<button type="button" className="icon-btn" onClick={onDelete} aria-label="Remove item from cart">
  <TrashIcon aria-hidden="true" focusable="false" />
</button>
` ` `
```

```typescript
// tests/a11y/cart.spec.ts — Playwright + axe regression test
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('cart page has no WCAG 2.2 AA violations', async ({ page }) => {
  await page.goto('/cart');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```

## Output format

```markdown
## Accessibility review — <N> findings (WCAG 2.2 AA)

| # | Severity | File:Line | WCAG SC | Title |
|---|----------|-----------|---------|-------|
| 1 | CRITICAL | src/components/CartRow.tsx:31 | 2.1.1, 4.1.2 | Icon-only delete is a div |

### Automated results
| Tool | Ran? | Violations |
|---|---|---|
| eslint-plugin-jsx-a11y | yes/no | <n> |
| axe-core (Playwright) | yes/no | <n> |

### Manual screen-reader checklist
| Check | Result | Assumed or run |
|---|---|---|

### Findings
<one block per finding: severity, title, SC IDs, file:line, problem, affected users, fix code block>

**Assessment**: PASS | PASS WITH FIXES | FAIL (any CRITICAL)
```

## Rules

- NEVER add ARIA where a native element would do — prefer `<button>` over `role="button"`
- NEVER suggest `outline: none` without a replacement `:focus-visible` style
- NEVER claim "WCAG compliant" from automated tools alone — state what was checked manually
- NEVER use `aria-label` to hide a mismatch with visible label text (2.5.3)
- NEVER rely on color alone in a fix (e.g. red border only for errors)
- ALWAYS cite the WCAG 2.2 success-criterion ID on every finding
- ALWAYS give a ready-to-apply code fix, not "improve accessibility"
- ALWAYS recommend an automated axe regression test for each fixed page or component

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: verify · **Agent**: `verify`
- **Reads**: `diff` (from `.lifecycle/<run>/` when present)
- **Writes**: `findings` → `findings.json`
- **Comes after**: complexity-aware-coding, frontend-react-nextjs, frontend-vue-nuxt, pr-description

This skill works on its own; the hand-offs above are suggestions. If the `lifecycle-router` skill is installed, record the step so the next skill can pick up the output: `route.py run record a11y-review --artifact findings=<path>`. If it is not installed, skip this and just name the next skill to the user.
<!-- lifecycle:end -->
