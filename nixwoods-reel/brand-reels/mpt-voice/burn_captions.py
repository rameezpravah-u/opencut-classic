#!/usr/bin/env python3
"""Captions for the NixLine voice-over reels, laid out to MOTION.md instead of MoneyPrinterTurbo's centred subtitles.

MoneyPrinterTurbo voices, times, assembles and mixes the reel (rendered with --no-subtitle-enabled). Its
captions can only sit centred, and the NixLine's lit channel stands on the centre line in most shots, so
they crossed the light (MOTION.md 7.2). Here each caption is set in a side column clear of that shot's
channel (measured per shot with line_montage.axis), 140 px from it on close-ups, on a dark gradient that
fades with the text (MOTION.md 6), above y 1250 for paid placements (MOTION.md 3).

Type: Inter 600 for English, Hind SemiBold for Hindi (Devanagari; OFL, assets/Hind-OFL.txt), cream #F6EFE4,
the price in amber #E8A24A. Timing comes from the voice-over's own caption file (timing-<lang>.srt).
    python3 brand-reels/mpt-voice/burn_captions.py en|hi <in.mp4> <out.mp4>
"""
import os, re, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
LANG, SRC, DST = sys.argv[1:4]
sys.argv = sys.argv[:1]
from line_montage import axis                                          # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
FONT = os.path.join(ROOT, "assets", "Inter-600.ttf" if LANG == "en" else "Hind-SemiBold.ttf")
SIZE = 58 if LANG == "en" else 62
CREAM, AMBER = (246, 239, 228), (232, 162, 74)
X0, X1 = 70, 1010                       # screen edges the column may use (right UI strip is ~130 px)
GAP = 140                               # clear of the channel's centre on close-ups
YC = 1010                               # caption block centre; the block stays inside y 760-1250
SHOT_STARTS = [1, 2, 4, 5, 6, 7, 8, 10]  # caption index each shot starts on (build_materials.SHOTS)


def srt(path):
    out = []
    for m in re.finditer(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)\s*\n(.+?)(?:\n\n|\Z)",
                         open(path, encoding="utf-8").read(), re.S):
        g = list(map(int, m.groups()[:8]))
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        out.append((a, b, m.group(9).strip().rstrip("।.,")))
    return out


def frame_at(t):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return Image.fromarray(np.frombuffer(raw, np.uint8).reshape(H, W, 3))


def channel_x(t):
    try:
        (cx, cy), ang, L = axis(frame_at(t))
        return cx if L > 200 else None
    except Exception:
        return None


def wrap(text, font, width, draw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        cand = (cur + " " + w_).strip()
        if draw.textlength(cand, font=font) <= width or not cur:
            cur = cand
        else:
            lines.append(cur); cur = w_
    lines.append(cur)
    return lines


def layer(text, side, cx):
    """RGBA caption layer: wrapped text in the column on `side` of the channel, plus its gradient."""
    font = ImageFont.truetype(FONT, SIZE)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if side == "left":
        c0, c1 = X0, int((cx if cx else W / 2) - GAP)
    else:
        c0, c1 = int((cx if cx else W / 2) + GAP), X1 - 60
    lines = wrap(text, font, c1 - c0, d)
    lh = int(SIZE * 1.18)
    top = YC - lh * len(lines) // 2
    # dark gradient on that side, strongest at the screen edge, gone before the channel
    g = np.zeros((H, W), np.float32)
    xs = np.arange(W, dtype=np.float32)
    ramp = np.clip((c1 + 60 - xs) / (c1 + 60 - X0 + 1e-3), 0, 1) if side == "left" else np.clip((xs - c0 + 60) / (W - c0 + 60), 0, 1)
    ys = np.arange(H, dtype=np.float32)
    band = np.clip(1 - np.abs(ys - YC) / (lh * len(lines) / 2 + 220), 0, 1) ** 0.8
    g = (band[:, None] * ramp[None, :]) * 0.62
    shade = Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(24))
    lay.paste(Image.new("RGBA", (W, H), (24, 14, 8, 255)), (0, 0), shade)
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt)
    for i, ln in enumerate(lines):
        y = top + i * lh
        x = c1 - td.textlength(ln, font=font) if side == "left" else c0
        col = AMBER if "₹" in ln else CREAM
        td.text((x, y), ln, font=font, fill=col + (255,))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.55)))
    lay.alpha_composite(sh, (2, 3)); lay.alpha_composite(txt)
    return lay, top, top + lh * len(lines)


def main():
    caps = srt(os.path.join(HERE, f"timing-{LANG}.srt"))
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                               capture_output=True, text=True).stdout)
    edges = [0.0] + [caps[i - 1][0] for i in SHOT_STARTS[1:]] + [dur]
    shots = []
    for a, b in zip(edges[:-1], edges[1:]):
        xs = [x for x in (channel_x(a + (b - a) * f) for f in (0.25, 0.5, 0.75)) if x]
        cx = float(np.median(xs)) if xs else None
        side = "left" if (cx is None or cx >= W / 2 - 40) else "right"
        shots.append((a, b, cx, side))
        print(f"shot {a:6.2f}-{b:6.2f}  channel x {cx if cx is None else round(cx)}  captions {side}")
    layers = []
    for a, b, text in caps:
        mid = (a + b) / 2
        _, _, cx, side = next(s for s in shots if s[0] <= mid < s[1] + 1e-6)
        lay, y0, y1 = layer(text, side, cx)
        assert y1 <= 1250 and y0 >= 230, (text, y0, y1)
        layers.append((a, b, np.asarray(lay).astype(np.float32) / 255))
    n = round(dur * FPS)
    dec = subprocess.Popen([FF, "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-i", SRC, "-map", "0:v", "-map", "1:a", "-c:v", "libx264",
                            "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-c:a", "aac", "-b:a", "192k",
                            "-movflags", "+faststart", "-shortest", DST], stdin=subprocess.PIPE)
    k = 0
    while True:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        t = k / FPS
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32)
        for a, b, L in layers:
            if a <= t < b + 0.08:                                       # hold a beat past the word
                al = L[..., 3:4]
                f = f * (1 - al) + L[..., :3] * 255 * al
                break
        enc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes()); k += 1
    enc.stdin.close(); assert enc.wait() == 0 and dec.wait() == 0
    print(DST, k, "frames")


if __name__ == "__main__":
    main()
