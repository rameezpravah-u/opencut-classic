#!/usr/bin/env python3
"""NixWoods Minimalist Wooden Floor Lamp (handle wooden-floor-lamp-minimalist-standing-light, solid rosewood,
from ₹6,999): "Watch the corner." One mirror corner of a home, dark at first. The lamp comes on, then stays
through the day: getting ready, work, and tea at dusk.

Identified with PRODUCT-ID.md: a thin lit rod rising from a round, cylindrical wooden base, about as tall as the
mirror. (A first cut called it the NixLine; the NixLine is a 30 in teak bar on a small block.) The clip does not
show which height it is (44 in, ₹6,999, or 60 in, ₹9,999), so the end card says "From ₹6,999".

Source (owner upload, 11 Oct 2026): src/owner-floor-lamp-mirror-corner-20261011.mov, 480x848 30 fps, 31.4 s.
It is already an edit (jump cuts at 4.5, 5.3, 6.9 and 8.1 s), probably forwarded over WhatsApp, so it is
upscaled to 1080x1920 (lanczos plus a light unsharp). The camera's orange exposure flash at 4.5-5.2 s is
skipped (MOTION.md: no flash pops); the cut to the lit corner warms in over 0.30 s instead.
A person's face is visible in the mirror. HOLD: do not post until she has agreed (no release on file).

music6-corners from its first beat (0.396 s), cuts on the beat, 12 beats = 10.03 s:
  0     - 1.671  the corner, lamp off, slow 6% push      "Watch the corner."
  1.671 - 2.507  the same corner lit, warming in 0.30 s
  2.507 - 4.179  getting ready in the mirror               "Ready by it."
  4.179 - 5.850  at the desk, 1.5x                         "Work by it."
  5.850 - 7.521  tea at dusk, 1.4x                         "Unwind by it."
  7.521 - 10.03  end card: Minimalist Floor Lamp. From ₹6,999, Solid rosewood · Dimmable, nixwoods.com
Every shot takes MOTION.md's montage grade at 45% (the source is already warm). Text sits above the mirror,
clear of the lit rod.
    python3 brand-reels/minimalist-floor-lamp-corner/watch_the_corner.py
"""
import os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import binary_dilation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import grade                                         # noqa: E402

OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261011-wooden-floor-lamp-minimalist-standing-light-watch-the-corner-v1.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
A = os.path.join(ROOT, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B, FIRST = 0.8357, 0.396
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)
S = lambda n: os.path.join(HERE, "src", n)
SRC = S("owner-floor-lamp-mirror-corner-20261011.mov")
# (source, source fps, in-point, beats, speed, push, text)
SHOTS = [(SRC, 30, 0.00, 2, 1.0, 0.06, "Watch the corner."),
         (SRC, 30, 5.60, 1, 1.0, 0.00, None),
         (SRC, 30, 9.20, 2, 1.0, 0.00, "Ready by it."),
         (SRC, 30, 19.00, 2, 1.5, 0.00, "Work by it."),
         (SRC, 30, 25.60, 2, 1.4, 0.00, "Unwind by it.")]
WARM_IN = 1                                                            # shot index where the lamp comes on
END_BEATS = 3


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def shot_frames(src, sfps, t0, beats, speed, push, start):
    n = round((start + beats * B) * FPS) - round(start * FPS)
    need = int(np.ceil(n * speed * sfps / FPS)) + 2
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", src, "-frames:v", str(need), "-vf", f"fps={sfps},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    out = []
    for k in range(n):
        a = fr[min(int(k * speed * sfps / FPS), len(fr) - 1)]
        im = Image.fromarray(a)
        if push:
            u = k / max(n - 1, 1); z = 1 + push * u * u * (3 - 2 * u)
            bw, bh = W / z, H / z
            cx, cy = W * 0.55, H * 0.5                                    # push towards the corner
            x0 = min(max(cx - bw / 2, 0), W - bw); y0 = min(max(cy - bh / 2, 0), H - bh)
            im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
        g = np.asarray(grade(im)).astype(np.float32)                    # the montage grade at 45%: the source
        out.append((0.45 * g + 0.55 * np.asarray(im)).astype(np.uint8))   # is already warm and goes muddy at full
    return out


