#!/usr/bin/env bash
# verify.sh — the post-render checks for reel.mp4. Run from anywhere.
# Catches the silent failures: a truncated tail, a missing end card, a colour-cast grade,
# a file over the storage ceiling, audio that is not at platform loudness.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
M="$DIR/reel.mp4"
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")

echo "== container =="
"$FF" -hide_banner -i "$M" 2>&1 | grep -E "Duration|Stream #"

echo "== full decode (frame count must equal duration x 25) =="
"$FF" -hide_banner -i "$M" -f null - 2>&1 | tr '\r' '\n' | grep -E "^frame=" | tail -1

echo "== end card present (last frame) =="
"$FF" -hide_banner -loglevel error -sseof -0.3 -i "$M" -frames:v 1 -q:v 3 -y "$DIR/build/_lastframe.jpg" && echo "wrote build/_lastframe.jpg — open it, it must be the NixWoods end card"

echo "== grade: warm means R > G > B, and no crushed midtones =="
for t in 0.6 3.9 6.5 10.0; do
  "$FF" -hide_banner -loglevel error -ss $t -i "$M" -frames:v 1 -y "$DIR/build/_g$t.png"
done
python3 - "$DIR" <<'PY'
import sys, numpy as np
from PIL import Image
d = sys.argv[1]
for t in ("0.6","3.9","6.5","10.0"):
    im = Image.open(f"{d}/build/_g{t}.png")
    a = np.asarray(im.convert("RGB"), float); l = np.asarray(im.convert("L"), float)
    warm = "warm" if a[...,0].mean() > a[...,1].mean() > a[...,2].mean() else "NOT WARM — check for a magenta/cool cast"
    print(f"  t={t:>5}s  R{a[...,0].mean():5.1f} G{a[...,1].mean():5.1f} B{a[...,2].mean():5.1f}  "
          f"lum mean {l.mean():5.1f} p5 {np.percentile(l,5):5.1f} p95 {np.percentile(l,95):5.1f}  {warm}")
PY

echo "== audio loudness (target about -14 LUFS, true peak below -1 dBFS) =="
"$FF" -hide_banner -nostats -i "$M" -af ebur128=peak=true -f null - 2>&1 | grep -A2 -E "Integrated loudness|True peak" | grep -E "I:|Peak:"

echo "== size (repo rule: re-encode at CRF 23 above ~21 MB) =="
du -h "$M"

echo "== contact sheet =="
"$FF" -hide_banner -loglevel error -i "$M" -vf "fps=1.2,scale=216:384,tile=5x3" -frames:v 1 -q:v 3 -y "$DIR/reel-contact-sheet.jpg" && echo "wrote reel-contact-sheet.jpg"
rm -f "$DIR"/build/_g*.png
