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

You'll be shown a **pure-bash checkbox picker** with visible Submit / Cancel buttons. Real arrow-key navigation, no dependencies, works on macOS default bash (3.2) and any modern bash.

```
  Select target agents for 'code-review'
  ↑↓ move · ENTER toggle (on agent) or activate (on button) · A toggle all · ESC cancel

  ▶ [ ] claude-code    Anthropic Claude Code CLI
    [x] codex-cli      OpenAI Codex CLI
    [ ] cursor         Cursor IDE
    [x] aider          Aider CLI
    [ ] continue       Continue (VS Code / JetBrains)
    ...
    [ ] zed            Zed AI
    ─────────────────────────────────────────────────────────
    [ Submit — install for 2 selected ]
    [ Cancel ]
```

**Keys**

| Key | Action |
|---|---|
| ↑ / ↓ | Move cursor through agents + Submit + Cancel (wraps at top / bottom) |
| ENTER on an agent | Toggle that agent's checkbox |
| ENTER on **Submit** | Install for the selected agents |
| ENTER on **Cancel** | Abort without installing |
| SPACE | Also toggles the highlighted agent (alt to ENTER) |
| A | Toggle all agents (select-all / deselect-all) |
| ESC | Cancel (~1s delay) |
| Q | Cancel immediately |

The Submit button's label shows the current selection count in real time (e.g. `[ Submit — install for 3 selected ]`) and is dimmed when no agents are selected. Pressing ENTER on Submit with 0 selected is a no-op — navigate to Cancel or press ESC/Q to abort.

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
