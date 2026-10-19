# Tech Debt Scan Skill — Hotspots, Debt Register & Paydown Plan for Claude Code, Cursor, Copilot

> **Find the debt that actually costs you.** Churn × complexity hotspots, aged TODOs, vulnerable deps, untested hot files, and dead code — ranked by blast radius and interest rate.

**Keywords**: technical debt scan, tech debt register, code hotspots, churn complexity analysis, git log hotspots, todo fixme inventory, dead code detection, refactoring priorities, ai tech debt, tech debt claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- tech-debt-scan
```

## What it does

- **Churn × complexity hotspots** from git history — not complexity alone
- **TODO / FIXME / HACK inventory** with age from git blame
- **Outdated and vulnerable dependencies** via the ecosystem's own tools
- **Missing tests on hot files**, **dead code**, and **duplicated logic**
- Scores every item by **blast radius × interest rate × effort**
- Outputs a **debt register** and the **top 5 paydown items**, each routed to the skill that fixes it

## When it triggers

- "Scan this repo for tech debt"
- "Find hotspots" / "What should we refactor first?"
- "Build a debt register"
- "How bad is this codebase?"

## Example

"Scan orders-service" → `pricing/calc.py` (61 commits in 12 months, complexity 48, 14 fix commits) → refactor; `requests` with 2 CVEs → dependency-upgrade; untested `checkout/handler.py` → test-generation.

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [refactor](../refactor) — pay down hotspots and duplication
- [dependency-upgrade](../dependency-upgrade) — fix stale and vulnerable deps
- [test-generation](../test-generation) — cover hot, untested files
- [deprecation](../deprecation) — remove dead code, flags, and old APIs
- [estimation](../estimation) — size the paydown items
