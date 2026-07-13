# Django REST Framework API Design Skill — DRF Best Practices for Claude Code, Cursor, Copilot

> **Design and review Django REST Framework APIs the senior-engineer way.** Split read/write serializers, ViewSet vs APIView choices, permission composition, N+1 prevention with select_related/prefetch_related, and atomic transactions.

**Keywords**: django rest framework best practices, drf api design, django api review, drf serializer patterns, drf viewset vs apiview, select_related prefetch_related, django permissions, drf throttling, drf claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- api-design-python-django
```

## What it does

- Enforces **separate read/write serializers** — no `fields = '__all__'`
- Catches N+1 queries by demanding `select_related` / `prefetch_related` on every ListView
- Mandates `@transaction.atomic` on multi-row writes
- Forces `permission_classes` on every view — no reliance on global defaults
- Requires cursor pagination for growing feeds
- Standardizes error envelope + drf-spectacular schema

## When it triggers

- Any file importing `rest_framework`
- "Design a DRF endpoint" / "review this serializer" / "review this viewset"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — general PR review
- [api-design-python-fastapi](../api-design-python-fastapi) — FastAPI equivalent
- [test-generation](../test-generation) — write tests for your DRF endpoints
