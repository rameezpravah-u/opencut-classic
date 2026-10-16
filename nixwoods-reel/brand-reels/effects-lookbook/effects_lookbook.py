"""NixWoods "9 lamps, 9 effects": a lookbook of effects from @tenfoldmarc's list (instagram.com/reel/Def_oOUzJeS,
"17 video effects Claude can create"), each on a different product and a different kind of material.

The owner asked on 16 Oct for a 15-20 s reel using several of them: "don't get stuck on one product or one type. Go
crazy." Every effect is built here in code on our own real photos and footage (no generated frames):

  0.00  orbit             Sculpted Glow cut out, six other lamps' photos circling it in 3D (clean 5 Aug shoot)
  3.15  cover story       NixLine floor lamp in front of its own magazine masthead (shoot photo + cut-out)
  4.87  paper cut         "HAND / MADE" in ransom-note paper, one letter a half-beat, over the CNC router (workshop)
  6.58  doodle boil       the Luma Pillar in smoke, hand-drawn doodles boiling around it (owner's styling clip)
  8.30  frame break       the Aurora on a wall in a photo frame; its light runs out past the frame (Aurora clip)
 10.01  glass type        frosted-glass letters over the Globe Edison (shoot photo)
 11.73  vertigo           the Minimalist floor lamp holds still while the room rushes in (shoot photo + cut-out)
 13.45  chart grow        the range's live prices, ₹999 to ₹9,999, drawn as a rising line (Shopify, 14 Oct)
 15.16  pull-back reveal  the Compact wall light pulls back into a phone on nixwoods.com, then the logo

Sections fall on the bars of music4-genz (starting 26.0 s into the track, so its drop lands at 1.43 s), with a
whoosh before each cut. Two cuts are written: the lookbook (a small "01 / 09 · orbit" tag on each, for choosing
effects) and a clean one to post.

    python3 brand-reels/effects-lookbook/make_masks.py      # once: the three lamp cut-outs
    python3 brand-reels/effects-lookbook/effects_lookbook.py
"""
import math, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "luma-styled"))
from made_well import encoder                                             # noqa: E402
import luma_shots as L                                                    # noqa: E402

FF = L.FF
W, H, FPS, SR = 1080, 1920, 30, 48000
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261016-nixwoods-range-effects-lookbook-v1"
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
WORKSHOP = os.path.join(ROOT, "brand-reels", "festive-ad-cuts", "src")
A = lambda p: os.path.join(ROOT, "assets", p)
CREAM, INK, AMBER, DUSK = (246, 239, 228), (58, 38, 24), (232, 162, 74), (49, 33, 26)
CORAL, MARIGOLD, GREEN, PLUM = (226, 92, 72), (240, 168, 52), (52, 132, 110), (128, 56, 96)

BAR = 4 * 0.4290                                       # music4-genz: 140 bpm, kicks every 0.2145 s
DROP = 1.433                                           # its drop (27.43 s in the track) with the track started at 26.0
M_IN = 26.0
CUTS = [0.0] + [DROP + BAR * (k + 1) for k in range(8)]
DUR = 17.6
NAMES = ["orbit", "cover story", "paper cut", "doodle boil", "frame break", "glass type", "vertigo", "chart grow",
         "pull-back reveal"]


def font(name, size):
    return ImageFont.truetype(A(name), size)


