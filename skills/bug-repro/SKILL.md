---
name: bug-repro
description: Turn a raw bug report into a minimal, reliable reproduction. Extracts observed vs expected behavior, environment, exact steps, and produces a failing test that captures the bug. Triggered when the user shares a bug report, customer complaint, stack trace, or asks "how do I reproduce X".
---

# bug-repro

## When to use

- User pastes a bug report, support ticket, or customer message
- User shares a stack trace with "reproduce this"
- User asks "why is X happening" without a repro

## Steps

1. **Extract structured fields** from the raw report:

   | Field | What to fill |
   |---|---|
   | Observed | What actually happens (the user's words + your read) |
   | Expected | What should happen (from spec, docs, or common sense) |
   | Environment | OS, browser, app version, region, user tier |
   | Trigger | The action that causes it (URL, button, API call, payload) |
   | Frequency | Always / sometimes / once |
   | First seen | Timestamp or version |

2. **Identify the affected code path** — read the relevant handler, component, or endpoint. Never guess.

3. **Reduce to minimum**:
   - Strip unrelated setup ("logged in as admin" — is admin required? test as regular user first)
   - Reduce data — 1 record instead of 1000
   - Reduce steps — cut anything the bug doesn't need

4. **Write the repro as a failing test** in the repo's test framework (see [test-generation](../test-generation) for conventions). The test MUST fail on `main` and pass after the fix.

5. **Output**: markdown report + failing test file.

## Output template

```markdown
# Bug repro — <one-line summary>

## Observed
Numeric field accepts negative values in the order form.

## Expected
Values < 0 should be rejected with "Quantity must be positive".

## Environment
- App: v2.14.1
- Browser: any (server-side validation missing)
- User: any

## Minimum reproduction
1. POST /api/v1/orders with `{"items": [{"id": "abc", "quantity": -5}]}`
2. Observe: 201 Created, order accepted
3. Expected: 400 with validation error

## Affected code
`src/api/orders.py:42` — `Quantity` model has no `gt=0` constraint

## Failing test
`tests/api/test_orders.py::test_rejects_negative_quantity`
```

```python
def test_rejects_negative_quantity(client):
    resp = client.post("/api/v1/orders", json={"items": [{"id": "abc", "quantity": -5}]})
    assert resp.status_code == 400
    assert "quantity" in resp.json()["error"]["details"][0]["field"]
```

## Rules

- NEVER claim a repro without running / reading through the exact steps
- NEVER include steps that aren't necessary — reducing to minimum is the whole point
- ALWAYS produce a failing test — a repro without a test is a description
- If you CANNOT reproduce, say so and list what more information is needed (log line, request ID, exact payload)
