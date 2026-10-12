#!/usr/bin/env python3
"""NixWoods "gravity build": three real lamps assemble themselves piece by piece in their own rooms, then switch on.

Idea from @pires.visuals' Seedance reel (instagram.com/reel/DdrdBZLo08N, 14.1 s, one take: debris flies in, a tower
builds itself floor by floor, the camera pulls back to the finished building). That reel is AI video. This one is
built for free from the 5 Aug 2026 DSLR shoot (real photos, no generated frames):

  1. the lamp is cut out of its own photo, and the room behind it is rebuilt row by row from the wall either side
     (an "empty plate");
  2. the cut-out is split into blocks that fly up into place bottom to top, with motion blur and sawdust;
  3. the light comes on on the beat (a warm-up for the Aurora, a line that draws itself up the rod and along the
     rope for the other two) and the room brightens to the untouched photo.

Scenes (music3-design, measured grid 0.6003 s from ~0 s; strong hits at 2.4, 3.6, 6.0, 9.6, 10.8, 13.2 s):
  0.0–3.6   Aurora linear wall light   AC4I9649   light on 2.4   from ₹1,999
  3.6–7.2   Minimalist floor lamp      AC4I9777   light on 6.0   from ₹6,999
  7.2–10.8  Sculpted Glow lamp         AC4I9882   light on 9.6   ₹9,999      (prices live on Shopify 12 Oct 2026)
  10.8–14.4 end card (Dusk): logo, "Solid wood. / Made by hand.", nixwoods.com

MOTION.md exceptions, both from the reference: pieces turn as they fly in (they settle, never spin), and the reel
runs 14.4 s like the reference instead of the 6–10 s organic length.

    python3 brand-reels/gravity-build/gravity_build.py            # full render
    python3 brand-reels/gravity-build/gravity_build.py --frames 0.5,2.0,3.0,5.0,6.5,9.0,10.5,12.0   # stills
"""
import argparse, glob, math, os, subprocess, sys
from collections import deque

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
ASSETS = os.path.join(ROOT, "assets")
AUDIO = os.path.join(ROOT, "aurora-reels", "audio")
NAME = "NW-CREATIVE-VID-20261012-nixwoods-gravity-build-v1"
FF = imageio_ffmpeg.get_ffmpeg_exe()

W, H, FPS = 1080, 1920, 30
BEAT = 0.6003
SCENE = 6 * BEAT            # 3.60 s
END_T = 18 * BEAT           # 10.80 s, the end card lands on the hit
DUR = 24 * BEAT             # 14.41 s
K = 0.75                    # working scale of the 3648 x 5472 photos

CREAM = np.array([246, 239, 228]) / 255
TEAK = np.array([46, 30, 20]) / 255
AMBER = (232, 162, 74)
AMBER_DARK = (176, 104, 40)
INK = (58, 38, 24)


def font(name, size):
    return ImageFont.truetype(os.path.join(ASSETS, name), size)


def sstep(x):
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3 - 2 * x)


def quart_out(u):
    u = np.clip(u, 0.0, 1.0)
    return 1 - (1 - u) ** 4


def expo_out_inverse(frac):
    """time fraction at which an expo-out draw (1 - 2^-10u) reaches `frac`"""
    frac = np.clip(frac, 0.0, 0.999)
    return -np.log2(1 - frac) / 10 / (-np.log2(1 - 0.999) / 10)


