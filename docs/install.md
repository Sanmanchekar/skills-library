# Install guide — skills-library

Each skill installs with one command. The installer asks which AI coding agent to target and drops the skill into the right location.

## One-liner (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- <skill-name>
```

Example:

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review
```

You'll be shown a **pure-bash checkbox picker** — real arrow-key navigation, no dependencies, works on macOS default bash (3.2) and any modern bash.

```
  Select target agents for 'code-review'
  ↑↓ move · SPACE toggle · A all · ENTER confirm · ESC cancel

  ▶ [ ] claude-code    Anthropic Claude Code CLI
    [ ] codex-cli      OpenAI Codex CLI
    [x] cursor         Cursor IDE
    [ ] aider          Aider CLI
    [x] continue       Continue (VS Code / JetBrains)
    [ ] cline          Cline (VS Code)
    ...
```

**Keys**

| Key | Action |
|---|---|
| ↑ / ↓ | Move cursor (wraps at top/bottom) |
| SPACE | Toggle the highlighted item |
| A | Toggle all (if any unselected → select all; else deselect all) |
| ENTER | Confirm selection and install |
| ESC | Cancel (1s delay — Q is instant) |
| Q | Cancel immediately |

If ENTER is pressed with nothing selected, the installer shows "Nothing selected" and exits without installing anything.

## Non-interactive

Pass `--agent` (single, comma-separated, or `all`) and optionally `--scope`:

```bash
# Single agent
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent claude-code --scope user

# Multiple agents (comma-separated)
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent claude-code,cursor,aider

# Every supported agent
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent all
```

- `--agent`: single agent, comma-separated list, or `all`
- `--scope`: `user` (global, default) or `project` (installs into current repo)

## Install into a project (not user-global)

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent claude-code --scope project
```

This drops files into the current directory (e.g., `.claude/skills/code-review/SKILL.md`) instead of `~/.claude/`.

## Local checkout

Clone once, install any skill without a network call:

```bash
git clone https://github.com/Sanmanchekar/skills-library.git
cd skills-library
./install.sh code-review
```

## Install everything

For every skill:

```bash
for skill in $(ls skills/); do
  ./install.sh "$skill" --agent claude-code
done
```

Or for every agent:

```bash
./install.sh code-review --agent all
```

## Where files land per agent

| Agent | Path |
|---|---|
| Claude Code (user) | `~/.claude/skills/<name>/SKILL.md` |
| Claude Code (project) | `.claude/skills/<name>/SKILL.md` |
| Codex CLI | `~/.codex/prompts/<name>.md` |
| Cursor | `.cursor/rules/<name>.mdc` |
| Aider | `.aider/conventions/<name>.md` (+ registered in `.aider.conf.yml`) |
| Continue | `~/.continue/rules/<name>.md` (or `.continue/rules/` for project) |
| Cline | `.clinerules/<name>.md` |
| Windsurf | `.windsurf/rules/<name>.md` |
| Cody | `.sourcegraph/<name>.md` |
| Copilot Chat | Appended to `.github/copilot-instructions.md` between markers |
| Roo Code | `.roo/rules/<name>.md` |
| Zed AI | `~/.config/zed/prompts/<name>.md` |

## Uninstall

Just delete the file(s). No system-wide registry.

## Troubleshooting

**"curl: (22) The requested URL returned error: 404"**
The skill name doesn't exist. Run `ls skills/` in a local checkout, or check the [root README](../README.md) skill table.

**"fetch: could not find SKILL.md"**
The repo owner/branch isn't right. Override:

```bash
export SKILLS_LIBRARY_OWNER=your-fork-owner
export SKILLS_LIBRARY_BRANCH=main
./install.sh <skill-name>
```

**Agent doesn't pick up the skill**
- Claude Code: restart the CLI so it re-scans `~/.claude/skills/`
- Cursor: reload the window
- Copilot Chat: re-open the repo (it re-reads `.github/copilot-instructions.md`)
