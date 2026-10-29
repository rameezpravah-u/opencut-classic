#!/usr/bin/env python3
"""Circular Hole Wall Light, v2: day / night (owner, 29 Oct 2026: v1 "used the most blurred clips" and was "so basic").

v1 was built on the two tilt clips (8115, 8116), the softest of the ten. v2 is built on the sharpest:
8123 (4K, lights off, flame grain), 8122 (lights off, the row of holes), 8118 and 8119 (lit macros), with the
light over the painting (8114's settled end) kept for one beat only. Every clip was scored for sharpness first
(Laplacian variance at 10 fps) and checked at native resolution.

The idea: by day it is a piece of wood; by night it is a row of warm light. Hook built on "clear, then curious"
(the Hook Master carousel, instagram.com/p/De8I3VcjtKq, 26 Oct): the first frame says what it is (a wooden bar),
the line opens the gap ("By day, a piece of wood."), the switch pays it off on the beat ("By night, this.").
Carousel craft carried over in MOTION.md's palette and type: a glass day/night toggle that flips on the switch,
small-caps labels over a spec card, a serif headline with one amber italic accent, grain.

  social  9:16, 10.0 s   day hook -> switch -> lit macro + spec card -> over the art (save line) -> end card
  ad      9:16 + 4:5, 10.0 s   day + ₹3,999 from frame 1 -> switch -> lit macro + spec card -> over the art -> end card

Facts: the live page on 29 Oct (see art_light.py). Real footage only, so no AI label.

    python3 brand-reels/art-light/art_light_v2.py
    python3 brand-reels/art-light/art_light_v2.py --only social --frames 0.3,2.2,4.5,6.2,8.5
"""
import argparse, os, sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from art_light import (FF, W, FPS, SRC, CREAM, INK, AMBER, AMBER_D, MUTED_D, GROUND, LINE, OUT, DATE, HANDLE,  # noqa
                       G, DUR, font, sstep, clip_frames, grade, scrim, text, alpha, layer, music_wav, grain, render_with)

MUTED_L = (124, 100, 82)
GLASS = (24, 17, 12)


def S(clip, t_in, speed=1.0, zoom=1.0, zy=1.0, y45=285, night=True, fps=FPS):
    """zoom: a fixed scale; zy: where the scaled frame is anchored vertically (0 top, 1 bottom); fps: decode rate
    (60 for the 4K 60p clip, so a slowed shot gets real in-between frames instead of repeats)."""
    return dict(clip=clip, t_in=t_in, speed=speed, zoom=zoom, zy=zy, y45=y45, night=night, fps=fps)


GRAIN_DAY = S("IMG_8123.mov", 0.0, 0.6, zoom=1.0, y45=520, night=False, fps=60)  # 4K 60p: flame grain, holes dark,
#                                                      slowed so the close-up holds before the camera pulls back
HOLES_DAY = S("IMG_8122.mov", 0.55, 1.0, zoom=1.35, zy=0.62, y45=430, night=False)  # the row of dark holes
MACRO_ON = S("IMG_8118.mov", 1.10, 1.0, zoom=1.25, zy=1.0, y45=285)              # lit holes under dark grain
SLIDE_ON = S("IMG_8117.mov", 1.58, 0.98, zoom=1.12, zy=0.75, y45=380)            # lit holes along the bar end
#                                                      (8119 is softer: Laplacian var 6-8 against 15-17 here)
OVER_ART = S("IMG_8114.mov", 1.55, 0.75, zoom=1.0, y45=60)                       # the light settled over the art

CUTS = {
    "social": [(GRAIN_DAY, 0.0, G(2)), (MACRO_ON, G(2), G(4)), (SLIDE_ON, G(4), G(6)), (OVER_ART, G(6), G(8)),
               ("end", G(8), DUR)],
    "ad": [(HOLES_DAY, 0.0, G(2)), (MACRO_ON, G(2), G(4)), (SLIDE_ON, G(4), G(6)), (OVER_ART, G(6), G(8)),
           ("end", G(8), DUR)],
}
SWITCH = G(2)


