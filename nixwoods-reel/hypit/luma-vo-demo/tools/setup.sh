#!/usr/bin/env bash
# Rebuild this Hypit project's working state in a fresh cloud session (global npm, ~/.cache and .hypit/ don't persist).
# 1) Hypit itself  2) the media it reads, copied from the repo  3) the local Profile (no hosted services, no keys)
#    4) the Runtime. Then: hypit build productions/luma-vo/runs/v1.svrun --follow  (see NOTES.md)
set -e
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"                     # nixwoods-reel/
bash "$REPO/../.claude/skills/hypit/setup.sh"
mkdir -p "$HERE/assets/audio" "$HERE/assets/footage" "$HERE/assets/fonts" "$HERE/assets/stills"
cp "$REPO/brand-reels/luma-styled/src/luma-vo-koyal-elevenlabs.mp3" "$REPO/brand-reels/luma-styled/src/luma-vo-words.json" "$HERE/assets/audio/"
cp "$REPO/brand-reels/luma-styled/src/luma-styling-20260331.mov" "$REPO/floor-reels/src/nx00-hero.mp4" "$REPO/floor-reels/src/nx04-7930.mp4" "$HERE/assets/footage/"
cp "$REPO/assets/Inter-600.ttf" "$REPO/assets/Inter-400.ttf" "$REPO/assets/Fraunces-600.ttf" "$HERE/assets/fonts/"
cp "$REPO/assets/logo.png" "$HERE/assets/"
python3 "$HERE/tools/make_stills.py" "$HERE/assets"
sed "s|__PROJECT__|$HERE|g" "$HERE/hypit.runtime.template.json" > "$HERE/hypit.runtime.json"
cd "$HERE" && hypit runtime up
echo READY
