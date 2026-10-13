#!/usr/bin/env python3
"""Footage bed for the Luma Pillar method reel (E2): the owner's styling clip cut to the voice-over.

The cuts follow the ElevenLabs take (Koyal, src/luma-vo-koyal-elevenlabs.mp3) at its word timings
(src/luma-vo-words.json, from a local faster-whisper pass, phrase starts snapped to the voice's own pauses).
Lit shots are straightened and every shot gets the MOTION.md photo grade. The bed is silent: the voice and the
music are separate tracks in index.html.
    python3 hyperframes/projects/luma-method/prep.py
"""
import os, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "luma-styled"))
from luma_shots import FF, FPS, H, W, shot                               # noqa: E402

# (output start s, shot): each runs to the next start; the bed ends where the end card takes over
CUTS = [(0.00, "books"),         # "Books."
        (0.98, "candle"),        # "Candle."
        (1.97, "mat"),           # "Cute mat."
        (3.30, "match"),         # "And it still looks…"
        (5.02, "placed"),        # "off?" (the lamp set down, unlit)
        (6.03, "macro-off"),     # "That's because it's missing…"
        (7.40, "macro-on"),      # "…light at eye level." (switched on at "light")
        (8.95, "wide-on"),       # "Meet the Luma Pillar."
        (11.15, "smoke-a"),      # "Solid wood, a soft, warm glow,"
        (13.75, "macro-grain"),  # "and grain no one else will have."
        (16.15, "smoke-b"),      # "Just ₹1,599."
        (18.00, "wide-on-2")]    # "on nixwoods.com"
END = 19.75


def main():
    out = os.path.join(HERE, "assets", "bed.mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "slow", "-pix_fmt",
                          "yuv420p", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    ends = [c[0] for c in CUTS[1:]] + [END]
    for (t0, name), t1 in zip(CUTS, ends):
        n = round(t1 * FPS) - round(t0 * FPS)
        for f in shot(name, n / FPS):
            x = f.astype(np.float32) / 255
            x = np.clip(np.clip(x * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** 1.04, 0, 1)   # MOTION.md 6
            p.stdin.write((x * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    assert p.wait() == 0
    print("wrote", out)


if __name__ == "__main__":
    main()