def day_grade(fr):
    a = fr.astype(np.float32) / 255.0
    a = np.clip(a * np.array([1.05, 1.0, 0.92], np.float32), 0, 1) ** (1 / 1.03)
    return (a * 255).astype(np.uint8)


def footage(sh, lt, secs, h, push=0.05):
    fr = clip_frames(sh["clip"], sh["t_in"], secs * sh["speed"] + 0.25, sh["fps"])
    k = min(int(round(lt * sh["speed"] * sh["fps"])), len(fr) - 1)
    im = Image.fromarray(grade(fr[k]) if sh["night"] else day_grade(fr[k]))
    z = sh["zoom"] * (1 + push * sstep(lt / secs))
    if z > 1.0001:
        im = im.resize((round(W * z), round(1920 * z)), Image.LANCZOS)
        x = (im.width - W) // 2
        y = round((im.height - 1920) * sh["zy"])
        im = im.crop((x, y, x + W, y + 1920))
    if h != 1920:
        im = im.crop((0, sh["y45"], W, sh["y45"] + h))
    return im


def switch_on(im, lt):
    """The LED driver warming up over 0.3 s: the frame comes up from dim, the hot spots bloom in last."""
    s = sstep(lt / 0.30)
    if s >= 1:
        return im
    a = np.asarray(im, np.float32)
    lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hot = np.clip((lum - 180) / 60, 0, 1)[..., None]
    base = a * (0.42 + 0.58 * s)
    out = base * (1 - hot) + a * hot * s + base * hot * (1 - s) * 0.5
    return Image.fromarray(out.clip(0, 255).astype(np.uint8))


def wash(im, top, bottom, strength=0.72, col=CREAM):
    """A cream wash fading out from the top edge (text on a light wall), the light-ground twin of scrim()."""
    h = im.height
    yy = np.linspace(0, 1, h)[:, None]
    a = np.clip((bottom - yy) / max(1e-3, bottom - top), 0, 1) * strength
    arr = np.asarray(im, np.float32)
    arr = arr * (1 - a[..., None]) + np.array(col, np.float32) * a[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def toggle(im, t, y=300):
    """A glass DAY / NIGHT pill; the knob slides to NIGHT on the switch and picks up the amber glow."""
    k = sstep((t - SWITCH + 0.06) / 0.24)
    pw, ph = 330, 84
    x0, y0 = (W - pw) // 2, y - ph // 2
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), ph // 2, fill=GLASS + (150,), outline=CREAM + (90,), width=2)
    kx = x0 + 42 + k * (pw - 84)
    if k > 0:
        g = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse((kx - 40, y - 40, kx + 40, y + 40), fill=AMBER + (int(150 * k),))
        lay = Image.alpha_composite(lay, g.filter(ImageFilter.GaussianBlur(16)))
        d = ImageDraw.Draw(lay)
    kc = tuple(int(CREAM[i] + (AMBER[i] - CREAM[i]) * k) for i in range(3))
    d.ellipse((kx - 30, y - 30, kx + 30, y + 30), fill=kc + (255,))
    f = font("Inter-600.ttf", 24)
    if k < 0.5:                                         # the label under the knob is hidden by it
        d.text((x0 + pw - 46, y), "NIGHT", font=f, anchor="rm", fill=MUTED_D + (255,))
    else:
        d.text((x0 + 46, y), "DAY", font=f, anchor="lm", fill=MUTED_D + (255,))
    im = im.convert("RGBA")
    return Image.alpha_composite(im, lay).convert("RGB")


