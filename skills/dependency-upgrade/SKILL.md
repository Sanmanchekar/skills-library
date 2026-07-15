---
name: dependency-upgrade
description: Plan and execute a dependency version upgrade — Python 3.x, Node LTS, Go, framework major versions, or transitive dep bumps for CVEs. Reads changelogs, categorizes breaking changes (API renames, removed features, behavior changes, deprecations), produces a migration checklist, and sequences the work so nothing lands broken. Triggered when the user asks to "upgrade X", "bump Y to version Z", "fix this CVE", or shares a Dependabot / renovate PR.
---

# dependency-upgrade

## When to use

- User asks: "upgrade Python 3.8 → 3.12", "bump Django to 5", "upgrade Node 18 → 22", "fix this CVE"
- User shares a Dependabot / Renovate PR
- Security scanner flagged a transitive CVE

## The three-question triage

Before touching code, answer:

1. **Why upgrade now?** (CVE / EOL / new feature / transitive requirement) — determines urgency and minimum-viable version
2. **What's the target version?** (latest stable / latest LTS / minimum-safe) — determines scope
3. **What am I willing to break?** (nothing / dev-only APIs / hard-deprecated calls) — determines risk budget

## Steps

### 1. Enumerate the delta
- List every intermediate major/minor version between current and target
- For each: read the CHANGELOG / release notes / migration guide (link them into the PR description)

### 2. Categorize breaking changes
For each intermediate version, classify each breaking change:

| Category | What it looks like | Action |
|---|---|---|
| **Removed API** | function/class deleted | must replace before upgrade |
| **Renamed API** | same behavior, new name | rename via codemod / sed |
| **Changed default** | argument default flipped, config default changed | audit call sites |
| **Behavior change** | same API, different semantics (e.g., timezone default, HTTP client retry) | requires code review, not just replace |
| **Hard deprecation** | warning becomes error | fix all warnings before upgrade |
| **Soft deprecation** | still works, warns | log for cleanup, don't block |
| **Removed transitive** | dep of a dep dropped | pin the transitive if you use it directly |

### 3. Scan the codebase against the delta
Grep for every removed/renamed symbol. Produce a **hit list** with file:line — not "we might use this".

### 4. Sequence the work
Split into PRs. Do NOT do it all at once.

**Standard sequence:**
1. PR A: fix deprecation warnings on current version (baseline clean)
2. PR B: bump version, apply codemods for renames
3. PR C: address behavior changes case by case
4. PR D: remove any compat shims added during migration

### 5. Regression coverage
- Identify code paths where behavior changed but tests didn't fail. Add tests for those specifically.
- Run the full test suite on both versions if possible; diff any changed outputs.

### 6. Rollout
- Merge to a feature branch, deploy to staging first
- If library-only: canary a small % of prod traffic before full
- Have a rollback plan (previous lockfile committed)

## Version-jump reference (common ones)

### Python 3.x major bumps
- Check `distutils` (removed 3.12), `typing.Union` → `X | Y` (recommended 3.10+), `asyncio` API renames
- `pip check` to find version conflicts before upgrading
- Use `python -W error::DeprecationWarning` on current version to surface warnings

### Node LTS bumps
- Check for CommonJS/ESM interop changes
- `npm ci` on a clean checkout — lockfile drift is where breakage hides
- Check `engines` field in package.json — CI must pin the same Node

### Framework majors (Django, Rails, Spring, Next.js, Nuxt, Angular)
- Read the OFFICIAL migration guide first — every major framework publishes one
- Framework majors often ship codemods (`ng update`, `nuxi upgrade`, Django's `manage.py check --deploy`)
- Update middleware / routing / auth changes carefully — these are behavior changes disguised as config

### Transitive CVE
- `npm audit fix` / `pip-audit --fix` / `govulncheck` first
- If the fix is only in a newer major of the parent lib: this is a framework upgrade, not a bump
- Consider `pip install --constraint` / `resolutions` in package.json to pin the safe transitive without upgrading the parent

## Output format

```markdown
# Upgrade plan — <library> <from> → <to>

## Motivation
CVE-2026-1234 (HIGH) in the current version; also unlocks feature X.

## Delta versions
- v18.0 → v19.0: [changelog](...)
- v19.0 → v20.0: [changelog](...)

## Breaking changes (grouped)
### Removed APIs (2 hits in our code)
- `foo.bar.OldClass` → replaced by `foo.baz.NewClass` — `src/handlers.py:42`, `src/tasks.py:118`

### Behavior changes
- Default retry policy changed from 0 to 3 retries. Audit call sites relying on immediate failure.

### Deprecations
- `Foo.old_method()` → warns since v19; use `Foo.new_method()`

## PR sequence
1. PR A: fix all deprecation warnings on v18
2. PR B: bump to v20 + apply codemod for renames
3. PR C: handle default-retry behavior change

## Rollout
- Staging first (1 week soak)
- Canary 10% prod → 100% over 2 days
- Rollback: revert PR B, lockfile restore
```

## Rules

- NEVER upgrade multiple majors at once without splitting PRs
- NEVER "just bump and see what tests say" — tests miss behavior changes
- NEVER upgrade a shared dep without checking downstream consumers (other services, sibling packages)
- ALWAYS read the migration guide before writing code
- ALWAYS resolve deprecation warnings on the CURRENT version before jumping — the warnings are the migration hints
- ALWAYS commit the new lockfile alongside the manifest change
