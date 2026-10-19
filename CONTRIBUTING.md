# Contributing to skills-library

## Add a new skill

1. Create `skills/<your-skill-name>/` (lowercase, hyphen-separated)
2. Add `SKILL.md` following the spec below
3. Add `README.md` (SEO-optimized landing page) — see any existing skill for template
4. Update the skill table in the root [README.md](README.md)
5. **Wire it into the lifecycle** — add a node to [`lifecycle/graph.yaml`](lifecycle/graph.yaml) (phase, triggers, inputs, outputs), list it under its phase agent's `owns`, and add at least one edge in or out
6. Add a routing case to [`lifecycle/evals/routing.yaml`](lifecycle/evals/routing.yaml) for each trigger phrase that should reach it (and a `not:` for any look-alike skill)
7. Run `pip install pyyaml && python3 lifecycle/build.py && python3 lifecycle/build.py eval` and commit the generated files
8. Open a PR

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

## Lifecycle metadata lives in the graph, not the frontmatter

Keep `SKILL.md` frontmatter to `name`, `description` and `allowed-tools`. Agents treat unknown keys differently, so all routing metadata goes in `lifecycle/graph.yaml`. `build.py` then appends a generated `## Lifecycle` section to each SKILL.md (between `<!-- lifecycle:begin -->` markers). That section tells any agent, even one without the router, what comes before and after. Never edit it by hand.

| Field | Meaning |
|---|---|
| `triggers.intents` | Regexes matched against the user's prompt |
| `triggers.paths` | Globs matched against changed / edited files |
| `triggers.content` | Regexes matched against added diff lines |
| `triggers.events` / `always_on` | Lifecycle events it listens to / always runs on |
| `inputs` / `outputs` | Artifact types read from / written to `.lifecycle/<run>/` |

Generated files (`skills/lifecycle-router/references/registry.json`, `agents/*.md`, `docs/lifecycle.md`, `lifecycle/bundles.txt`, the `## Lifecycle` sections) are checked for drift in CI.

## CI

Every PR runs `.github/workflows/validate.yml`, which:
- Checks every `skills/*/SKILL.md` has valid frontmatter (`name`, `description`)
- Checks every skill has a `README.md`
- Checks the root README index lists every skill
- Validates `lifecycle/graph.yaml` (every skill has a node, edges and loops reference real skills, every loop has a cap and exit) and fails if generated files are stale
- Runs the routing evals and router / hook / installer smoke tests

## License

By contributing you agree your contributions are MIT-licensed.
