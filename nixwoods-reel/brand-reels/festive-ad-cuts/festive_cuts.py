#!/usr/bin/env python3
"""Festive ad cuts for the Meta ads inbox (social desk request, 11 Oct 2026, task CREATIVE-festive-ad-cuts-20261013).

Three products, each in a 10 s and a 15 s cut (owner, 12 Oct: "Both lengths"), each in 9:16 and 4:5 = 12 files.
Concepts from 40-Content/IDEA-BANK.md (nixwoods-os):
  aurora   FESTIVE-P1-01  "A new thing for the house. / Made the slow way."   raw teak -> routed bars -> bar lit last
  nixline  FESTIVE-P1-06  "Solid teak. / Made to keep."                       hands on the teak stem -> switch-on last
  rubiks   FESTIVE-P1-08  "What a brother gives on Bhai Dooj: / something she keeps."  hand turns the lit cube warm

Rules held: real footage only (no generated frame, so no AI label); price on screen before 10 s, live Shopify price
(12 Oct: Aurora from 1,999, NixLine 999, Rubik's Cube from 2,999); nixwoods.com on the end card; lamps upright (the
NixLine shots are straightened); no delivery date, "order by" or ritual claim; no "brass" or "not iron" line;
"Rubik's" stays (D-017). Look and type from MOTION.md (Fraunces + Inter, cream / amber, montage grade, 30 fps,
cuts on the music grid). The Aurora cut has no hands: every Aurora hand clip on Drive is over the 7 MB the connector
can fetch (README).

    python3 brand-reels/festive-ad-cuts/festive_cuts.py                   # all 12
    python3 brand-reels/festive-ad-cuts/festive_cuts.py --only nixline --frames 1,5,9   # stills
"""
import argparse, os, subprocess, sys, wave

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import axis                                          # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
H45 = 1350
A = lambda p: os.path.join(ROOT, "assets", p)
SRC = lambda n: os.path.join(HERE, "src", n)
R = lambda p: os.path.join(ROOT, p)
LUMW = np.array([0.2126, 0.7152, 0.0722], np.float32)
CREAM, INK, AMBER, AMBER_D, MUTED_D = (246, 239, 228), (58, 38, 24), (232, 162, 74), (176, 104, 40), (200, 190, 178)
PILL = (240, 214, 178)

M6 = dict(path=R("aurora-reels/audio/music6-corners.mp3"), beat=0.8357, b0=0.396)
M1 = dict(path=R("aurora-reels/audio/music1-aesthetic.mp3"), beat=0.8823, b0=0.0)


def font(name, size):
    return ImageFont.truetype(A(name), size)


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# A shot: source, source fps, in-point, frame-x (0..1, for landscape sources), straighten, light-on (s into the shot or
# None), 4:5 crop centre (0..1 of the 9:16 height).  An edit: list of (shot, cut-at-beat) and the text events.
def S(src, fps, t_in, xf=0.5, straight=False, light=None, y45=0.5, t_src=None):
    return dict(src=src, fps=fps, t_in=t_in, xf=xf, straight=straight, light=light, y45=y45, t_src=t_src)


