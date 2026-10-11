#!/usr/bin/env python3
"""NixWoods "LAMPS UNDER Rs. 3000", v2: an exact style copy of @scoopedfriday's "Lamps under Rs. 1500"
(instagram.com/reel/Dc6DAC5zsGH), at the owner's request ("make the exact copy"). This deliberately
leaves MOTION.md for this one piece: the reference's type, colour, grade, layout and timings are copied,
measured off its frames (1080x1920 equivalents). Only the footage, product names and prices are ours.

What was measured on the reference:
  type     an extra-bold grotesk (Helvetica-like) with very tight tracking; here Liberation Sans Bold
           (Helvetica metrics, SIL OFL) at -0.085 em, so the letters touch
  colour   pale lime-yellow RGB (237, 243, 150), a faint dark shadow
  hook     "LAMPS / UNDER / Rs. 1500" centred, cap height ~183 px, lines at y 339, 586, 828; "LAMPS" melts in
           long drips that stretch and fall away by ~1.7 s; "UNDER" fades in from ~35%
  names    ~165 px, the price on its own lowercase "rs." line under the name, 146 px apart; each line fades in
           over ~0.25 s, the name ~0.1-0.25 s after the cut, the price ~1 s after the name
  grade    everything washed amber: blue ~30% of red at mid-tones, highlights going yellow
  timing   shots of 3.25, 2.15, 2.8, 2.8 and 3.67 s; the first lamp's name and price land at 2.25 s
  CTA      one small line near the bottom of the last shot (y ~1290)
Ours has four lamps (the reference has five): real footage exists for these four under ₹3,000 only.
  0     - 3.25   Rubik's Cube, rs. 2999        rubik-reels/src/14-1.mp4 from 0.6 s (green, then red)
  3.25  - 5.40   NixLine Floor Lamp, rs. 999   floor-reels/src/nx04-7930.mp4 from 0.75 s, straightened upright
  5.40  - 8.20   Aurora Wall Light, from rs. 1999   src/drive-aurora-v3-fullshoot-hook.mp4 from 3.6 s
  8.20  - 11.87  Edison Dimmer Lamp, rs. 2499  src/drive-edison-dimmer-demo-wa.mp4 from 10.4 s (the bulb
                 comes up on the dimmer), then "all four on nixwoods.com"
    python3 brand-reels/lamps-under-3000/lamps_under_3000_copy.py
"""
import os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import axis                                          # noqa: E402

OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261011-nixwoods-lamps-under-3000-v2.mp4")
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music1-aesthetic.mp3")
FONT = os.path.join(ROOT, "assets", "LiberationSans-Bold.ttf")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
YEL = (237, 243, 150)
R = lambda p: os.path.join(ROOT, p)
S = lambda n: os.path.join(HERE, "src", n)

# (source, fps, in-point, seconds, keep-own-colour, straighten, text blocks)
# a text block: (lines, x, y, align, appear-at seconds into the shot, size)
SHOTS = [
    (R("rubik-reels/src/14-1.mp4"), 25, 0.60, 3.25, 0.45, False,
     [(["Rubik's Cube", "rs. 2999"], 123, 1597, "left", 2.25, 165)]),
    (R("floor-reels/src/nx04-7930.mp4"), 30, 0.75, 2.15, 0.25, True,
     [(["NixLine", "Floor Lamp"], 1062, 330, "right", 0.25, 165),
      (["rs. 999"], 1062, 622, "right", 1.25, 165)]),
    (S("drive-aurora-v3-fullshoot-hook.mp4"), 30, 3.60, 2.80, 0.25, False,
     [(["Aurora", "Wall Light"], 1040, 640, "right", 0.10, 165),
      (["from rs. 1999"], 1040, 932, "right", 1.10, 120)]),
    (S("drive-edison-dimmer-demo-wa.mp4"), 25, 10.40, 3.67, 0.25, False,
     [(["Edison", "Dimmer Lamp"], 100, 127, "left", 0.25, 150),
      (["rs. 2499"], 100, 393, "left", 1.25, 150),
      (["all four on nixwoods.com"], 540, 1288, "center", 2.55, 52)]),
]
HOOK = [("LAMPS", 339), ("UNDER", 586), ("Rs. 3000", 828)]
HOOK_SIZE = 245


