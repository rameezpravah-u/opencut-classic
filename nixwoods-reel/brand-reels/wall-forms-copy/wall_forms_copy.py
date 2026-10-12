#!/usr/bin/env python3
"""NixWoods wall lights in the exact shape of @horon_design's "RIFT" reel (instagram.com/reel/DeLU26cRM8M, 23.68 s).
The owner asked for the reference's script, style, font, text placement and look. Like the lamps-under-3000 v2
copy, this one deliberately sets MOTION.md aside where the reference differs. All footage is real (no AI).

Measured on the reference (1080x1920 equivalents):
  type     thin grotesk caps (Helvetica-Neue-Light-like); here Inter 300, +0.03 em; the end title Inter 300 and
           its line under it Inter 400
  colour   white on dark ground, near-black on light ground (the cylinder and rectangle shots)
  layout   every word is rotated to run along an edge of the lamp; hook lines step down a ~36 degree diagonal
  timing   hook 0-9.6 s (macro), then four form shots of 3.3, 3.7, 2.0 and 5.08 s; each word fades in and out
           over ~0.3 s; the end title fades up at 21.3 s over the last shot
  script   THIS IS RIFT / FIRST LIGHTING SERIES / STARTED WITH / SIMPLE GEOMETRY / JUST OPENED UP / LINE OF LIGHT,
           CYLINDER SOFTER CALM, RECTANGLE BOLDER ARCHITECTURAL, TRIANGLE SHARP, SPLIT CURVE EDGE,
           "Rift Series / Available at Horon-design .com"
Ours keeps that script, swapping in true words for our lights ("FIRST" becomes "WALL", since "first" would be a claim):
  0     - 9.6    Aurora linear wall light, macro drift   src/drive-aurora-wall-6p.mp4 7.6-13.36 s at 0.6x, graded dark
  9.6   - 12.9   Compact wall light (lit)    drive-pull/shoot-20260805 AC4I9644      RECTANGLE / SOFTER / CALM
  12.9  - 16.6   NixLine 30" wall light (unlit, pine)  AC4I9658                     VERTICAL / BOLDER / ARCHITECTURAL
  16.6  - 18.6   Vertical curved wall light (unlit, rosewood)  AC4I9652             SLIM / SHARP
  18.6  - 23.68  Aurora linear wall light, front              src/drive-aurora-wall-6p.mp4 13.8 s on   LINE / WASH / EDGE
                 then "NixWoods Wall Series / Available at nixwoods.com"
The reference's lamps come on in each shot. Ours do on the two lit shots, by starting with only their lit areas
dimmed and bringing them up over 1.5 s; the unlit NixLine and vertical light stay as photographed.
    python3 brand-reels/wall-forms-copy/wall_forms_copy.py
"""
import os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261012-nixwoods-wall-lights-forms-v1.mp4")
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music1-aesthetic.mp3")
A = os.path.join(ROOT, "assets")
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
CLIP = os.path.join(HERE, "src", "drive-aurora-wall-6p.mp4")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
WHITE, INK = (250, 248, 244), (38, 34, 31)


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


# ---------- footage ----------
def clip_frames(t0, secs, speed, crop_cy=0.5):
    """The 4:5 Aurora clip as 9:16: a centre crop, then frames resampled at `speed` with a blend between.
    A generator: frames are made one at a time (a whole shot in float would not fit in memory)."""
    n = round(secs * FPS)
    need = int(np.ceil(secs * speed * 25)) + 3
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", CLIP, "-frames:v", str(need),
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 1350, 1080, 3)
    cw = 1350 * 9 / 16

    def gen():
        for k in range(n):
            p = k * speed * 25 / FPS; i = min(int(p), len(fr) - 2); u = p - i
            a = (fr[i].astype(np.float32) * (1 - u) + fr[i + 1].astype(np.float32) * u).astype(np.uint8)
            im = Image.fromarray(a).resize((W, H), Image.LANCZOS, box=((1080 - cw) / 2, 0, (1080 + cw) / 2, 1350))
            yield np.asarray(im).astype(np.float32)
    return n, gen


