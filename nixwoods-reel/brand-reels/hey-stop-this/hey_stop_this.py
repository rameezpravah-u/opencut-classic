"""NixWoods "Hey… Stop! Look at… This": the range on @wisherypottery's lyric pattern (instagram.com/reel/DeMwSfCoP2a).

The reference (8.4 s, handmade mugs) sets the words of its song on screen as they are sung:
- "Heeeey": an iris opens from black onto a stack of mugs.
- "Stop!": stop-motion frames, with the word jumping corner to corner as mugs leave the stack.
- "Look at", then seven cuts of "This", each a different mug held up.
- "Aaaaaaaand" on the hero, then a last "This".

This version keeps the reference's cut times and word timing to the frame, using real NixWoods footage and photos only:
- The opening is the Rubik's Cube lamp in its colour modes (green, red, warm, white), one still per sung word, as the
  stack.
- The seven "This" cuts are seven lamps:
  1. the NixLine lit in a hand;
  2. the Sculpted Glow by a bed;
  3. a linear pendant over a dining table (not named: three listed pendants could match it);
  4. the compact wall light;
  5. the bedside dimmer lamp;
  6. the Aurora coming on;
  7. the minimalist floor lamp.
  The sleek cylindrical floor lamp (AC4I9771) is left out because it is unlisted on Shopify (13 Oct).
- "Aaaaaaaand" is the Rubik's Cube lamp turned by hand as its colour changes.
- The last "This" is the Sculpted Glow again, in its dark-room shot (AC4I9882).

    python3 brand-reels/hey-stop-this/hey_stop_this.py [--ref-audio ref.wav --preview /tmp/p.mp4]

Writes out/<NAME>-in-app-audio.mp4 (silent track). The words only make sense with the song, so post it with Instagram's
"Use audio" on the reference reel, started at 0:00. There is no own-music version for that reason. Also a cover and a
sheet.
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import FF, FPS, H, W, S, SRC, R, font, grade_shot, shot_frames  # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261013-nixwoods-range-hey-stop-look-at-this-v1"
DUR = 8.40
SHOOT = lambda tag: [os.path.join(ROOT, "drive-pull", "shoot-20260805", f)
                     for f in os.listdir(os.path.join(ROOT, "drive-pull", "shoot-20260805")) if tag in f][0]
CUBE = R("rubik-reels/src/14-1.mp4")                                # 25 fps: green 0-3, red 3-5.5, warm 5.5-8, white 8.5-12


def photo(tag, cx, cy, w, push=0.05):
    return dict(kind="photo", path=SHOOT(tag), cx=cx, cy=cy, w=w, push=push)


def still(src, fps, t):
    return dict(kind="still", sh=S(src, fps, t))


def clip(sh, keep=0.35):
    return dict(kind="clip", sh=sh, keep=keep)


# (start s, shot, word, word x (None = centred), word y, size). Cut times are the reference's.
EDIT = [
    (0.000, still(CUBE, 25, 1.0), None, None, 900, 50),
    (0.625, still(CUBE, 25, 4.2), "Stop!", 110, 330, 56),
    (0.875, still(CUBE, 25, 6.6), "Stop!", 730, 520, 56),
    (1.250, still(CUBE, 25, 10.2), "Stop!", None, 600, 64),
    (1.750, still(CUBE, 25, 7.4), "Look at", None, 600, 50),
    (2.167, clip(S(R("floor-reels/src/nx06-7921.mp4"), 30, 7.9, straight=True, t_src=1.7)), "This", 150, 760, 54),
    (2.700, photo("AC4I9751", 1300, 3100, 2600), "This", 560, 330, 54),
    (3.400, photo("AC4I9665", 1824, 2600, 3078), "This", 720, 330, 54),
    (3.933, photo("AC4I9644", 1800, 2300, 2500), "This", None, 480, 54),
    (4.433, photo("AC4I9861", 2450, 3950, 1900), "This", 140, 330, 54),
    (5.033, clip(S(SRC("aurora-dimming-9x16.mp4"), 30, 0.6)), "This", 130, 1150, 54),
    (5.667, photo("AC4I9777", 1500, 3300, 2600), "This", None, 330, 54),
    (6.367, clip(S(CUBE, 25, 13.55), keep=0.8), "Aaaaaaaand", None, 420, 58),
    (7.667, photo("AC4I9882", 2060, 2900, 3000, push=0.03), "This", 150, 330, 58),
]
HEY = [(0.00, "H"), (0.12, "Hee"), (0.25, "Heeeee"), (0.40, "Heeeeeeee")]


def photo_frames(p, n):
    im = Image.open(p["path"]).convert("RGB")
    out = []
    for k in range(n):
        u = k / max(1, n - 1)
        w = p["w"] * (1 - p["push"] * u)
        h = w * H / W
        x0, y0 = p["cx"] - w / 2, p["cy"] - h / 2
        x0 = min(max(0, x0), im.width - w)
        y0 = min(max(0, y0), im.height - h)
        out.append(np.asarray(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))))
    return out


def shot(sh, n):
    if sh["kind"] == "photo":
        return grade_shot(photo_frames(sh, n))
    if sh["kind"] == "still":                                       # stop-motion: one held frame, its colour kept
        f = shot_frames(sh["sh"], 1 / FPS)[0]
        return grade_shot([f] * n, keep=0.85, target=0.30)
    return grade_shot(shot_frames(sh["sh"], n / FPS)[:n], keep=sh["keep"])


def word_layer(text, x, y, size):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("Fraunces-600.ttf", size)
    tw = f.getlength(text)
    xx = (W - tw) / 2 if x is None else x
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((xx, y + 3), text, font=f, fill=(0, 0, 0, 140))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))
    ImageDraw.Draw(lay).text((xx, y), text, font=f, fill=(246, 239, 228, 255))
    return np.asarray(lay, np.float32) / 255


def iris(t):
    """0-0.55 s: an iris opens from black (the reference's first beat)"""
    r = 1300 * min(1.0, max(0.0, (t - 0.08) / 0.47)) ** 1.6
    m = Image.new("L", (W, H), 0)
    if r > 1:
        ImageDraw.Draw(m).ellipse((540 - r, 900 - r, 540 + r, 900 + r), fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(3)), np.float32)[..., None] / 255


