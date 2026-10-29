#!/usr/bin/env python3
"""Circular Hole Wall Light over a painting: an organic reel and a Meta ad cut (owner, 29 Oct 2026, 10 phone clips).

The owner's clips show the light hung above a framed painting of a figure on a golden boat in sunset clouds, so the
light reads as a picture light. Both cuts are built on that: open on the art, look up, find the light.

  social  9:16, 10.0 s  hook "Everyone looks at the painting." -> "Until they look up." -> the wood-grain macro ->
                        the save line "Styling tip: hang it above your art." -> end card (name, facts, nixwoods.com)
  ad      9:16 + 4:5, 10.0 s  the light over the art with the price from frame 1 -> the macro -> the facts ->
                        end card with the price, the FLY100 prepaid saving and nixwoods.com

Facts are the live page on 29 Oct (handle 24-inch-circular-hole-wooden-wall-light, now titled 30-Inch): 30 in,
₹3,999 (no compare-at), real wood with natural grain, integrated 20 W warm LED, hardwired, 3-year wood warranty,
"Save ₹100 prepaid with FLY100". Not claimed: solid wood (only the title says it), a species, dimmable.
Real footage only, so no AI label. Look and type from MOTION.md; cuts on the music6 grid.

    python3 brand-reels/art-light/art_light.py                 # all three
    python3 brand-reels/art-light/art_light.py --only social --frames 0.3,3.5,6,8.5
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(HERE, "out")
FF = "/usr/bin/ffmpeg"                 # system ffmpeg: it has zscale for the HLG tone-map
W, FPS, SR = 1080, 30, 48000
A = lambda p: os.path.join(ROOT, "assets", p)
SRC = lambda n: os.path.join(HERE, "src", n)
CREAM, INK, AMBER, AMBER_D, MUTED_D, GROUND = (246, 239, 228), (58, 38, 24), (232, 162, 74), (176, 104, 40), \
    (200, 190, 178), (46, 30, 20)
LINE = (255, 238, 210)
TM = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")
MUSIC = os.path.join(ROOT, "aurora-reels", "audio", "music6-corners.mp3")
BEAT, B0 = 0.8357, 0.396
G = lambda k: round(B0 + k * BEAT, 3)  # beat k on the music6 grid
DUR = 10.0
DATE = "20261029"
HANDLE = "24-inch-circular-hole-wooden-wall-light"


def font(name, size):
    return ImageFont.truetype(A(name), size)


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# A shot: clip, source in-point, playback speed, 4:5 crop top (px of the 1920 frame).
# zoom: a fixed scale anchored at the bottom edge, lifting the subject up the frame.
def S(clip, t_in, speed=1.0, y45=285, zoom=1.0):
    return dict(clip=clip, t_in=t_in, speed=speed, y45=y45, zoom=zoom)


TILT = S("IMG_8115.mov", 0.0)                       # painting -> tilt up -> the light settles above the frame
OVER = S("IMG_8115.mov", 1.30, 0.80, y45=60)       # the light already in frame, settling over the painting
GRAIN = S("IMG_8118.mov", 0.90, y45=285, zoom=1.25)  # macro: wood grain and the row of lit holes, lifted to y ~900
DOWN = S("IMG_8116.mov", 0.0, 0.93, y45=150)       # the light, then a tilt down onto the painting

CUTS = {
    "social": [(TILT, 0.0, G(3)), (GRAIN, G(3), G(6)), (DOWN, G(6), G(8)), ("end", G(8), DUR)],
    "ad": [(OVER, 0.0, G(2)), (GRAIN, G(2), G(5)), (DOWN, G(5), G(8)), ("end", G(8), DUR)],
}


_cache = {}


def clip_frames(clip, t_in, secs, fps=FPS):
    key = (clip, t_in, secs, fps)
    if key not in _cache:
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", SRC(clip), "-t", f"{secs + 0.1:.3f}",
                              "-vf", f"{TM},fps={fps},scale={W}:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        _cache[key] = np.frombuffer(raw, np.uint8).reshape(-1, 1920, W, 3)
    return _cache[key]


def grade(fr):
    """MOTION.md photo grade, plus the lit holes and their spill pulled to the cream line core, so the light reads
    warm as the page states (the iPhone's tone-map renders the LEDs pinkish white)."""
    a = fr.astype(np.float32) / 255.0
    a = a * np.array([1.08, 1.02, 0.84], np.float32)          # photo grade, a touch warmer: the bar reads mauve
    a = np.clip(a, 0, 1) ** (1 / 1.04)
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    w = np.clip((lum - 0.72) / 0.22, 0, 1) * 0.75
    a = a * (1 - w) + np.array(LINE, np.float32) / 255.0 * w
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)


