#!/usr/bin/env python3
"""render.py — frame-exact video from any HTML sketch (p5.js + p5.brush, Rough.js, Matter.js, Anime.js, PixiJS).

    python3 motion-libs/render.py templates/brush-reveal/index.html out.mp4 --dur 6 \
        --audio brand-reels/audio/music3-design.mp3 --audio-start 0.4 --beats beats.json

The page must define `window.ready` (a Promise, or absent) and `window.renderAt(t)` (seconds), which
draws the frame for time t from scratch and returns (or resolves) when it is done. Nothing in the page may
depend on wall-clock time or on the previous frame, so every frame can be rendered alone (seek-safe).
Libraries are loaded from motion-libs/vendor/ by relative path: the render browser cannot use CDNs.

`--beats` hands the JSON from beats.py to the page as `window.BEATS` (shifted by --audio-start), so a
reveal can be placed on a downbeat instead of by eye (MOTION.md §4).
"""
import argparse, io, json, os, subprocess, sys

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "brand-reels", "festive-ad-cuts"))
from festive_cuts import FF   # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("out")
    ap.add_argument("--dur", type=float, required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--audio")
    ap.add_argument("--audio-start", type=float, default=0.0)
    ap.add_argument("--beats")
    ap.add_argument("--crf", type=int, default=17)
    ap.add_argument("--still", type=float, action="append", help="write a PNG of this time instead of a video")
    a = ap.parse_args()
    w, h = (int(v) for v in a.size.split("x"))
    beats = None
    if a.beats:
        b = json.load(open(a.beats))
        sh = lambda xs: [round(x - a.audio_start, 3) for x in xs if x - a.audio_start >= 0]
        beats = {**b, "beats": sh(b["beats"]), "downbeats": sh(b["downbeats"]), "strong": sh(b["strong"])}
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")    # the session's pre-installed build
        br = p.chromium.launch(executable_path=exe if os.path.exists(exe) else None, args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                     "--ignore-gpu-blocklist", "--allow-file-access-from-files"])
        pg = br.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.add_init_script(f"window.BEATS = {json.dumps(beats)}; window.DUR = {a.dur};")
        pg.on("console", lambda m: print("page:", m.text) if m.type in ("error", "warning") else None)
        pg.goto("file://" + os.path.abspath(a.page))
        pg.wait_for_function("typeof window.renderAt === 'function'", timeout=60000)
        pg.evaluate("() => window.ready || null")
        if a.still:
            for t in a.still:
                pg.evaluate("t => window.renderAt(t)", t)
                out = a.out.replace(".png", f"-{t:05.2f}.png") if len(a.still) > 1 else a.out
                pg.screenshot(path=out)
                print("still", out)
            br.close()
            return
        cmd = [FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(a.fps),
               "-i", "-"]
        if a.audio:
            cmd += ["-ss", f"{a.audio_start:.3f}", "-i", a.audio, "-map", "0:v", "-map", "1:a", "-c:a", "aac",
                    "-b:a", "192k", "-af", f"afade=t=out:st={max(0, a.dur - 0.8):.2f}:d=0.8", "-shortest"]
        cmd += ["-c:v", "libx264", "-crf", str(a.crf), "-preset", "slow", "-pix_fmt", "yuv420p",
                "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-movflags",
                "+faststart", "-t", f"{a.dur:.3f}", a.out]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        n = round(a.dur * a.fps)
        for i in range(n):
            pg.evaluate("t => window.renderAt(t)", i / a.fps)
            im = Image.open(io.BytesIO(pg.screenshot(type="png"))).convert("RGB")
            enc.stdin.write(im.tobytes())
            if i % 30 == 0:
                print(f"frame {i}/{n}", flush=True)
        enc.stdin.close()
        enc.wait()
        br.close()
    print("done", a.out)


if __name__ == "__main__":
    main()
