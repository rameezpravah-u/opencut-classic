#!/usr/bin/env python3
"""DRAFT, by Rameez's instruction (10 Oct): @artdecoplasteringfl's reel DeAROFURtzU with its wall sconces
swapped for our vertical wooden wall light. Third-party footage: Rameez will credit the original account
when he posts. Not for paid ads. The credit line is deliberately not burned in (his call).

The reference video is not stored in the repo; this script reads it from the path given (or the session
scratchpad) and writes the swapped version.

Per shot (16, cut boundaries detected by frame difference):
  track    the sconce's glowing tube, found per frame as the warm-bright component nearest a hand-marked
           start point, merged across its two lit segments, then fitted to a straight line through the shot
           (the camera only pushes); widened for the brass caps and back plate
  remove   a clean plate is inpainted once from the shot's first frame and warped with the track to every
           frame, so the fill does not flicker
  place    our walnut vertical wall light (AC4I9652, cut out of the 5 Aug shoot) at the sconce's centre,
           1.4x its height, toned to the room (dimmed, warmed), with a warm wash behind it on the wall and
           light along its edges
  labels   their white colour words are restored on top wherever the swap touched them
Audio: the reel's own track, unchanged.

    python3 brand-reels/swap-draft/swap_reel.py <ref.mp4>
"""
import glob, json, os, subprocess, sys
import numpy as np
import cv2
import imageio_ffmpeg
from PIL import Image, ImageOps
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
OUT = os.path.join(HERE, "NW-SWAPDRAFT-artdeco-reel-vertical-wall-light-9x16.mp4")
FF = imageio_ffmpeg.get_ffmpeg_exe()
SW, SH = 720, 1280                                   # the reference's size
W, H = 1080, 1920
CUTS = [0, 55, 105, 156, 182, 206, 234, 260, 287, 312, 338, 363, 389, 412, 463, 568, 621]
START = [(295, 460), (263, 447), (172, 488), (231, 477), (262, 569), (198, 387), (225, 390), (418, 450),
         (374, 432), (403, 432), (446, 432), (418, 432), (438, 450), (446, 450), (446, 464), (418, 450)]
BAR_BOX = (0.5077, 0.5603, 0.1988, 0.5541)           # the walnut bar in AC4I9652 (fractions)


def frames(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, SH, SW, 3)


def components(f):
    a = f.astype(np.float32)
    L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    m = ((L > 165) & (a[..., 0] - a[..., 2] > 35)).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m)
    return [(st[i], cen[i]) for i in range(1, n) if st[i][4] >= 60]


def track(fr):
    fits = []
    for s in range(16):
        prev, rows = START[s], []
        for k in range(CUTS[s], CUTS[s + 1]):
            near = [(st, c) for st, c in components(fr[k])
                    if abs(c[0] - prev[0]) < 45 and abs(c[1] - prev[1]) < 170 and st[3] >= st[2] * 1.2]
            if not near:
                continue
            x0 = min(st[0] for st, _ in near); y0 = min(st[1] for st, _ in near)
            x1 = max(st[0] + st[2] for st, _ in near); y1 = max(st[1] + st[3] for st, _ in near)
            rows.append((k, x0, y0, x1, y1)); prev = ((x0 + x1) / 2, (y0 + y1) / 2)
        g = np.array(rows, float); t = g[:, 0]; fit = []
        for j in range(4):
            v = g[:, j + 1]; p = np.polyfit(t, v, 1)
            res = np.abs(np.polyval(p, t) - v); keep = res < max(6, np.percentile(res, 70))
            fit.append(np.polyfit(t[keep], v[keep], 1) if keep.sum() > 3 else p)
        fits.append(fit)
    return fits


def box_at(fit, k, grow=(0.38, 0.22)):
    x0, y0, x1, y1 = [np.polyval(p, k) for p in fit]
    w, h = x1 - x0, y1 - y0
    return x0 - w * grow[0], y0 - h * grow[1], x1 + w * grow[0], y1 + h * grow[1]


