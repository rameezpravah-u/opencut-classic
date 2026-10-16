"""NixWoods "10 to 01": the Minimalist Wooden Floor Lamp counted down through its making, after Vijay Lamps'
countdown reel (instagram.com/reel/DeR6W_cygHa). Ten steps, each a number over one shot, dipping to black between
them on the reference's own frames, so its audio sits on our cuts through Instagram's "Use audio".

Footage: the owner's workshop phone clips on Drive (raw/2026-08-14-phone/workshop) and the 5 Aug shoot. They are
fetched into library/cache/ with library/fetch.py and never committed (this repository is public). Their Drive
ids are only in the private nixwoods-os 30-Creative/library/INDEX.tsv.

    python3 brand-reels/countdown-making/countdown.py
"""
import glob, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import A, FF, FPS, H, W, font, grade_shot, src_dims, sstep   # noqa: E402
from made_well import encoder, mark                                           # noqa: E402

CACHE = os.path.join(ROOT, "library", "cache")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261016-wooden-floor-lamp-minimalist-standing-light-ten-to-one-v1"
SR = 48000

# the reference's dips to black (frame of darkest luma), measured on its 30 fps file
DIPS = [0.0, 1.467, 3.100, 4.500, 5.867, 7.433, 8.833, 10.400, 11.867, 13.367, 14.367]
DUR = 16.067
HALF = 0.17                      # each dip: 0.17 s down to black, 0.17 s back up

# step, label, file name (cached by library/fetch.py; its Drive id is in the private INDEX.tsv), in-point, crop box in source px (x, y, w) or None (whole frame), keep-sound gain
SHOTS = [
    ("10", "the log",          "IMG_4519.MOV", 5.0, None, 0),
    ("09", "sawn",             "IMG_4517.MOV", 0.35, (560, 1350, 856), 0),
    ("08", "planed",           "IMG_4412.MOV", 1.0, None, 0),
    ("07", "slotted for light", "IMG_4410.mov", 0.2, None, 0),
    ("06", "sanded by hand",   "IMG_4409.mov", 0.1, None, 0),
    ("05", "drilled",          "IMG_6562.MOV", 0.2, None, 0),
    ("04", "finished",         "IMG_6558.mov", 1.3, None, 0),   # 6559 has a face
    ("03", "wired",            "DA127F80-70A7-4A3D-ABC0-395BB38DE023.MP4", 2.4, None, 0),
    ("02", "on its base",      "IMG_4198.mov", 5.9, None, 0),
    # the clip's own cut from the dim pair to the lit pair lands where the reference's lamp comes on (13.83 s)
    ("01", "lit",              "IMG_4198.mov", 1.19, None, 0),
    ("",   "",
     "NW-CREATIVE-VID-20260806-minimalist-wooden-floor-lamp-sleek-cylindrical-lifestyle-arched-window-9x16-v1.mp4",
     1.0, None, 0),
]
# the 5 Aug file name says "sleek cylindrical"; the lamp on screen has the Minimalist's tell (a lit rod on a round
# wooden base), PRODUCT-ID.md. Its last 3 s carry a burned-in NX mark, so only 1.0-2.7 s is used.
# the phone was held a little off level in IMG_4198: these turns (degrees, measured on the lit rods) stand the lamps
# upright (MOTION.md: never leaning)
ROT = {"02": -2.0, "01": -1.5}
NAME_LINE = "Minimalist floor lamp"
FACT_LINE = "solid rosewood  ·  from ₹6,999"        # Shopify 16 Oct: 44 in ₹6,999, 60 in ₹9,999


def src(name):
    hits = glob.glob(os.path.join(CACHE, f"*-{name}"))
    if not hits:
        sys.exit(f"missing {name}: look up its drive_id in nixwoods-os 30-Creative/library/INDEX.tsv and fetch it "
                 "with library/fetch.py")
    return hits[0]