# ----------------------------------------------------------------------------------------------- photo prep
def load(tag):
    path = glob.glob(os.path.join(SHOOT, f"*{tag}*"))[0]
    im = Image.open(path).convert("RGB")
    im = im.resize((round(im.width * K), round(im.height * K)), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


def extend_top(img, n, r0, r1, x_clean=None):
    """add n rows of plain wall above the photo: each column keeps the mean of rows r0..r1, darkening a little upward"""
    base = img[r0:r1].mean(0)
    base = cv2.GaussianBlur(base[None], (0, 0), sigmaX=4, sigmaY=0.1)[0]
    fall = 1 - 0.07 * (np.arange(n)[::-1] / n)
    ext = base[None] * fall[:, None, None]
    noise = cv2.GaussianBlur(np.random.default_rng(3).normal(0, 0.006, (n, img.shape[1], 3)).astype(np.float32),
                             (0, 0), 0.7)
    ext = ext + noise
    out = np.concatenate([np.clip(ext, 0, 1).astype(np.float32), img], 0)
    seam = slice(n - 24, n + 24)                       # soften the join
    out[seam] = cv2.GaussianBlur(out[seam], (0, 0), sigmaX=0.1, sigmaY=6)
    return out


def row_fill(img, mask, pad=4, win=10):
    """rebuild masked pixels row by row from the wall either side; returns the plate and the filled area"""
    out = img.copy()
    filled = np.zeros(mask.shape, bool)
    w = img.shape[1]
    for y in np.where(mask.any(1))[0]:
        xs = np.where(mask[y])[0]
        xl, xr = xs[0], xs[-1]
        lw = img[y, max(0, xl - pad - win):max(0, xl - pad)]
        rw = img[y, min(w, xr + pad):min(w, xr + pad + win)]
        L = np.median(lw, 0) if len(lw) else np.median(rw, 0)
        R = np.median(rw, 0) if len(rw) else L
        tt = np.linspace(0, 1, xr - xl + 1)[:, None]
        out[y, xl:xr + 1] = L * (1 - tt) + R * tt
        filled[y, xl:xr + 1] = True
    sm = cv2.GaussianBlur(out, (0, 0), sigmaX=2.5, sigmaY=7)
    out[filled] = sm[filled]
    grain = np.random.default_rng(11).normal(0, 0.005, out.shape).astype(np.float32)
    out[filled] += grain[filled]
    return np.clip(out, 0, 1), filled


def auto_mask(img, box, thr, min_area=400):
    x0, y0, x1, y1 = [round(v * K) for v in box]
    m = np.zeros(img.shape[:2], bool)
    m[y0:y1, x0:x1] = True
    plate, _ = row_fill(img, m)
    d = np.abs(img - plate).max(2)
    pm = (d > thr) & m
    pm = ndimage.binary_opening(pm, iterations=1)
    pm = ndimage.binary_closing(pm, iterations=3) & m
    holes = ndimage.binary_fill_holes(pm) & ~pm          # fill only small holes (a frame's inside stays open)
    lab, n = ndimage.label(holes)
    if n:
        sizes = ndimage.sum(holes, lab, range(1, n + 1))
        pm |= np.isin(lab, 1 + np.where(sizes < 1500 * K * K)[0])
    lab, n = ndimage.label(pm)
    sizes = ndimage.sum(pm, lab, range(1, n + 1))
    return np.isin(lab, 1 + np.where(sizes > min_area * K * K)[0])


def lum(img):
    return img @ np.array([0.2126, 0.7152, 0.0722], np.float32)


def rect_mask(shape, box, off=0):
    m = np.zeros(shape, bool)
    x0, y0, x1, y1 = box
    m[round((y0 + off) * K):round((y1 + off) * K), round(x0 * K):round(x1 * K)] = True
    return m


def geodesic(mask, start):
    """BFS distance (8-connected) inside mask from the pixel nearest `start`"""
    ys, xs = np.where(mask)
    i = np.argmin((ys - start[1]) ** 2 + (xs - start[0]) ** 2)
    dist = np.full(mask.shape, -1, np.int32)
    q = deque([(ys[i], xs[i])])
    dist[ys[i], xs[i]] = 0
    hgt, wid = mask.shape
    while q:
        y, x = q.popleft()
        d = dist[y, x] + 1
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < hgt and 0 <= xx < wid and mask[yy, xx] and dist[yy, xx] < 0:
                    dist[yy, xx] = d
                    q.append((yy, xx))
    return dist


# ----------------------------------------------------------------------------------------------- scenes
class Scene:
    """O lit photo, P0 pre-light plate (no lamp, no glow), U unlit lamp, pieces, light map T, camera keyframes"""

    def __init__(self, t0, light_at, light_dur, card, cam):
        self.t0, self.light_at, self.light_dur, self.card, self.cam = t0, light_at, light_dur, card, cam
        self.pieces = []
        self.dim = 0.50

    def add_pieces(self, mask, boxes, starts, off=0, flight=0.55, seed=0):
        rng = np.random.default_rng(seed)
        for box, ts in zip(boxes, starts):
            pm = mask & rect_mask(mask.shape, box, off)
            ys, xs = np.where(pm)
            if not len(ys):
                continue
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            a = pm[y0:y1, x0:x1].astype(np.float32)
            a = cv2.GaussianBlur(a, (0, 0), 0.6)            # soft edge, no stair-steps
            rgba = np.dstack([self.U[y0:y1, x0:x1] * a[..., None], a]).astype(np.float32)
            area = (x1 - x0) * (y1 - y0) / (K * K)
            big = min(1.0, area / 2.0e5)
            self.pieces.append(dict(img=rgba, x=x0, y=y0, ts=ts, dur=flight + 0.1 * big,
                                    dx=rng.uniform(-0.35, 0.35) * (1 - 0.5 * big), dy=rng.uniform(0.55, 0.85) * (1 - 0.35 * big),
                                    rot=rng.uniform(18, 34) * rng.choice([-1, 1]) * (1 - 0.6 * big)))


def scene_aurora():
    O = extend_top(load("AC4I9649"), round(1300 * K), round(20 * K), round(120 * K))
    off = 1300
    bar = auto_mask(O, (1030, 205 + off, 2430, 419 + off), 0.10)
    led = bar & (lum(O) > 0.80)
    led = ndimage.binary_dilation(led, iterations=1) & bar
    glow_box = rect_mask(bar.shape, (900, 120, 2560, 1180), off)     # bar + the glow it throws on the wall
    P0, _ = row_fill(O, glow_box)
    U = O.copy()
    U[led] = np.array([0.30, 0.28, 0.25], np.float32)
    s = Scene(0.0, 4 * BEAT, 0.30, ("Aurora wall light", "from ₹1,999"),
              cam=[(0.0, 1730, 1618 + 260 * 1500 / 1080, 1500), (SCENE, 1730, 1618 + 260 * 2300 / 1080, 2300)])
    s.O, s.P0, s.U, s.led = O, P0, U, led
    T = np.zeros(bar.shape, np.float32)                           # Aurora warms up evenly
    s.T = T
    xs = np.linspace(1047, 2412, 8)
    boxes = [(xs[i] - 2, 150 + off, xs[i + 1] + 2, 430 + off) for i in range(7)]
    s.add_pieces(bar, boxes, [0.20 + 0.2 * i for i in range(7)], seed=1)
    return s


def scene_floor():
    O = load("AC4I9777")
    lampm = np.zeros(O.shape[:2], np.uint8)
    cv2.rectangle(lampm, (round(1495 * K), round(2050 * K)), (round(1587 * K), round(4660 * K)), 1, -1)
    cv2.ellipse(lampm, (round(1560 * K), round(4640 * K)), (round(155 * K), round(38 * K)), 0, 0, 360, 1, -1)
    cv2.rectangle(lampm, (round(1405 * K), round(4640 * K)), (round(1715 * K), round(5150 * K)), 1, -1)
    cv2.ellipse(lampm, (round(1560 * K), round(5150 * K)), (round(155 * K), round(30 * K)), 0, 0, 360, 1, -1)
    lampm = lampm.astype(bool)
    rod = rect_mask(lampm.shape, (1495, 2050, 1587, 4660))
    led = rod & (lum(O) > 0.42)
    led = ndimage.binary_dilation(led, iterations=1) & rod
    P0, _ = row_fill(O, ndimage.binary_dilation(lampm, iterations=round(30 * K)))
    U = O.copy()
    U[led] = np.array([0.15, 0.13, 0.115], np.float32)
    s = Scene(SCENE, 4 * BEAT, 0.60, ("Minimalist floor lamp", "from ₹6,999"),
              cam=[(0.0, 1458, 4139, 1500), (3.0, 1200, 3339, 2400), (SCENE + 0.3, 1200, 3339, 2400)])
    s.O, s.P0, s.U, s.led = O, P0, U, led
    s.dim = 0.85                                                  # the room is already dark
    yy = np.arange(lampm.shape[0], dtype=np.float32)[:, None] / K
    frac = np.clip((4660 - yy) / (4660 - 2050), 0, 1) * np.ones(lampm.shape, np.float32)
    s.T = (expo_out_inverse(frac) * s.light_dur).astype(np.float32)
    boxes = [(1380, 4900, 1740, 5200), (1380, 4580, 1740, 4900)]
    seg = np.linspace(4660, 2040, 7)
    boxes += [(1480, seg[i + 1], 1600, seg[i] + 1) for i in range(6)]
    s.add_pieces(lampm, boxes, [0.15, 0.35] + [0.60 + 0.2 * i for i in range(6)], seed=2)
    return s


def scene_glow():
    off = 700
    O = extend_top(load("AC4I9882"), round(off * K), round(60 * K), round(500 * K))
    solid = np.zeros(O.shape[:2], bool)                       # the frame is all straight wood: exact boxes
    for b in [(1535, 880, 2840, 1195), (1535, 1195, 1850, 1680), (1420, 3930, 2700, 4360), (950, 4156, 3170, 4730)]:
        solid |= rect_mask(solid.shape, b, off)
    post = np.zeros(solid.shape, np.uint8)                     # the right post leans 4.4 % in the photo
    quad = np.array([(2494, 1195), (2836, 1195), (2718, 3935), (2370, 3935)], np.float32)
    quad[:, 1] += off
    cv2.fillPoly(post, [np.round(quad * K).astype(np.int32)], 1)
    solid |= post.astype(bool)
    collar = rect_mask(solid.shape, (1590, 1680, 1800, 1762), off)    # brass collar under the left post
    zone = rect_mask(solid.shape, (1050, 1680, 3150, 4100), off)
    core = zone & (lum(O) > 0.80)
    core = ndimage.binary_opening(core, iterations=2)
    lab, n = ndimage.label(core)
    sizes = ndimage.sum(core, lab, range(1, n + 1))
    core = np.isin(lab, 1 + np.where(sizes > 2000 * K * K)[0])  # the rope, including the bits seen past the post
    spiral = ndimage.binary_dilation(core, iterations=round(10 * K)) & zone & ~collar
    frame = solid | collar
    lamp = frame | spiral
    P0, _ = row_fill(O, ndimage.binary_dilation(lamp, iterations=round(14 * K)) |
                     (ndimage.binary_dilation(spiral, iterations=round(130 * K)) & ~rect_mask(lamp.shape, (0, 4150, 3648, 5472), off)))
    U = O.copy()
    hot = frame & (lum(O) > 0.40) & ndimage.binary_dilation(spiral, iterations=round(60 * K))
    hole = ((spiral & frame) | hot).astype(np.uint8)               # wood hidden behind the rope or burnt out by it
    hb = hole.astype(bool)
    for x in np.where(hb.any(0))[0]:                                # along the grain: wood above and below the gap
        col = hb[:, x]
        ys = np.where(col)[0]
        runs = np.split(ys, np.where(np.diff(ys) > 1)[0] + 1)
        for r in runs:
            a, b = r[0] - 3, r[-1] + 3
            if a >= 0 and b < len(col) and frame[a, x] and frame[b, x] and not hb[a, x] and not hb[b, x]:
                tt = np.linspace(0, 1, b - a + 1)[:, None]
                U[a:b + 1, x] = U[a, x] * (1 - tt) + U[b, x] * tt
                hb[a:b + 1, x] = False
    U8 = (np.clip(U, 0, 1) * 255).astype(np.uint8)
    U = cv2.inpaint(U8, hb.astype(np.uint8) * 255, 15, cv2.INPAINT_TELEA).astype(np.float32) / 255
    U = np.where(hole[..., None] > 0, cv2.GaussianBlur(U, (0, 0), sigmaX=0.6, sigmaY=3), U)
    U = np.where(hole[..., None] > 0, U * 0.85, U)                   # it sits in the rope's shadow
    s = Scene(2 * SCENE, 4 * BEAT, 0.80, ("Sculpted Glow lamp", "₹9,999"),
              cam=[(0.0, 2060, 4483, 1900), (3.0, 1824, 3091, 3078), (SCENE + 0.4, 1824, 3091, 3078)])
    s.O, s.P0, s.U = O, P0, U
    s.led = spiral
    s.dim = 0.60
    g = geodesic(spiral, (round(1700 * K), round((1775 + off) * K))).astype(np.float32)
    frac = np.where(g >= 0, g / max(1, g.max()), 0).astype(np.float32)
    miss = spiral & (g < 0)                                        # rope bits not joined to the start: nearest drawn point
    if miss.any():
        _, (iy, ix) = ndimage.distance_transform_edt(~(spiral & (g >= 0)), return_indices=True)
        frac[miss] = frac[iy[miss], ix[miss]]
    s.T = (expo_out_inverse(frac) * s.light_dur).astype(np.float32)
    boxes = [(940, 4150, 1700, 4740), (1700, 4150, 2450, 4740), (2450, 4150, 3180, 4740), (1410, 3890, 2710, 4370)]
    seg = np.linspace(3890, 1195, 4)
    boxes += [(2340, seg[i + 1], 2870, seg[i] + 1) for i in range(3)]
    boxes += [(1525, 870, 2850, 1196), (1525, 1196, 1860, 1760)]
    starts = [0.10, 0.25, 0.40, 0.60, 0.80, 0.98, 1.16, 1.36, 1.55]
    s.add_pieces(frame, boxes, starts, off=off, flight=0.70, seed=3)
    for pc in s.pieces:
        pc["dx"] *= 0.6
        pc["dy"] *= 0.7
    return s


# ----------------------------------------------------------------------------------------------- camera
def cam_at(s, t):
    ks = s.cam
    if t <= ks[0][0]:
        k = ks[0]
    elif t >= ks[-1][0]:
        k = ks[-1]
    else:
        for a, b in zip(ks, ks[1:]):
            if a[0] <= t <= b[0]:
                u = sstep((t - a[0]) / (b[0] - a[0]))
                k = tuple(a[i] + (b[i] - a[i]) * u for i in range(4))
                break
    _, cx, cy, ws = k
    ws *= K
    sc = W / ws
    return cx * K - ws / 2, cy * K - ws * H / W / 2, sc         # window x0, y0 (K px) and scale


def warp(layer, x0, y0, sc, interp=cv2.INTER_LINEAR):
    hgt, wid = layer.shape[:2]
    m = 6
    cx0, cy0 = max(0, int(x0) - m), max(0, int(y0) - m)
    cx1, cy1 = min(wid, int(x0 + W / sc) + m), min(hgt, int(y0 + H / sc) + m)
    crop = layer[cy0:cy1, cx0:cx1]
    if sc < 0.87 and interp == cv2.INTER_LINEAR:                    # pre-blur before shrinking: no shimmer
        crop = cv2.GaussianBlur(crop, (0, 0), 0.42 * (1 / sc - 1) + 0.01)
    M = np.array([[sc, 0, (cx0 - x0) * sc], [0, sc, (cy0 - y0) * sc]], np.float32)
    return cv2.warpAffine(crop, M, (W, H), flags=interp, borderMode=cv2.BORDER_REFLECT)


# ----------------------------------------------------------------------------------------------- particles
class Dust:
    """sawdust in output pixels: specks thrown up where a piece lands, soft puffs, and a slow drift at the start"""

    def __init__(self, seed):
        self.rng = np.random.default_rng(seed)
        self.p = []          # t0, x, y, vx, vy, life, r, col, gravity
        self.puffs = []      # t0, x, y, r

    def burst(self, t, x, y, n=26, spread=1.0):
        r = self.rng
        for _ in range(n):
            ang = r.uniform(-math.pi, 0)
            sp = r.uniform(120, 520) * spread
            col = (0.62, 0.46, 0.30) if r.random() < 0.6 else (0.80, 0.68, 0.52)
            self.p.append((t, x + r.uniform(-60, 60), y, math.cos(ang) * sp, math.sin(ang) * sp * 0.8,
                           r.uniform(0.45, 0.9), r.uniform(1.2, 3.2), col, 700.0))
        self.puffs.append((t, x, y, r.uniform(70, 120) * spread))

    def drift(self, t0, n=70):
        r = self.rng
        for _ in range(n):
            self.p.append((t0 + r.uniform(0, 1.0), r.uniform(0, W), r.uniform(1200, 1950), r.uniform(-40, 40),
                           r.uniform(-260, -90), r.uniform(1.0, 1.8), r.uniform(1.0, 2.6), (0.70, 0.58, 0.42), 0.0))

    def draw(self, frame, t):
        ap = np.zeros((H, W), np.float32)
        for (t0, x, y, r) in self.puffs:
            u = (t - t0) / 0.8
            if 0 <= u <= 1:
                cv2.circle(ap, (int(x), int(y - 30 * u)), int(r * (1 + 1.2 * u)), 0.16 * (1 - u) ** 1.5, -1,
                           cv2.LINE_AA)
        if ap.any():
            ap = cv2.GaussianBlur(ap, (0, 0), 28)[..., None]
            frame = frame * (1 - ap) + np.array([0.80, 0.70, 0.57], np.float32) * ap
        lay = np.zeros((H, W, 3), np.float32)
        al = np.zeros((H, W), np.float32)
        for (t0, x, y, vx, vy, life, r, col, gr) in self.p:
            dt = t - t0
            if 0 <= dt <= life:
                px, py = x + vx * dt, y + vy * dt + 0.5 * gr * dt * dt
                rad = max(1, int(round(r)))
                cv2.circle(lay, (int(px), int(py)), rad, col, -1, cv2.LINE_AA)
                cv2.circle(al, (int(px), int(py)), rad, 0.85 * (1 - dt / life), -1, cv2.LINE_AA)
        al = np.clip(al, 0, 1)[..., None]
        return frame * (1 - al) + lay * al


# ----------------------------------------------------------------------------------------------- render one scene frame
def place(frame, pc, tl, x0, y0, sc, subs):
    """composite one piece (premultiplied RGBA, K px) into the output frame, averaged over motion-blur subsamples"""
    acc = None
    hgt, wid = pc["img"].shape[:2]
    for ts in subs:
        u = (ts - pc["ts"]) / pc["dur"]
        if u < 0:
            continue
        p = quart_out(u)
        ws = W / sc
        ox = pc["dx"] * ws * (1 - p)
        oy = pc["dy"] * ws * H / W * (1 - p)
        th = math.radians(pc["rot"] * (1 - p) ** 1.5)
        cx, cy = pc["x"] + wid / 2 + ox, pc["y"] + hgt / 2 + oy
        c, s_ = math.cos(th) * sc, math.sin(th) * sc
        ocx, ocy = (cx - x0) * sc, (cy - y0) * sc
        M = np.array([[c, -s_, ocx - c * wid / 2 + s_ * hgt / 2], [s_, c, ocy - s_ * wid / 2 - c * hgt / 2]], np.float32)
        corners = np.array([[0, 0, 1], [wid, 0, 1], [0, hgt, 1], [wid, hgt, 1]], np.float32) @ M.T
        bx0, by0 = np.floor(corners.min(0)).astype(int) - 2
        bx1, by1 = np.ceil(corners.max(0)).astype(int) + 2
        bx0, by0, bx1, by1 = max(bx0, 0), max(by0, 0), min(bx1, W), min(by1, H)
        if bx1 <= bx0 or by1 <= by0:
            continue
        M2 = M.copy()
        M2[0, 2] -= bx0
        M2[1, 2] -= by0
        img = pc["img"]
        if sc < 0.87:
            img = cv2.GaussianBlur(img, (0, 0), 0.42 * (1 / sc - 1) + 0.01)
        out = cv2.warpAffine(img, M2, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR)
        if acc is None:
            acc = np.zeros((H, W, 4), np.float32)
        acc[by0:by1, bx0:bx1] += out / len(subs)
    if acc is not None:
        ys, xs = np.where(acc[..., 3] > 0)
        if len(ys):
            y0b, y1b, x0b, x1b = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            a = acc[y0b:y1b, x0b:x1b, 3:4]
            frame[y0b:y1b, x0b:x1b] = frame[y0b:y1b, x0b:x1b] * (1 - a) + acc[y0b:y1b, x0b:x1b, :3]
    return frame


def scene_frame(s, t, dust):
    x0, y0, sc = cam_at(s, t)
    O = warp(s.O, x0, y0, sc)
    A = warp(s.P0, x0, y0, sc)
    shutter = 0.5 / FPS
    for pc in s.pieces:
        moving = pc["ts"] <= t < pc["ts"] + pc["dur"]
        if moving:
            u = (t - pc["ts"]) / pc["dur"]
            speed = 4 * (1 - min(u, 1)) ** 3 / pc["dur"] * pc["dy"] * H          # output px per second, roughly
            n = int(np.clip(speed * shutter / 5, 2, 16))
            subs = [t + shutter * ((i + 0.5) / n - 0.5) for i in range(n)]
        else:
            subs = [t]
        A = place(A, pc, t, x0, y0, sc, subs)
        land = pc["ts"] + pc["dur"] * 0.82
        if not pc.get("landed") and t >= land:
            pc["landed"] = True
            hgt, wid = pc["img"].shape[:2]
            lx = (pc["x"] + wid / 2 - x0) * sc
            ly = (pc["y"] + hgt - y0) * sc
            dust.burst(t, lx, ly, n=22, spread=0.8 + 0.6 * min(1, wid * hgt / 2e5))
            LANDINGS.append(s.t0 + t)
    g = float(sstep((t - s.light_at) / s.light_dur))
    gray = lum(A)[..., None]
    pre = (0.62 * A + 0.38 * gray) * s.dim                           # before: dim, a little grey
    led = warp(s.led.astype(np.float32), x0, y0, sc)[..., None]
    if s.T.any():
        T = warp(s.T, x0, y0, sc)[..., None]
        R = sstep((t - s.light_at - T) / 0.08)
        if 0 < g < 1:                                  # the glow on the room follows the drawn part of the line
            near = cv2.GaussianBlur(led[..., 0], (0, 0), 70)
            rb = cv2.GaussianBlur((R * led)[..., 0], (0, 0), 70) / np.maximum(near, 1e-4)
            wgt = np.clip(near / max(near.max(), 1e-4) * 3, 0, 1)
            gmap = (g * (1 - wgt) + np.minimum(g, rb) * wgt)[..., None]
        else:
            gmap = g
    else:
        R = np.full((H, W, 1), sstep((t - s.light_at) / s.light_dur), np.float32)
        gmap = g
    frame = pre * (1 - gmap) + O * gmap
    lit = pre * (1 - R) + O * R
    return frame * (1 - led) + lit * led


LANDINGS = []
LIGHTS = []


# ----------------------------------------------------------------------------------------------- type
def text_layer(lines, size_px, fnt, fill, x, y, lead=1.05, track=-0.02, align="left", shadow=True):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    yy = y
    for parts in lines:                       # each line: list of (text, font, colour)
        widths = []
        for txt, f, col in parts:
            widths.append(sum(f.getlength(ch) + track * f.size for ch in txt))
        lw = sum(widths)
        xx = x if align == "left" else (W - lw) / 2
        for (txt, f, col), wdt in zip(parts, widths):
            for ch in txt:
                d.text((xx, yy), ch, font=f, fill=col)
                xx += f.getlength(ch) + track * f.size
        yy += size_px * lead
    if shadow:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        a = lay.split()[3].filter(ImageFilter.GaussianBlur(10))
        sh.putalpha(a.point(lambda v: int(v * 0.55)))
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(sh, (3, 6))
        out.alpha_composite(lay)
        return out
    return lay


def card_layer(name, price):
    f1, f2 = font("Inter-600.ttf", 36), font("Inter-600.ttf", 54)
    pad = 28
    w = int(max(f1.getlength(name), f2.getlength(price)) + 2 * pad)
    h = 36 + 12 + 54 + 2 * pad + 6
    x, y = 70, 250
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x + 4, y + 8, x + w + 4, y + h + 8), 26, fill=(20, 12, 6, 110))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(lay).rounded_rectangle((x, y, x + w, y + h), 26, fill=(246, 239, 228, 236))
    d = ImageDraw.Draw(lay)
    d.text((x + pad, y + pad - 4), name, font=f1, fill=INK)
    d.text((x + pad, y + pad + 44), price, font=f2, fill=AMBER_DARK)
    return lay


