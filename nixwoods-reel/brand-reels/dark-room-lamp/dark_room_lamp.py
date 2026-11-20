#!/usr/bin/env python3
"""Rosewood Edison Dimmer Lamp: "Switch off the tube light. Turn this up instead." (20 Nov 2026)

The hook comes from the owner's /last30days run (15 Nov): the most-reacted lighting post of the month was a
warm, lamp-lit room (r/CozyPlaces, ~27k upvotes), and people ask whether a dark room "can be fixed with lamps"
(r/InteriorDesign). Indian homes are lit by white tube lights, so the line names that.

Footage: the owner's shoot clip 16, Drive's small copy (`../lamps-under-3000/src/drive-edison-dimmer-demo-wa.mp4`,
1080x1920, 25 fps, 19.1 s, every frame seen): a dark room with the lamp low (0-3.5 s), a baked-in dissolve (4.0-5.0 s,
avoided), a close shot of a hand on the brass dimmer with the filament barely lit (5-10.5 s), the bulb coming up to
full (10.8-11.5 s), full glow (11.5-12.7 s), then down again, and the NX logo from 16.5 s (avoided).

Product: the oblong tube bulb is the PRODUCT-ID tell for the Bedside Dimmer Lamp (Classic Edison), handle
bedside-dimmer-lamp-soft-adjustable, live 20 Nov: ₹2,499 (was ₹3,399). Facts used: solid rosewood base, solid-brass
dimmer, Edison bulb included, free shipping on prepaid orders. Real footage only, so no AI label. A hand, no face.

Beats on music1-aesthetic (0.8823 s, first beat 0):
  0 - B3    the dark room, lamp low          "Switch off / the *tube light.*"
  B3 - B6   hand on the dimmer, filament dim  "Turn *this* up / instead."
  B6 - B9   the dimmer turns, the bulb blooms  (no text: the light is the line)
  B9 - 10 s end card on the lit lamp           name, two facts, nixwoods.com (ad: price + prepaid shipping)

    /usr/bin/python3 brand-reels/dark-room-lamp/dark_room_lamp.py [--frames 0.5,4,6.6,9.5] [--cut social|ad|all]
"""
import argparse, os, subprocess, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "art-light"))
from art_light import FF, W, FPS, SR, CREAM, AMBER, AMBER_D, MUTED_D, GROUND, font, sstep, text, alpha, layer, \
    grain  # noqa: E402

import wave  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(os.path.dirname(HERE), "lamps-under-3000", "src", "drive-edison-dimmer-demo-wa.mp4")
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music1-aesthetic.mp3")
OUT = os.path.join(HERE, "out")
BEAT = 0.8823
B = lambda k: round(k * BEAT, 3)
DUR = 10.0
DATE = "20261120"
HANDLE = "bedside-dimmer-lamp-soft-adjustable"
NAME = "Edison Dimmer Lamp"

# (source in, source out, start, end, push): playback speed = (out - in) / (end - start)
SHOTS = [
    (0.30, 3.40, 0.0, B(3), 0.07),     # dark room, lamp low
    (5.40, 8.05, B(3), B(6), 0.04),    # hand on the dimmer, filament barely lit
    (10.40, 12.60, B(6), B(9), 0.05),  # the turn: bulb blooms at ~6.0 s, full at ~6.6 s
    (12.20, 12.20, B(9), DUR, 0.06),   # end card on the full-glow frame, held
]
BLOOM = 6.0                            # when the bulb visibly comes up (for the sound cue)

_cache = {}


def shot_frames(i):
    if i in _cache:
        return _cache[i]
    _cache.clear()
    a, b, s, e, _ = SHOTS[i]
    n = max(1, round((e - s) * FPS))
    if b <= a:                                            # a held still
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{a:.3f}", "-i", SRC, "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(1, 1920, W, 3)
    else:
        speed = (b - a) / (e - s)
        vf = f"setpts=PTS/{speed:.5f},fps={FPS}"
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a:.3f}", "-i", SRC, "-vf", vf,
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        fr = np.frombuffer(raw, np.uint8).reshape(-1, 1920, W, 3)
    _cache[i] = (fr, n)
    return _cache[i]


def footage(t):
    for i, (a, b, s, e, push) in enumerate(SHOTS):
        if s <= t < e or i == len(SHOTS) - 1:
            break
    fr, n = shot_frames(i)
    k = min(len(fr) - 1, int((t - s) * FPS))
    im = Image.fromarray(fr[k])
    z = 1 + push * sstep((t - s) / (e - s))
    if z > 1.0001:
        im2 = im.resize((round(W * z), round(1920 * z)), Image.LANCZOS)
        x, y = (im2.width - W) // 2, (im2.height - 1920) // 2
        im = im2.crop((x, y, x + W, y + 1920))
    return im, i, t - s, e - s


def env(lt, secs, fin=0.35, fout=0.25):
    return sstep(lt / fin) * (1 - sstep((lt - (secs - fout)) / fout))


