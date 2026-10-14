"""NixWoods range, "dial a light": a phone keypad whose keys fill with our lamps, the call button, then the range.

The pattern follows @kalenjehgold's reel (instagram.com/reel/DeUjhgAId3t, 10.1 s, 282k views). The owner asked on
14 Oct: "Another idea. Use clean images."
- 0-3.7 s: a white phone keypad. One key at a time fills with a round product photo (keys 1-8 every 0.23 s, then 9 at
  2.6 s and 0 at 3.2 s, on the reference's own sound hits).
- 3.73 s: the green call button is pressed; the keys burst outward in a blur.
- 3.85-9.3 s: one product per beat, full screen, a small figure under each (theirs is the gram weight; ours is the
  live price), a small mark low in the frame.
- Then the logo on white.

Ours uses the clean 5 Aug 2026 shoot only (drive-pull/shoot-20260805, never the watermarked archive), nine products,
each named by its tell (PRODUCT-ID.md) or by the owner on 14 Oct, priced from live Shopify on 14 Oct, cheapest first:
NixLine floor lamp ₹999 · NixLine 30" wall light from ₹1,799 · bedside dimmer lamp ₹2,499 · 30" wall sconce ₹2,500 ·
Globe Edison table lamp ₹2,999 · Compact wall light from ₹4,999 · Minimalist floor lamp from ₹6,999 · Rosewood hollow
pendant ₹7,999 · Sculpted Glow ₹9,999. Key 0 carries the NX mark.

    python3 brand-reels/dial-range/dial_range.py [--ref-audio ref.wav --preview /tmp/p.mp4]

Writes out/<NAME>-in-app-audio.mp4 (silent track, cut on the reference's times: tap "Use audio" on the reference at
0:00) and out/<NAME>-music3.mp4 (our own sound: real keypad tones for each key, the call click, then music3-design
dropping on the first product, the cuts on its beat), plus a cover and a sheet.
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from made_well import encoder                                             # noqa: E402

import imageio_ffmpeg                                                     # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, SR = 1080, 1920, 30, 48000
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261014-nixwoods-range-dial-a-light-v1"
DUR = 10.1
A = lambda p: os.path.join(ROOT, "assets", p)
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
BG = (250, 250, 250)
INK = (58, 38, 24)
CREAM = (246, 239, 228)
GREEN = (52, 199, 89)

# key: (fill time, photo tag, product, price label, circle crop in the photo: centre x, centre y, diameter;
#       full-screen crop: centre x, centre y, width). Photos are 3648 x 5472.
KEYS = {
    1: (0.167, "AC4I9815", "NixLine floor lamp", (None, "₹999"), (2790, 3800, 1700), (2300, 3300, 2400)),
    2: (0.333, "AC4I9658", "NixLine 30\" wall light", ("from", "₹1,799"), (1800, 1950, 2300), (1800, 2700, 2600)),
    3: (0.567, "AC4I9861", "Bedside dimmer lamp", (None, "₹2,499"), (2550, 4350, 1300), (2200, 3500, 2200)),
    4: (0.800, "AC4I9652", "30\" wall sconce", (None, "₹2,500"), (1900, 2050, 2100), (1900, 2900, 2600)),
    5: (1.033, "AC4I9873", "Globe Edison table lamp", (None, "₹2,999"), (2150, 4050, 1600), (2050, 3300, 2400)),
    6: (1.267, "AC4I9629", "Compact wall light", ("from", "₹4,999"), (1800, 1300, 2600), (1824, 2736, 3078)),
    7: (1.500, "AC4I9776", "Minimalist floor lamp", ("from", "₹6,999"), (1550, 3200, 2900), (1700, 3050, 2700)),
    8: (1.733, "AC4I9736", "Rosewood hollow pendant", (None, "₹7,999"), (1700, 1450, 2000), (1824, 2736, 3078)),
    9: (2.600, "AC4I9882", "Sculpted Glow floor lamp", (None, "₹9,999"), (2000, 2900, 3000), (1824, 2736, 3078)),
}
ZERO_FILL = 3.200                                       # key 0: the NX mark
PRESS, BURST = 3.733, 3.85                              # the call button, then the keys burst out
CUTS_REF = [3.85, 4.467, 5.067, 5.7, 6.3, 6.933, 7.533, 8.133, 8.767]       # the reference's cuts
END_REF = 9.3
BEAT = 0.5998                                           # music3-design's kicks: 10.80, 11.40 … 13.80 s
CUTS_M3 = [3.85 + BEAT * k for k in range(9)]
END_M3 = 3.85 + BEAT * 9
M3_IN = 10.80 - 3.85                                    # music3's first full kick is at 10.80 s: it lands on 3.85

XS, YS, R = (256, 540, 824), (535, 800, 1066, 1332), 108
LAYOUT = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (0, 1), 5: (1, 1), 6: (2, 1), 7: (0, 2), 8: (1, 2), 9: (2, 2),
          "*": (0, 3), 0: (1, 3), "#": (2, 3)}
LETTERS = {2: "ABC", 3: "DEF", 4: "GHI", 5: "JKL", 6: "MNO", 7: "PQRS", 8: "TUV", 9: "WXYZ", 0: "+"}
CALL = (540, 1598, 105)


def font(name, size):
    return ImageFont.truetype(A(name), size)


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def photo(tag):
    f = [x for x in os.listdir(SHOOT) if tag in x][0]
    im = Image.open(os.path.join(SHOOT, f))
    im.draft("RGB", (im.width // 2, im.height // 2))               # half size is plenty for 1080 wide
    im = im.convert("RGB")
    return im, im.width / 3648


def tone_up(im):
    """the clean shoot as shot: only a touch of contrast and warmth"""
    x = np.asarray(im, np.float32) / 255
    x = np.clip((x - 0.5) * 1.07 + 0.5, 0, 1) * np.array([1.02, 1.0, 0.96], np.float32)
    return Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8))


def circle_thumb(key):
    _, tag, _, _, (cx, cy, d), _ = KEYS[key]
    im, s = photo(tag)
    box = [(cx - d / 2) * s, (cy - d / 2) * s, (cx + d / 2) * s, (cy + d / 2) * s]
    t = tone_up(im.resize((2 * R, 2 * R), Image.LANCZOS, box=box))
    return t


def zero_thumb():
    t = Image.new("RGB", (2 * R, 2 * R), (49, 33, 26))
    lg = Image.open(A("logo.png")).convert("RGBA")
    lg = lg.resize((130, round(130 * lg.height / lg.width)), Image.LANCZOS)
    tint = Image.new("RGBA", lg.size, CREAM + (255,))
    tint.putalpha(lg.getchannel("A"))
    t.paste(tint, (R - lg.width // 2, R - lg.height // 2), tint)
    return t


def mask(size):
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse((0, 0, size * 4 - 1, size * 4 - 1), fill=255)
    return m.resize((size, size), Image.LANCZOS)


def key_face(k):
    """a plain keypad key: white disc, digit, letters"""
    s = 2 * R
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    disc = Image.new("RGBA", (s, s), (255, 255, 255, 255))
    im.paste(disc, (0, 0), mask(s))
    d = ImageDraw.Draw(im)
    digit = {"*": "*", "#": "#"}.get(k, str(k))
    f = font("Inter-400.ttf", 66 if k not in ("*",) else 84)
    yd = R - 8 if k in LETTERS else R
    d.text((R, yd), digit, font=f, fill=(20, 20, 20, 255), anchor="mm")
    if k in LETTERS:
        fl = font("Inter-600.ttf", 17)
        t = LETTERS[k]
        tw = sum(fl.getlength(c) for c in t) + 4 * (len(t) - 1)
        x = R - tw / 2
        for c in t:
            d.text((x, R + 40), c, font=fl, fill=(20, 20, 20, 255), anchor="ls")
            x += fl.getlength(c) + 4
    return im


def call_face(pressed):
    s = 2 * CALL[2]
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    col = (110, 222, 140) if pressed else GREEN
    im.paste(Image.new("RGBA", (s, s), col + (255,)), (0, 0), mask(s))
    ic = Image.open(A("icon-call.png")).convert("RGBA").resize((96, 96), Image.LANCZOS)
    im.alpha_composite(ic, ((s - 96) // 2, (s - 96) // 2))
    return im


def shadow_layer():
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    for k, (c, r) in LAYOUT.items():
        x, y = XS[c], YS[r]
        d.ellipse((x - R, y - R + 8, x + R, y + R + 8), fill=(0, 0, 0, 22))
    x, y, rr = CALL
    d.ellipse((x - rr, y - rr + 8, x + rr, y + rr + 8), fill=(0, 0, 0, 22))
    return sh.filter(ImageFilter.GaussianBlur(14))


class Dial:
    def __init__(self):
        self.faces = {k: key_face(k) for k in LAYOUT}
        self.thumbs = {k: circle_thumb(k) for k in KEYS}
        self.thumbs[0] = zero_thumb()
        self.fill = {k: v[0] for k, v in KEYS.items()}
        self.fill[0] = ZERO_FILL
        self.m = mask(2 * R)
        self.shadow = shadow_layer()
        self.call = {False: call_face(False), True: call_face(True)}

    def key_image(self, k, t):
        """the key at time t: plain, or its photo popping in with a small overshoot"""
        c = 2 * R + 24
        im = Image.new("RGBA", (c, c), (0, 0, 0, 0))
        im.alpha_composite(self.faces[k], (12, 12))
        if k in self.fill and t >= self.fill[k]:
            u = min(1.0, (t - self.fill[k]) / 0.16)
            sc = 0.8 + 0.2 * (1 + 2.70158 * (u - 1) ** 3 + 1.70158 * (u - 1) ** 2)     # ease-out-back
            s = max(2, round(2 * R * sc))
            th = self.thumbs[k].resize((s, s), Image.LANCZOS).convert("RGBA")
            a = sstep((t - self.fill[k]) / 0.07)
            th.putalpha(mask(s).point(lambda v: int(v * a)))
            im.alpha_composite(th, ((c - s) // 2, (c - s) // 2))
        return im

    def frame(self, t, burst=0.0):
        canvas = Image.new("RGBA", (W, H), BG + (255,))
        if burst <= 0:
            canvas.alpha_composite(self.shadow)
        cx0, cy0 = W / 2, H / 2
        items = [(k, XS[c], YS[r]) for k, (c, r) in LAYOUT.items()] + [("call",) + CALL[:2]]
        for k, x, y in items:
            im = self.call[t >= PRESS] if k == "call" else self.key_image(k, t)
            if burst > 0:                                                # out from the centre, growing
                g = 1 + 1.6 * burst ** 1.4
                x, y = cx0 + (x - cx0) * g, cy0 + (y - cy0) * g
                im = im.resize((round(im.width * (1 + 0.7 * burst)), round(im.height * (1 + 0.7 * burst))))
            canvas.alpha_composite(im, (round(x - im.width / 2), round(y - im.height / 2)))
        return np.asarray(canvas.convert("RGB"), np.float32)


def burst_frame(dial, t):
    """the keys fly out with motion blur (9 sub-frames)"""
    u = (t - PRESS - 0.033) / (BURST - PRESS - 0.033)
    subs = [dial.frame(t, max(0.0, u - 0.2 * j / 8)) for j in range(9)]
    return np.mean(subs, axis=0)


def price_layer(label):
    """the price on a small cream chip (our walls are light, so bare text would not hold), the mark under it"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pre, price = label
    fp, fs = font("Inter-600.ttf", 44), font("Inter-400.ttf", 30)
    wpre = fs.getlength(pre + " ") if pre else 0
    tw = wpre + fp.getlength(price)
    x, y = (W - tw) / 2, 1418
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    chip = (x - 30, y - 52, x + tw + 30, y + 22)
    ImageDraw.Draw(sh).rounded_rectangle((chip[0], chip[1] + 6, chip[2], chip[3] + 6), 37, fill=(0, 0, 0, 70))
    lay = sh.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle(chip, 37, fill=CREAM + (236,))
    if pre:
        d.text((x, y), pre, font=fs, fill=INK + (255,), anchor="ls")
    d.text((x + wpre, y), price, font=fp, fill=INK + (255,), anchor="ls")
    fm = font("Inter-600.ttf", 20)
    m = "N I X W O O D S"
    ms = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ms).text(((W - fm.getlength(m)) / 2, 1490), m, font=fm, fill=(0, 0, 0, 120), anchor="ls")
    lay.alpha_composite(ms.filter(ImageFilter.GaussianBlur(3)))
    ImageDraw.Draw(lay).text(((W - fm.getlength(m)) / 2, 1488), m, font=fm, fill=CREAM + (235,), anchor="ls")
    return np.asarray(lay, np.float32) / 255


