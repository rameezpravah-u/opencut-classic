#!/usr/bin/env python3
"""NixLine sticky-note ad - one hand-written claim stuck into a real phone frame.

Built from the rules in system/refs/instagram/DeGkawhCB2j (read slide by slide):
  1 native, not pretty  -> Rameez's own phone frame, no grade, no designer type
  2 stop the thumb, sell the next click -> ONE claim on a pink sticky note, like "Moms! This acne
    killer works!"; nothing else on the image
  3 one USP angle, written onto the scene -> teak vs metal, in marker
  5 the page must match the ad -> see README: the PDP does not yet (AI renders, 999 INR)
The claim is the account's best-scoring hook, "stop buying metal floor lamps." (9/12, all gates).
No AI frames, no review (none verified yet - never invent one).

    python3 floor-reels/static/sticky_ad.py      # -> out/static/nixline-sticky-{4x5,9x16}.jpg
"""
import math, os, subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MARKER = os.path.join(ROOT, "..", "assets", "PermanentMarker-400.ttf")
OUT = os.path.join(ROOT, "out", "static")
FF = imageio_ffmpeg.get_ffmpeg_exe()

SRC = ("src/nx07-7922.mp4", 0.05)          # hand presenting the lit lamp over the workshop floor
LINES = ["Stop buying", "metal floor", "lamps!"]
PINK = (255, 140, 178)
FORMATS = {   # size, crop y0 into the 1080x1920 frame, note side, note centre, rotation (deg)
    "4x5":  {"size": (1080, 1350), "y0": 430, "note": 405, "centre": (232, 290), "rot": 5},
    "9x16": {"size": (1080, 1920), "y0": 0,   "note": 330, "centre": (262, 640), "rot": 5},
}
SAFE_9x16 = (70, 230, 950, 1500)


def grab(clip, t):
    p = subprocess.run([FF, "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", os.path.join(ROOT, clip),
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, stdin=subprocess.DEVNULL, check=True)
    return Image.fromarray(np.frombuffer(p.stdout, np.uint8).reshape(1920, 1080, 3))


def sticky_note(side):
    """A square paper note: flat pink, faint fibre noise, darker adhesive band, lifted bottom corner."""
    rng = np.random.default_rng(7)
    a = np.ones((side, side, 3), np.float32) * np.array(PINK, np.float32)
    a *= 1 + rng.normal(0, 0.018, (side, side, 1)).astype(np.float32)          # paper tooth
    y = np.linspace(0, 1, side, dtype=np.float32)[:, None, None]
    a *= 0.97 + 0.05 * y                                                        # light falls down the note
    a[: int(side * 0.16)] *= 0.94                                               # adhesive strip reads darker
    yy, xx = np.mgrid[0:side, 0:side].astype(np.float32) / side
    curl = np.clip((xx + yy - 1.55) / 0.45, 0, 1)[..., None]                    # bottom-right corner lifts
    a *= 1 - 0.22 * curl
    note = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(note)
    size = int(side * 0.19)                                                     # largest size that fits:
    while True:                                                                 # lines within 90% of the width,
        font = ImageFont.truetype(MARKER, size)                                 # block within 74% of the height
        lh = int(size * 1.05)
        if max(font.getlength(l) for l in LINES) <= side * 0.90 and lh * len(LINES) <= side * 0.74:
            break
        size -= 2
    top = (side - lh * len(LINES)) // 2 - int(side * 0.02)
    for i, l in enumerate(LINES):
        w = font.getlength(l)
        x = (side - w) / 2 + (i - 1) * side * 0.012                            # hand-written drift
        d.text((x, top + i * lh), l, font=font, fill=(24, 20, 22, 255))
    # marker underline under the last word, slightly wavy
    w = font.getlength(LINES[-1])
    x0, x1 = (side - w) / 2 - side * 0.02, (side + w) / 2 + side * 0.06
    yb = top + len(LINES) * lh + side * 0.01
    pts = [(x0 + (x1 - x0) * k / 20, yb + math.sin(k / 3.0) * side * 0.006) for k in range(21)]
    d.line(pts, fill=(24, 20, 22, 255), width=max(3, side // 70), joint="curve")
    return note


def place(img, note, centre, rot):
    rotated = note.rotate(rot, resample=Image.BICUBIC, expand=True)
    shadow = Image.new("RGBA", rotated.size, (0, 0, 0, 0))
    shadow.putalpha(rotated.getchannel("A").point(lambda v: v * 0.30))      # lying flat on the floor:
    shadow = shadow.filter(ImageFilter.GaussianBlur(5))                       # a tight contact shadow
    x = centre[0] - rotated.width // 2
    y = centre[1] - rotated.height // 2
    img.paste(shadow, (x + 3, y + 5), shadow)
    img.paste(rotated, (x, y), rotated)
    return (x, y, x + rotated.width, y + rotated.height)


def render(fmt):
    f = FORMATS[fmt]
    W, H = f["size"]
    img = grab(*SRC).crop((0, f["y0"], W, f["y0"] + H)).convert("RGB")
    img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    box = place(img, sticky_note(f["note"]), f["centre"], f["rot"])
    if fmt == "9x16":
        assert box[0] >= SAFE_9x16[0] and box[1] >= SAFE_9x16[1] and box[2] <= SAFE_9x16[2] and box[3] <= SAFE_9x16[3], box
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"nixline-sticky-{fmt}.jpg")
    img.save(out, quality=93, subsampling=0)
    return out, box


if __name__ == "__main__":
    for fmt in FORMATS:
        out, box = render(fmt)
        print(os.path.relpath(out, ROOT), "note box", box)
