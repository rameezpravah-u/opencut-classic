"""NixWoods "CAM 02": the NixLine heist, after the 13.8M-view CCTV "robbery" restaurant ad (breakdown:
instagram.com/reel/DekLWdWN6eH). Plan, prompts, credits and verdicts: README.md (owner approved 19 Oct).

Workshop CCTV at night. A masked thief creeps past the open cash box and every tool, wakes the watchman, shushes him,
takes only the NixLine floor lamp and walks out with it lit. In the grey CCTV grade the lamp's warm light is the only
colour. Then a cut to a moody still of the lamp in a corner: "Nobody steals a tubelight."

Everything is AI-generated (Higgsfield: Nano Banana 2.1 frames referenced on the owner's own NixLine clip nx04 and the
product page photo, Kling 3.0 Turbo clips, in gen2/). There is no on-screen AI label (owner, 19 Oct); disclosure is
Instagram's "Made with AI" toggle, Meta's AI disclosure for ads, and the caption. v1 used the 5 Aug photo AC4I9815,
which the owner says is not the NixLine (19 Oct).

    python3 brand-reels/cctv-heist/cctv_heist.py
"""
import os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import FF, FPS, H, W, font, sstep     # noqa: E402
from made_well import encoder                           # noqa: E402

GEN = os.path.join(HERE, "gen2")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261019-nix-line-solid-wood-floor-lamp-cctv-heist-v3-AI"
HERO = os.path.join(GEN, "hero.jpg")                # the aesthetic NixLine still, generated 19 Oct
SR = 48000

# (clip, in-point s, length s) on the timeline, in order; the lamp lights between B and C
SHOTS = [("A", 0.2, 4.4), ("B", 0.4, 3.2), ("C", 1.1, 3.8), ("D", 0.0, 2.8)]
END = 3.4                                     # the real lamp and the end card
CUTS = np.cumsum([0] + [s[2] for s in SHOTS])  # 0, 4.4, 7.6, 11.4, 14.2
DUR = float(CUTS[-1] + END)
SWITCH = float(CUTS[2])                       # the cut into the lit lamp

CAPS = [(0.25, 2.9, "CAM 02 caught this at 2:47 AM"), (SWITCH + 0.5, CUTS[3] - 0.1, "He skipped the cash."),
        (CUTS[3] + 0.15, CUTS[4] - 0.05, "Took the ₹999 lamp.")]
CREAM, INK, AMBER_D, MUTED_L = (246, 239, 228), (58, 38, 24), (176, 104, 40), (124, 100, 82)


