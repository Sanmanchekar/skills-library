---
name: pr-description
description: Generate a pull-request description from the branch diff. Produces summary (what changed and why), test plan (checkbox list), screenshots section (for UI changes), risk callouts, and links to related PRD / issue / RCA. Triggered when the user asks to write/open a PR, "create a PR description", or runs `gh pr create`.
---

# pr-description

## When to use

- User asks: "write a PR description", "open a PR for this"
- Running `gh pr create` or equivalent

## Steps

1. **Read the commit range** — `git log <base>..HEAD` and `git diff <base>...HEAD`.
2. **Detect the change class** — feature, bugfix, refactor, migration, revert. Different classes need different sections (see below).
3. **Extract linked issues** — scan commit bodies for `Refs: #`, `Fixes: #`, `Closes: #`.
4. **Emit** using the template below. Sections marked (optional) are omitted when not applicable.

## Template

```markdown
## Summary
1–3 sentences: WHAT changed and WHY. Not "this PR does X" — active voice: "adds X so that Y".

## Screenshots (if UI)
| Before | After |
|---|---|
| <img> | <img> |

## Test plan
- [ ] Unit tests pass locally (`pytest tests/api/test_orders.py`)
- [ ] Manual: create an order → verify total in confirmation email
- [ ] Manual: create an order with a negative quantity → verify 400 error
- [ ] Regression: existing checkout flow still works

## Risk
| Risk | Mitigation |
|---|---|
| DB migration adds a NOT NULL column on a 10M-row table | Backfill in prior PR (#4820); this PR only flips the column |

## Rollback
Revert this PR. No data migration to undo.

## Links
- PRD: <url>
- Fixes: #4821
- Runbook: <url>

## Reviewer notes (optional)
Anything the reviewer should look at first, or any decisions you want to flag.
```

## Section rules by change class

| Class | Required sections |
|---|---|
| Feature | Summary, Test plan, Rollback, Links |
| UI feature | + Screenshots |
| Bugfix | Summary, Repro steps, Test plan (must include a regression test), Links |
| Refactor | Summary, "No behavior change" attestation, Test plan |
| Migration | Summary, Data-safety analysis, Test plan, Rollback (with data-restore steps) |
| Revert | Summary (what and why), Impact on features that depended on it |

## Rules

- NEVER auto-generate the test plan from the diff without reading it — a test plan the author doesn't actually run is worse than no test plan
- NEVER omit the risk section for anything touching DB, auth, payments, or infra
- NEVER omit rollback for DB migrations — say explicitly if not rollbackable
- ALWAYS link related PRD / issue / runbook when the branch name or commits reference one
- If the PR is a "chore" (dep bump, formatting), a one-line summary is fine
