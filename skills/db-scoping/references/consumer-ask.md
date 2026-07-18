# Writing the consumer's data ask

Read this file when Step 4 needs to produce field 4 (What this service needs from the owning domain).

Frame from THIS service's perspective — what interface does it want from the owning domain, instead of the raw table. Do NOT specify the transport (REST/gRPC/event/replica) — that's the owner's decision informed by all consumers.

## Template

```markdown
### What this service needs

**As a consumer**, this service needs to <read | be notified about> <foreign data> WITHOUT touching `<table>` directly:

- `get_<entity>(<id>) -> { <only the fields we actually use> }` — <when we call it, what we key on>

**Access pattern we need**:
- <point-lookup by id> / <batch by ids (list the call sites that loop)> / <filtered list>

**Freshness we need**:
- <strong — must reflect the latest write> OR <eventual — seconds of lag OK> OR <daily snapshot OK>

**If a write is involved** (foreign-write cases):
- We currently write `<table>` at `<file:line>` to <effect>. We need `<owner>` to expose `<command(...)>` so the owner performs that write — we stop being a second writer.

**What we do NOT need from this party**:
- <the full row — we only read N of M columns>
- <write access — read-only is enough>
- <joins performed on our side — the owner can pre-join and hand us a projection>
```

The point: this service states the *data* it needs and the *shape* it needs it in — it does not design the owner's storage.

## Rules

- ALWAYS list only the columns / fields the service actually reads (not the whole row)
- ALWAYS state the access pattern (point-lookup / batch / filtered list) — the owner needs this to design the interface
- ALWAYS state freshness needed — strong / eventual / snapshot
- For foreign-write cases, frame the ask as "we want to STOP being a second writer" and name the command the owner should expose
- NEVER specify transport (REST / gRPC / event / replica) — owner's call
- NEVER specify storage / index / partition choices — owner's call
