#!/bin/bash
# Stop hook (D-086): a render committed under nixwoods-reel/ is not finished until the NixWoods OS knows about it.
# Runs creative_index.py --check --renders against ../nixwoods-os (or $NIXWOODS_OS). On a gap or a filing problem
# it exits 2, which hands the list back to Claude so the asset is filed (nixwoods-reel/CLAUDE.md, OS contract 1-7)
# or excused in 30-Creative/creative-not-registered.tsv before the turn ends. It blocks at most once per stop:
# when Claude is already continuing because of this hook (stop_hook_active), it only warns.
# Writes nothing. Silent when everything is filed, and when nixwoods-os is not beside this repo (the Mac).
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
NW_OS="${NIXWOODS_OS:-$(dirname "$PROJECT_DIR")/nixwoods-os}"
INPUT=$(cat)
[ -f "$NW_OS/40-Content/scripts/creative_index.py" ] || exit 0
OUT=$(python3 "$NW_OS/40-Content/scripts/creative_index.py" --check --renders "$PROJECT_DIR" 2>&1)
[ $? -eq 0 ] && exit 0
MSG="NixWoods OS audit failed (D-086). File these before finishing (nixwoods-reel/CLAUDE.md, OS contract 1-7), or list a render in 30-Creative/creative-not-registered.tsv with the reason:
$(printf '%s\n' "$OUT" | grep -E 'GAP|PROBLEM')"
if printf '%s' "$INPUT" | grep -q '"stop_hook_active" *: *true'; then
  echo "$MSG" >&2
  exit 0
fi
echo "$MSG" >&2
exit 2
