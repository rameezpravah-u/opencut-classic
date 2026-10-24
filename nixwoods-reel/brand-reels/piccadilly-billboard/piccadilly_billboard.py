"""
"NixWoods at Piccadilly Circus": our take on Westwing x Victoria Beckham's billboard reel (instagram.com/reel/
De1nWfEjkAf, sent by the owner on 24 Oct with "Make this"). 9:16, 21.2 s: a dusk drone over London, street level under
the curved screen, night under it, a wet pavement crowd, a night pull-out.

The city is AI (Higgsfield Nano Banana stills -> Kling clips, gen/), generated with the screen a flat chroma green. Here
the green is keyed per frame and our real lamp film (screen_film.py) is mapped onto it column by column between the
screen's fitted top and bottom edges, so it follows the camera and the curve; whatever stands in front stays in front.
The green light the screen threw on the street is shifted to the colour the screen is showing.

    python3 brand-reels/piccadilly-billboard/piccadilly_billboard.py [--still 3 9 15]
"""
import argparse, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import FF, FPS, sstep        # noqa: E402
from screen_film import SH, SW, ScreenFilm     # noqa: E402

W, H = 1080, 1920
SR = 48000
DUR = 21.2
GEN = os.path.join(HERE, "gen")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261024-nixwoods-range-piccadilly-billboard-v1-AI"
# (start, end, clip, clip in-point, screen brightness): the reference's order, each AI clip used once (5 s each)
SHOTS = [(0.0, 2.6, "A", 0.6, 1.00), (2.6, 7.6, "B", 0.0, 0.95), (7.6, 12.6, "C", 0.0, 1.00),
         (12.6, 17.0, "D", 0.1, 1.00), (17.0, DUR, "E", 0.4, 1.10)]
RNG = np.random.default_rng(24)


def clip_frames(k):
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(GEN, f"{k}.mp4"), "-vf",
                          f"scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3), 24.0


