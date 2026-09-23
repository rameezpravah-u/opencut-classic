#!/usr/bin/env bash
# build.sh — render reel.mp4 for the Double Arm Teak Pendant (9:16).
#
#   bash build.sh
#
# Three steps: measure the source photography, render the cut, then check the render for the
# failures that are silent (missing end card, wrong duration, a grade that has gone cold).
# The shot list lives in render_reel.py; teak-four-foot.json is the same cut expressed as a
# brief for the repo's own make_reel.py, kept for whoever prefers that route.
#
# Requires: pillow numpy imageio-ffmpeg (ffmpeg 7 ships with imageio-ffmpeg).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REEL="$(cd "$HERE/../../../../../../../nixwoods-reel" && pwd)"
# Framing/grade decisions are argued from these numbers — re-run when the PDP photography changes.
python3 "$HERE/measure_sources.py" "$REEL/teak-reels/hf"

python3 "$HERE/render_reel.py" --out "$HERE/reel.mp4"

# Guards (skill §10/§12): end card present, duration, size.
python3 "$HERE/check_render.py" "$HERE/reel.mp4"
