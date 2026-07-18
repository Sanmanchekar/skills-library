---
name: api-design-python-django
description: Design or review a REST API written in Python with Django REST Framework (DRF). Enforces serializer separation (read vs write), ViewSet vs APIView choice, permission classes, throttling, N+1 prevention via select_related/prefetch_related, atomic transactions, and drf-spectacular schema. Triggered when the user asks to design/review a DRF endpoint, serializer, viewset, or router.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# api-design-python-django

## When to use

- Repo has `djangorestframework` in requirements
- File imports `rest_framework`
- User asks: "design a DRF endpoint", "review this serializer", "how should I structure this Django API"

## Design checklist

### Serializers
- **Separate read and write serializers** — never overload one with `read_only_fields` for everything
  - `OrderCreateSerializer` — input contract
  - `OrderDetailSerializer` — output contract
- Validate at the serializer, not the view — `validate_<field>` and `validate` methods
- Never expose `id` alone as the URL key if it's a sequential PK — use UUIDs for public IDs

### View style
- **ViewSet + Router** for standard CRUD
- **APIView** for custom actions that don't fit CRUD
- **@action** decorators for related actions (e.g., `POST /orders/{id}/cancel/`)

### Permissions
- Every view sets `permission_classes` — never rely on the global default
- Compose with `IsAuthenticated & IsOwner` — don't repeat auth checks in `get_queryset`

### Query optimization (N+1 killer)
- Every ListView calls `select_related('customer')` for FK / one-to-one
- Every ListView calls `prefetch_related('items')` for reverse FK / m2m
- Serializer accessing nested relations without the prefetch = HIGH severity finding

### Transactions
- `@transaction.atomic` on any view that writes to more than one row / table
- Use `select_for_update()` inside a transaction when you need to lock rows

### Throttling
- Configure `DEFAULT_THROTTLE_CLASSES` — `UserRateThrottle` + `AnonRateThrottle`
- Sensitive endpoints (login, password reset): `ScopedRateThrottle`

### Error envelope
- Custom exception handler that returns:
```json
{
  "error": {"code": "ORDER_NOT_FOUND", "message": "...", "details": []},
  "request_id": "req_abc123"
}
```

### Pagination
- `CursorPagination` for feeds and growing lists
- `PageNumberPagination` only when total-count is genuinely needed
- Cap `page_size_query_param` at 100

### Schema
- `drf-spectacular` for OpenAPI — every viewset has `@extend_schema` where auto-inference is wrong

## Rules

- NEVER use `ModelSerializer` with `fields = '__all__'` — explicit fields only
- NEVER access `request.user.is_staff` inside `get_queryset` for filtering — use a permission class
- NEVER call `.save()` inside a loop without `bulk_create` / `bulk_update`
- NEVER return an internal DB PK if a public UUID exists
- ALWAYS `.only()` / `.defer()` when the serializer uses a subset of model fields