def still_frames(name, secs, cx=0.5, cy=0.5, push=0.03):
    """A DSLR still as a 9:16 shot with the reference's near-static camera: a slow 3% push."""
    im = Image.open(os.path.join(SHOOT, name)).convert("RGB")
    iw, ih = im.size
    bw = min(iw, ih * 9 / 16); bh = bw * 16 / 9
    x0 = np.clip(cx * iw - bw / 2, 0, iw - bw); y0 = np.clip(cy * ih - bh / 2, 0, ih - bh)
    n = round(secs * FPS)

    def gen():
        for k in range(n):
            u = k / max(n - 1, 1); z = 1 + push * u * u * (3 - 2 * u)
            w, h = bw / z, bh / z; xx, yy = x0 + (bw - w) / 2, y0 + (bh - h) / 2
            yield np.asarray(im.resize((W, H), Image.LANCZOS, box=(xx, yy, xx + w, yy + h))).astype(np.float32)
    return n, gen


def light_up(shot, secs=1.5, depth=0.72):
    """The lamp coming on: only the lit areas (the bar and its wash) start dimmed, and rise over `secs`."""
    n, gen = shot
    first = next(gen())
    L = first @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    lo, hi = np.percentile(L, 55), np.percentile(L, 99.7)
    w = np.clip((L - lo) / max(hi - lo, 1), 0, 1) ** 0.8
    w = np.asarray(Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32) / 255

    def g2():
        for k, a in enumerate(gen()):
            u = min(1.0, k / (secs * FPS)); u = u * u * (3 - 2 * u)
            yield a * (1 - depth * (1 - u) * w[..., None])
    return n, g2


def moody(shot, crush=2.4):
    """The reference's hook is near-black around a glowing lamp: crush the wall, keep the light."""
    n, gen = shot

    def g2():
        for a in gen():
            x = a / 255
            L = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
            k = np.clip((L - 0.62) / 0.3, 0, 1)[..., None]               # the bar and its brightest wash
            dark = x ** crush * np.array([1.0, 0.92, 0.82], np.float32)    # a warm, crushed ground
            yield np.clip(dark * (1 - k) + x * k, 0, 1) * 255
    return n, g2


# ---------- text ----------
def word_layer(text, size, cx, cy, angle, colour=None, bg=None, weight="Inter-300.ttf", track=0.03):
    """One line, letter-spaced, rotated `angle` degrees (positive = rising to the right), centred at (cx, cy).
    With no colour given, white or ink is picked from the ground under it, as the reference does."""
    f = font(weight, size)
    probe = ImageDraw.Draw(Image.new("L", (8, 8)))
    widths = [probe.textlength(c, font=f) for c in text]
    tw = int(sum(widths) + track * size * (len(text) - 1)) + 4
    asc, desc = f.getmetrics()
    tile = Image.new("L", (tw, asc + desc + 4), 0); d = ImageDraw.Draw(tile); x = 2
    for c, w in zip(text, widths):
        d.text((x, 2), c, font=f, fill=255); x += w + track * size
    rot = tile.rotate(angle, resample=Image.BICUBIC, expand=True)
    m = Image.new("L", (W, H), 0); m.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)))
    a = np.asarray(m).astype(np.float32) / 255
    if colour is None:
        sel = a > 0.3
        lum = float((bg[sel] @ np.array([0.2126, 0.7152, 0.0722])).mean()) / 255 if sel.any() else 0
        colour = INK if lum > 0.55 else WHITE
    return a, np.array(colour, np.float32)


def over(frame, layer, op):
    a, c = layer
    al = (a * op)[..., None]
    return frame * (1 - al) + c * al


def env(t, t_in, t_out, d=0.3):
    up = np.clip((t - t_in) / d, 0, 1); dn = np.clip((t_out - t) / d, 0, 1)
    u = min(up, dn); return u * u * (3 - 2 * u)