def shot_frame(sh, t, secs):
    fr = clip_frames(sh["clip"], sh["t_in"], secs * sh["speed"] + 0.2)
    k = min(int(round(t * sh["speed"] * FPS)), len(fr) - 1)
    return fr[k]


def scrim(img, top, bottom, strength=0.62):
    """A dark teak gradient over the band [top, bottom] in 0..1 of the height, full at the bottom edge."""
    h = img.height
    yy = np.linspace(0, 1, h)[:, None]
    a = np.clip((yy - top) / max(1e-3, bottom - top), 0, 1) * strength
    arr = np.asarray(img, np.float32)
    arr = arr * (1 - a[..., None]) + np.array(GROUND, np.float32) * a[..., None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def text(d, xy, s, f, fill, anchor="mm"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def alpha(c, a):
    return c + (int(255 * a),)


def layer(img, draw_fn):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(lay))
    img.paste(lay, (0, 0), lay)
    return img


def price_chip(d, cx, cy, a, size=64):
    f = font("Inter-600.ttf", size)
    tw = f.getlength("₹3,999")
    pw, ph = tw + 64, size + 44
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), 26, fill=alpha(CREAM, a * 236 / 255))
    text(d, (cx, cy + 2), "₹3,999", f, alpha(AMBER_D, a))


def fact_chips(d, cx, cy, items, a, size=34):
    f = font("Inter-600.ttf", size)
    widths = [f.getlength(s) + 52 for s in items]
    gap = 18
    x = cx - (sum(widths) + gap * (len(items) - 1)) / 2
    for s, w in zip(items, widths):
        d.rounded_rectangle((x, cy - 34, x + w, cy + 34), 34, outline=alpha(CREAM, a * 0.85), width=3)
        text(d, (x + w / 2, cy + 1), s, f, alpha(CREAM, a))
        x += w + gap


def footage(sh, t, secs, h, push=0.05):
    fr = grade(shot_frame(sh, t, secs))
    im = Image.fromarray(fr)
    if sh["zoom"] != 1.0:
        z = sh["zoom"]
        im = im.resize((round(W * z), round(1920 * z)), Image.LANCZOS)
        x = (im.width - W) // 2
        im = im.crop((x, im.height - 1920, x + W, im.height))
    s = 1 + push * sstep(t / secs)
    if s > 1.0001:
        im2 = im.resize((round(W * s), round(1920 * s)), Image.LANCZOS)
        x, y = (im2.width - W) // 2, (im2.height - 1920) // 2
        im = im2.crop((x, y, x + W, y + 1920))
    if h != 1920:
        im = im.crop((0, sh["y45"], W, sh["y45"] + h))
    return im


# ---- the organic cut ----------------------------------------------------------------------------------------------
def social(t, h):
    for sh, a, b in CUTS["social"]:
        if a <= t < b:
            break
    lt, secs = t - a, b - a
    if sh == "end":
        return end_card(lt, h, ad=False)
    im = footage(sh, lt, secs, h)
    if sh is TILT:
        im = scrim(im, 0.52, 0.86 if lt > 1.3 else 0.92, 0.62 if lt > 1.3 else 0.7)
        a1 = sstep((lt - 0.05) / 0.12) * (1 - sstep((lt - 1.25) / 0.2))
        a2 = sstep((lt - 1.5) / 0.28)
        hf = font("Fraunces-600.ttf", 88)
        it = font("Fraunces-500-i.ttf", 88)

        def dr(d):
            text(d, (W / 2, 1404), "Everyone looks", hf, alpha(CREAM, a1))      # under the boat, not over it
            text(d, (W / 2, 1494), "at the painting.", hf, alpha(CREAM, a1))
            text(d, (W / 2, 1270), "Until they", hf, alpha(CREAM, a2))
            text(d, (W / 2, 1366), "look up.", it, alpha(AMBER, a2))
        return layer(im, dr)
    if sh is GRAIN:
        im = scrim(im, 0.52, 0.86, 0.76)                                # the wall under the light is bright
        a1 = sstep((lt - 0.2) / 0.28)

        def dr(d):
            text(d, (W / 2, 1290), "Real wood.", font("Fraunces-600.ttf", 88), alpha(CREAM, a1))
            text(d, (W / 2, 1392), "Warm light through every hole.", font("Inter-400.ttf", 44), alpha(CREAM, a1))
        return layer(im, dr)
    if sh is DOWN:
        im = scrim(im, 0.50, 0.86)
        a0 = sstep((lt - 0.1) / 0.25)
        a1 = sstep((lt - 0.2) / 0.28)

        def dr(d):
            text(d, (W / 2, 1180), "SAVE THIS STYLING TIP", font("Inter-600.ttf", 32), alpha(AMBER, a0))
            text(d, (W / 2, 1272), "Hang it above your art.", font("Fraunces-600.ttf", 80), alpha(CREAM, a1))
            text(d, (W / 2, 1362), "The glow becomes the frame.", font("Fraunces-500-i.ttf", 64), alpha(CREAM, a1))
        return layer(im, dr)


