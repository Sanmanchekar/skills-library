# API Deprecation Skill — Deprecation & Sunset Headers, Brownouts, Safe Removal for Claude Code, Cursor, Copilot

> **Remove old APIs, flags, and functions without breaking anyone.** Find every caller, announce a timeline, add `Deprecation` / `Sunset` headers, brown out, gate on zero usage, then remove with a rollback.

**Keywords**: api deprecation, sunset header rfc 8594, deprecation header rfc 9745, api sunset policy, remove feature flag, deprecate endpoint, brownout, breaking change migration guide, ai deprecation plan, deprecation claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- deprecation
```

## What it does

- **Inventories every consumer** — code search plus access logs and metrics, by client
- **Announces** a dated timeline: deprecation, brownouts, sunset, replacement
- Adds **`Deprecation` (RFC 9745) and `Sunset` (RFC 8594) headers**, runtime warnings, and a usage metric
- Writes the **migration guide** (old → new mapping, behaviour differences)
- Runs **scheduled brownouts** so surprises happen before sunset, not after
- Enforces a **usage-to-zero gate** and produces a single revertable **removal PR**
- Works for endpoints, library functions, feature flags, config keys, and event fields

## When it triggers

- "Deprecate X" / "Sunset this endpoint"
- "Remove the v1 API"
- "Kill this feature flag"
- "Who still calls this?"

## Example

"Deprecate GET /v1/orders" → 3 consumers found (web app, a worker, a partner at 4k req/day) → headers + metric added → sunset date published → brownouts → 30 days at zero → removal PR with a `410 Gone` stub.

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [tech-debt-scan](../tech-debt-scan) — finds dead APIs and flags to deprecate
- [api-design-python-fastapi](../api-design-python-fastapi) — design the replacement API
- [db-migration](../db-migration) — drop the old schema in a later, separate change
- [release-notes](../release-notes) — announce deprecations and removals
- [docs-writer](../docs-writer) — write the migration guide
