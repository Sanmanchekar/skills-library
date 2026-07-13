#!/usr/bin/env bash
# skills-library universal installer
# Usage:
#   curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- <skill-name>
#   ./install.sh <skill-name>              # local checkout
#   ./install.sh <skill-name> --agent claude-code   # non-interactive
#   ./install.sh <skill-name> --scope user|project  # default: user
#
# Supported agents (auto-detected + interactive prompt):
#   claude-code, codex-cli, cursor, aider, continue, cline,
#   windsurf, cody, copilot-chat, roo-code, zed

set -euo pipefail

REPO_OWNER="${SKILLS_LIBRARY_OWNER:-Sanmanchekar}"
REPO_NAME="${SKILLS_LIBRARY_REPO:-skills-library}"
REPO_BRANCH="${SKILLS_LIBRARY_BRANCH:-main}"
RAW_BASE="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${REPO_BRANCH}"

SKILL_NAME="${1:-}"
shift || true

AGENT=""
SCOPE="user"
while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="$2"; shift 2 ;;
    --scope) SCOPE="$2"; shift 2 ;;
    --agent=*) AGENT="${1#*=}"; shift ;;
    --scope=*) SCOPE="${1#*=}"; shift ;;
    *) echo "Unknown flag: $1" >&2; exit 2 ;;
  esac
done

if [ -z "$SKILL_NAME" ]; then
  echo "Usage: install.sh <skill-name> [--agent <agent>] [--scope user|project]" >&2
  echo "Available skills: see README.md" >&2
  exit 2
fi

# ---- locate skill source (local checkout or remote) ----
SCRIPT_DIR="$( cd -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" &>/dev/null && pwd )" || SCRIPT_DIR=""
LOCAL_SKILL_DIR=""
if [ -n "$SCRIPT_DIR" ] && [ -d "$SCRIPT_DIR/skills/$SKILL_NAME" ]; then
  LOCAL_SKILL_DIR="$SCRIPT_DIR/skills/$SKILL_NAME"
fi

fetch() {
  # $1 = relative path from skill dir, $2 = destination path
  local rel="$1" dest="$2"
  if [ -n "$LOCAL_SKILL_DIR" ]; then
    if [ -f "$LOCAL_SKILL_DIR/$rel" ]; then
      mkdir -p "$(dirname "$dest")"
      cp "$LOCAL_SKILL_DIR/$rel" "$dest"
      return 0
    else
      return 1
    fi
  else
    local url="$RAW_BASE/skills/$SKILL_NAME/$rel"
    mkdir -p "$(dirname "$dest")"
    if curl -fsSL "$url" -o "$dest"; then
      return 0
    else
      return 1
    fi
  fi
}

# ---- interactive agent picker ----
if [ -z "$AGENT" ]; then
  cat <<'MENU'
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

MENU
  printf "Enter number or agent name [1]: "
  read -r choice </dev/tty || choice=1
  choice="${choice:-1}"
  case "$choice" in
    1|claude-code) AGENT=claude-code ;;
    2|codex-cli) AGENT=codex-cli ;;
    3|cursor) AGENT=cursor ;;
    4|aider) AGENT=aider ;;
    5|continue) AGENT=continue ;;
    6|cline) AGENT=cline ;;
    7|windsurf) AGENT=windsurf ;;
    8|cody) AGENT=cody ;;
    9|copilot-chat) AGENT=copilot-chat ;;
    10|roo-code) AGENT=roo-code ;;
    11|zed) AGENT=zed ;;
    12|all) AGENT=all ;;
    *) AGENT="$choice" ;;
  esac
fi

# ---- resolve install path per agent ----
install_for() {
  local agent="$1"
  local dest_dir=""
  case "$agent" in
    claude-code)
      if [ "$SCOPE" = "project" ]; then dest_dir=".claude/skills/$SKILL_NAME"; else dest_dir="$HOME/.claude/skills/$SKILL_NAME"; fi
      fetch "SKILL.md" "$dest_dir/SKILL.md" || { echo "FAIL: could not fetch SKILL.md" >&2; return 1; }
      # optional references
      fetch "references/index.md" "$dest_dir/references/index.md" 2>/dev/null || true
      ;;
    codex-cli)
      if [ "$SCOPE" = "project" ]; then dest_dir=".codex/prompts"; else dest_dir="$HOME/.codex/prompts"; fi
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    cursor)
      dest_dir=".cursor/rules"
      mkdir -p "$dest_dir"
      # translate SKILL.md -> .mdc frontmatter
      local tmp; tmp="$(mktemp)"
      fetch "SKILL.md" "$tmp" || return 1
      {
        echo "---"
        echo "description: $(grep -m1 '^description:' "$tmp" | sed 's/^description: *//')"
        echo "alwaysApply: false"
        echo "---"
        awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$tmp"
      } > "$dest_dir/${SKILL_NAME}.mdc"
      rm -f "$tmp"
      ;;
    aider)
      dest_dir=".aider/conventions"
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      # register in .aider.conf.yml if present
      if [ -f ".aider.conf.yml" ] && ! grep -q "$SKILL_NAME" .aider.conf.yml; then
        printf "\nread:\n  - .aider/conventions/%s.md\n" "$SKILL_NAME" >> .aider.conf.yml
      fi
      ;;
    continue)
      if [ "$SCOPE" = "project" ]; then dest_dir=".continue/rules"; else dest_dir="$HOME/.continue/rules"; fi
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    cline)
      dest_dir=".clinerules"
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    windsurf)
      dest_dir=".windsurf/rules"
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    cody)
      dest_dir=".sourcegraph"
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    copilot-chat)
      dest_dir=".github"
      mkdir -p "$dest_dir"
      local tmp; tmp="$(mktemp)"
      fetch "SKILL.md" "$tmp" || return 1
      touch "$dest_dir/copilot-instructions.md"
      if ! grep -q "<!-- skill:$SKILL_NAME -->" "$dest_dir/copilot-instructions.md"; then
        {
          echo ""
          echo "<!-- skill:$SKILL_NAME -->"
          awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$tmp"
          echo "<!-- /skill:$SKILL_NAME -->"
        } >> "$dest_dir/copilot-instructions.md"
      fi
      rm -f "$tmp"
      ;;
    roo-code)
      dest_dir=".roo/rules"
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    zed)
      if [ "$SCOPE" = "project" ]; then dest_dir=".zed/prompts"; else dest_dir="$HOME/.config/zed/prompts"; fi
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    *)
      echo "Unknown agent: $agent" >&2
      return 2
      ;;
  esac
  echo "✓ Installed $SKILL_NAME for $agent → $dest_dir"
}

if [ "$AGENT" = "all" ]; then
  for a in claude-code codex-cli cursor aider continue cline windsurf cody copilot-chat roo-code zed; do
    install_for "$a" || true
  done
else
  install_for "$AGENT"
fi