PLANKS = S(SRC("FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4"), 30, 0.0, y45=0.5)
BARS = S(SRC("IMG_7984.mov"), 30, 0.40, xf=0.45, y45=0.5)
BLACK = S(SRC("IMG_7990.mov"), 30, 0.50, y45=0.5)
TEST = S(SRC("IMG_7991.mov"), 30, 0.20, y45=0.5)
WALL = S(SRC("aurora-dimming-9x16.mp4"), 30, 0.0, y45=0.36, t_src=3.85)          # logo appears at 3.9 s: never reached
HAND = S(R("floor-reels/src/nx06-7921.mp4"), 30, 0.0, y45=0.55)
STEM = S(R("floor-reels/src/nx06-7921.mp4"), 30, 3.0, y45=0.5)
BUNDLE = S(R("floor-reels/src/nx03-7926.mp4"), 30, 0.0, y45=0.55)
BENCH = S(R("floor-reels/src/nx04-7930.mp4"), 30, 0.5, straight=True, light=0.12, y45=0.45, t_src=2.9)
BENCH2 = S(SRC("NW-RAW-20261011-unknown-ea1e0467.mov"), 30, 1.0, straight=True, y45=0.45, t_src=2.4)
LITHAND = S(R("floor-reels/src/nx06-7921.mp4"), 30, 7.9, straight=True, y45=0.55, t_src=1.7)
CUBE = S(SRC("NW-RAW-20261011-unknown-2e5660bf.mov"), 30, 0.0, y45=0.55, t_src=2.7)
TOUCH = S(R("rubik-reels/src/14-1.mp4"), 25, 12.20, y45=0.62, t_src=1.75)
WARM = S(R("rubik-reels/src/14-1.mp4"), 25, 5.70, y45=0.5)            # red mode ends at 5.5 s; warm, then warm white
CUBE2 = S(SRC("NW-RAW-20261011-unknown-92973dce.mov"), 30, 0.05, y45=0.55, t_src=1.9)
WHITE = S(R("rubik-reels/src/14-1.mp4"), 25, 9.30, y45=0.55, t_src=2.6)

PRODUCTS = {
    "aurora": dict(
        handle="nixwoods-aurora-linear-wall-light", slug="made-the-slow-way", music=M6,
        name="Aurora wall light", pre="from ", price="₹1,999", chips=["Solid teak", "COD"], card_y=890, card_y45=930,
        hook=["A new thing", "for the house."], line2=[("Made the ", False), ("slow", True), (" way.", False)],
        end_head="Made the slow way.",
        cuts={10: [(PLANKS, 0), (BARS, 3), (TEST, 5), (WALL, 6), (None, 12)],
              15: [(PLANKS, 0), (BARS, 3), (BLACK, 5), (TEST, 6), (WALL, 7), ("END", 15), (None, 18)]},
        light_click={10: [WALL, 0.40], 15: [WALL, 0.40]}),
    "nixline": dict(
        handle="nix-line-solid-wood-floor-lamp", slug="made-to-keep", music=M6,
        name="NixLine floor lamp", pre="", price="₹999", chips=["Solid teak", "COD"], card_y=890, card_y45=930,
        hook=["Solid teak."], line2=[("Made to ", False), ("keep", True), (".", False)],
        end_head="Solid teak. Made to keep.",
        cuts={10: [(HAND, 0), (STEM, 3), (BENCH, 5), (BENCH2, 8), (None, 12)],
              15: [(HAND, 0), (BUNDLE, 3), (STEM, 5), (BENCH, 6), (BENCH2, 9), (LITHAND, 12), ("END", 15), (None, 18)]}),
    "rubiks": dict(
        handle="rubiks-cube-table-lamp-sheesham-wood", slug="bhai-dooj-keeps", music=M1,
        name="Rubik's Cube lamp", pre="from ", price="₹2,999", chips=["Sheesham wood", "COD"], card_y=250, card_y45=70,
        hook=["What a brother gives", "on Bhai Dooj:"], line2=[("something she ", False), ("keeps", True), (".", False)],
        end_head="Something she keeps.",
        cuts={10: [(CUBE, 0), (TOUCH, 4), (WARM, 6), (None, 11.33)],
              15: [(CUBE, 0), (TOUCH, 4), (WARM, 6), (CUBE2, 10), (WHITE, 12), ("END", 14), (None, 17)]}),
}


