#!/usr/bin/env python3
"""NixWoods "photo carousel" reel — a recreation of @harshjpeg's Dbc3SVPIwmd ("Layout and photography
exploration", 13.4 s, 4:5, 210k views). Clean images only (Rameez, 10 Oct): the 5 Aug 2026 studio shoot
(drive-pull/shoot-20260805, never the watermarked archive). Nothing generated, no text.

The reference's grammar, measured off the video:
  - eight full-bleed photos, static, hard cuts
  - a fixed row of eight 4:5 thumbnails on a translucent dark panel across the middle
  - a white rounded frame glides from one thumbnail to the next (~0.8 s, eased); the photo cuts just
    before the frame lands; it holds ~0.9 s, then glides on
  - after the eighth it slides off the right of the panel and re-enters from the left onto the first,
    so the video loops: the last second and the first are the same photo
Cuts every 2 beats of music6-corners (71.8 bpm, 1.6714 s), the reference's ~1.67 s rhythm. The first and
last photo is NixLine, so the loop lands on the hero.

    python3 brand-reels/carousel/carousel_reel.py          # 4:5 (as the reference) and 9:16
"""
import glob, os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 30
BEAT, FIRST_BEAT = 0.8357, 0.396
P = 2 * BEAT                                   # one photo
GLIDE, CUT_AT = 0.80, 0.70                     # glide length; the photo cuts this far into the glide

# (frame, crop centre x, centre y, crop height as a fraction of the photo)
PHOTOS = [("9815", 0.70, 0.66, 0.58),          # NixLine beside the plant (hero, first and last)
          ("9861", 0.55, 0.60, 0.75),          # Edison dimmer lamp, pampas
          ("9882", 0.50, 0.50, 0.95),          # spiral, lit, olive wall
          ("9629", 0.50, 0.40, 0.75),          # wall light over the artwork
          ("9776", 0.45, 0.58, 0.72),          # floor lamp, living room at dusk
          ("9661", 0.47, 0.50, 0.60),          # pine wall light, the knot
          ("9798", 0.50, 0.45, 0.75),          # linear pendant, warm
          ("9751", 0.30, 0.55, 0.80)]          # spiral beside the bed
CX_9X16 = {"9861": 0.66}                       # the 9:16 crop is narrower: keep the lamp's teak block in frame

# geometry measured on the 720x900 reference, scaled to 1080 wide
SCALE = 1.5
PANEL = (90, 430, 630, 522)                    # x0 y0 x1 y1 at 720 wide
THUMB_X0, THUMB_Y0, THUMB_W, THUMB_H, PITCH = 97.5, 439, 60, 73, 67


def crop(key, cx, cy, hf, w, h):
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    ch = hf * im.height; cw = ch * w / h
    if cw > im.width:
        cw = im.width; ch = cw * h / w
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    im = im.resize((w, h), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    a = np.asarray(im).astype(np.float32) / 255                       # MOTION photo grade
    a = np.clip(a * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)
    return Image.fromarray((a * 255).astype(np.uint8))


def rounded(w, h, r, fill=255):
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), r * 4, fill=fill)
    return m.resize((w, h), Image.LANCZOS)


def ring(w, h, r, t):
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), r * 4, outline=255, width=t * 4)
    return m.resize((w, h), Image.LANCZOS)


def frame_pos(t, n):
    """Highlight position in thumbnail units (0 = first). Glide k runs from thumb k to k+1 and starts
    CUT_AT before the k-th cut; the photo cuts on the beat."""
    pos = 0.0
    for k in range(n):
        g0 = k * P - 0.03                                              # the first glide is already moving at t=0
        u = min(max((t - g0) / GLIDE, 0), 1)
        pos += u * u * (3 - 2 * u)
    return pos


def render(ratio):
    W = 1080
    H = 1350 if ratio == "4x5" else 1920
    out = os.path.join(HERE, f"NW-CAROUSEL-nixwoods-photo-carousel-{ratio}.mp4")
    n = len(PHOTOS)
    total = n * P
    bg = [crop(k, CX_9X16.get(k, cx) if ratio == "9x16" else cx, cy, hf, W, H) for k, cx, cy, hf in PHOTOS]
    tw, th = round(THUMB_W * SCALE), round(THUMB_H * SCALE)
    thumbs = [crop(k, cx, cy, hf, tw, th) for k, cx, cy, hf in PHOTOS]
    # the strip sits at the reference's height (0.53 of the frame); on 9:16 at the same height, inside the safe zone
    dy = (H * 0.528) - (PANEL[1] + PANEL[3]) / 2 * SCALE
    px0, py0, px1, py1 = [round(v * SCALE + (dy if i % 2 else 0)) for i, v in enumerate(PANEL)]
    panel = Image.new("RGBA", (px1 - px0, py1 - py0), (14, 10, 8, 0))
    panel.putalpha(rounded(px1 - px0, py1 - py0, 14, fill=82))
    tmask = rounded(tw, th, 7)
    strip = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    strip.alpha_composite(panel)
    for i, t_ in enumerate(thumbs):
        x = round((THUMB_X0 + i * PITCH) * SCALE) - px0
        y = round(THUMB_Y0 * SCALE + dy) - py0
        strip.paste(t_, (x, y), tmask)
    hw, hh, pad = tw + 10, th + 10, 5
    hl = Image.new("RGBA", (hw, hh), (255, 255, 255, 0)); hl.putalpha(ring(hw, hh, 11, 3))

    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", out + ".video.mp4"], stdin=subprocess.PIPE)
    nf = round(total * FPS)
    for f in range(nf):
        t = f / FPS
        shown = sum(1 for k in range(n) if t >= k * P - 0.03 + CUT_AT) % n   # the photo cuts near the end of each glide
        fr = bg[shown].convert("RGBA")
        s = strip.copy()
        pos = frame_pos(t, n)
        for p in (pos, pos - n):                                       # the wrap: off the right, in from the left
            x = round((THUMB_X0 + p * PITCH) * SCALE) - px0 - pad
            if -hw < x < s.width:
                s.paste(hl, (x, round(THUMB_Y0 * SCALE + dy) - py0 - pad), hl)      # clipped to the panel
        fr.alpha_composite(s, (px0, py0))
        proc.stdin.write(fr.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()
    # music from a beat such that a beat lands on every cut
    first_cut = CUT_AT - 0.03
    off = FIRST_BEAT + 2 * BEAT - first_cut
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", out + ".video.mp4", "-ss", f"{off:.4f}", "-i", MUSIC,
                    "-filter_complex", f"[1:a]atrim=0:{total:.3f},volume=0.9,afade=t=in:d=0.08,"
                    f"afade=t=out:st={total - 0.8:.3f}:d=0.8[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{nf / FPS:.3f}", out], check=True)
    os.remove(out + ".video.mp4")
    print(os.path.relpath(out, ROOT), f"{nf / FPS:.2f}s")


if __name__ == "__main__":
    for r in (sys.argv[1:] or ["4x5", "9x16"]):
        render(r)
