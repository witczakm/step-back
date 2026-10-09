#!/usr/bin/env bash
# Install the step-back skill (English) or krok-wstecz (Polish) into Claude Code and/or Codex.
# No network calls, no telemetry. An existing install is moved to a timestamped backup, never overwritten.
#
#   ./install.sh                 # English edition into Claude Code and Codex
#   ./install.sh --lang pl       # Polish edition (krok-wstecz)
#   ./install.sh --claude-only   # only ~/.claude/skills
#   ./install.sh --codex-only    # only ~/.codex/skills
#   ./install.sh --dry-run       # show what would happen, write nothing
set -euo pipefail

LANG_ED="en"; TARGETS="claude codex"; DRY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --lang) LANG_ED="${2:-}"; shift 2 ;;
    --claude-only) TARGETS="claude"; shift ;;
    --codex-only) TARGETS="codex"; shift ;;
    --dry-run) DRY=1; shift ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
done
case "$LANG_ED" in
  en) ID="step-back" ;;
  pl) ID="krok-wstecz" ;;
  *) echo "--lang must be en or pl" >&2; exit 2 ;;
esac

REPO="$(cd "$(dirname "$0")" && pwd)"
SRC="$REPO/plugins/$ID/skills/$ID"
[ -f "$SRC/SKILL.md" ] || { echo "Source not found: $SRC" >&2; exit 1; }
command -v python3 >/dev/null || echo "Warning: python3 not found — the skill needs it to count signals." >&2

run() { if [ "$DRY" = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }
STAMP="$(date +%Y%m%d-%H%M%S)"

for t in $TARGETS; do
  if [ "$t" = claude ]; then BASE="${CLAUDE_HOME:-$HOME/.claude}"; else BASE="${CODEX_HOME:-$HOME/.codex}"; fi
  DEST="$BASE/skills/$ID"
  run mkdir -p "$BASE/skills"
  if [ -e "$DEST" ] || [ -L "$DEST" ]; then
    run mkdir -p "$BASE/skills-backups"
    run mv "$DEST" "$BASE/skills-backups/$ID-$STAMP"
    echo "Backed up existing $DEST -> $BASE/skills-backups/$ID-$STAMP"
  fi
  run cp -R "$SRC" "$DEST"
  echo "Installed $ID -> $DEST"
done
echo
echo "Done. In Claude Code run /$ID in any project (first time: it reports NO LOG — see assets/ of the skill)."
echo "Optional: add the lines from $SRC/snippets/ to your CLAUDE.md / AGENTS.md."
