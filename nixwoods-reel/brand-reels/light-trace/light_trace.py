"""NixWoods "light-trace build": the Sculpted Glow lamp drawn in light, then made, then lit.

The pattern comes from @enrriquesdesign's reel (instagram.com/reel/DeAfrWxvAdd, 7.07 s, 192k views). That reel uses
three panels on black: a "Video prompt" text column, a small "Project image" and a large "Result". In the Result, golden
lines trace a house's footprint, rise into a glowing wireframe, the surfaces materialise and the lines fade to the
finished render. That reel is AI video.

This version is made from one real photo (5 Aug shoot, AC4I9882) with no generative model, so no AI label is needed:
- Left panel, "Made by hand": the steps, each lighting up as the Result reaches it.
- Top right, "The drawing": the lamp's own edges, drawn in teak ink on Paper. (MOTION.md: never the same photo twice
  on screen, so this panel is a drawing, not the photo.)
- Result: the room without the lamp. Lines sweep the surface, rise along the frame's real edges and trace the rope.
  The wood materialises from the lines, the rope light draws itself along its path, the lines fade, and the last frame
  is the photo itself.

    python3 brand-reels/light-trace/light_trace.py [--stills]

Writes out/<NAME>-in-app-audio.mp4 (silent track: add the reference's audio with Instagram's "Use audio"; the visual
timeline follows the reference second by second) and out/<NAME>-music3.mp4 (music3-design, the light on beat 8), plus
a cover and a sheet. The lamp masks and the clean plate come from ../gravity-build/gravity_build.py (scene_glow).
"""
import argparse, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "gravity-build"))
import gravity_build as gb                                               # noqa: E402

FF = gb.FF
W, H, FPS = 1080, 1920, 30
DUR = 7.0
NAME = "NW-CREATIVE-VID-20261013-luminous-spiral-sculptural-sheesham-wood-light-trace-v1"
OUT = os.path.join(HERE, "out")
K = gb.K

DUSK = (49, 33, 23)                       # teak ground #2E1E14 lifted +0.02 (MOTION.md: no pure black)
PANEL0, PANEL1 = (70, 50, 37), (52, 35, 25)
CREAM, PAPER, INK = (246, 239, 228), (238, 228, 212), (58, 38, 24)
AMBER, AMBER_D, MUTED = (232, 162, 74), (176, 104, 40), (200, 190, 178)
CORE = np.array([255, 238, 210], np.float32) / 255
AMB = np.array(AMBER, np.float32) / 255

# panels (x0, y0, x1, y1), measured off the reference at 1080 x 1920
LEFT = (48, 158, 448, 1760)
DRAW = (478, 158, 804, 740)
RES = (478, 772, 1032, 1760)
RAD = 22

# the Result's timeline, matched to the reference
LIGHT_AT, LIGHT_DUR = 4.80, 1.00          # the rope draws itself (beat 8 of music3-design)
FADE0, FADE1 = 5.40, 6.50                 # the lines fade
STEPS = [("Solid wood.", 0.6), ("Cut.", 1.3), ("Shaped.", 2.2), ("Joined.", 3.3), ("Wired.", 4.3),
         ("Lit.", LIGHT_AT)]
CHIP_AT = 5.9


def font(name, size):
    return ImageFont.truetype(os.path.join(ROOT, "assets", name), size)


def sstep(x):
    return gb.sstep(x)


