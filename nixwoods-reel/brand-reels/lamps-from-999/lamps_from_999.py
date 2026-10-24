"""
"Lamps from ₹999": our take on RAS Oils' tablet ad (instagram.com/p/DZsWYgMDE-e, sent by the owner on 24 Oct with
"make this exact, just replace the product"). 4:5, 15.4 s, the reference's layout and timings:
- a tablet on a desk plays a clip; the reference's clip is from *Friends*, which we do not have the rights to, so the
  tablet plays our own CAM 02 heist reel (cctv-heist v3, AI) with its own sound;
- three products arrive one by one where the reference's hand sets its jars down (0.75 s, 6.0 s, 7.0 s):
  NixLine ₹999, Luma Pillar ₹1,599, Rubik's Cube from ₹2,999 (prices from the live product pages, 24 Oct);
- the offer in a gold frame at the top, the logo top-right;
- a dark end card from 13.1 s, the logo fading in.
The products are cut-outs of our own product photos (cut/, see README); the desk, wall and tablet are drawn here.

    python3 brand-reels/lamps-from-999/lamps_from_999.py [--still 8.0]
"""
import argparse, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import A, FF, FPS, font, sstep  # noqa: E402

W, H = 1080, 1350
SR = 48000
DUR = 15.4
END = 13.1                                              # the end card, as the reference
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261024-nixwoods-lamps-from-999-tablet-v1-AI"
TABLET_SRC = os.path.join(ROOT, "brand-reels", "cctv-heist", "out",
                          "NW-CREATIVE-VID-20261019-nix-line-solid-wood-floor-lamp-cctv-heist-v3-AI.mp4")
CREAM, PAPER, INK, AMBER, AMBER_D, MUTED = (246, 239, 228), (238, 228, 212), (58, 38, 24), (232, 162, 74), \
    (176, 104, 40), (124, 100, 82)
GROUND = (20, 13, 9)                                    # the end card: near-black, warm (the reference's is black)
DESK_Y = 800                                            # where the wall meets the desk
TAB = (455, 330, 1017, 1080)                            # tablet, portrait (CAM 02 is a 9:16 reel)
BEZEL = 20
# product: sprite, landing time, bottom-centre on the desk, height, price tag
PRODUCTS = [
    dict(key="nixline", t=0.75, x=300, y=1250, h=880, name="NixLine", price="₹999", tag_x=205, enter=(-240, -90)),
    dict(key="luma", t=6.0, x=478, y=1244, h=420, name="Luma Pillar", price="₹1,599", tag_x=470, enter=(-240, -90)),
    dict(key="cube", t=7.0, x=790, y=1252, h=292, name="Rubik's Cube", price="from ₹2,999", tag_x=800,
         enter=(0, -170)),                               # set down from above, as the reference's second jar
]
IN_S = 0.6                                              # the move into place, ease-out, no overshoot (MOTION.md §5)
CUBE_SWAP = (10.0, 10.6)                                # the cube's light goes from amber to red: two real colours
RNG = np.random.default_rng(24)


def ease_out(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def rgba(path, h):
    im = Image.open(path).convert("RGBA")
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


# ---------------------------------------------------------------------------------------------- the set
def wood(w, h):
    """a light honey desk top: long grain running left to right, closer together towards the back edge"""
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    depth = 0.25 + 0.75 * y                              # 0.25 at the back edge, 1 at the front
    n = cv2.GaussianBlur(RNG.standard_normal((h, w)).astype(np.float32), (0, 0), 18) * 9
    phase = (y ** 0.6) * 140 + n + np.sin(x * 7 + y * 3) * 1.2
    g = 0.5 + 0.5 * np.sin(phase)
    fine = cv2.GaussianBlur(RNG.standard_normal((h, w)).astype(np.float32), (0, 0), sigmaX=40, sigmaY=0.8)
    g = g * 0.6 + np.clip(fine * 4 + 0.5, 0, 1) * 0.4
    base = np.array([214, 178, 132], np.float32) / 255
    dark = np.array([186, 144, 100], np.float32) / 255
    img = base + (dark - base) * g[..., None] * 0.8
    light = (0.92 + 0.12 * (1 - y)) * (1.0 - 0.10 * np.abs(x - 0.4) ** 1.5)   # brighter at the back, under the glow
    return np.clip(img * light[..., None] * (0.97 + 0.03 * depth[..., None]), 0, 1)


def wall(w, h):
    """a warm plaster wall under the gold light that pours in from the top, as the reference's"""
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    lo = np.array(PAPER, np.float32) / 255 * 0.93
    hi = np.array([255, 214, 130], np.float32) / 255
    r = np.sqrt(((x - 0.5) * 1.1) ** 2 + (y * 1.35) ** 2)
    glow = np.clip(1.08 - r, 0, 1) ** 1.3
    img = lo + (hi - lo) * glow[..., None]
    tex = cv2.GaussianBlur(RNG.standard_normal((h, w)).astype(np.float32), (0, 0), 3) * 0.012
    return np.clip(img * (1 - 0.10 * y[..., None]) + tex[..., None], 0, 1)


def shadow_layer(boxes):
    """soft shadows of the tablet on the wall and desk"""
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    for b, a in boxes:
        d.rounded_rectangle(b, 34, fill=a)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(26)), np.float32)[..., None] / 255