# ----------------------------------------------------------------------------------------------- footage
def src_dims(path):
    """display size after rotation"""
    import io
    png = subprocess.run([FF, "-v", "error", "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True).stdout
    return Image.open(io.BytesIO(png)).size


def shot_frames(sh, secs):
    """frames (uint8, 1080x1920) for `secs` of output, slowed to fit when the shot has a fixed source length"""
    n = round(secs * FPS)
    speed = 1.0 if sh["t_src"] is None else min(1.0, sh["t_src"] / secs)
    need = int(np.ceil(secs * speed * sh["fps"])) + 2
    sw, shh = src_dims(sh["src"])
    if sw / shh > W / H:                                                 # landscape: cover the height, pick the x
        nw = round(sw * H / shh / 2) * 2
        vf = f"fps={sh['fps']},scale={nw}:{H}:flags=lanczos,crop={W}:{H}:{round((nw - W) * sh['xf'])}:0"
    else:
        nh = round(shh * W / sw / 2) * 2
        vf = f"fps={sh['fps']},scale={W}:{nh}:flags=lanczos,crop={W}:{H}:0:{(nh - H) // 2}"
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{sh['t_in']:.3f}", "-i", sh["src"], "-frames:v", str(need),
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    idx = [min(int(k / FPS * speed * sh["fps"]), len(fr) - 1) for k in range(n)]
    out = [fr[i] for i in idx]
    if sh["straight"]:                                                   # never show the lamp leaning
        angs = {i: axis(Image.fromarray(fr[i]))[1] for i in sorted(set(idx))}
        ks = sorted(angs)
        sm = np.convolve(np.pad([angs[i] for i in ks], 7, mode="edge"), np.ones(15) / 15, "valid")
        angs = dict(zip(ks, sm))
        res = []
        for k in range(n):
            im = Image.fromarray(fr[idx[k]])
            th = np.radians(abs(angs[idx[k]]))
            zc = np.cos(th) + (H / W) * np.sin(th)
            im = im.rotate(-angs[idx[k]], resample=Image.BICUBIC)
            cw, ch = W / zc, H / zc
            im = im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
            res.append(np.asarray(im))
        out = res
    return out


def grade_shot(frames, light=None, keep=0.35, target=0.31):
    """MOTION.md montage grade (keep 35 % of the source colour, the rest one warm tint, the shot at mean luma 0.31),
    after an optional switch-on (only the lit areas start dimmed and warm up over 0.3 s). uint8 in, uint8 out."""
    tint = np.array([1.30, 1.0, 0.66], np.float32)
    tint /= tint @ LUMW
    mid = frames[len(frames) // 2].astype(np.float32) / 255
    L = mid @ LUMW
    toned = np.clip(keep * mid + (1 - keep) * L[..., None] * tint, 1e-4, 1)
    lo, hi = 0.3, 3.0
    for _ in range(30):
        g = (lo + hi) / 2
        if np.mean(toned ** g @ LUMW) > target:
            lo = g
        else:
            hi = g
    if light is not None:
        L0 = frames[0].astype(np.float32) @ LUMW / 255
        a, b = np.percentile(L0, 60), np.percentile(L0, 99.7)
        w = np.clip((L0 - a) / max(b - a, 1e-3), 0, 1) ** 0.8
        w = np.asarray(Image.fromarray((w * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18)),
                       np.float32)[..., None] / 255
    cream = np.array([1.0, 0.933, 0.824], np.float32)
    out = []
    for k, f in enumerate(frames):
        x = f.astype(np.float32) / 255
        if light is not None:
            x = x * (1 - 0.88 * (1 - sstep((k / FPS - light) / 0.30)) * w)
        L = x @ LUMW
        t = np.clip(keep * x + (1 - keep) * L[..., None] * tint, 0, 1) ** g
        core = np.clip((L - 0.88) / 0.1, 0, 1)[..., None]               # a lit channel keeps a cream core
        t = t * (1 - core) + cream * core
        out.append((np.clip(t, 0, 1) * 255 + 0.5).astype(np.uint8))
    return out


# ----------------------------------------------------------------------------------------------- type
def tracked(d, xy, text, f, fill, track=-0.02):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + track * f.size
    return x


def tw(text, f, track=-0.02):
    return sum(f.getlength(ch) + track * f.size for ch in text)


def head_layer(lines, size, x, y, canvas_h, center=False):
    """Fraunces 600 cream, one amber italic accent; lines are lists of (text, accent)"""
    lay = Image.new("RGBA", (W, canvas_h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fh, fi = font("Fraunces-600.ttf", size), font("Fraunces-500-i.ttf", size)
    yy = y
    for parts in lines:
        lw = sum(tw(t, fi if a else fh) for t, a in parts)
        xx = (W - lw) / 2 if center else x
        for t, a in parts:
            xx = tracked(d, (xx, yy), t, fi if a else fh, AMBER if a else CREAM)
        yy += size * 1.05
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.5)))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (3, 6))
    out.alpha_composite(lay)
    return out


def chips_draw(d, x, y, chips, size, fill, stroke, ink):
    f = font("Inter-600.ttf", size)
    for c in chips:
        w = f.getlength(c) + 2 * 18
        d.rounded_rectangle((x, y, x + w, y + size + 22), (size + 22) // 2, fill=fill, outline=stroke, width=2)
        d.text((x + 18, y + 9), c, font=f, fill=ink)
        x += w + 12
    return x


def card_layer(p, y, canvas_h):
    """the price card: rounded cream at 236/255, product, price in dark amber, chips, URL"""
    f1, fp, fs, fu = font("Inter-600.ttf", 40), font("Inter-600.ttf", 112), font("Inter-600.ttf", 44), \
        font("Inter-600.ttf", 36)
    pad = 32
    chip_w = sum(font("Inter-600.ttf", 30).getlength(c) + 48 for c in p["chips"])
    w = int(max(f1.getlength(p["name"]), fs.getlength(p["pre"]) + fp.getlength(p["price"]), chip_w,
                fu.getlength("nixwoods.com")) + 2 * pad)
    h = 40 + 10 + 120 + 18 + 52 + 16 + 36 + 2 * pad
    x = 70
    lay = Image.new("RGBA", (W, canvas_h), (0, 0, 0, 0))
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x + 4, y + 8, x + w + 4, y + h + 8), 28, fill=(20, 12, 6, 110))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((x, y, x + w, y + h), 28, fill=(*CREAM, 236))
    yy = y + pad - 6
    d.text((x + pad, yy), p["name"], font=f1, fill=INK)
    yy += 50
    xx = x + pad
    if p["pre"]:
        d.text((xx, yy + 58), p["pre"], font=fs, fill=AMBER_D)
        xx += fs.getlength(p["pre"])
    d.text((xx, yy - 8), p["price"], font=fp, fill=AMBER_D)
    yy += 138
    chips_draw(d, x + pad, yy, p["chips"], 30, PILL, INK, INK)
    yy += 68
    d.text((x + pad, yy), "nixwoods.com", font=fu, fill=AMBER_D)
    return lay, (x, y, x + w, y + h)


