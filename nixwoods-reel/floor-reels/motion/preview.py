"""Render selected frames of nixline_motion.py to a review sheet, without a full encode."""
import sys, numpy as np
from PIL import Image
import nixline_motion as M
M.CROP_X = {"tri_l": M.lamp_x(M.SRC("nx07-7922.mp4"), 0.0, 2.5),
            "tri_c": M.lamp_x(M.SRC("nx00-hero.mp4"), 6.4, 1.9), "tri_r": M.W * .5}
print("crop centres", {k: round(v) for k, v in M.CROP_X.items()})
M.open_shots()
ts = [float(x) for x in sys.argv[1].split(",")]
tiles = []
for t in ts:
    k = int(round(t * M.FPS))
    fr = M.frame(k).clip(0, 255).astype(np.uint8)
    tiles.append(np.asarray(Image.fromarray(fr).resize((216, 384), Image.LANCZOS)))
    print(f"t={t:5.2f}  mean {fr.mean():5.1f}  R{fr[...,0].mean():.0f} G{fr[...,1].mean():.0f} B{fr[...,2].mean():.0f}")
cols = 8
rows = [np.concatenate(tiles[i:i + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[i:i + cols])), 1)
        for i in range(0, len(tiles), cols)]
Image.fromarray(np.concatenate(rows, 0)).save(sys.argv[2], quality=90)
