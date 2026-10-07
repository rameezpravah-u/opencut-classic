#!/usr/bin/env python3
"""NixLine Meta test set, 7 Oct — five distinct concepts around the account's proven winner.

Evidence (research 7 Oct, nixwoods-reel/floor-reels/concepts/meta-set/README.md):
  the live NixLine static on the .in account ("Banner 1") is the best ad on either account —
  13.6x ROAS, 265 purchases at Rs 83, 7.1% CTR — a warm dusk corner, the lamp the only light,
  Rs 999 vs Rs 1,599, COD. Meta's delivery now rewards several genuinely different concepts in one
  ad set, so each card here keeps what won (warm dim corner, the real upright lamp, price + COD)
  and changes the angle.

Scenes are generated (Higgsfield gpt_image_2_5) with the live ad as the lamp reference and the
real lamp described from floor-reels/ref/AC4I9815 (upright on a teak block, channel on the front
face). All text is set here, never by the model, so prices and claims are exact.
Meta AI disclosure must be ticked: the scenes are generated.

    python3 floor-reels/static/meta_set.py   # -> floor-reels/concepts/meta-set/NX-META-*.jpg
"""
import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A = os.path.join(ROOT, "..", "assets")
SCN = os.path.join(ROOT, "concepts", "meta-set", "scenes")
OUT = os.path.join(ROOT, "concepts", "meta-set")
W, H = 1080, 1350

PRICE, WAS = "₹999", "₹1,599"            # as on the live winning ad — confirm against the landing page
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)


def font(name, size):
    return ImageFont.truetype(os.path.join(A, name), size)


SERIF = lambda s: font("Fraunces-600.ttf", s)
SANS = lambda s: font("Inter-600.ttf", s)
SANS_R = lambda s: font("Inter-400.ttf", s)


def cover(path, box=(W, H)):
    im = Image.open(path).convert("RGB")
    s = max(box[0] / im.width, box[1] / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x, y = (im.width - box[0]) // 2, (im.height - box[1]) // 2
    return im.crop((x, y, x + box[0], y + box[1]))


def scrim(img, side, strength=0.62, extent=0.55):
    """Darken one side with a smooth gradient so type reads without a box."""
    w, h = img.size
    m = Image.new("L", (w, h), 0)
    px = m.load()
    for i in range(w if side in ("left", "right") else h):
        t = i / ((w if side in ("left", "right") else h) * extent)
        a = int(255 * strength * max(0.0, 1 - t) ** 1.6)
        if side == "left":
            for y in range(h): px[i, y] = a
        elif side == "right":
            for y in range(h): px[w - 1 - i, y] = a
        elif side == "top":
            for x in range(w): px[x, i] = a
        else:
            for x in range(w): px[x, h - 1 - i] = a
    dark = Image.new("RGB", (w, h), (12, 8, 6))
    return Image.composite(dark, img, m)


def text(d, xy, s, f, fill, shadow=True, anchor="la"):
    if shadow:
        d.text((xy[0] + 2, xy[1] + 3), s, font=f, fill=(0, 0, 0, 150), anchor=anchor)
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def headline(d, x, y, lines, size=86, fill=CREAM, anchor="la"):
    f = SERIF(size)
    for i, l in enumerate(lines):
        text(d, (x, y + i * int(size * 1.08)), l, f, fill, anchor=anchor)
    return y + len(lines) * int(size * 1.08)


def price_block(d, x, y, anchor="l"):
    big, small = SANS(112), SANS_R(46)
    if anchor == "c":
        total = big.getlength(PRICE) + 26 + small.getlength(WAS)
        x = x - total / 2
    text(d, (x, y), PRICE, big, AMBER)
    sx = x + big.getlength(PRICE) + 26
    sy = y + 52
    text(d, (sx, sy), WAS, small, MUTED)
    wy = sy + 30
    d.line((sx - 2, wy, sx + small.getlength(WAS) + 2, wy), fill=MUTED, width=4)
    return y + 128


def chips(d, x, y, items, anchor="l"):
    f = SANS(30)
    pad, gap, h = 22, 14, 56
    widths = [f.getlength(t) + 2 * pad for t in items]
    if anchor == "c":
        x = x - (sum(widths) + gap * (len(items) - 1)) / 2
    for t, w in zip(items, widths):
        d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=(20, 14, 10, 175),
                            outline=(232, 162, 74, 140), width=2)
        d.text((x + pad, y + h / 2), t, font=f, fill=CREAM, anchor="lm")
        x += w + gap
    return y + h


def pill(d, x, y, s, anchor="l"):
    f = SANS(32)
    w = f.getlength(s) + 44
    if anchor == "c":
        x -= w / 2
    d.rounded_rectangle((x, y, x + w, y + 58), radius=29, fill=AMBER + (255,))
    d.text((x + 22, y + 29), s, font=f, fill=(28, 18, 10), anchor="lm")
    return y + 58


