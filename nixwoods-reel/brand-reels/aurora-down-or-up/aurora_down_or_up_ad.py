#!/usr/bin/env python3
"""Aurora "Down only, or up & down?": the Meta ad cut (22 Nov 2026, owner: "make a meta ad version of this too").

Same pictures and reveal as the social reel (`aurora_down_or_up.py`), cut for paid placements:
  - 10.0 s (MOTION: ads 9.5-10 s); the grain shot is folded into the end card ("Solid teak").
  - the price from frame 1: an "Aurora Wall Light · from ₹1,999" chip under the headline until the rooms.
  - end card: name, solid teak · 30 or 48 inch · warm 3000K, "from ₹1,999", "Free shipping on prepaid orders",
    "Shop at nixwoods.com". The page's old buy2 code is gone (checked 22 Nov), so it is not used.
  - every line of text ends above y 1250 on 9:16 (the CTA zone); 4:5 is the top 1350 px of the 9:16 frame.
Live page 22 Nov: 30 in down only ₹1,999 (was ₹2,749) ... 48 in up & down ₹3,499. AI imagery: "Made with AI" on.

    /usr/bin/python3 brand-reels/aurora-down-or-up/aurora_down_or_up_ad.py [--frames 0.5,4.4,6.4,9.5]
"""
import argparse, os, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import aurora_down_or_up as S  # noqa: E402
from aurora_down_or_up import (W, H, G, BEAT, CREAM, AMBER, MUTED_D, GROUND, DOWN, UPDN, ROOMS, BAR_Y, src, push,  # noqa: E402
                               scrim_band, headline, env, chip, font, text, alpha, layer, sstep)
import art_light  # noqa: E402

DUR = 10.0
Y45 = 0                                                           # 4:5 crop top: the top 1350 px keeps the bar, the baked size labels and all text
NAME = "NW-CREATIVE-VID-20261122-nixwoods-aurora-linear-wall-light-down-or-up-ad-{}-v1"
PRICE = "Aurora Wall Light · from ₹1,999"


def price_chip(d, a):
    chip(d, W / 2, 1165, PRICE, a, size=36)


def frame(t):
    if t < G(4):                                                   # down only, price from 0.4 s
        lt, secs = t, G(4)
        im = scrim_band(push(src(*DOWN), lt / secs, 0.06, 0.2), 900, 1200, 0.66)
        a = env(lt, secs, fout=0.01)
        k = sstep((lt - 0.05) / 0.3)
        p = sstep((lt - 0.4) / 0.3)
        return layer(im, lambda d: (text(d, (W / 2, 880), "AURORA · WHICH ONE IS YOURS?", font("Inter-600.ttf", 34),
                                         alpha(AMBER, k * env(lt, secs, fout=0.3))),
                                    headline(d, 975, "Down only:", "a warm pool below.", a, "below."),
                                    price_chip(d, p)))
    if t < G(6):                                                   # the up-light rises from the bar
        lt, secs = t - G(4), G(6) - G(4)
        a_im = push(src(*DOWN), 1.0, 0.06, 0.2)
        b_im = push(src(*UPDN), 1.0, 0.06, 0.2)
        r = sstep(lt / 0.75)
        edge = BAR_Y * H * (1 - r)
        yy = np.arange(H)[:, None, None].astype(np.float32)
        m = np.clip((yy - (edge - 90)) / 90, 0, 1)
        m = np.where(yy > BAR_Y * H + 40, 1.0, m) if r > 0 else np.zeros_like(m)
        m = m * sstep(lt / 0.12)
        arr = np.asarray(a_im, np.float32) * (1 - m) + np.asarray(b_im, np.float32) * m
        im = scrim_band(Image.fromarray(arr.astype(np.uint8)), 900, 1200, 0.66)
        a = env(lt - 0.25, secs - 0.25)
        g = sstep(lt / 0.1) * (1 - sstep((lt - 0.7) / 0.25))

        def dr(d):
            if g > 0.01:
                for k in range(6):
                    d.rectangle((0, edge - 4 - k * 5, W, edge + 4 + k * 5), fill=alpha(AMBER, g * 0.10))
            headline(d, 975, "Up & down:", "the whole wall glows.", a, "glows.")
            price_chip(d, 1 - sstep((lt - (secs - 0.2)) / 0.2))
        return layer(im, dr)
    if t < G(9):                                                   # three rooms, one per beat
        k = min(2, int((t - G(6)) / BEAT))
        lt = t - (G(6) + k * BEAT)
        n, box, label = ROOMS[k]
        im = scrim_band(push(src(n, box), lt / BEAT, 0.05), 1040, 1170, 0.62)
        return layer(im, lambda d: (chip(d, W / 2, 1070, label, sstep(lt / 0.18)),
                                    text(d, (W / 2, 1155), "30 inch" if k else "30 or 48 inch",
                                         font("Inter-600.ttf", 38), alpha(CREAM, sstep((lt - 0.08) / 0.18)))))
    lt = t - G(9)                                                  # end card with the price
    im = push(src(*UPDN), 1.0, 0.06, 0.2)
    k = sstep(lt / 0.35)
    arr = np.asarray(im, np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    m = np.clip((yy - 0.33) / 0.12, 0, 1) * 0.78 * k
    im = Image.fromarray((arr * (1 - m) + np.array(GROUND, np.float32) * m).clip(0, 255).astype(np.uint8))
    a1, a2, a3, a4 = (sstep((lt - d0) / 0.25) for d0 in (0.05, 0.18, 0.31, 0.44))
    return layer(im, lambda d: (
        text(d, (W / 2, 800), "Aurora Wall Light", font("Fraunces-600.ttf", 84), alpha(CREAM, a1)),
        text(d, (W / 2, 885), "Solid teak · 30 or 48 inch · warm 3000K", font("Inter-400.ttf", 38), alpha(MUTED_D, a2)),
        chip(d, W / 2, 990, "from ₹1,999", a2, size=56),
        text(d, (W / 2, 1085), "Free shipping on prepaid orders", font("Inter-400.ttf", 36), alpha(CREAM, a3)),
        text(d, (W / 2, 1170), "Shop at nixwoods.com", font("Inter-600.ttf", 44), alpha(CREAM, a4))))


def framed(t, h):
    im = frame(t)
    return im if h == H else im.crop((0, Y45, W, Y45 + h))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None)
    a = ap.parse_args()
    os.makedirs(S.OUT, exist_ok=True)
    if a.frames:
        for s in a.frames.split(","):
            for h, tag in ((H, "916"), (1350, "45")):
                framed(float(s), h).save(os.path.join(S.OUT, f"ad-{tag}-{float(s):05.2f}.jpg"), quality=88)
        return
    art_light.DUR = DUR
    for h, tag in ((H, "9x16"), (1350, "4x5")):
        path = os.path.join(S.OUT, NAME.format(tag) + ".mp4")
        art_light.render_with(framed, h, path)
        print("wrote", path)


if __name__ == "__main__":
    main()
