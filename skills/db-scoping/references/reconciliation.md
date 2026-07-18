# Reconciliation on re-run — db-scoping

Read this file when a prior `.audit/db-scoping/TODO.md` exists and Step 7 needs to merge.

## Behavior modes

- **Default** — write both files, merge with existing TODO.md
- **`dry-run`** — print the terminal summary + shopping list, do NOT touch the filesystem
- **`regen-contract`** — re-derive the Consumer Ask sections from the fresh scan, overwriting user edits (default: preserve them)
- **`no-history`** — skip appending to the Audit history table (useful for CI / test runs)

## The 6-case reconciliation table

Before writing a new TODO.md, PARSE the existing one (JSON canonical for prior state; markdown for latest human toggle). Then apply this table per todo:

| Existing state | Fresh scan | Action |
|---|---|---|
| absent | new foreign access found | add `- [ ]` with next `dbdep-<domain>-NNN` |
| `[ ]` open | access still present | keep verbatim (incl. user edits) |
| `[ ]` open | access GONE | flip to `[x]` + note `[auto-resolved YYYY-MM-DD — access no longer present]` |
| `[x]` done | access GONE | keep done |
| `[x]` done | access STILL present | ⚠️ **regression** — flip to `[ ]`, prepend `⚠️ regressed — direct access reappeared` |
| `[x]` done `#wontfix` | either | preserve verbatim (explicit decision) |

## Preservation rules

- **Team notes** — content between `<!-- notes-start -->` and `<!-- notes-end -->` — copied VERBATIM. Never modified.
- **Consumer ask** — content between `<!-- contract-start -->` and `<!-- contract-end -->` — preserved verbatim unless `regen-contract` mode was requested.
- **Owned** — content between `<!-- owned-start -->` and `<!-- owned-end -->` — preserved; append-only.
- **Ambient** — content between `<!-- ambient-start -->` and `<!-- ambient-end -->` — regenerated from fresh scan (accurate counts matter).
- **Confirm ownership** — content between `<!-- confirm-start -->` and `<!-- confirm-end -->` — preserved verbatim. If a user edited an inferred `institutes → identity` line to remove `(inferred)` or add `#confirmed`, honor it as evidenced on future runs; do not revert to `inferred`.
- **Inventory** — content between `<!-- inventory-start -->` and `<!-- inventory-end -->` — regenerated from fresh scan.
- **Audit history** — append a new row per run. Never rewrite prior rows.

## Precedence rules when markdown and JSON disagree

- JSON wins for **prior-run values** (severity, table, file, line, reason, created_run, history, inferred/confirmed ownership) — those are canonical
- Markdown wins for **latest human toggle** — user may have just checked `[x]` and JSON hasn't regenerated yet
- If a `#wontfix` appears in markdown but not JSON, honor markdown and update JSON to `status: wontfix` in the next write
- If a user removed `(inferred)` or added `#confirmed` in the Confirm block, promote `inferred: false` in JSON
- If the JSON block is malformed or missing, fall back to markdown parsing with a `⚠️ warning: JSON state block missing/corrupt — reconstructing from markdown` line in the terminal summary

## ID monotonicity

- Todo ids are monotonic per domain
- If `dbdep-identity-003` was retracted, the NEXT new identity finding gets `dbdep-identity-004`, not `dbdep-identity-003`
- Ids are never re-used
