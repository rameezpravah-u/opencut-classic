#!/usr/bin/env python3
"""Aurora Linear Wall Light: "Down only, or up & down?" (20 Nov 2026, owner: "make a reel for aurora")

Why this idea: the one real choice a buyer makes on the Aurora page is the light direction, and the page says it
plainly ("Down only: a warm pool of light below. The wall above stays dark." / "Up and down: ... the whole wall
glows."). A reel that answers it is a save, and the reveal (the wall above the bar lighting up) is the hook payoff.

Material: there is no real footage of the live Natural Teak bar (every Aurora clip on Drive is the August shoot with the
discontinued Black bar). The eight live product-page images (Shopify CDN, pulled 20 Nov) are 1254x1254 with no camera
metadata, the output size of an image generator, so they are treated as AI imagery: "Made with AI" on, and a caption
line. Images used: 03 (the page's own Downward / Up & Down pair; the up & down room is also the end card), 04 (above a
bed), 05 (above a painting, 30 in), 06 (above a bathroom mirror, 30 in), 02 (the grain and the light line).

Facts, live page 20 Nov: solid teak (no MDF, no veneer), 30 or 48 inch, warm white 3000K, down only or up and down,
from ₹1,999 (30 in, down only). Hardwired (not claimed on screen). No price on screen in the social cut.

music6-corners grid (0.8357 s, first beat 0.396):
  0 - G4      03 left (down only), slow push        "Down only:" / "a warm pool *below.*"
  G4 - G6     the up-light rises from the bar        "Up & down:" / "the whole wall *glows.*"
  G6 - G9     three rooms, one per beat              chips: above a bed · above a painting · above a mirror
  G9 - G11    02 grain macro                         "Solid teak." / "No MDF, no veneer."
  G11 - end   03 up & down room, darkened low            Aurora Wall Light · 30 or 48 inch · warm 3000K · nixwoods.com

    /usr/bin/python3 brand-reels/aurora-down-or-up/aurora_down_or_up.py [--frames 0.5,4.6,6.0,8.5,10.5]
"""
import argparse, os, subprocess, sys

import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "art-light"))
from art_light import FF, W, FPS, CREAM, AMBER, AMBER_D, MUTED_D, GROUND, font, sstep, text, alpha, layer, grain, \
    music_wav as _unused  # noqa: E402,F401
import art_light  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
IMG = lambda n: os.path.join(HERE, "src", f"pdp-{n:02d}.jpg")
OUT = os.path.join(HERE, "out")
H = 1920
BEAT, B0 = 0.8357, 0.396
G = lambda k: round(B0 + k * BEAT, 3)
DUR = G(13)                                   # 11.26 s
NAME = "NW-CREATIVE-VID-20261120-nixwoods-aurora-linear-wall-light-down-or-up-v1"

_cache = {}


def src(n, box):
    """Crop box (x0, y0, x1, y1) in source px, upscaled to 1080x1920, lightly sharpened."""
    key = (n, box)
    if key not in _cache:
        im = Image.open(IMG(n)).convert("RGB").crop(box).resize((W, H), Image.LANCZOS)
        _cache[key] = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return _cache[key]


def push(im, u, amount, cy=0.5):
    z = 1 + amount * sstep(u)
    if z <= 1.0001:
        return im.copy()
    im2 = im.resize((round(W * z), round(H * z)), Image.LANCZOS)
    x = (im2.width - W) // 2
    y = int((im2.height - H) * cy)
    return im2.crop((x, y, x + W, y + H))


# crops: image 03 is the pair (left panel x 0-627 down only, right panel x 627-1254 up & down); 9:16 of a 627-wide
# panel is 1115 tall, taken from the top so the baked labels at the bottom fall away.
DOWN = (3, (0, 30, 627, 1145))
UPDN = (3, (627, 30, 1254, 1145))
ROOMS = [(4, (275, 0, 980, 1254), "Above a bed"), (5, (240, 0, 945, 1254), "Above a painting"),
         (6, (300, 0, 1005, 1254), "Above a mirror")]
GRAIN = (2, (330, 0, 1035, 1254))


def scrim_band(im, y0, y1, strength=0.6):
    arr = np.asarray(im, np.float32)
    yy = np.arange(H)[:, None, None]
    m = (np.clip((yy - (y0 - 160)) / 160, 0, 1) * np.clip(((y1 + 160) - yy) / 160, 0, 1)) * strength
    arr = arr * (1 - m) + np.array(GROUND, np.float32) * m
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def headline(d, y, l1, l2, a, accent, rise=22):
    f, fi = font("Fraunces-600.ttf", 88), font("Fraunces-500-i.ttf", 88)
    dy = (1 - a) * rise
    text(d, (W / 2, y + dy), l1, f, alpha(CREAM, a))
    pre, word, post = l2.partition(accent)
    parts = [(pre, f, CREAM), (word, fi, AMBER), (post, f, CREAM)]
    x = W / 2 - sum(ff.getlength(s) for s, ff, _ in parts) / 2
    for s, ff, c in parts:
        if s:
            d.text((x, y + 106 + dy), s, font=ff, fill=alpha(c, a), anchor="lm")
            x += ff.getlength(s)


