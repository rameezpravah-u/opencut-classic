#!/usr/bin/env python3
"""Double Arm Teak pendant - installation, as a CGI motion piece.

Structure taken from a reference reel (steelhaus.in, Dd8M4uqMXHe): product-only CGI on a seamless
ground, rigid shot grid, hard cuts, one slow camera move per shot, wordmark end card. Only the
structure is borrowed - every frame here is rendered from our own model.

Content is NixWoods' own installation guide, nixwoods.com/pages/installation-video, steps quoted:
  1 Mark the position · 2 Drill and plug · 3 Fix the canopy, check it sits level ·
  4 Attach the suspension wire (the one you fit, at both ends) · 5 Seat the 2-in-1 wire (already
  runs from your light) · 6 Your electrician connects the supply · 7 Level it and set the height,
  both wires the same length · 8 Power on and use your remote, already paired · 9 Final check.
  Safety: power off at the MCB first. Height over a dining table: 75-90 cm above the tabletop.
The electrical connection is shown as a label only - no wiring is drawn.

Model: pendant3d.py (49 x 2 x 3 in teak bar, twin channels, teak canopy, black wires - from the PDP
and the real photographs). Canopy fixing points are not documented and are placed by eye.

Music: music6-corners, 71.8 BPM (beat 0.8357 s, phase 0.396 s). Shots are 4 beats.
"""
import os, sys, math, subprocess, glob
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pendant3d as R
sys.path.insert(0, os.path.join(HERE, "..", "..", "floor-reels", "motion"))
from nixline_motion import (F, word_img, paste, GROT, GROT_B, INTER, INTER_L, ASSET, FF,
                            clamp, prog, out_expo, in_expo, out_cubic, inout_cubic)

W, H, FPS = 1080, 1920, 30
B = 60 / 71.8; L = 4 * B
DUR = 5 * L + 2 * B
N = int(round(DUR * FPS))
SS = 1.25
FRAMES = os.path.join(HERE, "_frames"); os.makedirs(FRAMES, exist_ok=True)
OUTDIR = os.path.join(HERE, "..", "out", "motion"); os.makedirs(OUTDIR, exist_ok=True)

CY = 34.0                                   # ceiling
CAN_Y = CY - R.CAN_HH                       # canopy flush
FIT_CAN = CY - 2 * R.CAN_HH - R.GRIP_HH     # fitting under the canopy
BAR_Y = 6.0                                 # hung
TABLE = BAR_Y - R.BAR_HH - 32.0             # 32 in = ~81 cm, inside the guide's 75-90 cm

INK = (26, 22, 20); WOOD = (154, 91, 42); GREY = (138, 129, 120)

def lerp(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b)) if isinstance(a, tuple) else a + (b - a) * u

# ---------------------------------------------------------------- shots: return (P, cam)
def shotA(t):            # 01-02  mark · drill · plug
    rise = out_cubic(prog(t, .15, .85)); away = in_expo(prog(t, 1.55, .6))
    can_y = lerp(CAN_Y - 7, CAN_Y, rise) - 9 * away
    can_z = 14 * away
    marks_a = out_cubic(prog(t, 1.1, .3))
    pl = out_expo(prog(t, 2.05, .9))
    py = lerp(CY - 7.5, CY - .15, pl)
    P = R.params(bar=(0, -500, 0), can=(0, can_y, can_z), cables=False, ceiling=CY,
                 marks=[(-R.SCREW_X, 0), (R.SCREW_X, 0)], marks_a=marks_a,
                 plugs=[(-R.SCREW_X, py, 0), (R.SCREW_X, py, 0)] if t > 2.0 else None,
                 grips=[(0, -500, 0)] * 2 + [(-R.CABLE_X, can_y - R.CAN_HH - R.GRIP_HH, can_z), (R.CABLE_X, can_y - R.CAN_HH - R.GRIP_HH, can_z)])
    eye = lerp((10.3, -0.4, 38.5), (8.4, 1.2, 35.8), t / L)          # solved: canopy inside x .12-.90, y .44-.54
    return P, R.look(eye, (0, 33.0, 0), 48)

