#!/usr/bin/env python3
"""Contact sheet: python3 sheet.py input.mp4 out.jpg [fps] [cols]. 2 fps, 216 px wide tiles, time labels."""
import subprocess, sys, tempfile, os, glob
from PIL import Image, ImageDraw, ImageFont
src, out = sys.argv[1], sys.argv[2]
fps = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 10
with tempfile.TemporaryDirectory() as d:
    subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"fps={fps},scale=216:-1", f"{d}/f%04d.png"], check=True)
    files = sorted(glob.glob(f"{d}/f*.png"))
    ims = [Image.open(f).convert("RGB") for f in files]
w, h = ims[0].size
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 18)), (20, 20, 20))
dr = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * (h + 18)
    sheet.paste(im, (x, y + 18))
    t = i / fps  # ffmpeg fps filter: output frame i has pts i/fps
    dr.text((x + 4, y + 3), f"{i}: {t:.2f}s", fill=(255, 220, 120))
sheet.save(out, quality=88)
print(out, len(ims), "tiles")
