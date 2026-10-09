#!/usr/bin/env python3
"""NixLine "noir" macro reel — after the look of @faisal_saleh_photography's DePramhoNWl (night, teal
shadows, amber highlights, shallow focus, hard cuts, no talking). Real footage only (Rameez, 9 Oct:
"Real photos only (free)"): the workshop phone clips in floor-reels/src and the 5 Aug shoot frame
AC4I9815, regraded to night by noir_grade.py. Nothing is generated, so no AI label.

Cuts on music7-noir's beat (103.4 bpm, 0.580 s), 20 beats = 11.6 s:
  4 glide along the lit line · 2 diagonal line · 4 second glide · 2 vertical line · 2 row of lamps ·
  6 end card: the full lamp in a dark room, NixLine / solid teak floor lamp / ₹999 · nixwoods.com

    python3 floor-reels/static/macro_noir.py   # -> concepts/macro/NX-NOIR-nixline-macro-9x16.mp4
"""
import os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from noir_grade import grade, W, H

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, BEAT = 30, 0.580
SRC = os.path.join(ROOT, "src")
OUT = os.path.join(ROOT, "concepts", "macro", "NX-NOIR-nixline-macro-9x16.mp4")
MUSIC = os.path.join(ROOT, "audio", "music7-noir.mp3")
CORNER = os.path.join(ROOT, "..", "hyperframes", "projects", "nixline-showcase", "assets", "nixline-corner.jpg")
A = os.path.join(ROOT, "..", "assets")
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)

# (clip, start s, beats, grade kwargs)
SHOTS = [("nx01-7923", 0.00, 4, {}),
         ("nx07-7922", 0.00, 2, dict(thr=0.96, reach=0.05)),
         ("nx08-7924", 0.40, 4, {}),
         ("nx06-7921", 7.00, 2, dict(thr=0.96, reach=0.05)),
         ("nx03-7926", 0.00, 2, dict(thr=0.90, reach=0.06))]
END_BEATS = 6


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def clip_frames(name, start, n):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", os.path.join(SRC, name + ".mp4"),
                          "-frames:v", str(n), "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    assert len(fr) >= n, (name, len(fr), n)
    return fr[:n]


def night_corner(corner):
    """The real lamp at night: room down to teal dark, teak body kept, LED channel lit, its warm light on
    the wall. Channel measured in this crop (prep.py): x 552 -> 535, y 1603 -> 413."""
    a = np.asarray(corner.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    teal = np.array([0.16, 0.33, 0.38], np.float32)
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    room = a * 0.22 + teal * lum * 0.30
    body = Image.new("L", (W, H), 0)
    ImageDraw.Draw(body).polygon([(512, 370), (566, 370), (590, 1610), (600, 1760), (480, 1760), (500, 1610)], fill=255)
    body = np.asarray(body.filter(ImageFilter.GaussianBlur(5))).astype(np.float32)[..., None] / 255
    out = room * (1 - body) + a * 0.78 * body
    ch = Image.new("L", (W, H), 0)
    ImageDraw.Draw(ch).line([(552, 1596), (535, 420)], fill=255, width=17)
    chm = np.asarray(ch.filter(ImageFilter.GaussianBlur(2))).astype(np.float32)[..., None] / 255
    core = np.array([1.0, 0.94, 0.82], np.float32)
    out = out * (1 - chm) + core * chm
    amber = np.array([1.0, 0.62, 0.28], np.float32)
    from scipy.ndimage import gaussian_filter                           # float blur: no 8-bit banding
    chf = np.asarray(ch).astype(np.float32) / 255
    near = gaussian_filter(chf, 26)[..., None]
    wide = gaussian_filter(chf[::4, ::4], 45).repeat(4, 0).repeat(4, 1)[:H, :W]
    wide = gaussian_filter(wide, 4)[..., None]
    out = out + amber * (near * 1.1 + wide * 5.5)                      # its light on the wall and floor
    return np.clip(out, 0, 1)


def end_text(alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    a = lambda c, k=1.0: c + (int(255 * alpha * k),)
    d.text((470, 300), "NixLine", font=font("Fraunces-600.ttf", 104), fill=a(CREAM), anchor="ra")
    d.text((470, 432), "solid teak", font=font("Fraunces-500-i.ttf", 50), fill=a(MUTED), anchor="ra")
    d.text((470, 492), "floor lamp", font=font("Fraunces-500-i.ttf", 50), fill=a(MUTED), anchor="ra")
    d.text((470, 1060), "₹999", font=font("Inter-600.ttf", 104), fill=a(AMBER), anchor="ra")
    d.text((470, 1190), "nixwoods.com", font=font("Inter-600.ttf", 38), fill=a(CREAM, 0.9), anchor="ra")
    return layer


def main():
    rng = np.random.default_rng(7)
    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "22", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    total = 0
    for name, start, beats, kw in SHOTS:
        n = round(beats * BEAT * FPS)
        for f in clip_frames(name, start, n):
            proc.stdin.write(grade(Image.fromarray(f), rng, **kw).tobytes())
        total += n
    # end card: the real lamp in its corner, graded to night, slow 6% push, type fades in
    corner = Image.open(CORNER).convert("RGB")
    night = Image.fromarray((night_corner(corner) * 255).astype(np.uint8))
    n = round(END_BEATS * BEAT * FPS)
    for k in range(n):
        u = k / (n - 1)
        z = 1.0 + 0.06 * (u * u * (3 - 2 * u))
        bw, bh = corner.width / z, corner.height / z               # push centred on the frame (the lamp is at x 543)
        x0, y0 = (corner.width - bw) / 2, (corner.height - bh) / 2
        fr = night.resize((W, H), Image.LANCZOS, box=(x0 * W / corner.width, y0 * H / corner.height,
                                                       (x0 + bw) * W / corner.width, (y0 + bh) * H / corner.height))
        f = np.asarray(fr).astype(np.float32) / 255 + rng.normal(0, 0.016, (H, W, 1))
        g = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        g.alpha_composite(end_text(min(max((k / FPS - 0.25) / 0.35, 0), 1)))
        proc.stdin.write(g.convert("RGB").tobytes())
    total += n
    proc.stdin.close(); proc.wait()
    dur = total / FPS
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-i", MUSIC, "-filter_complex",
                    f"[1:a]atrim=0:{dur:.3f},volume=0.9,afade=t=in:d=0.1,afade=t=out:st={dur - 1.0:.3f}:d=1.0[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{dur:.3f}", OUT], check=True)
    os.remove(tmp)
    print(os.path.relpath(OUT, ROOT), f"{dur:.2f}s, {len(SHOTS)} shots + end card")


if __name__ == "__main__":
    main()