def shotB(t):            # 03  fix the canopy · check it sits level
    rise = out_cubic(prog(t, .1, .8))
    can_y = lerp(CAN_Y - 4.5, CAN_Y, rise)
    sc = out_expo(prog(t, .95, 1.0))
    head_y = lerp(CY - 8, CAN_Y - R.CAN_HH - R.HEAD_HH, sc)
    spin = 18 * out_cubic(prog(t, .95, 1.2))
    fit = can_y - R.CAN_HH - R.GRIP_HH
    P = R.params(bar=(0, -500, 0), can=(0, can_y, 0), cables=False, ceiling=CY,
                 screws=[(-R.SCREW_X, head_y, 0), (R.SCREW_X, head_y, 0)], screw_spin=spin,
                 grips=[(0, -500, 0)] * 2 + [(-R.CABLE_X, fit, 0), (R.CABLE_X, fit, 0)])
    eye = lerp((11.2, 26.4, 8.6), (10.0, 27.2, 7.4), t / L)
    return P, R.look(eye, (R.SCREW_X, 32.4, 0), 36)

def shotC(t):            # 04-05  fit the suspension wire · seat the 2-in-1
    a = out_cubic(prog(t, .15, 1.2)); b = out_cubic(prog(t, 1.55, 1.2))
    top_a = lerp(FIT_CAN - 5.5, FIT_CAN - R.GRIP_HH, a)
    top_b = lerp(FIT_CAN - 5.5, FIT_CAN - R.GRIP_HH, b)
    P = R.params(bar=(0, -500, 0), can=(0, CAN_Y, 0), ceiling=CY,
                 screws=[(-R.SCREW_X, CAN_Y - R.CAN_HH - R.HEAD_HH, 0), (R.SCREW_X, CAN_Y - R.CAN_HH - R.HEAD_HH, 0)], screw_spin=18,
                 grips=[(0, -500, 0)] * 2 + [(-R.CABLE_X, FIT_CAN, 0), (R.CABLE_X, FIT_CAN, 0)],
                 cableA=((R.CABLE_X, top_a, 0), (R.CABLE_X, top_a - 40, 0)),
                 cableB=((-R.CABLE_X, top_b, 0), (-R.CABLE_X, top_b - 40, 0)))
    u = inout_cubic(prog(t, 1.15, 2.1))
    eye = lerp((12.6, 29.4, 5.4), (16.5, 14.9, 61.6), u)            # wide end solved: both fittings in frame
    tgt = lerp((8.7, 32.0, 0), (0.0, 32.0, 0), u)
    return P, R.look(eye, tgt, lerp(32., 40., u))

def hung(bar_y, led=0.):
    top = bar_y + R.BAR_HH + R.GRIP_HH
    return R.params(bar=(0, bar_y, 0), can=(0, CAN_Y, 0), ceiling=CY, led=led, table=TABLE,
                    screws=[(-R.SCREW_X, CAN_Y - R.CAN_HH - R.HEAD_HH, 0), (R.SCREW_X, CAN_Y - R.CAN_HH - R.HEAD_HH, 0)], screw_spin=18,
                    grips=[(-R.CABLE_X, top, 0), (R.CABLE_X, top, 0), (-R.CABLE_X, FIT_CAN, 0), (R.CABLE_X, FIT_CAN, 0)],
                    cableA=((R.CABLE_X, FIT_CAN - R.GRIP_HH, 0), (R.CABLE_X, top + R.GRIP_HH, 0)),
                    cableB=((-R.CABLE_X, FIT_CAN - R.GRIP_HH, 0), (-R.CABLE_X, top + R.GRIP_HH, 0)))

def shotD(t):            # 06  electrician · 07  set the height
    y = lerp(CAN_Y - 9.5, BAR_Y, inout_cubic(prog(t, .2, 1.9)))
    eye = lerp((-31., -3., 94.), (-29., -4., 90.), t / L)
    return hung(y), R.look(eye, (0, -3.5, 0), 46)

def shotE(t):            # 08  power on · remote   09  final check
    on = out_cubic(prog(t, .35, .18))
    dim = 1 - .62 * math.sin(math.pi * clamp((t - 1.45) / 1.15)) ** 2
    eye = lerp((8., -23., 33.), (4., -25., 35.), t / L)
    return hung(BAR_Y, on * dim), R.look(eye, (0, 2.5, 0), 48)

SHOTS = [shotA, shotB, shotC, shotD, shotE]

# ---------------------------------------------------------------- overlays (on the seamless cream ground)
def W_(text, font, col): return word_img(text, font, col, shadow=False)
NUM = F(GROT_B, 112); TXT = F(GROT, 58); HOOK = F(GROT, 74); KICK = F(INTER, 30)
def kick(text, col=INK): return word_img(text.upper(), KICK, col, track=5, shadow=False)

