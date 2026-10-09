#!/usr/bin/env python3
"""NixWoods "Anatomy of light" — a recreation of @yi.rop's "Tomato Anatomy" (DbqpMAcuDQs, 12.6 s,
360k views) with NixWoods products. Clean images only (Rameez, 9 Oct): the 5 Aug 2026 studio shoot
(drive-pull/shoot-20260805, never the watermarked archive), cropped per plates.json. Nothing generated.

The reference's structure, on its 0.25 s grid (our music is retimed to 120 bpm so the grid is the beat):
  0.00-2.25  black; a 3x3 grid fills one tile at a time, all black-and-white
  2.50-4.75  tiles flip to colour one by one
  5.00-9.25  full-screen high-key "lab plates" (tiny logo top, tiny caption bottom, dish/scale marks):
             a black-and-white run, then the same plates in colour
  9.25-11.0  black-and-white / colour flicker on full-bleed textures
  11.25-end  colour run-out, ending on the hero (NixLine)

    python3 brand-reels/anatomy/anatomy.py   # -> brand-reels/anatomy/NW-ANATOMY-nixwoods-anatomy-of-light-9x16.mp4
"""
import glob, json, os, subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "drive-pull", "shoot-20260805")
A = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "NW-ANATOMY-nixwoods-anatomy-of-light-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music3-design.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
TW, TH, G = 358, 637, 3                     # 3x3 tiles with 3 px black gutters
INK, GREY = (34, 30, 28), (120, 112, 106)
WARM = (150, 92, 48)
END = 13.0