def scrim_top(h=620, a=0.55):
    y = np.arange(H, dtype=np.float32)
    return (a * sstep(1 - y / h))[:, None, None] * np.ones((1, W, 1), np.float32)


def end_card():
    ground = np.ones((H, W, 3), np.float32) * (TEAK + 0.02)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    ground *= np.clip(1.08 - 0.35 * r, 0, 1.2)[..., None]
    ground += np.random.default_rng(5).normal(0, 2.2 / 255, ground.shape).astype(np.float32)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    lw = 520
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    tint = Image.new("RGBA", logo.size, (246, 239, 228, 255))
    tint.putalpha(logo.split()[3])
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lx, ly = (W - lw) // 2, 560
    sh.alpha_composite(Image.merge("RGBA", (*Image.new("RGB", logo.size, (10, 6, 3)).split(),
                                            logo.split()[3].point(lambda v: int(v * 0.5)))), (lx + 4, ly + 8))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    lay.alpha_composite(tint, (lx, ly))
    fh, fi = font("Fraunces-600.ttf", 92), font("Fraunces-500-i.ttf", 92)
    head = text_layer([[("Solid wood.", fh, (246, 239, 228))],
                       [("Made by ", fh, (246, 239, 228)), ("hand", fi, AMBER), (".", fh, (246, 239, 228))]],
                      92, fh, None, 0, ly + logo.height + 120, align="center", shadow=False)
    lay.alpha_composite(head)
    url = text_layer([[("nixwoods.com", font("Inter-600.ttf", 46), AMBER)]], 46, None, None, 0, 1330,
                     track=0.0, align="center", shadow=False)
    lay.alpha_composite(url)
    return ground, lay


