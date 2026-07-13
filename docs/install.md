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

You'll be prompted:

```
Which AI coding agent do you want to install this skill for?

  1) claude-code    (Anthropic Claude Code CLI)
  2) codex-cli      (OpenAI Codex CLI)
  3) cursor         (Cursor IDE)
  4) aider          (Aider CLI)
  5) continue       (Continue for VS Code / JetBrains)
  6) cline          (Cline for VS Code)
  7) windsurf       (Windsurf / Codeium IDE)
  8) cody           (Sourcegraph Cody)
  9) copilot-chat   (GitHub Copilot Chat — .github/copilot-instructions.md)
 10) roo-code       (Roo Code for VS Code)
 11) zed            (Zed AI)
 12) all            (install for every detected agent on this machine)

Enter number or agent name [1]:
```

## Non-interactive

Pass `--agent` and optionally `--scope`:

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh \
  | bash -s -- code-review --agent claude-code --scope user
```

- `--agent`: one of the 11 supported agents, or `all`
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