def wordmark(img, x, y, h=64):
    logo = Image.open(os.path.join(A, "logo.png")).convert("RGBA")
    logo = logo.resize((round(logo.width * h / logo.height), h), Image.LANCZOS)
    img.paste(logo, (x, y), logo)


def finish(img, name):
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, name)
    img.convert("RGB").save(out, quality=93, subsampling=0)
    return out


def concept_a():   # control iteration: festive dusk corner, price-led
    img = scrim(cover(f"{SCN}/A-diwali-dusk.jpg"), "left", 0.70, 0.62).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = pill(d, 70, 120, "Diwali price drop")
    y = headline(d, 70, y + 40, ["Light up", "the corner."], 92)
    y = price_block(d, 70, y + 36)
    chips(d, 70, y + 18, ["Solid teak", "COD", "Free delivery"])
    wordmark(img, 70, H - 120)
    return finish(img, "NX-META-A-diwali-price-drop-4x5.jpg")


def concept_b():   # before / after, same corner
    left = cover(f"{SCN}/B-before-tubelight.jpg", (W // 2, H))
    right = cover(f"{SCN}/B-after-nixline.jpg", (W // 2, H))
    img = Image.new("RGB", (W, H))
    img.paste(left, (0, 0)); img.paste(right, (W // 2, 0))
    img = scrim(img, "bottom", 0.80, 0.42).convert("RGBA")
    d = ImageDraw.Draw(img)
    d.line((W // 2, 0, W // 2, H), fill=(246, 239, 228, 200), width=3)
    for cx, s, col in ((W // 4, "Tubelight", (225, 232, 240)), (3 * W // 4, "NixLine", AMBER)):
        f = SANS(40); w = f.getlength(s) + 48
        d.rounded_rectangle((cx - w / 2, 70, cx + w / 2, 134), radius=32, fill=(15, 12, 10, 170))
        d.text((cx, 102), s, font=f, fill=col, anchor="mm")
    y = headline(d, W // 2, H - 470, ["Same corner.", "Warmer nights."], 78, anchor="ma")
    y = price_block(d, W // 2, y + 18, anchor="c")
    chips(d, W // 2, y + 8, ["Solid teak", "COD", "Free delivery"], anchor="c")
    return finish(img, "NX-META-B-before-after-4x5.jpg")


def concept_c():   # persona: her evening
    img = scrim(cover(f"{SCN}/C-reading-nook.jpg"), "top", 0.72, 0.55).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = headline(d, 70, 96, ["Your evening,", "in warm light."], 84)
    y = price_block(d, 70, y + 26)
    chips(d, 70, y + 14, ["Solid teak", "COD", "Free delivery"])
    return finish(img, "NX-META-C-her-evening-4x5.jpg")


def concept_d():   # Diwali gift under Rs 1,000
    img = scrim(cover(f"{SCN}/D-diwali-gift.jpg"), "left", 0.74, 0.66).convert("RGBA")
    d = ImageDraw.Draw(img)
    y = pill(d, 70, 120, "Diwali gift under ₹1,000")
    y = headline(d, 70, y + 40, ["A gift", "that glows."], 92)
    y = price_block(d, 70, y + 36)
    chips(d, 70, y + 18, ["Handmade", "COD", "Free delivery"])
    wordmark(img, 70, H - 120)
    return finish(img, "NX-META-D-diwali-gift-4x5.jpg")


def concept_f():   # metal vs solid teak
    img = scrim(cover(f"{SCN}/F-metal-vs-teak.jpg"), "bottom", 0.82, 0.40).convert("RGBA")
    d = ImageDraw.Draw(img)
    for cx, s, col in ((W // 4, "Metal lamp", (225, 232, 240)), (3 * W // 4, "Solid teak", AMBER)):
        f = SANS(40); w = f.getlength(s) + 48
        d.rounded_rectangle((cx - w / 2, 70, cx + w / 2, 134), radius=32, fill=(15, 12, 10, 170))
        d.text((cx, 102), s, font=f, fill=col, anchor="mm")
    y = headline(d, W // 2, H - 430, ["Not brighter. Warmer."], 76, anchor="ma")
    y = price_block(d, W // 2, y + 22, anchor="c")
    chips(d, W // 2, y + 8, ["No MDF", "COD", "Free delivery"], anchor="c")
    return finish(img, "NX-META-F-metal-vs-teak-4x5.jpg")


if __name__ == "__main__":
    for fn in (concept_a, concept_b, concept_c, concept_d, concept_f):
        print(os.path.relpath(fn(), ROOT))
