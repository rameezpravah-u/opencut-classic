"""E1 — Luma Pillar, "Your corner is missing one thing." (owner brief 13 Oct: "free hand, go crazy, aesthetic,
sellable, FOMO, play with colours, be creative").

Concept: colour off, colour on. While the dresser is being styled and the lamp is off, every step is a bold
duotone in a colour taken from the props on that dresser (the mat's coral and marigold, its green, the books'
plum), with colour-block wipes between them. On the beat the lamp switches on, and true warm colour floods
back: the light is what makes it a room. Lit shots are never recoloured, so the lamp's light is shown as it is.

FOMO from real levers only (13 Oct):
- an impulse price under ₹1,600;
- "no two grains alike" (the product page: each piece one of a kind);
- the prepaid code on the product page (FLY100, ₹100 off).
No stock count, deadline or COD claim.

music1-aesthetic, beat 0.8823 s, 17 beats = 15.0 s. Real footage only: no AI label.

    python3 brand-reels/luma-styled/luma_colour.py
"""
import os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from luma_shots import FF, FPS, H, W, shot                               # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261013-luma-pillar-ambient-lamp-corner-missing-one-thing-v1"
BEAT = 0.8823
DUR = 17 * BEAT
A = lambda p: os.path.join(ROOT, "assets", p)

CREAM, INK, AMBER, AMBER_D, DUSK = (246, 239, 228), (58, 38, 24), (232, 162, 74), (176, 104, 40), (49, 33, 23)
# colours lifted from the props on the dresser
CORAL, MARIGOLD, GREEN, PLUM = (226, 92, 72), (240, 168, 52), (52, 132, 110), (128, 56, 96)

# (start beat, end beat, shot, duotone colour or None, words)
EDIT = [
    (0, 2, "smoke-b", None, "hook"),
    (2, 3, "mat", CORAL, ("mat", True)),
    (3, 4, "books", MARIGOLD, ("books", True)),
    (4, 5, "candle", GREEN, ("candle", True)),
    (5, 6.5, "match", PLUM, ("still… something's off", False)),
    (6.5, 7, "placed", CORAL, None),
    (7, 8, "macro-off", MARIGOLD, None),
    (8, 9.5, "macro-on", None, "switch"),
    (9.5, 12.5, "smoke-a", None, "solid"),
    (12.5, 14, "macro-grain", None, "grain"),
    (14, 17, None, None, "end"),
]


def font(name, size):
    return ImageFont.truetype(A(name), size)


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def true_grade(f):
    """MOTION.md photo grade: a touch warm, a touch of contrast"""
    x = f.astype(np.float32) / 255
    return np.clip(np.clip(x * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** 1.04, 0, 1)


def duotone(f, col):
    """luminance mapped deep shade -> the colour -> cream"""
    x = f.astype(np.float32) / 255
    L = np.clip((x @ np.array([0.2126, 0.7152, 0.0722], np.float32) - 0.04) / 0.8, 0, 1) ** 0.9
    c = np.array(col, np.float32) / 255
    deep = c * 0.22
    cream = np.array(CREAM, np.float32) / 255
    lo = deep + (c - deep) * np.clip(L / 0.55, 0, 1)[..., None]
    hi = c + (cream - c) * np.clip((L - 0.55) / 0.45, 0, 1)[..., None]
    return np.where((L < 0.55)[..., None], lo, hi)


def text_layer(draw_fn):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(sh), shadow=True)
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    draw_fn(ImageDraw.Draw(lay), shadow=False)
    return np.asarray(lay, np.float32) / 255


def centred(d, y, parts, size, shadow, fill=CREAM):
    """one line of (text, accent) parts, centred; Fraunces 600 with Fraunces 500 italic accent"""
    fh, fi = font("Fraunces-600.ttf", size), font("Fraunces-500-i.ttf", size)
    w = sum((fi if a else fh).getlength(t) for t, a in parts)
    x = (W - w) / 2
    for t, a in parts:
        f = fi if a else fh
        col = (0, 0, 0, 170) if shadow else (AMBER if a else fill)
        d.text((x, y), t, font=f, fill=col)
        x += f.getlength(t)


def hook(d, shadow):
    centred(d, 270, [("Your corner is", False)], 86, shadow)
    centred(d, 372, [("missing ", False), ("one", True), (" thing.", False)], 86, shadow)


def solid(d, shadow):
    centred(d, 270, [("Solid wood.", False)], 84, shadow)
    centred(d, 372, [("No two grains ", False), ("alike.", True)], 72, shadow)


def grain(d, shadow):
    f = font("GochiHand-400.ttf", 56)                              # kept left of the lit bar (x < 500)
    for i, line in enumerate(["yours won't", "match anyone", "else's."]):
        d.text((80, 330 + i * 66), line, font=f, fill=(0, 0, 0, 170) if shadow else CREAM)


