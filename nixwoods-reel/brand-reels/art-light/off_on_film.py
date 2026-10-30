#!/usr/bin/env python3
"""Circular Hole Wall Light: an off / on product film on Studio96's BiFROST pattern
(instagram.com/reel/DfCN36XNLWO, @studio96.fe, 28 Oct 2026, 35k views; owner 30 Oct: "Do this").

The reference, every frame seen (15.9 s, a licensed song with vocals that we never use, no on-screen text):
  0.00-3.47  the lamp off on a dark sideboard, art behind, a slow camera drift
  3.47-6.60  off, a close detail of the materials (steel edge, fluted glass)
  6.60-7.37  off, a slightly wider frame
  7.37       a hard cut to the lamp on, in nearly the same frame
  7.37-13.80 on: a close beat, then a long slow hold wider
  13.80-14.4 on, close
  14.37-15.9 off again, then fade to black
The whole idea is the switch: a beautiful object, then the same object lit.

Ours, on the owner's 29 Oct clips (sharpest windows, system/clip_triage.py), cut on music1's grid (0.8823 s, ours):
  off hero (8123, 4K 60p slowed) -> off detail, the holes in the grain (8122) -> off, the bar above the painting
  (8123's end) -> the switch on the beat: the lit bar in the same frame (8121, framed so the bar sits at y ~700 in
  both), the LEDs warming up over 0.3 s -> lit macro (8118) -> the long lit hold over the painting (8115's settled
  last frame, a slow push) -> lit close (8117) -> off again (8123's end), fade to black with the name and
  nixwoods.com. No other text, as in the reference. Real footage only.

    python3 brand-reels/art-light/off_on_film.py [--frames 1,7.2]
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from art_light import FF, W, FPS, CREAM, MUTED_D, OUT, font, sstep, text, alpha, layer, grain  # noqa: E402
from art_light_v2 import S, footage, switch_on  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
H, SR = 1920, 48000
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music1-aesthetic.mp3")
BEAT = 0.8823                                              # music1: 68 bpm, first beat at 0
B = lambda k: round(k * BEAT, 3)
NAME = "NW-CREATIVE-VID-20261030-24-inch-circular-hole-wooden-wall-light-off-on-film-v1"

OFF_HERO = S("IMG_8123.mov", 0.00, 0.35, zoom=1.2, zy=0.85, night=False, fps=60)  # 1.24 s of 4K 60p over 3.5 s
OFF_HOLES = S("IMG_8122.mov", 0.90, 0.45, zoom=1.35, zy=0.62, night=False)    # the holes in the grain
OFF_WIDE = S("IMG_8123.mov", 2.55, 0.85, zoom=1.25, zy=0.99, night=False, fps=60)  # the bar above the painting
ON_WIDE = S("IMG_8121.mov", 3.45, 0.80, zoom=1.12, zy=0.03)                   # the same frame, lit
ON_MACRO = S("IMG_8118.mov", 1.00, 0.80, zoom=1.25, zy=1.0)                   # lit holes under the grain
ON_HOLD = S("IMG_8115.mov", 2.90, 0.0, zoom=1.0)                              # the settled frame, held, pushed in
ON_CLOSE = S("IMG_8117.mov", 1.70, 0.90, zoom=1.12, zy=0.75)                  # lit holes along the bar's end
OFF_END = S("IMG_8123.mov", 3.30, 0.0, zoom=1.25, zy=0.99, night=False, fps=60)  # off again, held

# (shot, start, end, push): the switch is on beat 8 (7.06 s); the long lit hold is the reference's 5 s beat
CUTS = [(OFF_HERO, B(0), B(4), 0.06), (OFF_HOLES, B(4), B(7), 0.04), (OFF_WIDE, B(7), B(8), 0.0),
        (ON_WIDE, B(8), B(10), 0.0), (ON_MACRO, B(10), B(13), 0.04), (ON_HOLD, B(13), B(15.5), 0.07),
        (ON_CLOSE, B(15.5), B(16.5), 0.03), (OFF_END, B(16.5), B(18), 0.03)]
DUR = B(18)                                                # 15.88 s, the reference's length
SWITCH = B(8)


def frame(t):
    for sh, a, b, push in CUTS:
        if a <= t < b or sh is OFF_END:
            break
    lt, secs = t - a, b - a
    im = footage(sh, lt, secs, H, push=push)
    if sh is ON_WIDE:
        im = switch_on(im, lt)
    if sh is OFF_END:                                      # fade to black over the last 0.9 s, the name over it
        k = sstep((t - (DUR - 0.9)) / 0.9)
        im = Image.fromarray((np.asarray(im, np.float32) * (1 - 0.94 * k)).astype(np.uint8))
        a1 = sstep((t - (DUR - 1.05)) / 0.35)

        def dr(d):
            text(d, (W / 2, 900), "Circular Hole Wall Light", font("Fraunces-600.ttf", 64), alpha(CREAM, a1))
            text(d, (W / 2, 990), "nixwoods.com", font("Inter-600.ttf", 36), alpha(MUTED_D, a1))
        im = layer(im, dr)
    return im


def music(path):
    raw = subprocess.run([FF, "-v", "error", "-i", MUSIC, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f",
                          "f32le", "-"], capture_output=True, check=True).stdout
    n = int(DUR * SR)
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    t = np.arange(n) / SR
    m = m / (np.sqrt(np.mean(m ** 2)) + 1e-9) * 10 ** (-18 / 20)
    m *= (np.clip(t / 0.4, 0, 1) * np.clip((DUR - t) / 0.9, 0, 1))[:, None]          # MOTION: fade the last 0.9 s
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.frames:
        for s in a.frames.split(","):
            frame(float(s)).save(os.path.join(a.out, f"film-{float(s):05.2f}.jpg"), quality=90)
        return
    path = os.path.join(a.out, NAME + ".mp4")
    wav = path + ".wav"
    music(wav)
    rng = np.random.default_rng(30)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-shortest",
                          "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        p.stdin.write(grain(frame(i / FPS), rng).tobytes())
    p.stdin.close()
    assert p.wait() == 0, path
    os.remove(wav)
    print("wrote", path, "dur", DUR)


if __name__ == "__main__":
    main()
