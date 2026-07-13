# Go Gin API Design Skill — REST API Best Practices for Claude Code, Cursor, Copilot

> **Design and review Go + Gin REST APIs like a senior engineer.** Idempotency keys, structured error envelope, middleware ordering, context propagation, gorm/sqlx patterns — all in one skill.

**Keywords**: go api design, gin framework best practices, golang rest api, gin middleware order, gin idempotency, gin error handling, gorm patterns, sqlx patterns, go api review, gin claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- api-design-go-gin
```

## What it does

- Enforces the correct **middleware order** (recover → request-id → logger → cors → auth → ratelimit)
- Mandates **idempotency keys** on POST/PUT/PATCH
- Standardizes the **error envelope** (`code`, `message`, `details`, `request_id`)
- Catches missing `context` propagation to DB/RPC calls
- Blocks `context.Background()` inside handlers and raw DB errors leaking to clients
- Enforces cursor pagination for growing lists

## When it triggers

- Any file importing `github.com/gin-gonic/gin`
- "Design a Go endpoint" / "review this Gin handler" / "how should I structure this Go API"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — general PR review
- [api-design-node-express](../api-design-node-express) — Node.js equivalent
- [api-design-python-fastapi](../api-design-python-fastapi) — FastAPI equivalent
