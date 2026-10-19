# Threat Model Skill — STRIDE Threat Modeling & Attack Surface Analysis for Claude Code, Cursor, Copilot

> **Threat model a design before you build it.** STRIDE per data-flow element, trust boundaries, abuse cases, and a threat register with mitigations, owners, and accepted residual risk.

**Keywords**: threat modeling, stride threat model, threat model template, attack surface analysis, security design review, data flow diagram trust boundary, abuse cases, threat modeling ai, threat model claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- threat-model
```

## What it does

- Inventories **assets, entry points, and trust boundaries** for a feature or service
- Draws a **data-flow diagram** (mermaid) with boundaries where privilege or ownership changes
- Runs **STRIDE per element** using an applicability table — no element skipped
- Writes **abuse cases** ("As an attacker, I want to…") tied to threats
- Rates risk with a fixed **likelihood × impact matrix**
- Produces a **threat register** — mitigation, owner, status, and verification for every threat
- Records **residual risk** and who accepted it
- Design-time, complementary to diff-level `security-review`

## When it triggers

- "Threat model this"
- "STRIDE analysis for X"
- "What could an attacker do here?"
- "Security design review"
- A design doc introducing auth, uploads, webhooks, multi-tenancy, or admin tools

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [security-review](../security-review) — review the diff once code exists
- [tech-design](../tech-design) — the design doc this model analyses
- [compliance-review](../compliance-review) — regulatory controls for the same system
- [webhook-hardening](../webhook-hardening) — mitigations for webhook entry points
- [adr](../adr) — record accepted residual risks as decisions