# ----------------------------------------------------------------------------------------------- the Result's maps
def build_maps():
    s = gb.scene_glow()
    O, P0, U, led = s.O, s.P0, s.U, s.led
    hgt, wid = led.shape
    soft = np.zeros((hgt, wid), np.float32)                         # the wooden frame, from gravity-build's pieces
    for pc in s.pieces:
        a = pc["img"][..., 3]
        h, w = a.shape
        soft[pc["y"]:pc["y"] + h, pc["x"]:pc["x"] + w] = np.maximum(soft[pc["y"]:pc["y"] + h, pc["x"]:pc["x"] + w], a)
    frame = soft > 0.5
    ys, xs = np.where(frame)
    ytop, ybot = ys.min(), ys.max()
    xc = (xs.min() + xs.max()) / 2

    # lines: the frame's outline, its strong inner edges (block joints, the base's step) and the rope's outline
    outline = frame & ~ndimage.binary_erosion(frame, iterations=7)
    g8 = (np.clip(gb.lum(U), 0, 1) * 255).astype(np.uint8)
    can = cv2.Canny(cv2.GaussianBlur(g8, (0, 0), 2.0), 30, 80) > 0
    can &= ndimage.binary_erosion(frame, iterations=8)
    can = ndimage.binary_dilation(can, iterations=2)
    lab, n = ndimage.label(can)
    if n:
        sizes = ndimage.sum(lab > 0, lab, range(1, n + 1))
        can = np.isin(lab, 1 + np.where(sizes > 260)[0])
    rope = led & ~ndimage.binary_erosion(led, iterations=6)
    ground = np.zeros_like(frame)
    ground[ybot - 2:ybot + 4, :] = True
    ground[ybot + 70:ybot + 75, :] = True                            # and a second line along its front                              # the surface the lamp stands on

    T = np.full((hgt, wid), 99.0, np.float32)
    yy = np.arange(hgt, dtype=np.float32)[:, None] * np.ones((1, wid), np.float32)
    xx = np.ones((hgt, 1), np.float32) * np.arange(wid, dtype=np.float32)[None]
    rise = (ybot - yy) / (ybot - ytop)
    T[ground] = (0.55 + np.abs(xx - xc) / (wid / 2) * 0.75)[ground]  # sweeps out from under the base
    T[outline | can] = (1.05 + rise * 1.95)[outline | can]           # rises up the frame, 1.05 to 3.0 s
    tn = s.T / max(s.T.max(), 1e-6)
    T[rope] = np.minimum(T[rope], 2.30 + tn[rope] * 1.10)           # then the rope's path, 2.3 to 3.4 s
    lines = (ground | outline | can | rope).astype(np.float32)

    noise = cv2.GaussianBlur(np.random.default_rng(5).normal(0, 1, (hgt, wid)).astype(np.float32), (0, 0), 40)
    noise /= np.abs(noise).max() + 1e-6
    Tm = 3.15 + np.clip(rise, 0, 1) * 1.35 + 0.12 * noise            # wood materialises bottom to top, 3.15 to 4.5 s
    Tr = tn * LIGHT_DUR                                              # the rope lights along its path
    return dict(O=O, P0=P0, U=U, led=led.astype(np.float32), soft=soft, lines=lines, T=T, Tm=Tm, Tr=Tr,
                ybot=ybot, ytop=ytop, xc=xc)