def ffont(size):
    return ImageFont.truetype(FONT, size)


def draw_tight(d, xy, text, f, fill, track=-0.085):
    """Draw text letter by letter with the reference's tight tracking. Returns the drawn width."""
    x, y = xy
    for i, ch in enumerate(text):
        d.text((x, y), ch, font=f, fill=fill)
        x += d.textlength(ch, font=f) + track * f.size
        if i + 1 < len(text):                                          # keep the font's kerning pairs
            x += d.textlength(text[i:i + 2], font=f) - d.textlength(text[i], font=f) - d.textlength(text[i + 1], font=f)
    return x - xy[0] - track * f.size


def tight_width(text, f, track=-0.085):
    d = ImageDraw.Draw(Image.new("L", (8, 8)))
    return draw_tight(d, (0, 0), text, f, 0, track)


def text_rgba(lines, x, y, align, size, gap=None):
    """The reference's look: yellow, tight, a faint shadow. y is the top of the first line's caps."""
    f = ffont(size); gap = gap or round(size * 0.885)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    asc = f.getbbox("H")[1]                                            # so y is the cap top, as measured
    for k, ln in enumerate(lines):
        w = tight_width(ln, f)
        xx = {"left": x, "right": x - w, "center": x - w / 2}[align]
        draw_tight(d, (xx, y + k * gap - asc), ln, f, YEL + (255,))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.28)))
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0)); out.alpha_composite(sh, (2, 4)); out.alpha_composite(lay)
    return np.asarray(out).astype(np.float32) / 255


