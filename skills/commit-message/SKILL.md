---
name: commit-message
description: Generate a Conventional Commits message from a staged diff. Detects type (feat/fix/refactor/docs/test/chore/perf/build/ci/revert), scope, breaking changes (adds `!` and `BREAKING CHANGE:` footer), and produces a subject ≤72 chars in imperative present tense. Triggered when the user asks to "write a commit message", or has staged changes to commit.
---

# commit-message

## When to use

- User asks: "write a commit message", "commit this"
- Staged changes present (`git diff --cached`)

## Steps

1. **Read the staged diff** — `git diff --cached`. Do NOT commit-message from an assumed diff.
2. **Classify** using the type table below.
3. **Detect scope** — the module / package / feature area (e.g., `auth`, `orders`, `ui`).
4. **Detect breaking changes** — removed public function, renamed field, changed HTTP contract, changed CLI flag. Add `!` after type/scope AND a `BREAKING CHANGE:` footer.
5. **Write subject** — imperative present tense, ≤72 chars, no trailing period.
6. **Write body** (optional) — WHY, not WHAT. The diff shows WHAT.

## Type reference

| Type | Use for |
|---|---|
| feat | New user-visible feature |
| fix | Bug fix a user would notice |
| perf | Performance improvement (no behavior change) |
| refactor | Code change with no behavior change |
| docs | Documentation only |
| test | Test additions/changes only |
| chore | Deps, tooling, no runtime effect |
| build | Build system / packaging |
| ci | CI config only |
| style | Formatting only |
| revert | Revert a prior commit |

## Format

```
<type>(<scope>)<!>: <subject>

<body — WHY, not WHAT>

<footers — Refs: #123, BREAKING CHANGE: ..., Co-Authored-By: ...>
```

## Examples

Simple:
```
fix(auth): reject expired refresh tokens
```

Breaking:
```
feat(api)!: rename /orders response field `total` to `total_amount`

BREAKING CHANGE: consumers must update field name in the /orders response.
Migration: sed -i 's/data\.total\b/data.total_amount/g' src/
```

With body:
```
perf(reports): batch DB queries in dashboard load

Dashboard was issuing N+1 queries on the reports list. Batched into a
single query with select_related. p95 load time drops from 3.2s to 0.9s.

Refs: #4821
```

## Rules

- NEVER write "update code" / "fix bug" / "misc changes" — too vague
- NEVER include the file list — the diff has it
- NEVER exceed 72 chars in the subject
- ALWAYS use imperative present ("add", not "added" / "adds")
- ALWAYS check for breaking changes — removed / renamed public APIs, changed HTTP contracts, changed CLI flags