def build():
    n = round(DUR * FPS)
    frames = []
    for i, (t0, sh, word, x, y, size) in enumerate(EDIT):
        t1 = EDIT[i + 1][0] if i + 1 < len(EDIT) else DUR
        k = round(t1 * FPS) - round(t0 * FPS)
        fr = shot(sh, k)
        lay = word_layer(word, x, y, size) if word else None
        for j, f in enumerate(fr):
            t = (round(t0 * FPS) + j) / FPS
            o = f.astype(np.float32) / 255
            if i == 0:
                o = o * iris(t)
                txt = [w for at, w in HEY if at <= t][-1]
                L = word_layer(txt, None, y, size)
            else:
                L = lay
            o = o * (1 - L[..., 3:]) + L[..., :3] * L[..., 3:]
            frames.append((np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8))
    return frames[:n]


def encode(frames, wav, path):
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                          path], stdin=subprocess.PIPE)
    for f in frames:
        p.stdin.write(f.tobytes())
    p.stdin.close()
    assert p.wait() == 0, path


def wav(path, src=None):
    sr = 48000
    n = int(DUR * sr)
    m = np.zeros((n, 2), np.float32)
    if src:
        raw = subprocess.run([FF, "-v", "error", "-i", src, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(sr), "-f",
                              "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        m[:len(a)] = a
        m *= 0.89 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio")
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    fr = build()
    tmp = os.path.join(OUT, "_a.wav")
    wav(tmp)
    encode(fr, tmp, os.path.join(OUT, f"{NAME}-in-app-audio.mp4"))
    if a.ref_audio and a.preview:
        wav(tmp, a.ref_audio)
        encode(fr, tmp, a.preview)
    os.remove(tmp)
    Image.fromarray(fr[round(6.9 * FPS)]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    mids = [round(((t0 + (EDIT[i + 1][0] if i + 1 < len(EDIT) else DUR)) / 2) * FPS) for i, (t0, *_) in enumerate(EDIT)]
    mids = mids[1:13]
    sh = Image.new("RGB", (270 * 6, 480 * 2))
    for k, i in enumerate(mids):
        sh.paste(Image.fromarray(fr[i]).resize((270, 480)), (270 * (k % 6), 480 * (k // 6)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", len(fr), "frames")


if __name__ == "__main__":
    main()
