"""Luma Pillar, "money can't buy happiness but it can buy cool stuff for your room".

The pattern, music, rhythm and type follow @exen3d.ir's reel (instagram.com/reel/DeXK2zJqm7S, 6.34 s, a lamp shown
in the dark). The owner asked on 13 Oct for "the exact music and style and rhythm and fonts".
- 13 hard cuts at the reference's own cut times, each a different angle of the lit lamp.
- One word per cut, centred, in a wide fat serif in pure yellow (#F1F811). Ultra (Apache 2.0, assets/Ultra-400.ttf)
  is the closest free face to the reference's.
- A small brand mark low in the frame, where the reference keeps its own.
- The reference's track is instrumental, so the words are on screen only, as there.

Real footage only: the owner's styling clip (../luma-styled/src), lit shots only, with a moody low-key grade around
the lamp's true warm light.

    python3 brand-reels/cool-stuff/cool_stuff.py [--ref-audio ref.wav --preview /tmp/p.mp4]

Writes out/<NAME>-in-app-audio.mp4 (silent track). On Instagram, tap "Use audio" on the reference reel at 0:00; the
cuts are on its beats. It also writes out/<NAME>-music3.mp4 on our own music3-design track (cuts kept, for ads and
in case that audio is not offered to a business account), plus a cover and a sheet.
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "luma-styled"))
import luma_shots as L                                                   # noqa: E402

FF, FPS, W, H = L.FF, L.FPS, L.W, L.H
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261013-luma-pillar-ambient-lamp-cool-stuff-for-your-room-v1"
DUR = 6.34
CUTS = [0.0, 0.6, 1.167, 1.867, 2.433, 2.9, 3.4, 3.833, 4.3, 4.733, 5.067, 5.433, 5.8]   # the reference's cuts
WORDS = "money can't buy happiness but it can buy cool stuff for your room".split()
YELLOW = (241, 248, 17)

# extra lit sub-spans of the source clip (start, end, straighten), so no two cuts show the same moment
L.SPANS.update({
    "smoke-a2": (18.30, 19.20, True), "smoke-b2": (21.55, 22.25, True), "grain-2": (26.80, 27.55, True),
    "wide-on3": (20.30, 20.95, True), "lit-hand": (10.05, 10.75, True), "macro-on2": (24.55, 24.98, True),
})
SHOTS = ["wide-on", "macro-on", "smoke-a", "macro-grain", "wide-on-2", "smoke-b", "macro-on2", "lit-hand",
         "smoke-a2", "grain-2", "wide-on3", "smoke-b2", "wide-on"]


def moody(f):
    """low-key: true warm light kept, shadows pushed down, a soft vignette"""
    x = f.astype(np.float32) / 255
    x = np.clip(x * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** 1.35 * 0.98
    return x * VIG


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.35 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2)[..., None]


def word_layer(w):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = ImageFont.truetype(os.path.join(ROOT, "assets", "Ultra-400.ttf"), 69)   # "happiness" ~450 px, as there
    tw = f.getlength(w)
    b = f.getbbox(w)
    y = 952 - (b[1] + b[3]) / 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text(((W - tw) / 2, y + 2), w, font=f, fill=(0, 0, 0, 90))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    # a thin dark edge keeps the yellow legible where a word crosses the lit bar (the reference's lamp is blue)
    ImageDraw.Draw(lay).text(((W - tw) / 2, y), w, font=f, fill=YELLOW + (255,), stroke_width=2,
                             stroke_fill=(40, 26, 16, 150))
    m = ImageFont.truetype(os.path.join(ROOT, "assets", "Inter-600.ttf"), 22)   # the small mark, like theirs
    ImageDraw.Draw(lay).text(((W - m.getlength("nixwoods")) / 2, 1500), "nixwoods", font=m, fill=(246, 239, 228, 200))
    return np.asarray(lay, np.float32) / 255


def wav(path, src=None, start=0.0):
    sr = 48000
    n = int(DUR * sr)
    m = np.zeros((n, 2), np.float32)
    if src:
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", src, "-t", f"{DUR:.3f}", "-ac", "2",
                              "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        m[:len(a)] = a
        m *= np.clip((DUR - np.arange(n) / sr) / 0.4, 0, 1)[:, None]
        m *= 0.89 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def encode(frames, wavp, path):
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                          path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0, path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio")
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    frames, mids = [], []
    ends = CUTS[1:] + [DUR]
    for i, (t0, t1) in enumerate(zip(CUTS, ends)):
        n = round(t1 * FPS) - round(t0 * FPS)
        lay = word_layer(WORDS[i])
        al = lay[..., 3:]
        for k, f in enumerate(L.shot(SHOTS[i], n / FPS)):
            o = moody(f) * (1 - al) + lay[..., :3] * al
            frames.append((np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8))
            if k == n // 2:
                mids.append(frames[-1])
    tmp = os.path.join(OUT, "_a.wav")
    wav(tmp)
    encode(frames, tmp, os.path.join(OUT, f"{NAME}-in-app-audio.mp4"))
    # our own track: music3-design, its downbeat at 0 (beat 0.6003 s); the cuts stay where the reference has them
    wav(tmp, os.path.join(ROOT, "aurora-reels", "audio", "music3-design.mp3"), 0.0)
    encode(frames, tmp, os.path.join(OUT, f"{NAME}-music3.mp4"))
    if a.ref_audio and a.preview:
        wav(tmp, a.ref_audio)
        encode(frames, tmp, a.preview)
    os.remove(tmp)
    Image.fromarray(mids[3]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 7, 480 * 2))
    for i, im in enumerate(mids):
        sh.paste(Image.fromarray(im).resize((270, 480)), (270 * (i % 7), 480 * (i // 7)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", len(frames), "frames")


if __name__ == "__main__":
    main()
