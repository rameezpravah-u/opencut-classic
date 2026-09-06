"""sources.py — register a real product video as a source: find its colour states automatically.

    python3 sources.py src/14-1.mp4            # prints the amber / red / green / warm segments
    python3 sources.py src/campaign.mp4 --write rubik   # writes states + state_max into presets.json

How: samples the video at 4 fps, keeps the brightest 4% of pixels (the glowing glass), reads their
mean hue and saturation, and labels each sample red / green / amber / warm (low saturation warm white).
Runs of the same label longer than 0.8 s become states; the first run of each colour is what the
mechanisms cut from (products.<key>.states), its length is the cap (state_max).
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 135, 240, 4


def frames(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", path, "-vf", f"fps={FPS},scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    a = np.frombuffer(out, dtype=np.uint8)
    n = a.size // (W * H * 3)
    return a[:n * W * H * 3].reshape((n, H, W, 3)).astype(np.float32) / 255.0


def label(fr):
    lum = fr.max(axis=2)
    mask = lum >= np.percentile(lum, 96)
    px = fr[mask]
    mx, mn = px.max(axis=1), px.min(axis=1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = px[:, 0], px[:, 1], px[:, 2]
    # hue in degrees (0 red, 60 yellow, 120 green)
    d = np.maximum(mx - mn, 1e-6)
    hue = np.where(mx == r, (60 * ((g - b) / d)) % 360, np.where(mx == g, 60 * ((b - r) / d) + 120, 60 * ((r - g) / d) + 240))
    s, h = float(np.median(sat)), float(np.median(hue))
    bright = float(lum.mean())
    if bright < 0.06:
        return "dark", h, s
    if s < 0.35:
        return "warm", h, s
    if h < 22 or h > 330:
        return "red", h, s
    if 22 <= h < 58:
        return "amber", h, s
    if 70 <= h < 180:
        return "green", h, s
    return "other", h, s


def states(path, min_run=0.8):
    fr = frames(path)
    labs = [label(f)[0] for f in fr]
    runs, cur, start = [], None, 0
    for i, l in enumerate(labs + [None]):
        if l != cur:
            if cur is not None and (i - start) / FPS >= min_run:
                runs.append((cur, start / FPS, i / FPS))
            cur, start = l, i
    first = {}
    for l, s, e in runs:
        if l in ("red", "green", "amber", "warm") and l not in first:
            first[l] = (round(s, 2), round(e - s, 2))
    return runs, first, len(fr) / FPS


if __name__ == "__main__":
    path = sys.argv[1]
    runs, first, dur = states(path)
    print(f"{path}: {dur:.1f}s")
    for l, s, e in runs:
        print(f"  {s:6.2f}–{e:6.2f}  {l}")
    print("first run per colour (start, length):", first)
    if "--write" in sys.argv:
        key = sys.argv[sys.argv.index("--write") + 1]
        p = os.path.join(HERE, "presets.json"); d = json.load(open(p, encoding="utf-8"))
        prod = d["products"][key]
        prod.setdefault("sources", {})[os.path.basename(path)] = dict(states={k: v[0] for k, v in first.items()},
                                                                       state_max={k: v[1] for k, v in first.items()}, duration=round(dur, 2))
        json.dump(d, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("written to presets.products.%s.sources" % key)
