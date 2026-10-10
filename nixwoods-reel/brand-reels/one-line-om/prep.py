#!/usr/bin/env python3
"""Footage prep for "NixLine: One line of light", the first reel made through OpenMontage (hybrid
pipeline, HyperFrames atelier composition). Every frame is real: Rameez's NixLine workshop clips and the
clean 5 Aug shoot photo AC4I9815. Nothing generated, so no AI label.

The idea: one line of light holds still on the screen's centre (x 540) while the shots cut around it.
So each shot is aligned frame by frame:
  lit shots    the LED channel is found per frame (line_montage.axis, the detector V2 uses), its centre
               and angle smoothed over the shot, then each frame is rotated and shifted so the channel
               stands vertical on x 540. One zoom per shot, the smallest that never shows a frame edge.
  unlit shot   the bare teak bar is found the same way from its warm colour against the blue carpet.
  bundle       the many-bars shot is not aligned (there is no single line in it).
Every shot then takes MOTION.md's montage grade (line_montage.grade: 35% own colour, the rest one warm
tint, mean luma 0.31, the lit channel keeps a cream core), so cuts share one colour balance.

Writes into the OpenMontage project's HyperFrames workspace:
  assets/s1.mp4 .. s4.mp4   1080x1920, 30 fps, exact frame counts on the music6 beat grid
  assets/corner.jpg         AC4I9815 at 1.25x (so the push never upscales), channel on x 540
  assets/geometry.json      where the line sits in each shot, for the composition
    python3 brand-reels/one-line-om/prep.py [workspace]
"""
import json, os, subprocess, sys
import numpy as np
import cv2
import imageio_ffmpeg
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
sys.argv = sys.argv[:2]
from line_montage import axis, grade                                   # noqa: E402

WS = sys.argv[1] if len(sys.argv) > 1 else "/home/user/OpenMontage/projects/nixline-one-line-of-light/hyperframes"
OUT = os.path.join(WS, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = 0.8357                                                             # music6-corners beat
F = lambda n: round(n * B * FPS)                                       # frame index of beat n
CX = W // 2

# (name, source, in-point s, first beat, last beat, mode)
SHOTS = [("s1", "floor-reels/src/nx06-7921.mp4", 3.60, 0, 2, "bar"),
         ("s2", "floor-reels/src/nx06-7921.mp4", 6.60, 2, 4, "lit"),
         ("s3", "floor-reels/src/nx03-7926.mp4", 0.40, 4, 5, "none"),
         ("s4", "floor-reels/src/nx04-7930.mp4", 1.30, 5, 6, "lit")]
PHOTO = os.path.join(ROOT, "drive-pull", "shoot-20260805",
                     "NW-CREATIVE-IMG-20260805-nix-line-solid-wood-floor-lamp-AC4I9815-v1.JPG")
PK = 1.25                                                              # photo export scale
PBOX = (2100, 2349, 3648, 2349 + 1548 * 16 / 9)                       # nixline-showcase crop: channel on x 540


def frames(src, t0, n):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", os.path.join(ROOT, src), "-frames:v", str(n),
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    assert len(fr) >= n, (src, len(fr), n)
    return fr[:n]


def bar_axis(a):
    """The bare teak bar: warm pixels against the blue carpet, one centre per row, a straight-line fit.
    Returns (cx, cy), angle from vertical in degrees (axis() convention), and the bar's width."""
    hsv = cv2.cvtColor(np.ascontiguousarray(a), cv2.COLOR_RGB2HSV)
    # teak is saturated orange (S 130-255); the sunlit carpet fuzz is warm too but pale (S < 110)
    m = (hsv[..., 0] >= 12) & (hsv[..., 0] <= 28) & (hsv[..., 1] > 125) & (hsv[..., 2] > 130)
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA])                        # the bar is the largest warm blob
    ys, xs, ws = [], [], []
    for y in range(0, H, 8):
        row = np.nonzero(lab[y] == k)[0]
        if len(row) > 30:
            ys.append(y); xs.append((row[0] + row[-1]) / 2); ws.append(row[-1] - row[0])
    ys, xs = np.array(ys, float), np.array(xs, float)
    p = np.polyfit(ys, xs, 1)
    keep = np.abs(np.polyval(p, ys) - xs) < 25
    p = np.polyfit(ys[keep], xs[keep], 1)
    cy = H / 2
    return (np.polyval(p, cy), cy), float(np.degrees(np.arctan(p[0]))), float(np.median(ws)), float(ys[keep].min())


