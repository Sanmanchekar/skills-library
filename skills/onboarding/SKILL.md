---
name: onboarding
description: Generate a repo walkthrough for a new joiner from the codebase itself. Produces "what this repo is, how it's structured, how to run it, the 5 files you must read, common workflows, and where the landmines are." Reads manifests, entry points, README, CI config, and top-level directories. Triggered when the user asks to "onboard someone", "explain this repo", "generate an onboarding guide", or is a new engineer landing on a codebase.
---

# onboarding

## When to use

- User asks: "onboard me onto this repo", "generate an onboarding guide", "explain this codebase", "I'm new to this repo — where do I start"
- New joiner ramping up
- Handing a repo off to another team

## Steps

1. **Read the shape of the repo** (top-level ONLY at first):
   - Manifests: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile` → language + framework
   - `README.md` — start here for the author's own intent (but never trust as complete)
   - `CLAUDE.md` / `AGENTS.md` / `CONTRIBUTING.md` — hidden constraints
   - `Makefile` / `Justfile` / `scripts/` — how humans actually run things
   - `.github/workflows/` — what CI proves works
   - Top-level directories — is it monorepo / package / service / library?

2. **Find the entry point(s)**:
   - Web service: `main.go`, `manage.py`, `src/index.ts`, `app/main.py`
   - CLI: entry in `pyproject.toml [project.scripts]` / `package.json bin`
   - Library: `__init__.py`, `index.ts`, `mod.rs`
   - Monorepo: list each package's entry

3. **Trace one end-to-end path**. For a web service: pick one route, follow it to a handler, to a service, to a DB call, to a model. Explain this path in the guide — it teaches the layout.

4. **Identify the landmines** (the stuff that will confuse a new joiner):
   - Non-obvious naming (why is `foo/` called that?)
   - Global state / singletons
   - Circular deps or unusual import paths
   - "Do not touch" areas (git-blame shows one author, or CLAUDE.md warns)
   - Manual steps the README omits ("run this seed script before your first request")

5. **Write the guide**.

## Output template

```markdown
# Onboarding — <repo name>

## What this is
One paragraph: what the repo does, who uses it, and its role in the larger system.

## Stack
- Language: Python 3.12
- Framework: FastAPI + SQLAlchemy + Alembic
- Runtime: containerized (Docker); prod runs on ECS
- Data stores: Postgres (primary), Redis (cache + queue)

## Get it running (5 minutes)
` ` `bash
make setup   # deps, DB migrate, seed
make dev     # start server on :8000
make test    # run test suite
` ` `

If make targets don't exist, spell out the equivalent commands.

## The layout
- `app/api/` — HTTP routers (one file per resource)
- `app/services/` — business logic (routers delegate here)
- `app/db/` — SQLAlchemy models + migration definitions
- `app/tasks/` — background jobs
- `tests/` — mirrors `app/` structure

## The 5 files you must read (in order)
1. `app/main.py` — how the app wires up
2. `app/api/orders.py` — the "reference" router; other routers follow this shape
3. `app/services/order_service.py` — business-logic pattern
4. `app/db/models.py` — the data model
5. `alembic/versions/` (most recent) — how migrations work here

## End-to-end example: creating an order
1. `POST /api/v1/orders` hits `app/api/orders.py::create_order`
2. Body validated by `CreateOrderRequest` (Pydantic)
3. Delegates to `OrderService.create()` in `app/services/order_service.py`
4. Service writes to `orders` table via SQLAlchemy AsyncSession
5. Emits event to Redis stream `orders.created`
6. Background worker (`app/tasks/order_events.py`) picks up the event

## Common workflows
### Add a new endpoint
1. Add router in `app/api/<resource>.py`
2. Add service in `app/services/<resource>_service.py`
3. Add model if needed, then migration (`alembic revision --autogenerate`)
4. Add test in `tests/api/test_<resource>.py`

### Add a migration
See [db-migration](../db-migration) skill. Use `alembic revision -m "..."`; never edit an applied migration.

## Landmines
- `config.py` reads from env at import time — imports before env is loaded will use defaults
- `OrderService._legacy_calculate_total` is used by two old endpoints; do not delete without checking `grep _legacy_calculate_total`
- Tests use SQLite in CI but Postgres locally — Postgres-only features must be tested integration-style

## Who to ask
- Orders domain: @alice
- Auth: @bob
- Deploys / infra: @carol
```

## Steps if info is missing

- No README / no Makefile → say so. Suggest the joiner run `git log --format='%an' | sort | uniq -c | sort -rn | head` to find who to ask
- No tests → red flag; note it in the "Landmines"
- Multiple obvious entry points (monorepo) → produce one guide per package OR a top-level "how packages relate"

## Rules

- NEVER invent structure — if you can't tell what a folder is for, say so and mark it as "ask the team"
- NEVER copy the README's marketing pitch — extract what's true from the code
- ALWAYS include a "get it running in 5 minutes" section — most onboarding pain is here
- ALWAYS include the "5 files to read" list — a new joiner drowning in 500 files needs a starting order
- ALWAYS include landmines section — the WHY of weird code is what's expensive to lose