def base_set():
    img = np.zeros((H, W, 3), np.float32)
    img[:DESK_Y] = wall(W, DESK_Y)
    img[DESK_Y:] = wood(W, H - DESK_Y)
    edge = np.clip(1 - np.abs(np.arange(H) - DESK_Y) / 6, 0, 1)[:, None, None]  # the desk's back edge
    img *= 1 - 0.16 * edge
    x0, y0, x1, y1 = TAB
    sh = shadow_layer([((x0 + 26, y0 + 24, x1 + 30, y1 + 4), 120), ((x0 - 10, y1 - 20, x1 + 40, y1 + 26), 200)])
    return img * (1 - 0.42 * sh)


def tablet_frame():
    """the bezel, edge light and glass sheen as an RGBA layer; the screen area is left open"""
    x0, y0, x1, y1 = TAB
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x0, y0, x1, y1), 38, fill=(22, 20, 19, 255))
    d.rounded_rectangle((x0, y0, x1, y1), 38, outline=(92, 86, 80, 255), width=3)
    d.rounded_rectangle((x0 + BEZEL, y0 + BEZEL, x1 - BEZEL, y1 - BEZEL), 10, fill=(0, 0, 0, 0))
    d.ellipse(((x0 + x1) / 2 - 5, y0 + 6, (x0 + x1) / 2 + 5, y0 + 16), fill=(40, 38, 36, 255))   # camera
    return np.asarray(lay, np.float32) / 255


def sheen():
    x0, y0, x1, y1 = TAB
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    s = np.clip(1 - np.abs((xx - x0) * 0.8 + (yy - y0) * 0.55 - 260) / 160, 0, 1) * 0.07
    inside = (xx > x0 + BEZEL) & (xx < x1 - BEZEL) & (yy > y0 + BEZEL) & (yy < y1 - BEZEL)
    return (s * inside)[..., None]


