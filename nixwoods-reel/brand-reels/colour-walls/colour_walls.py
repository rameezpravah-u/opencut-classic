#!/usr/bin/env python3
"""NixWall on coloured walls — after @artdecoplasteringfl's DeAROFURtzU ("Moulding doesn't have to be white",
20.8 s: one room after another painted Red. Orange. Yellow. Green. Blue., a warm sconce on every wall, a
one-word serif label per colour, then a long hold where the same room repaints itself).

Rameez, 10 Oct: "Our wall light collection can be used. Rest remain the same ... change the light with our
wall lights." Their footage is theirs (and generated), so it is not reused: the structure, the labels, the
pacing and the repaint are rebuilt on our own clean photos of NixWall lit (AC4I9629 with the wall
moulding, 9641, 9644, 9645 — 5 Aug shoot).

The paint is applied in code, physically: each photo's wall is (white paint) x (light), so a new colour is
observed x paint / white, which keeps NixWall's warm pool, the soft shadows and the moulding's relief on
every colour. Objects (the wood bar, its lit strip, the artwork, the TV) are masked out and keep their own
colour. Nothing generated.

On music6-corners (71.8 bpm, 0.8357 s), first beat 0.396 s:
  round 1   five wide walls, 2 beats each: Red. Orange. Yellow. Green. Blue.
  round 2   five closer walls, 1 beat each
  finale    the moulding wall (9629) repaints Blue -> Red in the shot over 1 beat, then holds Red under a
            slow push for 7 beats, the music fading out

    python3 brand-reels/colour-walls/colour_walls.py   # -> brand-reels/colour-walls/NW-COLOURWALL-nixwall-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from scipy.ndimage import gaussian_filter, binary_dilation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
A = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "NW-COLOURWALL-nixwall-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
MUSIC_IN = 0.396
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = 0.8357
SC = 1.05                                                    # 5% headroom for the push

# paint colours (albedo, 0-1), deep and chalky like the reference's walls
PAINT = {"Red": (0.42, 0.08, 0.09), "Orange": (0.56, 0.22, 0.10), "Yellow": (0.66, 0.46, 0.14),
         "Green": (0.28, 0.34, 0.22), "Blue": (0.15, 0.22, 0.34)}
MOOD = 0.86                                                  # the reference's rooms sit darker than our studio

# objects that keep their own colour, as photo fractions (x0, x1, y0, y1); bars are the tight measured boxes
OBJ = {"9629": [(0.1721, 0.8564, 0.0614, 0.1016), (0.235, 0.755, 0.355, 0.705)],     # bar, artwork
       "9641": [(0.2368, 0.7160, 0.0651, 0.1089), (0.06, 0.90, 0.565, 1.0)],           # bar, TV + its mount
       "9644": [(0.2423, 0.7215, 0.1111, 0.1586), (0.255, 0.705, 0.345, 0.665)],       # bar, artwork
       "9645": [(0.1901, 0.4730, 0.1195, 0.1809), (0.185, 0.470, 0.430, 0.870)]}       # bar, artwork

# shots: (photo, crop cx, crop height as a fraction of the photo, where the bar sits in the frame, colour, beats)
ROUND1 = [("9629", 0.50, 0.95, 0.20, "Red", 2), ("9644", 0.48, 0.70, 0.22, "Orange", 2),
          ("9641", 0.48, 0.52, 0.24, "Yellow", 2), ("9645", 0.33, 0.90, 0.20, "Green", 2),
          ("9644", 0.48, 0.55, 0.26, "Blue", 2)]
ROUND2 = [("9629", 0.52, 0.34, 0.34, "Red", 1), ("9644", 0.48, 0.34, 0.34, "Orange", 1),
          ("9645", 0.33, 0.50, 0.30, "Yellow", 1), ("9641", 0.48, 0.40, 0.32, "Green", 1),
          ("9629", 0.42, 0.50, 0.24, "Blue", 1)]
FINALE = ("9629", 0.50, 0.95, 0.20)                     # wide enough for the whole 40-inch bar
PAD = 0.35                                                   # wall added above the bar, as a fraction of the photo


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def load(key):
    """The photo with plain wall added above it (the bars sit near the top of every frame). The wall is
    extended from its own top rows and grain; it is painted over anyway, so the seam disappears."""
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    small = np.asarray(im.resize((im.width // 4, im.height // 4))).astype(np.float32) / 255
    p = round(PAD * small.shape[0])
    row = gaussian_filter(small[:10].mean(0), (12, 0))
    noise = small[:10] - gaussian_filter(small[:10], (1, 1, 0))
    rng = np.random.default_rng(int(key))
    ext = row[None] * np.linspace(0.94, 1.0, p)[:, None, None] + rng.choice(noise.reshape(-1, 3), size=p * small.shape[1]).reshape(p, -1, 3)
    top = Image.fromarray((np.clip(ext, 0, 1) * 255).astype(np.uint8)).resize((im.width, p * 4), Image.BICUBIC)
    out = Image.new("RGB", (im.width, im.height + top.height)); out.paste(top, (0, 0)); out.paste(im, (0, top.height))
    return out, top.height, im.height


def crop(im, pad, h0, key, cx, hf, bar_at):
    ch = hf * h0; cw = ch * 9 / 16
    if cw > im.width:
        cw = im.width; ch = cw * 16 / 9
    bx0, bx1, by0, by1 = OBJ[key][0]
    bar_y = pad + (by0 + by1) / 2 * h0
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(bar_y - bar_at * ch, 0), im.height - ch)
    return (x0, y0, x0 + cw, y0 + ch)


def wall_mask(key, im, box, size, pad, h0):
    """1 on the wall (moulding included), 0 on objects, soft at the edges."""
    w, h = size
    m = np.ones((h, w), np.float32)
    x0, y0, x1, y1 = box
    sx, sy = w / (x1 - x0), h / (y1 - y0)
    boxes = []
    for fx0, fx1, fy0, fy1 in OBJ[key]:
        a0, a1 = int((fx0 * im.width - x0) * sx), int((fx1 * im.width - x0) * sx)
        b0, b1 = int((pad + fy0 * h0 - y0) * sy), int((pad + fy1 * h0 - y0) * sy)
        m[max(b0, 0):max(b1, 0), max(a0, 0):max(a1, 0)] = 0
        boxes.append((max(a0, 0), max(b0, 0), max(a1, 0), max(b1, 0)))
    return m, boxes


def painter(key, cx, hf, bar_at):
    """Returns (photo float, wall mask, white reference) at output size (with push headroom)."""
    im, pad, h0 = load(key)
    box = crop(im, pad, h0, key, cx, hf, bar_at)
    size = (round(W * SC), round(H * SC))
    a = np.asarray(im.resize(size, Image.LANCZOS, box=box)).astype(np.float32) / 255
    m, boxes = wall_mask(key, im, box, size, pad, h0)
    L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    sat = (a.max(2) - a.min(2)) / np.maximum(a.max(2), 1e-3)
    wl = np.median(L[m > 0.5])
    a0, b0, a1, b1 = boxes[0]                                          # inside the bar's box, paint what is wall:
    sub = (sat[b0:b1, a0:a1] < 0.16) & (L[b0:b1, a0:a1] > 0.6 * wl) & (L[b0:b1, a0:a1] < 0.9)   # pale, grey, not the strip
    m[b0:b1, a0:a1] = np.maximum(m[b0:b1, a0:a1], sub.astype(np.float32))
    m = m * (L > 0.10) * (L < 0.995)                                   # not the darkest shadows
    m = gaussian_filter(m, 2.0)
    sel = m > 0.9
    white = np.median(a[sel], 0) if sel.sum() > 1000 else np.array([0.75, 0.75, 0.75], np.float32)
    white = white / white.mean() * np.percentile(L[sel], 92)          # the wall's own white, near its lit end
    return a, m[..., None], white


def paint(a, m, white, colour):
    rgb = np.array(colour, np.float32)
    painted = np.clip(a * rgb / np.maximum(white, 1e-3), 0, 1) * MOOD
    return a * (1 - m) + painted * m


VIGN = None


def grade(a):
    global VIGN
    if VIGN is None or VIGN.shape[:2] != a.shape[:2]:
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        r = np.sqrt(((xx - a.shape[1] / 2) / (a.shape[1] / 2)) ** 2 + ((yy - a.shape[0] / 2) / (a.shape[0] / 2)) ** 2)
        VIGN = np.clip(1.06 - 0.30 * r, 0, 1)[..., None].astype(np.float32)
    return np.clip(a * VIGN * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)


def label_layer(word, alpha, pos):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text(pos, word + ".", font=font("Fraunces-600.ttf", 92), fill=(246, 239, 228, int(255 * alpha)), anchor="mm")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55)))
    lay.alpha_composite(sh, (0, 4)); lay.alpha_composite(txt)
    return lay


def frame_from(a, z):
    """Centre crop of the oversized frame at zoom z (1 = the 5% headroom kept), as a PIL image."""
    img = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    bw, bh = W / z, H / z
    x0, y0 = (img.width - bw) / 2, (img.height - bh) / 2
    return img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))


def main():
    shots = [(s, "cut") for s in ROUND1 + ROUND2]
    nf_total = round((sum(s[5] for s in ROUND1 + ROUND2) + 8) * B * FPS)
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    t0 = 0
    for (key, cx, hf, bar_at, colour, beats), _ in shots:
        label_pos = (W // 2, round((bar_at + 0.15) * H))                  # under the light, as the reference
        a, m, white = painter(key, cx, hf, bar_at)
        img = grade(paint(a, m, white, PAINT[colour]))
        n = round((t0 + beats * B) * FPS) - round(t0 * FPS)
        for k in range(n):
            u = k / max(n - 1, 1)
            fr = frame_from(img, 1 + 0.025 * u).convert("RGBA")          # a gentle creep, like the reference
            fr.alpha_composite(label_layer(colour, min(1, (k / FPS) / 0.12), label_pos))
            proc.stdin.write(fr.convert("RGB").tobytes())
        t0 += beats * B
    # finale: the same moulding wall repaints Blue -> Red, then holds Red under a slow push
    a, m, white = painter(*FINALE)
    label_pos = (W // 2, round((FINALE[3] + 0.15) * H))
    blue, red = grade(paint(a, m, white, PAINT["Blue"])), grade(paint(a, m, white, PAINT["Red"]))
    n = nf_total - round(t0 * FPS)
    for k in range(n):
        t = k / FPS
        u = min(t / B, 1); e = u * u * (3 - 2 * u)                         # the repaint takes one beat
        img = blue * (1 - e) + red * e
        p = k / max(n - 1, 1); z = 1 + 0.05 * (p * p * (3 - 2 * p))
        fr = frame_from(img, z).convert("RGBA")
        if e < 0.5:
            fr.alpha_composite(label_layer("Blue", 1 - e * 2, label_pos))
        else:
            fr.alpha_composite(label_layer("Red", (e - 0.5) * 2, label_pos))
        proc.stdin.write(fr.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()

    total = nf_total / FPS
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{MUSIC_IN:.3f}", "-i", MUSIC, "-t", f"{total:.3f}", "-ac", "2",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    k = int(0.9 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x = x * (0.6 / max(np.abs(x).max(), 1e-3))
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f}s")


if __name__ == "__main__":
    main()
