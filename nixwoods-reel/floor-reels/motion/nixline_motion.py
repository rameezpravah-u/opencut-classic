#!/usr/bin/env python3
"""NixLine — 15 s motion piece.  "one line."

The product is called NixLine and its light *is* a line, so the whole piece is built on one
amber line: it draws up the frame, opens like an aperture onto the lamp, measures it, and at the
end the last shot collapses back into a horizontal line that becomes the wordmark's underline.
Vertical line in, horizontal line out — the lamp standing, then lying down.

Every cut sits on the beat grid of music5-3040 (95.7 BPM, beat 0.627 s, phase 0.370 s into the
track — the music is started there so beat 0 is frame 0).

Palette is the PDP's own stylesheet (.nw-pdp): ink #1A1614, cream #F3EDE3, amber #E8A24A,
warm grey #8a8178. Type: Space Grotesk (the house noir headline) set against Cormorant Garamond
italic on the one word per line that carries the idea — the boutique-hotel half of the brand.

Claims on screen, all from the live PDP: solid teak · no MDF · no veneer · 30 in · slim column ·
warm LED 2700-3000K · plug in and place · handcrafted in Uttar Pradesh. No price (owner's call).
All footage is Rameez's own; no generated frames, so no AI disclosure.

    python3 floor-reels/motion/nixline_motion.py            # -> floor-reels/out/motion/
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

FF   = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # floor-reels/
ASSET = os.path.join(os.path.dirname(ROOT), "assets")
OUT  = os.path.join(ROOT, "out", "motion"); os.makedirs(OUT, exist_ok=True)

W, H, FPS, DUR = 1080, 1920, 30, 15.0
N = int(round(DUR * FPS))
B = 0.627                                          # one beat
def beat(k): return k * B

INK   = np.array([26, 22, 20],   np.float32)
CREAM = np.array([243, 237, 227], np.float32)
AMBER = np.array([232, 162, 74],  np.float32)
GREY  = np.array([138, 129, 120], np.float32)
SAFE_L, SAFE_R, SAFE_T, SAFE_B = 70, 950, 230, 1500
X0 = 96                                            # house left margin (noir style)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def prog(t, t0, d): return clamp((t - t0) / d)
def out_expo(x): return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)
def in_expo(x):  return 0.0 if x <= 0 else 2 ** (10 * x - 10)
def out_cubic(x): return 1 - (1 - x) ** 3
def inout_cubic(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def out_back(x, s=1.4): x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------------------------------------------------------------- footage
class Reader:
    """Forward-only frame source. Output time only moves forward, so every clip is read once."""
    def __init__(self, path, ss, need):
        have = clip_len(path)
        if ss + need > have + 1e-3:                    # the silent-truncation guard
            sys.exit(f"{path}: ss {ss:.2f} + {need:.2f} runs past the end ({have:.2f}s)")
        self.p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-ss", f"{ss:.3f}", "-i", path,
                                   "-t", f"{need + 0.2:.3f}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                  stdout=subprocess.PIPE, stdin=subprocess.DEVNULL)
        self.i, self.cur = -1, None
    def at(self, local_t):
        want = int(local_t * FPS)
        while self.i < want:
            buf = self.p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break               # hold last frame rather than go black
            self.cur = np.frombuffer(buf, np.uint8).reshape(H, W, 3); self.i += 1
        return self.cur

def clip_len(path):
    o = subprocess.run([FF, "-nostdin", "-i", path], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL).stderr
    h, m, s = o.split("Duration:")[1].split(",")[0].strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

SRC = lambda n: os.path.join(ROOT, "src", n)

def lamp_x(path, ss, dur):
    """Where the lit channel sits horizontally, so narrow crops land on the lamp, not the floor."""
    d = subprocess.run([FF, "-nostdin", "-v", "error", "-ss", str(ss), "-t", str(dur), "-i", path,
                        "-vf", "fps=4,scale=270:480", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                       capture_output=True, stdin=subprocess.DEVNULL).stdout
    g = np.frombuffer(d, np.uint8).reshape(-1, 480, 270)
    cols = (g > 235).sum(axis=(0, 1)).astype(float)
    return float((cols * np.arange(270)).sum() / max(cols.sum(), 1)) / 270 * W if cols.sum() else W / 2

# ---------------------------------------------------------------- grade
def _lut():
    x = np.linspace(0, 1, 256)
    pts = [(0, 0), (.22, .15), (.55, .50), (.82, .84), (1, 1)]          # toe down, mids firm
    y = np.interp(x, [p[0] for p in pts], [p[1] for p in pts])
    r = np.clip(y * 1.035 * 255, 0, 255); g = np.clip(y * 1.0 * 255, 0, 255); b = np.clip(y * .93 * 255, 0, 255)
    return np.stack([r, g, b]).astype(np.uint8)
LUT = _lut()
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - .42 * (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H * .48) / (H * .60)) ** 2) ** 1.4).clip(.38, 1)[..., None]
_sy = np.arange(H, dtype=np.float32)
SCRIM = (np.clip((_sy - 960) / 380, 0, 1) ** 1.6 * .66)[:, None, None]
def legible(f, a=1.0):
    """Darken the lower band the type lives in. A gradient, never a plate - plates read as smudges."""
    f *= 1 - SCRIM * a

GRAIN = [np.random.default_rng(s).normal(0, 3.2, (H // 2, W // 2, 1)).astype(np.float32) for s in range(6)]

def grade(fr, k):
    f = np.stack([LUT[c][fr[..., c]] for c in range(3)], -1).astype(np.float32)
    f *= VIG
    g = GRAIN[k % 6]; f += np.repeat(np.repeat(g, 2, 0), 2, 1)
    return f

def push(fr, s, cx=.5, cy=.5):
    """Slow push-in — nothing in a motion piece should sit perfectly still."""
    if s <= 1.0005: return fr
    im = Image.fromarray(fr); w, h = int(W / s), int(H / s)
    x0 = int((W - w) * cx); y0 = int((H - h) * cy)
    return np.asarray(im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR))

# ---------------------------------------------------------------- light primitives
def glow_profile(sig, n=161):
    d = np.arange(n) - n // 2
    return np.exp(-(d ** 2) / (2 * sig ** 2)).astype(np.float32)

def vline(f, x, y0, y1, a=1.0, core=3, sig=22, col=AMBER):
    """Amber line with a gaussian halo, additive — the way a lit diffuser actually reads."""
    if y1 <= y0 or a <= 0: return
    y0, y1 = int(max(0, y0)), int(min(H, y1))
    prof = glow_profile(sig); r = len(prof) // 2
    xa, xb = int(x) - r, int(x) + r + 1
    pa, pb = max(0, -xa), len(prof) - max(0, xb - W)
    xa, xb = max(0, xa), min(W, xb)
    f[y0:y1, xa:xb] += (prof[pa:pb][None, :, None] * col[None, None] * .55 * a)
    c0, c1 = int(x - core / 2), int(x + core / 2 + 1)
    f[y0:y1, max(0, c0):min(W, c1)] = f[y0:y1, max(0, c0):min(W, c1)] * (1 - a) + (CREAM * .3 + AMBER * .7) * a + 40 * a

def hline(f, y, x0, x1, a=1.0, core=3, sig=20, col=AMBER):
    if x1 <= x0 or a <= 0: return
    x0, x1 = int(max(0, x0)), int(min(W, x1))
    prof = glow_profile(sig); r = len(prof) // 2
    ya, yb = int(y) - r, int(y) + r + 1
    pa, pb = max(0, -ya), len(prof) - max(0, yb - H)
    ya, yb = max(0, ya), min(H, yb)
    f[ya:yb, x0:x1] += (prof[pa:pb][:, None, None] * col[None, None] * .55 * a)
    c0, c1 = int(y - core / 2), int(y + core / 2 + 1)
    f[max(0, c0):min(H, c1), x0:x1] = f[max(0, c0):min(H, c1), x0:x1] * (1 - a) + (CREAM * .3 + AMBER * .7) * a + 40 * a

def bloom(f, cx, cy, rad, a):
    """a is a fraction of full amber at the centre (0-1), not a gain on the colour."""
    if a <= 0: return
    d2 = ((xx - cx) / rad) ** 2 + ((yy - cy) / (rad * 1.6)) ** 2
    f += (np.exp(-d2)[..., None] * AMBER[None, None] * a)

# ---------------------------------------------------------------- type
F = lambda n, s: ImageFont.truetype(os.path.join(ASSET, n), s)
GROT, GROT_B = "Space_Grotesk-500.ttf", "Space_Grotesk-700.ttf"
SERIF_I, INTER, INTER_L = "Fraunces-500-i.ttf", "Inter-600.ttf", "Inter-300.ttf"

def word_img(text, font, fill=(243, 237, 227), track=0, shadow=True):
    """One word, baseline-aligned, with a soft shadow baked in for legibility on footage."""
    asc, desc = font.getmetrics()
    if track:
        widths = [font.getlength(c) + track for c in text]; wd = int(sum(widths) - track)
    else:
        wd = int(font.getlength(text))
    pad = 30
    im = Image.new("RGBA", (wd + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    def draw(dr, col):
        if track:
            x = pad
            for c, w in zip(text, widths): dr.text((x, pad), c, font=font, fill=col); x += w
        else:
            dr.text((pad, pad), text, font=font, fill=col)
    if shadow:
        sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); draw(ImageDraw.Draw(sh), (0, 0, 0, 210))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(14)))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(3)))
    draw(ImageDraw.Draw(im), fill + (255,))
    return np.asarray(im).astype(np.float32), pad, asc

class Line:
    """A line of words; each word animates on its own so the line can stagger in."""
    def __init__(self, parts, x, baseline, gap=0.30):
        self.words = []; cx = x
        for txt, font, col in parts:
            for i, w in enumerate(txt.split(" ")):
                if not w: continue
                img, pad, asc = word_img(w, font, col)
                self.words.append((img, cx - pad, baseline - asc - pad))
                cx += font.getlength(w) + font.getlength(" ") * (1 if i < len(txt.split(" ")) - 1 or txt.endswith(" ") else 0)
        self.width = cx - x
    def draw(self, f, t, t_in, t_out=None, stagger=.07, rise=34):
        for i, (img, x, y) in enumerate(self.words):
            p = out_cubic(prog(t, t_in + i * stagger, .42))
            a = p
            dy = (1 - p) * rise
            if t_out is not None:
                q = prog(t, t_out, .22); a *= 1 - q; dy -= in_expo(q) * 18
            if a > 0.004: paste(f, img, x, y + dy, a)

def paste(f, img, x, y, a=1.0):
    x, y = int(round(x)), int(round(y)); h, w = img.shape[:2]
    xa, ya, xb, yb = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if xa >= xb or ya >= yb: return
    sub = img[ya - y:yb - y, xa - x:xb - x]
    al = sub[..., 3:4] / 255 * a
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - al) + sub[..., :3] * al

# accent is the PDP amber lifted toward cream: #E8A24A itself has no contrast against teak
C = (243, 237, 227); A = (255, 198, 124); G = (138, 129, 120)
def L(parts, y, x=X0): return Line(parts, x, y)
g90, s112 = F(GROT, 100), F(SERIF_I, 126)

# hook — two lines, the second lands on beat 3
T_HOOK1 = L([("one side is ", g90, C), ("teak.", s112, A)], 1290)
T_HOOK2 = L([("turn it.", g90, C)], 1415)
# the payoff word gets its own line, larger - and it keeps the line inside the action rail
T_LIGHT = L([("the other is", g90, C)], 1270)
T_LIGHT2 = L([("light.", F(SERIF_I, 178), A)], 1445)
T_SOLID = L([("solid ", g90, C), ("teak.", s112, A)], 1290)
T_NOMDF = L([("no mdf. no veneer.", F(GROT, 66), C)], 1395)
# starts at the "30", clear of the dimension line at x=150
T_SLIM  = L([("a slim column of solid teak.", F(GROT, 46), C)], 1330, x=236)
T_PLUG  = L([("plug in", g90, C)], 1290)
T_PLACE = L([("and ", g90, C), ("place.", s112, A)], 1415)
T_HAND  = L([("handcrafted in", F(GROT, 74), C)], 1290)
T_UP    = L([("uttar ", s112, A), ("pradesh.", s112, A)], 1420)

KICK = F(INTER, 30)
def kicker(text, col=G): return word_img(text.upper(), KICK, col, track=6, shadow=True)
K_WARM = kicker("warm led")
K_IN   = kicker("nixline")

# spec type
BIG = F(GROT_B, 250); IN_I = F(SERIF_I, 120)
DIGITS = {str(n): word_img(str(n), BIG, C) for n in range(0, 31)}
UNIT_IN = word_img("in", IN_I, A)
KELVIN = word_img("2700–3000K", F(GROT_B, 120), C)

# end card
WORD = F(GROT_B, 168)
LETTERS = [word_img(c, WORD, C, shadow=False) for c in "nixline"]
LET_W = [WORD.getlength(c) for c in "nixline"]
TAG = word_img("solid teak floor lamp", F(INTER_L, 50), C, shadow=False)
URL = word_img("NIXWOODS.COM", F(INTER, 34), (232, 162, 74), track=7, shadow=False)
LOGO = np.asarray(Image.open(os.path.join(ASSET, "logo.png")).convert("RGBA").resize((188, 133), Image.LANCZOS)).astype(np.float32)

# ---------------------------------------------------------------- shots
#   nx06: plain teak faces camera 3.3-5.7 s, the lit channel swings round at 6.0 s (measured).
#   Reveal is put on beat 5, so the take starts at 6.0 - beat(5) = 2.865 s of source.
NX06_OFF = 6.0 - beat(5)
SHOTS = {}
def open_shots():
    SHOTS["nx06"] = Reader(SRC("nx06-7921.mp4"), beat(1) + NX06_OFF, beat(8) - beat(1))
    SHOTS["tri_l"] = Reader(SRC("nx07-7922.mp4"), 0.0, beat(12) - beat(8))
    SHOTS["tri_c"] = Reader(SRC("nx00-hero.mp4"), 6.4, beat(12) - beat(9))
    SHOTS["tri_r"] = Reader(SRC("nx08-7924.mp4"), 0.5, beat(12) - beat(10))
    SHOTS["spec"] = Reader(SRC("nx05-7920.mp4"), 0.0, beat(14) - beat(12))
    SHOTS["kelvin"] = Reader(SRC("nx06-7921.mp4"), 7.95, beat(16) - beat(14))
    SHOTS["horiz"] = Reader(SRC("nx01-7923.mp4"), 0.3, beat(18) - beat(16))
    SHOTS["wood"] = Reader(SRC("nx05-7920.mp4"), 3.0, beat(20) - beat(18) + .4)

STRIP_W, GAP = 330, 15
STRIP_X = [GAP + i * (STRIP_W + GAP) + 7 for i in range(3)]
CROP_X = {}

# ---------------------------------------------------------------- the frame
def frame(k):
    t = k / FPS
    f = np.empty((H, W, 3), np.float32); f[:] = INK

    # ---- 1  a line draws up the frame, then opens like an aperture onto the teak side
    if t < beat(8):
        if t >= beat(1):
            src = SHOTS["nx06"].at(t - beat(1))
            # the reveal: push in and flare on beat 5, as the light comes round
            rv = prog(t, beat(5), .55)
            s = 1.04 + .05 * out_expo(rv) + .02 * prog(t, beat(1), beat(7))
            img = grade(push(src, s, .5, .45), k)
            if t >= beat(5):
                flash = math.exp(-(t - beat(5)) / .16)
                img *= 1 + .28 * flash
                bloom(img, W * .48, H * .44, 380, .62 * math.exp(-(t - beat(5)) / .45))
            ap = inout_cubic(prog(t, beat(1), beat(2) - beat(1)))          # aperture width 0 -> full
            half = 3 + ap * W / 2
            # clamp: a negative start index in numpy counts from the right, so an aperture that
            # opens past the frame edge would otherwise show three columns of footage, not all of it
            x0, x1 = max(0, int(W / 2 - half)), min(W, int(W / 2 + half))
            f[:, x0:x1] = img[:, x0:x1]
            if ap < 1:                                                     # the two edges carry the light outward
                e = 1 - ap ** 2
                vline(f, x0, 0, H, e); vline(f, x1, 0, H, e)
        if t < beat(2):
            d = out_expo(prog(t, .05, beat(1) - .05))                       # draw bottom -> top
            if t < beat(1):
                y_top = H - d * H
                vline(f, W / 2, y_top, H, 1.0, core=4, sig=26)
                bloom(f, W / 2, y_top, 70, .95 * (1 - d * .6))              # the hot tip
        legible(f, prog(t, beat(1), .4))
        T_HOOK1.draw(f, t, .18, t_out=beat(5) - .32)
        T_HOOK2.draw(f, t, beat(3), t_out=beat(5) - .32)
        T_LIGHT.draw(f, t, beat(5) + .05, t_out=beat(8) - .26)
        T_LIGHT2.draw(f, t, beat(5) + .22, t_out=beat(8) - .26, rise=50)
        return f

    # ---- 2  three lines: three strips slide up on three beats
    if t < beat(12):
        for i, key in enumerate(("tri_l", "tri_c", "tri_r")):
            t_in = beat(8 + i)
            if t < t_in: continue
            p = out_expo(prog(t, t_in, .62))
            src = SHOTS[key].at(t - t_in)
            img = grade(push(src, 1.06 - .04 * p), k)
            cx = CROP_X[key]; sx = int(clamp(cx - STRIP_W / 2, 0, W - STRIP_W))
            strip = img[:, sx:sx + STRIP_W]
            dy = int((1 - p) * H * .9)
            x = STRIP_X[i]
            f[dy:, x:x + STRIP_W] = strip[:H - dy]
            hline(f, dy + 1, x, x + STRIP_W, .9 * p, core=2, sig=10)          # each strip is lit along its edge
        legible(f)
        T_SOLID.draw(f, t, beat(8) + .22, t_out=beat(12) - .24)
        T_NOMDF.draw(f, t, beat(10), t_out=beat(12) - .24, stagger=.05)
        return f

    # ---- 3  the spec, drawn as graphics on the lamp
    if t < beat(16):
        if t < beat(14):
            src = SHOTS["spec"].at(t - beat(12))
            f = grade(push(src, 1.03 + .04 * prog(t, beat(12), 2 * B), .5, .4), k)
        else:
            src = SHOTS["kelvin"].at(t - beat(14))
            f = grade(push(src, 1.06 - .03 * out_cubic(prog(t, beat(14), 2 * B)), .5, .4), k)
        f *= .80                                                           # let the graphics carry
        legible(f, .8)
        a_dim = 1 - prog(t, beat(14) - .25, .25)
        # dimension line, drawn upward with end ticks
        d = out_expo(prog(t, beat(12) + .08, .75))
        yb, yt = 1470, 330
        ytop = yb - d * (yb - yt)
        vline(f, 150, ytop, yb, a_dim, core=3, sig=14)
        hline(f, yb, 126, 174, a_dim, core=3, sig=8)
        if d > .98: hline(f, yt, 126, 174, a_dim, core=3, sig=8)
        # counter 0 -> 30
        n = int(round(30 * out_cubic(prog(t, beat(12) + .15, .9))))
        img, pad, asc = DIGITS[str(n)]
        pa = out_cubic(prog(t, beat(12) + .1, .3)) * a_dim
        paste(f, img, 230 - pad, 1000 - pad, pa)
        uimg, upad, _ = UNIT_IN
        paste(f, uimg, 230 + BIG.getlength("30") + 20 - upad, 1080 - upad, pa * out_cubic(prog(t, beat(12) + .9, .3)))
        T_SLIM.draw(f, t, beat(13) + .2, t_out=beat(14) - .25, stagger=.03, rise=18)
        # colour temperature: a bar that wipes in, warm to slightly less warm, the real 2700-3000K span
        if t >= beat(14):
            w = out_expo(prog(t, beat(14), .7)) * (W - 2 * X0)
            grad = np.linspace(0, 1, W - 2 * X0)[:, None]
            k27, k30 = np.array([255, 166, 87.]), np.array([255, 180, 107.])
            bar = (k27 * (1 - grad) + k30 * grad)[None]
            f[1360:1374, X0:X0 + int(w)] = bar[:, :int(w)]
            hline(f, 1367, X0, X0 + w, .7, core=0, sig=16)
            kimg, kpad, _ = KELVIN
            ka = out_cubic(prog(t, beat(14) + .15, .35)) * (1 - prog(t, beat(16) - .22, .22))
            paste(f, kimg, X0 - kpad, 1180 - kpad + (1 - ka) * 30, ka)
            wimg, wpad, _ = K_WARM
            paste(f, wimg, X0 - wpad, 1400 - wpad, ka)
        return f

    # ---- 4  lying down: the line goes horizontal
    if t < beat(18):
        src = SHOTS["horiz"].at(t - beat(16))
        f = grade(push(src, 1.08 - .05 * out_cubic(prog(t, beat(16), 2 * B)), .5, .5), k)
        legible(f)
        T_PLUG.draw(f, t, beat(16) + .05, t_out=beat(18) - .22)
        T_PLACE.draw(f, t, beat(17), t_out=beat(18) - .22)
        return f

    # ---- 5  back to the wood
    if t < beat(20):
        src = SHOTS["wood"].at(t - beat(18))
        f = grade(push(src, 1.04 + .04 * prog(t, beat(18), 2 * B), .5, .45), k)
        legible(f)
        T_HAND.draw(f, t, beat(18) + .05, t_out=beat(20) - .2, stagger=.05)
        T_UP.draw(f, t, beat(19) - .1, t_out=beat(20) - .2)
        return f

    # ---- 6  the last shot collapses into a line, and the line becomes the wordmark
    y_line = 1085
    c = in_expo(prog(t, beat(20), .38))
    if c < 1:
        src = SHOTS["wood"].at(t - beat(18))
        img = grade(src, k)
        h = max(2, int(H * (1 - c)))
        sl = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8)).resize((W, h), Image.BILINEAR)).astype(np.float32)
        y0 = int(y_line - h * (y_line / H))
        f[max(0, y0):max(0, y0) + h] = sl[:H - max(0, y0)] if y0 >= 0 else sl[-y0:]
        f[max(0, y0):max(0, y0) + h] = f[max(0, y0):max(0, y0) + h] * (1 - c) + (AMBER + 20) * c
    tw = sum(LET_W); wx = (W - tw) / 2
    # underline narrows from full width to the wordmark, and breathes
    n = out_expo(prog(t, beat(20) + .3, .7))
    half = (W / 2) * (1 - n) + (tw / 2 + 10) * n
    breath = .85 + .15 * math.sin((t - beat(20)) * 2.4)
    hline(f, y_line, W / 2 - half, W / 2 + half, min(1, c * 1.2) * breath if c < 1 else breath, core=4, sig=24)
    # wordmark, letter by letter, rising out of the line
    x = wx
    for i, (img, pad, asc) in enumerate(LETTERS):
        p = out_back(prog(t, beat(20) + .55 + i * .055, .5), 1.2)
        a = clamp(prog(t, beat(20) + .55 + i * .055, .25))
        if a > 0:
            yb = y_line - 26 - asc
            paste(f, img, x - pad, yb - pad + (1 - p) * 70, a)
        x += LET_W[i]
    la = out_cubic(prog(t, beat(21) + .3, .5))
    paste(f, LOGO, (W - LOGO.shape[1]) / 2, 600 + (1 - la) * 24, la)
    ti, tp, _ = TAG
    paste(f, ti, (W - ti.shape[1]) / 2, y_line + 40 + (1 - out_cubic(prog(t, beat(21) + .6, .45))) * 20, out_cubic(prog(t, beat(21) + .6, .45)))
    ui, up, _ = URL
    paste(f, ui, (W - ui.shape[1]) / 2, y_line + 120, out_cubic(prog(t, beat(22), .5)))
    # a slow fade to ink in the last 0.25 s so a loop does not jump
    f *= 1 - .35 * prog(t, DUR - .25, .25)
    return f


def main():
    global CROP_X
    CROP_X = {"tri_l": lamp_x(SRC("nx07-7922.mp4"), 0.0, 2.5),
              "tri_c": lamp_x(SRC("nx00-hero.mp4"), 6.4, 1.9),
              "tri_r": W * .5}
    print("strip crop centres:", {k: round(v) for k, v in CROP_X.items()})
    open_shots()
    silent = os.path.join(OUT, "_video.mp4")
    enc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", silent], stdin=subprocess.PIPE)
    for k in range(N):
        fr = frame(k)
        enc.stdin.write(fr.clip(0, 255).astype(np.uint8).tobytes())
        if k % 45 == 0: print(f"  frame {k}/{N}  t={k / FPS:5.2f}s", flush=True)
    enc.stdin.close(); enc.wait()

    aud = os.path.join(ROOT, "audio")
    final = os.path.join(OUT, "NX-MOTION-nixline-one-line-v1.mp4")
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", silent,
                    "-ss", "0.370", "-t", str(DUR), "-i", os.path.join(aud, "music5-3040.mp3"),
                    "-i", os.path.join(aud, "sfx-whoosh.mp3"), "-i", os.path.join(aud, "sfx-turn.mp3"),
                    "-i", os.path.join(aud, "sfx-whoosh.mp3"),
                    "-filter_complex",
                    "[1:a]volume=-2dB,afade=t=in:d=0.12,afade=t=out:st=14.1:d=0.9[m];"
                    f"[2:a]adelay={int((beat(1) - .12) * 1000)}|{int((beat(1) - .12) * 1000)},volume=-9dB[w1];"
                    f"[3:a]adelay={int((beat(5) - .06) * 1000)}|{int((beat(5) - .06) * 1000)},volume=-6dB[tr];"
                    f"[4:a]adelay={int((beat(20) - .1) * 1000)}|{int((beat(20) - .1) * 1000)},volume=-9dB[w2];"
                    "[m][w1][tr][w2]amix=inputs=4:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", str(DUR), final], check=True)
    os.remove(silent)
    print("done", final)


if __name__ == "__main__":
    main()