def clip(name, t_in, secs):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", os.path.join(GEN, f"{name}.mp4"), "-t",
                          f"{secs:.3f}", "-vf", "fps=30,scale=1080:1920:flags=lanczos,unsharp=5:5:0.5",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    n = round(secs * FPS)
    return [fr[min(i // 2 * 2, len(fr) - 1)] for i in range(n)]     # held to 15 fps, as a CCTV feed records


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1.1 - 0.75 * (((XX - W / 2) / W) ** 2 + ((YY - H / 2) / H) ** 2) * 2.0, 0.45, 1)[..., None]
SCAN = (1 - 0.05 * ((np.arange(H) % 4) < 2))[:, None, None].astype(np.float32)
RNG = np.random.default_rng(3)


GRAIN = {}


def grain(i):
    """coarse sensor grain, refreshed every second frame like a 15 fps CCTV feed (and so the reel stays small)"""
    k = i // 2
    if k not in GRAIN:
        GRAIN.clear()
        GRAIN[k] = RNG.normal(0, 0.018, (H // 4, W // 4, 1)).repeat(4, 0).repeat(4, 1).astype(np.float32)
    return GRAIN[k]


def cctv(f, i):
    """night CCTV: green-grey, crushed, grainy, scanlines, vignette; only warm light (the lamp) keeps its colour"""
    x = f.astype(np.float32) / 255
    L = x @ np.array([0.299, 0.587, 0.114], np.float32)
    grey = np.clip((L[..., None] - 0.06) * 1.18, 0, 1) * np.array([0.90, 1.0, 0.92], np.float32)
    warm = np.clip((x[..., 0] - x[..., 2] - 0.05) / 0.15, 0, 1) * np.clip((L - 0.35) / 0.2, 0, 1)
    warm = np.asarray(Image.fromarray((warm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)),
                      np.float32)[..., None] / 255
    # the lamp's light is pushed to a warm cream (3000K), so it reads as the one colour in the frame
    lit = np.clip(x * np.array([1.12, 1.0, 0.78], np.float32) + np.array([0.05, 0.02, 0.0], np.float32), 0, 1)
    y = grey * (1 - warm) + lit * warm
    y = y * VIG * SCAN + grain(i)
    return np.clip(y, 0, 1)


def tear(x, k):
    """a CCTV frame glitch at the cuts: a few horizontal bands slip sideways"""
    y = x.copy()
    for _ in range(4):
        a = RNG.integers(0, H - 120)
        h = RNG.integers(20, 110)
        y[a:a + h] = np.roll(y[a:a + h], int(RNG.integers(-60, 60) * k), axis=1)
    return y


def layer(fn):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay), lay)
    return np.asarray(lay, np.float32) / 255


def over(base, lay, a=1.0):
    return base * (1 - lay[..., 3:] * a) + lay[..., :3] * lay[..., 3:] * a


def hud(t, rec_on):
    """REC dot, camera name and a ticking clock, top of the safe zone"""
    def draw(d, _):
        f = font("Space_Grotesk-700.ttf", 34)
        g = font("Space_Grotesk-500.ttf", 30)
        if rec_on:
            d.ellipse((80, 258, 106, 284), fill=(226, 52, 40, 255))
        d.text((118, 253), "REC", font=f, fill=(240, 240, 236, 235))
        cam = "CAM 02 · NIXWOODS CCTV"
        d.text((W - 80 - g.getlength(cam), 256), cam, font=g, fill=(240, 240, 236, 225))
        s = 13 + int(t)
        clock = f"02:47:{s:02d} AM"
        d.text((80, 300), clock, font=g, fill=(240, 240, 236, 215))
    return layer(draw)


def caption(text):
    def draw(d, _):
        f = font("Inter-600.ttf", 52)
        tw = f.getlength(text)
        x0, y0 = (W - tw) / 2 - 30, 1250
        d.rounded_rectangle((x0, y0, x0 + tw + 60, y0 + 92), 14, fill=(12, 12, 12, 215))
        d.text((x0 + 30, y0 + 16), text, font=f, fill=(250, 250, 246, 255))
    return layer(draw)


def end_card():
    """cream type in the dark wall space above the chair, clear of the lamp's glow"""
    def draw(d, _):
        f = font("Fraunces-600.ttf", 84)
        d.text((90, 330), "Nobody steals", font=f, fill=CREAM + (255,))
        d.text((90, 428), "a tubelight.", font=f, fill=CREAM + (255,))
        g = font("Inter-600.ttf", 42)
        d.text((90, 600), "NixLine floor lamp", font=g, fill=CREAM + (255,))
        d.text((90, 656), "solid teak", font=font("Inter-400.ttf", 38), fill=(214, 196, 172, 255))
        p = font("Inter-600.ttf", 64)
        d.text((90, 720), "₹999", font=p, fill=(232, 162, 74, 255))
        w = p.getlength("₹999")
        q = font("Inter-400.ttf", 38)
        x = 90 + w + 24
        d.text((x, 742), "₹1,599", font=q, fill=(190, 170, 148, 255))
        lw = q.getlength("₹1,599")
        d.line((x, 765, x + lw, 765), fill=(190, 170, 148, 255), width=3)
        d.text((90, 820), "nixwoods.com", font=font("Inter-600.ttf", 40), fill=CREAM + (255,))
    return layer(draw)


def real_frames(n):
    """the hero still, cropped to 9:16, a slow push in towards the lamp"""
    base = Image.open(HERO).convert("RGB")
    w, h = base.size
    cw = min(w, round(h * W / H))
    base = base.crop(((w - cw) // 2, 0, (w - cw) // 2 + cw, h))
    out = []
    for i in range(n):
        z = 1 + 0.06 * sstep(i / max(n - 1, 1))
        bw, bh = base.width / z, base.height / z
        cx, cy = base.width * 0.80, base.height * 0.55            # towards the lamp
        x0 = min(max(cx - bw / 2, 0), base.width - bw)
        y0 = min(max(cy - bh / 2, 0), base.height - bh)
        out.append(np.asarray(base.crop((x0, y0, x0 + bw, y0 + bh)).resize((W, H), Image.LANCZOS),
                              np.float32) / 255)
    return out


def audio(path):
    """music7-noir creeping under the CCTV, a switch click and silence at the lamp, then music1 warms the real shot;
    a low room hum throughout the CCTV"""
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)
    t = np.arange(n) / SR

    def load(p, ss=0.0):
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{ss:.3f}", "-i", p, "-t", f"{DUR:.3f}", "-ac", "2", "-ar",
                              str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        out = np.zeros((n, 2), np.float32)
        out[:len(a)] = a
        return out / (np.sqrt(np.mean(a ** 2)) + 1e-9)

    noir = load(os.path.join(ROOT, "brand-reels", "audio", "music7-noir.mp3")) * 10 ** (-19 / 20)
    m += noir * np.clip((SWITCH - t) / 0.08, 0, 1)[:, None]
    warm = load(os.path.join(ROOT, "brand-reels", "audio", "music1-aesthetic.mp3")) * 10 ** (-21 / 20)
    m += warm * (np.clip((t - SWITCH - 0.4) / 2.5, 0, 1) * 0.55 + np.clip((t - CUTS[4]) / 0.6, 0, 1) * 0.45)[:, None]
    hum = (0.6 * np.sin(2 * np.pi * 100 * t) + 0.4 * np.sin(2 * np.pi * 50 * t)) * 10 ** (-38 / 20)
    m += (hum * np.clip((CUTS[4] - t) / 0.2, 0, 1))[:, None]
    k = int(0.02 * SR)                                              # the switch click
    rng = np.random.default_rng(5)
    click = rng.standard_normal(k) * np.exp(-np.arange(k) / (k / 6)) * 0.5
    i0 = int((SWITCH - 0.05) * SR)
    m[i0:i0 + k] += click[:, None]
    m *= (np.clip(t / 0.15, 0, 1) * np.clip((DUR - t) / 0.6, 0, 1))[:, None]
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    wavp = os.path.join(OUT, ".a.wav")
    audio(wavp)
    enc = encoder(wavp, os.path.join(OUT, f"{NAME}.mp4"), crf=23)
    caps = [(a, b, caption(s)) for a, b, s in CAPS]
    card = end_card()
    keep, i = {}, 0
    for k, (name, t_in, secs) in enumerate(SHOTS):
        for j, f in enumerate(clip(name, t_in, secs)):
            t = i / FPS
            x = cctv(f, i)
            if j < 3 and k > 0:
                x = tear(x, 1 - j / 3)
            if name == "C" and j < 8:                               # the switch: a warm flash as the lamp comes on
                x = np.clip(x + (1 - j / 8) * 0.35 * np.array([1.0, 0.8, 0.55], np.float32), 0, 1)
            x = over(x, hud(t, (i // 15) % 2 == 0))
            for a, b, c in caps:
                if a <= t < b:
                    x = over(x, c, sstep((t - a) / 0.12))
            px = (x * 255 + 0.5).astype(np.uint8)
            enc.stdin.write(px.tobytes())
            if j == round(secs * FPS) // 2:
                keep[name] = px
            i += 1
    for j, x in enumerate(real_frames(round(END * FPS))):
        t = i / FPS
        if j < 2:
            x = np.clip(x + 0.5 * (1 - j / 2), 0, 1)                # the CCTV feed cuts to the real room
        x = over(x, card, sstep((j / FPS - 0.25) / 0.4))
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(px.tobytes())
        if j == round(END * FPS) - 10:
            keep["end"] = px
        i += 1
    enc.stdin.close()
    enc.wait()
    os.remove(wavp)
    ims = [Image.fromarray(keep[k]).resize((270, 480)) for k in ("A", "B", "C", "D", "end")]
    sheet = Image.new("RGB", (270 * 5, 480))
    for k, im in enumerate(ims):
        sheet.paste(im, (270 * k, 0))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep["C"]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", i, "frames", f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
