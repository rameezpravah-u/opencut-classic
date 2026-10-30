#!/usr/bin/env python3
"""NixWoods "the art of making": our workshop and our lights, cut on A-DIY's pattern (instagram.com/reel/DfDCMtChEYy,
@decks, 28 Oct 2026, 14k views; owner 30 Oct: "Make like this").

The reference, every frame seen (8.1 s, 720x1280, music only):
- 13 static shots, each held about 0.62 s (cuts every 18-19 frames at 30 fps), no camera moves, no transitions;
- materials and machines as texture: stacked stick ends (the hook), a control panel, timber, ducting, sawdust, a
  machine wheel, belts, chips on a conveyor, a green machine, steel rods, the shop floor, planks;
- one small lowercase line, "the art of making", white, centred at mid-frame, on screen from frame 1 to the end;
- a muted grade; no logo, no price, no end card.

Ours: the same grammar on our own real footage, no faces. Thirteen shots on music3's beat grid (0.6036 s, the
nearest of our tracks to the reference's 0.62 s), the drop on the first cut, the finished light last and held two
beats with "nixwoods.com" under the line. Each shot is the sharpest steady 0.6 s of its clip (system/clip_triage.py),
graded with the MOTION.md montage grade. Text: Inter 400 at the reference's size and place.

    python3 brand-reels/art-of-making/art_of_making.py [--frames 0.3,4.0]
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import font, LUMW  # noqa: E402

FF = "/usr/bin/ffmpeg"                                      # has zscale for the iPhone HLG tone-map
W, H, FPS, SR = 1080, 1920, 30, 48000
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261030-nixwoods-art-of-making-v1"
TM = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
FEST = lambda n: os.path.join(ROOT, "brand-reels", "festive-ad-cuts", "src", n)
LIGHT = lambda n: os.path.join(ROOT, "brand-reels", "art-light", "src", n)
FLOOR = lambda n: os.path.join(ROOT, "floor-reels", "src", n)
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music3-design.mp3")
BEAT = 0.6036
M_OFF = 10.161                                              # music3 from 10.161 s: its drop (10.765 s) lands on cut 1
LINE_Y = 960                                                # the reference's line sits at mid-frame

# (source, in-point s, x-anchor for landscape sources, zoom, y-centre of the zoom as a fraction of the frame[,
#  mean-luma target]):
# one beat each, the last two beats
SEQ = [
    (FEST("IMG_7984.mov"), 0.85, 0.50, 1.00, 0.5),   # routed bars in rows: the repeating-pattern hook (ref: stick ends)
    (FEST("FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4"), 1.40, 0.5, 1.10, 0.5),  # teak planks (clean span 1.2-2.6 s)
    (FEST("IMG_7698.mov"), 1.85, 0.5, 1.00, 0.5),    # the router in pine (ref: machine)
    (FEST("IMG_7653.mov"), 0.15, 0.5, 1.00, 0.5),    # strips in the sawdust (ref: sawdust)
    (LIGHT("IMG_8123.mov"), 0.10, 0.5, 2.00, 0.685, 0.42),  # flame grain and holes, light off: 4K at 2x is native
    #                                          (luma 0.42: at 0.31 the bright wall drags the grain to black)
    (FEST("IMG_7990.mov"), 0.15, 0.5, 1.00, 0.5),    # black-finished bars, fanned (ref: steel rods)
    (LIGHT("IMG_8123.mov"), 2.55, 0.5, 1.80, 0.53, 0.42),   # the row of holes above the frame (4K; 8122 pans soft)
    (FEST("NW-RAW-20261011-unknown-7d43cbb6.mov"), 0.00, 0.5, 1.00, 0.5),  # bars bundled, lit (sharpest frames first)
    (FEST("IMG_7991.mov"), 0.05, 0.5, 1.00, 0.5),    # a bar switched on, on test
    (FEST("IMG_7992.mov"), 0.85, 0.5, 1.00, 0.5),    # a lit bar over the black bars
    (LIGHT("IMG_8118.mov"), 1.20, 0.5, 1.30, 0.58),   # lit holes under dark grain
    (FLOOR("nx01-7923.mp4"), 0.00, 0.5, 1.00, 0.5),  # a lit teak bar on the floor
    (LIGHT("IMG_8114.mov"), 1.75, 0.5, 1.00, 0.5),   # the finished light over the painting, settled
]
CUTS = [round(k * BEAT, 4) for k in range(len(SEQ))]
DUR = round((len(SEQ) + 1) * BEAT, 4)                       # the last shot holds two beats: 8.45 s


def probe(path):
    o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height,color_transfer:stream_side_data=rotation", "-of", "csv=p=0:s=,", path],
                       capture_output=True, text=True).stdout.split()
    first = o[0].split(",")
    w, h, trc = int(first[0]), int(first[1]), first[2] if len(first) > 2 else ""
    rot = next((abs(int(float(x))) for x in o[1:] if x.lstrip("-").replace(".", "").isdigit()), 0)
    if rot == 90:
        w, h = h, w
    return w, h, trc in ("arib-std-b67", "smpte2084")


def frames(src, t_in, xf, zoom, yc, n):
    sw, sh, hdr = probe(src)
    # one scale straight from the source to the zoomed size (a 4K clip at 2x stays native), then the crop
    if sw / sh > W / H:                                      # landscape: cover the height, choose the x
        zh = round(H * zoom / 2) * 2
        zw = round(sw * zh / sh / 2) * 2
        x0 = round((zw - W) * xf)
    else:
        zw = round(W * zoom / 2) * 2
        zh = round(sh * zw / sw / 2) * 2
        x0 = (zw - W) // 2
    y0 = min(max(0, round(zh * yc - H / 2)), zh - H)
    geo = f"scale={zw}:{zh}:flags=lanczos,crop={W}:{H}:{x0}:{y0}"
    vf = (TM + "," if hdr else "") + f"fps={FPS}," + geo
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", src, "-frames:v", str(n + 1), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    return [fr[min(k, len(fr) - 1)] for k in range(n)]


def grade(frames_, keep=0.20, target=0.31):
    """MOTION.md's montage grade with the reference's tint: keep 20 % of each shot's own colour (not 35 %: our teak
    is far warmer than their pine), the rest one muted near-neutral tint, every shot at mean luma 0.31, a lit channel
    keeps its cream core. Measured on A-DIY's 13 shots: R/G 1.03-1.15, B/G 0.81-0.98 (spreads 0.13 / 0.17); ours
    lands at R/G 1.14-1.30, B/G 0.70-0.87 (spreads 0.16 / 0.17)."""
    tint = np.array([1.08, 1.0, 0.90], np.float32)
    tint /= tint @ LUMW
    mid = frames_[len(frames_) // 2].astype(np.float32) / 255
    L = mid @ LUMW
    toned = np.clip(keep * mid + (1 - keep) * L[..., None] * tint, 1e-4, 1)
    lo, hi = 0.3, 3.0
    for _ in range(30 if target is not None else 0):
        g = (lo + hi) / 2
        lo, hi = (g, hi) if np.mean(toned ** g @ LUMW) > target else (lo, g)
    g = (lo + hi) / 2 if target is not None else 1.0
    cream = np.array([1.0, 0.933, 0.824], np.float32)
    out = []
    for f in frames_:
        x = f.astype(np.float32) / 255
        Lx = x @ LUMW
        t = np.clip(keep * x + (1 - keep) * Lx[..., None] * tint, 0, 1) ** g
        core = np.clip((Lx - 0.88) / 0.1, 0, 1)[..., None]
        out.append(((t * (1 - core) + cream * core) * 255).clip(0, 255).astype(np.uint8))
    return out


def text_layer(t_last):
    """"the art of making", Inter 400 34 px white with a soft shadow, at mid-frame; nixwoods.com joins it on the last
    shot."""
    def lay(with_url):
        im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        f, f2 = font("Inter-400.ttf", 34), font("Inter-600.ttf", 28)
        rows = [("the art of making", f, LINE_Y)] + ([("nixwoods.com", f2, LINE_Y + 52)] if with_url else [])
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for s, ff, y in rows:
            ImageDraw.Draw(sh).text((W / 2, y + 2), s, font=ff, fill=(0, 0, 0, 150), anchor="mm")
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
        for s, ff, y in rows:
            ImageDraw.Draw(im).text((W / 2, y), s, font=ff, fill=(255, 255, 255, 242), anchor="mm")
        return np.asarray(im, np.float32)
    return lay(False), lay(True)


def music(path):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{M_OFF:.3f}", "-i", MUSIC, "-t", f"{DUR:.3f}", "-ac", "2", "-ar",
                          str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(DUR * SR)
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    t = np.arange(n) / SR
    m *= (np.clip(t / 0.05, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1))[:, None]         # MOTION: fade the last 0.8 s
    m *= 0.89 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def build():
    out = []
    ends = CUTS[1:] + [DUR]
    for (src, t_in, xf, zoom, yc, *tg), a, b in zip(SEQ, CUTS, ends):
        n = round(b * FPS) - round(a * FPS)
        out += grade(frames(src, t_in, xf, zoom, yc, n), target=tg[0] if tg else 0.31)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", default=None)
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    fr = build()
    t1, t2 = text_layer(CUTS[-1])
    last = round(CUTS[-1] * FPS)
    rng = np.random.default_rng(30)

    def comp(i):
        txt = t2 if i >= last else t1
        al = txt[..., 3:] / 255
        o = fr[i].astype(np.float32) * (1 - al) + txt[..., :3] * al + rng.normal(0, 2.2, (H, W, 1))
        return o.clip(0, 255).astype(np.uint8)

    if a.frames:
        for s in a.frames.split(","):
            Image.fromarray(comp(min(round(float(s) * FPS), len(fr) - 1))).save(
                os.path.join(a.out, f"f-{float(s):05.2f}.jpg"), quality=90)
        return
    path = os.path.join(a.out, NAME + ".mp4")
    wav = path + ".wav"
    music(wav)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k", "-shortest",
                          "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        p.stdin.write(comp(min(i, len(fr) - 1)).tobytes())
    p.stdin.close()
    assert p.wait() == 0, path
    os.remove(wav)
    print("wrote", path, "cuts", CUTS, "dur", DUR)


if __name__ == "__main__":
    main()
