#!/usr/bin/env python3
"""clip_triage.py: look at every clip the owner sends, whole and in its true orientation, and score how sharp each
moment is, before choosing a single shot.

Why (29 Oct 2026): ten circular-hole clips were judged from a contact sheet whose tiles were squashed middle strips of
vertical frames. Six clips read as "blank wall" and were skipped; they held the sharpest shots (the light switched
off, 4K flame grain). The reel was built on the two softest tilts instead. The owner: "of all the videos I sent you,
you worked on the most blurred".

For each clip: duration, size, fps, and an 8-frame strip at the clip's displayed aspect (iPhone rotation applied,
HLG tone-mapped), plus sharpness per 0.5 s (variance of the Laplacian on a 540-wide grey frame; compare clips of the
same subject: lit holes and plain walls score low everywhere, a painting scores high). The sheet is one JPEG; the
table prints the best window of each clip.

    python3 system/clip_triage.py <clip or folder> [...] --out triage.jpg
"""
import argparse, glob, json, os, subprocess

import numpy as np
from PIL import Image, ImageDraw

FF = "/usr/bin/ffmpeg" if os.path.exists("/usr/bin/ffmpeg") else "ffmpeg"
TM = ("zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=tv,format=yuv420p")


def probe(path):
    out = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                     "stream=width,height,r_frame_rate,color_transfer:stream_side_data=rotation:"
                                     "format=duration", "-of", "json", path], capture_output=True, text=True).stdout)
    st = out["streams"][0]
    rot = 0
    for sd in st.get("side_data_list", []) or []:
        rot = int(sd.get("rotation", 0) or 0)
    w, h = st["width"], st["height"]
    if abs(rot) == 90:
        w, h = h, w
    n, d = st["r_frame_rate"].split("/")
    hdr = st.get("color_transfer") in ("arib-std-b67", "smpte2084")
    return dict(w=w, h=h, fps=float(n) / float(d), dur=float(out["format"]["duration"]), hdr=hdr)


def frames(path, info, fps, width):
    h = round(width * info["h"] / info["w"] / 2) * 2
    vf = (TM + "," if info["hdr"] else "") + f"fps={fps},scale={width}:{h}"
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, width, 3)


def sharpness(fr):
    g = fr.astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    lap = g[1:-1, 1:-1] * 4 - g[:-2, 1:-1] - g[2:, 1:-1] - g[1:-1, :-2] - g[1:-1, 2:]
    return float(lap.var())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--out", default="triage.jpg")
    a = ap.parse_args()
    clips = []
    for p in a.paths:
        clips += sorted(glob.glob(os.path.join(p, "*"))) if os.path.isdir(p) else [p]
    clips = [c for c in clips if c.lower().endswith((".mov", ".mp4", ".m4v"))]
    tw, rows = 200, []
    for c in clips:
        info = probe(c)
        fr = frames(c, info, 2, 540)                                  # 2 fps for scores
        sc = [sharpness(f) for f in fr]
        th = round(tw * info["h"] / info["w"])
        idx = np.linspace(0, len(fr) - 1, 8).round().astype(int)
        strip = Image.new("RGB", (tw * 8, th + 22), (20, 20, 20))
        for k, i in enumerate(idx):
            im = Image.fromarray(fr[i]).resize((tw, th))
            strip.paste(im, (k * tw, 22))
            ImageDraw.Draw(strip).text((k * tw + 4, 26), f"{i / 2:.1f}s  {sc[i]:.0f}", fill=(255, 220, 0))
        best = int(np.argmax(sc))
        name = os.path.basename(c)
        ImageDraw.Draw(strip).text((4, 4), f"{name}  {info['w']}x{info['h']} {info['fps']:.0f}fps {info['dur']:.1f}s"
                                           f"{'  HDR' if info['hdr'] else ''}  sharpest {best / 2:.1f}s ({sc[best]:.0f})",
                                   fill=(255, 255, 255))
        rows.append(strip)
        print(f"{name:28s} {info['w']}x{info['h']} {info['fps']:5.1f}fps {info['dur']:5.1f}s  "
              f"sharpness median {np.median(sc):5.0f}  best {sc[best]:5.0f} at {best / 2:.1f}s  "
              + " ".join(f"{s:.0f}" for s in sc))
    sheet = Image.new("RGB", (max(r.width for r in rows), sum(r.height for r in rows)), (20, 20, 20))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(a.out, quality=85)
    print("sheet", a.out)


if __name__ == "__main__":
    main()