class Shot:
    def __init__(self, k):
        _, tag, _, label, _, (cx, cy, w) = KEYS[k]
        self.im, self.s = photo(tag)
        self.cx, self.cy, self.w = cx * self.s, cy * self.s, w * self.s
        self.lay = price_layer(label)

    def at(self, u, push=0.04):
        w = self.w * (1 - push * u)
        h = w * H / W
        box = (self.cx - w / 2, self.cy - h / 2, self.cx + w / 2, self.cy + h / 2)
        return np.asarray(tone_up(self.im.resize((W, H), Image.LANCZOS, box=box)), np.float32)

    def frame(self, u):
        f = self.at(u) / 255
        return (f * (1 - self.lay[..., 3:]) + self.lay[..., :3] * self.lay[..., 3:]) * 255


def end_card():
    im = Image.new("RGBA", (W, H), BG + (255,))
    lg = Image.open(A("logo.png")).convert("RGBA")
    lg = lg.resize((300, round(300 * lg.height / lg.width)), Image.LANCZOS)
    ink = Image.new("RGBA", lg.size, INK + (255,))
    ink.putalpha(lg.getchannel("A"))
    im.alpha_composite(ink, ((W - lg.width) // 2, 960 - lg.height // 2 - 60))
    f = font("Inter-600.ttf", 40)
    ImageDraw.Draw(im).text((W / 2, 960 + lg.height // 2 + 30), "nixwoods.com", font=f, fill=INK + (255,),
                            anchor="mt")
    return np.asarray(im.convert("RGB"), np.float32)


def frames(cuts, end, dial, shots, card):
    """every frame of one cut, as uint8"""
    for i in range(round(DUR * FPS)):
        t = i / FPS
        if t < PRESS + 0.033:
            f = dial.frame(t)
        elif t < cuts[0]:
            f = burst_frame(dial, t)
        elif t < end:
            j = max(n for n, c in enumerate(cuts) if c <= t + 1e-6)
            t1 = cuts[j + 1] if j + 1 < len(cuts) else end
            f = shots[j].frame((t - cuts[j]) / (t1 - cuts[j]))
        else:
            f = card
        yield (np.clip(f, 0, 255) + 0.5).astype(np.uint8)


DTMF = {1: (697, 1209), 2: (697, 1336), 3: (697, 1477), 4: (770, 1209), 5: (770, 1336), 6: (770, 1477),
        7: (852, 1209), 8: (852, 1336), 9: (852, 1477), 0: (941, 1336)}


def music3_track():
    """real keypad tones (DTMF) on each key, music3's quiet intro under them, a click on the call button, a beat of
    silence, then music3's kick dropping on the first product"""
    n = int(DUR * SR)
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{M3_IN:.3f}", "-i", os.path.join(ROOT, "aurora-reels", "audio",
                          "music3-design.mp3"), "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    mus = np.zeros((n, 2), np.float32)
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    mus[:len(a)] = a
    t = np.arange(n) / SR
    env = np.where(t < 3.85, 0.45, 1.0)                                  # the intro sits under the tones
    env *= np.clip((3.5 - t) / 0.08, 0, 1) + (t >= 3.85)                 # silence 3.5-3.85 s
    env *= np.clip((DUR - t) / 0.7, 0, 1)
    mix = mus * env[:, None]
    for k, f0 in list({k: v[0] for k, v in KEYS.items()}.items()) + [(0, ZERO_FILL)]:
        lo, hi = DTMF[k]
        m = int(0.11 * SR)
        tt = np.arange(m) / SR
        tone = 0.16 * (np.sin(2 * np.pi * lo * tt) + np.sin(2 * np.pi * hi * tt))
        tone *= np.clip(np.minimum(tt, 0.11 - tt) / 0.005, 0, 1)
        i = int(f0 * SR)
        mix[i:i + m] += tone[:, None]
    rng = np.random.default_rng(7)
    m = int(0.025 * SR)
    click = rng.normal(0, 0.25, m) * np.exp(-np.arange(m) / (0.004 * SR))
    i = int(PRESS * SR)
    mix[i:i + m] += click[:, None]
    return mix * 0.89 / (np.abs(mix).max() + 1e-9)


def write_wav(path, m):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def ref_track(path):
    n = int(DUR * SR)
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le",
                          "-"], capture_output=True, check=True).stdout
    m = np.zeros((n, 2), np.float32)
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    m[:len(a)] = a
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio")
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    dial = Dial()
    shots = [Shot(k) for k in range(1, 10)]
    card = end_card()
    n = round(DUR * FPS)
    jobs = [(CUTS_REF, END_REF, np.zeros((int(DUR * SR), 2), np.float32), f"{NAME}-in-app-audio.mp4"),
            (CUTS_M3, END_M3, music3_track(), f"{NAME}-music3.mp4")]
    picks = [round(3.5 * FPS)] + [round((c + 0.3) * FPS) for c in CUTS_REF] + [round(9.7 * FPS)]
    keep = {}
    for cuts, end, track, fname in jobs:
        wp = os.path.join(OUT, "_a.wav")
        write_wav(wp, track)
        outs = [encoder(wp, os.path.join(OUT, fname))]
        if cuts is CUTS_REF and a.ref_audio and a.preview:
            wr = os.path.join(OUT, "_r.wav")
            write_wav(wr, ref_track(a.ref_audio))
            outs.append(encoder(wr, a.preview))
        done = 0
        for i, f in enumerate(frames(cuts, end, dial, shots, card)):
            for e in outs:
                e.stdin.write(f.tobytes())
            done += 1
            if cuts is CUTS_REF and i in picks:
                keep[i] = f
        assert done == n, done
        for e in outs:
            e.stdin.close()
            assert e.wait() == 0, fname
        for p in (wp, os.path.join(OUT, "_r.wav")):
            if os.path.exists(p):
                os.remove(p)
        print("wrote", fname, flush=True)
    Image.fromarray(keep[round(3.5 * FPS)]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 6, 480 * 2))
    for j, i in enumerate(picks):
        sh.paste(Image.fromarray(keep[i]).resize((270, 480)), (270 * (j % 6), 480 * (j // 6)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)


if __name__ == "__main__":
    main()
