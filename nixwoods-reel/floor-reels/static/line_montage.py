#!/usr/bin/env python3
"""NixLine — "One line of light." A flicker montage after @stimuli.life's DdJEo0tM4l_ (9 s, ~10 cuts/s,
one brand mark fixed dead-centre while the world changes behind it).

Our constant is the product itself: every NixLine image we have — Rameez's phone footage, the real
shoot frame AC4I9815, and the accurate generated scenes — is rotated, scaled and placed so the lit
channel stands exactly vertical at the centre of the frame. The rooms change every sixteenth note;
the line never moves; the words sit either side of it, so the lamp is the space between them.
Excluded: every leaning-lamp image, the 30" wall light (different product), and nx00 @6.9 s (motion
blur, channel runs off frame).

Pacing is a notch calmer than the reference (0.15 s vs 0.10 s) for the brand's "no meme/EDM" rule:
music3-design (minimal electronic, 99.4 bpm, cleared for paid) from its measured drop at 10.752 s,
a cut on every sixteenth (0.1509 s) for 12 beats, then a 4-beat end card with price.
All frames are graded to one warm exposure so the cuts flicker without strobing.
Generated scenes are in the mix: tick Meta's AI disclosure.

    python3 floor-reels/static/line_montage.py   # -> concepts/meta-set/NX-META-V2-one-line-9x16.mp4
"""
import glob, json, os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from scipy import ndimage as ndi

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_set as m

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 99.4
SIX = BEAT / 4
MUSIC = os.path.join(m.ROOT, "audio", "music3-design.mp3")
DROP = 10.752
MONTAGE_BEATS, END_BEATS = 12, 4
TARGET_LEN = 980            # channel length on screen when the whole lamp is in shot
CX, CY = W // 2, 930        # where the channel's centre always sits
GAP = 84                    # half the space left for the line between words (widest channel: 58 px)
SAFE_BOTTOM = 1250
SRC = os.path.join(m.ROOT, "concepts", "meta-set", "line-src")
OUT = os.path.join(m.OUT, "NX-META-V2-one-line-9x16.mp4")


def axis(im):
    """Longest bright, low-saturation, elongated blob = the LED channel. Returns centre, angle, length."""
    s = 600 / max(im.size)
    a = np.asarray(im.resize((round(im.width * s), round(im.height * s)))).astype(np.float32)
    mx, mn = a.max(2), a.min(2)
    lab, n = ndi.label(ndi.binary_opening((mx > 228) & ((mx - mn) < 70)))
    best = None
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(xs) < 40:
            continue
        p = np.stack([xs, ys], 1).astype(np.float32); c = p.mean(0); q = p - c
        ev, vec = np.linalg.eigh(np.cov(q.T)); ax = vec[:, 1]
        L = np.percentile(q @ ax, 99.5) - np.percentile(q @ ax, 0.5)
        el = L / max(4 * np.sqrt(max(ev[0], 1e-6)), 1)
        if el >= 4 and (best is None or L * min(el, 15) > best[0]):
            best = (L * min(el, 15), c, ax, L)
    _, c, ax, L = best
    if ax[1] < 0:
        ax = -ax
    return c / s, float(np.degrees(np.arctan2(ax[0], ax[1]))), L / s


def grade(im, mask_keep=None):
    """One warm exposure for every source: mean luma toward ~0.30, a gentle amber balance."""
    a = np.asarray(im).astype(np.float32) / 255
    luma = (a @ [0.2126, 0.7152, 0.0722]).mean()
    g = np.log(0.30) / np.log(max(min(luma, 0.95), 0.05))
    a = np.clip(a, 1e-4, 1) ** g
    a *= [1.06, 1.0, 0.86]
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))


def place(path):
    src = Image.open(path).convert("RGB")
    (cx, cy), ang, L = axis(src)
    im = src.rotate(-ang, resample=Image.BICUBIC, center=(cx, cy), expand=False)
    valid = Image.new("L", src.size, 255).rotate(-ang, resample=Image.BICUBIC, center=(cx, cy), expand=False)
    full = L > 0.85 * im.height                      # a close-up: the line runs off the frame
    s_t = (H * 1.02 / L) if full else TARGET_LEN / L
    s_cov = max(CX / max(min(cx, im.width - cx), 1), CY / max(cy, 1), (H - CY) / max(im.height - cy, 1))
    s = max(s_t, min(s_cov, s_t * 1.4))
    size = (round(im.width * s), round(im.height * s))
    fg = im.resize(size, Image.LANCZOS)
    ox, oy = round(CX - cx * s), round(CY - cy * s)
    # background: the unrotated picture, covering the frame, blurred and dimmed, for any edge the source
    # can't fill (unrotated, so the rotation's empty corners never show)
    bs = max(W / src.width, H / src.height) * 1.05
    bg = src.resize((round(src.width * bs), round(src.height * bs)), Image.LANCZOS)
    bx, by = round(CX - cx * bs), round(CY - cy * bs)
    bx, by = min(0, max(bx, W - bg.width)), min(0, max(by, H - bg.height))
    canvas = Image.new("RGB", (W, H))
    canvas.paste(bg.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.55)), (bx, by))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rectangle((24, 24, size[0] - 24, size[1] - 24), fill=255)
    mask = ImageChops.multiply(mask, valid.resize(size).filter(ImageFilter.MinFilter(9)))
    canvas.paste(fg, (ox, oy), mask.filter(ImageFilter.GaussianBlur(18)))
    return grade(canvas)


