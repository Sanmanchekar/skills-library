# FastAPI API Design Skill — Python REST Best Practices for Claude Code, Cursor, Copilot

> **Design and review Python FastAPI REST APIs with confidence.** Pydantic v2 contracts, dependency injection, async SQLAlchemy patterns, structured error envelope, idempotency — enforced by your AI coding agent.

**Keywords**: fastapi best practices, fastapi api design, python rest api, pydantic v2 patterns, fastapi async sqlalchemy, fastapi dependency injection, fastapi error handling, python api review, fastapi claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- api-design-python-fastapi
```

## What it does

- Mandates **Pydantic v2** request AND response models — separates internal DB models from wire contracts
- Enforces **async purity** — blocks sync blocking calls in async handlers
- Requires `response_model=` on every route (runtime contract + docs)
- Standardizes error envelope via global exception handlers
- Enforces **AsyncSession** rules (per-request, `select()` over `query()`, `async with db.begin()`)
- Idempotency-key handling for POST/PUT/PATCH

## When it triggers

- Any file importing `fastapi`
- "Design a FastAPI endpoint" / "review this route"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — general PR review
- [api-design-python-django](../api-design-python-django) — DRF equivalent
- [api-design-go-gin](../api-design-go-gin) — Go equivalent
