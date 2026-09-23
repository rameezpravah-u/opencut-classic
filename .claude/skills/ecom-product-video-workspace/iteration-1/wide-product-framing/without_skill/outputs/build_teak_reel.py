#!/usr/bin/env python3
"""
Double Arm Teak Pendant - 9:16 product reel.

Built directly with PIL + imageio_ffmpeg (no paid APIs, no generation).

Framing principle
-----------------
The product is a 49 in (four-foot) LINEAR pendant and every source photo is
square (1:1). A 9:16 centre crop keeps only the middle 56.25% of the width,
which slices the ends off the bar in all six photos (measured - see NOTES.md).
So the product is NEVER cropped horizontally: each shot is a full-width,
vertically-cropped band of the source, laid on a colour-matched field built
from the photo's own blurred pixels. Motion is vertical-only parallax, so the
ends of the bar can never leave the frame.

Brand values (nixwoods-reel/system/presets.json, style "3040"):
  canvas 1080x1920 @ 25fps, cut grid 2.526 s, Playfair Display 600 / DM Sans 500,
  music5-3040.mp3, ivory #F4EADB text, accent #D9A05B, espresso #14110E card.
"""
import os, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageChops
import numpy as np
import imageio_ffmpeg

REEL = "/home/user/opencut-classic/nixwoods-reel"
HF   = f"{REEL}/teak-reels/hf"
FONT = f"{REEL}/assets"
MUSIC= f"{REEL}/teak-reels/audio/music5-3040.mp3"
LOGO = f"{REEL}/assets/logo.png"
OUT  = os.path.dirname(os.path.abspath(__file__))

W, H, FPS = 1080, 1920, 25
CUT      = 2.526          # measured beat grid of music5-3040.mp3
XFADE    = 0.30
BAND_W   = 1000           # product band width: full-bleed minus a 40px margin
BAND_CY  = 790            # every band shares one optical centre
IVORY    = (244, 234, 219)
ACCENT   = (217, 160, 91)
ESPRESSO = (20, 17, 14)

F_HEAD = ImageFont.truetype(f"{FONT}/Playfair_Display-600.ttf", 66)
F_HEAD_S = ImageFont.truetype(f"{FONT}/Playfair_Display-600.ttf", 58)
F_SUB  = ImageFont.truetype(f"{FONT}/DM_Sans-500.ttf", 38)
F_KICK = ImageFont.truetype(f"{FONT}/DM_Sans-500.ttf", 29)
F_PRICE= ImageFont.truetype(f"{FONT}/Playfair_Display-700.ttf", 104)
F_NAME = ImageFont.truetype(f"{FONT}/Playfair_Display-600.ttf", 60)
F_DIM  = ImageFont.truetype(f"{FONT}/DM_Sans-500.ttf", 36)

# ---------------------------------------------------------------- shot list
# crop = (y0, y1) as a fraction of the SQUARE source. Full width always kept.
SHOTS = [
    dict(key="s1", img="sh00-marble-dining.jpg", crop=(0.04, 0.92), dur=CUT,
         head=["Two lines of light.", "One piece of teak."], sub=None,
         bright=1.02, lightup=True),
    dict(key="s2", img="sh01-underside-twin.jpg", crop=(0.16, 0.98), dur=CUT,
         head=["Twin LED channels."], sub="warm 3000K, along the underside",
         bright=1.04),
    dict(key="s3", img="sh02-strip-fluted.jpg", crop=(0.10, 0.90), dur=CUT,
         head=["49 in, end to end."], sub="four feet of solid teak",
         bright=1.02, dimension=True),
    dict(key="s4", img="sh02-strip-fluted.jpg", crop=(0.10, 0.90), dur=CUT,
         head=["One bar. The whole table."], sub="lights the table, not your eyeline",
         bright=1.02, dimension_hold=True),
    dict(key="s5", img="sh04-end-channels.webp", crop=(0.02, 0.98), dur=CUT,
         head=["Handcrafted in India."], sub="solid teak · rounded end caps",
         bright=1.03, card_w=780),
    dict(key="s6", img="sh03-dark-two-lines.jpg", crop=(0.16, 0.99), dur=CUT,
         head=["Dimmable, by remote."], sub="3000K warm · 18W",
         bright=1.10, sat=1.04),
    dict(key="s7", img="sh05-canopy-cables.jpg", crop=(0.00, 0.86), dur=CUT,
         head=["One canopy. Two cables."], sub="solid teak, ceiling to bar",
         bright=1.03),
    dict(key="s8", img="sh00-marble-dining.jpg", crop=(0.04, 0.92), dur=CUT,
         head=None, sub=None, bright=0.55, endcard=True),
]

