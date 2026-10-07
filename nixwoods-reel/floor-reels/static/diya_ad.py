#!/usr/bin/env python3
"""NixLine — "The tallest diya in the family." A quirky Diwali static, 4:5 and 9:16.

The lamp stands at the end of a row of clay diyas like their tall big sibling. Every claim is true:
no oil, no refills, LED rated 25,000+ hours (PDP FAQ), solid teak, Rs 999 / Rs 1,599 (nixwoods.com compare-at, set 7 Oct; same as the
Rs 1,599 on the Shopdeck .in ad), COD, free delivery. Scene generated (AI disclosure in Ads Manager); lamp
checked against floor-reels/ref/AC4I9815: upright on its teak block, channel on the front face.

    python3 floor-reels/static/diya_ad.py   # -> concepts/meta-set/NX-META-G-tallest-diya-{4x5,9x16}.jpg
"""
import os, sys, math
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_set as m
import meta_set_916 as v

SCENE = f"{m.SCN}/G-tallest-diya.jpg"
HAND = lambda s: m.font("GochiHand-400.ttf", s)
ITAL = lambda s: m.font("Fraunces-500-i.ttf", s)


def mixed_line(d, cx, y, parts, size):
    """Centre a line made of (text, font, colour) parts."""
    fonts = [(t, f(size), c) for t, f, c in parts]
    total = sum(f.getlength(t) for t, f, _ in fonts)
    x = cx - total / 2
    for t, f, c in fonts:
        m.text(d, (x, y), t, f, c)
        x += f.getlength(t)


def headline(d, cx, y, size):
    mixed_line(d, cx, y, [("The ", m.SERIF, m.CREAM), ("tallest", ITAL, m.AMBER), (" diya", m.SERIF, m.CREAM)], size)
    mixed_line(d, cx, y + int(size * 1.1), [("in the family.", m.SERIF, m.CREAM)], size)
    return y + int(size * 2.2)


def note(d, x, y, tip, size=50):
    """A hand-written aside with a hand-drawn arrow curving to the lamp."""
    f = HAND(size)
    for i, l in enumerate(["no oil.", "no refills."]):
        m.text(d, (x, y + i * int(size * 1.0)), l, f, m.CREAM)
    sx, sy = x + f.getlength("no refills.") + 14, y + size * 1.25
    pts = []
    for k in range(25):
        t = k / 24
        px = sx + (tip[0] - sx) * t
        py = sy + (tip[1] - sy) * t - math.sin(t * math.pi) * 60
        pts.append((px, py))
    d.line(pts, fill=m.CREAM + (235,), width=5, joint="curve")
    ang = math.atan2(pts[-1][1] - pts[-3][1], pts[-1][0] - pts[-3][0])
    for da in (2.5, -2.5):
        d.line((tip, (tip[0] - 26 * math.cos(ang + da / 6), tip[1] - 26 * math.sin(ang + da / 6))),
               fill=m.CREAM + (235,), width=5)


def four_by_five():
    img = m.scrim(m.scrim(m.cover(SCENE), "top", 0.55, 0.35), "bottom", 0.78, 0.36).convert("RGBA")
    d = ImageDraw.Draw(img)
    headline(d, 540, 90, 92)
    note(d, 470, 470, (835, 560))
    y = m.price_block(d, 540, 1088, anchor="c")
    m.chips(d, 540, y + 6, ["Solid teak", "25,000-hr LED", "COD", "Free delivery"], anchor="c")
    return m.finish(img, "NX-META-G-tallest-diya-4x5.jpg")


def nine_by_sixteen():
    img = v.crop_fill(SCENE, 0.62)
    img = m.scrim(m.scrim(img, "top", 0.60, 0.40), "bottom", 0.80, 0.55).convert("RGBA")
    d = ImageDraw.Draw(img)
    headline(d, 540, 300, 96)
    note(d, 470, 740, (905, 860))
    y = m.price_block(d, 540, 1000, anchor="c")
    end = m.chips(d, 540, y + 6, ["Solid teak", "25,000-hr LED", "COD"], anchor="c")
    assert end <= v.SAFE[3], end
    return m.finish(img, "NX-META-G-tallest-diya-9x16.jpg")


if __name__ == "__main__":
    print(os.path.relpath(four_by_five(), m.ROOT))
    print(os.path.relpath(nine_by_sixteen(), m.ROOT))
