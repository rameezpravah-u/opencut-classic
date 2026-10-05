"""Render nixline_trace.py sequentially (the light trails accumulate frame to frame), keep chosen frames."""
import sys, time, numpy as np
from PIL import Image
import nixline_trace as T
T.setup()
want = sorted(float(x) for x in sys.argv[1].split(","))
ks = {int(round(t * T.FPS)): t for t in want}
tiles = []; t0 = time.time()
for k in range(max(ks) + 1):
    fr = T.frame(k)
    if k in ks:
        u = fr.clip(0, 255).astype(np.uint8)
        tiles.append(np.asarray(Image.fromarray(u).resize((216, 384), Image.LANCZOS)))
        print(f"t={ks[k]:5.2f}  mean {u.mean():5.1f}  clipped {100*(u>=254).all(-1).mean():5.2f}%  R{u[...,0].mean():.0f} G{u[...,1].mean():.0f} B{u[...,2].mean():.0f}", flush=True)
print(f"{max(ks)+1} frames in {time.time()-t0:.0f}s")
cols = 8
rows = [np.concatenate(tiles[i:i+cols] + [np.zeros_like(tiles[0])]*(cols-len(tiles[i:i+cols])), 1) for i in range(0, len(tiles), cols)]
Image.fromarray(np.concatenate(rows, 0)).save(sys.argv[2], quality=90)