def ease(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def back(u, s=1.7):
    u = min(1.0, max(0.0, u)) - 1
    return 1 + (s + 1) * u ** 3 + s * u ** 2


_cache = {}


def photo(tag):
    """a shoot photo at half size (1824 x 2736), RGB float 0-255, with its mask if one was made"""
    if tag not in _cache:
        f = [x for x in os.listdir(SHOOT) if tag in x][0]
        im = cv2.imread(os.path.join(SHOOT, f))
        im = cv2.resize(im, (1824, 2736), interpolation=cv2.INTER_AREA)[..., ::-1].astype(np.float32)
        mp = os.path.join(HERE, "masks", f"{tag}.png")
        m = cv2.resize(cv2.imread(mp, 0), (1824, 2736), interpolation=cv2.INTER_AREA).astype(np.float32) / 255 \
            if os.path.exists(mp) else None
        _cache[tag] = (im, m)
    return _cache[tag]


def crop(img, cx, cy, w, out=(W, H)):
    """the region centred (cx, cy) in full-photo pixels, w wide, at the output's aspect, resized to out"""
    s = img.shape[1] / 3648
    ow, oh = out
    h = w * oh / ow
    x0, y0 = (cx - w / 2) * s, (cy - h / 2) * s
    M = np.float32([[ow / (w * s), 0, -x0 * ow / (w * s)], [0, oh / (h * s), -y0 * oh / (h * s)]])
    return cv2.warpAffine(img, M, (ow, oh), flags=cv2.INTER_AREA if w * s > ow else cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def over(base, rgb, a):
    a = a[..., None] if a.ndim == 2 else a
    return base * (1 - a) + rgb * a


def layer(draw_fn, blur=0):
    """an RGBA PIL layer drawn by draw_fn(ImageDraw, Image) -> (rgb, alpha) float arrays"""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(im), im)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    a = np.asarray(im, np.float32)
    return a[..., :3], a[..., 3] / 255


def text_layer(items, shadow=10):
    """items: (x, y, text, font, fill rgb, anchor). A soft shadow under all of them."""
    def sh(d, im):
        for x, y, t, f, c, an in items:
            d.text((x, y + 4), t, font=f, fill=(0, 0, 0, 120), anchor=an)
    def fg(d, im):
        for x, y, t, f, c, an in items:
            d.text((x, y), t, font=f, fill=tuple(c) + (255,), anchor=an)
    srgb, sa = layer(sh, shadow)
    frgb, fa = layer(fg)
    return (srgb, sa), (frgb, fa)


def put_text(base, tl):
    (srgb, sa), (frgb, fa) = tl
    return over(over(base, srgb, sa), frgb, fa)


def chip(base, label, y=1425, alpha=1.0):
    """the product name and price on a cream chip, as in the dial reel"""
    if alpha <= 0:
        return base
    name, price = label
    fn, fp = font("Inter-400.ttf", 32), font("Inter-600.ttf", 38)
    tw = fn.getlength(name + "   ") + fp.getlength(price)
    x = (W - tw) / 2
    def sh(d, im):
        d.rounded_rectangle((x - 32, y - 50, x + tw + 32, y + 24 + 6), 40, fill=(0, 0, 0, 80))
    def fg(d, im):
        d.rounded_rectangle((x - 32, y - 56, x + tw + 32, y + 24), 40, fill=CREAM + (238,))
        d.text((x, y), name, font=fn, fill=INK + (255,), anchor="ls")
        d.text((x + fn.getlength(name + "   "), y), price, font=fp, fill=INK + (255,), anchor="ls")
    srgb, sa = layer(sh, 12)
    frgb, fa = layer(fg)
    return over(over(base, srgb, sa * alpha), frgb, fa * alpha)


def dusk_bg(glow=(540, 1000), r=900, strength=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - glow[0]) ** 2 + (yy - glow[1]) ** 2) / r
    g = np.clip(1 - d, 0, 1) ** 2 * strength
    base = np.array(DUSK, np.float32) * 0.75
    return base + g[..., None] * (np.array([232, 162, 74], np.float32) - base) * 0.6


