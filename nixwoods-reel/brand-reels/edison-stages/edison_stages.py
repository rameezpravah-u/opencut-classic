#!/usr/bin/env python3
"""NixWoods Edison dimmer lamp, "from wood to light" — after Callycoffee's DeSOVQngjHh (5.2 s: four empty
cups in one still frame; on each one-second beat, with a click, the next cup fills with the next stage —
beans, grounds, espresso, latte art — then it holds).

Here the four cups are four shelves, each a full-width strip of one real photo, AC4I9873 (the globe-bulb
Edison lamp on its rosewood block, 5 Aug shoot). Every stage is that same photo, edited, not generated:
  empty    the lamp taken out: the fluted wall continued column by column (its ribs are vertical, so each
           column's own wall colour carries straight down), the table under the block filled from either side
  block    the bulb and the dimmer taken off the block the same way
  off      the bulb in, unlit: the light over the wall (filament, glow in the glass) subtracted, the
           filament kept as a dark copper wire
  ember    the dimmer low: a third of the light, warmer
  lit      the photo as shot
Row 1 becomes the block on beat 1, row 2 the lamp off on beat 2, row 3 the ember on beat 3, row 4 the full
glow on beat 4, each with the dimmer's click (ElevenLabs SFX, sfx/). Then it holds, as the reference does.

    python3 brand-reels/edison-stages/edison_stages.py   # -> brand-reels/edison-stages/NW-EDISON-wood-to-light-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageOps
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
OUT = os.path.join(HERE, "NW-EDISON-wood-to-light-9x16.mp4")
CLICK = os.path.join(HERE, "sfx", "sfx-dimmer-click.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
ROW_H = H // 4
BEAT, TOTAL = 1.0, 5.6
TEAK = (58, 38, 24)

# regions in AC4I9873 pixels (3648 x 5472), measured on the 9873 crop
STRIP = (110, 3280, 3485, 3280 + round(3375 * ROW_H / W))   # full-width strip, 1080:480
ABOVE = (1600, 3280, 2720, 4264)                             # bulb, socket and dimmer: everything above the block
TOPFACE = [(1940, 4262, 2170, 4292), (2520, 4262, 2700, 4292)]  # socket and dimmer feet on the block's top face
LAMP = (1600, 3280, 2975, 4640)                              # the whole lamp (the table fill then covers from 4578)
TABLE = (1645, 4578, 2990, STRIP[3])                         # table where the block and its reflection stood
BULB = (1600, 3360, 2380, 4249)


def wall_model(a):
    """The fluted wall: each column's colour from the clean rows at the top of the strip, times the wall's
    vertical falloff measured in clean columns right of the lamp."""
    top = a[0:70].mean(0)                                                    # per column (strip coordinates)
    clean = a[:, 2930 - STRIP[0]:3400 - STRIP[0]].mean(1)                    # per row, right of the lamp
    g = clean / clean[0:70].mean(0)
    return top[None] * g[:, None]


def grain_like(a, box, shape, seed):
    x0, y0, x1, y1 = box
    patch = a[y0:y1, x0:x1]
    res = patch - gaussian_filter(patch, (2, 2, 0))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, res.shape[0] * res.shape[1], size=shape[0] * shape[1])
    return res.reshape(-1, 3)[idx].reshape(shape[0], shape[1], 3)


def stages():
    f = glob.glob(os.path.join(SHOOT, "*AC4I9873*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    a = np.asarray(im.crop(STRIP)).astype(np.float32) / 255
    ox, oy = STRIP[0], STRIP[1]
    rel = lambda b: (b[0] - ox, b[1] - oy, b[2] - ox, b[3] - oy)
    wall = wall_model(a)
    gr = grain_like(a, rel((2990, 3300, 3400, 4200)), a.shape[:2], 1)
    wall_g = np.clip(wall + gr, 0, 1)

    def fill_wall(img, box, feather=10):
        x0, y0, x1, y1 = rel(box)
        m = np.zeros(img.shape[:2], np.float32); m[y0:y1, x0:x1] = 1
        m = gaussian_filter(m, feather)[..., None]
        return img * (1 - m) + wall_g * m

    def fill_table(img, box, sides="both"):
        """Fill rows across a box from the clean surface beside it (both sides, or the right side only where
        the dried grass sits on the left), smoothed so the photo's row noise does not streak, then grained."""
        x0, y0, x1, y1 = rel(box)
        out = img.copy()
        right = gaussian_filter(img[y0:y1, x1:x1 + 50].mean(1), (2, 0))
        left = gaussian_filter(img[y0:y1, x0 - 40:x0].mean(1), (2, 0)) if sides == "both" else right
        u = np.linspace(0, 1, x1 - x0)[None, :, None]
        out[y0:y1, x0:x1] = left[:, None] * (1 - u) + right[:, None] * u + gr[y0:y1, x0:x1]
        m = np.zeros(img.shape[:2], np.float32); m[y0 - 3:y1, x0:x1 + 8] = 1
        m = gaussian_filter(m, (4, 4 if sides == "both" else 40))[..., None]   # a wide blend where one side is borrowed
        m[y0:y1, x0 + 60:x1] = 1
        return img * (1 - m) + out * m

    lit = a
    empty = fill_table(fill_wall(a, LAMP), TABLE, sides="right")
    block = fill_wall(a, ABOVE, feather=4)
    for b in TOPFACE:                                                        # the top face is even left to right
        block = fill_table(block, b)
    # the bulb's own light: what it adds over the wall behind it
    x0, y0, x1, y1 = rel(BULB)
    excess = np.zeros_like(a)
    excess[y0:y1, x0:x1] = np.clip(a[y0:y1, x0:x1] - wall[y0:y1, x0:x1], 0, None)
    fil = np.clip((a.mean(2) - 0.80) / 0.15, 0, 1) * (excess.sum(2) > 0.3)  # the filament wires
    fil = gaussian_filter(fil, 0.8)[..., None]
    off = np.clip(a - excess * 0.92, 0, 1)
    off = off * (1 - fil) + np.array([0.33, 0.21, 0.13], np.float32) * fil  # a dark copper wire
    ember = np.clip(off + excess * 0.36 * np.array([1.0, 0.62, 0.32], np.float32), 0, 1)
    look = lambda x: np.clip(x * 1.10 * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)  # MOTION photo grade, +10% exposure (the wall reads grey)
    sz = (W, ROW_H)
    return [Image.fromarray((look(s) * 255).astype(np.uint8)).resize(sz, Image.LANCZOS)
            for s in (empty, block, off, ember, lit)]