def env(lt, secs, fin=0.35, fout=0.22):
    return sstep(lt / fin) * (1 - sstep((lt - (secs - fout)) / fout))


def chip(d, cx, cy, s, a, size=40):
    f = font("Inter-600.ttf", size)
    pw, ph = f.getlength(s) + 60, size + 38
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), ph / 2, fill=alpha(CREAM, a * 0.93))
    text(d, (cx, cy + 1), s, f, alpha(AMBER_D, a))


BAR_Y = 0.165          # the bar's light line in the 03 crop, as a fraction of the height (checked on stills)


def frame(t):
    if t < G(4):                                                   # down only
        lt, secs = t, G(4)
        im = push(src(*DOWN), lt / secs, 0.06, 0.2)
        im = scrim_band(im, 1090, 1330, 0.66)
        a = env(lt, secs, fout=0.01)
        k = sstep((lt - 0.05) / 0.3)
        return layer(im, lambda d: (headline(d, 1200, "Down only:", "a warm pool below.", a, "below."),
                                    text(d, (W / 2, 1090), "AURORA · WHICH ONE IS YOURS?",
                                         font("Inter-600.ttf", 34), alpha(AMBER, k * env(lt, secs, fout=0.3)))))
    if t < G(6):                                                   # the up-light rises from the bar
        lt, secs = t - G(4), G(6) - G(4)
        a_im = push(src(*DOWN), 1.0, 0.06, 0.2)
        b_im = push(src(*UPDN), 1.0, 0.06, 0.2)
        r = sstep(lt / 0.75)                                       # the reveal edge climbs from the bar to the top
        edge = BAR_Y * H * (1 - r)
        yy = np.arange(H)[:, None, None].astype(np.float32)
        m = np.clip((yy - (edge - 90)) / 90, 0, 1)
        m = np.where(yy > BAR_Y * H + 40, 1.0, m) if r > 0 else np.zeros_like(m)
        m = m * sstep(lt / 0.12)
        arr = np.asarray(a_im, np.float32) * (1 - m) + np.asarray(b_im, np.float32) * m
        im = scrim_band(Image.fromarray(arr.astype(np.uint8)), 1090, 1330, 0.66)
        a = env(lt - 0.25, secs - 0.25)
        g = sstep(lt / 0.1) * (1 - sstep((lt - 0.7) / 0.25))         # a soft amber edge rides the rising light

        def dr(d):
            if g > 0.01:
                for k in range(6):
                    d.rectangle((0, edge - 4 - k * 5, W, edge + 4 + k * 5), fill=alpha(AMBER, g * 0.10))
            headline(d, 1200, "Up & down:", "the whole wall glows.", a, "glows.")
        return layer(im, dr)
    if t < G(9):                                                   # three rooms, one per beat
        k = min(2, int((t - G(6)) / BEAT))
        lt = t - (G(6) + k * BEAT)
        n, box, label = ROOMS[k]
        im = scrim_band(push(src(n, box), lt / BEAT, 0.05), 1150, 1290, 0.45)
        return layer(im, lambda d: (chip(d, W / 2, 1180, label, sstep(lt / 0.18)),
                                    text(d, (W / 2, 1268), "30 inch" if k else "30 or 48 inch",
                                         font("Inter-600.ttf", 38), alpha(CREAM, sstep((lt - 0.08) / 0.18)))))
    if t < G(11):                                                  # the grain
        lt, secs = t - G(9), G(11) - G(9)
        im = scrim_band(push(src(*GRAIN), lt / secs, 0.07), 1180, 1330)
        a = env(lt, secs)
        return layer(im, lambda d: headline(d, 1200, "Solid teak.", "No MDF, no veneer.", a, "no veneer."))
    lt = t - G(11)                                                 # end card
    im = push(src(*UPDN), 1.0 + 0 * lt, 0.06, 0.2)
    k = sstep(lt / 0.4)
    arr = np.asarray(im, np.float32)
    yy = np.linspace(0, 1, H)[:, None, None]
    m = (np.clip((yy - 0.48) / 0.22, 0, 1)) * 0.72 * k
    im = Image.fromarray((arr * (1 - m) + np.array(GROUND, np.float32) * m).clip(0, 255).astype(np.uint8))
    a1, a2, a3 = (sstep((lt - d0) / 0.3) for d0 in (0.1, 0.25, 0.4))
    return layer(im, lambda d: (text(d, (W / 2, 1220), "Aurora Wall Light", font("Fraunces-600.ttf", 84), alpha(CREAM, a1)),
                                text(d, (W / 2, 1310), "Solid teak · 30 or 48 inch · warm 3000K",
                                     font("Inter-400.ttf", 38), alpha(MUTED_D, a2)),
                                text(d, (W / 2, 1420), "nixwoods.com", font("Inter-600.ttf", 44), alpha(CREAM, a3))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    if a.frames:
        for s in a.frames.split(","):
            frame(float(s)).save(os.path.join(OUT, f"still-{float(s):05.2f}.jpg"), quality=88)
        return
    art_light.DUR = DUR                                            # music6 bed, faded over the last 0.8 s
    path = os.path.join(OUT, NAME + ".mp4")
    art_light.render_with(lambda t, h: frame(t), H, path)
    print("wrote", path, "dur", DUR)


if __name__ == "__main__":
    main()
