#!/usr/bin/env python3
"""make_reel.py — brief.json → reel (music + clean), cover, contact sheet, timeline.

    python3 make_reel.py briefs/T1-transformation.json --root <dir with src/ audio/ hf/> [--audio music|clean|both] [--no-sheet]

Steps: lint the copy (banned words, ≤12 words per screen) → build the mechanism → check every text
layer against the safe zone and the hook rule (on screen by 0.3 s, holds ≥1.2 s) → render → cover +
contact sheet → out/<name>-timeline.json for review.
"""
import argparse, json, math, os, re, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "rubik-reels"))
import mechanisms as MX
import reelkit as rk
from PIL import Image

PRESETS = MX.PRESETS


def _strings(v, label):
    if isinstance(v, str):
        yield label, v
    elif isinstance(v, list):
        for i, item in enumerate(v):
            yield from _strings(item, f"{label}[{i}]")
    elif isinstance(v, dict):
        for k, vv in v.items():
            yield from _strings(vv, f"{label}.{k}")


def lint(brief):
    """brand-voice and readability checks on every copy string"""
    problems = []
    banned = set(PRESETS["banned_words"])
    maxw = PRESETS["sizes"]["max_words_per_screen"]
    for label, s in _strings(brief.get("copy", {}), "copy"):
        words = re.findall(r"[a-zA-Z']+", s.lower())
        for w in words:
            if w in banned:
                problems.append(f"{label}: banned word '{w}' in {s!r}")
        if len(words) > maxw and not label.endswith(".quote"):
            problems.append(f"{label}: {len(words)} words (max {maxw}) in {s!r}")
    return problems


def check_cues(reel):
    """safe-zone + hook timing on the rendered text layers"""
    warn = []
    safe = rk.SAFE
    for p, s, e, fi, fo, rise in reel.cues:
        bb = Image.open(p).getbbox()
        if not bb:
            continue
        x0, y0, x1, y1 = bb
        tol = 12   # drop-shadow bleed
        if y0 < safe["top"] - tol or y1 > safe["bottom"] + tol or x0 < safe["left"] - tol or x1 > safe["right"] + tol:
            warn.append(f"{os.path.basename(p)} {s:.2f}–{e:.2f}s bbox {bb} leaves the safe area (x {safe['left']}–{safe['right']}, y {safe['top']}–{safe['bottom']})")
    hook = PRESETS["hook"]
    first = min((c[1] for c in reel.cues), default=None)
    if first is None or first > hook["on_screen_by"] + 0.01:
        warn.append(f"hook text starts at {first}s (rule: ≤{hook['on_screen_by']}s)")
    else:
        # kinetic hooks chain short cues; measure the span of everything that starts in the first 1.5 s
        hold = max(c[2] for c in reel.cues if c[1] <= first + 1.5) - first
        if hold < hook["hold_at_least"]:
            warn.append(f"hook holds {hold:.2f}s (rule: ≥{hook['hold_at_least']}s)")
    return warn


def cover(video, out_jpg, t):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video,
                    "-frames:v", "1", "-q:v", "2", out_jpg], check=True)
    return out_jpg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--root", default=".", help="asset root: paths in the brief/presets are relative to it")
    ap.add_argument("--out", default=None, help="output dir (default <root>/out/system)")
    ap.add_argument("--audio", default="both", choices=["music", "clean", "both"])
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--force", action="store_true", help="render even if the copy lint fails")
    ap.add_argument("--dry", action="store_true", help="build + checks only, no render")
    a = ap.parse_args()

    brief = json.load(open(a.brief, encoding="utf-8"))
    root = os.path.abspath(a.root)
    out = os.path.abspath(a.out or os.path.join(root, "out", "system"))
    os.makedirs(out, exist_ok=True)

    problems = lint(brief)
    for p in problems:
        print("LINT", p)
    if problems and not a.force:
        raise SystemExit("copy lint failed (use --force to render anyway)")

    t0 = time.time()
    reel = MX.build(brief, root, out)
    warns = check_cues(reel)
    for w in warns:
        print("CHECK", w)
    tl = dict(name=reel.name, mechanism=brief["mechanism"], style=brief.get("style", "broad"), duration=reel.duration,
              shots=[dict(kind=s["kind"], src=os.path.relpath(s["path"], root) if s["path"].startswith(root) else s["path"],
                          ss=round(s["ss"], 3), start=round(s["start"], 3), end=round(s["end"], 3),
                          xfade=s["xfade"], cam=s["kw"].get("cam")) for s in reel.shots],
              cues=[dict(png=os.path.basename(c[0]), start=round(c[1], 3), end=round(c[2], 3)) for c in reel.cues],
              audio=[dict(src=os.path.basename(s["path"]), start=s["start"], gain=s["gain"], music=s["music"]) for s in reel.audio],
              lint=problems, checks=warns)
    json.dump(tl, open(os.path.join(out, f"{reel.name}-timeline.json"), "w"), indent=1, ensure_ascii=False)
    print(f"built {reel.name}: {reel.duration:.2f}s, {len(reel.shots)} shots, {len(reel.cues)} text cues, {len(reel.audio)} audio")
    if a.dry:
        return

    outputs = []
    if a.audio in ("music", "both"):
        outputs.append(reel.render("-music", with_music=True))
        print(f"rendered {outputs[-1]}  {time.time() - t0:.0f}s", flush=True)
    if a.audio in ("clean", "both"):
        outputs.append(reel.render("-clean", with_music=False))
        print(f"rendered {outputs[-1]}  {time.time() - t0:.0f}s", flush=True)
    main_out = outputs[0]
    cover(main_out, os.path.join(out, f"{reel.name}-cover.jpg"), brief.get("cover_t", 1.0))
    if not a.no_sheet:
        rows = max(1, math.ceil(reel.duration * 2 / 8))
        rk.contact_sheet(main_out, os.path.join(out, f"{reel.name}-sheet.png"), fps=2, cols=8, rows=rows, scale=200)
    print("done", *outputs)


if __name__ == "__main__":
    main()
