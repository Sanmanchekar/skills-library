---
name: api-contract
description: Contract-first API design, framework-agnostic — writes or reviews the spec before the code (OpenAPI 3.1 for HTTP, protobuf for gRPC, AsyncAPI for events). Covers resource naming, versioning, a single error model (RFC 9457 application/problem+json), cursor pagination, idempotency keys, and backward-compatibility rules (additive only, never repurpose or retype a field), plus breaking-change detection with oasdiff or buf breaking in CI. Emits the spec plus a compatibility report; hands implementation review to the per-framework api-design skills. Triggered when the user says "design the API for X", "write the OpenAPI spec", "is this a breaking change", "review this proto", "API contract", or "how should we version this endpoint".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# api-contract

## When to use

- User says: "design the API for X", "write the OpenAPI / proto / AsyncAPI spec", "API contract", "contract-first"
- User asks "is this a breaking change?" or shares a diff touching `openapi.yaml`, `*.proto`, `asyncapi.yaml`
- A design doc adds or changes a public or cross-team interface
- For framework-specific implementation review, hand off to `api-design-go-gin`, `api-design-node-express`, `api-design-python-fastapi`, or `api-design-python-django`

## Steps

1. **Pick the spec format** — HTTP request/response → OpenAPI 3.1; RPC between services → protobuf (gRPC / Connect); events on a broker → AsyncAPI 3. Find an existing spec first (`Glob **/openapi*.{yaml,json}`, `**/*.proto`, `**/asyncapi*.yaml`) and extend it.
2. **Model resources** — nouns, plural, kebab-case paths, max 2 levels of nesting. Verbs only for non-CRUD actions as sub-resources (`POST /orders/{id}/cancel`).
3. **Define schemas** — explicit types, `required` lists, formats (`date-time`, `uuid`), enums documented as open (clients must tolerate unknown values). Money as integer minor units + currency code.
4. **Apply the cross-cutting checklist** below — errors, pagination, idempotency, versioning, auth.
5. **Check compatibility** — if a previous spec exists, diff it with the rules table and run the tool (`oasdiff breaking base.yaml head.yaml`, `buf breaking --against '.git#branch=main'`). Paste the tool output.
6. **Emit** the spec fragment and the compatibility report in the output format.

## Design checklist

| Area | Rule |
|---|---|
| Naming | `/v1/orders/{order_id}/items`; fields `snake_case` or `camelCase` — match the existing spec, never mix |
| Versioning | Major version in path (`/v1`) or package (`acme.orders.v1`); new major only for unavoidable breaks; old major gets a sunset date (`Sunset` + `Deprecation` headers) |
| Errors | Every 4xx/5xx returns RFC 9457 `application/problem+json`: `type`, `title`, `status`, `detail`, `instance`, plus a stable machine `code` and `errors[]` for field validation |
| Status codes | 400 malformed, 401 unauthenticated, 403 forbidden, 404 not found, 409 conflict / idempotency mismatch, 422 validation, 429 rate-limited (with `Retry-After`) |
| Pagination | Cursor-based: `?limit=&cursor=` → `{ data: [], next_cursor }`; cap `limit` (e.g. max 100); opaque cursor; stable sort key |
| Idempotency | Every non-idempotent `POST` that creates or moves money accepts `Idempotency-Key`; same key + same body → same response; same key + different body → 409/422 |
| Filtering | Explicit allow-listed query params; no free-form query language on public APIs |
| Timestamps | UTC, RFC 3339; never local time |
| Auth | Declared in `securitySchemes`; scopes per operation |
| Events | AsyncAPI: event name past-tense (`order.cancelled`), envelope with `id`, `type`, `occurred_at`, `schema_version` |

## Compatibility rules

| Change | Safe? |
|---|---|
| Add optional request field / new response field | Safe |
| Add new endpoint, new enum value (if clients tolerate unknowns) | Safe |
| Add required request field | BREAKING |
| Remove or rename a field, endpoint, or enum value | BREAKING |
| Change a field's type, format, or meaning (repurpose) | BREAKING — add a new field instead |
| Tighten validation (shorter max length, narrower pattern) | BREAKING |
| Change default value or error code for an existing case | BREAKING |
| protobuf: reuse a field number or change its type | BREAKING — `reserved` the old number |

## Output format

````markdown
## API contract — <resource / service>

**Format**: OpenAPI 3.1 | protobuf | AsyncAPI 3   **Spec file**: <path>

### Spec
```yaml
<spec fragment>
```

### Compatibility report
| # | Change | Location | Verdict | Fix |
|---|---|---|---|---|

**Tool output**: `<oasdiff / buf breaking output, or "no previous spec">`
**Verdict**: COMPATIBLE | BREAKING (needs /v2 or a new field)

### Next
- Implementation review → `api-design-<framework>`
````

## Example

**Input**: diff to `orders-service/openapi.yaml` changes `amount` from `number` to `string` and adds required `channel` to `POST /v1/orders`.

**Output (excerpt)**:

```markdown
### Compatibility report
| # | Change | Location | Verdict | Fix |
|---|---|---|---|---|
| 1 | `amount` type number → string | CreateOrder.amount | BREAKING | keep `amount`; add `amount_minor` (integer) + `currency`; deprecate `amount` |
| 2 | new required `channel` | CreateOrder.channel | BREAKING | make optional with server default `"web"` |

**Tool output**: `error [request-property-type-changed] ... 'amount'` / `error [new-required-request-property] ... 'channel'`
**Verdict**: BREAKING
```

## Rules

- NEVER write handlers before the spec for a new interface — contract first
- NEVER repurpose, retype, or rename an existing field — add a new one and deprecate the old
- NEVER return ad-hoc error shapes — one RFC 9457 problem+json model everywhere
- NEVER use offset pagination on large or mutating collections — use cursors
- NEVER reuse a protobuf field number — mark it `reserved`
- ALWAYS run a breaking-change tool when a previous spec exists, and paste its output
- ALWAYS require `Idempotency-Key` on POSTs that create resources or move money

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: build · **Agent**: `build`
- **Reads**: `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `api-contract` → `api-contract.yaml`
- **Comes after**: tech-design
- **Hand off to**:
  - `api-design-go-gin` — if content match `github.com/gin-gonic/gin`
  - `api-design-node-express` — if content match `express`
  - `api-design-python-fastapi` — if content match `fastapi`
  - `api-design-python-django` — if content match `rest_framework`
  - `contract-testing` — if: _Does another service consume this API?_

When the step is done, record it so the next skill can pick up the output:
`route.py run record api-contract --artifact api-contract=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
