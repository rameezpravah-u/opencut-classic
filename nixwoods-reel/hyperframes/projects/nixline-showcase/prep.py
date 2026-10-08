#!/usr/bin/env python3
"""Assets for the NixLine showcase reel: the real 5 Aug shoot frame (AC4I9815), cropped so the lit
channel sits on x = 540, graded with MOTION.md's photo grade, at 1.2x so the 5% push never upscales.
Prints the channel's measured on-screen position so the drawn line can land exactly on it.
    python3 hyperframes/projects/nixline-showcase/prep.py
"""
import os, sys
import numpy as np
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import axis                      # the same channel detector V2 uses
SRC = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                   "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
K = 1.2                                             # export scale over 1080x1920
BOX = (2100, 2349, 3648, 2349 + 1548 * 16 / 9)      # channel (x 2875, y 2934-4631) lands at x 540, centre y ~1000

im = ImageOps.exif_transpose(Image.open(SRC)).convert("RGB")
out = im.resize((round(1080 * K), round(1920 * K)), Image.LANCZOS, box=BOX)
a = np.asarray(out).astype(np.float32) / 255
a = np.clip(a * np.array([1.06, 1.0, 0.88]), 0, 1) ** 1.04          # MOTION.md 6: photo grade
out = Image.fromarray((a * 255).astype(np.uint8))
out.save(os.path.join(HERE, "assets", "nixline-corner.jpg"), quality=92)
(cx, cy), ang, L = axis(out)
print(f"channel on screen: x {cx / K:.1f}, centre y {cy / K:.1f}, length {L / K:.1f}, "
      f"top {cy / K - L / K / 2:.1f}, bottom {cy / K + L / K / 2:.1f}, angle {ang:.2f} deg")
