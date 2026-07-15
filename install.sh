#!/usr/bin/env bash
# skills-library universal installer
# Usage:
#   curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- <skill-name>
#   ./install.sh <skill-name>                                       # local checkout, interactive checkbox picker
#   ./install.sh <skill-name> --agent claude-code                   # single agent (non-interactive)
#   ./install.sh <skill-name> --agent claude-code,cursor,aider      # multiple agents (comma-separated)
#   ./install.sh <skill-name> --agent all                           # every supported agent
#   ./install.sh <skill-name> --scope user|project                  # default: user
#
# Supported agents:
#   claude-code, codex-cli, cursor, aider, continue, cline,
#   windsurf, cody, copilot-chat, roo-code, zed
#
# Interactive picker prefers a real TUI checkbox widget (whiptail / gum / dialog).
# Falls back to a numbered-list multi-select (space-separated) when none is present.

set -euo pipefail

REPO_OWNER="${SKILLS_LIBRARY_OWNER:-Sanmanchekar}"
REPO_NAME="${SKILLS_LIBRARY_REPO:-skills-library}"
REPO_BRANCH="${SKILLS_LIBRARY_BRANCH:-main}"
RAW_BASE="https://raw.githubusercontent.com/${REPO_OWNER}/${REPO_NAME}/${REPO_BRANCH}"

# Ordered agent list — MUST match the numbered picker indices below.
ALL_AGENTS=(claude-code codex-cli cursor aider continue cline windsurf cody copilot-chat roo-code zed)

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
  echo "Usage: install.sh <skill-name> [--agent <agent>[,<agent>...]] [--scope user|project]" >&2
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

# ---- interactive checkbox picker ----
# Pure-bash TUI: arrow keys, SPACE to toggle, A to toggle all,
# ENTER to submit, ESC/Q to cancel. Zero external dependencies.
# Sets global AGENTS_LIST (space-separated agent names).
AGENTS_LIST=""

# Descriptions parallel to ALL_AGENTS
ALL_AGENT_DESCS=(
  "Anthropic Claude Code CLI"
  "OpenAI Codex CLI"
  "Cursor IDE"
  "Aider CLI"
  "Continue (VS Code / JetBrains)"
  "Cline (VS Code)"
  "Windsurf / Codeium IDE"
  "Sourcegraph Cody"
  "GitHub Copilot Chat (.github/copilot-instructions.md)"
  "Roo Code (VS Code)"
  "Zed AI"
)

# Renders the menu to /dev/tty, reads keypresses from /dev/tty, sets AGENTS_LIST.
checkbox_picker() {
  local n=${#ALL_AGENTS[@]}
  local selected=()
  local i cursor=0
  for ((i=0; i<n; i++)); do selected+=(0); done

  # Terminal state: hide cursor now; always restore on any exit
  printf '\e[?25h' >/dev/tty  # ensure known state
  printf '\e[?25l' >/dev/tty
  local cleanup='printf "\e[?25h\n" >/dev/tty'
  trap "$cleanup" EXIT INT TERM HUP

  # Draw column widths — pad agent name so descriptions align
  local maxname=0
  for name in "${ALL_AGENTS[@]}"; do
    [ ${#name} -gt "$maxname" ] && maxname=${#name}
  done

  local first=1
  while true; do
    if [ $first -eq 0 ]; then
      printf '\e[%dA' $((n + 3)) >/dev/tty
    fi
    first=0

    # Header
    printf '\e[2K\r  \e[1mSelect target agents for '\''%s'\''\e[0m\n' "$SKILL_NAME" >/dev/tty
    printf '\e[2K\r  \e[2m↑↓ move · SPACE toggle · A all · ENTER confirm · ESC cancel\e[0m\n' >/dev/tty
    printf '\e[2K\r\n' >/dev/tty

    # Items
    for ((i=0; i<n; i++)); do
      local mark=" "
      [ "${selected[i]}" = "1" ] && mark="x"
      local line
      printf -v line "[%s] %-*s  \e[2m%s\e[0m" "$mark" "$maxname" "${ALL_AGENTS[i]}" "${ALL_AGENT_DESCS[i]}"
      if [ "$i" = "$cursor" ]; then
        printf '\e[2K\r  \e[7m▶ %s\e[0m\n' "$line" >/dev/tty
      else
        printf '\e[2K\r    %s\n' "$line" >/dev/tty
      fi
    done

    # Read one keypress; handle escape sequences for arrow keys
    local key seq
    # -n1 (lowercase) for bash 3.2 compat (macOS default). ENTER returns "" (newline is default delimiter);
    # case pattern below handles that alongside '\n' and '\r'.
    IFS= read -rsn1 key </dev/tty || { eval "$cleanup"; return 1; }
    case "$key" in
      $'\e')
        # Arrow keys are ESC + [ + A/B/C/D — read 2 more chars with a tiny timeout
        seq=""
        # Arrow key: 2 more chars follow ESC almost instantly (already buffered).
        # Bash 3.2 rejects fractional -t; integer 1 is the smallest allowed.
        # Bare ESC (no follow-up) → 1s wait then empty seq → cancel below.
        # (Q also cancels instantly, so the 1s ESC delay only bites the rare ESC-alone user.)
        IFS= read -rsn2 -t 1 seq </dev/tty || true
        case "$seq" in
          '[A') cursor=$(( (cursor - 1 + n) % n )) ;;   # up
          '[B') cursor=$(( (cursor + 1) % n )) ;;       # down
          '')   eval "$cleanup"; echo "Cancelled." >&2; return 1 ;;
        esac
        ;;
      ' ')
        if [ "${selected[cursor]}" = "1" ]; then selected[cursor]=0; else selected[cursor]=1; fi
        ;;
      'a'|'A')
        # Toggle all: if any unselected → select all; else deselect all
        local any_unsel=0
        for ((i=0; i<n; i++)); do
          [ "${selected[i]}" = "0" ] && any_unsel=1
        done
        local newval=0
        [ $any_unsel -eq 1 ] && newval=1
        for ((i=0; i<n; i++)); do selected[i]=$newval; done
        ;;
      $'\n'|$'\r'|'')
        eval "$cleanup"
        local result=""
        for ((i=0; i<n; i++)); do
          [ "${selected[i]}" = "1" ] && result="$result ${ALL_AGENTS[i]}"
        done
        if [ -z "$result" ]; then
          echo "Nothing selected. Press SPACE to toggle items before ENTER." >&2
          return 1
        fi
        AGENTS_LIST="${result# }"
        return 0
        ;;
      'q'|'Q')
        eval "$cleanup"
        echo "Cancelled." >&2
        return 1
        ;;
    esac
  done
}

