#!/usr/bin/env python3
"""NixWoods Double Arm Teak Pendant (handle double-arm-teak-pendant-light-sculptural-led, ₹9,999):
"Made here. Lives here." From the workshop to the dining table, from the owner's own footage only.

Sources (owner uploads, 11 Oct 2026; iPhone HLG tone-mapped to SDR 1080x1920 with zscale + hable, the same
recipe as curve-reels/src):
  src/IMG_2602-sdr.mp4            the pendant lit in the workshop, 60 fps (slowed to half speed here)
  src/workshop-frame-fitting.mp4  the teak frame and its brass joint, by hand
  src/IMG_7292-sdr.mp4            the pendant over a dining table, 4K60 source. Only the first 2.1 s are used:
                                  people walk in after that, and no on-camera release is signed yet.
Not used from the same upload: two AI clips (one shows a different product, the other is a poster with
burned-in text), the teak plank pendant (a different product), and a 720x544 clip (too low to upscale).

music6-corners from its first beat (0.396 s), cuts on the beat, 12 beats = 10.03 s:
  0     - 1.671  the loop's knot, half speed            "Made here."
  1.671 - 2.507  the teak frame's brass joint
  2.507 - 3.343  the loop to the frame's end, half speed
  3.343 - 4.179  along the loop, half speed
  4.179 - 6.686  the dining room, a slow 12% push        "Lives here."
  6.686 - 10.03  end card: Double Arm Teak Pendant, ₹9,999, Teak · Curved LED, nixwoods.com
Every shot takes MOTION.md's montage grade (the cool white LED reads warm with a cream core, as on every
NixWoods reel). Text sits where the lit loop never goes during that shot, on a dark gradient.
    python3 brand-reels/pendant-made-here/pendant_made_here.py
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

OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261011-double-arm-teak-pendant-light-sculptural-led-made-here-v1.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
A = os.path.join(ROOT, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B, FIRST = 0.8357, 0.396
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)
S = lambda n: os.path.join(HERE, "src", n)
# (source, source fps, in-point, beats, speed, push, text)
SHOTS = [(S("IMG_2602-sdr.mp4"), 60, 3.20, 2, 0.5, 0.00, "Made here."),
         (S("workshop-frame-fitting.mp4"), 30, 4.15, 1, 0.6, 0.00, None),
         (S("IMG_2602-sdr.mp4"), 60, 5.60, 1, 0.5, 0.00, None),
         (S("IMG_2602-sdr.mp4"), 60, 6.55, 1, 0.5, 0.00, None),
         (S("IMG_7292-sdr.mp4"), 60, 0.00, 3, 0.85, 0.12, "Lives here.")]
END_BEATS = 4


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def shot_frames(src, sfps, t0, beats, speed, push, start):
    n = round((start + beats * B) * FPS) - round(start * FPS)
    need = int(np.ceil(n * speed * sfps / FPS)) + 2
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", src, "-frames:v", str(need), "-vf", f"fps={sfps},scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    out = []
    for k in range(n):
        a = fr[min(int(k * speed * sfps / FPS), len(fr) - 1)]
        im = Image.fromarray(a)
        if push:
            u = k / max(n - 1, 1); z = 1 + push * u * u * (3 - 2 * u)
            bw, bh = W / z, H / z
            cx, cy = W / 2, H * 0.36                                     # push towards the pendant
            x0 = min(max(cx - bw / 2, 0), W - bw); y0 = min(max(cy - bh / 2, 0), H - bh)
            im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))
        out.append(np.asarray(grade(im)))
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
    im.alpha_composite(sh, ((W - lw) // 2 + 4, 330 + 8)); im.alpha_composite(cream, ((W - lw) // 2, 330))
    d = ImageDraw.Draw(im)
    d.text((W / 2, 790), "Double Arm", font=font("Fraunces-600.ttf", 92), fill=CREAM, anchor="mm")
    d.text((W / 2, 890), "Teak Pendant.", font=font("Fraunces-600.ttf", 92), fill=CREAM, anchor="mm")
    d.text((W / 2, 1035), "₹9,999", font=font("Inter-600.ttf", 112), fill=AMBER, anchor="mm")
    fc = font("Inter-600.ttf", 34)
    chips = ["Teak", "Curved LED"]
    ws = [d.textlength(c, font=fc) + 48 for c in chips]
    x = (W - sum(ws) - 20) / 2
    for c, w in zip(chips, ws):
        d.rounded_rectangle((x, 1130, x + w, 1190), radius=30, outline=(246, 239, 228, 180), width=2)
        d.text((x + w / 2, 1160), c, font=fc, fill=CREAM, anchor="mm"); x += w + 20
    d.text((W / 2, 1240), "nixwoods.com", font=font("Inter-600.ttf", 44), fill=CREAM, anchor="mm")
    return np.asarray(im.convert("RGB")).astype(np.float32)


def main():
    frames, t = [], 0.0
    for src, sfps, t0, beats, speed, push, words in SHOTS:
        fr = shot_frames(src, sfps, t0, beats, speed, push, t)
        lay = text_layer(words, fr) if words else None
        for i, a in enumerate(fr):
            a = a.astype(np.float32)
            if lay is not None:
                tt = i / FPS
                op = min(1.0, max(0.0, (tt - 0.05) / 0.12)) if t == 0 else min(1.0, max(0.0, (tt - 0.15) / 0.25))
                al = lay[..., 3:4] * op
                a = a * (1 - al) + lay[..., :3] * 255 * al
            frames.append(np.clip(a, 0, 255).astype(np.uint8))
        t += beats * B
    card, hero = end_card(), frames[-1].astype(np.float32)
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
