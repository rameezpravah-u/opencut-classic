#!/usr/bin/env python3
"""verify_reel.py — the pre-ship checks for reel.mp4, all measured rather than eyeballed.

1. container duration vs decoded frame count (a container can report full length after
   ffmpeg silently ran out of source frames — the fault that eats end cards)
2. the end card is actually the last frame (not black, carries the logo plate's ink)
3. a 4x4 contact sheet for framing / text placement
4. per-channel means on the lit beats: warm light must read R > G > B, not magenta
5. file size against the 50 MB social ceiling
"""
import os
import subprocess
import sys

import numpy as np
import imageio_ffmpeg
from PIL import Image

FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
MP4 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "reel.mp4")


def probe(path):
    r = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True)
    return r.stderr


def frames_gray(path, w=32, h=57):
    r = subprocess.run([FF, "-v", "quiet", "-i", path, "-map", "0:v:0", "-vf", f"scale={w}:{h}",
                        "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w)


def frame_at(path, t, out):
    subprocess.run([FF, "-y", "-v", "error", "-ss", f"{t}", "-i", path, "-frames:v", "1", out],
                   check=True)
    return np.asarray(Image.open(out).convert("RGB"), dtype=np.float32)


print(f"== {MP4}  {os.path.getsize(MP4)/1e6:.1f} MB")
info = probe(MP4)
for line in info.splitlines():
    if "Duration" in line or "Stream #" in line:
        print("  ", line.strip())

g = frames_gray(MP4)
n = len(g)
print(f"   decoded frames: {n}  -> {n/25:.2f} s at 25 fps")

# --- shot boundaries, the same frame-difference pass used to read the reference
d = np.abs(np.diff(g.astype(np.float32), axis=0)).mean(axis=(1, 2))
thr = d.mean() + 2.2 * d.std()
cuts = [round(i / 25, 2) for i, v in enumerate(d) if v > thr]
print(f"   frame-diff cuts (>{thr:.1f}): {cuts}")

# --- last frame / end card
scratch = os.path.join(HERE, "_check")
os.makedirs(scratch, exist_ok=True)
last = frame_at(MP4, max(0, n / 25 - 0.12), os.path.join(scratch, "last.png"))
print(f"   last frame: mean lum {last.mean():.1f}, ink pixels (>200) "
      f"{(last.max(axis=2) > 200).mean()*100:.2f}%  -> end card present: "
      f"{last.mean() > 3 and (last.max(axis=2) > 200).mean() > 0.001}")

# --- warm-light sanity on the lit beats
for t in (6.5, 12.0, 17.0, 23.0):
    if t < n / 25:
        f = frame_at(MP4, t, os.path.join(scratch, f"t{t}.png"))
        r, gg, b = f[..., 0].mean(), f[..., 1].mean(), f[..., 2].mean()
        print(f"   t={t:>5}s  R{r:6.1f} G{gg:6.1f} B{b:6.1f}   warm(R>G>B): {r > gg > b}")

# --- contact sheet
sheet = os.path.join(HERE, "contact-sheet.jpg")
subprocess.run([FF, "-y", "-v", "error", "-i", MP4,
                "-vf", f"select='not(mod(n\\,{max(1, n//16)}))',scale=270:480,tile=4x4",
                "-frames:v", "1", "-q:v", "3", sheet], check=True)
print(f"   contact sheet -> {sheet}")

# --- audio: does it actually run to the end, or does the bed stop early?
raw = subprocess.run([FF, "-v", "quiet", "-i", MP4, "-map", "0:a:0", "-ac", "1", "-ar", "8000",
                      "-f", "s16le", "-"], capture_output=True).stdout
a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0
print(f"   audio: {len(a)/8000:.2f} s decoded vs {n/25:.2f} s of video")
step = 8000  # 1 s buckets
rms = [float(np.sqrt((a[i:i+step] ** 2).mean() + 1e-12)) for i in range(0, len(a) - step, step)]
print("   audio RMS per second: " + " ".join(f"{v:.3f}" for v in rms))
tail = rms[-4:] if len(rms) >= 4 else rms
print(f"   last 4 s audible (RMS > 0.005): {all(v > 0.005 for v in tail)}")

# --- banding in the dark gradients, where re-encoding shows first
dark = frame_at(MP4, 16.0, os.path.join(scratch, "dark.png"))
col = dark[:, dark.shape[1] // 2, :].mean(axis=1)
steps = np.unique(np.round(col)).size
print(f"   dark-frame centre column: {steps} distinct levels over {len(col)} px "
      f"(low numbers = banding)")

size_mb = os.path.getsize(MP4) / 1e6
print(f"   size {size_mb:.1f} MB  under 50 MB ceiling: {size_mb < 50}")
