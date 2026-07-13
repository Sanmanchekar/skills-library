---
name: e2e-testing
description: Generate end-to-end Playwright tests from a feature spec, user flow, or UI walkthrough. Stack-agnostic — works for Next.js, Nuxt, Django, Rails, or plain HTML. Produces tests using web-first assertions, role-based locators, network mocking, and stable selectors — no CSS or nth-child. Triggered when the user asks to write E2E tests, "test this flow", or provides a user story.
---

# e2e-testing

## When to use

- User asks: "write E2E tests for X", "test this flow", "generate Playwright tests"
- User provides a user story, feature spec, or Figma link with a walkthrough

## Steps

1. **Read the app**. Find the relevant page component(s) or route(s). Note the data-testid attributes, roles, and labels already present.
2. **If stable selectors are missing** — flag it and suggest `data-testid` additions BEFORE writing tests. Tests over brittle selectors are worse than no tests.
3. **Write the flow as user actions**, not implementation details:
   - "user clicks 'Sign in'"  →  `page.getByRole('button', { name: /sign in/i }).click()`
   - "user types email"  →  `page.getByLabel('Email').fill('...')`
4. **Assert web-first** — `expect(locator).toBeVisible()`, `toHaveText()`, `toHaveURL()`. Never `waitForTimeout`.
5. **Mock the network** at the boundary — `page.route('**/api/orders', ...)` — so tests don't need a running backend.
6. **Cover**: happy path, one validation error, one server error (500), one empty state.

## Locator priority (highest → lowest)

1. `getByRole('button', { name: /submit/i })`
2. `getByLabel('Email')`
3. `getByPlaceholder('you@example.com')`
4. `getByText(/welcome back/i)`
5. `getByTestId('order-card-42')`
6. CSS / XPath — LAST RESORT, flag as tech debt

## Output template

```typescript
import { test, expect } from '@playwright/test';

test.describe('Order checkout', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/products', (route) =>
      route.fulfill({ json: [{ id: 1, name: 'Widget', price: 10 }] })
    );
    await page.goto('/checkout');
  });

  test('happy path — user completes checkout', async ({ page }) => {
    await page.getByLabel('Card number').fill('4242 4242 4242 4242');
    await page.getByRole('button', { name: /pay/i }).click();
    await expect(page).toHaveURL(/\/orders\/\w+\/confirmation/);
    await expect(page.getByText(/order confirmed/i)).toBeVisible();
  });

  test('server error — user sees retry option', async ({ page }) => {
    await page.route('**/api/orders', (route) => route.fulfill({ status: 500 }));
    await page.getByRole('button', { name: /pay/i }).click();
    await expect(page.getByText(/something went wrong/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /try again/i })).toBeVisible();
  });
});
```

## Rules

- NEVER use `page.waitForTimeout(...)` — use web-first assertions with auto-wait
- NEVER use CSS `.class-name` or `#id` selectors — use role/label/testid
- NEVER hit the real backend from an E2E test — mock at the route
- ALWAYS test one flow per `test()` — no god-tests
- ALWAYS include an error-path test — happy-path-only tests give false confidence
