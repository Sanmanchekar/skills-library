---
name: tech-debt-scan
description: Scan a repository for technical debt and produce a ranked debt register. Finds churn × complexity hotspots from git history, inventories TODO / FIXME / HACK markers with their age via git blame, flags outdated and vulnerable dependencies, hot files with no tests, dead code, and duplicated logic — then ranks each item by blast radius with an interest-rate framing (what it costs per month to leave it). Outputs a debt register table and the top 5 paydown items, each routed to the skill that fixes it (refactor, dependency-upgrade, test-generation, deprecation). Stack-agnostic. Triggered when the user says "scan for tech debt", "where is our tech debt", "find hotspots", "what should we refactor first", "debt register", or "how bad is this codebase".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# tech-debt-scan

## When to use

- User says: "tech debt scan", "find hotspots", "what should we pay down first", "debt register"
- Planning a cleanup sprint or quarterly engineering investment
- Onboarding to an unfamiliar repo and wanting the risk map
- Velocity is dropping and nobody can say where the friction is

## Steps

1. **Set the window** — default last 12 months of git history; exclude vendored, generated, lock, and migration files.
2. **Churn** — commits per file (command A).
3. **Complexity** — per-file complexity or LOC proxy (command B). Use a real tool if installed (`lizard`, `radon`, `gocyclo`, `eslint complexity`), else LOC + max nesting.
4. **Hotspots** — rank `churn × complexity`; top 20 are candidates. Read the top 5 before judging them.
5. **Markers** — TODO / FIXME / HACK / XXX with age from git blame (command C).
6. **Dependencies** — outdated and vulnerable via the ecosystem's own tool (command D).
7. **Test gaps** — hotspots with no matching test file or near-zero coverage.
8. **Dead code** — unreferenced exports/functions, unused flags, unreachable branches (use `vulture`, `ts-prune`/`knip`, `deadcode`, `staticcheck` if available; else grep for zero references).
9. **Duplication** — copy-paste blocks (`jscpd` or similar); confirm by reading.
10. **Score** each item (scoring table), build the register, pick top 5, route each to a skill.

## Commands

```bash
# A. Churn — commits per file, last 12 months
git log --since="12 months ago" --name-only --format='' -- . \
  ':!*.lock' ':!*vendor/*' ':!*generated*' | sort | uniq -c | sort -rn | head -50

# B. Complexity proxy if no tool installed (LOC per file)
git ls-files '*.py' '*.ts' '*.go' '*.java' | xargs wc -l | sort -rn | head -50

# C. Markers with age (author date of the line)
git grep -nE '\b(TODO|FIXME|HACK|XXX)\b' | while IFS=: read -r f l _; do
  printf '%s:%s\t%s\n' "$f" "$l" "$(git blame -L "$l,$l" --date=short -- "$f" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)"
done | sort -k2

# D. Dependencies (pick the ecosystem present)
npm outdated; npm audit --omit=dev
pip list --outdated; pip-audit
go list -u -m all; govulncheck ./...

# Bug-fix density per file (fix commits touching it)
git log --since="12 months ago" -i --grep='fix' --name-only --format='' | sort | uniq -c | sort -rn | head -20
```

## Debt categories

| Category | Signal | Routed to |
|---|---|---|
| Hotspot complexity | top churn × complexity, long functions, deep nesting | [refactor](../refactor) |
| Stale / vulnerable deps | major versions behind, known CVEs, EOL runtime | [dependency-upgrade](../dependency-upgrade) |
| Missing tests on hot files | hotspot with no test file / low coverage | [test-generation](../test-generation) |
| Dead code / dead flags / old APIs | zero references, flags 100% on for months, endpoints with no traffic | [deprecation](../deprecation) |
| Duplicated logic | same rule implemented in 2+ places | [refactor](../refactor) |
| Old markers | TODO/FIXME > 12 months old | triage: fix, ticket, or delete |

## Scoring (blast radius × interest rate)

| Factor | 1 | 2 | 3 |
|---|---|---|---|
| Blast radius | leaf module, internal | shared module / one service | core path (auth, payments, data writes) |
| Interest rate (cost of leaving it) | rarely touched | touched monthly, slows changes | touched weekly, causes bugs/incidents |
| Paydown effort (inverse) | > 2 weeks | 2–10 days | < 2 days |

`priority = blast_radius × interest_rate × effort_inverse` (max 27). Interest-rate evidence: churn, bug-fix commits, incident links, review time — never "feels messy".

## Example

Input: "Scan orders-service for tech debt."

Output (excerpt):
| # | Item | Category | Evidence | Blast | Interest | Effort | Score | Skill |
|---|---|---|---|---|---|---|---|---|
| 1 | `pricing/calc.py` | Hotspot | 61 commits/12mo, CC 48, 14 fix commits | 3 | 3 | 2 | 18 | refactor |
| 2 | `requests` 2.19 | Vulnerable dep | 2 CVEs (pip-audit) | 3 | 2 | 3 | 18 | dependency-upgrade |
| 3 | `checkout/handler.py` | No tests | 38 commits, no test file | 3 | 3 | 2 | 18 | test-generation |

## Output format

```markdown
## Tech debt scan — <repo> — window <since>

### Summary
- Files scanned: N · Hotspots: N · Markers: N (M older than 12 mo) · Vulnerable deps: N

### Debt register
| # | Item | Category | Evidence | Blast | Interest | Effort | Score | Skill |

### Top 5 paydown items
1. <item> — score <n> — why now: <interest evidence> — next: <skill> — est <size>

### Marker inventory (oldest first)
| File:line | Marker | Age | Text |

### Not debt (checked, left alone)
- <item> — stable, low churn; complexity is inherent
```

## Rules

- NEVER rank by complexity alone — complex code nobody touches is cheap debt
- NEVER call something dead without confirming zero references (and zero runtime traffic for endpoints)
- NEVER include generated, vendored, or lock files in hotspots
- NEVER propose fixes in this skill — route each item to its owning skill
- ALWAYS read the top hotspots before scoring them — numbers find candidates, reading confirms them
- ALWAYS cite evidence (commit counts, CVE ids, blame dates) for every register row
- ALWAYS include a "not debt" list so the scan shows what was judged and rejected
- ALWAYS cap the paydown list at 5 — a list of 40 priorities is no priority

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: maintain · **Agent**: `maintain`
- **Writes**: `debt-register` → `debt-register.md`
- **Hand off to**:
  - `refactor` — always
  - `dependency-upgrade` — always
  - `deprecation` — if: _Is any debt item dead code or an unused API?_
  - `test-generation` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record tech-debt-scan --artifact debt-register=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