# ---------------------------------------------------------------- helpers
def load(name):
    return Image.open(f"{HF}/{name}").convert("RGB")

def vignette_mask():
    y, x = np.mgrid[0:H, 0:W]
    nx = (x - W / 2) / (W / 2); ny = (y - H / 2) / (H / 2)
    r = np.sqrt(nx * nx + ny * ny * 0.55)
    v = np.clip(1.0 - 0.30 * np.clip((r - 0.62) / 0.85, 0, 1) ** 1.6, 0, 1)
    return (v * 255).astype(np.uint8)
VIG = Image.fromarray(vignette_mask(), "L")

def make_backdrop(src):
    """Colour-matched full-bleed field from the photo's own pixels.
    Oversized so it can drift without exposing an edge."""
    bw, bh = W + 140, H + 200
    s = src.resize((bw, bw), Image.LANCZOS)          # square -> stretch to width
    s = s.crop((0, (bw - bh) // 2, bw, (bw - bh) // 2 + bh)) if bw > bh else s.resize((bw, bh), Image.LANCZOS)
    s = s.filter(ImageFilter.GaussianBlur(70))
    m = np.asarray(src).reshape(-1, 3).mean(0)
    warm = (min(255, m[0] * 0.78), min(255, m[1] * 0.68), min(255, m[2] * 0.58))
    tone = Image.new("RGB", (bw, bh), tuple(int(c) for c in warm))
    s = Image.blend(s, tone, 0.62)
    s = ImageEnhance.Brightness(s).enhance(0.66)
    # gentle top/bottom falloff so the field has depth instead of reading flat
    g = np.linspace(0, 1, bh)[:, None]
    fall = (1.0 - 0.34 * np.clip(np.abs(g - 0.44) * 2.0 - 0.25, 0, 1) ** 1.3)
    a = np.asarray(s).astype(float) * fall[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def make_band(src, crop, bright, sat, width):
    w, h = src.size
    y0, y1 = int(crop[0] * h), int(crop[1] * h)
    b = src.crop((0, y0, w, y1))
    bh = max(1, round(width * b.size[1] / b.size[0]))
    b = b.resize((width, bh), Image.LANCZOS)
    b = ImageEnhance.Brightness(b).enhance(bright)
    b = ImageEnhance.Color(b).enhance(sat)
    b = ImageEnhance.Contrast(b).enhance(1.05)
    return b

def warm_balance(im, k):
    a = np.asarray(im).astype(float) * np.array(k, dtype=float)[None, None, :]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def band_shadow(size):
    sw, sh = size[0] + 80, size[1] + 80
    m = Image.new("L", (sw, sh), 0)
    ImageDraw.Draw(m).rectangle([40, 44, sw - 40, sh - 36], fill=150)
    return m.filter(ImageFilter.GaussianBlur(26))

def text_layer(shot):
    """Precomposed RGBA caption block, drawn once per shot."""
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    if shot.get("endcard"):
        return L
    y = 1330
    if shot.get("head"):
        f = F_HEAD if max(len(s) for s in shot["head"]) <= 22 else F_HEAD_S
        for line in shot["head"]:
            tw = d.textlength(line, font=f)
            d.text((W / 2 - tw / 2, y), line, font=f, fill=IVORY + (255,),
                   stroke_width=0)
            y += f.size + 14
    if shot.get("sub"):
        y += 12
        tw = d.textlength(shot["sub"], font=F_SUB)
        d.text((W / 2 - tw / 2, y), shot["sub"], font=F_SUB, fill=ACCENT + (235,))
    # soft drop shadow so type holds on any plate
    sh = L.split()[3].filter(ImageFilter.GaussianBlur(14)).point(lambda p: int(p * 0.85))
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    base.paste(Image.new("RGBA", (W, H), (0, 0, 0, 255)), (0, 3), sh)
    base.alpha_composite(L)
    return base

def endcard_layer():
    L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rectangle([0, 0, W, H], fill=ESPRESSO + (205,))
    # logo
    try:
        lg = Image.open(LOGO).convert("RGBA")
        lw = 250; lh = round(lw * lg.size[1] / lg.size[0])
        lg = lg.resize((lw, lh), Image.LANCZOS)
        L.alpha_composite(lg, (W // 2 - lw // 2, 600 - lh))
    except Exception:
        pass
    def ctr(txt, font, yy, fill):
        tw = d.textlength(txt, font=font)
        d.text((W / 2 - tw / 2, yy), txt, font=font, fill=fill)
    ctr("Double Arm Teak Pendant", F_NAME, 680, IVORY + (255,))
    ctr("solid teak  ·  49 in  ·  3000K  ·  dimmable", F_KICK, 780, ACCENT + (230,))
    d.line([(W / 2 - 90, 858), (W / 2 + 90, 858)], fill=ACCENT + (170,), width=2)
    ctr(PRICE_TXT, F_PRICE, 906, IVORY + (255,))
    ctr(COMPARE_TXT, F_SUB, 1052, (200, 186, 170, 180))
    ctr("nixwoods.com", F_SUB, 1180, IVORY + (235,))
    return L

# rupee glyph check -> fall back to "Rs" if the face has no U+20B9
def has_glyph(fontpath, ch):
    try:
        from fontTools.ttLib import TTFont
        f = TTFont(fontpath, fontNumber=0)
        return any(ord(ch) in t.cmap for t in f["cmap"].tables)
    except Exception:
        probe = Image.new("L", (160, 160), 0)
        ImageDraw.Draw(probe).text((10, 10), ch, font=ImageFont.truetype(fontpath, 100), fill=255)
        return np.asarray(probe).sum() > 0
RUP = "₹" if has_glyph(f"{FONT}/Playfair_Display-700.ttf", "₹") else "Rs "
PRICE_TXT = f"{RUP}9,999"
COMPARE_TXT = f"was {RUP}12,999"

# ---------------------------------------------------------------- prepare
print("preparing shots ...")
cache = {}
for s in SHOTS:
    src = load(s["img"])
    w = s.get("card_w", BAND_W)
    band = make_band(src, s["crop"], s["bright"], s.get("sat", 1.06), w)
    if s.get("warm"): band = warm_balance(band, s["warm"])
    cache[s["key"]] = dict(
        band=band, bx=(W - w) // 2, by=BAND_CY - band.size[1] // 2,
        shadow=band_shadow(band.size), back=make_backdrop(src),
        text=text_layer(s), end=endcard_layer() if s.get("endcard") else None,
    )
    print(f"  {s['key']}: {s['img']}  band {band.size}  y {cache[s['key']]['by']}"
          f"..{cache[s['key']]['by']+band.size[1]}")

# the dimension bracket: measured against the band of s3/s4
def bracket(layer, band_box, prog, alpha):
    """An architect's dimension line under the bar, drawn left end to right end.
    It spans the FULL band width, which is the full length of the fixture."""
    if alpha <= 0.01 or prog <= 0.0: return
    bx, by, bw, bh = band_box
    y = by + int(bh * 0.76)
    x0, x1 = bx + 8, bx + bw - 8
    xe = x0 + (x1 - x0) * prog
    d = ImageDraw.Draw(layer)
    col = ACCENT + (int(235 * alpha),)
    d.line([(x0, y), (xe, y)], fill=col, width=4)
    d.line([(x0, y - 20), (x0, y + 20)], fill=col, width=4)
    if prog > 0.98:
        d.line([(x1, y - 20), (x1, y + 20)], fill=col, width=4)

def frame_for(shot, lt):
    """Render one shot at local time lt."""
    c = cache[shot["key"]]
    dur = shot["dur"]
    p = lt / dur
    # backdrop drifts one way, band the other -> parallax without any h-scale
    bwi, bhi = c["back"].size
    ox = int((bwi - W) / 2 + math.sin(p * math.pi) * 18)
    oy = int((bhi - H) / 2 - 40 + p * 80)
    f = c["back"].crop((ox, oy, ox + W, oy + H)).copy()
    # product band: vertical drift only (8 px), full width preserved
    dy = int(round(-4 + p * 8))
    f.paste(Image.new("RGB", c["shadow"].size, (0, 0, 0)),
            (c["bx"] - 40, c["by"] - 44 + dy), c["shadow"])
    band = c["band"]
    if shot.get("lightup"):
        k = min(1.0, lt / 0.55)
        e = 0.88 + 0.12 * (k * k * (3 - 2 * k))
        band = ImageEnhance.Brightness(band).enhance(e)
        band = ImageEnhance.Color(band).enhance(0.90 + 0.10 * k)
    f.paste(band, (c["bx"], c["by"] + dy))
    f = Image.composite(f, Image.new("RGB", (W, H), (0, 0, 0)), VIG)

    if shot.get("endcard"):
        f = f.convert("RGBA"); f.alpha_composite(c["end"]); return f.convert("RGB")

    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if shot.get("dimension") or shot.get("dimension_hold"):
        bb = (c["bx"], c["by"] + dy, band.size[0], band.size[1])
        if shot.get("dimension"):
            prog = min(1.0, max(0.0, (lt - 0.30) / 1.10))
            prog = prog * prog * (3 - 2 * prog)
            bracket(ov, bb, prog, min(1.0, max(0.0, (lt - 0.25) / 0.30)))
        else:
            bracket(ov, bb, 1.0, max(0.0, 1.0 - lt / 0.55))

    a = min(1.0, max(0.0, (lt - 0.08) / 0.30)) * min(1.0, max(0.0, (dur - lt) / 0.30))
    if a > 0:
        t = c["text"].copy()
        t.putalpha(t.split()[3].point(lambda q: int(q * a)))
        ov.alpha_composite(t)
    f = f.convert("RGBA"); f.alpha_composite(ov)
    return f.convert("RGB")

# ---------------------------------------------------------------- render
starts, acc = [], 0.0
for s in SHOTS:
    starts.append(acc); acc += s["dur"]
TOTAL = acc
n = int(round(TOTAL * FPS))
print(f"rendering {n} frames ({TOTAL:.2f}s) ...")

silent = f"{OUT}/_silent.mp4"
ff = imageio_ffmpeg.get_ffmpeg_exe()
proc = subprocess.Popen(
    [ff, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18",
     "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent],
    stdin=subprocess.PIPE)

for i in range(n):
    t = i / FPS
    k = max(j for j in range(len(SHOTS)) if starts[j] <= t + 1e-6)
    k = min(k, len(SHOTS) - 1)
    lt = t - starts[k]
    img = frame_for(SHOTS[k], lt)
    # cross-dissolve in from the outgoing shot (skip s3->s4: same plate)
    if k > 0 and lt < XFADE and SHOTS[k]["key"] != "s4":
        prev = SHOTS[k - 1]
        img = Image.blend(frame_for(prev, prev["dur"] + lt), img, lt / XFADE)
    proc.stdin.write(img.tobytes())
    if i % 50 == 0: print(f"  {i}/{n}")
proc.stdin.close(); proc.wait()
print("video done, muxing music ...")

out = f"{OUT}/reel.mp4"
subprocess.run(
    [ff, "-y", "-loglevel", "error", "-i", silent, "-i", MUSIC,
     "-filter_complex",
     f"[1:a]atrim=0:{TOTAL},asetpts=N/SR/TB,"
     f"afade=t=in:st=0:d=0.4,afade=t=out:st={TOTAL-1.1:.3f}:d=1.1,"
     f"volume=0.82[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy",
     "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
os.remove(silent)
print("wrote", out)
