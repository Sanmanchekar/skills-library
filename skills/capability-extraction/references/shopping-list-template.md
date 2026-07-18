# Shopping list template — capability-extraction

Read this file when Step 5 needs to produce the evidence packet.

Also used verbatim as the body of the per-run `.audit/capability/shopping-list-YYYY-MM-DD.md` snapshot.

```markdown
# Capability audit — <service name>

**Scanned at**: <UTC>
**Service**: <path>
**This service's real job**: <one sentence — the domain statement>

## Summary
This service currently owns N capabilities that don't fit its domain. Ranked by value of delegating:

1. <capability> — <coupling severity> · <hit count>
2. <capability> — ...
3. ...

Delegating these to centralized parties would remove ~X lines of code and unblock Y coupling smells.

## Shopping list

### 1. Needs: centralized `<capability>-service`

**What's here now**
- N sites; providers: A (n), B (n), C (n)
- Sample: `path:line`, `path:line`, `path:line`, ...

**Coupling smells**
- CRITICAL: `path:line` — <specific coupling smell, with concrete impact>
- HIGH: N sites have their own retry loops with different backoff (X exponential, Y fixed, Z none).
- HIGH: opt-out check present in N sites, MISSING in M (regulatory: <specific regime>).
- MEDIUM: N different template-rendering approaches within this one service.

**Why it doesn't fit the domain**
<One sentence anchored to the service's domain statement.>

**What this service needs (consumer's ask)**
<See references/consumer-ask.md — use that template>

**Impact of delegating**
- Removes ~<N> lines from this service (retry loops, template rendering, provider adapters)
- Drops direct dependencies: <list>
- Unblocks CRITICAL coupling in `<path:line>` — <specific impact>
- Eliminates <specific regulatory / operational gap>

---

### 2. Needs: centralized `<capability>-service`
... (same shape)

---

## What this service should keep

Capabilities that DO fit the domain and should stay local:
- <capability 1>
- <capability 2>
- ...

## What's out of scope for this audit
- How the centralized services are built (their design is their team's problem, informed by ALL consumers, not just this one)
- Vendor selection
- Whether any of these centralized services already exist in some form elsewhere in the org (that's a discovery question for architecture)
- Team ownership of the new centralized services

## Next step
Hand this shopping list to architecture / platform. They'll:
- Check if any of these centralized services already exist
- If not, sequence their creation
- Come back to this service team with the actual provider API to migrate to
```
