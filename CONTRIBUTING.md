# Contributing to skills-library

## Add a new skill

1. Create `skills/<your-skill-name>/` (lowercase, hyphen-separated)
2. Add `SKILL.md` following the spec below
3. Add `README.md` (SEO-optimized landing page) — see any existing skill for template
4. Update the skill table in the root [README.md](README.md)
5. Open a PR

## SKILL.md spec

Every skill's `SKILL.md` MUST be a markdown file with YAML frontmatter:

```markdown
---
name: your-skill-name
description: One-sentence summary of when this skill triggers and what it produces. This exact text is what agents read to decide whether to activate the skill, so make it specific.
---

# Your Skill Title

## When to use

Bullet list of concrete triggers. Include the phrases a user would type
("review this PR", "write a runbook", "generate release notes") and the
patterns in the code / repo state that should activate the skill.

## Steps

Numbered, mechanical sequence the agent should follow. No prose paragraphs.

1. Do X
2. Then Y
3. Output format: ...

## Output format

Show the exact shape of the output — table, headings, code blocks — that
the skill should produce. Agents copy this literally.

## Rules

- Never do X
- Always Y
- Prefer Z over W
```

## Rules for good skills

1. **One skill, one job.** If it needs two `SKILL.md` files, it's two skills.
2. **Structured over prose.** Decision tables, checklists, numbered steps — not paragraphs.
3. **Concrete examples.** Show input → output for at least one case.
4. **No hallucination surface.** If the skill produces code, tell the agent to read the target file first.
5. **Portable.** Assume the SKILL.md may be installed into Claude Code, Cursor, Copilot, Aider, etc. — don't hard-code CLI flags for one agent.

## README.md (per-skill) spec

Each skill README serves as its SEO landing page. Structure:

```markdown
# <Keyword-rich H1> — for Claude Code, Cursor, Copilot, Aider

> One-sentence pitch containing the search phrases the target user would type.

## Install

`curl -sSL .../install.sh | bash -s -- <skill-name>`

## What it does
## When it triggers
## Example
## Compatible with
## Related skills
```

## CI

Every PR runs `.github/workflows/validate.yml`, which:
- Checks every `skills/*/SKILL.md` has valid frontmatter (`name`, `description`)
- Checks every skill has a `README.md`
- Checks the root README index lists every skill

## License

By contributing you agree your contributions are MIT-licensed.