def split(d, y, left, right, f, fill=None, fill_r=None):
    """Words either side of the line: the lamp itself is the space between them."""
    m.text(d, (CX - GAP, y), left, f, fill or m.CREAM, anchor="ra")
    m.text(d, (CX + GAP, y), right, f, fill_r or fill or m.CREAM, anchor="la")


def endcard(base):
    """Only the line stays lit: the room dims away from it, and the type sits either side of it."""
    x = np.abs(np.arange(W) - CX)
    keep = np.clip(1 - (x - 70) / 120, 0, 1)                          # full brightness within 70 px of the line
    k = (0.38 + 0.62 * keep)[None, :, None]
    img = Image.fromarray((np.asarray(base).astype(np.float32) * k).astype(np.uint8))
    img = m.scrim(img, "top", 0.55, 0.30).convert("RGBA")
    d = ImageDraw.Draw(img)
    split(d, 300, "One line", "of light.", m.SERIF(92))
    # left of the line: the price, right-aligned to it
    big, small = m.SANS(112), m.SANS_R(46)
    m.text(d, (CX - GAP, 820), m.PRICE, big, m.AMBER, anchor="ra")
    sy = 960
    m.text(d, (CX - GAP, sy), m.WAS, small, m.MUTED, anchor="ra")
    wy = sy + 30
    d.line((CX - GAP - small.getlength(m.WAS) - 2, wy, CX - GAP + 2, wy), fill=m.MUTED, width=4)
    # right of the line: the reasons, stacked
    y = 830
    for c in ["Solid teak", "COD", "Free delivery"]:
        y = m.chips(d, CX + GAP, y, [c]) + 16
    assert y <= SAFE_BOTTOM, y
    return img.convert("RGB")


def main():
    srcs = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
    real = [p for p in srcs if os.path.basename(p).startswith("real-")]
    gen = [p for p in srcs if os.path.basename(p).startswith("gen-")]
    frames = {p: place(p) for p in srcs}
    # alternate real and generated so the workshop and the homes keep trading places
    order, r, g = [], 0, 0
    slots = MONTAGE_BEATS * 4
    for k in range(slots):
        use_gen = (k % 3 == 2) or not real
        if use_gen:
            order.append(gen[g % len(gen)]); g += 1
        else:
            order.append(real[r % len(real)]); r += 1
    order[0] = next(p for p in gen if "A-diwali" in p)          # first frame = the thumbnail
    mark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    split(ImageDraw.Draw(mark), 300, "one line", "of light.", m.font("Fraunces-500-i.ttf", 64))
    end = endcard(frames[next(p for p in gen if "A-diwali" in p)])

    dur = (MONTAGE_BEATS + END_BEATS) * BEAT
    n = round(dur * FPS)
    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                             "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                             "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    cache = {}
    for i in range(n):
        t = i / FPS
        k = int(t / SIX)
        if k < slots:
            key = order[k]
            if key not in cache:
                f = frames[key].convert("RGBA"); f.alpha_composite(mark); cache[key] = f.convert("RGB")
            f = cache[key]
        else:
            f = end
        proc.stdin.write(f.tobytes())
    proc.stdin.close(); proc.wait()
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-ss", f"{DROP:.3f}", "-t", f"{dur:.3f}", "-i", MUSIC,
                    "-filter_complex", f"[1:a]volume=0.9,afade=t=out:st={dur - 0.8:.3f}:d=0.8,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{dur:.3f}", OUT], check=True)
    os.remove(tmp)
    json.dump({"order": [os.path.basename(p) for p in order], "slot_s": SIX, "duration_s": dur},
              open(OUT.replace(".mp4", "-timeline.json"), "w"), indent=1)
    print(os.path.relpath(OUT, m.ROOT), f"{dur:.2f}s, {slots} cuts, {len(srcs)} images ({len(real)} real, {len(gen)} generated)")


if __name__ == "__main__":
    main()
