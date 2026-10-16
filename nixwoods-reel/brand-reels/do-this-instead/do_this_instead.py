"""NixWoods "Stop guessing. Do this instead.": a five-step how-to on the real nixwoods.com, after @marcelodesignxh's
reel (instagram.com/reel/DccR9uIh5OO, 15.4 s, 719k views, 7.7k comments).

What that reel teaches: do not start from a blank page; start from a strong reference and follow numbered steps.
Its format: a hook bubble over a strong first shot, then numbered pills ("1. Go to …", "2. Explore" …) above
floating browser windows on a dark grid, a result, and a comment-keyword call to action, which is what drives its
comment count.

Ours: the same format on our own site, ending on the lamp lit in a real room.
  hook   Minimalist floor lamp, real footage (5 Aug shoot): "Stop guessing which lamp fits your corner."
  1      Go to nixwoods.com        the address typed, the home page
  2      Pick your room            the nav, then the Wooden Floor Lamps collection
  3      Pick your lamp            the Minimalist floor lamp card
  4      Check the size            its size chart and the 44 in / 60 in buttons
  5      Light up your corner      the lamp lit by an arched window (real footage)
  CTA    "Comment LAMP for the link"

Screens are real captures of nixwoods.com (Chromium, 16 Oct 2026, 1280 px wide at 2x), saved by capture.py into
work/ (not committed: they are re-captured on demand). Footage comes from library/cache via library/fetch.py.

    python3 brand-reels/do-this-instead/capture.py
    python3 brand-reels/do-this-instead/do_this_instead.py
"""
import glob, math, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import A, FF, FPS, H, W, font   # noqa: E402
from made_well import encoder                    # noqa: E402

WORK = os.path.join(HERE, "work")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261016-wooden-floor-lamp-minimalist-standing-light-do-this-instead-v1"
SR = 48000
DUR = 15.4
CACHE = os.path.join(ROOT, "library", "cache")
CLIP = "NW-CREATIVE-VID-20260806-minimalist-wooden-floor-lamp-sleek-cylindrical-lifestyle-arched-window-9x16-v1.mp4"

DUSK = np.array((46, 30, 20), np.float32) / 255
CREAM = (246, 239, 228)
INK = (58, 38, 24)
AMBER = (232, 162, 74)

# the window: a 1280x800 css viewport drawn 960 px wide (0.375 of the 2560 px capture)
WX, WY, WW = 60, 640, 960
BAR = 54                                   # browser chrome height
WH = 600                                   # content height
S = WW / 2560                              # capture px -> screen px

# steps: (start, end, pill text)
STEPS = [(3.0, 5.4, "1. Go to nixwoods.com"), (5.4, 7.4, "2. Pick your room"), (7.4, 9.6, "3. Pick your lamp"),
         (9.6, 11.6, "4. Check the size"), (11.6, DUR, "5. Light up your corner")]
HOOK = (0.0, 3.0)
CTA_T = 13.2


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def ease(u):
    u = min(1.0, max(0.0, u))
    return 1 - (1 - u) ** 3


def lerp(a, b, u):
    return a + (b - a) * u


# ------------------------------------------------------------------ assets
def load_shot(name):
    return np.asarray(Image.open(os.path.join(WORK, f"{name}-full.png")).convert("RGB"))


def clip_frames(t_in, secs):
    hits = glob.glob(os.path.join(CACHE, f"*-{CLIP}"))
    if not hits:
        sys.exit(f"missing {CLIP}: fetch it with library/fetch.py (drive id in the private INDEX.tsv)")
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", hits[0], "-t", f"{secs:.3f}", "-vf",
                          "fps=30,scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)


