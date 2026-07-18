---
name: code-review
description: Review a pull request or a set of code changes. Produce severity-tagged findings (CRITICAL / HIGH / MEDIUM / LOW) with a problem statement, impact, and a concrete suggested fix as a ready-to-apply code block. Triggered when the user asks to "review this PR", "review my changes", "code review", or passes a diff / PR URL.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# code-review

## When to use

- User types: "review this PR", "review my changes", "code review", "look at this diff"
- User provides a GitHub / GitLab PR URL, PR number, branch name, or a raw diff
- CI hook requests review on new commits

## Steps

1. **Detect scope**. If given a PR: fetch the diff and file contents. If given a branch: `git diff <base>...HEAD`. If given a raw diff: work from it directly. Never assume — always read the files.
2. **Load rubric** (in this order, per changed file):
   - Correctness — logic bugs, off-by-one, unhandled errors, race conditions
   - Security — injection, authz bypass, secrets, unsafe deserialization, unvalidated input
   - Performance — N+1 queries, missing indexes, quadratic loops, sync-in-async
   - Maintainability — dead code, tangled abstractions, missing tests for new logic
   - Stability — retry without backoff, missing timeouts, unbounded queues
   - Style / conventions — only if a `CLAUDE.md`, `AGENTS.md`, `.editorconfig`, or lint config sets them
3. **Emit findings**. Every finding gets: severity, file:line, title, problem, impact, suggested fix.
4. **Suggested fix must be a ready-to-apply code block** — the exact replacement text, not "consider doing X".
5. **Output** as the format below.

## Output format

```markdown
## Review — <N> findings

| # | Severity | File:Line | Title |
|---|----------|-----------|-------|
| 1 | CRITICAL | src/auth.py:42 | JWT signature not verified |

### 1. CRITICAL — src/auth.py:42 — JWT signature not verified
**Problem**: `jwt.decode(token, options={"verify_signature": False})` accepts any token.
**Impact**: Any client can forge authentication.
**Suggested fix**:
` ` `python
payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
` ` `
```

## Severity rubric

| Severity | Meaning |
|---|---|
| CRITICAL | Security bypass, data loss, service crash on a normal path |
| HIGH | Bug on the happy path, or perf regression >2x |
| MEDIUM | Bug on an edge case, or maintainability trap |
| LOW | Style, naming, minor duplication |

## Rules

- Do NOT invent code you have not seen — always Read the file before commenting on a line
- Do NOT flag stylistic choices unless the repo has an explicit config for them
- Every finding MUST include an actionable suggested fix
- Sort findings CRITICAL → LOW
- If there are zero findings, output "LGTM — no issues found" and stop
