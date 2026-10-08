#!/usr/bin/env python3
"""NixLine "Swipe to reveal" carousel — 7 slides, 4:5.

Format 6 of @yoursocialteam's Ddw6x4jnb9w ("Swipe to Reveal" / "hold the dots and slide to reveal what
you need"): the same picture on every slide, pixelated in big blocks that get finer slide by slide,
clear only at the end. Holding the carousel dots flips the slides like a flipbook, so the picture
comes into focus as one little animation; swiping does it a step at a time. Everything except the
pixel size is identical on slides 1-6 so the flipbook doesn't jump.

The picture is the real NixLine in a corner (clean 5 Aug shoot, AC4I9815, from Drive). No generated
imagery; price, COD and free delivery as on the .com PDP and Shopify shipping rates.

    python3 floor-reels/static/reveal.py   # -> concepts/reveal/NX-REVEAL-01..07.jpg
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "assets")
PHOTO = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                     "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
OUT = os.path.join(ROOT, "floor-reels", "concepts", "reveal")
W, H = 1080, 1350
CROP = (1400, 2300, 3648, 2300 + 2248 * H / W)   # the corner: right half of the plant, the lamp, the floor
BLOCKS = [120, 72, 45, 27, 15, 8]                # pixel size per slide, coarse to fine; slide 7 is clear
CREAM, TEAK, MUTED, AMBER = (246, 239, 228), (52, 34, 22), (110, 90, 74), (176, 104, 40)


def font(name, size):
    return ImageFont.truetype(os.path.join(A, name), size)


def base():
    im = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
    im = im.resize((W, H), Image.LANCZOS, box=CROP)
    a = np.asarray(im).astype(np.float32) / 255
    a = np.clip(a * np.array([1.06, 1.0, 0.88]), 0, 1) ** 1.04          # the same warm grade as the other set
    return Image.fromarray((a * 255).astype(np.uint8))


def pixelate(im, b):
    """Average over b x b blocks (box filter down, nearest up) so each block is a flat square."""
    small = im.resize((max(1, W // b), max(1, H // b)), Image.BOX)
    return small.resize((W, H), Image.NEAREST)


def band(img, top=True, strength=0.78, extent=0.30):
    """A soft cream wash so the type sits clear of the picture, as on the reference's cards."""
    m = np.zeros((H, W), np.float32)
    n = int(H * extent)
    ramp = np.linspace(strength, 0, n) ** 1.4
    if top:
        m[:n] = ramp[:, None]
    else:
        m[H - n:] = ramp[::-1][:, None]
    cream = Image.new("RGB", (W, H), CREAM)
    return Image.composite(cream, img, Image.fromarray((m * 255).astype(np.uint8)))


def arrows_note(d, y):
    f = font("Inter-600.ttf", 36)
    s = "hold the dots and slide to reveal it"
    d.text((W // 2, y), s, font=f, fill=TEAK, anchor="mm")
    w = f.getlength(s)
    for x in (W // 2 - w / 2 - 50, W // 2 + w / 2 + 50):                 # the reference's ↓ either side
        d.line((x, y - 22, x, y + 18), fill=TEAK, width=4)
        d.polygon([(x - 11, y + 8), (x + 11, y + 8), (x, y + 24)], fill=TEAK)


def teaser(px):
    img = band(band(px, True, 0.86, 0.24), False, 0.80, 0.16)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 104), "What's missing here?", font=font("Fraunces-600.ttf", 86), fill=TEAK, anchor="ma")
    arrows_note(d, H - 92)
    d.text((W - 60, 60), "@nix_woods", font=font("Inter-600.ttf", 26), fill=MUTED, anchor="ra")
    return img


def reveal(clear):
    img = band(band(clear, True, 0.94, 0.30), False, 0.0, 0.01)
    d = ImageDraw.Draw(img)
    d.text((W // 2, 104), "A line of warm light.", font=font("Fraunces-600.ttf", 86), fill=TEAK, anchor="ma")
    d.text((W // 2, 214), "NixLine · solid teak floor lamp", font=font("Inter-600.ttf", 38), fill=MUTED, anchor="ma")
    # price card on the floor, left of the lamp
    x, y = 70, 1020
    card = Image.new("RGBA", (440, 250), CREAM + (236,))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, 439, 249), 28, fill=255)
    img.paste(card.convert("RGB"), (x, y), m)
    big, small = font("Inter-600.ttf", 92), font("Inter-400.ttf", 40)
    d.text((x + 30, y + 22), "₹999", font=big, fill=AMBER)
    wx = x + 40 + big.getlength("₹999")
    d.text((wx, y + 64), "₹1,599", font=small, fill=MUTED)
    d.line((wx - 2, y + 88, wx + small.getlength("₹1,599") + 2, y + 88), fill=MUTED, width=4)
    d.text((x + 30, y + 150), "Cash on delivery · Free delivery", font=font("Inter-600.ttf", 26), fill=TEAK)
    d.text((x + 30, y + 192), "nixwoods.com", font=font("Inter-600.ttf", 30), fill=TEAK)
    d.text((W - 60, 60), "@nix_woods", font=font("Inter-600.ttf", 26), fill=MUTED, anchor="ra")
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    clear = base()
    for i, b in enumerate(BLOCKS, 1):
        teaser(pixelate(clear, b)).save(os.path.join(OUT, f"NX-REVEAL-{i:02d}.jpg"), quality=93)
    reveal(clear).save(os.path.join(OUT, f"NX-REVEAL-{len(BLOCKS) + 1:02d}.jpg"), quality=93)
    print(os.path.relpath(OUT, ROOT), f"{len(BLOCKS) + 1} slides")


if __name__ == "__main__":
    main()
