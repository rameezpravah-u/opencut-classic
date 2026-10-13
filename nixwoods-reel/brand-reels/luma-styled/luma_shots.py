"""Shots for the two Luma Pillar reels, cut from the owner's styling clip (src/luma-styling-20260331.mov,
27.6 s, 480x848 phone export, 31 Mar 2026).

Every shot is a source span stretched (or not) to a target length:
- slowed with motion-compensated interpolation, so slow motion does not stutter;
- upscaled to cover 1080x1920 with lanczos and a light unsharp, since the source is only 480 px wide;
- straightened when the lamp is lit (MOTION.md: never leaning).

Each shot is written once to work/<name>.mp4 (CRF 12, untracked) and reused by luma_colour.py (E1) and the
HyperFrames method reel (E2).

Spans were chosen from a 4-6 fps survey. A woman's head and hair enter at the right edge at 6.4-8.8 s and
12-14 s; no span below touches those times.
"""
import os, subprocess, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import axis                                            # noqa: E402
import imageio_ffmpeg                                                    # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
SRC = os.path.join(HERE, "src", "luma-styling-20260331.mov")
WORK = os.path.join(HERE, "work")
W, H, FPS = 1080, 1920, 30

# name: (source in, source out, straighten). Times in the source clip.
SPANS = {
    "mat":        (0.30, 1.90, False),     # the coral and marigold mat slides on
    "books":      (1.90, 2.95, False),     # books placed
    "candle":     (4.30, 5.15, False),     # candle placed
    "match":      (5.30, 6.30, False),     # the match strike, candle lit
    "placed":     (8.95, 9.75, False),     # the lamp set down, unlit
    "macro-off":  (22.35, 24.10, False),   # unlit, close: the frosted slot
    "macro-on":   (24.20, 24.98, True),    # lit, close, low angle
    "wide-on":    (19.30, 20.95, True),    # lit, the whole styled dresser
    "smoke-a":    (17.30, 19.20, True),    # smoke drifting through the glow
    "smoke-b":    (21.00, 22.25, True),    # the big smoke burst
    "macro-grain": (26.05, 27.55, True),   # lit, close, beside a book
    "wide-on-2":  (14.05, 15.40, True),    # lit wide, a second take
}


def shot(name, dur):
    """frames (uint8 HxWx3) for `dur` seconds of output from the named span, cached as work/<name>-<dur>.mp4"""
    a, b, straight = SPANS[name]
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, f"{name}-{dur:.3f}.mp4")
    n = round(dur * FPS)
    if not os.path.exists(path):
        k = dur / (b - a)
        vf = [f"setpts={k:.5f}*PTS"]
        if k > 1.05:
            vf.append("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1")
        # the source is 480x848 (0.566): scaled to 1920 tall it is 1087 wide, so cover the height and crop the sides
        vf += ["fps=30", f"scale=-2:{H}:flags=lanczos", f"crop={W}:{H}:(iw-{W})/2:0", "unsharp=5:5:0.6:5:5:0.0"]
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{b - a + 0.1:.3f}", "-i", SRC, "-an",
                        "-vf", ",".join(vf), "-frames:v", str(n), "-c:v", "libx264", "-crf", "12", "-preset", "fast",
                        "-pix_fmt", "yuv420p", path], check=True)
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = list(np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3))
    while len(fr) < n:
        fr.append(fr[-1])
    fr = fr[:n]
    if straight:
        fr = upright(fr)
    return fr


def upright(frames):
    """rotate each frame by the lit slot's measured tilt (smoothed), zoomed to cover so no corner shows"""
    angs = []
    for f in frames[::3]:
        try:
            (cx, cy), ang, L = axis(Image.fromarray(f))
        except TypeError:                                                # no lit line found in this frame
            ang, L = 0.0, 0
        angs.append(ang if L > 500 and abs(ang) < 8 else 0.0)
    angs = np.interp(np.arange(len(frames)), np.arange(0, len(frames), 3)[:len(angs)], angs)
    angs = np.convolve(np.pad(angs, 7, mode="edge"), np.ones(15) / 15, "valid")
    out = []
    for f, a in zip(frames, angs):
        if abs(a) < 0.15:
            out.append(f)
            continue
        th = np.radians(abs(a))
        z = np.cos(th) + (H / W) * np.sin(th)
        im = Image.fromarray(f).rotate(-a, resample=Image.BICUBIC)
        cw, ch = W / z, H / z
        out.append(np.asarray(im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2,
                                                                     (H + ch) / 2))))
    return out
