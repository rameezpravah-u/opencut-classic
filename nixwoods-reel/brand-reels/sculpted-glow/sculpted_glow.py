#!/usr/bin/env python3
"""NixWoods Sculpted Glow (handle luminous-spiral-sculptural-sheesham-wood, ₹9,999): "Off, it's a sculpture.
On, it's light." Built from the owner's own phone clip (src/owner-sculpted-glow-20261011.mov, 464x832,
46 s). Every frame is real; nothing is generated.

music3-design from 8.338 s, so its drop (10.752 s) lands at 2.414 s:
  0     - 2.414  4 beats  the lamp unlit in daylight (the cool "before"); hook up by 0.17 s
  2.414 - 3.621  2 beats  ON: the unlit frame warms into the lit one over 0.30 s on the drop, with a switch click
  3.621 - 7.242  6 beats  one beat each: rosewood base, base, the rope's twist, twist, night reflections, the wide lamp
  7.242 - 9.656  4 beats  end card: Sculpted Glow, ₹9,999, Solid rosewood · LED rope, nixwoods.com
The source's own switch-on is a white flash cut; MOTION.md 5 forbids pops and strobes, so it is not used.
Text is placed per shot where the lit rope is not (the rope's mask over the whole shot, 84 px clear),
on a dark gradient that fades with it.
    python3 brand-reels/sculpted-glow/sculpted_glow.py
"""
import os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import binary_dilation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import grade                                         # noqa: E402  (MOTION.md montage grade)

SRC = os.path.join(HERE, "src", "owner-sculpted-glow-20261011.mov")
OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261011-luminous-spiral-sculptural-sheesham-wood-sculpted-glow-v1.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music3-design.mp3")
CLICK = os.path.join(ROOT, "brand-reels", "edison-stages", "sfx", "sfx-dimmer-click.mp3")
A = os.path.join(ROOT, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B, DROP = 0.6036, 10.752
T_DROP = 4 * B
MUSIC_IN = DROP - T_DROP
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)

# (source in-point, beats, speed, look)
SHOTS = [(1.95, 4, 1.0, "before"),          # unlit, daylight
         (5.10, 2, 0.80, "on"),             # lit wide (after the source's flash has settled)
         (14.0, 1, 1.0, "night"),           # rosewood base, rope across it
         (17.2, 1, 1.0, "night"),
         (21.6, 1, 1.0, "night"),           # the rope's twist past the frame
         (24.6, 1, 1.0, "night"),
         (38.6, 1, 1.0, "night"),           # night, reflections in the glass
         (28.3, 1, 1.0, "night")]           # the whole lamp at night
END_BEATS = 4
TEXT = {0: ("Off, it's a sculpture.", None)}        # the lit shots stay clean: the rope fills them, and the light is the answer


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def read(t0, n_src):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", SRC, "-frames:v", str(n_src), "-vf", f"fps={FPS}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 832, 464, 3)


def up(a):
    """464x832 phone frame to 1080x1920: Lanczos, then a light unsharp mask against the softness."""
    return Image.fromarray(a).resize((W, H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=55, threshold=2))


def before(im):
    """The cool 'before' (MOTION.md 1): daylight, a little desaturated, no warm tint."""
    a = np.asarray(im).astype(np.float32) / 255
    y = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    a = y + (a - y) * 0.75
    a = np.clip(a * np.array([0.97, 1.0, 1.05], np.float32), 0, 1) ** 1.05
    return Image.fromarray((a * 255).astype(np.uint8))


def shot_frames(t0, beats, speed, look, start):
    n = round((start + beats * B) * FPS) - round(start * FPS)
    src = read(t0, int(np.ceil(n * speed)) + 2)
    idx = np.minimum((np.arange(n) * speed).astype(int), len(src) - 1)
    f = before if look == "before" else grade
    return [np.asarray(f(up(src[i]))) for i in idx]


def rope_mask(frames):
    m = np.zeros((H, W), bool)
    for a in frames[:: max(1, len(frames) // 6)]:
        m |= (a.max(2) > 225) & (a.max(2).astype(int) - a.min(2) < 80)
    return binary_dilation(m, iterations=84)


def text_layer(words, accent, frames, lit=True):
    """Headline in the first free spot (top band, centre / left / right) the rope never enters during the shot."""
    f = font("Fraunces-600.ttf", 84); fi = font("Fraunces-500-i.ttf", 84)
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    w = probe.textlength(words, font=f) + (probe.textlength(accent, font=fi) if accent else 0)
    lines = [words] if w <= 880 else words.rsplit(" ", 1)
    mask = rope_mask(frames) if lit else np.zeros((H, W), bool)          # unlit: there is no light to avoid
    for y in (250, 330, 420):
        for align in ("center", "left", "right"):
            boxes, ok = [], True
            for k, ln in enumerate(lines):
                lw = probe.textlength(ln, font=f) + (probe.textlength(accent, font=fi) if accent and k == len(lines) - 1 else 0)
                x = {"center": (W - lw) / 2, "left": 70, "right": 950 - lw}[align]
                box = (int(x), y + k * 92, int(x + lw), y + k * 92 + 90)
                boxes.append(box)
                if mask[box[1]:box[3], max(box[0], 0):box[2]].any():
                    ok = False
            if ok:
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                g = np.zeros((H, W), np.float32)
                ys = np.arange(H)[:, None]
                g[:] = np.clip(1 - np.abs(ys - (y + 45 * len(lines))) / 340, 0, 1) * 0.55
                lay.paste(Image.new("RGBA", (W, H), (24, 14, 8, 255)), (0, 0),
                          Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)))
                txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
                for k, (ln, box) in enumerate(zip(lines, boxes)):
                    d.text((box[0], box[1]), ln, font=f, fill=CREAM + (255,))
                    if accent and k == len(lines) - 1:
                        d.text((box[0] + d.textlength(ln, font=f), box[1]), accent, font=fi, fill=AMBER + (255,))
                sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.5)))
                lay.alpha_composite(sh, (2, 4)); lay.alpha_composite(txt)
                print(f"  '{words}{accent or ''}' at y {y}, {align}")
                return np.asarray(lay).astype(np.float32) / 255
    raise SystemExit(f"no rope-free spot for: {words}")


