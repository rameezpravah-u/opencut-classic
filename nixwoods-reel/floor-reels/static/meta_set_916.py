#!/usr/bin/env python3
"""9:16 cuts of the NixLine Meta test set (Reels / Stories placements).

Same scenes and type system as meta_set.py. Reels UI covers the top ~14% and the bottom ~35% of
the frame, so every word sits between y 280 and y 1250, x 65-1015; render() asserts it.

    python3 floor-reels/static/meta_set_916.py   # -> concepts/meta-set/NX-META-*-9x16.jpg
"""
import os, sys
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_set as m

W, H = 1080, 1920
SAFE = (65, 280, 1015, 1250)


def crop_fill(path, fx, box=(W, H)):
    """Scale to fill the box, then choose the horizontal crop: fx 0 = left edge, 1 = right edge."""
    im = Image.open(path).convert("RGB")
    s = max(box[0] / im.width, box[1] / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = round((im.width - box[0]) * fx)
    y = (im.height - box[1]) // 2
    return im.crop((x, y, x + box[0], y + box[1]))


class Guard:
    """Collects every text bottom so render() can prove nothing falls under the Reels UI."""
    def __init__(self): self.max_y = 0
    def __call__(self, y): self.max_y = max(self.max_y, y); return y


def labels(d, y, pairs):
    for cx, s, col in pairs:
        f = m.SANS(42); w = f.getlength(s) + 52
        d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + 68), radius=34, fill=(15, 12, 10, 175))
        d.text((cx, y + 34), s, font=f, fill=col, anchor="mm")


def a():
    g = Guard()
    img = m.scrim(crop_fill(f"{m.SCN}/A-diwali-dusk.jpg", 0.30), "left", 0.70, 0.66).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = g(m.pill(d, 80, 300, "Diwali price drop"))
    y = g(m.headline(d, 80, y + 44, ["Light up", "the corner."], 104))
    y = g(m.price_block(d, 80, y + 40))
    g(m.chips(d, 80, y + 20, ["Solid teak", "COD", "Free delivery"]))
    return img, g, "NX-META-A-diwali-price-drop-9x16.jpg"


def b():
    g = Guard()
    half = (W // 2, H)
    left = crop_fill(f"{m.SCN}/B-before-tubelight.jpg", 0.62, half)
    right = crop_fill(f"{m.SCN}/B-after-nixline.jpg", 0.62, half)
    img = Image.new("RGB", (W, H)); img.paste(left, (0, 0)); img.paste(right, (W // 2, 0))
    img = m.scrim(img, "top", 0.80, 0.50).convert("RGBA")          # text sits above the lamp
    d = ImageDraw.Draw(img)
    d.line((W // 2, 0, W // 2, H), fill=(246, 239, 228, 200), width=3)
    labels(d, 300, ((W // 4, "Tubelight", (225, 232, 240)), (3 * W // 4, "NixLine", m.AMBER)))
    g(368)
    y = g(m.headline(d, W // 2, 430, ["Same corner.", "Warmer nights."], 76, anchor="ma"))
    y = g(m.price_block(d, W // 2, y + 20, anchor="c"))
    g(m.chips(d, W // 2, y + 10, ["Solid teak", "COD", "Free delivery"], anchor="c"))
    return img, g, "NX-META-B-before-after-9x16.jpg"


def c():
    g = Guard()
    img = m.scrim(crop_fill(f"{m.SCN}/C-reading-nook.jpg", 0.80), "top", 0.75, 0.50).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = g(m.headline(d, 80, 300, ["Your evening,", "in warm light."], 92))
    y = g(m.price_block(d, 80, y + 30))
    g(m.chips(d, 80, y + 16, ["Solid teak", "COD", "Free delivery"]))
    return img, g, "NX-META-C-her-evening-9x16.jpg"


def dd():
    g = Guard()
    img = m.scrim(crop_fill(f"{m.SCN}/D-diwali-gift.jpg", 0.30), "left", 0.74, 0.68).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = g(m.pill(d, 80, 300, "Diwali gift under ₹1,000"))
    y = g(m.headline(d, 80, y + 44, ["A gift", "that glows."], 104))
    y = g(m.price_block(d, 80, y + 40))
    g(m.chips(d, 80, y + 20, ["Handmade", "COD", "Free delivery"]))
    return img, g, "NX-META-D-diwali-gift-9x16.jpg"


def f():
    g = Guard()
    img = m.scrim(crop_fill(f"{m.SCN}/F-metal-vs-teak.jpg", 0.50), "bottom", 0.85, 0.60).convert("RGBA")
    d = ImageDraw.Draw(img)
    labels(d, 300, ((W // 4, "Metal lamp", (225, 232, 240)), (3 * W // 4, "Solid teak", m.AMBER)))
    g(368)
    y = g(m.headline(d, W // 2, 840, ["Not brighter.", "Warmer."], 86, anchor="ma"))
    y = g(m.price_block(d, W // 2, y + 20, anchor="c"))
    g(m.chips(d, W // 2, y + 10, ["No MDF", "COD", "Free delivery"], anchor="c"))
    return img, g, "NX-META-F-metal-vs-teak-9x16.jpg"


if __name__ == "__main__":
    for fn in (a, b, c, dd, f):
        img, g, name = fn()
        assert g.max_y <= SAFE[3], (name, g.max_y)
        print(os.path.relpath(m.finish(img, name), m.ROOT), "text ends at y", g.max_y)
