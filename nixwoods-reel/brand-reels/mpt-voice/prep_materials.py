#!/usr/bin/env python3
"""Footage for the NixLine voice-over reels made with MoneyPrinterTurbo (Hindi and English).

Real footage only: the NixLine workshop clips and the clean 5 Aug shoot photo AC4I9815. Every shot shows
the lamp vertical (never leaning, never lying down). Each piece takes MOTION.md's montage grade
(line_montage.grade) so the cuts share one warm colour balance, then goes to MoneyPrinterTurbo's
local-materials folder in the order the voice-over needs.
    python3 brand-reels/mpt-voice/prep_materials.py [out_dir]
"""
import os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/MoneyPrinterTurbo/storage/local_videos/nixline"
sys.argv = sys.argv[:1]
from line_montage import grade                                         # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
CLIPS = [("m1-bare-teak", "floor-reels/src/nx06-7921.mp4", 3.0, 3.3),       # the bare bar before it is lit
         ("m2-lit-bar", "floor-reels/src/nx06-7921.mp4", 6.5, 3.0),        # flipped: the lit channel
         ("m3-many-bars", "floor-reels/src/nx03-7926.mp4", 0.0, 2.5),      # a bundle of lit bars
         ("m4-standing", "floor-reels/src/nx04-7930.mp4", 0.6, 2.8),       # one bar standing upright
         ("m5-upright", "floor-reels/src/nx05-7920.mp4", 0.0, 1.4)]        # upright, lit, in the workshop
PHOTO = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                     "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
PBOX = (2100, 2349, 3648, 2349 + 1548 * 16 / 9)                       # the lamp centred, upright on its block


def clip(name, src, t0, dur):
    n = round(dur * FPS)
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", os.path.join(ROOT, src), "-frames:v", str(n),
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-an",
                          os.path.join(OUT, name + ".mp4")], stdin=subprocess.PIPE)
    for a in fr:
        p.stdin.write(np.asarray(grade(Image.fromarray(a))).tobytes())
    p.stdin.close(); assert p.wait() == 0
    print(name, len(fr), "frames")


def main():
    os.makedirs(OUT, exist_ok=True)
    for c in CLIPS:
        clip(*c)
    im = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB").resize((W, H), Image.LANCZOS, box=PBOX)
    grade(im).save(os.path.join(OUT, "m6-corner.jpg"), quality=93)
    print("m6-corner.jpg")


if __name__ == "__main__":
    main()
