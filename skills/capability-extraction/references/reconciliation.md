# Reconciliation on re-run

Read this file when a prior `.audit/capability/TODO.md` exists and Step 6 needs to merge.

## Behavior modes

- **Default** — write both files, merge with existing TODO.md
- **`dry-run`** — print the terminal summary + shopping list, do NOT touch the filesystem. For preview before commit.
- **`regen-contract`** — re-derive the Consumer Contract sections from the fresh scan, overwriting user edits (default: preserve user-edited contracts)
- **`no-history`** — skip appending to the Audit history table (useful for CI / test runs)

Ask the user which mode if unclear.

## The 6-case reconciliation table

Before writing a new TODO.md, PARSE the existing one (JSON canonical for prior state; markdown for latest human toggle). Then apply this table per finding:

| Existing state | Fresh scan finding | Action |
|---|---|---|
| absent | new site found | add as `- [ ]` new item with next available `cap-<cap>-NNN` id |
| `[ ]` open | site still exists | keep verbatim (including user edits to description) |
| `[ ]` open | site GONE | flip to `[x]` with note `[auto-resolved YYYY-MM-DD — call site no longer present]` |
| `[x]` done | site GONE | keep as done, no change |
| `[x]` done | site STILL PRESENT | flag as ⚠️ **regression**: flip back to `[ ]`, prepend `⚠️ regressed — was marked done but call site reappeared` |
| `[x]` done with `#wontfix` tag | either | preserve verbatim — user's explicit decision |

## Preservation rules

- **Team notes** — content between `<!-- notes-start -->` and `<!-- notes-end -->` is copied VERBATIM. Never modified.
- **Consumer contract** — content between `<!-- contract-start -->` and `<!-- contract-end -->` is preserved verbatim unless `regen-contract` mode was requested.
- **Kept-local block** — content between `<!-- kept-local-start -->` and `<!-- kept-local-end -->` is preserved (users may edit); appended to only if the fresh scan surfaces a new domain-fit capability.
- **Audit history** — append a new row per run with: run number, date, total findings, open count, resolved count, one-line Δ vs prior run. Never rewrite prior rows.

## Precedence rules when markdown and JSON disagree

- JSON wins for **prior-run values** (severity, file, line, reason, created_run, history) — those are canonical
- Markdown wins for the **latest human toggle** — user may have just checked `[x]` and JSON hasn't regenerated yet
- If a `#wontfix` appears in markdown but not JSON, honor markdown and update JSON to `status: wontfix` in the next write
- If the JSON block is malformed or missing entirely, fall back to markdown parsing with a `⚠️ warning: JSON state block missing/corrupt — reconstructing from markdown` line in the terminal summary

## ID monotonicity

- Todo ids are monotonic per capability
- If `cap-notif-003` was retracted (call site gone before ever being marked done), the NEXT new notification finding gets `cap-notif-004`, not `cap-notif-003`
- Ids are never re-used