class Card:
    """Step number plus one or two lines, rising in with a stagger."""
    def __init__(self, num, lines, y=330, x=96):
        self.items = []
        if num:
            self.items.append((W_(num, NUM, WOOD), x, y))
            y += 128
        for ln in lines:
            self.items.append((W_(ln, TXT, INK), x, y)); y += 74
    def draw(self, f, t, t_in, t_out=None):
        for i, ((img, pad, asc), x, y) in enumerate(self.items):
            p = out_cubic(prog(t, t_in + i * .07, .4)); a = p; dy = (1 - p) * 26
            if t_out is not None:
                q = prog(t, t_out, .2); a *= 1 - q; dy -= q * 14
            if a > .004: paste(f, img, x - pad, y - pad + dy, a)

HOOK_L = [W_("before you drill,", HOOK, INK), W_("watch this.", HOOK, INK)]
SAFE = kick("power off at the MCB first")
CARDS = {
    "A": Card("01–02", ["mark. drill. plug."], y=1150),
    "B1": Card("03", ["fix the canopy."], y=1150),
    "B2": Card("", ["check it sits level."], y=1150 + 128 + 74),
    "C1": Card("04", ["fit the suspension", "wire."], y=1150),
    # x=220: the left wire's screen path through this band, measured over the dolly, ends at x=179
    "C2": Card("05", ["seat the 2-in-1", "wire."], y=1150, x=220),
    "D1": Card("06", ["your electrician", "connects the supply."], y=960),
    "D2": Card("07", ["set both wires to", "the same length."], y=960),
    "E1": Card("08", ["power on. the remote", "is already paired."], y=1150),
    "E2": Card("09", ["final check: screws", "tight, wires locked."], y=1150),
}
DIM_LBL = W_("75–90 cm", F(GROT_B, 64), WOOD); DIM_SUB = kick("above the table", GREY)

