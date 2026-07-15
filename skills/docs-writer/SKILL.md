---
name: docs-writer
description: Generate README, API reference, or module docs from source code. Stack-agnostic. Reads the actual code (never invents functions), extracts public surface (exported symbols), infers usage from tests, and produces prose + code examples. Triggered when the user asks to "write docs for X", "generate a README", "document this module", or "write API docs".
---

# docs-writer

## When to use

- User asks: "write docs for X", "generate a README", "document this module", "API reference for Y"
- New library / package needs a README
- Public-facing API needs reference docs

## Steps

1. **Read the code** — never invent functions or arguments. Grep the public surface:
   - Exported symbols (public class / function / const)
   - Type signatures / docstrings already present
2. **Read the tests** — how the code is *actually used* is often clearer than the code itself. Steal usage examples from tests.
3. **Ask the "why" the code can't answer** — if the WHY isn't in the code, either you know it from context, or you leave a `TODO: explain motivation` for the author.
4. **Pick the doc type** and generate.

## Doc types (STRICT templates)

### README
```markdown
# <package-name>

> One-sentence description that would fit in a search result.

## Install
` ` `bash
<install command>
` ` `

## Quick start
` ` `<lang>
<smallest useful working example, 5-10 lines>
` ` `

## Why this exists
1-3 sentences. What problem does this solve that alternatives don't?

## Usage

### <common task 1>
` ` `<lang>
<example>
` ` `

### <common task 2>
...

## API
Link to the API reference OR keep small APIs inline.

## Requirements
- Runtime version (e.g., Python ≥3.10, Node ≥20)
- Optional deps and what they enable

## Development
- How to run tests
- How to release / publish
- How to contribute (link to CONTRIBUTING.md)

## License
```

### API reference (per function / class)
```markdown
### `functionName(arg1, arg2, options?)`

One-line description.

**Parameters**
- `arg1` (Type) — what it means. Constraints (range, format).
- `arg2` (Type) — ...
- `options` (Object, optional):
  - `foo` (bool, default: `false`) — ...

**Returns**: Type — what it represents.

**Throws** (if applicable):
- `SomeError` — when X.

**Example**
` ` `<lang>
<minimal usage>
` ` `

**Notes**
- Any non-obvious behavior (retry semantics, idempotency, side effects).
```

### Module / package docs
- Overview: what the module does, one paragraph
- Concept map: the 3-5 key nouns (Order, Customer, etc.) and how they relate
- Reference the API reference for details

## Rules for good code examples

- **Runnable**. Copy-paste into a fresh file — it must work. No `...` placeholders that leave the reader guessing.
- **Minimal**. Show ONE thing. If you're teaching two things, that's two examples.
- **Realistic**. Use plausible names (`user`, `order`), not `foo` and `bar`, unless you're explaining generics.
- **Complete imports**. Include the import line. Nothing worse than "which module was that from?"

## What to leave OUT of generated docs

- Marketing language ("blazing fast", "revolutionary")
- Comparative claims without a benchmark
- Rationale that's actually PR / commit context ("added for issue #42")
- Roadmap items or unreleased APIs
- Content the code doesn't back up

## Rules

- NEVER document a function you haven't read
- NEVER invent an argument or return type
- NEVER add "coming soon" content — docs describe what exists
- ALWAYS prefer real usage from tests over synthetic examples
- ALWAYS include installation + quick start in a README — those are the two most-read sections
- ALWAYS distinguish "public API" from "internals" — internals do not need reference docs