def greenness(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    return g - np.maximum(r, b)


class Screen:
    """per-frame screen region and its top/bottom edge curves, smoothed over time"""

    def __init__(self):
        self.prev = None

    def fit(self, img):
        gr = greenness(img)
        core = (gr > 0.30) & (img[..., 1] > 0.45)
        core = ndimage.binary_opening(core, iterations=2)
        lab, n = ndimage.label(core)
        if n == 0:
            return self.prev
        sizes = ndimage.sum(core, lab, range(1, n + 1))
        reg = lab == (1 + int(np.argmax(sizes)))
        reg = ndimage.binary_fill_holes(ndimage.binary_closing(reg, iterations=6))
        ys, xs = np.nonzero(reg)
        x0, x1 = xs.min(), xs.max()
        cols = np.arange(x0, x1 + 1)
        top = np.full(len(cols), np.nan)
        bot = np.full(len(cols), np.nan)
        any_ = reg[:, x0:x1 + 1].any(0)
        top[any_] = reg[:, x0:x1 + 1].argmax(0)[any_]
        bot[any_] = H - 1 - reg[::-1, x0:x1 + 1].argmax(0)[any_]
        hgt = bot - top
        ok = any_ & (hgt > 0.5 * np.nanmax(hgt))
        ok[:max(2, len(cols) // 40)] = False                    # the side edges are ragged: fit on the middle
        ok[-max(2, len(cols) // 40):] = False
        u = (cols - x0) / max(1, x1 - x0)
        pt = np.polyfit(u[ok], top[ok], 2)
        pb = np.polyfit(u[ok], bot[ok], 2)
        cur = np.concatenate([[x0, x1], pt, pb]).astype(np.float64)
        if self.prev is not None and np.abs(cur[:2] - self.prev[0][:2]).max() < 40:
            cur = self.prev[0] * 0.35 + cur * 0.65                 # light smoothing against key jitter
        self.prev = (cur, reg)
        return self.prev


def map_screen(film, geom):
    """remap the screen frame onto the frame's screen: u along the columns, v between the fitted top and bottom"""
    p, reg = geom
    x0, x1 = p[0], p[1]
    pt, pb = p[2:5], p[5:8]
    xs = np.arange(W, dtype=np.float32)
    u = (xs - x0) / max(1.0, x1 - x0)
    top = np.polyval(pt, u)
    bot = np.polyval(pb, u)
    ys = np.arange(H, dtype=np.float32)[:, None]
    v = (ys - top[None, :]) / np.maximum(1.0, (bot - top)[None, :])
    mx = np.broadcast_to(u[None, :] * (SW - 1), (H, W)).astype(np.float32)
    my = (v * (SH - 1)).astype(np.float32)
    # coordinates are clamped, so key pixels just past the fitted edge still get the screen's edge (no green rim)
    out = cv2.remap(film, np.clip(mx, 0, SW - 1), np.clip(my, 0, SH - 1), cv2.INTER_LINEAR)
    inside = ((u[None, :] >= -0.03) & (u[None, :] <= 1.03) & (v >= -0.06) & (v <= 1.06)).astype(np.float32)
    return out, inside


def composite(img, film, geom, gain):
    gr = greenness(img)
    p, reg = geom
    near = cv2.dilate(reg.astype(np.uint8), np.ones((11, 11), np.uint8)).astype(bool)
    key = np.clip((gr - 0.06) / 0.18, 0, 1) * near                 # soft key: lamp posts and heads stay in front
    key = cv2.GaussianBlur(key.astype(np.float32), (0, 0), 0.8)
    scr, inside = map_screen(film, geom)
    scr = np.clip(scr * gain, 0, 1)
    a = (key * inside)[..., None]
    # despill: wherever green light fell (street, wet ground, faces), give it the colour the screen is showing
    mean = film.reshape(-1, 3).mean(0)
    tint = mean / max(1e-3, mean.max())
    exc = np.clip(gr, 0, None)[..., None]
    base = img.copy()
    base[..., 1] -= exc[..., 0]
    base = np.clip(base + exc * tint[None, None, :] * 0.9, 0, 1)
    out = base * (1 - a) + scr * a
    # the screen glows: a soft bloom of its own light
    glow = cv2.GaussianBlur(scr * a, (0, 0), 22)
    return np.clip(out + glow * 0.18, 0, 1)


def grade(img, t):
    img = np.clip(img * np.array([1.04, 1.0, 0.94], np.float32), 0, 1)
    img = img + RNG.normal(0, 1.6 / 255, img.shape[:2])[..., None].astype(np.float32)
    return np.clip(img, 0, 1) * (1 - sstep((t - (DUR - 0.8)) / 0.8))     # fade to dark at the end, as the reference


def frame(t, ctx):
    for a, b, k, t_in, gain in SHOTS:
        if a <= t < b or (k == "E" and t >= a):
            fr, fps = ctx["clips"][k]
            i = min(int((t - a + t_in) * fps), len(fr) - 1)
            img = fr[i].astype(np.float32) / 255
            geom = ctx["screens"][k].fit(img)
            img = composite(img, ctx["film"].at(t), geom, gain)
            return (grade(img, t) * 255 + 0.5).astype(np.uint8)


def audio(path):
    """ours: a low city bed (rumble, distant traffic hiss) and music1 from 2.6 s, fading out with the picture"""
    n = int(DUR * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(7)
    noise = rng.standard_normal(n).astype(np.float32)
    rumble = np.convolve(noise, np.ones(400) / 400, "same") * 6
    hiss = noise - np.convolve(noise, np.ones(6) / 6, "same")
    bed = rumble * 0.10 + hiss * 0.012
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(ROOT, "brand-reels", "audio", "music1-aesthetic.mp3"),
                          "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    mus = np.zeros((n, 2), np.float32)
    mus[:len(a)] = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 10 ** (-19 / 20)
    m = bed[:, None] * np.clip(t / 0.4, 0, 1)[:, None] + mus * np.clip((t - 0.3) / 2.3, 0, 1)[:, None]
    m *= np.clip((DUR - t) / 0.8, 0, 1)[:, None]
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
    ctx = dict(clips={k: clip_frames(k) for k in "ABCDE"}, screens={k: Screen() for k in "ABCDE"}, film=ScreenFilm())
    if a.still is not None:
        for s in a.still:
            Image.fromarray(frame(s, ctx)).save(os.path.join(OUT, f"_still-{s:05.2f}.jpg"), quality=92)
        return
    wavp = os.path.join(OUT, ".audio.wav")
    audio(wavp)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                            str(FPS), "-i", "-", "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf",
                            "20", "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
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
