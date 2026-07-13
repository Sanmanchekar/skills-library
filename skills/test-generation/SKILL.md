---
name: test-generation
description: Generate unit and integration tests for a given function, class, or module. Detects the test framework in the repo (pytest, jest, vitest, go test, rspec, junit) and matches its conventions. Produces AAA-structured tests, table-driven cases, edge-case coverage (empty, null, boundary, error path), and fixtures/mocks scoped to the test. Triggered when the user asks to write/add tests for X.
---

# test-generation

## When to use

- User asks: "write tests for X", "add tests to Y", "generate a test file"
- User pastes a function or class and asks "what tests should this have"

## Steps

1. **Detect the framework**. Check for `pytest.ini` / `conftest.py` / `pyproject.toml` (pytest); `jest.config.*` / `vitest.config.*` (jest/vitest); `*_test.go` (go); `spec/` + `Gemfile` (rspec); `pom.xml` + `src/test` (junit). Match the repo's conventions.
2. **Read the target file** — never invent function signatures.
3. **Enumerate cases** — build the case matrix before writing code:

   | Category | Case |
   |---|---|
   | Happy path | typical valid input |
   | Boundary | empty, zero, one, max |
   | Null / missing | undefined, null, None, nil |
   | Type edge | negative, float where int expected, unicode |
   | Error path | invalid input → exception / error return |
   | Integration | interaction with the primary dependency (mocked) |

4. **Structure every test as AAA**:
   ```
   // Arrange
   // Act
   // Assert
   ```
5. **Use table-driven tests** where the framework supports it (Go, pytest parametrize, jest.each).
6. **Mock the smallest surface** — mock the network client, not the whole module.
7. **Name tests as sentences**: `test_returns_empty_list_when_no_orders`, `it('returns 404 when order missing')`.

## Framework quick-reference

### pytest
```python
import pytest

@pytest.mark.parametrize("input_,expected", [
    ("", 0),
    ("hi", 2),
    ("😀", 1),
])
def test_char_count(input_, expected):
    assert char_count(input_) == expected

def test_raises_on_none():
    with pytest.raises(TypeError):
        char_count(None)
```

### jest / vitest
```typescript
describe('charCount', () => {
  test.each([
    ['', 0],
    ['hi', 2],
    ['😀', 1],
  ])('charCount(%p) → %p', (input, expected) => {
    expect(charCount(input)).toBe(expected);
  });

  test('throws on null', () => {
    expect(() => charCount(null)).toThrow();
  });
});
```

### go test
```go
func TestCharCount(t *testing.T) {
    tests := []struct{ name, in string; want int }{
        {"empty", "", 0},
        {"ascii", "hi", 2},
        {"emoji", "😀", 1},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            if got := CharCount(tt.in); got != tt.want {
                t.Errorf("got %d, want %d", got, tt.want)
            }
        })
    }
}
```

## Rules

- NEVER write a test that just re-runs the implementation (`assert add(1,1) == add(1,1)`)
- NEVER assert on private / internal state — assert on observable outputs
- ALWAYS include at least one error-path test
- ALWAYS use table-driven / parametrize when there are 3+ variations of the same shape
- Coverage target: every conditional branch has at least one test
