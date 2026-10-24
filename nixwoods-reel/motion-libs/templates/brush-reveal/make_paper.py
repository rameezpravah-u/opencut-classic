#!/usr/bin/env python3
"""paper.jpg: MOTION.md Paper ground (#EEE4D4 into Cream #F6EFE4) with a fine grain and soft fibres, made once."""
import os
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
rng = np.random.default_rng(5)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cream, paper = np.array([246, 239, 228], np.float32), np.array([238, 228, 212], np.float32)
g = np.clip(((xx - W / 2) ** 2 + (yy - H * 0.45) ** 2) ** 0.5 / (H * 0.75), 0, 1)[..., None]
base = cream * (1 - g) + paper * g
grain = rng.normal(0, 1, (H, W)).astype(np.float32)
blot = np.asarray(Image.fromarray((rng.random((H // 8, W // 8)) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                  .filter(ImageFilter.GaussianBlur(18)), np.float32) / 255 - 0.5
img = base + grain[..., None] * 3.0 + blot[..., None] * 10.0
fib = Image.new("L", (W, H), 0)
from PIL import ImageDraw
d = ImageDraw.Draw(fib)
for _ in range(900):                                   # paper fibres
    x, y, a, L = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0, np.pi), rng.uniform(6, 22)
    d.line([(x, y), (x + np.cos(a) * L, y + np.sin(a) * L)], fill=int(rng.uniform(40, 90)), width=1)
img -= np.asarray(fib.filter(ImageFilter.GaussianBlur(0.6)), np.float32)[..., None] * 0.06
Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(os.path.dirname(__file__), "paper.jpg"), quality=90)
print("paper.jpg")