def grid_bg(t):
    """Dusk ground with a faint cream grid drifting up, as the reference's dark grid"""
    img = np.empty((H, W, 3), np.float32)
    img[:] = DUSK
    g = np.zeros((H, W), np.float32)
    off = int(t * 12) % 90
    g[(np.arange(H) + off) % 90 == 0, :] = 1
    g[:, np.arange(W) % 90 == 45] = 1
    yy, xx = np.mgrid[0:H, 0:W]
    vign = np.clip(1 - (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 1.6, 0.35, 1)
    img += g[..., None] * 0.07 * vign[..., None]
    return img


def text_img(text, f, fill):
    l, t, r, b = f.getbbox(text)
    im = Image.new("RGBA", (r - l + 4, b - t + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - l, 2 - t), text, font=f, fill=fill)
    return im


def pill(text, size=46):
    """the numbered step label: cream rounded pill, teak ink, Inter 600, a soft shadow"""
    f = font("Inter-600.ttf", size)
    ti = text_img(text, f, INK + (255,))
    pw, ph = ti.width + 52, ti.height + 34
    im = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20, 26, 20 + pw, 26 + ph), 18, fill=(0, 0, 0, 110))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    ImageDraw.Draw(im).rounded_rectangle((20, 20, 20 + pw, 20 + ph), 18, fill=CREAM + (255,),
                                         outline=(200, 190, 178, 255), width=2)
    im.alpha_composite(ti, (46, 37))
    return im


def emoji(ch, size):
    f = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    return im.resize((round(im.width * size / im.height), size), Image.LANCZOS)


def bubble(lines, size=58, mark=None):
    """the hook / CTA bubble: cream, rounded, two lines, an emoji in front of the first"""
    f = font("Inter-600.ttf", size)
    tis = [text_img(l, f, INK + (255,)) for l in lines]
    em = emoji(mark, round(size * 1.05)) if mark else None
    lead = (em.width + 14) if em else 0
    bw = max(ti.width for ti in tis) + lead + 70
    bh = sum(ti.height for ti in tis) + 20 * (len(tis) - 1) + 60
    im = Image.new("RGBA", (bw + 60, bh + 60), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((30, 38, 30 + bw, 38 + bh), 30, fill=(0, 0, 0, 120))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    ImageDraw.Draw(im).rounded_rectangle((30, 30, 30 + bw, 30 + bh), 30, fill=CREAM + (255,))
    y = 60
    for i, ti in enumerate(tis):
        x = 65 + (lead if i == 0 else 0)
        if i == 0 and em:
            im.alpha_composite(em, (65, y + (ti.height - em.height) // 2))
        im.alpha_composite(ti, (x, y))
        y += ti.height + 20
    return im


def chrome(url_text, caret):
    """the browser bar: three dots, an address field with the url, a caret while typing"""
    im = Image.new("RGBA", (WW, BAR), (238, 232, 224, 255))
    d = ImageDraw.Draw(im)
    for i, c in enumerate([(236, 106, 94), (244, 190, 79), (98, 197, 84)]):
        d.ellipse((22 + i * 26, 20, 36 + i * 26, 34), fill=c + (255,))
    d.rounded_rectangle((120, 10, WW - 30, BAR - 10), 12, fill=(255, 255, 255, 255))
    f = font("Inter-400.ttf", 22)
    d.text((140, 15), url_text, font=f, fill=INK + (255,))
    if caret:
        x = 140 + f.getlength(url_text) + 2
        d.line((x, 16, x, 38), fill=INK + (255,), width=2)
    return im


def cursor_img():
    im = Image.new("RGBA", (44, 60), (0, 0, 0, 0))
    pts = [(4, 2), (4, 46), (15, 36), (24, 56), (32, 52), (23, 33), (38, 33)]
    d = ImageDraw.Draw(im)
    d.polygon(pts, fill=(20, 14, 10, 255))
    inner = [(8, 11), (8, 37), (16, 30), (25, 49), (28, 47), (19, 29), (30, 29)]
    d.polygon(inner, fill=(255, 255, 255, 255))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 3, y + 4) for x, y in pts], fill=(0, 0, 0, 90))
    out = sh.filter(ImageFilter.GaussianBlur(3))
    out.alpha_composite(im)
    return out