# ---- the ad cut ----------------------------------------------------------------------------------------------------
def ad(t, h):
    for sh, a, b in CUTS["ad"]:
        if a <= t < b:
            break
    lt, secs = t - a, b - a
    if sh == "end":
        return end_card(lt, h, ad=True)
    im = footage(sh, lt, secs, h)
    sq = h != 1920
    # paid 9:16 keeps text above y 1250 (Meta's CTA bar); 4:5 keeps it inside the frame's lower third
    by = 1150 if not sq else 1060
    if sh is OVER:
        im = scrim(im, 0.36, 0.78 if not sq else 0.95, 0.74)
        a1 = sstep((t - 0.05) / 0.12)
        oy = by - 50 if not sq else by                                   # the chip's foot stays above y 1250

        def dr(d):
            hf = font("Fraunces-600.ttf", 86 if not sq else 78)
            text(d, (W / 2, oy - 150), "Light that frames", hf, alpha(CREAM, a1))
            text(d, (W / 2, oy - 58), "your art.", font("Fraunces-500-i.ttf", 86 if not sq else 78), alpha(AMBER, a1))
            price_chip(d, W / 2, oy + 70, a1)
        return layer(im, dr)
    if sh is GRAIN:
        im = scrim(im, 0.40, 0.80 if not sq else 0.95, 0.76)
        a1 = sstep((lt - 0.15) / 0.28)

        def dr(d):
            text(d, (W / 2, by - 40), "Real wood.", font("Fraunces-600.ttf", 86 if not sq else 78), alpha(CREAM, a1))
            text(d, (W / 2, by + 56), "Warm light through every hole.", font("Inter-400.ttf", 44 if not sq else 40),
                 alpha(CREAM, a1))
        return layer(im, dr)
    if sh is DOWN:
        im = scrim(im, 0.45, 0.85 if not sq else 0.98)
        a1 = sstep((lt - 0.15) / 0.28)
        a2 = sstep((lt - 0.45) / 0.28)

        def dr(d):
            text(d, (W / 2, by - 70), "30 inches of glow", font("Fraunces-600.ttf", 80 if not sq else 74),
                 alpha(CREAM, a1))
            fact_chips(d, W / 2, by + 50, ["20 W warm LED", "3-yr wood warranty"], a2, 34 if not sq else 30)
        return layer(im, dr)


# ---- end card: the light over the painting, held, dimmed, with the name ------------------------------------------
_end_bg = {}