def hook_layers():
    """LAMPS, UNDER and the price line, and the drip origins under LAMPS's letters."""
    layers = [text_rgba([t], W // 2, y, "center", HOOK_SIZE) for t, y in HOOK]
    a = layers[0][..., 3] > 0.5
    rows = np.where(a.any(1))[0]; bottom = rows.max()
    band = a[bottom - 30:bottom + 1]                                   # where the letters touch their baseline
    cols = np.where(band.any(0))[0]
    runs, s = [], cols[0]
    for c0, c1 in zip(cols[:-1], cols[1:]):
        if c1 > c0 + 1:
            runs.append((s, c0)); s = c1
    runs.append((s, cols[-1]))
    return layers, runs, bottom


def drips(t, runs, bottom):
    """The melting LAMPS: one drip from each stem foot. They stretch long and thin, then fall away."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(7)
    feet = [(x0, x1) for x0, x1 in runs if x1 - x0 >= 20]
    pick = sorted(rng.choice(len(feet), size=min(6, len(feet)), replace=False))   # about six drips, as the reference
    for i in pick:
        x0, x1 = feet[i]
        for j in range(1):
            cx = (x0 + x1) / 2 + rng.uniform(-10, 10)
            w0 = min(x1 - x0, 66) * rng.uniform(0.85, 1.0)
            lmax = rng.uniform(300, 1100); delay = rng.uniform(0, 0.3)
            u = np.clip((t - delay) / 1.25, 0, 1); u = 0.18 + 0.82 * u * u     # already hanging at frame 1
            L = lmax * u
            fall = max(0.0, t - 1.35) * 1900                           # after ~1.35 s the drip lets go and falls
            al = int(255 * np.clip(1 - (t - 1.35) / 0.35, 0, 1))
            if al <= 0:
                continue
            wt = w0 * (1 - 0.35 * u); wb = max(5, w0 * (0.42 - 0.3 * u))   # stem-wide at the top, tapering
            top = bottom - 6 + fall
            d.polygon([(cx - wt / 2, top), (cx + wt / 2, top), (cx + wb / 2, top + L), (cx - wb / 2, top + L)],
                      fill=YEL + (al,))
            d.ellipse((cx - wb / 2, top + L - wb / 2, cx + wb / 2, top + L + wb / 2), fill=YEL + (al,))
            if fall == 0:                                              # the letter's foot melting into the drip
                d.ellipse((cx - wt / 2 - 8, bottom - 22, cx + wt / 2 + 8, bottom + 26), fill=YEL + (al,))
    return np.asarray(lay).astype(np.float32) / 255


def amber(a, keep):
    """The reference's grade: luma mapped to an amber ramp (blue ~30% of red, highlights going yellow)."""
    x = a.astype(np.float32) / 255
    L = x @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    L = L ** 1.12                                                      # a touch darker in the mids
    r = np.minimum(1, 1.12 * L ** 0.85)
    g = (0.52 * L + 0.26 * L * L) * 1.05
    b = 0.27 * L
    t = np.stack([r, g, b], -1)
    return np.clip((keep * x + (1 - keep) * t) * 255, 0, 255)


def shot_frames(src, sfps, t0, secs, straighten, start):
    n = round((start + secs) * FPS) - round(start * FPS)
    need = int(np.ceil(n * sfps / FPS)) + 2
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", src, "-frames:v", str(need),
                          "-vf", f"fps={sfps},scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    idx = [min(int(k * sfps / FPS), len(fr) - 1) for k in range(n)]
    if straighten:                                                     # never show the lamp leaning
        angs = {i: axis(Image.fromarray(fr[i]))[1] for i in sorted(set(idx))}
        ks = sorted(angs); sm = np.convolve(np.pad([angs[i] for i in ks], 7, mode="edge"), np.ones(15) / 15, "valid")
        angs = dict(zip(ks, sm))
    out = []
    for k in range(n):
        im = Image.fromarray(fr[idx[k]])
        if straighten:
            th = np.radians(abs(angs[idx[k]])); zc = np.cos(th) + (H / W) * np.sin(th)
            im = im.rotate(-angs[idx[k]], resample=Image.BICUBIC)
            cw, ch = W / zc, H / zc
            im = im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        out.append(np.asarray(im))
    return out


def fade(t, t0, dur=0.25):
    u = min(1.0, max(0.0, (t - t0) / dur))
    return u * u * (3 - 2 * u)


def over(a, lay, op):
    al = lay[..., 3:4] * op
    return a * (1 - al) + lay[..., :3] * 255 * al


def main():
    hook, runs, bottom = hook_layers()
    frames, t = [], 0.0
    for j, (src, sfps, t0, secs, keep, straighten, blocks) in enumerate(SHOTS):
        fr = shot_frames(src, sfps, t0, secs, straighten, t)
        lays = [(text_rgba(lines, x, y, al, size), at) for lines, x, y, al, at, size in blocks]
        for i, a in enumerate(fr):
            tt = i / FPS
            a = amber(a, keep)
            if j == 0:
                a = over(a, hook[0], 1.0)
                if tt < 1.75:
                    a = over(a, drips(tt, runs, bottom), 1.0)
                a = over(a, hook[1], 0.35 + 0.65 * fade(tt, 1.0, 0.5) if tt >= 0.72 else 0.0)
                a = over(a, hook[2], 1.0)
            for lay, at in lays:
                a = over(a, lay, fade(tt, at))
            frames.append(np.clip(a, 0, 255).astype(np.uint8))
        t += secs
    total = len(frames) / FPS

    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
                         stdin=subprocess.PIPE)
    for a in frames:
        p.stdin.write(a.tobytes())
    p.stdin.close(); assert p.wait() == 0
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-t", f"{total:.3f}", "-i", MUSIC, "-ac", "2", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    k = int(0.04 * sr); x[:k] *= np.linspace(0, 1, k)[:, None]
    k = int(0.8 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x *= 0.65 / max(np.abs(x).max(), 1e-3)
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f} s, {len(frames)} frames")


if __name__ == "__main__":
    main()