def spec_card(d, cx, cy, a, sq=False):
    """The carousel's two-column info card, in our colours: small-caps amber labels, cream values."""
    cols = [("WOOD", "Natural grain"), ("LIGHT", "20 W warm LED"), ("SIZE", "30 in")]
    fl, fv = font("Inter-600.ttf", 22 if sq else 24), font("Inter-600.ttf", 32 if sq else 34)
    ws = [max(fl.getlength(l), fv.getlength(v)) + 48 for l, v in cols]
    gap = 14
    x = cx - (sum(ws) + gap * (len(ws) - 1)) / 2
    hh = 118 if not sq else 108
    for (l, v), w in zip(cols, ws):
        d.rounded_rectangle((x, cy - hh / 2, x + w, cy + hh / 2), 20, fill=GLASS + (int(170 * a),),
                            outline=CREAM + (int(70 * a),), width=2)
        d.text((x + 24, cy - hh / 2 + 22), l, font=fl, fill=AMBER + (int(255 * a),), anchor="la")
        d.text((x + 24, cy + hh / 2 - 22), v, font=fv, fill=CREAM + (int(255 * a),), anchor="ld")
        x += w + gap


def headline(d, y, l1, l2, a, size, ink, accent, l2_italic=True):
    text(d, (W / 2, y), l1, font("Fraunces-600.ttf", size), alpha(ink, a))
    text(d, (W / 2, y + round(size * 1.08)), l2, font("Fraunces-500-i.ttf" if l2_italic else "Fraunces-600.ttf", size),
         alpha(accent, a))


def price_chip_dark(d, cx, cy, a, size=60):
    f = font("Inter-600.ttf", size)
    tw = f.getlength("₹3,999")
    pw, ph = tw + 64, size + 42
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), 26, fill=GROUND + (int(232 * a),))
    text(d, (cx, cy + 2), "₹3,999", f, alpha(AMBER, a))


def frame(cut, t, h):
    for sh, a, b in CUTS[cut]:
        if a <= t < b:
            break
    lt, secs = t - a, b - a
    sq = h != 1920
    ad = cut == "ad"
    if sh == "end":
        return end_card(lt, h, ad)
    im = footage(sh, lt, secs, h)
    # paid 9:16 text ends above y 1250; organic sits in the 230-1500 safe zone; 4:5 keeps a 60 px margin
    if sh is GRAIN_DAY or sh is HOLES_DAY:
        im = wash(im, 0.0, 0.42 if not sq else 0.5, 0.80)
        a1 = sstep((t - 0.05) / 0.12)
        y = 470 if not sq else 250

        def dr(d):
            headline(d, y, "By day,", "a piece of wood.", a1, 92 if not sq else 80, INK, INK)
            if ad:
                price_chip_dark(d, W / 2, y + (250 if not sq else 220), a1)
        im = layer(im, dr)
        return toggle(im, t, 300 if not sq else 104)
    if sh is MACRO_ON:
        im = switch_on(im, lt)
        im = scrim(im.transpose(Image.FLIP_TOP_BOTTOM), 0.62, 1.0, 0.55).transpose(Image.FLIP_TOP_BOTTOM)
        a1 = sstep((lt - 0.12) / 0.2)
        y = 470 if not sq else 250

        def dr(d):
            headline(d, y, "By night,", "this.", a1, 92 if not sq else 80, CREAM, AMBER)
        im = layer(im, dr)
        return toggle(im, t, 300 if not sq else 104)
    if sh is SLIDE_ON:
        im = scrim(im.transpose(Image.FLIP_TOP_BOTTOM), 0.55, 1.0, 0.6).transpose(Image.FLIP_TOP_BOTTOM)
        a1 = sstep((lt - 0.1) / 0.25)
        a2 = sstep((lt - 0.35) / 0.28)
        y = 430 if not sq else 230

        def dr(d):
            headline(d, y, "Warm light,", "through every hole.", a1, 84 if not sq else 74, CREAM, AMBER)
            spec_card(d, W / 2, y + (260 if not sq else 230), a2, sq)
        return layer(im, dr)
    if sh is OVER_ART:
        im = scrim(im, 0.48, 0.80 if not sq else 0.96, 0.72)
        a0 = sstep((lt - 0.08) / 0.22)
        a1 = sstep((lt - 0.18) / 0.26)
        by = (1290 if not ad else 1110) if not sq else 1080

        def dr(d):
            text(d, (W / 2, by - 112), "SAVE THIS STYLING TIP" if not ad else "3-YEAR WOOD WARRANTY",
                 font("Inter-600.ttf", 30), alpha(AMBER, a0))
            text(d, (W / 2, by - 30), "Hang it above your art.", font("Fraunces-600.ttf", 78 if not sq else 70),
                 alpha(CREAM, a1))
            text(d, (W / 2, by + 56), "The glow becomes the frame.", font("Fraunces-500-i.ttf", 60 if not sq else 54),
                 alpha(CREAM, a1))
        return layer(im, dr)


