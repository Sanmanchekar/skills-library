---
name: test-gap
description: Find missing tests for a diff or branch — maps every changed function and branch to the tests that exercise it, uses a coverage diff when available (diff-cover, coverage.py, nyc/c8, go test -coverprofile, JaCoCo), lists untested branches, error paths, and boundaries ranked by risk, and emits failing-by-default test skeletons in the repo's own framework. Hands the skeletons to test-generation to fill in. Triggered when the user says "what tests am I missing", "test gaps in this PR", "is this diff covered", "coverage for my changes", or "what should I test before merging".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# test-gap

## When to use

- User says: "what tests am I missing", "test gaps", "is this PR covered", "coverage for my changes", "what should I test before merging"
- A PR adds logic but the test diff is empty or tiny
- `code-review` raised "missing tests for new logic" and the user wants specifics
- NOT for writing full tests from scratch for a module — that is `test-generation`

## Steps

1. **Get the diff** — `git diff <base>...HEAD` (default base: the repo's main branch). List changed source files; ignore docs, lockfiles, generated code, and test files themselves.
2. **Detect the test framework** — pytest / unittest, jest / vitest / mocha, `go test`, JUnit / Kotest, RSpec / minitest, cargo test. Read 1–2 existing tests to learn naming, fixtures, and folder layout.
3. **Coverage diff (if runnable)** — run the suite with coverage, then report only changed lines:

   | Stack | Command |
   |---|---|
   | Python | `coverage run -m pytest && coverage xml && diff-cover coverage.xml --compare-branch=origin/main` |
   | JS/TS | `npx c8 --reporter=cobertura npm test` (or `jest --coverage`) then `diff-cover coverage/cobertura-coverage.xml` |
   | Go | `go test -coverprofile=cover.out ./...` then map uncovered blocks to changed lines |
   | JVM | JaCoCo XML report then `diff-cover jacoco.xml` |

   If coverage cannot run, say so and continue with static mapping. Line coverage is a floor, not proof — still do step 4.
4. **Static mapping** — for each changed function/method: Grep tests for its name and its callers; Read the function and enumerate its branches (`if`/`else`, `switch` arms, early returns, `catch`/`except`, loop zero/one/many, guard clauses).
5. **Classify each branch** — covered (test asserts on it), touched (executed but no meaningful assertion), or untested.
6. **Rank by risk** using the table below. Drop LOW items if the list exceeds ~15.
7. **Emit skeletons** — one per gap, in the repo's framework and naming style, failing by default (`pytest.fail`, `t.Fatal`, `throw new Error`) so nobody merges an empty test.
8. **Hand off** — point to `test-generation` to fill the bodies; do not invent assertions you cannot justify from the code.

## Risk ranking

| Risk | Gap kind |
|---|---|
| HIGH | Money / auth / authz / data-deletion branch untested; error path that swallows or retries; new public API handler with no test |
| MEDIUM | Boundary values (0, 1, max, empty, null, unicode, timezone edges); new branch in existing function; concurrency or idempotency path |
| LOW | Logging-only branches, simple getters, pure formatting |

## Output format

````markdown
## Test gaps — <branch> vs <base>

**Framework**: <pytest | jest | go test | ...>   **Coverage diff**: <X% of changed lines covered | not run: reason>

| # | Risk | File:Line | Function | Untested branch / case | Status |
|---|---|---|---|---|---|

### Skeletons
```<lang>
<one failing-by-default test per gap, in repo style>
```

**Next**: run `test-generation` on the skeletons above to fill the bodies.
````

## Example

**Input**: diff adds `apply_discount(order, code)` in `orders-service/app/pricing.py` with branches for expired code, percent > 100, and currency mismatch. Only `test_apply_discount_happy_path` exists.

**Output (excerpt)**:

```markdown
**Framework**: pytest   **Coverage diff**: 41% of changed lines covered (diff-cover)

| # | Risk | File:Line | Function | Untested branch / case | Status |
|---|---|---|---|---|---|
| 1 | HIGH | app/pricing.py:52 | apply_discount | currency mismatch raises `PricingError` | untested |
| 2 | HIGH | app/pricing.py:47 | apply_discount | percent > 100 clamps total to 0, never negative | untested |
| 3 | MEDIUM | app/pricing.py:44 | apply_discount | code expires exactly at `now` (boundary) | untested |
| 4 | MEDIUM | app/pricing.py:40 | apply_discount | happy path asserts no total, only "no exception" | touched |
```

```python
# tests/test_pricing.py
import pytest

def test_apply_discount_rejects_currency_mismatch():
    pytest.fail("TODO: order in EUR, code in USD -> PricingError")

def test_apply_discount_over_100_percent_clamps_total_to_zero():
    pytest.fail("TODO: 150% code -> total_minor == 0")

@pytest.mark.parametrize("offset_seconds, valid", [(-1, True), (0, False), (1, False)])
def test_apply_discount_expiry_boundary(offset_seconds, valid):
    pytest.fail("TODO: expiry relative to frozen now")
```

## Rules

- NEVER report a gap without reading the changed function — cite `file:line` for every row
- NEVER treat line coverage as branch coverage — enumerate branches explicitly
- NEVER emit skeletons that pass when empty — they must fail until filled
- NEVER add a second test framework or new folder layout — match the repo
- ALWAYS rank by risk and put money / auth / error-path gaps first
- ALWAYS mark "touched" tests that execute code without asserting on its outcome
- ALWAYS hand filling the bodies to `test-generation`

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: verify · **Agent**: `verify` · **Loop**: `review`
- **Reads**: `diff` (from `.lifecycle/<run>/` when present)
- **Writes**: `tests` → `tests.md`
- **Comes after**: complexity-aware-coding, dependency-upgrade, pr-description
- **Hand off to**:
  - `test-generation` — once a `tests` artifact exists

This skill works on its own; the hand-offs above are suggestions. If the `lifecycle-router` skill is installed, record the step so the next skill can pick up the output: `route.py run record test-gap --artifact tests=<path>`. If it is not installed, skip this and just name the next skill to the user.
<!-- lifecycle:end -->
