---
name: refactor
description: Safe refactor — restructure code without changing behavior. Enforces test coverage BEFORE any change (characterization tests for legacy code), small mechanical steps, one refactoring per commit, and behavior-preservation verification (tests still pass, no diff in observable output). Stack-agnostic. Triggered when the user says "refactor X", "clean this up", "split this", "extract this into Y".
---

# refactor

## When to use

- User says: "refactor this", "clean up X", "extract this", "split this file", "rename Y"
- User wants to reduce duplication, decompose a god class, or move code
- Pre-work for a feature that a messy area of code is blocking

## The refactor contract

> **A refactor changes structure, not behavior.** If observable behavior changes, it is a rewrite or a bug fix, not a refactor.

## Pre-flight (MANDATORY before any change)

### 1. Behavior baseline
Answer: **how would I know if I broke this?**
- Are there tests covering the code you're about to touch? Run them first — they must pass BEFORE the refactor.
- If tests are missing / thin: write **characterization tests** first. These capture current behavior (even if buggy). Refactor after.
- No tests possible? (Legacy, side-effecty code) Snapshot the observable output — logs, DB rows, API responses — for a fixed input, and diff after.

### 2. Scope the change
- What is the smallest useful refactor? Refactor "the file I care about", not "the whole module".
- Is this atomic, or a sequence? If sequence: split into commits, each keeping tests green.

### 3. Non-goals
Write down what you are **NOT** changing in this refactor:
- Public API surface (unless the refactor IS an API rename)
- Behavior on any tested input
- Performance beyond ± noise

## The mechanical steps

Each refactor is a named pattern. Do ONE pattern per commit.

| Pattern | What it does | Safe if |
|---|---|---|
| **Rename** (symbol, file) | new name, same behavior | tests use the symbol via public path; codemod covers all call sites |
| **Extract method / function** | pull a chunk into its own callable | inputs + outputs are clear; no hidden shared state |
| **Inline method** | reverse of extract | function was misleading or over-decomposed |
| **Move** | relocate a symbol to another module | import graph stays acyclic |
| **Introduce parameter** | replace hardcoded value with argument | all call sites can supply the value |
| **Replace conditional with polymorphism** | swap if/switch for interface | branches share a stable shape |
| **Split class / file** | one concern per unit | responsibilities are actually separable, not entangled |
| **Merge duplicates** | fold N similar functions into one | truly duplicated, not merely similar |

## The loop

```
1. Green: baseline tests pass
2. Apply ONE mechanical step (small)
3. Green: tests still pass
4. Commit
5. Go to 2
```

If step 3 fails: `git reset --hard HEAD` and try smaller. Do not "fix forward" on a refactor.

## What NOT to do in a refactor commit

- Add features
- Fix bugs (unless it's a bug in *behavior you're preserving*; if so, split into two commits: (1) preserve behavior including bug, (2) fix bug)
- Rename + reformat + move in the same commit — reviewers can't tell what changed
- "While I'm here" cleanup of unrelated code

## Common anti-patterns

| Anti-pattern | Correction |
|---|---|
| Big-bang rewrite disguised as refactor | Small mechanical steps or it's a rewrite |
| Refactor without tests | Write characterization tests first, always |
| Refactor + feature in same PR | Split. Refactor first, feature second |
| Refactor toward "cleaner" with no concrete win | Refactor toward a specific goal — the next feature, better testability, removed hazard |
| Renaming to match personal preference | Match repo conventions or don't rename |
| Extracting abstractions for hypothetical reuse | Wait for the third similar case. Two is coincidence, three is a pattern |

## Output format

For each refactor step, produce:

```markdown
## Refactor step N: <pattern name>

### Before
- <file:lines>

### After
- <file:lines>

### Behavior preservation
- Ran `<test command>` — N tests passed, same output
- No public API changed
- Diff review: only <structural changes>, no logic edits

### Commit
` ` `
refactor(<scope>): <one-line what changed>

<optional: why this refactor unblocks something>
` ` `
```

## Rules

- NEVER refactor without a way to detect behavior change (tests or snapshot)
- NEVER combine refactor + feature in one commit
- NEVER refactor toward "cleaner" without a concrete goal
- NEVER introduce abstractions for hypothetical future reuse
- ALWAYS run tests after each step; if red, `git reset --hard` and try smaller
- ALWAYS split rename + reformat + logic-preserving move into separate commits
