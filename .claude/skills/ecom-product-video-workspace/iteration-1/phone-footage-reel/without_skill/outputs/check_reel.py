#!/usr/bin/env python3
"""Measure a finished 9:16 reel: container, frame stats, loudness, safe-zone pixels.

There is no ffprobe binary in this container, so everything here is done with the
ffmpeg that ships inside imageio_ffmpeg: the container line is parsed out of
ffmpeg's stderr, and the picture is measured by decoding greyscale rawvideo into
numpy.

    python3 check_reel.py reel.mp4
"""
import re, subprocess, sys
import numpy as np
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 1080, 1920
SAFE = dict(top=230, bottom=1500, left=70, right=950)   # presets.json -> safe


def container(path):
    err = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    out = {}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", err)
    if m:
        h, mi, s = m.groups()
        out["duration_s"] = round(int(h) * 3600 + int(mi) * 60 + float(s), 2)
    m = re.search(r"Video: (\w+).*?, (\d+)x(\d+).*?, ([\d.]+) fps", err, re.S)
    if m:
        out["codec"], out["w"], out["h"], out["fps"] = m.group(1), int(m.group(2)), int(m.group(3)), float(m.group(4))
    m = re.search(r"Audio: (\w+).*?, (\d+) Hz, (\w+)", err)
    if m:
        out["audio"] = f"{m.group(1)} {m.group(2)}Hz {m.group(3)}"
    return out


def gray(path, fps=5, w=135, h=240):
    p = subprocess.run([FF, "-v", "error", "-i", path, "-vf",
                        f"fps={fps},scale={w}:{h},format=gray", "-f", "rawvideo",
                        "-pix_fmt", "gray", "-"], capture_output=True)
    a = np.frombuffer(p.stdout, dtype=np.uint8)
    return a[: (len(a) // (w * h)) * w * h].reshape(-1, h, w)


def loudness(path):
    p = subprocess.run([FF, "-v", "info", "-i", path, "-af",
                        "loudnorm=print_format=summary", "-f", "null", "-"],
                       capture_output=True, text=True)
    return {k: v.strip() for k, v in re.findall(r"(Input \w+(?: \w+)*):\s+([-\d.]+ *\w*)", p.stderr)}


def main(path):
    c = container(path)
    print("container:", c)
    ok = c.get("w") == W and c.get("h") == H
    print(f"9:16 1080x1920        : {'OK' if ok else 'FAIL'}")
    d = c.get("duration_s", 0)
    print(f"length {d}s           : {'OK (<=30s, feed-native)' if d <= 30 else 'LONG'}")

    g = gray(path)
    per = g.reshape(len(g), -1)
    print(f"frames sampled        : {len(g)}")
    print(f"grey mean / p50       : {per.mean():.1f} / {np.percentile(per, 50):.0f}"
          f"   (dark grade target: mean < 80)")
    print(f"p1 / p99              : {np.percentile(per, 1):.0f} / {np.percentile(per, 99):.0f}")
    print(f"clipped >=254         : {100 * (per >= 254).mean():.2f}%  (blown highlights)")
    print(f"crushed <=1           : {100 * (per <= 1).mean():.2f}%  (dead black)")
    # per-frame: does any frame go fully black (a hole in the cut)?
    fm = per.mean(axis=1)
    black = np.where(fm < 3)[0]
    print(f"near-black frames     : {len(black)}"
          + (f"  at t={[round(i / 5, 1) for i in black]}" if len(black) else ""))
    # motion: frame-to-frame difference, to confirm nothing is frozen
    dif = np.abs(np.diff(per.astype(np.int16), axis=0)).mean(axis=1)
    print(f"frame-to-frame delta  : min {dif.min():.1f}  mean {dif.mean():.1f}  "
          f"(min 0 would mean a frozen frame)")
    print("loudness:", loudness(path))
    # safe zone as a fraction of the canvas, for reference when checking type placement
    print(f"safe zone             : x {SAFE['left']}-{SAFE['right']}, y {SAFE['top']}-{SAFE['bottom']} of {W}x{H}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "reel.mp4")
