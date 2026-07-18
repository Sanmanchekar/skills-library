# Terminal summary format

Read this file when Step 6 needs to print the summary.

## Format

```
╭─ Capability audit — <service-name> ─────────────────────────────────╮
│  Run #<N> · <UTC timestamp> · <actor>                               │
│  Domain: <one-sentence domain statement>                            │
╰──────────────────────────────────────────────────────────────────────╯

Summary
  <N> capabilities recommended for delegation
  <N> total findings · <N> open · <N> resolved · <N> wontfix
  Δ vs Run #<N-1>: <one-line diff>

By capability
  🔴 <n>  🟠 <n>  🟡 <n>  🟢 <n>   <capability>   <N> sites → <N> open   → <recommended-service>
  ...

Top 5 by blast radius
  <emoji> <cap-id>   <file:line>   <one-line coupling smell>
  ...

Recent runs (last 3)
  #<N>    today       <findings>  <open>  <resolved>  (<diff summary>)
  #<N-1>  <days> ago  <findings>  <open>  <resolved>  (<diff summary>)
  #<N-2>  <days> ago  <findings>  <open>  <resolved>  (<diff summary>)

Regressions (was done, back to open)
  ⚠️ <cap-id>  <file:line>  <one-line why>
  ...
  (omit this whole block if no regressions this run)

Files written
  .audit/capability/TODO.md                     (updated: +<N> new, −<N> auto-resolved, <N> regression)
  .audit/capability/shopping-list-<date>.md     (new snapshot)
  (In dry-run mode: "Would write" instead of "Files written")

Next
  1. Review .audit/capability/TODO.md
  2. Prioritize <top CRITICAL id> (<severity>) this sprint
  3. Hand the <capability>-service consumer contract to <owner> for scoping
```

## Width-adaptive rendering

- If terminal is < 100 cols: drop the box-drawing header, use `===` separators instead
- If terminal is < 80 cols: drop the emoji-count row in "By capability", keep only the count line
- If output is being piped (`| grep`, `| less`, non-TTY): drop all ANSI colors, use plain text; box-drawing chars are safe (they're just Unicode)

## Marriage between terminal + TODO.md + snapshots

The **todo id** (`cap-notif-001`) is the join key. Every axis is kept consistent across all three surfaces:

| Property | Terminal | TODO.md | shopping-list-*.md |
|---|---|---|---|
| Run number | `Run #3` header | `<!-- audit_run: 3 -->` marker | Referenced in the snapshot body |
| Timestamp | UTC in header | `<!-- last_audited_at: ... -->` | Filename date |
| Todo IDs | Shown in Top-N + Regressions | Each item labeled `cap-notif-001` | Referenced in the recommendation body |
| Severity emojis | 🔴🟠🟡🟢 | Same on every item | Same in coupling breakdown |
| Capability slug | `notifications` | Heading `## Capability: notifications` | Same slug |
| Domain statement | Header | `<!-- domain_statement: ... -->` | First paragraph |

## Rules

- ALWAYS start the terminal output with a UTC-timestamped header including run number, actor, and the domain statement
- ALWAYS show the diff vs prior run when a prior run exists (`Δ vs Run #N`)
- ALWAYS surface regressions (⚠️) as their own block when present — they matter more than raw open counts
- ALWAYS end with the "Files written" block so the user knows where the details live
- ALWAYS end with a "Next" block naming the highest-severity open item by id
- If output is being piped or the terminal is narrow, use the width-adaptive fallbacks — never print box-drawing that will visually break on 60-col terminals
