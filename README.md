# skills-library — AI Coding Agent Skills for Claude Code, Cursor, Codex, Copilot, Aider

> **Battle-tested skills for AI coding agents.** One command installs any skill into Claude Code, Cursor, GitHub Copilot Chat, Codex CLI, Aider, Continue, Cline, Windsurf, Cody, Roo Code, or Zed AI.

<!--
Keywords: claude code skills, cursor rules, copilot instructions, codex prompts, aider conventions,
ai code review, ai pr review, rca automation, incident postmortem, e2e testing playwright,
observability dashboard generator, grafana loki prometheus, adr generator, prd writer,
runbook generator, iac review terraform, api design go gin, api design fastapi django express,
next.js best practices, react code standards, vue nuxt patterns
-->

Each skill is a **portable capability pack** — a `SKILL.md` (spec + instructions) plus optional references and helpers. Install once, use across every agent you have.

---

## Install any skill (one command)

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- <skill-name>
```

You'll be asked which agent to install to (Claude Code, Cursor, Copilot Chat, Codex, Aider, Continue, Cline, Windsurf, Cody, Roo Code, Zed, or **all**).

Non-interactive:

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent claude-code --scope user
```

---

## Skills

| Skill | Role | Description |
|---|---|---|
| [code-review](skills/code-review) | dev | Stateful PR review with severity-tagged findings, ```suggestion blocks, and iterative recheck |
| [rca](skills/rca) | dev | Phased incident root-cause orchestration with timeline, contributing factors, action items |
| [api-design-go-gin](skills/api-design-go-gin) | backend | REST API design review for Go + Gin: idempotency, pagination, error envelopes, middleware ordering |
| [api-design-node-express](skills/api-design-node-express) | backend | REST API design review for Node.js + Express: validation, async error handling, rate limiting |
| [api-design-python-fastapi](skills/api-design-python-fastapi) | backend | REST API design review for Python + FastAPI: Pydantic contracts, dependency injection, async patterns |
| [api-design-python-django](skills/api-design-python-django) | backend | REST API design review for Python + Django REST Framework: serializers, viewsets, permissions |
| [frontend-react-nextjs](skills/frontend-react-nextjs) | frontend | Next.js App Router review: server components, streaming, caching, Core Web Vitals |
| [frontend-vue-nuxt](skills/frontend-vue-nuxt) | frontend | Nuxt 3 review: composables, server routes, hydration, SEO metadata |
| [e2e-testing](skills/e2e-testing) | qa | Stack-agnostic Playwright test generation from feature spec or user flow |
| [test-generation](skills/test-generation) | qa | Unit + integration test generation from source with fixtures and edge cases |
| [bug-repro](skills/bug-repro) | qa | Turn a bug report into a minimal reproduction with steps, expected vs actual, environment |
| [observability](skills/observability) | devops | Generate Grafana / Loki / Prometheus dashboards from service code |
| [runbook](skills/runbook) | devops | Incident runbook scaffolding — symptoms, triage, mitigations, rollback, escalation |
| [iac-review](skills/iac-review) | devops | Terraform / ECS / Helm config review for security, drift, and cost |
| [prd-writer](skills/prd-writer) | pm | Turn a rough ask into a structured PRD — problem, users, scope, success metrics |
| [release-notes](skills/release-notes) | pm | Changelog / release notes from merged PRs, grouped by user impact |
| [commit-message](skills/commit-message) | shared | Conventional commit message generator with scope + BREAKING CHANGE detection |
| [pr-description](skills/pr-description) | shared | PR description generator — summary, test plan, screenshots, risk callouts |
| [adr](skills/adr) | shared | Architecture Decision Record generator — context, options, decision, consequences |

---

## Agent support matrix

| Agent | Install location | Format |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/SKILL.md` | SKILL.md as-is |
| Codex CLI | `~/.codex/prompts/<name>.md` | SKILL.md body |
| Cursor | `.cursor/rules/<name>.mdc` | Translated to `.mdc` |
| Aider | `.aider/conventions/<name>.md` | Referenced from `.aider.conf.yml` |
| Continue | `.continue/rules/<name>.md` | SKILL.md body |
| Cline | `.clinerules/<name>.md` | SKILL.md body |
| Windsurf | `.windsurf/rules/<name>.md` | SKILL.md body |
| Cody | `.sourcegraph/<name>.md` | SKILL.md body |
| Copilot Chat | `.github/copilot-instructions.md` | Appended, marker-fenced |
| Roo Code | `.roo/rules/<name>.md` | SKILL.md body |
| Zed AI | `~/.config/zed/prompts/<name>.md` | SKILL.md body |

---

## Design principles

1. **Self-contained** — each `skills/<name>/` folder is copy-paste portable
2. **One skill, one job** — no god-skills
3. **Structured, not prose** — every skill has a decision table, checklist, or step sequence
4. **Agent-agnostic** — SKILL.md is the source of truth; the installer translates per agent
5. **SEO discoverable** — README titles and metadata target real search terms

---

## Contributing

New skill? See [CONTRIBUTING.md](CONTRIBUTING.md) for the SKILL.md spec and PR checklist.

## License

[MIT](LICENSE)
