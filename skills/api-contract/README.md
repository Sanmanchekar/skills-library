# API Contract Skill — Contract-First OpenAPI, Protobuf & AsyncAPI Design for Claude Code, Cursor, Copilot

> **Design the API contract before the code.** OpenAPI 3.1 / protobuf / AsyncAPI specs with RFC 9457 errors, cursor pagination, idempotency keys, and breaking-change detection via oasdiff and buf.

**Keywords**: contract-first api design, openapi 3.1 generator, api breaking change detection, oasdiff, buf breaking, rfc 9457 problem details, api versioning, cursor pagination, idempotency key, asyncapi, protobuf api design, api contract claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- api-contract
```

## What it does

- Picks the right spec format — **OpenAPI 3.1** (HTTP), **protobuf** (gRPC), **AsyncAPI 3** (events)
- Enforces **resource naming**, versioning with **Sunset / Deprecation** headers, and UTC RFC 3339 timestamps
- One error model: **RFC 9457 `application/problem+json`** with stable machine codes
- **Cursor pagination** with capped limits and stable sort keys
- **Idempotency-Key** on POSTs that create resources or move money
- **Backward-compat rules** — additive only, never repurpose or retype a field, `reserved` protobuf numbers
- Runs **oasdiff / buf breaking** and emits a compatibility report with a fix per break
- Framework-agnostic — hands implementation review to the per-framework API skills

## When it triggers

- "Design the API for X"
- "Write the OpenAPI spec / proto"
- "Is this a breaking change?"
- "How should we version this endpoint?"
- A diff touching `openapi.yaml`, `*.proto`, or `asyncapi.yaml`

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [api-design-go-gin](../api-design-go-gin) — implementation review for Go / Gin
- [api-design-node-express](../api-design-node-express) — implementation review for Node / Express
- [api-design-python-fastapi](../api-design-python-fastapi) — implementation review for FastAPI
- [api-design-python-django](../api-design-python-django) — implementation review for Django / DRF
- [idempotency-review](../idempotency-review) — verify idempotency keys are honoured server-side
- [tech-design](../tech-design) — the design doc whose APIs section this fills