def screen_frames():
    """CAM 02 v3 from 0 s, cropped to the tablet's portrait screen (the REC line and captions stay inside)"""
    x0, y0, x1, y1 = TAB
    sw, sh = x1 - x0 - 2 * BEZEL, y1 - y0 - 2 * BEZEL
    ch = round(1080 * sh / sw)
    raw = subprocess.run([FF, "-v", "error", "-i", TABLET_SRC, "-t", f"{END:.3f}", "-vf",
                          f"fps={FPS},crop=1080:{ch}:0:190,scale={sw}:{sh}:flags=lanczos", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, sh, sw, 3), (x0 + BEZEL, y0 + BEZEL, sw, sh)


# ---------------------------------------------------------------------------------------------- type
def headline():
    """the gold frame with the offer: 'Lamps / from' stacked small, '₹999' large, as 'Buy / Any 3 @1399'"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fx0, fy0, fx1, fy1 = 168, 58, 912, 296
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((fx0 - 6, fy0 - 6, fx1 + 6, fy1 + 6), 18, outline=AMBER + (150,), width=10)
    lay.alpha_composite(glow.filter(ImageFilter.GaussianBlur(9)))
    d.rounded_rectangle((fx0, fy0, fx1, fy1), 14, fill=(255, 246, 226, 120), outline=AMBER_D + (255,), width=3)
    d.rounded_rectangle((fx0 + 9, fy0 + 9, fx1 - 9, fy1 - 9), 9, outline=AMBER + (230,), width=2)
    for cx, cy in [(fx0, fy0), (fx1, fy0), (fx0, fy1), (fx1, fy1)]:              # small diamond corners
        r = 13
        d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=AMBER + (255,), outline=AMBER_D + (255,))
    f_tag = font("Fraunces-500-i.ttf", 30)
    t = "@nix_woods"
    d.text(((fx0 + fx1 - f_tag.getlength(t)) / 2, fy0 + 20), t, font=f_tag, fill=AMBER_D + (255,))
    f_s, f_b = font("Fraunces-600.ttf", 64), font("Fraunces-600.ttf", 178)
    big = "₹999"
    wb = f_b.getlength(big)
    ws = max(f_s.getlength("Lamps"), f_s.getlength("from"))
    gap = 26
    x = (fx0 + fx1 - (ws + gap + wb)) / 2
    base = fy1 - 34                                                                # shared baseline
    asc_b = f_b.getbbox(big)[3]
    d.text((x + wb + ws + gap - wb, base - asc_b), big, font=f_b, fill=INK + (255,))
    d.text((x + ws - f_s.getlength("Lamps"), base - 132), "Lamps", font=f_s, fill=INK + (255,))
    d.text((x + ws - f_s.getlength("from"), base - 68), "from", font=f_s, fill=INK + (255,))
    return np.asarray(lay, np.float32) / 255


def logo(width, color):
    lg = Image.open(A("logo.png")).convert("RGBA")
    lg = lg.resize((width, round(width * lg.height / lg.width)), Image.LANCZOS)
    ink = Image.new("RGBA", lg.size, color + (255,))
    ink.putalpha(lg.getchannel("A"))
    return ink


def corner_logo():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lg = logo(96, INK)
    lay.alpha_composite(lg, (W - lg.width - 28, 22))
    return np.asarray(lay, np.float32) / 255


def tag(p):
    """a small cream price card under each product (MOTION.md: rounded cream card at 236/255)"""
    f_n, f_p = font("Inter-600.ttf", 23), font("Inter-600.ttf", 25)
    wn, wp = f_n.getlength(p["name"]), f_p.getlength(p["price"])
    w, h = wn + wp + 44, 46
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = min(max(p["tag_x"] - w / 2, 24), W - 24 - w)
    y = 1282
    d.rounded_rectangle((x, y, x + w, y + h), 25, fill=CREAM + (236,))
    d.text((x + 17, y + 10), p["name"], font=f_n, fill=INK + (255,))
    d.text((x + 27 + wn, y + 8), p["price"], font=f_p, fill=AMBER_D + (255,))
    return np.asarray(lay, np.float32) / 255


def end_card():
    lay = Image.new("RGBA", (W, H), GROUND + (255,))
    lg = logo(440, CREAM)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.alpha_composite(logo(440, (0, 0, 0)), ((W - lg.width) // 2 + 4, 520 + 8))
    lay.alpha_composite(Image.fromarray((np.asarray(sh) * [1, 1, 1, 0.5]).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(14)))
    logo_l = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo_l.alpha_composite(lg, ((W - lg.width) // 2, 520))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    f1, f2 = font("Inter-600.ttf", 26), font("Inter-600.ttf", 40)
    t1 = "S O L I D   W O O D   L I G H T I N G"
    d.text(((W - f1.getlength(t1)) / 2, 520 + lg.height + 34), t1, font=f1, fill=(200, 190, 178, 255))
    t2 = "nixwoods.com"
    d.text(((W - f2.getlength(t2)) / 2, 520 + lg.height + 104), t2, font=f2, fill=AMBER + (255,))
    f = lambda im: np.asarray(im, np.float32) / 255
    return f(lay)[..., :3], f(logo_l), f(txt)


# ---------------------------------------------------------------------------------------------- compositing
def over(dst, lay, a=1.0):
    al = lay[..., 3:] * a
    return dst * (1 - al) + lay[..., :3] * al


def place(dst, spr, x, y_bottom, alpha=1.0):
    """an RGBA sprite with its bottom-centre at (x, y_bottom)"""
    h, w = spr.shape[:2]
    x0, y0 = int(round(x - w / 2)), int(round(y_bottom - h))
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]
    a = s[..., 3:] * alpha
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - a) + s[..., :3] * a


def glow(dst, cx, cy, rx, ry, color, a):
    """a warm light pool from a lit lamp (screen blend, so it brightens the desk and wall it falls on)"""
    yy, xx = np.ogrid[0:H, 0:W]
    g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)).astype(np.float32)[..., None] * a
    c = np.array(color, np.float32) / 255
    return 1 - (1 - dst) * (1 - g * c)


def contact(dst, x, y, w, a):
    yy, xx = np.ogrid[0:H, 0:W]
    g = np.exp(-(((xx - x) / (w * 0.55)) ** 2 + ((yy - y) / 9) ** 2)).astype(np.float32)[..., None]
    return dst * (1 - 0.55 * a * g)


def cast_layer(spr, x, y_bottom):
    """the lamp's soft shadow thrown back and to the right on the wall by the gold light at the top-left"""
    m = np.zeros((H, W), np.float32)
    h, w = spr.shape[:2]
    x0, y0 = int(round(x - w / 2)) + 34, int(round(y_bottom - h)) - 10
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    m[ya:yb, xa:xb] = spr[ya - y0:yb - y0, xa - x0:xb - x0, 3]
    m[DESK_Y + 10:] *= 0.0                               # on the wall only; the desk gets the contact shadow
    return cv2.GaussianBlur(m, (0, 0), 14)[..., None]


def cast(dst, lay, dx, dy, a):
    if a <= 0:
        return dst
    if dx or dy:
        lay = cv2.warpAffine(lay[..., 0], np.float32([[1, 0, dx], [0, 1, dy]]), (W, H))[..., None]
    return dst * (1 - a * lay)


def grade(img):
    """MOTION.md photo grade, then fine grain"""
    img = np.clip(img * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)
    return np.clip(img + RNG.normal(0, 2.2 / 255, img.shape[:2])[..., None].astype(np.float32), 0, 1)


def sparkles():
    """a few slow glints in the gold light over the frame, as the reference's (no strobing)"""
    pts = RNG.uniform([150, 40], [930, 330], (16, 2))
    return pts, RNG.uniform(0, 2 * np.pi, 16), RNG.uniform(0.5, 1.0, 16)


def frame(t, ctx):
    img = ctx["set"].copy()
    sx, sy, sw, sh = ctx["scr_box"]
    k = min(int(t * FPS), len(ctx["scr"]) - 1)
    img[sy:sy + sh, sx:sx + sw] = ctx["scr"][k].astype(np.float32) / 255
    img = over(img, ctx["tab"])
    img = np.clip(img + ctx["sheen"], 0, 1)
    pts, ph, amp = ctx["spark"]
    for (px, py), p0, a in zip(pts, ph, amp):
        v = a * (0.5 + 0.5 * np.sin(t * 1.3 + p0)) ** 3
        if v > 0.05:
            img = glow(img, px, py, 11, 11, (255, 236, 190), v)
            img = glow(img, px, py, 3, 26, (255, 246, 220), 0.8 * v)    # a thin star flare
            img = glow(img, px, py, 26, 3, (255, 246, 220), 0.8 * v)
    for p in PRODUCTS:
        u = ease_out((t - p["t"]) / IN_S)
        if t < p["t"]:
            continue
        dx, dy = p["enter"]                              # in from the left, where the reference's hand comes from,
        x = p["x"] + dx * (1 - u)                        # with a little lift, set down at the end of the move
        y = p["y"] + dy * (1 - u) * (1 - u) if dx else p["y"] + dy * (1 - u)
        a_in = sstep((t - p["t"]) / 0.18)
        lit = sstep((t - p["t"] - IN_S) / 0.30)          # its light pools on the desk once it is down (0.30 s)
        if p["key"] == "nixline":
            img = glow(img, x + 30, p["y"] - 420, 150, 420, AMBER, 0.20 * lit)
        elif p["key"] == "luma":
            img = glow(img, x, p["y"] - 120, 170, 140, AMBER, 0.28 * lit)
        else:
            swp = sstep((t - CUBE_SWAP[0]) / (CUBE_SWAP[1] - CUBE_SWAP[0]))
            col = tuple(np.array(AMBER) * (1 - swp) + np.array([235, 70, 40]) * swp)
            img = glow(img, x, p["y"] - 60, 230, 120, col, 0.30 * lit)
        img = cast(img, ctx["cast"][p["key"]], x - p["x"], y - p["y"], a_in * 0.30)
        img = contact(img, x, p["y"] - 2, ctx["spr"][p["key"]][0].shape[1], a_in * (0.6 + 0.4 * u))
        if p["key"] == "cube":
            swp = sstep((t - CUBE_SWAP[0]) / (CUBE_SWAP[1] - CUBE_SWAP[0]))
            place(img, ctx["spr"]["cube"][0], x, y, a_in * (1 - swp))
            if swp > 0:
                place(img, ctx["spr"]["cube"][1], x, y, a_in * swp)
        else:
            place(img, ctx["spr"][p["key"]][0], x, y, a_in)
        img = over(img, ctx["tags"][p["key"]], sstep((t - p["t"] - IN_S) / 0.28))
    img = over(img, ctx["head"])
    img = over(img, ctx["logo"])
    img = grade(img)
    if t >= END:                                         # the end card: a cut to dark, the logo fades up
        bg, lg, tx = ctx["end"]
        e = bg.copy()
        e = over(e, lg, sstep((t - END - 0.15) / 0.8))
        e = over(e, tx, sstep((t - END - 0.75) / 0.3))
        yy, xx = np.ogrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 1.6
        e = np.clip(e * (1.08 - 0.35 * r)[..., None], 0, 1)
        img = np.clip(e + RNG.normal(0, 2.2 / 255, e.shape[:2])[..., None], 0, 1)
    return (img * 255 + 0.5).astype(np.uint8)


def context():
    scr, box = screen_frames()
    spr = {"nixline": [rgba(os.path.join(HERE, "cut", "nixline.png"), PRODUCTS[0]["h"])],
           "luma": [rgba(os.path.join(HERE, "cut", "luma-pillar.png"), PRODUCTS[1]["h"])],
           "cube": [rgba(os.path.join(HERE, "cut", "rubiks-cube-candy-amber.png"), PRODUCTS[2]["h"]),
                    rgba(os.path.join(HERE, "cut", "rubiks-cube-candy-red.png"), PRODUCTS[2]["h"])]}
    return dict(set=base_set(), tab=tablet_frame(), sheen=sheen(), scr=scr, scr_box=box, spr=spr,
                tags={p["key"]: tag(p) for p in PRODUCTS},
                cast={p["key"]: cast_layer(spr[p["key"]][0], p["x"], p["y"]) for p in PRODUCTS}, head=headline(), logo=corner_logo(), end=end_card(),
                spark=sparkles())


# ---------------------------------------------------------------------------------------------- sound
def audio(path):
    """the tablet's own sound (CAM 02's noir, hum and click, all ours), as if from a tablet speaker; a soft wooden
    knock as each lamp is set down; music1 under the end card"""
    n = int(DUR * SR)
    t = np.arange(n) / SR

    def load(p, af=None, t_len=DUR):
        cmd = [FF, "-v", "error", "-i", p, "-t", f"{t_len:.3f}"]
        if af:
            cmd += ["-af", af]
        raw = subprocess.run(cmd + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True,
                             check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        out = np.zeros((n, 2), np.float32)
        out[:len(a)] = a
        return out

    m = load(TABLET_SRC, "highpass=f=220,lowpass=f=7500", END) * 0.8
    m *= np.clip((END - t) / 0.12, 0, 1)[:, None]
    rng = np.random.default_rng(5)
    for p in PRODUCTS:
        i0 = int((p["t"] + IN_S - 0.02) * SR)
        L = int(0.09 * SR)
        k = np.arange(L) / SR
        knock = (np.sin(2 * np.pi * 180 * k) * 0.8 + np.sin(2 * np.pi * 420 * k) * 0.4) * np.exp(-k / 0.018)
        knock += rng.standard_normal(L) * np.exp(-k / 0.004) * 0.25
        m[i0:i0 + L] += (knock * 0.22)[:, None]
    mus = load(os.path.join(ROOT, "brand-reels", "audio", "music1-aesthetic.mp3"))
    mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * 10 ** (-20 / 20)
    m += mus * (np.clip((t - END) / 0.3, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1))[:, None]
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, nargs="*")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    ctx = context()
    if a.still is not None:
        for s in a.still:
            Image.fromarray(frame(s, ctx)).save(os.path.join(OUT, f"_still-{s:05.2f}.jpg"), quality=92)
        return
    wavp = os.path.join(OUT, ".audio.wav")
    audio(wavp)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                            str(FPS), "-i", "-", "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf",
                            "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                            "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest",
                            "-movflags", "+faststart", os.path.join(OUT, f"{NAME}.mp4")], stdin=subprocess.PIPE)
    n = round(DUR * FPS)
    for i in range(n):
        enc.stdin.write(frame(i / FPS, ctx).tobytes())
    enc.stdin.close()
    enc.wait()
    os.remove(wavp)
    print("done", n, "frames")


if __name__ == "__main__":
    main()