def smooth(v, k=9):
    v = np.asarray(v, float)
    if len(v) < 3:
        return v
    k = min(k, len(v) | 1 if len(v) % 2 else len(v) - 1)
    pad = np.pad(v, k // 2, mode="edge")
    return np.convolve(pad, np.ones(k) / k, mode="valid")


def matrix(cx, cy, ang, s):
    """Rotate about the line's centre so it stands vertical, scale by s, put it on x 540."""
    M = cv2.getRotationMatrix2D((float(cx), float(cy)), -ang, s)      # cv2: +angle = counter-clockwise
    M[0, 2] += CX - cx
    return M


def covers(M):
    Mi = cv2.invertAffineTransform(M)
    c = np.array([[0, 0, 1], [W, 0, 1], [0, H, 1], [W, H, 1]], float) @ Mi.T
    return (c[:, 0] >= 0).all() and (c[:, 0] <= W).all() and (c[:, 1] >= 0).all() and (c[:, 1] <= H).all()


def min_scale(track):
    lo, hi = 1.0, 2.0
    for _ in range(25):
        s = (lo + hi) / 2
        lo, hi = (lo, s) if all(covers(matrix(cx, cy, ang, s)) for cx, cy, ang in track) else (s, hi)
    return hi * 1.004


def encode(path, fr):
    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-g", "1",
                          "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-movflags", "+faststart", path], stdin=subprocess.PIPE)
    for a in fr:
        p.stdin.write(np.ascontiguousarray(a).tobytes())
    p.stdin.close(); assert p.wait() == 0, path


def main():
    os.makedirs(OUT, exist_ok=True)
    geo = {"beat": B, "fps": FPS, "frames": {}, "shots": {}}
    for name, src, t0, b0, b1, mode in SHOTS:
        n = F(b1) - F(b0)
        fr = frames(src, t0, n)
        info = {"source": src, "in": t0, "frames": n, "start_frame": F(b0)}
        if mode == "none":
            out = [np.asarray(grade(Image.fromarray(a))) for a in fr]
        else:
            raw = []
            for a in fr:
                if mode == "lit":
                    (cx, cy), ang, L = axis(Image.fromarray(a))
                    raw.append((cx, cy, ang, L))
                else:
                    (cx, cy), ang, wbar, top = bar_axis(a)
                    raw.append((cx, cy, ang, wbar, top))
            r = np.array(raw)
            track = list(zip(smooth(r[:, 0]), smooth(r[:, 1]), smooth(r[:, 2])))
            s = min_scale(track)
            out = []
            for a, (cx, cy, ang) in zip(fr, track):
                M = matrix(cx, cy, ang, s)
                g = cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                out.append(np.asarray(grade(Image.fromarray(g))))
            info.update(scale=round(s, 3), cx_raw=[round(float(v), 1) for v in r[[0, -1], 0]],
                        angle_raw=[round(float(v), 2) for v in r[[0, -1], 2]])
            if mode == "bar":
                info["bar_width"] = round(float(np.median(r[:, 3]) * s), 1)
                # top of the bar on screen (row of the first warm row, mapped through the transform)
                cx, cy, ang = track[0]
                M = matrix(cx, cy, ang, s)
                info["bar_top"] = round(float((M @ [cx, np.median(r[:, 4]), 1])[1]), 1)
            # check: the channel/bar now sits on x 540, vertical
            chk = axis(Image.fromarray(out[len(out) // 2])) if mode == "lit" else None
            if chk:
                (ccx, ccy), cang, cL = chk
                info.update(check_cx=round(ccx, 1), check_angle=round(cang, 2), channel_len=round(cL, 1),
                            channel_top=round(ccy - cL / 2, 1), channel_bottom=round(ccy + cL / 2, 1))
                lit = (np.asarray(out[len(out) // 2]).max(2) > 228)[int(ccy)]
                xs = np.nonzero(lit[CX - 120:CX + 120])[0]
                if len(xs):
                    info["channel_width"] = int(xs[-1] - xs[0] + 1)
        encode(os.path.join(OUT, f"{name}.mp4"), out)
        geo["shots"][name] = info
        print(name, json.dumps(info, default=float))

    im = ImageOps.exif_transpose(Image.open(PHOTO)).convert("RGB")
    ph = im.resize((round(W * PK), round(H * PK)), Image.LANCZOS, box=PBOX)
    ph = grade(ph)
    ph.save(os.path.join(OUT, "corner.jpg"), quality=93)
    (cx, cy), ang, L = axis(ph)
    geo["shots"]["corner"] = {"source": os.path.relpath(PHOTO, ROOT), "scale": PK,
                              "channel_cx": round(cx / PK, 1), "channel_cy": round(cy / PK, 1),
                              "channel_len": round(L / PK, 1), "angle": round(ang, 2)}
    print("corner", json.dumps(geo["shots"]["corner"], default=float))
    # end card: the flat Dusk ground (MOTION.md 6: vignette 1.08 - 0.35 r, grain sigma 2.2, lift 0.02)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    g = np.array([46, 30, 20], np.float32)[None, None] * (1.08 - 0.35 * r)[..., None]
    g = g + np.random.default_rng(7).normal(0, 2.2, (H, W, 1)) + 0.02 * 255 * 0.25
    Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).save(os.path.join(OUT, "ground.png"))
    # the logo, tinted cream for Dusk (MOTION.md 3)
    lg = Image.open(os.path.join(ROOT, "assets", "logo.png")).convert("RGBA")
    cream = Image.new("RGBA", lg.size, (246, 239, 228, 255)); cream.putalpha(lg.getchannel("A"))
    cream.save(os.path.join(OUT, "logo-cream.png"))
    geo["frames"] = {f"b{k}": F(k) for k in range(13)}
    with open(os.path.join(OUT, "geometry.json"), "w") as f:
        json.dump(geo, f, indent=1, default=float)


if __name__ == "__main__":
    main()
