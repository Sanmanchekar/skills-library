# Terminal summary format — db-scoping

Read this file when Step 7 needs to print the summary.

## Format

```
╭─ DB scoping audit — <service-name> ─────────────────────────────────╮
│  Run #<N> · <UTC> · <actor>                                         │
│  Owns: <one-sentence owned-data statement>                          │
╰──────────────────────────────────────────────────────────────────────╯

Inventory
  <N> tables touched · <owned> owned · <fr> foreign-read · <fw> foreign-write · <sr> shared-ref · <amb> ambient
  Ambient surface: imports <declared> tables, queries <queried> → <unused> unused
  Δ vs Run #<N-1>: <one-line diff>

By owning domain
  🔴 <n>  🟠 <n>  🟡 <n>   <domain>   <tables: list>   <N> open   (R/W)
  ...

Top 5 by dependency risk
  <emoji> <dbdep-id>   <table>   <file:line>   <one-line smell (foreign-write / cross-domain-txn / join)>
  ...

Recent runs (last 3)
  #<N>    today       <touched> tables  <foreign> foreign  <open> open
  ...

Regressions (direct access reappeared)
  ⚠️ <dbdep-id>  <table>  <file:line>
  (omit block if none)

Files written
  .audit/db-scoping/TODO.md                          (updated: +<N> new, −<N> auto-resolved)
  .audit/db-scoping/data-dependencies-<date>.md      (new snapshot)

Next
  1. Review .audit/db-scoping/TODO.md
  2. Fix <top CRITICAL id> (<severity>) — <foreign-write is the priority>
  3. Confirm inferred ownership with architecture, then hand each domain its consumer ask
```

## Width-adaptive rendering

- If terminal is < 100 cols: drop the box-drawing header, use `===` separators instead
- If terminal is < 80 cols: drop the emoji-count row in "By owning domain", keep only the count line
- If output is being piped or non-TTY: drop ANSI colors, use plain text; box-drawing chars are safe

## Marriage between terminal + TODO.md + snapshots

The **`dbdep-<domain>-NNN`** id is the join key across all three surfaces. Every axis is kept consistent:

| Property | Terminal | TODO.md | data-dependencies-*.md |
|---|---|---|---|
| Run number | `Run #3` header | `<!-- audit_run: 3 -->` | Referenced in snapshot body |
| Timestamp | UTC in header | `<!-- last_audited_at: ... -->` | Filename date |
| Todo IDs | Shown in Top-N + Regressions | Each item labeled `dbdep-identity-001` | Referenced in the domain recommendation |
| Severity emojis | 🔴🟠🟡🟢 | Same on every item | Same in coupling smells |
| Domain slug | `identity` | `## Domain: identity` heading | Same slug |
| Owned-data statement | Header | `<!-- owned_data_statement: ... -->` | First paragraph |

## Rules

- ALWAYS start with a UTC-timestamped header including run number, actor, and owned-data statement
- ALWAYS show the diff vs prior run when a prior run exists
- ALWAYS surface regressions (⚠️) as their own block when present
- ALWAYS end with "Files written" and "Next" blocks
- Width-adaptive fallbacks — never print box-drawing that will visually break on 60-col terminals