def end_layers(p, canvas_h):
    """Dusk end card: teak ground, vignette, grain; logo, line, price in amber, chips, URL"""
    yy, xx = np.mgrid[0:canvas_h, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - canvas_h / 2) / (canvas_h / 2)) ** 2) / np.sqrt(2)
    ground = np.ones((canvas_h, W, 3), np.float32) * (np.array([46, 30, 20], np.float32) / 255 + 0.02)
    ground *= np.clip(1.08 - 0.35 * r, 0, 1.2)[..., None]
    ground += np.random.default_rng(5).normal(0, 2.2 / 255, ground.shape).astype(np.float32)
    lay = Image.new("RGBA", (W, canvas_h), (0, 0, 0, 0))
    logo = Image.open(A("logo.png")).convert("RGBA")
    lw = 440 if canvas_h == H else 360
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    tint = Image.new("RGBA", logo.size, (*CREAM, 255))
    tint.putalpha(logo.split()[3])
    top = 430 if canvas_h == H else 120
    lay.alpha_composite(tint, ((W - lw) // 2, top))
    y = top + logo.height + 90
    lay.alpha_composite(head_layer([[(p["end_head"], False)]], 72 if canvas_h == H else 64, 0, y, canvas_h,
                                   center=True))
    d = ImageDraw.Draw(lay)
    y += 130
    fp, fs = font("Inter-600.ttf", 112), font("Inter-600.ttf", 44)
    tot = fs.getlength(p["pre"]) + fp.getlength(p["price"])
    x = (W - tot) / 2
    if p["pre"]:
        d.text((x, y + 58), p["pre"], font=fs, fill=AMBER)
        x += fs.getlength(p["pre"])
    d.text((x, y - 8), p["price"], font=fp, fill=AMBER)
    y += 150
    cw = sum(font("Inter-600.ttf", 30).getlength(c) + 48 for c in p["chips"])
    chips_draw(d, (W - cw) / 2, y, p["chips"], 30, None, CREAM, CREAM)
    y += 90
    fu = font("Inter-600.ttf", 46)
    d.text(((W - fu.getlength("nixwoods.com")) / 2, y), "nixwoods.com", font=fu, fill=AMBER)
    return ground, lay


def scrim(canvas_h, h=620, a=0.55):
    y = np.arange(canvas_h, dtype=np.float32)
    s = np.clip(1 - y / h, 0, 1)
    return (a * s * s * (3 - 2 * s))[:, None, None]


def over(f, lay, op):
    arr = np.asarray(lay, np.float32) / 255
    al = arr[..., 3:4] * op
    return f * (1 - al) + arr[..., :3] * al


# ----------------------------------------------------------------------------------------------- one cut
def build(key, length, frames_at=None):
    p = PRODUCTS[key]
    mu = p["music"]
    edit = p["cuts"][length]
    dur = min(edit[-1][1] * mu["beat"], length + 0.05)
    cut = lambda b: 0.0 if b == 0 else min(dur, mu["b0"] + b * mu["beat"])
    segs = [(sh, cut(b), cut(b2) if k < len(edit) - 2 else dur) for k, ((sh, b), (_, b2)) in enumerate(zip(edit, edit[1:]))]
    print(f"{key} {length}s: {dur:.2f} s; cuts " + ", ".join(f"{a:.2f}" for _, a, _ in segs), flush=True)
    frames, y45s, lights = [], [], []
    for sh, a, b in segs:
        n = round(b * FPS) - round(a * FPS)
        if sh == "END":
            frames += [None] * n
            y45s += [None] * n
            continue
        fr = grade_shot(shot_frames(sh, n / FPS), sh["light"])
        if sh["light"] is not None:
            lights.append(a + sh["light"])
        frames += fr
        y45s += [sh["y45"]] * n
        if key in ("aurora",) and sh is WALL:
            lights.append(a + 0.40 / (min(1.0, sh["t_src"] / (b - a))))
    # text timing
    first_cut = segs[1][1]
    pay = next(a for sh, a, b in segs if sh in (WALL, BENCH, WARM))
    price_at = pay + (0.85 if key == "aurora" else 0.6)
    end_at = next((a for sh, a, b in segs if sh == "END"), None)
    out = {}

    def make(ratio, ch):
        hook = head_layer([[(t, False)] for t in p["hook"]], 84 if key == "rubiks" else 92, 70,
                          262 if ch == H else 70, ch)
        line2 = head_layer([p["line2"]], 84 if key == "rubiks" else 92, 70, 262 if ch == H else 70, ch)
        card, box = card_layer(p, p["card_y"] if ch == H else p["card_y45"], ch)
        ground, endlay = end_layers(p, ch)
        END = over(ground, endlay, 1.0)
        sc = scrim(ch)

        def frame(k):
            t = k / FPS
            f = frames[k]
            if f is None:
                return END
            f = f.astype(np.float32) / 255
            if ch == H45:
                c = int(np.clip(y45s[k] * H - H45 / 2, 0, H - H45))
                f = f[c:c + H45]
            ha = sstep((t - 0.05) / 0.12) * (1 - sstep((t - first_cut + 0.1) / 0.2))
            la = sstep((t - first_cut) / 0.25) * (1 - sstep((t - price_at + 0.35) / 0.25))
            if key == "rubiks":
                la = sstep((t - first_cut) / 0.25) * (1 - sstep((t - price_at + 0.3) / 0.25))
            sa = max(ha, la)
            if sa > 0:
                f = f * (1 - sc * sa)
            if ha > 0:
                f = over(f, hook, ha)
            if la > 0:
                f = over(f, line2, la)
            ca = sstep((t - price_at) / 0.25)
            if ca > 0:
                f = over(f, card, ca)
            if end_at is not None and t >= end_at - 0.3:                 # the end card fades in over 0.3 s
                ea = sstep((t - end_at + 0.3) / 0.3)
                f = f * (1 - ea) + END * ea
            return f

        return frame

    for ratio, ch in (("9x16", H), ("4x5", H45)):
        out[ratio] = make(ratio, ch)
    return dur, frames, out, lights, price_at


def audio(mu, dur, lights, path):
    sr = 48000
    raw = subprocess.run([FF, "-v", "error", "-i", mu["path"], "-t", f"{dur:.3f}", "-ac", "2", "-ar", str(sr), "-f",
                          "f32le", "-"], capture_output=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(dur * sr)
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    m *= np.clip((dur - np.arange(n) / sr) / 0.8, 0, 1)[:, None]
    m /= np.abs(m).max() + 1e-9
    m *= 0.62
    rng = np.random.default_rng(4)
    for t in lights:                                                     # a 0.06 s switch click
        L = int(0.06 * sr)
        tt = np.arange(L) / sr
        c = rng.normal(0, 1, L) * np.exp(-tt / 0.006)
        c[:40] += np.linspace(1, 0, 40)
        i = int(t * sr)
        j = min(n, i + L)
        if i < n:
            m[i:j] += (c[:j - i] * 0.2)[:, None]
    m *= 0.65 / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="aurora | nixline | rubiks")
    ap.add_argument("--length", type=int, help="10 or 15")
    ap.add_argument("--frames", help="comma-separated times: write JPEG stills (both ratios) instead of video")
    a = ap.parse_args()
    outdir = os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    for key in ([a.only] if a.only else list(PRODUCTS)):
        p = PRODUCTS[key]
        for length in ([a.length] if a.length else [10, 15]):
            dur, frames, fns, lights, price_at = build(key, length)
            print(f"  price on screen at {price_at:.2f} s", flush=True)
            base = f"NW-CREATIVE-VID-20261012-{p['handle']}-festive-{p['slug']}-{length}s"
            for ratio, fn in fns.items():
                ch = H if ratio == "9x16" else H45
                if a.frames:
                    for ts in [float(v) for v in a.frames.split(",")]:
                        k = min(len(frames) - 1, round(ts * FPS))
                        Image.fromarray((np.clip(fn(k), 0, 1) * 255).astype(np.uint8)).save(
                            os.path.join(outdir, f"still-{key}-{length}-{ratio}-{ts:05.2f}.jpg"), quality=88)
                    continue
                tv, ta = os.path.join(outdir, "_v.mp4"), os.path.join(outdir, "_a.wav")
                pr = subprocess.Popen([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{ch}",
                                       "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17",
                                       "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                                       "-color_trc", "bt709", tv], stdin=subprocess.PIPE)
                for k in range(len(frames)):
                    pr.stdin.write((np.clip(fn(k), 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
                pr.stdin.close()
                pr.wait()
                audio(p["music"], len(frames) / FPS, lights, ta)
                out = os.path.join(outdir, f"{base}-{ratio}-v1.mp4")
                subprocess.run([FF, "-y", "-v", "error", "-i", tv, "-i", ta, "-c:v", "copy", "-c:a", "aac", "-b:a",
                                "192k", "-shortest", "-movflags", "+faststart", out], check=True)
                os.remove(tv)
                os.remove(ta)
                print("  wrote", os.path.basename(out), flush=True)


if __name__ == "__main__":
    main()
