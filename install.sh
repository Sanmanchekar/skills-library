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
# Prefer a real TUI widget. Fall back to a numbered multi-select.
# Sets global AGENTS_LIST (space-separated agent names).
AGENTS_LIST=""

pick_agents_interactive() {
  # whiptail: broadly available on Linux, honors /dev/tty
  if command -v whiptail >/dev/null 2>&1; then
    local sel
    sel=$(whiptail --title "skills-library — install $SKILL_NAME" \
      --checklist "SPACE to toggle · ENTER to confirm · ESC to cancel" \
      22 74 13 \
      claude-code   "Anthropic Claude Code CLI"           OFF \
      codex-cli     "OpenAI Codex CLI"                    OFF \
      cursor        "Cursor IDE"                          OFF \
      aider         "Aider CLI"                           OFF \
      continue      "Continue (VS Code / JetBrains)"      OFF \
      cline         "Cline (VS Code)"                     OFF \
      windsurf      "Windsurf / Codeium IDE"              OFF \
      cody          "Sourcegraph Cody"                    OFF \
      copilot-chat  "GitHub Copilot Chat (.github/...)"   OFF \
      roo-code      "Roo Code (VS Code)"                  OFF \
      zed           "Zed AI"                              OFF \
      3>&1 1>&2 2>&3 </dev/tty) || { echo "Cancelled." >&2; exit 1; }
    # whiptail returns space-separated, quoted tags: "cursor" "aider"
    AGENTS_LIST=$(echo "$sel" | tr -d '"')
    return 0
  fi

  # gum: charmbracelet — clean UX if the user has it installed
  if command -v gum >/dev/null 2>&1; then
    AGENTS_LIST=$(printf '%s\n' "${ALL_AGENTS[@]}" \
      | gum choose --no-limit --header "Select target agents (x to toggle, enter to confirm)" \
      < /dev/tty | tr '\n' ' ')
    [ -z "$AGENTS_LIST" ] && { echo "Nothing selected." >&2; exit 1; }
    return 0
  fi

  # dialog: same widget family as whiptail
  if command -v dialog >/dev/null 2>&1; then
    local sel
    sel=$(dialog --stdout --separate-output --checklist "Select target agents" \
      22 74 13 \
      claude-code   "Anthropic Claude Code CLI"           off \
      codex-cli     "OpenAI Codex CLI"                    off \
      cursor        "Cursor IDE"                          off \
      aider         "Aider CLI"                           off \
      continue      "Continue (VS Code / JetBrains)"      off \
      cline         "Cline (VS Code)"                     off \
      windsurf      "Windsurf / Codeium IDE"              off \
      cody          "Sourcegraph Cody"                    off \
      copilot-chat  "GitHub Copilot Chat"                 off \
      roo-code      "Roo Code (VS Code)"                  off \
      zed           "Zed AI"                              off \
      </dev/tty) || { echo "Cancelled." >&2; exit 1; }
    AGENTS_LIST=$(echo "$sel" | tr '\n' ' ')
    return 0
  fi

  # Fallback: numbered checklist, user types space-separated numbers
  cat <<'MENU' >&2

┌─────────────────────────────────────────────────────────────┐
│  Select target agents (checkbox-style, multi-select)        │
│  Enter the numbers you want, separated by spaces.           │
│  Example: 1 3 9    → claude-code, cursor, copilot-chat     │
│  Enter "all"        → install for every agent               │
│  Enter "*" or ENTER on empty line → cancel                  │
└─────────────────────────────────────────────────────────────┘

  [ ] 1)  claude-code    (Anthropic Claude Code CLI)
  [ ] 2)  codex-cli      (OpenAI Codex CLI)
  [ ] 3)  cursor         (Cursor IDE)
  [ ] 4)  aider          (Aider CLI)
  [ ] 5)  continue       (Continue for VS Code / JetBrains)
  [ ] 6)  cline          (Cline for VS Code)
  [ ] 7)  windsurf       (Windsurf / Codeium IDE)
  [ ] 8)  cody           (Sourcegraph Cody)
  [ ] 9)  copilot-chat   (GitHub Copilot Chat — .github/copilot-instructions.md)
  [ ] 10) roo-code       (Roo Code for VS Code)
  [ ] 11) zed            (Zed AI)

MENU
  printf "Your selection: " >&2
  local input
  read -r input </dev/tty || { echo "Cancelled." >&2; exit 1; }
  input="${input:-}"
  if [ -z "$input" ] || [ "$input" = "*" ]; then
    echo "Cancelled." >&2; exit 1
  fi
  if [ "$input" = "all" ]; then
    AGENTS_LIST="${ALL_AGENTS[*]}"
    return 0
  fi
  # Map numbers → agent names
  local picked=""
  for n in $input; do
    if ! [[ "$n" =~ ^[0-9]+$ ]] || [ "$n" -lt 1 ] || [ "$n" -gt "${#ALL_AGENTS[@]}" ]; then
      echo "Invalid selection: '$n' (must be 1..${#ALL_AGENTS[@]}, 'all', or empty)" >&2
      exit 2
    fi
    picked="$picked ${ALL_AGENTS[$((n - 1))]}"
  done
  AGENTS_LIST="${picked# }"
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