_end = {}


def end_card(lt, h, ad):
    """The light over the painting (8114's last frame, the sharpest settled one), dimmed from the cut."""
    sq = h != 1920
    key = (h, ad)
    if key not in _end:
        fr = clip_frames(OVER_ART["clip"], 2.40, 0.15)[1]
        im = Image.fromarray(grade(fr))
        if sq:
            im = im.crop((0, 60, W, 60 + h))
        elif ad:
            im = im.resize((round(W * 1.18), round(1920 * 1.18)), Image.LANCZOS)
            x = (im.width - W) // 2
            im = im.crop((x, 300, x + W, 300 + 1920))
        _end[key] = scrim(im, 0.28, 0.66 if not sq else 0.72, 0.86)
    base = _end[key]
    s = 1 + 0.035 * sstep(lt / 3.0)
    im = base.resize((round(W * s), round(h * s)), Image.LANCZOS)
    x = (im.width - W) // 2
    im = im.crop((x, 0, x + W, h))
    a1, a2 = sstep((lt - 0.05) / 0.3), sstep((lt - 0.3) / 0.3)
    y0 = (720 if ad else 960) if not sq else 830

    def dr(d):
        headline(d, y0, "Circular Hole", "Wall Light", a1, 88 if not sq else 78, CREAM, CREAM, l2_italic=False)
        if ad:
            text(d, (W / 2, y0 + 232), "₹3,999", font("Inter-600.ttf", 112 if not sq else 96), alpha(AMBER, a1))
            text(d, (W / 2, y0 + 334), "Save ₹100 prepaid with FLY100", font("Inter-400.ttf", 40 if not sq else 36),
                 alpha(MUTED_D, a2))
            text(d, (W / 2, y0 + 412), "Shop at nixwoods.com", font("Inter-600.ttf", 46 if not sq else 42),
                 alpha(CREAM, a2))
        else:
            text(d, (W / 2, y0 + 212), "30 in · real wood · warm LED", font("Inter-400.ttf", 42), alpha(MUTED_D, a2))
            text(d, (W / 2, y0 + 300), "nixwoods.com", font("Inter-600.ttf", 46), alpha(AMBER, a2))
    im = layer(im, dr)
    if not ad and not sq:
        lg = Image.open(os.path.join(os.path.dirname(os.path.dirname(HERE)), "assets", "logo.png")).convert("RGBA")
        lg = lg.resize((340, round(340 * lg.height / lg.width)), Image.LANCZOS)
        ink = Image.new("RGBA", lg.size, CREAM + (255,))
        ink.putalpha(lg.getchannel("A").point(lambda v: int(v * a2)))
        im.paste(ink, ((W - lg.width) // 2, y0 + 380), ink)
    return im


JOBS = {
    "social": ("social", 1920, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-day-night-reel-v2.mp4"),
    "ad916": ("ad", 1920, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-day-night-ad-9x16-v2.mp4"),
    "ad45": ("ad", 1350, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-day-night-ad-4x5-v2.mp4"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(JOBS) + ["ad"], default=None)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    keys = [k for k in JOBS if args.only in (None, k) or (args.only == "ad" and k.startswith("ad"))]
    os.makedirs(args.out, exist_ok=True)
    for k in keys:
        cut, h, name = JOBS[k]
        fn = lambda t, hh, c=cut: frame(c, t, hh)
        if args.frames:
            for s in args.frames.split(","):
                fn(float(s), h).save(os.path.join(args.out, f"{k}-{float(s):05.2f}.jpg"), quality=90)
            continue
        render_with(fn, h, os.path.join(args.out, name))
        print("wrote", name)


if __name__ == "__main__":
    main()