def crop_work(m, box, f=0.5):
    """crop the K-space maps to the camera's reach and shrink by f; line times min-pooled so no line is lost"""
    x0, y0, x1, y1 = box
    out = {}
    for k in ("O", "P0", "U", "led", "soft", "lines", "Tm", "Tr"):
        a = m[k][y0:y1, x0:x1]
        out[k] = cv2.resize(a, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    t = m["T"][y0:y1, x0:x1]
    hh, ww = (t.shape[0] // 2) * 2, (t.shape[1] // 2) * 2
    out["T"] = t[:hh, :ww].reshape(hh // 2, 2, ww // 2, 2).min((1, 3))
    out["T"] = cv2.resize(out["T"], (out["lines"].shape[1], out["lines"].shape[0]), interpolation=cv2.INTER_NEAREST)
    return out


def result_at(w, t):
    """one Result frame at work resolution, float RGB"""
    a = w["soft"][..., None] * sstep((t - w["Tm"]) / 0.5)[..., None]
    A = w["P0"] * (1 - a) + w["U"] * a
    pre = (0.62 * A + 0.38 * gb.lum(A)[..., None]) * 0.64
    front = w["soft"] * np.exp(-((t - w["Tm"] - 0.15) / 0.28) ** 2)     # the wood arrives on a warm glow front
    pre = pre + AMB * (0.42 * front)[..., None]
    R = sstep((t - LIGHT_AT - w["Tr"]) / 0.08)[..., None]
    g = float(sstep((t - LIGHT_AT - 0.15) / 1.35))
    led = w["led"][..., None]
    img = (pre * (1 - g) + w["O"] * g) * (1 - led) + (pre * (1 - R) + w["O"] * R) * led
    fade = 1 - float(sstep((t - FADE0) / (FADE1 - FADE0)))
    if fade > 0:
        on = (w["T"] <= t).astype(np.float32)
        age = np.clip(t - w["T"], 0, 9)
        head = 1 + 1.6 * np.exp(-age / 0.18) * on
        L = np.clip(w["lines"] * on * fade, 0, 1)
        halo = cv2.GaussianBlur(L * head, (0, 0), 3.0)
        wide = cv2.GaussianBlur(L * head, (0, 0), 11.0)
        img = img + AMB * (1.25 * halo + 0.80 * wide)[..., None]
        core = np.clip(L * (0.75 + 0.25 * np.minimum(head, 2)), 0, 1)[..., None]
        img = img * (1 - core) + CORE * core
    return np.clip(img, 0, 1)


def cam(t, base):
    """window (x0, y0, w) in work px: a 4 % push and a slight drift, no rotation"""
    cx, cy, ww = base
    u = float(sstep(t / DUR))
    return cx + 14 * u - ww * (1 - 0.04 * u) / 2, cy - 6 * u - ww * (1 - 0.04 * u) * PH / PW / 2, ww * (1 - 0.04 * u)


PW, PH = RES[2] - RES[0], RES[3] - RES[1]


def to_panel(img, win):
    x0, y0, ww = win
    sc = PW / ww
    M = np.array([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]], np.float32)
    src = cv2.GaussianBlur(img, (0, 0), 0.42 * (1 / sc - 1) + 0.01) if sc < 0.87 else img
    return cv2.warpAffine(src, M, (PW, PH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


# ----------------------------------------------------------------------------------------------- the frame around it
def rounded(size, r):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), r, fill=255)
    return np.asarray(m, np.float32)[..., None] / 255


def pill(d, x, y, text):
    f = font("Inter-600.ttf", 22)
    tw = f.getlength(text)
    d.rounded_rectangle((x, y, x + tw + 26, y + 38), 12, fill=CREAM)
    d.text((x + 13, y + 7), text, font=f, fill=INK)


def background():
    rng = np.random.default_rng(2)
    bg = np.ones((H, W, 3), np.float32) * np.array(DUSK, np.float32) / 255
    bg += cv2.GaussianBlur(rng.normal(0, 0.012, (H, W, 3)).astype(np.float32), (0, 0), 2.2)
    x0, y0, x1, y1 = LEFT
    grad = np.linspace(0, 1, y1 - y0, dtype=np.float32)[:, None, None]
    pan = (np.array(PANEL0, np.float32) * (1 - grad) + np.array(PANEL1, np.float32) * grad) / 255
    pan = pan * np.ones((1, x1 - x0, 1), np.float32)
    m = rounded((x1 - x0, y1 - y0), RAD)
    bg[y0:y1, x0:x1] = bg[y0:y1, x0:x1] * (1 - m) + pan * m
    return np.clip(bg, 0, 1)


def drawing_panel(m, box):
    """the lamp's lines in teak ink on Paper, fitted to the small panel"""
    x0, y0, x1, y1 = box
    L = m["lines"][y0:y1, x0:x1]
    dw, dh = DRAW[2] - DRAW[0], DRAW[3] - DRAW[1]
    sc = min(dw / L.shape[1], dh / L.shape[0]) * 0.98
    L = cv2.resize(cv2.dilate(L, np.ones((3, 3), np.uint8)), None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    L = np.clip(L * 1.6, 0, 1)
    pan = np.ones((dh, dw, 3), np.float32) * np.array(PAPER, np.float32) / 255
    pan += cv2.GaussianBlur(np.random.default_rng(9).normal(0, 0.01, pan.shape).astype(np.float32), (0, 0), 1.2)
    ox, oy = (dw - L.shape[1]) // 2, (dh - L.shape[0]) // 2 + 20
    ink = np.array(INK, np.float32) / 255
    sub = pan[oy:oy + L.shape[0], ox:ox + L.shape[1]]
    hh, ww = sub.shape[:2]
    sub[:] = sub * (1 - L[:hh, :ww, None]) + ink * L[:hh, :ww, None]
    return np.clip(pan, 0, 1)


def static_layer():
    """labels and the byline (RGBA, drawn once)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fi, fa = font("Inter-600.ttf", 46), font("Fraunces-500-i.ttf", 50)
    x, y = LEFT[0] + 34, LEFT[1] + 36
    d.text((x, y), "Made ", font=fi, fill=CREAM)
    d.text((x + fi.getlength("Made "), y - 4), "by hand", font=fa, fill=AMBER)
    pill(d, DRAW[0] + 12, DRAW[1] + 12, "The drawing")
    pill(d, RES[0] + 14, RES[1] + 14, "Result")
    by = Image.new("RGBA", (DRAW[3] - DRAW[1], 70), (0, 0, 0, 0))     # vertical byline, like the reference's
    bd = ImageDraw.Draw(by)
    bd.text((0, 4), "By NixWoods", font=font("Inter-600.ttf", 24), fill=CREAM)
    bd.text((0, 36), "nixwoods.com", font=font("Inter-400.ttf", 20), fill=MUTED)
    by = by.rotate(90, expand=True)
    lay.alpha_composite(by, (DRAW[2] + 8, DRAW[3] - by.height))
    return lay


def steps_layer(t):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fn, fs = font("Inter-400.ttf", 24), font("Inter-600.ttf", 42)
    x, y = LEFT[0] + 34, LEFT[1] + 170
    for i, (txt, at) in enumerate(STEPS):
        u = float(sstep((t - at) / 0.25))
        col = tuple(round(MUTED[c] * (1 - u) + CREAM[c] * u) for c in range(3))
        al = round(105 + 150 * u)
        d.text((x, y), f"{i + 1:02d}", font=fn, fill=AMBER + (al,) if u > 0.5 else MUTED + (al,))
        d.text((x, y + 30), txt, font=fs, fill=col + (al,))
        y += 132
    u = float(sstep((t - CHIP_AT) / 0.3))
    if u > 0:                                                        # the price card, inside the safe zone
        cx0, cy0 = LEFT[0] + 24, LEFT[1] + 1005
        card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((cx0, cy0, LEFT[2] - 24, cy0 + 150), 18, fill=CREAM + (236,))
        cd.text((cx0 + 22, cy0 + 22), "Sculpted Glow", font=font("Inter-600.ttf", 32), fill=INK)
        cd.text((cx0 + 22, cy0 + 60), "floor lamp", font=font("Inter-400.ttf", 26), fill=INK)
        cd.text((cx0 + 22, cy0 + 96), "₹9,999", font=font("Inter-600.ttf", 34), fill=AMBER_D)
        a = np.asarray(card).copy()
        a[..., 3] = (a[..., 3] * u).astype(np.uint8)
        lay.alpha_composite(Image.fromarray(a))
    return lay


def over(base, lay):
    a = np.asarray(lay, np.float32) / 255
    return base * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:]


# ----------------------------------------------------------------------------------------------- audio, encode
def wav_silent(path):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\0" * int(DUR * 48000) * 4)


def wav_music3(path):
    sr = 48000
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(gb.AUDIO, "music3-design.mp3"), "-t", f"{DUR:.3f}",
                          "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(DUR * sr)
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    m *= np.clip((DUR - np.arange(n) / sr) / 0.6, 0, 1)[:, None]
    m *= 0.65 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    m = build_maps()
    hgt, wid = m["led"].shape
    lamp_h = m["ybot"] - m["ytop"]
    win_h = lamp_h * 1.22                                            # K px; the lamp fills about 82 % of the height
    win_w = win_h * PW / PH
    cx, cy = m["xc"], (m["ytop"] + m["ybot"]) / 2 + lamp_h * 0.02
    box = (int(max(0, cx - win_w / 2 - 80)), int(max(0, cy - win_h / 2 - 80)),
           int(min(wid, cx + win_w / 2 + 80)), int(min(hgt, cy + win_h / 2 + 80)))
    f = 0.5
    w = crop_work(m, box, f)
    base = ((cx - box[0]) * f, (cy - box[1]) * f, win_w * f)
    bg = background()
    bg[DRAW[1]:DRAW[3], DRAW[0]:DRAW[2]] = bg[DRAW[1]:DRAW[3], DRAW[0]:DRAW[2]] * (1 - rounded(
        (DRAW[2] - DRAW[0], DRAW[3] - DRAW[1]), RAD)) + drawing_panel(m, (int(cx - win_w / 2), int(cy - win_h / 2),
                                                                           int(cx + win_w / 2), int(cy + win_h / 2))) * \
        rounded((DRAW[2] - DRAW[0], DRAW[3] - DRAW[1]), RAD)
    bg = over(bg, static_layer())
    rmask = rounded((PW, PH), RAD)

    def frame_at(t):
        r = to_panel(result_at(w, t), cam(t, base))
        fr = bg.copy()
        fr[RES[1]:RES[3], RES[0]:RES[2]] = fr[RES[1]:RES[3], RES[0]:RES[2]] * (1 - rmask) + r * rmask
        fr = over(fr, steps_layer(t))
        return (np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8)

    if a.stills:
        for t in (0.3, 1.0, 2.0, 3.0, 4.0, 5.1, 5.6, 6.95):
            Image.fromarray(frame_at(t)).save(os.path.join(OUT, f"_still-{t:.2f}.jpg"), quality=88)
        return

    n = round(DUR * FPS)
    frames = [frame_at(i / FPS) for i in range(n)]
    tmp = os.path.join(OUT, "_a.wav")
    for tag, mk in (("in-app-audio", wav_silent), ("music3", wav_music3)):
        mk(tmp)
        path = os.path.join(OUT, f"{NAME}-{tag}.mp4")
        p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                              str(FPS), "-i", "-", "-i", tmp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf",
                              "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                              "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k",
                              "-shortest", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
        for fr in frames:
            p.stdin.write(fr.tobytes())
        p.stdin.close()
        assert p.wait() == 0, path
        print("wrote", path)
    os.remove(tmp)
    Image.fromarray(frames[-1]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    pick = [round(t * FPS) for t in (0.3, 0.9, 1.5, 2.1, 2.7, 3.3, 3.9, 4.5, 5.1, 5.7, 6.3, 6.95)]
    sh = Image.new("RGB", (270 * 6, 480 * 2))
    for k, i in enumerate(pick):
        sh.paste(Image.fromarray(frames[min(i, n - 1)]).resize((270, 480)), (270 * (k % 6), 480 * (k // 6)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)


if __name__ == "__main__":
    main()
