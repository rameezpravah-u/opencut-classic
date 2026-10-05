#!/usr/bin/env python3
"""NixLine — 15 s motion piece #2.  "trace."

The light writes. Five techniques, none used in "one line":

  A  slit-scan       every row of the frame is a different moment of the lamp being turned, so the
                     turn twists into a helix of teak and light; the light sweeps up from the bottom
  B  light painting  the LED is keyed and accumulated with decay while the lamp tilts from vertical
                     to horizontal - a long exposure, a fan drawn in light
  C  type behind     a giant serif word sits behind the lamp; the lit channel is keyed back in front
     light
  D  strobe          the drop: twelve half-beat flashes, one word each
  E  written in      a glowing pen traces the real glyph outlines of "nixline" (Space Grotesk 700,
     light           read with fontTools), pen-up between contours, then the word fills

Music: music3-design, 99.4 BPM (beat 0.6036 s). The track has a quiet intro and a drop on the
downbeat at 10.752 s (phase 0.490 s, measured on the loud section where the kick is clean). It
starts at 2.905 s so the drop lands on output beat 13 = the first strobe flash, and every output
beat k*B coincides with a beat in the track. A-C sit on the quiet intro; D is the drop.

Claims, all from the live PDP: solid teak, no MDF, no veneer, 30 inches, 2700-3000K warm LED,
plug in and place, handcrafted. Footage all Rameez's own. The trails in B and the time-warp in A
are visual effects on real footage, not product behaviour - no caption claims them as a demo.

    python3 floor-reels/motion/nixline_trace.py
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nixline_motion as M          # palette, type, grade, glow, readers - verified in "one line"
from nixline_motion import (W, H, FPS, INK, CREAM, AMBER, X0, Reader, SRC, grade, push, vline, hline,
                            bloom, word_img, Line, paste, legible, F, GROT, GROT_B, SERIF_I, INTER, INTER_L,
                            clamp, prog, out_expo, in_expo, out_cubic, inout_cubic, out_back, ASSET, OUT, ROOT, FF)

DUR = 15.0; N = int(DUR * FPS)
B = 60 / 99.4
def beat(k): return k * B
MUSIC_OFF = 10.752 - beat(13)                       # drop -> beat 13

C = (243, 237, 227); A = (255, 198, 124); G = (138, 129, 120)

# ================================================================ A  slit-scan
SLIT_T0, SLIT_T1 = 3.30, 7.15                       # nx06: teak faces camera 3.3-5.7, light at 6.0
SLIT_SPAN = 1.60                                    # top row lags the bottom row by this much
def slit_base(t): return 4.90 + t * 0.90             # 4.90-1.60 = 3.30 (buffer start); 4.90+0.9*2.41 = 7.07 (< 7.15)
SLITBUF = None
def load_slit():
    global SLITBUF
    r = Reader(SRC("nx06-7921.mp4"), SLIT_T0, SLIT_T1 - SLIT_T0 - .25)
    n = int((SLIT_T1 - SLIT_T0) * FPS)
    SLITBUF = np.empty((n, H, W, 3), np.uint8)
    for i in range(n):
        SLITBUF[i] = r.at(i / FPS)
    print(f"slit-scan buffer {SLITBUF.nbytes / 1e6:.0f} MB")

ROWS = np.arange(H)
def slitscan(t):
    src = slit_base(t) - (1 - ROWS / H) * SLIT_SPAN           # bottom row is "now", top row is the past
    fi = (src - SLIT_T0) * FPS
    fi = np.clip(fi, 0, len(SLITBUF) - 1.001)
    i0 = fi.astype(int); fr = (fi - i0)[:, None, None]
    a = SLITBUF[i0, ROWS].astype(np.float32); b = SLITBUF[i0 + 1, ROWS].astype(np.float32)
    return (a * (1 - fr) + b * fr).clip(0, 255).astype(np.uint8)

# ================================================================ B  light painting
TRAIL = None
WARM = np.array([255, 186, 112], np.float32)
def shoulder(f, knee=188.0, room=67.0):
    """Roll highlights off toward 255 instead of clipping - additive light stacks up fast."""
    over = np.maximum(f - knee, 0)
    return np.where(f > knee, knee + room * (1 - np.exp(-over / room)), f)
def luma(u8): return u8[..., 0] * .2126 + u8[..., 1] * .7152 + u8[..., 2] * .0722
def light_key(u8, lo=185, hi=245):
    L = luma(u8.astype(np.float32))
    return np.clip((L - lo) / (hi - lo), 0, 1) ** 1.5

def glow_of(img, rad=10, gain=.9):
    """Cheap wide glow: blur at quarter resolution, upsample."""
    small = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    small = small.filter(ImageFilter.GaussianBlur(rad))
    return np.asarray(small.resize((W, H), Image.BILINEAR)).astype(np.float32) * gain

# ================================================================ C  type behind light
BIGWORD = None
def make_bigword():
    global BIGWORD
    size = 560
    while True:
        f = F(SERIF_I, size)
        if f.getlength("teak.") <= 850: break                 # inside x 70-950, clear of the action rail
        size -= 10
    img, pad, asc = word_img("teak.", f, C, shadow=False)
    BIGWORD = (img, pad, asc, f.getlength("teak."))

# ================================================================ D  strobe
STROBE = [  # (word, accent?, clip, ss)
    ("solid",   False, "nx01-7923.mp4", 0.40), ("teak.",     True, "nx05-7920.mp4", 0.30),
    ("no mdf.", False, "nx08-7924.mp4", 1.00), ("no veneer.", True, "nx00-hero.mp4", 6.60),
    ("30",      False, "nx03-7926.mp4", 0.40), ("inches.",   True, "nx04-7930.mp4", 1.20),
    ("2700–",   False, "nx01-7923.mp4", 1.60), ("3000k.",    True, "nx02-7925.mp4", 0.60),
    ("plug in.", False, "nx08-7924.mp4", 2.40), ("place.",   True, "nx00-hero.mp4", 1.70),
    ("hand",    False, "nx05-7920.mp4", 3.40), ("crafted.",  True, "nx06-7921.mp4", 4.20),
]
STROBE_IMG = []
def make_strobe():
    for word, acc, _, _ in STROBE:
        font_name = SERIF_I if acc else GROT_B
        size = 300 if acc else 250
        while F(font_name, size).getlength(word) > 860: size -= 8
        STROBE_IMG.append(word_img(word, F(font_name, size), A if acc else C))
    print("strobe word sizes ok")

# ================================================================ E  written in light
class FlatPen(BasePen):
    """Flattens TrueType outlines (quadratic) into polylines, one list per contour."""
    def __init__(self, gs, steps=14):
        super().__init__(gs); self.contours, self.cur, self.steps = [], None, steps
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _qCurveToOne(self, p1, p2):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            u = i / self.steps
            self.cur.append(((1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u*u*p2[0], (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u*u*p2[1]))
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for i in range(1, self.steps + 1):
            u = i / self.steps; v = 1 - u
            self.cur.append((v**3*p0[0] + 3*v*v*u*p1[0] + 3*v*u*u*p2[0] + u**3*p3[0],
                             v**3*p0[1] + 3*v*v*u*p1[1] + 3*v*u*u*p2[1] + u**3*p3[1]))
    def _closePath(self):
        if self.cur:
            self.cur.append(self.cur[0]); self.contours.append(self.cur); self.cur = None
    _endPath = _closePath

WORDMARK = "nixline"
PATH = None; PATH_LEN = None; WM_FILL = None; WM_BOX = None
def make_writeon():
    global PATH, PATH_LEN, WM_FILL, WM_BOX
    tt = TTFont(os.path.join(ASSET, GROT_B)); gs = tt.getGlyphSet(); cmap = tt.getBestCmap()
    upm = tt["head"].unitsPerEm; hmtx = tt["hmtx"]
    contours, x = [], 0
    for ch in WORDMARK:
        g = cmap[ord(ch)]
        pen = FlatPen(gs); gs[g].draw(pen)
        for c in pen.contours: contours.append([(px + x, py) for px, py in c])
        x += hmtx[g][0]
    allp = np.concatenate([np.array(c) for c in contours])
    target_w = 800
    s = target_w / (allp[:, 0].max() - allp[:, 0].min())
    ox = (W - target_w) / 2 - allp[:, 0].min() * s
    cy = 980
    oy = cy + (allp[:, 1].max() + allp[:, 1].min()) / 2 * s
    PATH = [np.column_stack([np.array(c)[:, 0] * s + ox, oy - np.array(c)[:, 1] * s]) for c in contours]
    seg = [np.r_[0, np.cumsum(np.hypot(*np.diff(c, axis=0).T))] for c in PATH]
    PATH_LEN = seg
    # the same word, filled, for the settle - drawn from the same outlines so stroke and fill register
    m = Image.new("L", (W, H), 0); d = ImageDraw.Draw(m)
    # even-odd fill via XOR of each contour gives correct counters (holes in e)
    acc = np.zeros((H, W), bool)
    for c in PATH:
        t = Image.new("L", (W, H), 0); ImageDraw.Draw(t).polygon([tuple(p) for p in c], fill=255)
        acc ^= np.asarray(t) > 127
    WM_FILL = acc.astype(np.float32)
    ys, xs = np.where(acc); WM_BOX = (xs.min(), ys.min(), xs.max(), ys.max())
    total = sum(l[-1] for l in seg)
    print(f"wordmark: {len(PATH)} contours, {sum(len(c) for c in PATH)} points, path {total:.0f}px, box {WM_BOX}")

def draw_path(d_target):
    """Rasterise the outline up to distance d_target along the pen's route. Returns (mask, head)."""
    m = Image.new("L", (W, H), 0); dr = ImageDraw.Draw(m)
    left, head = d_target, None
    for c, cl in zip(PATH, PATH_LEN):
        if left <= 0: break
        if left >= cl[-1]:
            dr.line([tuple(p) for p in c], fill=255, width=5, joint="curve"); left -= cl[-1]; head = c[-1]
        else:
            k = int(np.searchsorted(cl, left))
            pts = [tuple(p) for p in c[:k]]
            f = (left - cl[k - 1]) / max(cl[k] - cl[k - 1], 1e-6)
            end = c[k - 1] + (c[k] - c[k - 1]) * f
            pts.append(tuple(end))
            if len(pts) > 1: dr.line(pts, fill=255, width=5, joint="curve")
            head = end; left = 0
    return np.asarray(m).astype(np.float32) / 255, head