def chip_layer(text, col, check):
    """a cream label on a colour block, bottom-left of the safe zone"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font("Inter-600.ttf", 50) if check else font("GochiHand-400.ttf", 66)
    tw = f.getlength(text)
    x0, y0 = 90, 1010
    pad = 30
    hgt = 92 if check else 104
    extra = 70 if check else 0
    d.rounded_rectangle((x0, y0, x0 + tw + 2 * pad + extra, y0 + hgt), 22, fill=CREAM + (245,))
    d.text((x0 + pad, y0 + (18 if check else 14)), text, font=f, fill=col)
    if check:                                                      # a drawn tick, in the step's colour
        cx = x0 + pad + tw + 22
        d.line([(cx, y0 + 48), (cx + 14, y0 + 62), (cx + 40, y0 + 30)], fill=col, width=9, joint="curve")
    return np.asarray(lay, np.float32) / 255


def end_card():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    g = np.ones((H, W, 3), np.float32) * np.array(DUSK, np.float32) / 255
    g *= np.clip(1.08 - 0.35 * r, 0, 1.2)[..., None]
    g += np.random.default_rng(5).normal(0, 2.2 / 255, g.shape).astype(np.float32)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for i, c in enumerate([CORAL, MARIGOLD, GREEN, PLUM]):          # the props' colours, as a strip
        d.rounded_rectangle((90 + i * 228, 250, 90 + i * 228 + 210, 268), 9, fill=c + (255,))
    logo = Image.open(A("logo.png")).convert("RGBA")
    lw = 300
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    tint = Image.new("RGBA", logo.size, CREAM + (255,))
    tint.putalpha(logo.split()[3])
    lay.alpha_composite(tint, ((W - lw) // 2, 360))
    y = 360 + logo.height + 90
    fh = font("Fraunces-600.ttf", 96)
    d.text(((W - fh.getlength("Luma Pillar")) / 2, y), "Luma Pillar", font=fh, fill=CREAM)
    y += 150
    fp = font("Inter-600.ttf", 128)
    d.text(((W - fp.getlength("₹1,599")) / 2, y), "₹1,599", font=fp, fill=AMBER)
    y += 190
    fc = font("Inter-600.ttf", 36)
    t = "₹100 off prepaid · code FLY100"
    tw = fc.getlength(t)
    d.rounded_rectangle(((W - tw) / 2 - 30, y, (W + tw) / 2 + 30, y + 74), 37, fill=CORAL + (255,))
    d.text(((W - tw) / 2, y + 15), t, font=fc, fill=CREAM)
    y += 130
    fu = font("Inter-600.ttf", 48)
    d.text(((W - fu.getlength("nixwoods.com")) / 2, y), "nixwoods.com", font=fu, fill=AMBER)
    a = np.asarray(lay, np.float32) / 255
    return np.clip(g * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:], 0, 1), a


def over(fr, lay, alpha=1.0):
    a = lay[..., 3:] * alpha
    return fr * (1 - a) + lay[..., :3] * a


def music(path):
    sr = 48000
    raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(ROOT, "aurora-reels", "audio", "music1-aesthetic.mp3"),
                          "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(DUR * sr)
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    m *= np.clip((DUR - np.arange(n) / sr) / 1.0, 0, 1)[:, None]
    m *= 0.65 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    layers = {"hook": text_layer(hook), "solid": text_layer(solid), "grain": text_layer(grain)}
    card, card_a = end_card()
    wav = os.path.join(OUT, "_a.wav")
    music(wav)
    path = os.path.join(OUT, f"{NAME}.mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                          path], stdin=subprocess.PIPE)
    keep = []
    prev_col = None
    for b0, b1, name, col, words in EDIT:
        f0, f1 = round(b0 * BEAT * FPS), round(b1 * BEAT * FPS)
        n = f1 - f0
        frames = shot(name, n / FPS) if name else [None] * n
        chip = chip_layer(words[0], col, words[1]) if isinstance(words, tuple) else None
        for k, f in enumerate(frames):
            t = k / FPS
            if name is None:                                         # the end card rises over 0.3 s
                u = sstep(t / 0.3)
                fr = card * u + keep_last * (1 - u)
            elif col is not None:
                fr = duotone(f, col)
                if k < 7 and prev_col is not None:                   # a colour block wipes across
                    x0 = int(-W + (2 * W) * (k + 1) / 7)
                    xa, xb = max(0, x0), min(W, x0 + W)
                    if xb > xa:
                        fr[:, xa:xb] = np.array(col, np.float32) / 255
            else:
                fr = true_grade(f)
                if words == "switch":                                # the light comes on: a warm bloom on the beat
                    fl = np.exp(-t / 0.18) * 0.55
                    fr = np.clip(fr + fl * np.array([1.0, 0.86, 0.62], np.float32), 0, 1)
            if words in layers:
                a = sstep(t / 0.25) if words != "hook" else min(1.0, 0.4 + t / 0.2)
                fr = over(fr, layers[words], a)
            if chip is not None:
                fr = over(fr, chip, sstep((t - 0.08) / 0.15))
            keep_last = fr
            p.stdin.write((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
            if k == n // 2:
                keep.append((np.clip(fr, 0, 1) * 255 + 0.5).astype(np.uint8))
        prev_col = col if col is not None else prev_col
    p.stdin.close()
    assert p.wait() == 0, path
    os.remove(wav)
    Image.fromarray(keep[7]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 6, 480 * 2))
    for i, im in enumerate(keep[:11] + [keep[-1]]):
        sh.paste(Image.fromarray(im).resize((270, 480)), (270 * (i % 6), 480 * (i // 6)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", path)


if __name__ == "__main__":
    main()
