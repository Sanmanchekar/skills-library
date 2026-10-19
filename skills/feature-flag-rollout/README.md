# Feature Flag Rollout Skill — Progressive Delivery, Kill Switches & Flag Cleanup for Claude Code, Cursor, Copilot

> **Ship risky changes behind a feature flag with a real rollout plan.** Flag type, default-off, kill switch, 1→5→25→50→100 ramp with gate metrics, both-path tests, and a cleanup date so flags don't rot.

**Keywords**: feature flag rollout, progressive delivery, percentage rollout, kill switch, canary release, dark launch, feature toggle best practices, flag debt cleanup, openfeature, launchdarkly, unleash, feature flag claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- feature-flag-rollout
```

## What it does

- Picks the **flag type** — release, ops / kill switch, experiment, permission — with lifetime and default
- **Vendor-neutral** — reuses the flag system already in the repo (OpenFeature, LaunchDarkly, Unleash, Flagsmith, GrowthBook, config table)
- Enforces **default-off and fail-safe** evaluation when the flag provider is down
- **One seam per flag**, no nested flags, no re-evaluation deep in the stack
- **Progressive ramp** 1% → 5% → 25% → 50% → 100% with hold times, gate metrics, and rollback triggers
- **Tests both paths**, including old-path reads of data written by the new path
- Sets **owner + cleanup date** to prevent flag debt

## When it triggers

- "Put this behind a flag"
- "Plan the rollout" / "gradual rollout" / "canary this"
- "Add a kill switch"
- "Clean up old flags"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [tech-design](../tech-design) — the rollout table this plan makes concrete
- [observability](../observability) — dashboards and alerts for the gate metrics
- [runbook](../runbook) — document who flips the kill switch and how
- [db-migration](../db-migration) — keep schema changes compatible with both flag paths
- [release-notes](../release-notes) — announce the feature at 100%
