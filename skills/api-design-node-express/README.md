# Node.js Express API Design Skill — REST Best Practices for Claude Code, Cursor, Copilot

> **Design and review Node.js + Express REST APIs the right way.** Async error handling, zod/joi validation, helmet + cors + rate-limit ordering, Prisma/Knex patterns, idempotency, and error envelope.

**Keywords**: node.js api design, express best practices, express middleware order, express async error handling, zod validation express, prisma api patterns, node rest api, express idempotency, express claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- api-design-node-express
```

## What it does

- Enforces middleware order: **helmet → cors → body → logger → rate-limit → auth → router**
- Catches missing `await` (unhandled promise rejections)
- Mandates zod/joi validation at every route entry
- Standardizes the error envelope with request IDs
- Blocks `origin: '*'` on auth'd APIs and leaked `x-powered-by` header
- Enforces Prisma `select` and cursor pagination

## When it triggers

- Any file importing `express`
- "Design a Node endpoint" / "review this Express handler"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — general PR review
- [api-design-go-gin](../api-design-go-gin) — Go equivalent
- [frontend-react-nextjs](../frontend-react-nextjs) — Next.js consumer
