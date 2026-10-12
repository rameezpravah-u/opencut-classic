#!/usr/bin/env python3
"""Ad cut-downs (15 s or less, ₹999 on screen before 10 s) of the NixLine voice-over reels, English and Hindi.

Requested by the social desk on 11 Oct: the full reels show the price at ~22 s, and the ad rule is price before 10 s.
Edge TTS was refused on 12 Oct (Bing returns 403 to the websocket from this sandbox), so nothing is re-voiced: the
lines are cut from the same voice-only tracks the full reels were made from (MoneyPrinterTurbo tasks ...e1 / ...a1,
Edge TTS en-IN-NeerjaNeural / hi-IN-SwaraNeural at 1.1x), in this order, with the pauses inside a line tightened:

  hook            "Still living with one white tubelight?"                      line 1
  material        "One line of warm light / set in thirty inches of solid teak."  lines 3-4
  price           "Only ₹999."                                                    line 10
  made            "Made by hand in Uttar Pradesh."                                line 5
  offer           "Cash on delivery. / Free delivery."                            lines 11-12

Every claim is in the approved full scripts (brand.md facts). Shots are the full reels' own (build_materials.py), one
per caption, real footage only, the lamp vertical. music6-corners under the voice. Captions: burn_captions.py <lang>-ad.
    python3 brand-reels/mpt-voice/ad_cut.py en|hi
"""
import os, subprocess, sys, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LANG = sys.argv[1]
sys.argv = [sys.argv[0], LANG, "/tmp/unused"]
import build_materials as bm                                           # noqa: E402  (its helpers; argv is its LANG)

FF, W, H, FPS = bm.FF, bm.W, bm.H, bm.FPS
TASK = {"en": "0e1f1a00-0000-4000-8000-0000000000e1", "hi": "0e1f1a00-0000-4000-8000-0000000000a1"}[LANG]
VOICE = f"/home/user/MoneyPrinterTurbo/storage/tasks/{TASK}/audio.mp3"
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
# (line in timing-<lang>.srt, pause after it)
PIECES = [(1, 0.30), (3, 0.22), (4, 0.30), (10, 0.30), (5, 0.30), (11, 0.20), (12, 0.45)]
if LANG == "hi":                                                      # Hindi lines run longer: tighter pauses
    PIECES = [(1, 0.22), (3, 0.18), (4, 0.22), (10, 0.22), (5, 0.22), (11, 0.15), (12, 0.40)]
# one shot per new caption (caption = piece index, 1-based); full reels' shots
SHOTS = [("01-bare-teak", 1, "clip", "floor-reels/src/nx06-7921.mp4", 2.70),
         ("02-lit", 2, "clip", "floor-reels/src/nx06-7921.mp4", 6.40),
         ("04-standing", 3, "clip", "floor-reels/src/nx04-7930.mp4", 0.60),
         ("07-price-hand", 4, "clip", "floor-reels/src/nx07-7922.mp4", 0.00),     # a hand holds the lit bar upright
         ("05-by-hand", 5, "clip", "floor-reels/src/nx03-7926.mp4", 0.00),
         ("07-plug-in", 6, "clip", "floor-reels/src/nx05-7920.mp4", 0.00),        # vertical for its first 1.35 s
         ("10-lit-hand", 7, "clip", "floor-reels/src/nx06-7921.mp4", 7.90)]
# Not the 5 Aug photo AC4I9815: whether it shows the NixLine or the corner floor lamp is still an open owner check, and
# a ₹999 price must not sit on a lamp that might be the ₹6,999 one.
CAP = {"07-price-hand": 1.2}       # nx07 swings off vertical at 1.3 s (measured): keep only the upright part
SLOW = {"07-price-hand"}           # ...played slower (0.45x) to fill its line instead of freezing
PAD_IN, PAD_OUT = 0.06, 0.10
MAX_LEN = 15.0
SR = 48000
NAME = f"NW-CREATIVE-VID-20261012-nix-line-solid-wood-floor-lamp-voiceover-{LANG}-ad-cut-v1"


def upright(frames):
    """never leaning: rotate each frame by its lit channel's measured angle (smoothed), zoomed to cover"""
    from PIL import Image
    from line_montage import axis
    angs = []
    for f in frames:
        try:
            _, a, L = axis(Image.fromarray(f))
            angs.append(a if L > 400 else None)
        except Exception:
            angs.append(None)
    if all(a is None for a in angs):
        return frames
    known = [a for a in angs if a is not None]
    angs = [a if a is not None else float(np.median(known)) for a in angs]
    sm = np.convolve(np.pad(angs, 7, mode="edge"), np.ones(15) / 15, "valid")
    out = []
    for f, a in zip(frames, sm):
        th = np.radians(abs(a))
        zc = np.cos(th) + (H / W) * np.sin(th)
        im = Image.fromarray(f).rotate(-a, resample=Image.BICUBIC)
        cw, ch = W / zc, H / zc
        out.append(np.asarray(im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))))
    return out