def level_widget(f, t, t_in):
    """A spirit level, drawn: the bubble settles to centre and the tick turns warm."""
    a = out_cubic(prog(t, t_in, .3))
    if a <= 0: return
    from PIL import ImageDraw
    w, h = 420, 64; x0, y0 = 96, 1440
    im = Image.new("RGBA", (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 10 + w, 10 + h), radius=h // 2, outline=INK + (255,), width=4)
    settle = out_expo(prog(t, t_in + .25, .9))
    bx = 10 + w / 2 + (1 - settle) * 120 * math.cos((t - t_in) * 9) * (1 - settle)
    col = tuple(int(c) for c in np.array(GREY) * (1 - settle) + np.array(WOOD) * settle)
    d.ellipse((bx - 26, 10 + h / 2 - 22, bx + 26, 10 + h / 2 + 22), fill=col + (255,))
    d.line((10 + w / 2 - 40, 14, 10 + w / 2 - 40, 10 + h - 4), fill=INK + (255,), width=3)
    d.line((10 + w / 2 + 40, 14, 10 + w / 2 + 40, 10 + h - 4), fill=INK + (255,), width=3)
    paste(f, np.asarray(im).astype(np.float32), x0 - 10, y0 - 10, a)

def project(cam, X):
    e, fw, r, u, th = cam[0:3], cam[3:6], cam[6:9], cam[9:12], cam[12]
    v = np.array(X) - e; z = v @ fw
    return ((v @ r) / (z * th * W / H) + 1) / 2 * W, (1 - (v @ u) / (z * th)) / 2 * H

def dimension(f, t, t_in, cam):
    a = out_cubic(prog(t, t_in, .35))
    if a <= 0: return
    x3 = R.BAR_HL + 4.0
    xs, ytop = project(cam, (x3, BAR_Y - R.BAR_HH, 0)); _, ybot = project(cam, (x3, TABLE, 0))
    d = out_expo(prog(t, t_in, .6)); yb = ytop + (ybot - ytop) * d
    xs = min(xs, 940)
    f[int(ytop):int(yb), int(xs) - 2:int(xs) + 2] = f[int(ytop):int(yb), int(xs) - 2:int(xs) + 2] * (1 - a) + np.array(WOOD) * a
    for yy in (ytop, yb if d > .97 else None):
        if yy is not None: f[int(yy) - 2:int(yy) + 2, int(xs) - 22:int(xs) + 22] = f[int(yy) - 2:int(yy) + 2, int(xs) - 22:int(xs) + 22] * (1 - a) + np.array(WOOD) * a
    img, pad, _ = DIM_LBL
    la = a * out_cubic(prog(t, t_in + .35, .3))
    ly = max(ytop + (ybot - ytop) * .72, 1250)             # below the step text block (ends ~1180)
    paste(f, img, xs - 26 - img.shape[1] + pad, ly - 70 - pad, la)
    si, sp, _ = DIM_SUB; paste(f, si, xs - 26 - si.shape[1] + sp, ly + 6 - sp, la)

def overlay(f, shot, t, cam):
    if shot == 0:
        for i, (img, pad, asc) in enumerate(HOOK_L):
            p = out_cubic(prog(t, .12 + i * .1, .4)); a = p * (1 - prog(t, 1.45, .2))
            paste(f, img, 96 - pad, 300 + i * 90 - pad + (1 - p) * 26, a)
        si, sp, _ = SAFE; paste(f, si, 96 - sp, 300 + 200 - sp, out_cubic(prog(t, .55, .4)))
        CARDS["A"].draw(f, t, 1.6)
    elif shot == 1:
        CARDS["B1"].draw(f, t, .1); CARDS["B2"].draw(f, t, 1.95); level_widget(f, t, 2.0)
    elif shot == 2:
        CARDS["C1"].draw(f, t, .1, t_out=1.45); CARDS["C2"].draw(f, t, 1.6)
    elif shot == 3:
        CARDS["D1"].draw(f, t, .1, t_out=1.5); CARDS["D2"].draw(f, t, 1.65); dimension(f, t, 2.0, cam)
    elif shot == 4:
        CARDS["E1"].draw(f, t, .15, t_out=1.75); CARDS["E2"].draw(f, t, 1.9)

# ---------------------------------------------------------------- end card
LOGO = np.asarray(Image.open(os.path.join(ASSET, "logo.png")).convert("RGBA").resize((230, 163), Image.LANCZOS)).astype(np.float32)
LOGO[..., :3] = np.array(INK, np.float32)                     # the white logo, inked for a light ground
E_NAME = W_("double arm teak pendant", F(GROT, 60), INK)
E_FULL = kick("full guide", GREY)
E_URL = W_("nixwoods.com/pages/installation-video", F(INTER, 34), WOOD)
CREAM8 = np.array([243, 237, 227], np.float32)

def end_card(t):
    f = np.empty((H, W, 3), np.float32); f[:] = CREAM8
    la = out_cubic(prog(t, .05, .45)); paste(f, LOGO, (W - LOGO.shape[1]) / 2, 680 + (1 - la) * 20, la)
    for k, (img, y, d) in enumerate([(E_NAME, 920, .25), (E_FULL, 1040, .45), (E_URL, 1090, .55)]):
        im, pad, _ = img; p = out_cubic(prog(t, d, .4))
        paste(f, im, (W - im.shape[1]) / 2 + pad * 0, y - pad + (1 - p) * 18, p)
    # the line, once more, under the name
    from nixline_motion import hline
    u = out_expo(prog(t, .35, .6)); half = 300 * u
    hline(f, 1005, W / 2 - half, W / 2 + half, .85, core=3, sig=12)
    return f

# ---------------------------------------------------------------- render
def render_frame(k):
    t = k / FPS
    s = int(t // L)
    if s >= 5:
        return end_card(t - 5 * L).clip(0, 255).astype(np.uint8)
    lt = t - s * L
    P, cam = SHOTS[s](lt)
    img = R.frame_rgb(W, H, cam, P, ss=SS).astype(np.float32)
    overlay(img, s, lt, cam)
    return img.clip(0, 255).astype(np.uint8)

def main(only=None):
    ks = range(N) if only is None else only
    for k in ks:
        out = os.path.join(FRAMES, f"f{k:04d}.jpg")
        if os.path.exists(out): continue                     # resumable after a container restart
        Image.fromarray(render_frame(k)).save(out, quality=95)
        if k % 15 == 0: print(f"  frame {k}/{N}  t={k / FPS:5.2f}s", flush=True)
    if only is not None: return
    aud = os.path.join(HERE, "..", "..", "floor-reels", "audio")
    final = os.path.join(OUTDIR, "NX-MOTION-teak-pendant-install-v1.mp4")
    sfx_at = 4 * L + .33
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(FRAMES, "f%04d.jpg"),
                    "-ss", "0.396", "-t", f"{DUR:.3f}", "-i", os.path.join(aud, "music6-corners.mp3"),
                    "-i", os.path.join(aud, "sfx-turn.mp3"),
                    "-filter_complex",
                    f"[1:a]volume=-1dB,afade=t=in:d=0.2,afade=t=out:st={DUR - 1.0:.2f}:d=1.0[m];"
                    f"[2:a]adelay={int(sfx_at * 1000)}|{int(sfx_at * 1000)},volume=-9dB[s];"
                    "[m][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{DUR:.3f}", final], check=True)
    print("done", final)

if __name__ == "__main__":
    main()