# ------------------------------------------------------------------ composition
def paste(base, im, x, y, alpha=1.0):
    """alpha-composite an RGBA PIL image onto a float RGB frame"""
    a = np.asarray(im, np.float32) / 255
    x, y = int(round(x)), int(round(y))
    h, w = a.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
    al = sub[..., 3:] * alpha
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * al


def window_frame(content, url, caret):
    """the floating window: chrome + content, rounded, with a shadow; returns (RGBA PIL, x, y)"""
    win = Image.new("RGBA", (WW, BAR + WH), (0, 0, 0, 0))
    win.alpha_composite(chrome(url, caret), (0, 0))
    win.alpha_composite(Image.fromarray(content).convert("RGBA"), (0, BAR))
    mask = Image.new("L", win.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, WW - 1, BAR + WH - 1), 22, fill=255)
    win.putalpha(mask)
    out = Image.new("RGBA", (WW + 80, BAR + WH + 80), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((40, 52, 40 + WW, 52 + BAR + WH), 22, fill=(0, 0, 0, 150))
    out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    out.alpha_composite(win, (40, 40))
    return out


def view(shot, y, zoom=1.0, fx=0.5, fy=0.5):
    """the window's content: the capture scrolled to y (capture px), optionally zoomed about (fx, fy)"""
    src_h = round(WH / S)
    y = int(max(0, min(y, shot.shape[0] - src_h)))
    crop = shot[y:y + src_h]
    if zoom > 1.001:
        cw, ch = 2560 / zoom, src_h / zoom
        x0 = min(max(fx * 2560 - cw / 2, 0), 2560 - cw)
        y0 = min(max(fy * src_h - ch / 2, 0), src_h - ch)
        crop = crop[int(y0):int(y0 + ch), int(x0):int(x0 + cw)]
    return cv2.resize(crop, (WW, WH), interpolation=cv2.INTER_AREA)


def to_screen(px, py, y, zoom=1.0, fx=0.5, fy=0.5):
    """a capture-px point -> frame px, for the cursor, given the same view parameters"""
    src_h = WH / S
    y = max(0, y)
    sx, sy = px, py - y
    if zoom > 1.001:
        cw, ch = 2560 / zoom, src_h / zoom
        x0 = min(max(fx * 2560 - cw / 2, 0), 2560 - cw)
        y0 = min(max(fy * src_h - ch / 2, 0), src_h - ch)
        sx, sy = (sx - x0) * zoom, (sy - y0) * zoom
    return WX + 40 + sx * S, WY + 40 + BAR + sy * S


def main():
    os.makedirs(OUT, exist_ok=True)
    home, floor, mini = load_shot("home"), load_shot("floor"), load_shot("minimalist")
    hook_clip = clip_frames(6.3, HOOK[1] + 0.2)            # the shoot camera moving in on the lamp
    end_clip = clip_frames(1.0, DUR - STEPS[4][0] + 0.2)    # the lamp lit by the arched window
    pills = {s[2]: pill(s[2]) for s in STEPS}
    hook = bubble(["Stop guessing which lamp", "fits your corner. Do this instead."], 50, "✋")
    cta = bubble(["Comment LAMP", "for the link"], 56, "👇")
    cur = cursor_img()

    wavs = os.path.join(OUT, ".a.wav")
    clicks = audio(wavs)
    enc = encoder(wavs, os.path.join(OUT, f"{NAME}.mp4"), crf=20)
    keep = {}
    n = round(DUR * FPS)
    for i in range(n):
        t = i / FPS
        if t < HOOK[1]:
            x = hook_clip[min(i, len(hook_clip) - 1)].astype(np.float32) / 255
            x = x * 0.92 + 0.02
            u = ease((t - 0.15) / 0.35)
            paste(x, hook, (W - hook.width) / 2, 300 - 40 * (1 - u), u)
            # the hook card lifts away into the grid
            if t > HOOK[1] - 0.25:
                v = sstep((t - (HOOK[1] - 0.25)) / 0.25)
                x = x * (1 - v) + grid_bg(t) * v
        else:
            x = grid_bg(t)
            k = next(j for j, s in enumerate(STEPS) if s[0] <= t < s[1] or j == len(STEPS) - 1)
            a, b, label = STEPS[k]
            lt = t - a
            url, caret, cursor = "", False, None
            if k == 0:
                typed = "nixwoods.com"
                nch = int(min(len(typed), max(0, (lt - 0.15) / 0.06)))
                url, caret = typed[:nch], lt < 1.0
                content = view(home, lerp(0, 700, ease((lt - 1.1) / 1.2))) if lt > 0.95 else \
                    np.full((WH, WW, 3), 250, np.uint8)
            elif k == 1:
                url = "nixwoods.com"
                nav = (964, 160)                                   # "Wooden Floor Lamps" in the nav (capture px)
                if lt < 0.95:
                    z, fx, fy = 1 + 1.0 * ease((lt - 0.05) / 0.6), nav[0] / 2560, nav[1] / (WH / S)
                    content = view(home, 0, z, fx, fy)
                    p0, p1 = (1500, 700), nav
                    u = ease((lt - 0.1) / 0.7)
                    cursor = to_screen(lerp(p0[0], p1[0], u), lerp(p0[1], p1[1], u), 0, z, fx, fy)
                else:
                    url = "nixwoods.com/collections/wooden-floor-lamps"
                    yy = lerp(0, 230, ease((lt - 1.0) / 0.9))
                    content = view(floor, yy, 1.35, 0.42, 0.5)
            elif k == 2:
                url = "nixwoods.com/collections/wooden-floor-lamps"
                card = (804, 820)                                  # the Minimalist floor lamp card
                z = 1.35 + 1.15 * ease((lt - 1.0) / 0.7)
                fx = lerp(0.42, card[0] / 2560, ease(lt / 0.9))
                fy = lerp(0.5, (card[1] - 230) / (WH / S), ease(lt / 0.9))
                content = view(floor, 230, z, fx, fy)
                u = ease((lt - 0.1) / 0.75)
                cursor = to_screen(lerp(1500, card[0], u), lerp(1200, card[1] + 40, u), 230, z, fx, fy)
            elif k == 3:
                url = "nixwoods.com/products/wooden-floor-lamp-minimalist-standing-light"
                chart = (1076, 636)                                # the SIZE CHART image (capture px)
                sizes = (1860, 1186)                               # the 44 in / 60 in buttons
                u = ease((lt - 0.9) / 0.6)
                fx, fy = lerp(chart[0], sizes[0], u) / 2560, lerp(chart[1], sizes[1], u) / (WH / S)
                z = 1 + 1.1 * ease((lt - 0.15) / 0.6)
                content = view(mini, 0, z, fx, fy)
                if lt > 1.15:
                    cursor = to_screen(lerp(2200, 2040, ease((lt - 1.15) / 0.5)), 1186, 0, z, fx, fy)
            else:
                url = "nixwoods.com"
                content = None
            if content is not None:
                win = window_frame(content, url, caret and (i // 8) % 2 == 0)
                appear = ease((t - STEPS[0][0]) / 0.4)
                paste(x, win, WX, WY + 60 * (1 - appear), appear)
                if cursor:
                    paste(x, cur, cursor[0] - 4, cursor[1] - 2)
                    for ct in clicks:                              # a soft ring where the cursor clicks
                        if 0 <= t - ct < 0.35:
                            r = 10 + 60 * (t - ct) / 0.35
                            ring = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
                            ImageDraw.Draw(ring).ellipse((80 - r, 80 - r, 80 + r, 80 + r),
                                                         outline=AMBER + (int(220 * (1 - (t - ct) / 0.35)),),
                                                         width=5)
                            paste(x, ring, cursor[0] - 80, cursor[1] - 80)
            else:
                # step 5: the real lamp grows out of the window to fill the frame
                u = ease(lt / 0.7)
                fr = end_clip[min(round(lt * FPS), len(end_clip) - 1)].astype(np.float32) / 255
                fr = (np.clip((fr - 0.5) * 1.18 + 0.45, 0, 1) ** 1.12 * 255).astype(np.uint8)   # a little depth
                cw, ch = lerp(WW, W, u), lerp(WW * 16 / 9, H, u)
                cx, cy = lerp(WX + 40 + WW / 2, W / 2, u), lerp(WY + 40 + BAR + WH / 2, H / 2, u)
                card = cv2.resize(fr, (int(cw), int(ch)), interpolation=cv2.INTER_AREA)
                rad = int(lerp(22, 0, u))
                im = Image.fromarray(card).convert("RGBA")
                if rad:
                    m = Image.new("L", im.size, 0)
                    ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), rad, fill=255)
                    im.putalpha(m)
                paste(x, im, cx - cw / 2, cy - ch / 2)
                if t >= CTA_T:
                    v = ease((t - CTA_T) / 0.35)
                    paste(x, cta, 70 - 30, 1180 + 40 * (1 - v), v)          # left, clear of the lamp at x ~760
            # the step pill above the window (on the footage for step 5)
            pv = ease(lt / 0.25)
            pl = pills[label]
            paste(x, pl, (W - pl.width) / 2, 470 - 30 * (1 - pv), pv)
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(px.tobytes())
        if i in (45, 120, 190, 250, 330, 380, 440):
            keep[i] = px
    enc.stdin.close()
    enc.wait()
    os.remove(wavs)
    ims = [Image.fromarray(keep[k]).resize((270, 480)) for k in sorted(keep)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for j, im in enumerate(ims):
        sheet.paste(im, (270 * j, 0))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep[440]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", n, "frames")


def audio(path):
    """music3-design under the steps, typed keys in step 1, a click for each cursor click, a whoosh on each step;
    returns the click times so the picture can ring them"""
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)

    def load(p, ss=0.0, secs=DUR):
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{ss:.3f}", "-i", p, "-t", f"{secs:.3f}", "-ac", "2", "-ar",
                              str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.float32).reshape(-1, 2)

    mu = load(os.path.join(ROOT, "brand-reels", "audio", "music3-design.mp3"), 10.80 - 3.0)   # its kick on step 1
    mu = mu[:n] / (np.sqrt(np.mean(mu[:n] ** 2)) + 1e-9) * 10 ** (-19 / 20)
    m[:len(mu)] += mu
    rng = np.random.default_rng(7)

    def tick(t, gain, dur=0.025, hp=0.6):
        k = int(dur * SR)
        nz = rng.standard_normal(k).astype(np.float32)
        nz = np.diff(np.r_[0, nz]) * hp + nz * (1 - hp)            # brighter
        env = np.exp(-np.arange(k) / (k / 5))
        i0 = int(t * SR)
        seg = (nz * env * gain)[: max(0, n - i0)]
        m[i0:i0 + len(seg)] += seg[:, None]

    for c in range(12):                                            # "nixwoods.com" typed in step 1
        tick(STEPS[0][0] + 0.15 + c * 0.06, 0.18, 0.02)
    clicks = [STEPS[1][0] + 0.85, STEPS[2][0] + 0.9, STEPS[3][0] + 1.6]
    for c in clicks:
        tick(c, 0.45, 0.03, 0.3)
    wh = load(os.path.join(ROOT, "brand-reels", "audio", "sfx-whoosh.mp3"), 0, 2.0)
    wh = wh / (np.abs(wh).max() + 1e-9) * 10 ** (-16 / 20)
    pk = int(np.argmax(np.abs(wh[:, 0])))
    for a, _, _ in STEPS:
        i0 = max(0, int(a * SR) - pk)
        seg = wh[: n - i0]
        m[i0:i0 + len(seg)] += seg
    t = np.arange(n) / SR
    m *= np.clip((DUR - t) / 0.6, 0, 1)[:, None]
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())
    return clicks


if __name__ == "__main__":
    main()
