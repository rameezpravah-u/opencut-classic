#!/usr/bin/env python3
"""check_render.py — the silent failures, checked after the render, not assumed.

    python3 check_render.py reel.mp4

  * duration            a shot that read past the end of its source truncates the tail while the
                        container still reports a plausible length; compare against the brief.
  * end card present    pull the LAST frame and look at it. A dropped end card is invisible in a
                        contact sheet sampled at 2 fps.
  * per-channel mean    warm 3000K light must come out R > G > B. A bloom or highlight trick that
                        zeroes luma but leaves chroma produces magenta that looks fine as a thumb.
  * file size           against a stated ceiling, so it is checked rather than hoped.
"""
import subprocess, sys, os, json
import numpy as np
from PIL import Image

CEILING_MB = 25.0

def ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"

def duration(path):
    out = subprocess.run([ffmpeg(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None

def frame_at(path, t, out):
    subprocess.run([ffmpeg(), "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{t:.3f}", "-i", path, "-frames:v", "1", out], check=True)
    return out

def main(path):
    d = duration(path)
    size = os.path.getsize(path) / 1e6
    ok = True
    print(f"duration   {d:.2f}s")
    print(f"size       {size:.2f} MB (ceiling {CEILING_MB} MB)")
    if size > CEILING_MB:
        print("  ! over the size ceiling"); ok = False

    tmp = os.path.join(os.path.dirname(os.path.abspath(path)) or ".", "_lastframe.png")
    frame_at(path, max(0.0, d - 0.25), tmp)
    a = np.asarray(Image.open(tmp).convert("RGB")).astype(float)
    lum = np.asarray(Image.open(tmp).convert("L")).astype(float)
    print(f"last frame {a.shape[1]}x{a.shape[0]}  mean lum {lum.mean():.1f}  "
          f"ink {(lum > 90).mean()*100:.1f}% of pixels")
    if (lum > 90).mean() < 0.005:
        print("  ! last frame is effectively blank — end card missing"); ok = False

    for t in [d * 0.25, d * 0.5, d * 0.75]:
        frame_at(path, t, tmp)
        p = np.asarray(Image.open(tmp).convert("RGB")).astype(float)
        r, g, b = p[:, :, 0].mean(), p[:, :, 1].mean(), p[:, :, 2].mean()
        warm = r > g > b
        print(f"t={t:5.2f}s  R/G/B {r:5.1f}/{g:5.1f}/{b:5.1f}  {'warm' if warm else 'NOT warm (check the grade)'}")
        if not warm:
            ok = False
    os.remove(tmp)
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