# ------------------------------------------------------------------------------------------------ 1 orbit
class Orbit:
    CARDS = [("AC4I9861", 2550, 4300, 1500), ("AC4I9652", 1900, 2050, 1700), ("AC4I9736", 1700, 1500, 2300),
             ("AC4I9658", 1800, 1950, 1900), ("AC4I9873", 2150, 4000, 1700), ("AC4I9777", 1550, 3200, 2300)]
    CW, CH = 290, 380

    def __init__(self):
        img, m = photo("AC4I9882")
        x0, y0, x1, y1 = 880, 900, 3150, 4830                     # the lamp's box, full-photo pixels
        s = 1824 / 3648
        sub = img[int(y0 * s):int(y1 * s), int(x0 * s):int(x1 * s)]
        sm = m[int(y0 * s):int(y1 * s), int(x0 * s):int(x1 * s)]
        h = 1060
        w = round(sub.shape[1] * h / sub.shape[0])
        self.lamp = cv2.resize(sub, (w, h), interpolation=cv2.INTER_AREA)
        self.lm = cv2.resize(sm, (w, h), interpolation=cv2.INTER_AREA)
        self.lpos = ((W - w) // 2, 1030 - h // 2)
        self.bg = dusk_bg((540, 1050), 950, 0.7)
        self.cards = []
        for tag, cx, cy, cw in self.CARDS:
            im, _ = photo(tag)
            c = crop(im, cx, cy, cw, (self.CW, self.CH))
            a = np.zeros((self.CH, self.CW), np.float32)
            cv2.rectangle(a, (0, 0), (self.CW - 1, self.CH - 1), 1.0, -1)
            rr = np.zeros_like(a)
            cv2.rectangle(rr, (8, 8), (self.CW - 9, self.CH - 9), 1.0, -1)
            c = np.where(rr[..., None] > 0, c, 246.0)                  # a white border, like a print
            self.cards.append((c, a))
        self.hook = text_layer([(540, 250, "9 ways to look", font("Fraunces-600.ttf", 92), CREAM, "ms"),
                                (540, 350, "at a lamp.", font("Fraunces-500-i.ttf", 72), AMBER, "ms")])

    def card_at(self, base, i, t, behind):
        n = len(self.cards)
        spin = 0.45 * t + (0.35 * max(0.0, t - DROP)) ** 1.0               # it speeds up on the drop
        ang = 2 * math.pi * (i / n + spin / 1.0 * 0.5)
        rad = ease(t / 1.1)
        x = 540 + 500 * rad * math.cos(ang)
        y = 1300 + 170 * rad * math.sin(ang)
        depth = math.sin(ang)
        if (depth < 0) != behind:
            return base
        sc = (0.55 + 0.5 * (depth + 1) / 2) * (0.4 + 0.6 * rad)
        c, a = self.cards[i]
        cw, ch = max(4, round(self.CW * sc)), max(4, round(self.CH * sc))
        tilt = -8 * math.cos(ang)
        M = cv2.getRotationMatrix2D((cw / 2, ch / 2), tilt, 1.0)
        big = cv2.resize(c, (cw, ch))
        ba = cv2.resize(a, (cw, ch))
        pad = int(0.2 * max(cw, ch))
        M[0, 2] += pad
        M[1, 2] += pad
        big = cv2.warpAffine(big, M, (cw + 2 * pad, ch + 2 * pad))
        ba = cv2.warpAffine(ba, M, (cw + 2 * pad, ch + 2 * pad))
        dim = 0.55 + 0.45 * (depth + 1) / 2                               # far cards in shadow
        x0, y0 = int(x - big.shape[1] / 2), int(y - big.shape[0] / 2)
        return paste(base, big * dim, ba, x0, y0, shadow=True)

    def frame(self, t, d):
        f = self.bg.copy()
        for i in range(len(self.cards)):
            f = self.card_at(f, i, t, True)
        x0, y0 = self.lpos
        f = paste(f, self.lamp * (0.9 + 0.1 * sstep((t - DROP) / 0.3)), self.lm, x0, y0)
        for i in range(len(self.cards)):
            f = self.card_at(f, i, t, False)
        f = put_text(f, self.hook)
        return chip(f, ("Sculpted Glow", "₹9,999"), y=1640, alpha=sstep((t - DROP) / 0.25))


def paste(base, rgb, a, x0, y0, shadow=False):
    """paste rgb/alpha at (x0, y0), clipped to the frame; optional soft drop shadow"""
    h, w = a.shape
    xs, ys = max(0, x0), max(0, y0)
    xe, ye = min(W, x0 + w), min(H, y0 + h)
    if xe <= xs or ye <= ys:
        return base
    sub_a = a[ys - y0:ye - y0, xs - x0:xe - x0]
    sub = rgb[ys - y0:ye - y0, xs - x0:xe - x0]
    if shadow:
        sa = np.zeros((H, W), np.float32)
        sa[min(H, ys + 14):min(H, ye + 14), xs:xe] = sub_a[:max(0, min(H, ye + 14) - min(H, ys + 14))]
        sa = cv2.GaussianBlur(sa, (0, 0), 14) * 0.5
        base = base * (1 - sa[..., None])
    out = base.copy()
    out[ys:ye, xs:xe] = over(base[ys:ye, xs:xe], sub, sub_a)
    return out


# ------------------------------------------------------------------------------------------------ 2 cover story
class Cover:
    def __init__(self):
        img, m = photo("AC4I9815")
        self.args = (2600, 3880, 1700)
        self.img, self.m = img, m
        self.mast = font("Playfair_Display-700.ttf", 215)

    def frame(self, t, d):
        cx, cy, w = self.args
        w = w * (1 - 0.03 * t / d)
        bg = crop(self.img, cx, cy, w)
        bg = np.clip((bg - 128) * 1.06 + 128, 0, 255)
        lm = crop(self.m[..., None].repeat(3, 2) * 255, cx, cy, w)[..., 0] / 255
        u = ease(t / 0.35)
        def mast(dr, im):
            dr.text((540, 520 - 160 * (1 - u)), "NIXLINE", font=self.mast, fill=CREAM + (int(255 * u),), anchor="ms")
        mrgb, ma = layer(mast)
        def msh(dr, im):
            dr.text((540, 528 - 160 * (1 - u)), "NIXLINE", font=self.mast, fill=(0, 0, 0, int(110 * u)), anchor="ms")
        srgb, sa = layer(msh, 14)
        f = over(over(bg, srgb, sa), mrgb, ma)
        f = over(f, bg, lm)                                              # the lamp in front of its own masthead
        lines = [(0.30, (70, 640, "ISSUE 01 · OCTOBER 2026", font("Inter-600.ttf", 26), CREAM, "ls")),
                 (0.43, (70, 760, "₹999", font("Fraunces-600.ttf", 120), AMBER, "ls")),
                 (0.64, (74, 830, "SOLID TEAK.", font("Archivo_Black-400.ttf", 46), CREAM, "ls")),
                 (0.86, (74, 892, "PLUG IN. DONE.", font("Archivo_Black-400.ttf", 46), CREAM, "ls")),
                 (1.07, (74, 1010, "The 30-inch lamp", font("Fraunces-500-i.ttf", 44), CREAM, "ls")),
                 (1.07, (74, 1062, "that fixes a corner", font("Fraunces-500-i.ttf", 44), CREAM, "ls"))]
        on = [it for at, it in lines if t >= at]
        if on:
            f = put_text(f, text_layer(on, 8))
        # a little barcode, bottom left, like a newsstand cover
        if t >= 1.2:
            def bc(dr, im):
                rng = np.random.default_rng(3)
                x = 74
                dr.rectangle((60, 1340, 300, 1500), fill=(250, 250, 250, 235))
                while x < 286:
                    wdt = int(rng.integers(2, 7))
                    dr.rectangle((x, 1356, x + wdt, 1462), fill=(20, 20, 20, 255))
                    x += wdt + int(rng.integers(2, 6))
                dr.text((180, 1490), "NIXWOODS.COM", font=font("Inter-600.ttf", 18), fill=(20, 20, 20, 255),
                        anchor="ms")
            brgb, ba = layer(bc)
            f = over(f, brgb, ba)
        return f


# ------------------------------------------------------------------------------------------------ 3 paper cut
class PaperCut:
    FONTS = ["Archivo_Black-400.ttf", "Fraunces-600.ttf", "Bebas_Neue-400.ttf", "Playfair_Display-700.ttf",
             "Space_Grotesk-700.ttf", "Ultra-400.ttf", "PermanentMarker-400.ttf", "DM_Sans-600.ttf"]
    PAPERS = [CREAM, MARIGOLD, (20, 20, 20), CORAL, (250, 250, 250), GREEN, AMBER, PLUM]

    def __init__(self, d):
        n = round(d * FPS)
        cap = cv2.VideoCapture(os.path.join(WORKSHOP, "IMG_7698.mov"))
        fr = []
        while len(fr) < n:
            ok, im = cap.read()
            if not ok:
                break
            fr.append(im)
        cap.release()
        out = []
        for im in fr:
            h, w = im.shape[:2]
            s = max(W / w, H / h)
            im = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_CUBIC)
            y0, x0 = (im.shape[0] - H) // 2, (im.shape[1] - W) // 2
            im = im[y0:y0 + H, x0:x0 + W, ::-1].astype(np.float32)
            g = im @ np.array([0.2126, 0.7152, 0.0722], np.float32)
            out.append(np.clip(0.55 * im + 0.45 * g[..., None], 0, 255) * 0.62)      # muted so the paper pops
        self.fr = out + [out[-1]] * (n - len(out))
        rng = np.random.default_rng(11)
        self.pieces = []
        for i, ch in enumerate("HANDMADE"):
            row, col = divmod(i, 4)
            fnt = font(self.FONTS[i], 210 if self.FONTS[i] != "Bebas_Neue-400.ttf" else 250)
            paper = self.PAPERS[i]
            ink = (20, 20, 20) if sum(paper) > 380 else CREAM
            cx = 175 + col * 243 + rng.integers(-14, 14)
            cy = 780 + row * 330 + rng.integers(-24, 24)
            rot = float(rng.uniform(-11, 11))
            self.pieces.append(self.piece(ch, fnt, paper, ink, rot, rng, cx, cy))
        self.strip = self.piece("in Uttar Pradesh", font("DM_Sans-600.ttf", 52), CREAM, (20, 20, 20), -3, rng,
                                540, 1250, pad=(30, 18))

    def piece(self, ch, fnt, paper, ink, rot, rng, cx, cy, pad=(26, 22)):
        """one letter on a torn scrap of paper: jagged edge, drop shadow, slight rotation"""
        b = fnt.getbbox(ch)
        tw, th = b[2] - b[0], b[3] - b[1]
        pw, ph = tw + 2 * pad[0], th + 2 * pad[1]
        S = 2
        im = Image.new("RGBA", ((pw + 40) * S, (ph + 40) * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        pts = []
        for k in range(48):                                              # a jagged outline round the scrap
            u = k / 48
            if u < 0.25:
                x, y = 20 + pw * u / 0.25, 20
            elif u < 0.5:
                x, y = 20 + pw, 20 + ph * (u - 0.25) / 0.25
            elif u < 0.75:
                x, y = 20 + pw * (1 - (u - 0.5) / 0.25), 20 + ph
            else:
                x, y = 20, 20 + ph * (1 - (u - 0.75) / 0.25)
            pts.append(((x + rng.uniform(-5, 5)) * S, (y + rng.uniform(-5, 5)) * S))
        d.polygon(pts, fill=tuple(paper) + (255,))
        bf = fnt.font_variant(size=fnt.size * S)
        d.text(((20 + pw / 2) * S, (20 + ph / 2) * S), ch, font=bf, fill=tuple(ink) + (255,), anchor="mm")
        im = im.resize((pw + 40, ph + 40), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC, expand=True)
        a = np.asarray(im, np.float32)
        return a[..., :3], a[..., 3] / 255, cx, cy

    def frame(self, t, d):
        f = self.fr[min(len(self.fr) - 1, round(t * FPS))].copy()
        step = 0.2145
        for i, (rgb, a, cx, cy) in enumerate(self.pieces):
            t0 = i * step
            if t < t0:
                continue
            u = back((t - t0) / 0.12, 2.4)
            sc = 0.6 + 0.4 * u
            h, w = a.shape
            r2 = cv2.resize(rgb, (max(2, int(w * sc)), max(2, int(h * sc))))
            a2 = cv2.resize(a, (max(2, int(w * sc)), max(2, int(h * sc))))
            f = paste(f, r2, a2, int(cx - a2.shape[1] / 2), int(cy - a2.shape[0] / 2), shadow=True)
        if t >= 8 * step - 0.1:
            rgb, a, cx, cy = self.strip
            f = paste(f, rgb, a * sstep((t - 8 * step + 0.1) / 0.1), int(cx - a.shape[1] / 2),
                      int(cy - a.shape[0] / 2), shadow=True)
        return f


# ------------------------------------------------------------------------------------------------ 4 doodle boil
class Doodle:
    def __init__(self, d):
        self.fr = [f.astype(np.float32) for f in L.shot("smoke-b", d)]
        self.hand = font("GochiHand-400.ttf", 76)
        self.hand2 = font("GochiHand-400.ttf", 60)

    def strokes(self, rng, j):
        """every doodle as polylines, re-jittered each boil step j (the 'boil')"""
        def jit(pts, a=5.0):
            r = np.random.default_rng(1000 + j)
            return [(x + r.uniform(-a, a), y + r.uniform(-a, a)) for x, y in pts]
        out = []
        def star(cx, cy, r):
            pts = []
            for k in range(11):
                rr = r if k % 2 == 0 else r * 0.45
                an = -math.pi / 2 + k * math.pi / 5
                pts.append((cx + rr * math.cos(an), cy + rr * math.sin(an)))
            return pts
        out.append((jit(star(250, 520, 60)), MARIGOLD, 7))
        out.append((jit(star(860, 400, 44)), CREAM, 6))
        out.append((jit(star(830, 1180, 34)), MARIGOLD, 6))
        heart = [(180 + 46 * 16 * math.sin(a) ** 3 / 16, 1040 - 46 * (13 * math.cos(a) - 5 * math.cos(2 * a)
                  - 2 * math.cos(3 * a) - math.cos(4 * a)) / 16) for a in np.linspace(0, 2 * math.pi, 40)]
        out.append((jit(heart), CORAL, 7))
        ring = [(540 + 250 * math.cos(a) + 12 * math.sin(5 * a), 930 + 520 * math.sin(a)) for a in
                np.linspace(0.3, 2 * math.pi + 0.6, 70)]
        out.append((jit(ring, 7), CREAM, 6))
        arrow = [(860, 700), (800, 760), (730, 820), (690, 850)]
        out.append((jit(arrow), CREAM, 7))
        out.append((jit([(690, 850), (712, 806)]), CREAM, 7))
        out.append((jit([(690, 850), (738, 852)]), CREAM, 7))
        for k in range(3):                                               # sparkle ticks round the lamp's head
            an = -2.2 + 0.55 * k
            out.append((jit([(540 + 150 * math.cos(an), 470 + 150 * math.sin(an)),
                             (540 + 210 * math.cos(an), 470 + 210 * math.sin(an))]), MARIGOLD, 7))
        return out

    def frame(self, t, d):
        f = self.fr[min(len(self.fr) - 1, round(t * FPS))]
        j = int(t * FPS) // 3                                             # redraw every 3 frames: the boil
        reveal = ease(t / 0.45)
        rng = np.random.default_rng(j)
        def dr(dd, im):
            for pts, col, wdt in self.strokes(rng, j):
                n = max(2, int(len(pts) * reveal))
                dd.line(pts[:n], fill=tuple(col) + (255,), width=wdt, joint="curve")
            if t > 0.3:
                r = np.random.default_rng(j + 7)
                dd.text((870 + r.uniform(-3, 3), 640 + r.uniform(-3, 3)), "₹1,599!", font=self.hand,
                        fill=MARIGOLD + (255,), anchor="ms")
            if t > 0.55:
                r = np.random.default_rng(j + 9)
                dd.text((540 + r.uniform(-3, 3), 1560 + r.uniform(-3, 3)), "cozy mode: ON", font=self.hand2,
                        fill=CREAM + (255,), anchor="ms")
        rgb, a = layer(dr)
        f = over(f, np.zeros_like(rgb), cv2.GaussianBlur(a, (0, 0), 4) * 0.45)
        f = over(f, rgb, a)
        return chip(f, ("Luma Pillar", "₹1,599"), y=1460)


# ------------------------------------------------------------------------------------------------ 5 frame break
class FrameBreak:
    FW, FH = 760, 980                                                    # the picture inside the frame

    def __init__(self, d):
        n = round(d * FPS)
        src = os.path.join(WORKSHOP, "aurora-dimming-9x16.mp4")
        raw = subprocess.run([FF, "-v", "error", "-ss", "0.55", "-i", src, "-t", "0.85", "-vf",
                              f"setpts={d / 0.85:.4f}*PTS,minterpolate=fps=30:mi_mode=blend,"
                              f"scale={self.FW}:-2,crop={self.FW}:{self.FH}:0:0", "-frames:v", str(n),
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, self.FH, self.FW, 3).astype(np.float32)
        self.fr = list(fr) + [fr[-1]] * max(0, n - len(fr))
        g = self.fr[len(self.fr) // 2] @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        rows = g.mean(1)
        self.by = int(np.argmax(rows))                                   # the lit bar's row in the picture
        cols = np.where(g[max(0, self.by - 3):self.by + 4].mean(0) > 0.6 * g[self.by].max())[0]
        self.bx0, self.bx1 = int(cols.min()), int(cols.max())
        self.bg = dusk_bg((540, 760), 1000, 0.25)

    def frame(self, t, d):
        f = self.bg.copy()
        pic = self.fr[min(len(self.fr) - 1, round(t * FPS))]
        fx0, fy0 = (W - self.FW) // 2, 380
        border = 34
        # the white frame, then the picture
        frame_a = np.zeros((H, W), np.float32)
        cv2.rectangle(frame_a, (fx0 - border, fy0 - border), (fx0 + self.FW + border, fy0 + self.FH + 120), 1, -1)
        sh = cv2.GaussianBlur(np.roll(frame_a, 18, 0), (0, 0), 22) * 0.55
        f = f * (1 - sh[..., None])
        f = over(f, np.full_like(f, 244.0), frame_a)
        f[fy0:fy0 + self.FH, fx0:fx0 + self.FW] = pic
        # the light runs out of the frame, along its own line, and washes the wall round the frame
        u = ease((t - 0.25) / 0.9)
        y = fy0 + self.by
        x0 = fx0 + self.bx0 - (fx0 + self.bx0 + 40) * u
        x1 = fx0 + self.bx1 + (W - fx0 - self.bx1 + 40) * u
        core = np.zeros((H, W), np.float32)
        cv2.line(core, (int(x0), y), (int(x1), y), 1.0, 12, cv2.LINE_AA)
        glow = cv2.GaussianBlur(core, (0, 0), 26) * 5 + cv2.GaussianBlur(core, (0, 0), 110) * 14
        warm = np.array([255, 214, 160], np.float32)
        f = f + glow[..., None] * warm * 0.7 * u
        f = over(f, np.array([255, 246, 228], np.float32) * np.ones_like(f), core * u)
        f = np.clip(f, 0, 255)
        cap = text_layer([(540, fy0 + self.FH + 86, "light doesn't stay in the frame", font("Fraunces-500-i.ttf", 42),
                           INK, "ms")], 0)
        f = put_text(f, ((np.zeros((H, W, 3), np.float32), np.zeros((H, W), np.float32)), cap[1]))
        return chip(f, ("Aurora wall light", "from ₹1,999"), y=1600)


# ------------------------------------------------------------------------------------------------ 6 glass type
class Glass:
    def __init__(self):
        img, _ = photo("AC4I9873")
        self.img = img
        self.word = "warm"
        self.f = font("Archivo_Black-400.ttf", 300)

    def frame(self, t, d):
        bg = crop(self.img, 2050, 3500, 2500 * (1 - 0.03 * t / d))
        bg = np.clip((bg - 128) * 1.05 + 128, 0, 255)
        u = ease(t / 0.4)
        y = 760 + 120 * (1 - u)
        def m(dr, im):
            dr.text((540, y), self.word, font=self.f, fill=(255, 255, 255, 255), anchor="ms")
        _, a = layer(m)
        blur = cv2.GaussianBlur(bg, (0, 0), 22)
        frost = np.clip(blur * 1.12 + np.array([40, 26, 8], np.float32), 0, 255)   # frosted: blurred, lifted, warm
        # refraction: the frosted fill is sampled a little off, like thick glass
        frost = np.roll(frost, (14, -10), (0, 1))
        edge = np.clip(a - cv2.erode(a, np.ones((5, 5), np.uint8)), 0, 1)
        hi = np.clip(cv2.GaussianBlur(edge, (0, 0), 1.2) * 1.6, 0, 1)
        sh = cv2.GaussianBlur(np.roll(a, 16, 0), (0, 0), 16) * 0.35
        f = bg * (1 - sh[..., None])
        f = over(f, frost, a * u)
        f = over(f, np.full_like(f, 255.0), np.clip(hi * 1.3, 0, 1) * u)
        sheen = np.clip(1 - np.abs(np.arange(W)[None, :] - (-200 + 1500 * ((t - 0.4) / 1.0))) / 140, 0, 1)
        f = over(f, np.full_like(f, 255.0), a * sheen * 0.35 * u)
        return chip(f, ("Globe Edison table lamp", "₹2,999"), y=1500)


# ------------------------------------------------------------------------------------------------ 7 vertigo
class Vertigo:
    def __init__(self):
        img, m = photo("AC4I9776")
        self.cx, self.cy, self.w = 1600, 3150, 2600
        self.img, self.m = img, m
        small = cv2.resize(img, (912, 1368)).astype(np.uint8)
        ms = (cv2.resize(m, (912, 1368)) > 0.2).astype(np.uint8) * 255
        ms = cv2.dilate(ms, np.ones((9, 9), np.uint8))
        fill = cv2.inpaint(small, ms, 9, cv2.INPAINT_TELEA).astype(np.float32)
        fill = cv2.resize(fill, (1824, 2736), interpolation=cv2.INTER_CUBIC)
        mb = cv2.resize(ms, (1824, 2736)).astype(np.float32)[..., None] / 255
        mb = cv2.GaussianBlur(mb, (0, 0), 4)[..., None]
        self.clean = img * (1 - mb) + fill * mb                         # the room with the lamp taken out

    def frame(self, t, d):
        u = sstep(t / d)
        z = 1 + 0.9 * u                                                   # the room rushes in…
        bg = crop(self.clean, self.cx, self.cy - 120 * u, self.w / z)
        k = int(1 + 10 * math.sin(math.pi * u))                           # a little zoom blur mid-move
        if k > 2:
            M = cv2.getRotationMatrix2D((540, 1000), 0, 1.02)
            bg = 0.6 * bg + 0.4 * cv2.warpAffine(bg, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
        lamp = crop(self.img, self.cx, self.cy, self.w)                   # …while the lamp holds still
        lm = crop(self.m[..., None].repeat(3, 2) * 255, self.cx, self.cy, self.w)[..., 0] / 255
        f = over(bg, lamp, lm)
        return chip(f, ("Minimalist floor lamp", "from ₹6,999"), y=1500)


# ------------------------------------------------------------------------------------------------ 8 chart grow
class Chart:
    PRICES = [("AC4I9815", 999, (2790, 3800, 1700)), ("AC4I9658", 1799, (1800, 1950, 2300)),
              ("AC4I9861", 2499, (2550, 4350, 1300)), ("AC4I9652", 2500, (1900, 2050, 2100)),
              ("AC4I9873", 2999, (2150, 4050, 1600)), ("AC4I9629", 4999, (1800, 1300, 2600)),
              ("AC4I9776", 6999, (1550, 3200, 2900)), ("AC4I9736", 7999, (1700, 1450, 2000)),
              ("AC4I9882", 9999, (2000, 2900, 3000))]

    def __init__(self):
        self.bg = dusk_bg((540, 1100), 1100, 0.35)
        self.pts = []
        for i, (tag, p, (cx, cy, dd)) in enumerate(self.PRICES):
            x = 120 + i * 105
            y = 1420 - (math.log(p) - math.log(999)) / (math.log(9999) - math.log(999)) * 760
            im, _ = photo(tag)
            th = crop(im, cx, cy, dd, (124, 124))
            a = np.zeros((124, 124), np.float32)
            cv2.circle(a, (62, 62), 60, 1.0, -1, cv2.LINE_AA)
            self.pts.append((x, y, p, th, a))
        self.title = text_layer([(540, 330, "A light for every budget", font("Fraunces-600.ttf", 70), CREAM, "ms"),
                                 (540, 410, "solid wood, ₹999 to ₹9,999", font("Fraunces-500-i.ttf", 46), AMBER,
                                  "ms")])

    def frame(self, t, d):
        f = put_text(self.bg.copy(), self.title)
        u = ease(t / 1.15)
        xs = [p[0] for p in self.pts]
        xe = xs[0] + (xs[-1] - xs[0]) * u
        line = np.zeros((H, W), np.float32)
        poly = []
        for (x, y, *_), (x2, y2, *_) in zip(self.pts, self.pts[1:]):
            if x > xe:
                break
            if x2 > xe:
                y2 = y + (y2 - y) * (xe - x) / (x2 - x)
                x2 = xe
            poly.append(((int(x), int(y)), (int(x2), int(y2))))
        for a, b in poly:
            cv2.line(line, a, b, 1.0, 9, cv2.LINE_AA)
        glow = cv2.GaussianBlur(line, (0, 0), 14) * 1.5
        f = np.clip(f + glow[..., None] * np.array([232, 162, 74], np.float32) * 0.6, 0, 255)
        f = over(f, np.array(AMBER, np.float32) * np.ones_like(f), line)
        for i, (x, y, p, th, a) in enumerate(self.pts):
            if x > xe + 1:
                break
            s = back((t - i * 1.15 / 8) / 0.18)
            n = max(4, int(124 * s))
            up = i % 2 == 0                                                 # photos alternate above and below
            f = paste(f, cv2.resize(th, (n, n)), cv2.resize(a, (n, n)), int(x - n / 2),
                      int(y - n / 2) + (-110 if up else 110), shadow=True)
            lab = f"₹{p:,}"
            f = put_text(f, text_layer([(x, y + 4, "●", font("Inter-600.ttf", 26), CREAM, "mm"),
                                        (x, y - 190 if up else y + 210, lab, font("Inter-600.ttf", 30), CREAM,
                                         "ms")], 4))
        return f


# ------------------------------------------------------------------------------------------------ 9 pull-back
class PullBack:
    PW, PH = 560, 1180                                                   # the phone's screen

    def __init__(self):
        img, _ = photo("AC4I9629")
        self.full = crop(img, 1824, 2736, 3078)
        self.bg = dusk_bg((540, 900), 1100, 0.45)
        lg = Image.open(A("logo.png")).convert("RGBA")
        lg = lg.resize((240, round(240 * lg.height / lg.width)), Image.LANCZOS)
        tint = Image.new("RGBA", lg.size, CREAM + (255,))
        tint.putalpha(lg.getchannel("A"))
        a = np.asarray(tint, np.float32)
        self.logo = (a[..., :3], a[..., 3] / 255)

    def screen(self):
        """the phone screen: nixwoods.com in a browser, the photo, the name and price"""
        sw, sh = self.PW, self.PH
        s = np.full((sh, sw, 3), 250.0, np.float32)
        img_h = round(sw * 16 / 9 * 0.62)
        s[150:150 + img_h] = cv2.resize(self.full, (sw, img_h), interpolation=cv2.INTER_AREA)[:, :, :] \
            if img_h <= sh - 150 else s[150:150 + img_h]
        im = Image.fromarray(s.astype(np.uint8))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((24, 70, sw - 24, 124), 27, fill=(232, 232, 232))
        d.text((sw / 2, 106), "nixwoods.com", font=font("Inter-600.ttf", 26), fill=(40, 40, 40), anchor="ms")
        y = 150 + img_h + 56
        d.text((30, y), "Compact wall light", font=font("Fraunces-600.ttf", 40), fill=INK, anchor="ls")
        d.text((30, y + 54), "from ₹4,999", font=font("Inter-600.ttf", 34), fill=INK, anchor="ls")
        d.rounded_rectangle((30, y + 86, sw - 30, y + 150), 32, fill=INK)
        d.text((sw / 2, y + 128), "See it on nixwoods.com", font=font("Inter-600.ttf", 28), fill=CREAM, anchor="ms")
        return np.asarray(im, np.float32)

    def frame(self, t, d):
        if not hasattr(self, "scr"):
            self.scr = self.screen()
        u = ease((t - 0.15) / 0.9)
        # the full-screen photo shrinks into the phone's picture slot
        sx, sy = (W - self.PW) // 2, 300
        img_h = round(self.PW * 16 / 9 * 0.62)
        tgt = (sx, sy + 150, self.PW, img_h)
        x0 = 0 + (tgt[0] - 0) * u
        y0 = 0 + (tgt[1] - 0) * u
        w = W + (tgt[2] - W) * u
        h = H + (tgt[3] - H) * u
        f = self.bg.copy()
        if u > 0.02:
            # the phone body and screen fade up as the picture lands
            body = np.zeros((H, W), np.float32)
            cv2.rectangle(body, (sx - 22, sy - 22), (sx + self.PW + 22, sy + self.PH + 22), 1.0, -1)
            body = cv2.GaussianBlur(body, (0, 0), 2)
            shd = cv2.GaussianBlur(np.roll(body, 30, 0), (0, 0), 30) * 0.6 * u
            f = f * (1 - shd[..., None])
            f = over(f, np.full_like(f, 22.0), body * u)
            f[sy:sy + self.PH, sx:sx + self.PW] = over(f[sy:sy + self.PH, sx:sx + self.PW], self.scr,
                                                       np.full((self.PH, self.PW), u, np.float32))
        pic = cv2.resize(self.full, (max(2, int(w)), max(2, int(h * 1.0))), interpolation=cv2.INTER_AREA)
        if u < 1:
            src_h = int(H * (h / H))
            pic = cv2.resize(self.full, (max(2, int(w)), max(2, int(w * H / W))), interpolation=cv2.INTER_AREA)
            off = (pic.shape[0] - int(h)) // 2
            pic = pic[off:off + int(h)]
        f = paste(f, pic, np.ones(pic.shape[:2], np.float32), int(x0), int(y0))
        lu = sstep((t - 1.05) / 0.35)
        if lu > 0:
            lrgb, la = self.logo
            f = paste(f, lrgb, la * lu, (W - la.shape[1]) // 2, sy + self.PH + 60)
        return f


def tag_layer(i):
    def dr(d, im):
        t = f"{i + 1:02d} / 09 · {NAMES[i]}"
        fnt = font("Space_Grotesk-700.ttf", 30)
        tw = fnt.getlength(t)
        d.rounded_rectangle((48, 1724, 48 + tw + 44, 1780), 28, fill=(20, 20, 20, 170))       # low, clear of the
        d.text((70, 1763), t, font=fnt, fill=(241, 248, 17, 255), anchor="ls")                 # content
    return layer(dr)


def soundtrack():
    n = int(DUR * SR)
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{M_IN:.3f}", "-i", os.path.join(ROOT, "aurora-reels", "audio",
                          "music4-genz.mp3"), "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    m = np.zeros((n, 2), np.float32)
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    m[:len(a)] = a
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(ROOT, "aurora-reels", "audio", "sfx-whoosh.mp3"),
                          "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    wh = np.frombuffer(raw, np.float32).reshape(-1, 2)
    pk = int(np.argmax(np.abs(wh).sum(1)))
    wh = wh * (0.35 / (np.abs(wh).max() + 1e-9))
    for c in CUTS[2:]:                                                   # a whoosh peaking on each cut
        i = int(c * SR) - pk
        j0, j1 = max(0, i), min(n, i + len(wh))
        m[j0:j1] += wh[j0 - i:j1 - i]
    t = np.arange(n) / SR
    m *= np.clip((DUR - t) / 0.9, 0, 1)[:, None]
    return m * 0.89 / (np.abs(m).max() + 1e-9)


def main():
    os.makedirs(OUT, exist_ok=True)
    durs = [b - a for a, b in zip(CUTS, CUTS[1:] + [DUR])]
    segs = [Orbit(), Cover(), PaperCut(durs[2]), Doodle(durs[3]), FrameBreak(durs[4]), Glass(), Vertigo(), Chart(),
            PullBack()]
    tags = [tag_layer(i) for i in range(9)]
    wp = os.path.join(OUT, "_a.wav")
    with wave.open(wp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((soundtrack() * 32767).astype(np.int16).tobytes())
    encs = [encoder(wp, os.path.join(OUT, f"{NAME}.mp4")), encoder(wp, os.path.join(OUT, f"{NAME}-tagged.mp4"))]
    picks, keep = {round((c + 0.75) * FPS) for c in CUTS}, {}
    n = round(DUR * FPS)
    for i in range(n):
        t = i / FPS
        k = max(j for j, c in enumerate(CUTS) if c <= t + 1e-6)
        f = np.clip(segs[k].frame(t - CUTS[k], durs[k]), 0, 255)
        clean = (f + 0.5).astype(np.uint8)
        trgb, ta = tags[k]
        tagged = (np.clip(over(f, trgb, ta), 0, 255) + 0.5).astype(np.uint8)
        encs[0].stdin.write(clean.tobytes())
        encs[1].stdin.write(tagged.tobytes())
        if i in picks:
            keep[i] = tagged
        if i % 60 == 0:
            print(f"{t:5.2f} s", flush=True)
    for e in encs:
        e.stdin.close()
        assert e.wait() == 0
    os.remove(wp)
    ks = sorted(keep)
    Image.fromarray(keep[ks[0]]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 5, 480 * 2))
    for j, i in enumerate(ks[:10]):
        sh.paste(Image.fromarray(keep[i]).resize((270, 480)), (270 * (j % 5), 480 * (j // 5)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", n, "frames")


if __name__ == "__main__":
    main()
