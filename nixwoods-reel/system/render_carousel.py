#!/usr/bin/env python3
"""render_carousel.py — an approved reel-engine carousel -> 4:5 Instagram carousel slides + 9:16 Story frames.

Input: nixwoods-os 40-Content/reel-engine/scripts/<NW-CREATIVE-CAROUSEL-...>.json (type "carousel", status APPROVED
or RENDERED), gate-checked by check_script.py. Each slide: headline, body, image (clip id in <product>-reels/src/),
optional crop [x0, y0, x1, y1] (fractions of the photo). Brand: Fraunces display, DM Sans body, Bone / Muted Bone,
the scrim from the brand kit, the NX logo from assets/logo.png on the last slide (never typeset).

Run from nixwoods-reel/:
  python3 system/render_carousel.py <carousel.json> --product aurora-reels [--out DIR]
Writes slide-01..NN.jpg (1080x1350), story-01..NN.jpg (1080x1920) and contact.jpg.
"""
import argparse
import json
import pathlib

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
F_HEAD = str(ROOT / "assets" / "Fraunces-600.ttf")
F_BODY = str(ROOT / "assets" / "DM_Sans-500.ttf")
LOGO = ROOT / "assets" / "logo.png"
BONE, MUTED = (246, 241, 231), (215, 208, 197)
MARGIN = 96


def font(path, size):
    return ImageFont.truetype(path, size)


def width(text, size, path=F_HEAD):
    return ImageDraw.Draw(Image.new("L", (1, 1))).textlength(text, font=font(path, size))


def wrap(text, size, path, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and width(t, size, path) > max_w:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def find_image(src, image_id):
    hits = sorted(p for p in pathlib.Path(src).iterdir()
                  if (p.name.startswith(image_id + "-") or p.stem == image_id) and p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))
    if not hits:
        raise FileNotFoundError(f"no image for {image_id} in {src}")
    return hits[0]


def cover(im, w, h, crop=None):
    if crop:
        x0, y0, x1, y1 = crop
        W0, H0 = im.size
        im = im.crop((int(x0 * W0), int(y0 * H0), int(x1 * W0), int(y1 * H0)))
    s = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * s + 0.5), int(im.height * s + 0.5)), Image.LANCZOS)
    l, t = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((l, t, l + w, t + h))


def scrim(w, h, start):
    a = Image.new("L", (w, h), 0)
    px = a.load()
    for y in range(start, h):
        v = int(255 * 0.62 * ((y - start) / (h - start)) ** 0.85)
        for x in range(w):
            px[x, y] = v
    black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    black.putalpha(a)
    return black


def slide_image(photo, sl, idx, n, w, h, text_top, last):
    base = cover(photo, w, h, sl.get("crop")).convert("RGBA")
    base.alpha_composite(scrim(w, h, int(h * 0.48)))
    txt = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    hs = 70 if idx == 0 else 60
    heads = wrap(sl["headline"], hs, F_HEAD, w - 2 * MARGIN)
    bodies = wrap(sl.get("body", ""), 38, F_BODY, w - 2 * MARGIN) if sl.get("body") else []
    block = len(heads) * int(hs * 1.16) + (24 + len(bodies) * 52 if bodies else 0)
    y = max(text_top, text_top + (h - text_top - 140 - block) // 2) if idx == 0 else text_top
    for ln in heads:
        d.text((MARGIN, y), ln, font=font(F_HEAD, hs), fill=BONE)
        y += int(hs * 1.16)
    if bodies:
        y += 24
        for ln in bodies:
            d.text((MARGIN, y), ln, font=font(F_BODY, 38), fill=MUTED)
            y += 52
    d.text((w - MARGIN - width(f"{idx + 1}/{n}", 26, F_BODY), 64 if h < 1600 else 260), f"{idx + 1}/{n}", font=font(F_BODY, 26), fill=MUTED)
    a = txt.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5))
    shadow = Image.merge("RGBA", (Image.new("L", (w, h), 0),) * 3 + (a,))
    base.alpha_composite(shadow)
    base.alpha_composite(txt)
    if last and LOGO.exists():
        lg = Image.open(LOGO).convert("RGBA")
        lg.thumbnail((180, 180))
        base.alpha_composite(lg, (MARGIN, h - (140 if h < 1600 else 330) - lg.height // 2))
    return base.convert("RGB")


def render(c, src, out, preview=False):
    if c.get("type") != "carousel":
        raise ValueError(f"{c.get('id')}: not a carousel")
    if not preview and c.get("status") not in ("APPROVED", "RENDERED"):
        raise ValueError(f"{c.get('id')}: status {c.get('status')!r}; only an owner-approved carousel renders")
    out = pathlib.Path(out)
    out.mkdir(parents=True, exist_ok=True)
    photos = [Image.open(find_image(src, sl["image"])).convert("RGB") for sl in c["slides"]]
    n = len(c["slides"])
    thumbs = []
    for i, (sl, ph) in enumerate(zip(c["slides"], photos)):
        last = i == n - 1
        s = slide_image(ph, sl, i, n, 1080, 1350, 820, last)
        s.save(out / f"slide-{i + 1:02d}.jpg", quality=92)
        slide_image(ph, sl, i, n, 1080, 1920, 1300, last).save(out / f"story-{i + 1:02d}.jpg", quality=92)
        thumbs.append(s.resize((270, 338)))
    sheet = Image.new("RGB", (270 * n, 338), (0, 0, 0))
    for i, t in enumerate(thumbs):
        sheet.paste(t, (270 * i, 0))
    sheet.save(out / "contact.jpg", quality=88)
    if preview:
        (out / "PREVIEW.txt").write_text(f"Preview for owner review: {c.get('id')} status {c.get('status')}. Not for posting until APPROVED.\n")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carousel")
    ap.add_argument("--product", required=True, help="product folder, e.g. aurora-reels")
    ap.add_argument("--out")
    ap.add_argument("--preview", action="store_true", help="render an unapproved carousel for review only")
    a = ap.parse_args()
    c = json.loads(pathlib.Path(a.carousel).read_text())
    pdir = ROOT / a.product
    sub = "preview" if a.preview else "render_carousel"
    print(render(c, pdir / "src", a.out or pdir / "out" / sub / c["id"], preview=a.preview))