def end_card(lt, h, ad):
    sq = h != 1920
    key = (h, ad)
    if key not in _end_bg:
        fr = grade(clip_frames(TILT["clip"], 2.75, 0.3)[3])
        im = Image.fromarray(fr)
        if sq:
            im = im.crop((0, 60, W, 60 + h))
        elif ad:                                                        # paid 9:16: lift the light so the whole
            im = im.resize((round(W * 1.18), round(1920 * 1.18)), Image.LANCZOS)   # block ends above y 1250
            x = (im.width - W) // 2
            im = im.crop((x, 310, x + W, 310 + 1920))
        _end_bg[key] = im
    base = _end_bg[key]
    s = 1 + 0.04 * sstep(lt / 3.0)
    im = base.resize((round(W * s), round(h * s)), Image.LANCZOS)
    x, y = (im.width - W) // 2, 0                                       # anchored at the top: the light stays whole
    im = im.crop((x, y, x + W, y + h))
    a0 = sstep(lt / 0.3)
    im = scrim(im, 0.30 if h == 1920 else 0.25, 0.70 if h == 1920 else 0.75, 0.86)   # dim from the cut: no flash
    y0 = (720 if ad else 980) if not sq else 830                                        # 4:5: below the light and the frame top
    lg = Image.open(A("logo.png")).convert("RGBA")
    lw = 360 if not sq else 300
    lg = lg.resize((lw, round(lw * lg.height / lg.width)), Image.LANCZOS)
    ink = Image.new("RGBA", lg.size, CREAM + (255,))
    ink.putalpha(lg.getchannel("A").point(lambda v: int(v * a0)))
    a1 = sstep((lt - 0.15) / 0.3)
    a2 = sstep((lt - 0.35) / 0.3)

    def dr(d):
        text(d, (W / 2, y0), "Circular Hole", font("Fraunces-600.ttf", 88 if not sq else 78), alpha(CREAM, a1))
        text(d, (W / 2, y0 + 96), "Wall Light", font("Fraunces-600.ttf", 88 if not sq else 78), alpha(CREAM, a1))
        if ad:
            text(d, (W / 2, y0 + 228), "₹3,999", font("Inter-600.ttf", 112 if not sq else 96), alpha(AMBER, a1))
            text(d, (W / 2, y0 + 330), "Save ₹100 prepaid with FLY100", font("Inter-400.ttf", 40 if not sq else 36),
                 alpha(MUTED_D, a2))
            text(d, (W / 2, y0 + 410), "Shop at nixwoods.com", font("Inter-600.ttf", 46 if not sq else 42),
                 alpha(CREAM, a2))
        else:
            text(d, (W / 2, y0 + 200), "30 in · real wood · warm LED", font("Inter-400.ttf", 42), alpha(MUTED_D, a2))
            text(d, (W / 2, y0 + 290), "nixwoods.com", font("Inter-600.ttf", 46), alpha(AMBER, a2))
    im = layer(im, dr)
    if not ad and not sq:                                               # the ads close on "Shop at nixwoods.com"
        im.paste(ink, ((W - lg.width) // 2, y0 + 400), ink)
    return im


# ---- audio and encode ----------------------------------------------------------------------------------------------
def music_wav(path):
    n = int(DUR * SR)
    raw = subprocess.run([FF, "-v", "error", "-i", MUSIC, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le",
                          "-"], capture_output=True, check=True).stdout
    m = np.zeros((n, 2), np.float32)
    a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
    m[:len(a)] = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 10 ** (-18 / 20)
    t = np.arange(n) / SR
    m *= (np.clip(t / 0.3, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1))[:, None]
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def grain(img, rng):
    a = np.asarray(img, np.float32) + rng.normal(0, 2.2, (img.height, img.width, 1))
    return a.clip(0, 255).astype(np.uint8)


def render(cut, h, path):
    render_with(social if cut == "social" else ad, h, path)


def render_with(fn, h, path):
    """fn(t, h) -> PIL image; writes the mp4 with the music bed (v2 renders through this too)"""
    rng = np.random.default_rng(29)
    wavp = path + ".wav"
    music_wav(wavp)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{h}", "-r",
                            str(FPS), "-i", "-", "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf",
                            "17", "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc",
                            "bt709", "-colorspace", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "192k",
                            "-shortest", "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for i in range(round(DUR * FPS)):
        enc.stdin.write(grain(fn(i / FPS, h), rng).tobytes())
    enc.stdin.close()
    enc.wait()
    os.remove(wavp)
    if enc.returncode:
        sys.exit(f"encode failed: {path}")


JOBS = {
    "social": ("social", 1920, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-art-light-reel-v1.mp4"),
    "ad916": ("ad", 1920, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-art-light-ad-9x16-v1.mp4"),
    "ad45": ("ad", 1350, f"NW-CREATIVE-VID-{DATE}-{HANDLE}-art-light-ad-4x5-v1.mp4"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=list(JOBS) + ["ad"], default=None)
    ap.add_argument("--frames", default=None, help="comma-separated seconds: write stills instead of rendering")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    keys = [k for k in JOBS if args.only in (None, k) or (args.only == "ad" and k.startswith("ad"))]
    os.makedirs(args.out, exist_ok=True)
    for k in keys:
        cut, h, name = JOBS[k]
        if args.frames:
            for s in args.frames.split(","):
                fn = social if cut == "social" else ad
                fn(float(s), h).save(os.path.join(args.out, f"{k}-{float(s):05.2f}.jpg"), quality=90)
            continue
        render(cut, h, os.path.join(args.out, name))
        print("wrote", name)


if __name__ == "__main__":
    main()