pick_agents_interactive() {
  if [ ! -e /dev/tty ] || [ ! -r /dev/tty ]; then
    echo "install.sh needs an interactive terminal. Non-interactive?" >&2
    echo "Use --agent <name>[,<name>...] or --agent all" >&2
    exit 2
  fi
  checkbox_picker || exit 1
}

# ---- resolve the agent list from CLI flag or interactive picker ----
if [ -z "$AGENT" ]; then
  pick_agents_interactive
elif [ "$AGENT" = "all" ]; then
  AGENTS_LIST="${ALL_AGENTS[*]}"
else
  # Accept comma-separated for --agent
  AGENTS_LIST=$(echo "$AGENT" | tr ',' ' ')
fi

# ---- install path per agent ----
install_for() {
  local agent="$1"
  local dest_dir=""
  case "$agent" in
    claude-code)
      if [ "$SCOPE" = "project" ]; then dest_dir=".claude/skills/$SKILL_NAME"; else dest_dir="$HOME/.claude/skills/$SKILL_NAME"; fi
      fetch "SKILL.md" "$dest_dir/SKILL.md" || { echo "FAIL: could not fetch SKILL.md" >&2; return 1; }
      fetch "references/index.md" "$dest_dir/references/index.md" 2>/dev/null || true
      ;;
    codex-cli)
      if [ "$SCOPE" = "project" ]; then dest_dir=".codex/prompts"; else dest_dir="$HOME/.codex/prompts"; fi
      fetch "SKILL.md" "$dest_dir/${SKILL_NAME}.md" || return 1
      ;;
    cursor)
      dest_dir=".cursor/rules"
      mkdir -p "$dest_dir"
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
      # If a prior block for this skill exists, remove it so we replace (not skip).
      # -i.bak works on both BSD sed (macOS) and GNU sed (Linux); then clean the backup.
      if grep -q "<!-- skill:$SKILL_NAME -->" "$dest_dir/copilot-instructions.md"; then
        sed -i.bak "/<!-- skill:$SKILL_NAME -->/,/<!-- \/skill:$SKILL_NAME -->/d" \
          "$dest_dir/copilot-instructions.md"
        rm -f "$dest_dir/copilot-instructions.md.bak"
      fi
      {
        echo "<!-- skill:$SKILL_NAME -->"
        awk 'BEGIN{fm=0} /^---$/{fm++; next} fm>=2{print}' "$tmp"
        echo "<!-- /skill:$SKILL_NAME -->"
      } >> "$dest_dir/copilot-instructions.md"
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

# ---- iterate the selected agents ----
if [ -z "${AGENTS_LIST// /}" ]; then
  echo "No agents selected." >&2
  exit 1
fi
for a in $AGENTS_LIST; do
  install_for "$a" || true
done
