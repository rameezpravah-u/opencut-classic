#!/usr/bin/env python3
"""NixLine "Follow the line" carousel — 6 slides, 4:5, one unbroken line across all of them.

From @yoursocialteam's Ddw6x4jnb9w ("These carousel trends are going viral right now", 17k likes,
19.8k comments). It lists seven interactive carousel formats; the point of all of them is that the
swipe itself is the entertainment, so people stay longer and Instagram pushes the post. Format 3,
"Follow the line", is a set of lines that run continuously across every slide from a start on slide
one to an answer on the last. For NixWoods the product IS a line of light, so the line is one warm
stroke that threads past each reason to buy and, on the last slide, runs up the teak block and
becomes the lit channel of the real lamp (clean 5 Aug shoot, AC4I9815, from Drive).

Drawn as one 6480 x 1350 panorama and cut into six 1080 x 1350 slides, so the line meets itself
exactly at every edge. Real photograph, no generated imagery; claims as on the .com PDP.

    python3 floor-reels/static/follow_line.py   # -> concepts/follow-line/NX-FOLLOW-LINE-01..06.jpg
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "assets")
PHOTO = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                     "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
OUT = os.path.join(ROOT, "floor-reels", "concepts", "follow-line")
SW, SH, N = 1080, 1350, 6
PW = SW * N
CREAM, PAPER = (246, 239, 228), (238, 228, 212)
TEAK, MUTED = (58, 38, 24), (124, 100, 82)
AMBER, CORE = (232, 162, 74), (255, 238, 210)
PILL = (240, 214, 178)
CHANNEL = (2875, 2934, 4631)         # NixLine channel in AC4I9815: x, top y, bottom y (measured)


def font(name, size):
    return ImageFont.truetype(os.path.join(A, name), size)


SERIF, ITAL = (lambda s: font("Fraunces-600.ttf", s)), (lambda s: font("Fraunces-500-i.ttf", s))
SANS, SANS_B = (lambda s: font("Inter-400.ttf", s)), (lambda s: font("Inter-600.ttf", s))
HAND = lambda s: font("GochiHand-400.ttf", s)


def photo():
    return ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")


def card(src, box, size, radius=34):
    """Crop box (x0, y0, x1, y1) in photo pixels, scaled to size, rounded corners, warm grade."""
    im = src.resize(size, Image.LANCZOS, box=box)
    a = np.asarray(im).astype(np.float32) / 255
    a = np.clip(a * np.array([1.05, 1.0, 0.9]), 0, 1) ** 1.05
    im = Image.fromarray((a * 255).astype(np.uint8))
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return im, m


def place_card(pano, img, mask, xy):
    sh = Image.new("L", pano.size, 0)
    sh.paste(mask, (xy[0] + 6, xy[1] + 14))
    shadow = Image.new("RGB", pano.size, (70, 48, 30))
    pano.paste(shadow, (0, 0), sh.filter(ImageFilter.GaussianBlur(22)).point(lambda p: int(p * 0.35)))
    pano.paste(img, xy, mask)


def catmull(pts, n=40):
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    out.append(pts[-1])
    return out


def glow_line(pano, path, width=12):
    """A warm-white core with an amber glow, like the lit channel it ends in."""
    halo = Image.new("L", pano.size, 0)
    ImageDraw.Draw(halo).line(path, fill=255, width=width * 5, joint="curve")
    pano.paste(Image.new("RGB", pano.size, AMBER), (0, 0), halo.filter(ImageFilter.GaussianBlur(22)).point(lambda p: int(p * 0.55)))
    mid = Image.new("L", pano.size, 0)
    ImageDraw.Draw(mid).line(path, fill=255, width=width + 8, joint="curve")
    pano.paste(Image.new("RGB", pano.size, AMBER), (0, 0), mid.filter(ImageFilter.GaussianBlur(3)))
    core = Image.new("L", pano.size, 0)
    ImageDraw.Draw(core).line(path, fill=255, width=width, joint="curve")
    pano.paste(Image.new("RGB", pano.size, CORE), (0, 0), core.filter(ImageFilter.GaussianBlur(1)))


def pill(d, x, y, s, f=None):
    f = f or SANS_B(34)
    w = f.getlength(s) + 56
    d.rounded_rectangle((x, y, x + w, y + 64), radius=32, fill=PILL)
    d.text((x + 28, y + 32), s, font=f, fill=TEAK, anchor="lm")
    return y + 64


def headline(d, x, y, lines, size, fill=TEAK):
    f = SERIF(size)
    for i, l in enumerate(lines):
        d.text((x, y + i * int(size * 1.02)), l, font=f, fill=fill)
    return y + len(lines) * int(size * 1.02)


def handle(d, k):
    d.text((k * SW + SW - 70, 92), "@nix_woods", font=SANS_B(28), fill=MUTED, anchor="ra")


def main():
    src = photo()
    pano = Image.new("RGB", (PW, SH), CREAM)
    rng = np.random.default_rng(3)
    paper = (np.asarray(pano).astype(np.float32) + rng.normal(0, 2.0, (SH, PW, 1))).clip(0, 255).astype(np.uint8)
    pano = Image.fromarray(paper)
    d = ImageDraw.Draw(pano)

    # --- slide 6 first: its photo fixes where the line must end -------------------------------------------
    x6 = 5 * SW
    cx0, cy0, cw = 2300, 2560, 1348                       # crop of AC4I9815 around the lamp
    cardw, cardh = 570, 1090
    ch = cw * cardh / cardw
    s6 = cardw / cw
    img6, m6 = card(src, (cx0, cy0, cx0 + cw, cy0 + ch), (cardw, cardh))
    p6 = (x6 + 470, 150)
    place_card(pano, img6, m6, p6)
    chan_x = p6[0] + (CHANNEL[0] - cx0) * s6 + 4     # +4: the bar leans 0.75°, so the channel base sits right of its centre line
    chan_bot = p6[1] + (CHANNEL[2] - cy0) * s6
    floor_y = p6[1] + (4985 - cy0) * s6                  # bottom of the teak block

    # --- the cards on slides 2, 3 and 5 ---------------------------------------------------------------------
    c2, m2 = card(src, (2690, 4560, 3070, 4950), (600, 616))            # the teak block, close
    place_card(pano, c2, m2, (1 * SW + 410, 560))
    c3box, c3size, c3xy = (2240, 2700, 3480, 5040), (480, 906), (2 * SW + 80, 300)   # the whole lamp
    c3, m3 = card(src, c3box, c3size)
    place_card(pano, c3, m3, c3xy)
    s3 = c3size[1] / (c3box[3] - c3box[1])
    lamp_top = c3xy[1] + (2900 - c3box[1]) * s3          # top of the teak bar
    lamp_bot = c3xy[1] + (4985 - c3box[1]) * s3          # bottom of its block
    c5, m5 = card(src, (1250, 2350, 3648, 5150), (560, 654))            # the corner it lights
    place_card(pano, c5, m5, (4 * SW + 70, 520))

    # --- the line -------------------------------------------------------------------------------------------
    s3_x = 2 * SW + 620                                                      # the ruler, beside the lamp card
    pts = [(170, 1000), (420, 1090), (760, 1080), (1080, 1180),               # 1
           (1260, 1270), (1700, 1265), (2160, 1250),                        # 2: under the card
           (2400, 1262), (s3_x, lamp_bot), (s3_x, lamp_top),                  # 3: up, measuring the lamp
           (s3_x + 110, 290), (3240, 330), (3300, 520), (3330, 860), (3420, 1150),   # 4: down the left side
           (3800, 1265), (4320, 1270),                                      # 4 -> 5
           (4760, 1268), (5150, 1230), (5400, floor_y + 4),                   # 5: under the card
           (chan_x - 120, floor_y + 4), (chan_x, floor_y - 30), (chan_x, chan_bot)]  # 6: into the lamp
    path = catmull(pts[:9]) + [pts[9]] + catmull(pts[9:20]) + [(chan_x - 120, floor_y + 4)]
    path += catmull([(chan_x - 120, floor_y + 4), (chan_x - 20, floor_y - 6), (chan_x, floor_y - 40)], 20)
    path += [(chan_x, chan_bot)]
    glow_line(pano, path)
    r = 22                                                                  # where it starts
    d.ellipse((170 - r, 1000 - r, 170 + r, 1000 + r), fill=CORE, outline=AMBER, width=6)

    # 30-inch measure ticks on slide 3
    for i in range(7):                                                       # 30-inch measure ticks, 5 in apart
        y = lamp_bot - (lamp_bot - lamp_top) * i / 6
        d.line((s3_x + 16, y, s3_x + 36, y), fill=TEAK, width=4)

    # --- type -----------------------------------------------------------------------------------------------
    lg = Image.open(os.path.join(A, "logo.png")).convert("RGBA")
    lg = lg.crop(lg.getbbox()); lg = lg.resize((150, round(lg.height * 150 / lg.width)), Image.LANCZOS)
    tint = Image.new("RGBA", lg.size, TEAK + (255,)); tint.putalpha(lg.getchannel("A"))
    pano.paste(tint, (70, 70), tint)

    # 1
    headline(d, 70, 300, ["Follow", "the line."], 170)
    d.text((80, 690), "it ends somewhere warm", font=HAND(64), fill=(176, 104, 40))
    pill(d, 70, 1180, "swipe  →")
    # 2
    pill(d, SW + 70, 150, "the wood")
    headline(d, SW + 70, 250, ["Solid", "Indian teak."], 104)
    d.text((SW + 70, 490), "No MDF. No veneer.", font=SANS(42), fill=MUTED)
    # 3
    x3 = 2 * SW
    pill(d, x3 + 80, 150, "the size")
    d.text((x3 + 700, 420), "30", font=SERIF(230), fill=TEAK)
    d.text((x3 + 706, 690), "inches", font=SERIF(86), fill=TEAK)
    for i, l in enumerate(["Upright on", "its own", "teak block."]):
        d.text((x3 + 706, 840 + i * 52), l, font=SANS(40), fill=MUTED)
    # 4
    x4 = 3 * SW
    pill(d, x4 + 330, 150, "the light")
    headline(d, x4 + 330, 250, ["Warm,", "not white."], 112)
    d.text((x4 + 330, 500), "2700–3000K LED.", font=SANS_B(44), fill=TEAK)
    d.text((x4 + 330, 556), "A tubelight is usually 6500K.", font=SANS(40), fill=MUTED)
    gx0, gx1, gy = x4 + 330, x4 + 1010, 760                              # cool -> warm scale
    for x in range(gx0, gx1):
        t = (x - gx0) / (gx1 - gx0)
        c = tuple(int(a + (b - a) * t) for a, b in zip((214, 228, 246), (255, 196, 120)))
        d.line((x, gy, x, gy + 70), fill=c)
    d.rounded_rectangle((gx0, gy, gx1, gy + 70), 18, outline=PAPER, width=2)
    d.text((gx0, gy + 96), "tubelight", font=SANS(36), fill=MUTED)
    d.text((gx1, gy + 96), "NixLine", font=SANS_B(36), fill=TEAK, anchor="ra")
    d.polygon([(gx1 - 60, gy - 14), (gx1 - 40, gy - 14), (gx1 - 50, gy - 2)], fill=TEAK)
    # 5
    x5 = 4 * SW
    pill(d, x5 + 680, 150, "the setup")
    headline(d, x5 + 680, 250, ["Plug in.", "Done."], 100)
    d.text((x5 + 680, 480), "No assembly.", font=SANS(42), fill=MUTED)
    d.text((x5 + 680, 534), "No electrician.", font=SANS(42), fill=MUTED)
    # 6
    headline(d, x6 + 70, 170, ["It ends", "in a warm", "corner."], 78)
    f, fs = SANS_B(120), SANS(48)
    d.text((x6 + 70, 600), "₹999", font=f, fill=(176, 104, 40))
    d.text((x6 + 74, 744), "₹1,599", font=fs, fill=MUTED)
    w = fs.getlength("₹1,599")
    d.line((x6 + 70, 772, x6 + 78 + w, 772), fill=MUTED, width=4)
    yy = 860
    for c in ["Cash on delivery", "Free delivery"]:
        cf = SANS_B(32); cw2 = cf.getlength(c) + 44
        d.rounded_rectangle((x6 + 70, yy, x6 + 70 + cw2, yy + 58), radius=29, outline=TEAK, width=2)
        d.text((x6 + 92, yy + 29), c, font=cf, fill=TEAK, anchor="lm")
        yy += 76
    d.text((x6 + 70, 1060), "nixwoods.com", font=SANS_B(40), fill=TEAK)
    for k in range(1, N):
        handle(d, k)

    os.makedirs(OUT, exist_ok=True)
    pano.save(os.path.join(OUT, "NX-FOLLOW-LINE-panorama.jpg"), quality=90)
    for k in range(N):
        sl = pano.crop((k * SW, 0, (k + 1) * SW, SH))
        sl.save(os.path.join(OUT, f"NX-FOLLOW-LINE-{k + 1:02d}.jpg"), quality=93)
    print(os.path.relpath(OUT, ROOT), f"{N} slides, line ends at x {chan_x - x6:.0f}, y {chan_bot:.0f} on slide 6")


if __name__ == "__main__":
    main()