def our_bar():
    """The walnut bar cut out of AC4I9652 (white wall -> alpha), RGBA float."""
    f = glob.glob(os.path.join(SHOOT, "*AC4I9652*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    x0, x1, y0, y1 = BAR_BOX
    pad = 30
    box = (int(x0 * im.width) - pad, int(y0 * im.height) - pad, int(x1 * im.width) + pad, int(y1 * im.height) + pad)
    a = np.asarray(im.crop(box)).astype(np.float32) / 255
    wall = np.concatenate([a[:, :20], a[:, -20:]], 1).mean(1)          # wall colour per row, both sides
    d = np.sqrt(((a - wall[:, None]) ** 2).sum(2))
    alpha = np.clip((d - 0.10) / 0.15, 0, 1)
    alpha[:pad - 4] = 0; alpha[-(pad - 4):] = 0
    return np.dstack([a, gaussian_filter(alpha, 0.7)])


def text_mask(f):
    """Their white serif labels: bright and neutral (the sconce glass is bright but warm)."""
    a = f.astype(np.float32)
    white = (a.min(2) > 200) & (a[..., 0] - a[..., 2] < 32)
    return cv2.dilate(white.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)


def main(ref):
    fr = frames(ref)
    fits = track(fr)
    bar = our_bar()
    bh0, bw0 = bar.shape[:2]
    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    for s in range(16):
        fit = fits[s]
        k0 = CUTS[s]
        # clean plate from the shot's first frame
        X0, Y0, X1, Y1 = box_at(fit, k0)
        hole = np.zeros((SH, SW), np.uint8)
        hole[int(max(Y0, 0)):int(min(Y1, SH)), int(max(X0, 0)):int(min(X1, SW))] = 255
        plate = cv2.inpaint(np.ascontiguousarray(fr[k0]), hole, 9, cv2.INPAINT_TELEA).astype(np.float32)
        for k in range(CUTS[s], CUTS[s + 1]):
            f = fr[k].astype(np.float32)
            x0, y0, x1, y1 = box_at(fit, k)
            # warp the plate from the first frame's box to this frame's (scale about the box centre)
            sc = (y1 - y0) / (Y1 - Y0)
            cx0, cy0, cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2, (x0 + x1) / 2, (y0 + y1) / 2
            M = np.float32([[sc, 0, cx - sc * cx0], [0, sc, cy - sc * cy0]])
            warped = cv2.warpAffine(plate, M, (SW, SH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            m = np.zeros((SH, SW), np.float32)
            m[int(max(y0, 0)):int(min(y1, SH)), int(max(x0, 0)):int(min(x1, SW))] = 1
            m = gaussian_filter(m, 3)[..., None]
            out = f * (1 - m) + warped * m
            # our light: 1.4x the sconce's height, centred on it
            th = (y1 - y0) * 1.4                                         # 1.4x the (capped) sconce height
            sbar = th / bh0
            nb = cv2.resize(bar, (max(3, round(bw0 * sbar)), max(3, round(bh0 * sbar))), interpolation=cv2.INTER_AREA)
            bx0, by0 = int(round(cx - nb.shape[1] / 2)), int(round(cy - nb.shape[0] / 2))
            # the room's light level around the sconce sets how bright the wood reads
            ring = f[int(max(y0 - 40, 0)):int(min(y1 + 40, SH)), int(max(x0 - 60, 0)):int(min(x1 + 60, SW))]
            lvl = np.clip(ring.mean() / 255 / 0.45, 0.35, 1.0)
            rgb = nb[..., :3] * 255 * np.array([1.0, 0.88, 0.74], np.float32) * 0.90 * lvl
            al = nb[..., 3:4]
            # light along the edges: the LED washes the wall behind the bar
            glow = np.zeros((SH, SW), np.float32)
            ys, xs = slice(max(by0, 0), min(by0 + nb.shape[0], SH)), slice(max(bx0, 0), min(bx0 + nb.shape[1], SW))
            sub = al[(ys.start - by0):(ys.stop - by0), (xs.start - bx0):(xs.stop - bx0), 0]
            glow[ys, xs] = sub
            halo = gaussian_filter(glow, max(4, nb.shape[1] * 0.45)) * 0.9 + gaussian_filter(glow, nb.shape[1] * 1.8) * 1.2
            out = out + (halo / max(halo.max(), 1e-3))[..., None] * np.array([255, 170, 90], np.float32) * 0.80
            reg = out[ys, xs]
            sub_rgb = rgb[(ys.start - by0):(ys.stop - by0), (xs.start - bx0):(xs.stop - bx0)]
            sub_al = al[(ys.start - by0):(ys.stop - by0), (xs.start - bx0):(xs.stop - bx0)]
            edge = np.clip((sub_al - gaussian_filter(sub_al, (0, 2.5, 0))) * 2.2, 0, 1)        # the LED along both long edges
            reg = reg * (1 - sub_al) + sub_rgb * sub_al
            reg = reg * (1 - edge * 0.85) + edge * 0.85 * np.array([255, 238, 210], np.float32)
            out[ys, xs] = reg
            # their words back on top
            tm = text_mask(fr[k])
            tx0, ty0, tx1, ty1 = box_at(fit, k, grow=(0.15, 0.10))           # not the old sconce's glass
            tm[int(max(ty0, 0)):int(min(ty1, SH)), int(max(tx0, 0)):int(min(tx1, SW))] = 0
            tm = gaussian_filter(tm, 0.6)[..., None]
            out = out * (1 - tm) + f * tm
            img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).resize((W, H), Image.LANCZOS)
            proc.stdin.write(img.tobytes())
    proc.stdin.close(); proc.wait()
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-i", ref, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", OUT],
                   check=True)
    os.remove(tmp)
    print(os.path.relpath(OUT, ROOT), "done")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         "/tmp/claude-0/-home-user-opencut-classic/f863beaa-1937-5cac-8a95-89d282b7c923/scratchpad/ref10/ref.mp4")
