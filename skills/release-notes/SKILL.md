---
name: release-notes
description: Generate release notes / changelog entries from merged PRs, commits, or a version diff. Groups by user impact (New / Improved / Fixed / Security / Deprecated / Breaking) with concise user-facing language — not "refactored X" or commit SHAs. Triggered when the user asks to write release notes, changelog, or "what changed since vX".
---

# release-notes

## When to use

- User asks: "release notes for vX", "changelog since Y", "what shipped this week"
- CI / release automation triggers on tag push

## Steps

1. **Get the input**:
   - `git log v1.2.0..v1.3.0 --oneline` OR
   - `gh pr list --search "merged:>2026-07-01" --state merged` OR
   - a specific list of PRs

2. **Read each PR / commit** to understand the user impact. Do NOT copy the commit subject verbatim — translate.

3. **Group by user impact** (in this exact order):

   | Group | Icon | What goes here |
   |---|---|---|
   | 🚨 Breaking | 🚨 | API changes that break existing consumers |
   | ✨ New | ✨ | New features / capabilities |
   | 🔧 Improved | 🔧 | Meaningful improvements to existing features (perf, UX) |
   | 🐛 Fixed | 🐛 | Bug fixes users would notice |
   | 🔒 Security | 🔒 | Security fixes (CVE reference if applicable) |
   | ⚠️ Deprecated | ⚠️ | Features slated for removal, with sunset date |
   | 🏗️ Internal | 🏗️ | Ship-worthy refactors (optional — often omitted in public notes) |

4. **Skip pure-internal changes** in user-facing notes — bumps, chores, test-only, docs-only, CI. Include them only in developer-audience changelogs.

5. **Every entry is one line, past tense, active voice**:
   - ✅ "Added support for CSV export"
   - ❌ "This PR adds CSV export capability"
   - ❌ "Refactored the export module"

6. **Breaking changes get a subsection with migration steps**.

## Output format

```markdown
# v1.3.0 — 2026-07-14

## 🚨 Breaking
- Renamed `POST /orders` response field `total` to `total_amount`. Update clients.
  - Migration: `sed -i 's/data\.total\b/data.total_amount/g' src/`

## ✨ New
- Added CSV export from the reports page
- Added SSO login via Okta

## 🔧 Improved
- Reduced dashboard load time from 3.2s to 0.9s
- Payment errors now surface the reason inline instead of a generic message

## 🐛 Fixed
- Order search no longer misses orders with unicode in the customer name
- Fixed a race condition that duplicated webhook deliveries on retry

## 🔒 Security
- Fixed CVE-2026-1234 in the file-upload path (upgrade required)
```

## Rules

- NEVER paste commit subjects verbatim — translate to user-facing language
- NEVER include internal refactors in the "New" or "Improved" sections
- NEVER omit a breaking-change migration step
- ALWAYS sort within each group by impact (biggest first)
- If the changeset is trivial, say so — "v1.3.1 — minor bug fixes" is a valid release note