LOGO = M.LOGO
TAG = word_img("solid teak floor lamp", F(INTER_L, 50), C, shadow=False)
URL = word_img("NIXWOODS.COM", F(INTER, 34), (232, 162, 74), track=7, shadow=False)
KICK = word_img("NIXLINE", F(INTER, 30), C, track=10)

T_HOOK1 = Line([("watch one line", F(GROT, 96), C)], X0, 1300)
T_HOOK2 = Line([("of ", F(GROT, 96), C), ("light.", F(SERIF_I, 140), A)], X0, 1440)
T_SLIM  = Line([("a slim column of solid teak.", F(GROT, 50), C)], X0, 1420)

READERS = {}
def reader(key, path, ss, need):
    if key not in READERS: READERS[key] = Reader(SRC(path), ss, need)
    return READERS[key]

# ================================================================ the frame
def frame(k):
    global TRAIL
    t = k / FPS

    # ---- A  slit-scan: the turn becomes a twist, the light sweeps up the frame
    if t < beat(4):
        src = slitscan(t)
        f = grade(push(src, 1.10 - .06 * out_cubic(prog(t, 0, beat(4))), .5, .45), k)
        # a cold open: fade up from ink over the first 0.25 s, the light line drawn first
        up = out_cubic(prog(t, 0, .35))
        f = f * up + INK * (1 - up)
        legible(f)
        T_HOOK1.draw(f, t, .15, t_out=beat(4) - .25)
        T_HOOK2.draw(f, t, .45, t_out=beat(4) - .25, rise=46)
        return f

    # ---- B  light painting: the lamp tilts and leaves a fan of light
    if t < beat(8):
        lt = t - beat(4)
        src = reader("paint", "nx07-7922.mp4", .25, beat(8) - beat(4)).at(lt)
        key = light_key(src, 222, 252)[..., None] ** 1.4           # the hottest core of the channel only
        lit = key * WARM * .62
        TRAIL = lit if TRAIL is None else np.maximum(TRAIL * .925, lit)
        base = grade(push(src, 1.04, .5, .5), k) * .40
        f = shoulder(base + TRAIL + glow_of(TRAIL, 10, .75))
        # brand kicker breathes in and out - this section is for looking, not reading
        ki, kp, _ = KICK
        ka = out_cubic(prog(t, beat(4) + .3, .5)) * (1 - prog(t, beat(8) - .35, .3))
        paste(f, ki, (W - ki.shape[1]) / 2, 300 - kp, ka * .85)
        return f

    # ---- C  type behind light: a giant word, the lit channel keyed back over it
    if t < beat(13):
        lt = t - beat(8)
        src = reader("behind", "nx06-7921.mp4", 6.40, beat(13) - beat(8)).at(lt)
        f = grade(push(src, 1.03 + .04 * prog(t, beat(8), 5 * B), .5, .42), k) * .82
        img, pad, asc, wd = BIGWORD
        p = out_expo(prog(t, beat(8) + .05, .7))
        drift = 1 + .05 * prog(t, beat(8), 5 * B)
        if drift > 1.001:
            im = Image.fromarray(img.astype(np.uint8), "RGBA")
            im = im.resize((int(img.shape[1] * drift), int(img.shape[0] * drift)), Image.BILINEAR)
            big = np.asarray(im).astype(np.float32)
        else:
            big = img
        bx = (M.SAFE_L + M.SAFE_R) / 2 - big.shape[1] / 2; by = 760 - big.shape[0] / 2 + (1 - p) * 120
        paste(f, big, bx, by, p * .96)
        # the light, back in front of the word
        key = light_key(src, 200, 245)
        key = np.asarray(Image.fromarray((key * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[..., None] / 255
        gsrc = grade(push(src, 1.03 + .04 * prog(t, beat(8), 5 * B), .5, .42), k)
        f = f * (1 - key) + gsrc * key + glow_of(gsrc * key, 8, .9)
        f = shoulder(f)
        # build into the drop: a white-out on the last half-beat
        f += 255 * in_expo(prog(t, beat(13) - .18, .18)) * .55
        return f

    # ---- D  the drop: twelve half-beat flashes
    if t < beat(19):
        i = int((t - beat(13)) / (B / 2)); i = min(i, len(STROBE) - 1)
        t_in = beat(13) + i * B / 2; lt = t - t_in
        word, acc, clip, ss = STROBE[i]
        src = reader(f"strobe{i}", clip, ss, B / 2 + .05).at(lt)
        punch = 1.16 - .12 * out_expo(prog(lt, 0, B / 2))
        f = grade(push(src, punch, .5, .5), k) * .62
        f += 255 * .35 * math.exp(-lt / .05)                         # onset flash
        img, pad, asc = STROBE_IMG[i]
        sc = 1 + .08 * (1 - out_expo(prog(lt, 0, .2)))
        if sc > 1.002:
            im = Image.fromarray(img.astype(np.uint8), "RGBA").resize((int(img.shape[1] * sc), int(img.shape[0] * sc)), Image.BILINEAR)
            img2 = np.asarray(im).astype(np.float32)
        else:
            img2 = img
        paste(f, img2, (W - img2.shape[1]) / 2, 880 - img2.shape[0] / 2, 1.0)
        # a beat-counter rule across the bottom: twelve ticks filling in
        for j in range(12):
            x0 = X0 + j * (W - 2 * X0) / 12
            on = j <= i
            hline(f, 1450, x0 + 4, x0 + (W - 2 * X0) / 12 - 4, .85 if on else .18, core=2, sig=6)
        return f

    # ---- E  written in light
    f = np.empty((H, W, 3), np.float32); f[:] = INK
    t_w0, t_w1 = beat(19) + .15, beat(19) + .15 + 1.85
    total = sum(l[-1] for l in PATH_LEN)
    d = total * inout_cubic(prog(t, t_w0, t_w1 - t_w0))
    if d > 0:
        mask, head = draw_path(d)
        settle = out_cubic(prog(t, t_w1 - .05, .45))
        stroke = mask[..., None] * (CREAM * .35 + AMBER * .65 + 30)
        g = glow_of(stroke, 7, 1.25)
        f += (stroke + g) * (1 - .55 * settle)
        if head is not None and t < t_w1:
            bloom(f, head[0], head[1], 22, .95); bloom(f, head[0], head[1], 70, .35)
        if settle > 0:
            fill = WM_FILL[..., None]
            f = f * (1 - fill * settle) + CREAM * fill * settle
    # underline - the line comes back one last time
    if t > t_w1:
        x0b, y0b, x1b, y1b = WM_BOX
        u = out_expo(prog(t, t_w1 + .1, .6))
        mid = (x0b + x1b) / 2; half = (x1b - x0b) / 2 * u
        hline(f, y1b + 46, mid - half, mid + half, .95, core=4, sig=22)
    la = out_cubic(prog(t, t_w1 + .25, .5))
    paste(f, LOGO, (W - LOGO.shape[1]) / 2, 640 + (1 - la) * 24, la)
    ti, tp, _ = TAG
    ta = out_cubic(prog(t, t_w1 + .5, .45))
    paste(f, ti, (W - ti.shape[1]) / 2, WM_BOX[3] + 80 + (1 - ta) * 20, ta)
    ui, up, _ = URL
    paste(f, ui, (W - ui.shape[1]) / 2, WM_BOX[3] + 160, out_cubic(prog(t, t_w1 + .75, .45)))
    return f


def setup():
    load_slit(); make_bigword(); make_strobe(); make_writeon()


def main():
    setup()
    silent = os.path.join(OUT, "_trace.mp4")
    enc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                            "-color_trc", "bt709", silent], stdin=subprocess.PIPE)
    for k in range(N):
        enc.stdin.write(frame(k).clip(0, 255).astype(np.uint8).tobytes())
        if k % 45 == 0: print(f"  frame {k}/{N}  t={k / FPS:5.2f}s", flush=True)
    enc.stdin.close(); enc.wait()
    aud = os.path.join(ROOT, "audio")
    master = os.path.join(OUT, "_trace_master.mp4")
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", silent,
                    "-ss", f"{MUSIC_OFF:.3f}", "-t", str(DUR), "-i", os.path.join(aud, "music3-design.mp3"),
                    "-i", os.path.join(aud, "sfx-whoosh.mp3"), "-i", os.path.join(aud, "sfx-whoosh.mp3"),
                    "-filter_complex",
                    "[1:a]volume=0dB,afade=t=in:d=0.25,afade=t=out:st=14.1:d=0.9[m];"
                    f"[2:a]adelay={int((beat(4) - .15) * 1000)}|{int((beat(4) - .15) * 1000)},volume=-12dB[w1];"
                    f"[3:a]adelay={int((beat(19) - .1) * 1000)}|{int((beat(19) - .1) * 1000)},volume=-10dB[w2];"
                    "[m][w1][w2]amix=inputs=3:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", str(DUR), master], check=True)
    os.remove(silent)
    print("done", master)


if __name__ == "__main__":
    main()