def over(frame, lay, a=1.0):
    arr = np.asarray(lay, np.float32) / 255
    al = arr[..., 3:4] * a
    return frame * (1 - al) + arr[..., :3] * al


# ----------------------------------------------------------------------------------------------- audio
def audio(path_wav):
    sr = 48000
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(AUDIO, "music3-design.mp3"), "-t", f"{DUR:.3f}",
                          "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True).stdout
    mus = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(DUR * sr)
    mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    fade = np.clip((DUR - np.arange(n) / sr) / 0.8, 0, 1)
    mus *= fade[:, None]
    mus /= np.abs(mus).max() + 1e-9
    mix = mus * 0.62
    rng = np.random.default_rng(9)

    def add(sig, t, gain):
        i = int(t * sr)
        j = min(n, i + len(sig))
        if i < n:
            mix[i:j] += sig[:j - i, None] * gain

    for t in LANDINGS:                                         # a dry wooden knock per landing
        L = int(0.16 * sr)
        tt = np.arange(L) / sr
        f = rng.uniform(150, 240)
        body = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.040)
        nz = rng.normal(0, 1, L)
        nz = np.convolve(nz, np.ones(6) / 6, "same") * np.exp(-tt / 0.010)
        add((0.7 * body + 0.5 * nz).astype(np.float32), t, 0.16)
    for t in LIGHTS:                                           # switch click, 0.06 s
        L = int(0.06 * sr)
        tt = np.arange(L) / sr
        click = rng.normal(0, 1, L) * np.exp(-tt / 0.006)
        click[:40] += np.linspace(1, 0, 40)
        add(click.astype(np.float32), t, 0.22)
    wraw = subprocess.run([FF, "-v", "error", "-i", os.path.join(AUDIO, "sfx-whoosh.mp3"), "-ac", "1", "-ar", str(sr),
                           "-f", "f32le", "-"], capture_output=True).stdout
    wh = np.frombuffer(wraw, np.float32).copy()
    wh /= np.abs(wh).max() + 1e-9
    for t, gn in [(0.0, 0.18), (SCENE - 0.25, 0.22), (2 * SCENE - 0.25, 0.22)]:
        add(wh, max(0.0, t), gn)
    mix *= 0.65 / (np.abs(mix).max() + 1e-9)
    pcm = (mix * 32767).astype(np.int16)
    import wave
    with wave.open(path_wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


# ----------------------------------------------------------------------------------------------- main
def grade(f):
    f = np.clip(f, 0, 1) * np.array([1.04, 1.0, 0.93], np.float32)
    return np.clip(f, 0, 1) ** (1 / 1.03)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", help="comma-separated times: write JPEG stills instead of the video")
    a = ap.parse_args()
    print("preparing scenes ...", flush=True)
    scenes = [scene_aurora(), scene_floor(), scene_glow()]
    for s in scenes:
        LIGHTS.append(s.t0 + s.light_at)
    dusts = [Dust(20 + i) for i in range(3)]
    for d in dusts:
        d.drift(0.0)
    fh = font("Fraunces-600.ttf", 92)
    hook = text_layer([[("Built piece", fh, (246, 239, 228))], [("by piece.", fh, (246, 239, 228))]], 92, fh, None,
                      70, 262)
    cards = [card_layer(*s.card) for s in scenes]
    ground, endlay = end_card()
    scrim = scrim_top()

    def frame_at(t):
        if t < END_T + 0.3:
            i = min(2, int(t // SCENE))
            s = scenes[i]
            lt = t - s.t0
            f = scene_frame(s, lt, dusts[i])
            f = dusts[i].draw(f, lt)
            f = grade(f)
            if i == 0:                                             # hook on a top scrim, gone before the light
                ha = sstep((t - 0.05) / 0.12) * (1 - sstep((t - (s.light_at - 0.3)) / 0.25))
                if ha > 0:
                    f = f * (1 - scrim * ha)
                    f = over(f, hook, ha)
            ca = sstep((lt - s.light_at - 0.35) / 0.25)
            if ca > 0:
                f = over(f, cards[i], ca)
            if t >= END_T:
                ea = sstep((t - END_T) / 0.30)
                f = f * (1 - ea) + over(ground, endlay) * ea
            return f
        return END

    END = over(ground, endlay)
    if a.frames:
        outdir = os.path.join(HERE, "stills")
        os.makedirs(outdir, exist_ok=True)
        for ts in [float(v) for v in a.frames.split(",")]:
            # walk the timeline up to ts so the landings and dust are in the right state
            for s in scenes:
                for pc in s.pieces:
                    pc.pop("landed", None)
            for d in dusts:
                d.p = [p for p in d.p if p[8] == 0.0]
                d.puffs = []
            for tt in np.arange(0, ts, 1 / FPS):
                i = min(2, int(tt // SCENE))
                s = scenes[i]
                lt = tt - s.t0
                for pc in s.pieces:
                    land = pc["ts"] + pc["dur"] * 0.82
                    if not pc.get("landed") and lt >= land:
                        pc["landed"] = True
                        x0, y0, sc = cam_at(s, lt)
                        hgt, wid = pc["img"].shape[:2]
                        dusts[i].burst(lt, (pc["x"] + wid / 2 - x0) * sc, (pc["y"] + hgt - y0) * sc, n=22)
            f = frame_at(ts)
            Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).save(
                os.path.join(outdir, f"t{ts:05.2f}.jpg"), quality=90)
            print("still", ts, flush=True)
        return

    tmp_v = os.path.join(HERE, "_video.mp4")
    tmp_a = os.path.join(HERE, "_audio.wav")
    p = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt",
                          "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          tmp_v], stdin=subprocess.PIPE)
    nf = int(round(DUR * FPS))
    for k in range(nf):
        f = frame_at(k / FPS)
        p.stdin.write((np.clip(f, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if k % 30 == 0:
            print(f"frame {k}/{nf}", flush=True)
    p.stdin.close()
    p.wait()
    audio(tmp_a)
    out = os.path.join(HERE, NAME + ".mp4")
    subprocess.run([FF, "-y", "-v", "error", "-i", tmp_v, "-i", tmp_a, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(tmp_v)
    os.remove(tmp_a)
    print("wrote", out)


if __name__ == "__main__":
    main()
