#!/usr/bin/env python3
"""Shot list for the NixLine voice-over reels (MoneyPrinterTurbo, Hindi and English), cut to the voice.

MoneyPrinterTurbo voices the script (Edge TTS), times the captions and assembles the reel from local
materials in order. To keep every shot under the line it belongs to, each material here is cut to the
gap between two caption starts in that language's voice-over (timing-<lang>.srt, written by the
subtitle stage), so the reel plays each shot once, in order, with no loop.

Real footage only (NixLine workshop clips, the 5 Aug shoot photo AC4I9815), the lamp always vertical.
Every shot takes MOTION.md's montage grade. Photo shots get one slow push (5-6%, smoothstep).
    python3 brand-reels/mpt-voice/build_materials.py en|hi [out_dir]
"""
import os, re, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
LANG = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else f"/home/user/MoneyPrinterTurbo/storage/local_videos/nixline-{LANG}"
sys.argv = sys.argv[:1]
from line_montage import grade                                         # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
PHOTO = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                     "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
# (name, caption index the shot starts on (1-based), kind, source, in-point / (cx, cy, height) in photo px)
SHOTS = [("01-bare-teak", 1, "clip", "floor-reels/src/nx06-7921.mp4", 2.70),   # ends before the bar flips
         ("02-lit", 2, "clip", "floor-reels/src/nx06-7921.mp4", 6.40),        # runs under captions 2-3
         ("04-standing", 4, "clip", "floor-reels/src/nx04-7930.mp4", 0.60),
         ("05-by-hand", 5, "clip", "floor-reels/src/nx03-7926.mp4", 0.00),
         ("06-block", 6, "photo", PHOTO, (2875, 4560, 1300)),
         ("07-plug-in", 7, "clip", "floor-reels/src/nx05-7920.mp4", 0.00),
         ("08-channel", 8, "photo", PHOTO, (2875, 3420, 1500)),
         ("09-corner", 10, "photo", PHOTO, None)]                      # None: the full lamp, centred
MAXSRC = {"07-plug-in": 1.35}                                        # nx05 tilts after 1.35 s: keep it vertical
TAIL = 0.6                                                             # hold after the last word
MIN_SPEED = 0.7                                                        # slowest a clip may run to fill its line


def srt_starts(path):
    t = []
    for a in re.findall(r"(\d+):(\d+):(\d+),(\d+) -->", open(path, encoding="utf-8").read()):
        h, m, s, ms = map(int, a)
        t.append(h * 3600 + m * 60 + s + ms / 1000)
    return t


def audio_len(task_dir):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 os.path.join(task_dir, "audio.mp3")], capture_output=True, text=True).stdout)


def encode(path, frames):
    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-an", path],
                         stdin=subprocess.PIPE)
    for a in frames:
        p.stdin.write(np.ascontiguousarray(a).tobytes())
    p.stdin.close(); assert p.wait() == 0, path


def clip_frames(src, t0, n_out, cap=None):
    """n_out frames from src at t0, slowed (never below MIN_SPEED) when the source span is short."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                os.path.join(ROOT, src)], capture_output=True, text=True).stdout)
    avail = dur - t0 - 0.05
    if cap:
        avail = min(avail, cap)
    speed = max(MIN_SPEED, min(1.0, avail * FPS / n_out))
    n_src = min(int(avail * FPS), int(np.ceil(n_out * speed)) + 1)
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", os.path.join(ROOT, src), "-frames:v", str(n_src),
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    idx = np.minimum((np.arange(n_out) * speed).astype(int), len(fr) - 1)
    return [np.asarray(grade(Image.fromarray(fr[i]))) for i in idx], speed, len(fr) / FPS


def photo_frames(spec, n_out, push):
    im = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
    if spec is None:
        box = (2100, 2349, 3648, 2349 + 1548 * 16 / 9)
    else:
        cx, cy, h = spec
        w = h * 9 / 16
        box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    base = np.asarray(grade(im.resize((round(W * 1.2), round(H * 1.2)), Image.LANCZOS, box=box)))
    base = Image.fromarray(base)
    out = []
    for k in range(n_out):
        u = k / max(n_out - 1, 1); z = 1 + push * u * u * (3 - 2 * u)
        bw, bh = base.width / z / 1.2, base.height / z / 1.2
        x0, y0 = (base.width - bw * 1.2) / 2 + 0, (base.height - bh * 1.2) / 2
        fr = base.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw * 1.2, y0 + bh * 1.2))
        out.append(np.asarray(fr))
    return out


def main():
    task = {"en": "0e1f1a00-0000-4000-8000-0000000000e1", "hi": "0e1f1a00-0000-4000-8000-0000000000a1"}[LANG]
    starts = srt_starts(os.path.join(HERE, f"timing-{LANG}.srt"))
    end = audio_len(f"/home/user/MoneyPrinterTurbo/storage/tasks/{task}") + TAIL
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        os.remove(os.path.join(OUT, f))
    edges = [0.0] + [starts[s[1] - 1] for s in SHOTS[1:]] + [end]
    for (name, _, kind, src, arg), a, b in zip(SHOTS, edges[:-1], edges[1:]):
        n = round(b * FPS) - round(a * FPS)
        if kind == "clip":
            fr, speed, have = clip_frames(src, arg, n, MAXSRC.get(name))
            note = f"speed {speed:.2f} (source {have:.2f} s)"
        else:
            fr = photo_frames(arg, n, 0.06 if arg is None else 0.05)
            note = "photo push"
        encode(os.path.join(OUT, f"{name}.mp4"), fr)
        print(f"{name:14s} {a:6.2f}-{b:6.2f}  {n / FPS:5.2f} s  {note}")


if __name__ == "__main__":
    main()