def srt(path):
    import re
    out = []
    for m in re.finditer(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)\s*\n(.+?)(?:\n\n|\Z)",
                         open(path, encoding="utf-8").read(), re.S):
        g = list(map(int, m.groups()[:8]))
        out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000, g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000,
                    m.group(9).strip()))
    return out


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def pcm(path, extra=()):
    raw = subprocess.run([FF, "-v", "error", "-i", path, *extra, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main():
    caps = srt(os.path.join(HERE, f"timing-{LANG}.srt"))
    voice = pcm(VOICE)
    parts, new_caps, t = [], [], 0.0
    for i, (line, gap) in enumerate(PIECES):
        a, b, text = caps[line - 1]
        a0, b0 = max(0.0, a - PAD_IN), b + PAD_OUT
        seg = voice[int(a0 * SR):int(b0 * SR)]
        new_caps.append((t + (a - a0), t + (a - a0) + (b - a), text))
        parts += [seg, np.zeros((int(gap * SR), 2), np.float32)]
        t += len(seg) / SR + gap
    v = np.concatenate(parts)
    total = len(v) / SR
    tempo = max(1.0, total / MAX_LEN)                                  # never past 4 % (1.1 x 1.04 < 1.15)
    assert tempo <= 1.04, f"{LANG}: {total:.2f} s needs tempo {tempo:.3f}; drop a line instead"
    if tempo > 1.0:
        tmp = os.path.join(HERE, "_v.wav")
        with wave.open(tmp, "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
            w.writeframes((np.clip(v, -1, 1) * 32767).astype(np.int16).tobytes())
        v = pcm(tmp, ["-af", f"atempo={tempo:.4f}"])
        os.remove(tmp)
        new_caps = [(a / tempo, b / tempo, x) for a, b, x in new_caps]
    dur = len(v) / SR
    with open(os.path.join(HERE, f"timing-{LANG}-ad.srt"), "w", encoding="utf-8") as f:
        for k, (a, b, x) in enumerate(new_caps, 1):
            f.write(f"{k}\n{ts(a)} --> {ts(b)}\n{x}\n\n")
    price = next(a for a, b, x in new_caps if "₹" in x)
    print(f"{LANG}: {dur:.2f} s, tempo {tempo:.3f}, price spoken and on screen at {price:.2f} s")
    # pictures: one shot per caption start, cut to the voice
    edges = [0.0] + [new_caps[s[1] - 1][0] for s in SHOTS[1:]] + [dur]
    frames = []
    for (name, _, kind, src, arg), a, b in zip(SHOTS, edges[:-1], edges[1:]):
        n = round(b * FPS) - round(a * FPS)
        if kind == "clip":
            bm.MIN_SPEED = 0.44 if name in SLOW else 0.7
            fr, speed, _ = bm.clip_frames(src, arg, n, CAP.get(name, bm.MAXSRC.get(name)))
            fr = upright(fr)
        else:
            fr = bm.photo_frames(arg, n, 0.06 if arg is None else 0.05)
        frames += fr
        print(f"  {name:13s} {a:5.2f}-{b:5.2f}")
    vid = os.path.join(HERE, "_ad_v.mp4")
    bm.encode(vid, frames)
    # sound: the voice over music6 at the full reels' level (MoneyPrinterTurbo bgm volume 0.18), music fades out
    mus = pcm(MUSIC)[:len(v)]
    mus = np.pad(mus, ((0, len(v) - len(mus)), (0, 0)))
    mus *= np.clip((dur - np.arange(len(v)) / SR) / 0.8, 0, 1)[:, None]
    mix = v + mus * 0.18
    mix *= 0.65 / (np.abs(mix).max() + 1e-9)
    wav = os.path.join(HERE, "_ad_a.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    raw = os.path.join(HERE, "_ad_raw.mp4")
    subprocess.run([FF, "-v", "error", "-y", "-i", vid, "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", raw], check=True)
    os.remove(vid); os.remove(wav)
    out = os.path.join(HERE, NAME + ".mp4")
    subprocess.run([sys.executable, os.path.join(HERE, "burn_captions.py"), f"{LANG}-ad", raw, out], check=True)
    os.remove(raw)
    print("wrote", os.path.basename(out))


if __name__ == "__main__":
    main()