def light_mask(frames):
    m = np.zeros((H, W), bool)
    for a in frames[:: max(1, len(frames) // 6)]:
        m |= (a.max(2) > 225) & (a.max(2).astype(int) - a.min(2) < 80)
    return binary_dilation(m, iterations=84)


def text_layer(words, frames):
    f = font("Fraunces-600.ttf", 96)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    lw = probe.textlength(words, font=f)
    mask = light_mask(frames)
    for y in (250, 330, 420, 1120, 1180):
        for align in ("center", "left", "right"):
            x = {"center": (W - lw) / 2, "left": 70, "right": 950 - lw}[align]
            box = (int(x), y, int(x + lw), y + 104)
            if mask[box[1]:box[3], box[0]:box[2]].any():
                continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ys = np.arange(H)[:, None]
            g = np.broadcast_to(np.clip(1 - np.abs(ys - (y + 52)) / 320, 0, 1) * 0.55, (H, W))
            lay.paste(Image.new("RGBA", (W, H), (24, 14, 8, 255)), (0, 0),
                      Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)))
            txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(txt).text((box[0], box[1]), words, font=f, fill=CREAM + (255,))
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.5)))
            lay.alpha_composite(sh, (2, 4)); lay.alpha_composite(txt)
            print(f"  '{words}' at y {y}, {align}")
            return np.asarray(lay).astype(np.float32) / 255
    raise SystemExit(f"no light-free spot for: {words}")


def end_card():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    g = np.array([46, 30, 20], np.float32)[None, None] * (1.08 - 0.35 * r)[..., None]
    g = g + np.random.default_rng(5).normal(0, 2.2, (H, W, 1)) + 1.3
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    lg = Image.open(os.path.join(A, "logo.png")).convert("RGBA")
    lw = 440; lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
    cream = Image.new("RGBA", lg.size, CREAM + (255,)); cream.putalpha(lg.getchannel("A"))
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 0)); sh.putalpha(lg.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .45)))
    im.alpha_composite(sh, ((W - lw) // 2 + 4, 300 + 8)); im.alpha_composite(cream, ((W - lw) // 2, 300))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 760), "Minimalist", font=font("Fraunces-600.ttf", 100), fill=CREAM, anchor="mm")
    d.text((W / 2, 865), "Floor Lamp.", font=font("Fraunces-600.ttf", 100), fill=CREAM, anchor="mm")
    d.text((W / 2, 975), "From", font=font("Inter-400.ttf", 40), fill=MUTED, anchor="mm")
    d.text((W / 2, 1050), "₹6,999", font=font("Inter-600.ttf", 112), fill=AMBER, anchor="mm")
    fc = font("Inter-600.ttf", 34)
    chips = ["Solid rosewood", "Dimmable"]
    ws = [d.textlength(c, font=fc) + 48 for c in chips]
    x = (W - sum(ws) - 20) / 2
    for c, w in zip(chips, ws):
        d.rounded_rectangle((x, 1120, x + w, 1180), radius=30, outline=(246, 239, 228, 180), width=2)
        d.text((x + w / 2, 1150), c, font=fc, fill=CREAM, anchor="mm"); x += w + 20
    d.text((W / 2, 1225), "nixwoods.com", font=font("Inter-600.ttf", 44), fill=CREAM, anchor="mm")
    return np.asarray(im.convert("RGB")).astype(np.float32)


def main():
    frames, t = [], 0.0
    for j, (src, sfps, t0, beats, speed, push, words) in enumerate(SHOTS):
        fr = shot_frames(src, sfps, t0, beats, speed, push, t)
        lay = text_layer(words, fr) if words else None
        clean_last = fr[-1].astype(np.float32)                         # the last frame without its text
        for i, a in enumerate(fr):
            a = a.astype(np.float32)
            if j == WARM_IN and i < 9:                                 # the light warms in over 0.30 s
                u = i / 9; u = u * u * (3 - 2 * u)
                a = a * np.array([0.70 + 0.30 * u, 0.68 + 0.32 * u, 0.66 + 0.34 * u], np.float32)
            if lay is not None:
                tt = i / FPS
                op = min(1.0, max(0.0, (tt - 0.05) / 0.12)) if t == 0 else min(1.0, max(0.0, (tt - 0.15) / 0.25))
                al = lay[..., 3:4] * op
                a = a * (1 - al) + lay[..., :3] * 255 * al
            frames.append(np.clip(a, 0, 255).astype(np.uint8))
        t += beats * B
    card, hero = end_card(), clean_last
    n_end = round((t + END_BEATS * B) * FPS) - round(t * FPS)
    for i in range(n_end):
        u = min(1.0, i / 9); u = u * u * (3 - 2 * u)
        frames.append((hero * (1 - u) + card * u).astype(np.uint8))
    total = len(frames) / FPS

    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
                         stdin=subprocess.PIPE)
    for a in frames:
        p.stdin.write(a.tobytes())
    p.stdin.close(); assert p.wait() == 0
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{FIRST:.3f}", "-t", f"{total:.3f}", "-i", MUSIC, "-ac", "2", "-ar", str(sr),
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