def two_line(d, y, l1, l2, a, accent, rise):
    """Fraunces headline, one amber italic accent word inside line 1 or 2 (accent = (line_no, word))."""
    f = font("Fraunces-600.ttf", 92)
    fi = font("Fraunces-500-i.ttf", 92)
    dy = (1 - a) * rise
    for n, line in enumerate((l1, l2), 1):
        yy = y + (n - 1) * 112 + dy
        if accent and accent[0] == n:
            pre, word, post = line.partition(accent[1])
            parts = [(pre, f, CREAM), (word, fi, AMBER), (post, f, CREAM)]
            tw = sum(ff.getlength(s) for s, ff, _ in parts)
            x = W / 2 - tw / 2
            for s, ff, c in parts:
                if s:
                    d.text((x, yy), s, font=ff, fill=alpha(c, a), anchor="lm")
                    x += ff.getlength(s)
        else:
            text(d, (W / 2, yy), line, f, alpha(CREAM, a))


def chip(d, cx, cy, s, a, size=40, fill=CREAM, ink=AMBER_D):
    f = font("Inter-600.ttf", size)
    pw, ph = f.getlength(s) + 56, size + 36
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), ph / 2, fill=alpha(fill, a * 0.92))
    text(d, (cx, cy + 1), s, f, alpha(ink, a))


def darken_top(im, frac=0.55, strength=0.55):
    arr = np.asarray(im, np.float32)
    yy = np.linspace(0, 1, im.height)[:, None, None]
    m = np.clip(1 - yy / frac, 0, 1) * strength
    arr = arr * (1 - m) + np.array(GROUND, np.float32) * m
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def frame(t, cut):
    im, i, lt, secs = footage(t)
    ad = cut == "ad"
    if i == 0:
        a = env(lt, secs)

        def dr(d):
            two_line(d, 470, "Switch off", "the tube light.", a, (2, "tube light."), 24)
            if ad:
                chip(d, W / 2, 330, f"{NAME} · ₹2,499", sstep((lt - 0.5) / 0.35) * env(lt, secs, 0.01))
        im = layer(im, dr)
    elif i == 1:
        a = env(lt, secs)

        def dr(d):
            two_line(d, 470, "Turn this up", "instead.", a, (1, "this"), 24)
            if ad:
                chip(d, W / 2, 330, f"{NAME} · ₹2,499", env(lt, secs, 0.01))
        im = layer(im, dr)
    elif i == 3:
        k = sstep(lt / 0.45)
        im = darken_top(im, 0.45, 0.70 * k)
        a1, a2, a3 = (sstep((lt - d0) / 0.35) for d0 in (0.10, 0.30, 0.50))

        def dr(d):
            text(d, (W / 2, 300), NAME, font("Fraunces-600.ttf", 84), alpha(CREAM, a1))
            text(d, (W / 2, 385), "Solid rosewood · brass dimmer", font("Inter-400.ttf", 40), alpha(MUTED_D, a2))
            if ad:
                chip(d, W / 2, 485, "₹2,499", a2, size=56)
                text(d, (W / 2, 575), "Free shipping on prepaid orders", font("Inter-400.ttf", 34), alpha(CREAM, a3))
                text(d, (W / 2, 650), "Shop at nixwoods.com", font("Inter-600.ttf", 42), alpha(CREAM, a3))
            else:
                text(d, (W / 2, 470), "nixwoods.com", font("Inter-600.ttf", 42), alpha(CREAM, a3))
        im = layer(im, dr)
    return im


def music_wav(path):
    n = int(DUR * SR)
    raw = subprocess.run([FF, "-v", "error", "-i", MUSIC, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f",
                          "f32le", "-"], capture_output=True, check=True).stdout
    m = np.zeros((n, 2), np.float32)
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    m[:len(a)] = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 10 ** (-18 / 20)
    t = np.arange(n) / SR
    m *= (np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1))[:, None]   # MOTION: fade the last 0.8 s
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def render(cut, path):
    rng = np.random.default_rng(20)
    wav = path + ".wav"
    music_wav(wav)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x1920", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-shortest",
                          "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for k in range(round(DUR * FPS)):
        p.stdin.write(grain(frame(k / FPS, cut), rng).tobytes())
    p.stdin.close()
    assert p.wait() == 0, path
    os.remove(wav)
    print("wrote", path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None)
    ap.add_argument("--cut", default="all", choices=["social", "ad", "all"])
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cuts = ["social", "ad"] if a.cut == "all" else [a.cut]
    for cut in cuts:
        if a.frames:
            for s in a.frames.split(","):
                frame(float(s), cut).save(os.path.join(OUT, f"{cut}-{float(s):05.2f}.jpg"), quality=88)
            continue
        slug = "dark-room-v1" if cut == "social" else "dark-room-ad-9x16-v1"
        render(cut, os.path.join(OUT, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-{slug}.mp4"))


if __name__ == "__main__":
    main()
