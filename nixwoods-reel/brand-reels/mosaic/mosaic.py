#!/usr/bin/env python3
"""NixWoods mosaic reel — after @thedelhidecorcompany's DdynGS4zTbg (5.3 s, 306k views).

What the reference does, frame by frame (30 fps):
  0.0–0.3 s   an empty ground in one deep colour taken from the photos' own palette
  0.3–1.5 s   a 3 x 4 grid of edge-to-edge portrait tiles fills one cell at a time (hard pops)
  1.5–3.5 s   single tiles keep swapping to new shots; a few blink back to the ground
  ~3.1 s      a serif wordmark lands across the middle of the grid
  3.5–4.5 s   tiles drop out one by one
  4.5 s–end   the wordmark alone on the ground
It works because every tile is the same world: one shoot, one palette, wide shots and close details.

Ours: the clean 5 Aug 2026 studio shoot from Drive (NW-CREATIVE-IMG-20260805-*, never the
watermarked archive), each photo cropped twice (the room, and a close detail), all graded to one
warm look on a deep teak ground, the NixWoods logo as the wordmark.

    python3 brand-reels/mosaic/mosaic.py [crops.json] [out.mp4]
"""
import json, os, random, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(ROOT, "drive-pull", "shoot-20260805")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
COLS, ROWS = 3, 4
TW, TH = W // COLS, H // ROWS                      # 360 x 480, the reference's 3:4 tiles
GROUND = (46, 30, 20)                               # deep teak, sampled from the shoot's wood
CREAM = (246, 238, 226)
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
BEAT, OFF = 0.8357, 0.396                           # music6-corners, measured grid

# timeline, in frames (30 fps); the reference's beats stretched to 6.4 s so the end card can be read
T_FILL0, T_FILL1 = 9, 45        # first tile pops / grid full
T_LOGO = 96                     # wordmark lands (a beat of the track: 0.396 + 4 * 0.8357 = 3.74 s)
T_DROP0, T_DROP1 = 112, 150     # tiles drop out
N = 192                         # 6.4 s


def grade(im):
    """One warm, slightly soft look for every tile, whatever time of day it was shot."""
    a = np.asarray(im).astype(np.float32) / 255
    luma = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    a = a * 0.82 + luma[..., None] * 0.18                  # take the edge off the colour
    a = np.clip(a, 0, 1) ** 1.08                          # a touch deeper in the mids
    a *= np.array([1.07, 1.0, 0.86], np.float32)          # warm: white walls become cream
    a = 0.03 + a * 0.95                                   # lift the blacks a little, film-like
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def tile(path, box):
    """box = [cx, cy, h] as fractions of the photo: centre of the crop and its height. 3:4 aspect."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    cx, cy, h = box
    ch = h * im.height
    cw = ch * TW / TH
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    t = im.resize((TW, TH), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return grade(t)


def ground():
    """The teak ground: flat colour, a soft vignette, fine grain so it doesn't band."""
    rng = np.random.default_rng(7)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H / 2) / H) ** 2)
    v = 1.08 - 0.35 * r
    a = np.array(GROUND, np.float32)[None, None, :] * v[..., None]
    a += rng.normal(0, 2.2, (H, W, 1))
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def logo_layer():
    lg = Image.open(os.path.join(ROOT, "assets", "logo.png")).convert("RGBA")
    lg = lg.crop(lg.getbbox())
    s = 520 / lg.width
    lg = lg.resize((round(lg.width * s), round(lg.height * s)), Image.LANCZOS)
    tint = Image.new("RGBA", lg.size, CREAM + (0,))
    tint.putalpha(lg.getchannel("A"))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    x, y = (W - lg.width) // 2, (H - lg.height) // 2 - 40
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.paste((10, 6, 3, 170), (x + 4, y + 8), lg.getchannel("A"))
    layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    layer.alpha_composite(tint, (x, y))
    return layer, y + lg.height


def url_layer(y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = ImageFont.truetype(os.path.join(ROOT, "assets", "Inter-400.ttf"), 34)
    d.text((W // 2, y + 70), "solid-wood lighting  ·  nixwoods.com", font=f, fill=CREAM + (215,), anchor="ma")
    return layer


def schedule(pool, rng):
    """For every frame, what each of the 12 cells shows: a tile index, or None for the ground."""
    cells = list(range(COLS * ROWS))
    fill_order = cells[:]; rng.shuffle(fill_order)
    drop_order = cells[:]; rng.shuffle(drop_order)
    deck = list(range(len(pool))); rng.shuffle(deck)
    used = 0

    def draw():
        nonlocal used, deck
        if used >= len(deck):
            deck = list(range(len(pool))); rng.shuffle(deck); used = 0
        used += 1
        return deck[used - 1]

    state = [None] * len(cells)
    blink = {}                                      # cell -> frame it comes back
    frames = []
    fill_step = (T_FILL1 - T_FILL0) / (len(cells) - 1)
    drop_step = (T_DROP1 - T_DROP0) / (len(cells) - 1)
    for f in range(N):
        for i, c in enumerate(fill_order):          # 1. fill, one cell at a time
            if f == T_FILL0 + round(i * fill_step):
                state[c] = draw()
        if T_FILL1 < f < T_DROP0 and f % 3 == 0:    # 2. shimmer: swaps and blinks every 3 frames
            live = [c for c in cells if state[c] is not None and c not in blink]
            for c in rng.sample(live, min(2, len(live))):
                if rng.random() < 0.22:
                    state[c] = None; blink[c] = f + rng.choice((3, 6))
                else:
                    state[c] = draw()
        for c, back in list(blink.items()):
            if f >= back:
                state[c] = draw(); del blink[c]
        for i, c in enumerate(drop_order):          # 3. drop out, one at a time
            if f == T_DROP0 + round(i * drop_step):
                state[c] = None; blink.pop(c, None)
        frames.append(list(state))
    return frames


def main():
    crops = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "crops.json")))
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "NW-BRAND-mosaic-9x16.mp4")
    pool = []
    for name, boxes in crops.items():
        for b in boxes:
            pool.append(tile(os.path.join(SRC, name), b))
    rng = random.Random(20261007)
    sched = schedule(pool, rng)
    base = ground()
    logo, logo_bottom = logo_layer()
    url = url_layer(logo_bottom)

    tmp = out + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    for f, state in enumerate(sched):
        fr = base.copy()
        for c, t in enumerate(state):
            if t is not None:
                fr.paste(pool[t], ((c % COLS) * TW, (c // COLS) * TH))
        if f >= T_LOGO:
            fr = fr.convert("RGBA"); fr.alpha_composite(logo)
            if f >= T_DROP1:
                k = min((f - T_DROP1) / 8, 1.0)
                u = url.copy(); u.putalpha(u.getchannel("A").point(lambda p: int(p * k)))
                fr.alpha_composite(u)
            fr = fr.convert("RGB")
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    dur = N / FPS
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-ss", f"{OFF:.3f}", "-t", f"{dur:.3f}",
                    "-i", MUSIC, "-filter_complex",
                    f"[1:a]volume=0.9,afade=t=in:d=0.08,afade=t=out:st={dur - 0.9:.3f}:d=0.9[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{dur:.3f}", out], check=True)
    os.remove(tmp)
    print(os.path.relpath(out, ROOT), f"{dur:.2f}s, {len(pool)} tiles from {len(crops)} photos")


if __name__ == "__main__":
    main()
