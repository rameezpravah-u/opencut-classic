#!/usr/bin/env python3
"""Code-made stills (no generation models): text scrims, the Dusk end-card ground and a cream logo.
Colours from nixwoods-reel/MOTION.md. Usage: python3 make_stills.py <project>/assets"""
import sys, numpy as np
from PIL import Image
out = sys.argv[1]
W, H = 1080, 1920
teak = np.array([46, 30, 20], float)          # teak ground #2E1E14
def smooth(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
y = np.arange(H, dtype=float)[:, None] * np.ones((1, W))
# caption scrim: dark teak gradient rising behind the caption band (captions sit ~y 1000-1240)
a = smooth((y - 820) / 360) * (1 - smooth((y - 1500) / 300)) * 0.72
rgba = np.dstack([np.broadcast_to(teak, (H, W, 3)), a[..., None] * 255]).astype(np.uint8)
Image.fromarray(rgba, "RGBA").save(f"{out}/stills/scrim-captions.png")
# hook scrim: top gradient behind the hook headline (y 230-560)
a = (1 - smooth((y - 380) / 380)) * 0.78
rgba = np.dstack([np.broadcast_to(teak, (H, W, 3)), a[..., None] * 255]).astype(np.uint8)
Image.fromarray(rgba, "RGBA").save(f"{out}/stills/scrim-hook.png")
# Dusk end-card ground: teak, soft vignette (1.08 - 0.35 r), grain sigma 2.2, lifted blacks
xx = (np.arange(W)[None, :] - W / 2) / (W / 2); yy = (np.arange(H)[:, None] - H / 2) / (H / 2)
r = np.sqrt(xx ** 2 + yy ** 2) / np.sqrt(2)
g = teak[None, None, :] * (1.08 - 0.35 * r)[..., None]
g += np.random.default_rng(7).normal(0, 2.2, (H, W, 1))
Image.fromarray(np.clip(g + 5, 0, 255).astype(np.uint8), "RGB").save(f"{out}/stills/endcard-ground.png")
# logo tinted cream #F6EFE4
logo = np.asarray(Image.open(f"{out}/logo.png").convert("RGBA")).astype(float)
logo[..., :3] = np.array([246, 239, 228])
Image.fromarray(logo.astype(np.uint8), "RGBA").save(f"{out}/stills/logo-cream.png")
print("ok", Image.open(f"{out}/stills/logo-cream.png").size)