GRID = ["P1", "P2", "P6", "P4", "P5", "P3", "P7", "P9", "P8"]
T_IN = [0.00, 0.50, 0.75, 1.00, 1.25, 1.75, 2.00, 2.25, 2.25]
T_COL = [2.50, 3.00, 3.25, 3.50, 3.75, 4.00, 4.50, 4.75, 4.75]
# full-screen run: (start, plate, colour?)
RUN = [(5.00, "P1", 0), (5.25, "P2", 0), (5.75, "P3", 0), (6.00, "P4", 0), (6.25, "P5", 0), (7.00, "P6", 0),
       (7.25, "P7", 0), (7.50, "P1", 1), (7.75, "P2", 1), (8.00, "P3", 1), (8.50, "P4", 1), (8.75, "P5", 1),
       (9.25, "P7", 0), (9.75, "P7", 1), (10.00, "P6", 0), (10.25, "P6", 1), (10.50, "P8", 0), (11.00, "P8", 1),
       (11.25, "P2", 0), (11.50, "P2", 1), (11.75, "P3", 1), (12.00, "P4", 1), (12.25, "P1", 1)]


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def crop(v, scale=1.08):
    f = glob.glob(os.path.join(SRC, f"*{v['photo']}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    cx, cy, h = v["box"]
    ch = h * im.height; cw = ch * 9 / 16
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    return im.resize((round(W * scale), round(H * scale)), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))


def high_key(im, colour, bleed):
    """The reference's look: the wall goes to clean white, the object stays crisp and dark."""
    a = np.asarray(im).astype(np.float32) / 255
    L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    w = np.percentile(L, 97 if bleed else 70)
    b = np.percentile(L, 0.5)
    Ln = np.clip((L - b) / max(w - b, 1e-3), 0, 1) ** 1.15
    if not colour:
        out = np.repeat(Ln[..., None], 3, 2)
    else:
        if not bleed:                                                       # neutralise the wall: white stays white
            sel = (L >= np.percentile(L, 60)) & (L < 0.97)                  # the wall, not the clipped LED
            if sel.sum() > 1000:
                wall = a[sel].mean(0)
                hl = np.clip((L - 0.75) / 0.2, 0, 1)[..., None]             # the light itself keeps its warmth
                a = np.clip(a * (wall.mean() / np.maximum(wall, 1e-3)) * (1 - hl) + a * hl, 0, 1)
                L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
        gain = (Ln / np.maximum(L, 1e-3))[..., None]
        out = np.clip(a * gain, 0, 1)
        lum = (out @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        out = np.clip(lum + (out - lum) * 1.3, 0, 1)                       # a little more colour
    return Image.fromarray((out * 255).astype(np.uint8))


def dressing(v, colour, plate=None):
    """Tiny logo top, tiny caption bottom, and the lab marks: a dish circle or a measuring scale.
    The caption turns light where the bottom of the plate is dark wood."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dark = plate is not None and np.asarray(plate.convert("L").crop((300, 1740, 780, 1830))).mean() < 120
    cap, cap2 = ((246, 239, 228), (220, 212, 202)) if dark else (INK, GREY)
    d = ImageDraw.Draw(layer)
    mark = (WARM if colour else INK) + (255,)
    if v.get("lab") == "dish":
        d.ellipse((W / 2 - 430, H / 2 - 430 - 40, W / 2 + 430, H / 2 + 430 - 40), outline=mark, width=4)
    if v.get("lab") == "scale":
        x, y0, y1 = 560, 330, 1560
        d.line((x, y0, x, y1), fill=mark, width=3)
        for i in range(31):                                                 # 30 inches, a tick each
            y = y1 - i * (y1 - y0) / 30
            ln = 34 if i % 5 == 0 else 16
            d.line((x, y, x + ln, y), fill=mark, width=3)
            if i % 10 == 0:
                d.text((x + 46, y), str(i), font=font("Inter-400.ttf", 26), fill=mark, anchor="lm")
    if v["kind"] == "isolated":
        lg = Image.open(os.path.join(A, "logo.png")).convert("RGBA")
        lg = lg.crop(lg.getbbox()); s = 96 / lg.width
        lg = lg.resize((96, round(lg.height * s)), Image.LANCZOS)
        tint = Image.new("RGBA", lg.size, INK + (0,)); tint.putalpha(lg.getchannel("A"))
        layer.alpha_composite(tint, ((W - 96) // 2, 96))
        d.text((W // 2, 1752), v["label"], font=font("Fraunces-500-i.ttf", 28), fill=cap + (255,), anchor="ma")
        d.text((W // 2, 1796), "NixWoods Lab · solid wood lighting", font=font("Inter-400.ttf", 20), fill=cap2 + (255,), anchor="ma")
    return layer


def main():
    P = {k: v for k, v in json.load(open(os.path.join(HERE, "plates.json"))).items() if not k.startswith("_")}
    base = {k: crop(v) for k, v in P.items()}
    full = {}
    for k, v in P.items():
        for c in (0, 1):
            im = high_key(base[k], c, v["kind"] == "bleed")
            vis = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
            full[k, c] = (im, dressing(v, c, vis))
    tiles = {(k, c): high_key(base[k], c, P[k]["kind"] == "bleed").resize((TW, TH), Image.LANCZOS)
             for k in GRID for c in (0, 1)}

    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    n = round(END * FPS)
    for k in range(n):
        t = k / FPS + 1e-6
        if t < 5.0:                                                         # the grid
            fr = Image.new("RGB", (W, H), (0, 0, 0))
            for i, p in enumerate(GRID):
                if t >= T_IN[i]:
                    fr.paste(tiles[p, int(t >= T_COL[i])], ((i % 3) * (TW + G), (i // 3) * (TH + G)))
        else:                                                               # the plates
            j = max(i for i, r in enumerate(RUN) if r[0] <= t)
            t0, p, c = RUN[j]
            t1 = RUN[j + 1][0] if j + 1 < len(RUN) else END
            u = (t - t0) / (t1 - t0)
            im, dr = full[p, c]
            z = 1.0 + 0.035 * u                                             # the reference's slow creep in
            bw, bh = W / z, H / z
            x0, y0 = (im.width - bw) / 2, (im.height - bh) / 2
            fr = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)).convert("RGBA")
            fr.alpha_composite(dr)
            fr = fr.convert("RGB")
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    # music3-design from its measured drop (10.752 s), retimed 99.4 -> 120 bpm (pitch kept)
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-ss", "10.752", "-i", MUSIC, "-filter_complex",
                    f"[1:a]atempo={120 / 99.4:.5f},atrim=0:{END:.3f},volume=0.9,afade=t=out:st={END - 0.8:.3f}:d=0.8,"
                    f"alimiter=limit=0.95[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-movflags", "+faststart", "-t", f"{END:.3f}", OUT], check=True)
    os.remove(tmp)
    print(os.path.relpath(OUT, ROOT), f"{END:.2f}s")


if __name__ == "__main__":
    main()