def main():
    S = stages()                                                             # 0 empty .. 4 lit
    final = [1, 2, 3, 4]                                                     # what each row becomes
    nf = round(TOTAL * FPS)
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    for f in range(nf):
        t = f / FPS
        fr = Image.new("RGB", (W, H))
        for r in range(4):
            fr.paste(S[final[r]] if t >= (r + 1) * BEAT else S[0], (0, r * ROW_H))
        d = ImageDraw.Draw(fr)
        for r in range(1, 4):                                               # the shelf edges between rows
            d.rectangle((0, r * ROW_H - 4, W, r * ROW_H + 3), fill=TEAK)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()

    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", "1.26", "-t", "0.16", "-i", CLICK, "-ac", "2", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    click = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    click *= np.linspace(1, 0, len(click))[:, None] ** 0.5
    click /= np.abs(click).max()
    x = np.zeros((round(TOTAL * sr), 2), np.float32)
    for r in range(4):
        a = int(((r + 1) * BEAT - 0.04) * sr)                                # the click's attack lands on the cut
        x[a:a + len(click)] += click * 0.55
    x += np.random.default_rng(2).normal(0, 0.0015, x.shape).astype(np.float32)  # a breath of room tone
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{TOTAL:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{TOTAL:.2f}s")


if __name__ == "__main__":
    main()