def main():
    hook = moody(clip_frames(7.6, 9.6, 0.6))
    f1 = light_up(still_frames("NW-CREATIVE-IMG-20260805-compact-wooden-wall-light-AC4I9644-v1.JPG", 3.3, cy=0.42))
    f2 = still_frames("NW-CREATIVE-IMG-20260805-solid-wood-led-wall-light-30-inch-AC4I9658-v1.JPG", 3.7, cy=0.42)
    f3 = still_frames("NW-CREATIVE-IMG-20260805-vertical-wooden-wall-light-AC4I9652-v1.JPG", 2.0, cy=0.42)
    f4 = moody(light_up(clip_frames(13.8, 5.08, 1.0)), crush=1.6)     # the reference ends on a dusk-dark room
    # words: (text, size, cx, cy, angle, t_in, t_out) with t relative to the shot; positions as measured,
    # except the hook's first lines and LINE, moved down so they never cross our glowing bar
    hook_words = [("THIS IS", 44, 560, 894, -36, 1.2, 2.3), ("NIXWOODS", 80, 720, 970, -36, 1.2, 3.8),
                  ("WALL LIGHTING SERIES", 44, 767, 1126, -36, 2.5, 4.6),
                  ("STARTED WITH", 44, 713, 1222, -36, 4.6, 6.4), ("SIMPLE GEOMETRY", 44, 752, 1374, -36, 5.6, 7.7),
                  ("JUST", 52, 614, 1507, -36, 7.3, 8.0), ("JUST OPENED UP", 52, 772, 1636, -36, 8.0, 8.8),
                  ("LINE OF LIGHT", 44, 685, 1766, -36, 8.3, 9.5)]
    f1_words = [("RECTANGLE", 66, 449, 1183, 40, 0.4, 1.9), ("SOFTER", 44, 540, 1247, 40, 1.05, 3.3),
                ("CALM", 44, 561, 1361, 40, 1.75, 3.3)]
    f2_words = [("VERTICAL", 66, 858, 697, -60, 0.4, 2.1), ("BOLDER", 44, 297, 518, 35, 1.4, 3.1),
                ("ARCHITECTURAL", 44, 384, 826, -45, 2.75, 3.7)]
    f3_words = [("SLIM", 58, 923, 875, -35, 0.4, 2.0), ("SHARP", 44, 81, 1183, 90, 1.05, 2.0)]
    f4_words = [("LINE", 58, 485, 900, -25, 0.4, 1.4), ("WASH", 44, 455, 1183, 90, 1.4, 2.1),
                ("EDGE", 44, 640, 1590, -25, 2.1, 2.5),
                ("NixWoods Wall Series", 88, 540, 518, 0, 2.7, 9.0), ("Available at nixwoods.com", 36, 540, 606, 0, 2.7, 9.0)]
    plan = [(hook, hook_words), (f1, f1_words), (f2, f2_words), (f3, f3_words), (f4, f4_words)]
    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
                         stdin=subprocess.PIPE)
    count = 0
    for (n, gen), words in plan:
        mid = None
        for j, a in enumerate(gen()):
            if j == n // 2 or mid is None and j == 0:
                pass
            if j == 0:                                                 # the ground under each word, for its colour
                g = gen(); [next(g) for _ in range(n // 2)]; mid = next(g); del g
                lays = []
                for text, size, cx, cy, ang, ti, to in words:
                    wt = "Inter-400.ttf" if text.startswith("Available") else "Inter-300.ttf"
                    tr = 0.0 if text.startswith(("NixWoods", "Available")) else 0.03
                    colour = WHITE if text.startswith(("NixWoods", "Available")) else None
                    lays.append((word_layer(text, size, cx, cy, ang, colour, mid, wt, tr), ti, to))
            t = j / FPS
            for lay, ti, to in lays:
                op = env(t, ti, to)
                if op > 0:
                    a = over(a, lay, op)
            p.stdin.write(np.clip(a, 0, 255).astype(np.uint8).tobytes()); count += 1
    p.stdin.close(); assert p.wait() == 0
    total = count / FPS
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-t", f"{total:.3f}", "-i", MUSIC, "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    k = int(0.04 * sr); x[:k] *= np.linspace(0, 1, k)[:, None]
    k = int(1.2 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x *= 0.65 / max(np.abs(x).max(), 1e-3)
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f} s, {count} frames")


if __name__ == "__main__":
    main()