def clip(path, t_in, box, n, rot=0.0):
    """n frames at 30 fps, 1080x1920: the crop box (9:16, from x, y, width) or the whole portrait frame"""
    vf = [f"trim=start={t_in:.3f}", "setpts=PTS-STARTPTS", "fps=30"]
    if box:
        x, y, w = box
        vf.append(f"crop={w}:{round(w * H / W / 2) * 2}:{x}:{y}")
    if rot:
        vf.append(f"rotate={rot}*PI/180:c=black,scale=iw*1.07:ih*1.07,crop=iw/1.07:ih/1.07")
    vf += [f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase", f"crop={W}:{H}", "unsharp=5:5:0.3"]
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf", ",".join(vf), "-frames:v", str(n), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = list(np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3))
    assert len(fr) >= n - 2, (path, len(fr), n)
    return (fr + [fr[-1]] * n)[:n]


def number_layer(num, label):
    """the count, centred at about 30 % height as in the reference, with one small word under it"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = font("Inter-600.ttf", 170)
    tw = f.getlength(num)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.text(((W - tw) / 2 + 3, 470 + 5), num, font=f, fill=(20, 12, 8, 120))
    if label:
        g = font("Inter-400.ttf", 50)
        ds.text(((W - g.getlength(label)) / 2 + 2, 690 + 3), label, font=g, fill=(20, 12, 8, 150))
    from PIL import ImageFilter
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    d.text(((W - tw) / 2, 470), num, font=f, fill=(246, 239, 228, 255))
    if label:
        d.text(((W - g.getlength(label)) / 2, 690), label, font=g, fill=(246, 239, 228, 235))
    return np.asarray(lay, np.float32) / 255


def end_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    grad = np.zeros((H, W, 4), np.float32)
    y = np.arange(H)[:, None]
    grad[..., 3] = np.clip((y - 1000) / 380, 0, 1) * 0.80
    grad[..., :3] = np.array((30, 20, 13), np.float32) / 255
    lay.alpha_composite(Image.fromarray((grad * 255).astype(np.uint8)))
    d = ImageDraw.Draw(lay)
    f = font("Fraunces-600.ttf", 76)
    g = font("Inter-600.ttf", 40)
    d.text(((W - f.getlength(NAME_LINE)) / 2, 1265), NAME_LINE, font=f, fill=(246, 239, 228, 255))
    a, b = FACT_LINE.split("from ")
    x0 = (W - g.getlength(FACT_LINE)) / 2
    d.text((x0, 1380), a + "from ", font=g, fill=(200, 190, 178, 255))
    d.text((x0 + g.getlength(a + "from "), 1380), b, font=g, fill=(232, 162, 74, 255))
    return np.asarray(lay, np.float32) / 255


def over(base, lay, a=1.0):
    return base * (1 - lay[..., 3:] * a) + lay[..., :3] * lay[..., 3:] * a


def dip(t):
    """brightness at time t: 0 at each dip, back to 1 within HALF either side; the reel opens and ends in black"""
    v = 1.0
    for k in DIPS[1:]:
        v = min(v, sstep(abs(t - k) / HALF))
    v = min(v, sstep(t / 0.14), sstep((DUR - 0.12 - t) / 0.45))
    return v


def audio(path, sound):
    """sound=True: each shot's own recorded sound, levelled, with 40 ms fades at the dips and soft music1 under it.
    sound=False: a silent track, for the posting master that takes the reference's audio in the app."""
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)
    if sound:
        for k, s in enumerate(SHOTS):
            a, b = DIPS[k], (DIPS[k + 1] if k + 1 < len(DIPS) else DUR)
            raw = subprocess.run([FF, "-v", "error", "-ss", f"{s[3]:.3f}", "-i", src(s[2]), "-t",
                                  f"{b - a:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True).stdout
            x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
            if not len(x):
                continue
            rms = np.sqrt(np.mean(x ** 2)) + 1e-9
            x *= min(10 ** (-20 / 20) / rms, 10 ** (18 / 20))                  # to about -20 dBFS, lift at most 18 dB
            f = int(0.04 * SR)
            env = np.ones(len(x), np.float32)
            env[:f] = np.linspace(0, 1, f)[:len(env[:f])]
            env[-f:] = np.minimum(env[-f:], np.linspace(1, 0, f)[-len(env[-f:]):])
            i0 = int(a * SR)
            seg = (x * env[:, None])[: n - i0]
            m[i0:i0 + len(seg)] += seg
        raw = subprocess.run([FF, "-v", "error", "-i", A("../brand-reels/audio/music1-aesthetic.mp3"), "-t",
                              f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        mu = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        mu = mu / (np.sqrt(np.mean(mu ** 2)) + 1e-9) * 10 ** (-24 / 20)
        m[:len(mu)] += mu
        t = np.arange(n) / SR
        m *= np.clip((DUR - t) / 0.6, 0, 1)[:, None] * np.clip(t / 0.08, 0, 1)[:, None]
        m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


def main():
    os.makedirs(OUT, exist_ok=True)
    wavs = {k: os.path.join(OUT, f".{k}.wav") for k in ("in-app-audio", "own-sound")}
    audio(wavs["in-app-audio"], False)
    audio(wavs["own-sound"], True)
    encs = {k: encoder(v, os.path.join(OUT, f"{NAME}-{k}.mp4"), crf=23) for k, v in wavs.items()}   # under ~21 MB
    mk, endl = mark(), end_layer()
    done = 0
    keep = {}
    for k, s in enumerate(SHOTS):
        a, b = DIPS[k], (DIPS[k + 1] if k + 1 < len(DIPS) else DUR)
        n0, n1 = round(a * FPS), round(b * FPS)
        fr = clip(src(s[2]), s[3], s[4], n1 - n0, ROT.get(s[0], 0.0))
        fr = grade_shot(fr, keep=0.62, target=0.30 if s[0] else 0.21)
        num = number_layer(s[0], s[1]) if s[0] else None
        for i, f in enumerate(fr):
            t = (n0 + i) / FPS
            x = f.astype(np.float32) / 255
            if num is not None:
                x = over(x, num)
            else:
                x = over(x, endl, sstep((t - a - 0.25) / 0.35))
            x = over(x, mk, 0.9)
            x = x * dip(t) + 0.02 * (1 - dip(t))                                 # MOTION.md: blacks keep a little air
            px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
            for e in encs.values():
                e.stdin.write(px.tobytes())
            if i == len(fr) // 2:
                keep[s[0] or "end"] = px
            done += 1
    for e in encs.values():
        e.stdin.close()
        e.wait()
    for v in wavs.values():
        os.remove(v)
    ims = [Image.fromarray(keep[k]).resize((270, 480)) for k in keep]
    sheet = Image.new("RGB", (270 * 6, 480 * 2), (20, 20, 20))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 6) * 270, (i // 6) * 480))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep["01"]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", done, "frames")


if __name__ == "__main__":
    main()