def end_card():
    """Dusk ground (MOTION.md 6: vignette, grain), logo, name, price, chips, URL (MOTION.md 2-3)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    g = np.array([46, 30, 20], np.float32)[None, None] * (1.08 - 0.35 * r)[..., None]
    g = g + np.random.default_rng(3).normal(0, 2.2, (H, W, 1)) + 1.3
    im = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert("RGBA")
    lg = Image.open(os.path.join(A, "logo.png")).convert("RGBA")
    lw = 440; lg = lg.resize((lw, round(lg.height * lw / lg.width)), Image.LANCZOS)
    cream = Image.new("RGBA", lg.size, CREAM + (255,)); cream.putalpha(lg.getchannel("A"))
    sh = Image.new("RGBA", lg.size, (0, 0, 0, 0)); sh.putalpha(lg.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .45)))
    im.alpha_composite(sh, ((W - lw) // 2 + 4, 330 + 8)); im.alpha_composite(cream, ((W - lw) // 2, 330))
    d = ImageDraw.Draw(im)
    fh, fhi = font("Fraunces-600.ttf", 92), font("Fraunces-500-i.ttf", 92)
    a_, b_ = "On, it's ", "light."
    x0 = (W - d.textlength(a_, font=fh) - d.textlength(b_, font=fhi)) / 2
    d.text((x0, 790), a_, font=fh, fill=CREAM, anchor="lm")
    d.text((x0 + d.textlength(a_, font=fh), 790), b_, font=fhi, fill=AMBER, anchor="lm")
    d.text((W / 2, 880), "Sculpted Glow floor lamp", font=font("Inter-400.ttf", 42), fill=MUTED, anchor="mm")
    d.text((W / 2, 975), "₹9,999", font=font("Inter-600.ttf", 112), fill=AMBER, anchor="mm")
    fc = font("Inter-600.ttf", 34)
    chips = ["Solid rosewood", "LED rope"]
    ws = [d.textlength(c, font=fc) + 48 for c in chips]
    x = (W - sum(ws) - 20) / 2
    for c, w in zip(chips, ws):
        d.rounded_rectangle((x, 1080, x + w, 1140), radius=30, outline=(246, 239, 228, 180), width=2)
        d.text((x + w / 2, 1110), c, font=fc, fill=CREAM, anchor="mm"); x += w + 20
    d.text((W / 2, 1210), "nixwoods.com", font=font("Inter-600.ttf", 44), fill=CREAM, anchor="mm")
    return np.asarray(im.convert("RGB")).astype(np.float32)


def main():
    frames, t, layers = [], 0.0, []
    for k, (t0, beats, speed, look) in enumerate(SHOTS):
        fr = shot_frames(t0, beats, speed, look, t)
        lay = text_layer(*TEXT[k], fr, look != "before") if k in TEXT else None
        if k == 0:
            clean_last = fr[-1].astype(np.float32)                      # the unlit frame without its text
        if k == 1:                                                      # the light warms up over 0.30 s
            last = clean_last
            for i in range(9):
                u = (i + 1) / 10; u = u * u * (3 - 2 * u)
                fr[i] = (last * (1 - u) + fr[i].astype(np.float32) * u).astype(np.uint8)
        for i, a in enumerate(fr):
            a = a.astype(np.float32)
            if lay is not None:
                tt = i / FPS
                op = min(1.0, max(0.0, (tt - 0.05) / 0.12)) if k == 0 else min(1.0, max(0.0, (tt - 0.10) / 0.25))
                al = lay[..., 3:4] * op
                a = a * (1 - al) + lay[..., :3] * 255 * al
            frames.append(np.clip(a, 0, 255).astype(np.uint8))
        t += beats * B
    card = end_card()
    hero = frames[-1].astype(np.float32)
    n_end = round((t + END_BEATS * B) * FPS) - round(t * FPS)
    for i in range(n_end):
        u = min(1.0, i / 9); u = u * u * (3 - 2 * u)                    # end card fades in over 0.30 s
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
    def pcm(path, ss, dur):
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{ss:.3f}", "-t", f"{dur:.3f}", "-i", path, "-ac", "2", "-ar", str(sr),
                              "-f", "f32le", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = pcm(MUSIC, MUSIC_IN, total)
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    x *= 0.6 / max(np.abs(x).max(), 1e-3)
    c = pcm(CLICK, 1.26, 0.16); c *= np.linspace(1, 0, len(c))[:, None] ** 0.5; c /= np.abs(c).max()
    a0 = int((T_DROP - 0.03) * sr); x[a0:a0 + len(c)] += c * 0.35
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
