#!/usr/bin/env python3
"""measure_sources.py — what you must know about a still before you frame it in 9:16.

For every source image: pixel size, aspect, mean/p5/p95 luminance, per-channel mean, and the
upscale factor the image is subjected to by each 9:16 fit mode at 1080x1920.

    python3 measure_sources.py ../../../../../nixwoods-reel/teak-reels/hf

Why each number matters
  aspect            a square source cover-cropped to 9:16 keeps only 9/16 = 56.25% of its width.
                    For a 49-inch linear pendant that is where the ends of the product go.
                    It also means crop_cy is a no-op on a square source: only crop_cx moves the window.
  mean luminance    "contain" lays the subject over a blurred, dimmed copy of itself, so the
                    backing lands near mean*0.82. Below ~70 mean the backing is effectively black
                    and the subject reads as a thin lit band in an empty frame. p5 tells you
                    separately how much shadow crush the grade can take.
  upscale           anything past ~2x is visibly soft at 1080 wide on a phone. Measure, don't squint.
  channel means     warm light wants R > G > B. Check after any grade or bloom.
"""
import sys, os, glob
import numpy as np
from PIL import Image

W, H = 1080, 1920
AR = W / H

def report(path):
    im = Image.open(path)
    w, h = im.size
    rgb = np.asarray(im.convert("RGB")).astype(float)
    lum = np.asarray(im.convert("L")).astype(float)
    ar = w / h
    # cover: scale so the frame is filled, then crop
    cover = max(W / w, H / h)
    # contain: whole image fits inside the frame
    contain = min(W / w, H / h)
    kept_w = min(1.0, (ar and (AR / ar))) if ar >= AR else 1.0
    return dict(
        name=os.path.basename(path), w=w, h=h, ar=ar,
        mean=lum.mean(), p5=np.percentile(lum, 5), p95=np.percentile(lum, 95),
        r=rgb[:, :, 0].mean(), g=rgb[:, :, 1].mean(), b=rgb[:, :, 2].mean(),
        cover=cover, contain=contain, kept_w=kept_w,
    )

def main(d):
    files = sorted(f for f in glob.glob(os.path.join(d, "*"))
                   if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")))
    print(f"{'file':30s} {'px':>11s} {'ar':>6s} {'mean':>6s} {'p5':>5s} {'p95':>5s} "
          f"{'R/G/B':>13s} {'cover':>6s} {'contain':>8s} {'width kept':>11s}")
    for f in files:
        r = report(f)
        flags = []
        if r["cover"] > 2.0:
            flags.append(f"cover {r['cover']:.1f}x = soft")
        if r["mean"] < 70:
            flags.append(f"mean {r['mean']:.0f} -> contain backing ~{r['mean']*0.82:.0f}, near black")
        if r["p5"] < 30:
            flags.append(f"p5 {r['p5']:.0f} = no room for a shadow crush")
        if r["kept_w"] < 0.75:
            flags.append(f"cover keeps only {r['kept_w']*100:.0f}% of width")
        print(f"{r['name']:30s} {r['w']:5d}x{r['h']:<5d} {r['ar']:6.3f} {r['mean']:6.1f} "
              f"{r['p5']:5.0f} {r['p95']:5.0f} {r['r']:4.0f}/{r['g']:3.0f}/{r['b']:3.0f} "
              f"{r['cover']:5.2f}x {r['contain']:7.2f}x {r['kept_w']*100:9.0f}%")
        for fl in flags:
            print(f"{'':30s}   ! {fl}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
