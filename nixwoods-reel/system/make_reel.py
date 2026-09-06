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
import hooks as HK
from datetime import date
from PIL import Image

PRESETS = MX.PRESETS


def product_root(key):
    """asset folder for a product, from presets.json → products.<key>.root (relative to nixwoods-reel/)"""
    rel = PRESETS["products"].get(key, {}).get("root")
    if not rel:
        raise SystemExit(f"product {key!r} has no 'root' in presets.json and no --root was given")
    return os.path.abspath(os.path.join(os.path.dirname(HERE), rel))


def _strings(v, label):
    if isinstance(v, str):
        yield label, v
    elif isinstance(v, list):
        for i, item in enumerate(v):
            yield from _strings(item, f"{label}[{i}]")
    elif isinstance(v, dict):
        for k, vv in v.items():
            yield from _strings(vv, f"{label}.{k}")


def lint(brief, warn=None):
    """brand-voice and readability checks on every copy string; trademark hits go to warn (ads only)"""
    problems = []
    warn = warn if warn is not None else []
    banned = set(PRESETS["banned_words"])
    maxw = PRESETS["sizes"]["max_words_per_screen"]
    for label, s in _strings(brief.get("copy", {}), "copy"):
        words = re.findall(r"[a-zA-Z']+", s.lower())
        for w in words:
            if w in banned:
                problems.append(f"{label}: banned word '{w}' in {s!r}")
        if len(words) > maxw and not label.endswith(".quote"):
            problems.append(f"{label}: {len(words)} words (max {maxw}) in {s!r}")
        for term in HK.trademark_hits(s):
            if label != "copy.name":
                warn.append(f"{label}: trademark term '{term}' in {s!r} — ad cuts use copy.name_ad")
    return problems


def preflight(brief, reel, warns):
    """the Ads Engine §7 six checks, with everything a script can verify filled in"""
    E = MX.PRESETS["engine"]
    c = brief.get("copy", {})
    hook = c.get("hook") or (brief.get("vo_lines") or [[0, 0, ""]])[0][2]
    hook = " ".join(hook) if isinstance(hook, list) else hook
    hs = HK.score_hook(hook, brief.get("product", "rubik")) if hook else None
    uses_ai = any("hf/" in s["path"].replace(os.sep, "/") for s in reel.shots)
    text = " ".join(s for _, s in _strings(c, "copy"))
    rows = [
        dict(check="rules · at least two colours shown", ok=len(reel.colours) >= 2, detail=", ".join(reel.colours)),
        dict(check="rules · no dispatch-time claim while backlogged", ok=not re.search(r"\b(ships?|dispatch\w*|deliver\w*)\b.*\b\d+\s*(days?|hrs?|hours?)", text.lower()), detail="brief.copy.delivery is a claim: confirm the backlog first" if "deliver" in text.lower() else ""),
        dict(check="facts · banned words / trademark / numbers in PDP facts", ok=not [w for w in warns if "trademark" in w] and (hs["gates"]["truth"] if hs else True), detail="; ".join(w for w in warns if "trademark" in w) or (f"hook truth gate {'pass' if hs and hs['gates']['truth'] else 'FAIL'}" if hs else "")),
        dict(check="landing = the product shown, .nw-pdp template, stock visible", ok=None, detail="manual"),
        dict(check="visual confirmation (watch the mp4, not the sheet)", ok=None, detail="manual"),
        dict(check="named control in the same ad set", ok=None, detail=E["controls"].get(brief.get("product", "rubik"), {}).get("creative_id", "none on record")),
        dict(check="kill threshold written on the ad", ok=None, detail=E["kill_threshold"]),
        dict(check="AI disclosure ticked in Ads Manager", ok=(None if uses_ai else True), detail="Higgsfield frames in this cut → tick by hand" if uses_ai else "no generated frames"),
        dict(check="hook on screen by 0.3 s, holds 1.2 s; all text in the safe zone", ok=not [w for w in warns if "hook" in w or "safe" in w], detail="; ".join(w for w in warns if "hook" in w or "safe" in w)),
        dict(check="length · 25–30 s cut exists for ads (Medium bucket 4.54x vs 0.98x Short)", ok=(reel.duration >= 25) or None, detail=f"{reel.duration:.1f} s" + ("" if reel.duration >= 25 else " — render again with \"stretch\" for the ad cut")),
    ]
    short = {"rubik": "Rubiks"}.get(brief.get("product", "rubik"), brief.get("product", "").title())
    aud = {"genz": "GenZ", "3040": "30-40", "aesthetic": "Broad", "broad": "Broad", "design": "Design", "festive": "Festive", "ugc": "Broad", "social": "Broad"}.get(brief.get("style", "broad"), "Broad")
    ad_name = E["naming"].format(Product=short, Audience=aud, Objective="Sales", **{"Launch date": date.today().strftime("%b%d")})
    return dict(ad_name=ad_name, hook_score=hs, uses_generated_frames=uses_ai, colours=reel.colours,
                hypothesis=[h for h, v in E["hypotheses"].items() if brief.get("name") in v.get("briefs", [])],
                category_focus=E["category_focus"]["rule"], rows=rows)


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
    ap.add_argument("--root", default=None, help="asset root; defaults to nixwoods-reel/<products.<key>.root> from presets.json, so it is normally not needed")
    ap.add_argument("--out", default=None, help="output dir (default <root>/out/system)")
    ap.add_argument("--audio", default="both", choices=["music", "clean", "both"])
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--force", action="store_true", help="render even if the copy lint fails")
    ap.add_argument("--dry", action="store_true", help="build + checks only, no render")
    ap.add_argument("--rank", action="store_true", help="brief is a directory: rank its briefs by tag index × hook score (Growth System layer 3 order)")
    ap.add_argument("--all", action="store_true", help="brief is a directory: render every brief in it and print a summary table")
    a = ap.parse_args()

    if a.all:
        import subprocess as sp
        table = []
        for f in sorted(os.listdir(a.brief)):
            if not f.endswith(".json"):
                continue
            cmd = [sys.executable, os.path.abspath(__file__), os.path.join(a.brief, f), "--audio", a.audio] + (["--root", a.root] if a.root else []) + (["--out", a.out] if a.out else []) + (["--dry"] if a.dry else []) + (["--no-sheet"] if a.no_sheet else [])
            r = sp.run(cmd, capture_output=True, text=True)
            out = r.stdout + r.stderr
            name = f[:-5]
            hook = re.search(r"HOOK (\d+)/12", out); pre = re.findall(r"(✓|✗|□) ", out.split("PREFLIGHT")[-1]) if "PREFLIGHT" in out else []
            dur = re.search(r"built \S+: ([\d.]+)s", out)
            status = "ok" if r.returncode == 0 else "FAILED: " + out.strip().splitlines()[-1][:70]
            table.append((name, dur.group(1) if dur else "-", hook.group(1) if hook else "-", pre.count("✓"), pre.count("✗"), pre.count("□"), len(re.findall(r"^CHECK", out, re.M)), status))
            print(f"{name:26s} {table[-1][1]:>6}s hook {table[-1][2]:>2}/12  preflight ✓{table[-1][3]} ✗{table[-1][4]} □{table[-1][5]}  checks {table[-1][6]}  {status}", flush=True)
        return

    if a.rank:
        E = MX.PRESETS["engine"]; idx = E["tag_index"]
        rows = []
        for f in sorted(os.listdir(a.brief)):
            if not f.endswith(".json"):
                continue
            b = json.load(open(os.path.join(a.brief, f), encoding="utf-8"))
            hook = b.get("copy", {}).get("hook") or ""
            hs = HK.score_hook(hook, b.get("product", "rubik")) if hook else None
            tag = 1.0
            for t in b.get("tags", []):
                tag *= float(idx.get(t, 1.0))
            score = (hs["score"] if hs else 6) * tag
            rows.append((score, b["name"], b["mechanism"], b.get("style", ""), ",".join(b.get("tags", [])), hs["score"] if hs else "-", "".join("✓" if v else "✗" for v in hs["gates"].values()) if hs else "---", hook))
        rows.sort(key=lambda r: -r[0])
        print(f"{'order':>6} {'brief':22s} {'mechanism':14s} {'style':9s} {'tags':28s} {'hook':>4} gates  hook line")
        for r in rows:
            print(f"{r[0]:6.1f} {r[1]:22s} {r[2]:14s} {r[3]:9s} {r[4]:28s} {str(r[5]):>4} {r[6]}    {r[7]}")
        return

    brief = json.load(open(a.brief, encoding="utf-8"))
    root = os.path.abspath(a.root) if a.root else product_root(brief.get("product", "rubik"))
    out = os.path.abspath(a.out or os.path.join(root, "out", "system"))
    os.makedirs(out, exist_ok=True)

    lint_warns = []
    problems = lint(brief, lint_warns)
    for p in problems:
        print("LINT", p)
    for w in lint_warns:
        print("WARN", w)
    if problems and not a.force:
        raise SystemExit("copy lint failed (use --force to render anyway)")

    t0 = time.time()
    reel = MX.build(brief, root, out)
    warns = check_cues(reel)
    for w in warns:
        print("CHECK", w)
    pf = preflight(brief, reel, warns + lint_warns)
    if pf["hook_score"]:
        h = pf["hook_score"]; g = "".join("✓" if v else "✗" for v in h["gates"].values())
        print(f"HOOK {h['score']}/12 gates gap/truth/pull {g} · {h['hook']!r}")
    print(f"PREFLIGHT {pf['ad_name']} · colours {','.join(reel.colours)} · " + " · ".join(f"{'✓' if r['ok'] else '✗' if r['ok'] is False else '□'} {r['check'].split(' ·')[0]}" for r in pf["rows"]))
    tl = dict(name=reel.name, mechanism=brief["mechanism"], style=brief.get("style", "broad"), duration=reel.duration,
              shots=[dict(kind=s["kind"], src=os.path.relpath(s["path"], root) if s["path"].startswith(root) else s["path"],
                          ss=round(s["ss"], 3), start=round(s["start"], 3), end=round(s["end"], 3),
                          xfade=s["xfade"], cam=s["kw"].get("cam")) for s in reel.shots],
              cues=[dict(png=os.path.basename(c[0]), start=round(c[1], 3), end=round(c[2], 3)) for c in reel.cues],
              audio=[dict(src=os.path.basename(s["path"]), start=s["start"], gain=s["gain"], music=s["music"]) for s in reel.audio],
              lint=problems, warnings=lint_warns, checks=warns, tags=brief.get("tags", []), preflight=pf)
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
        # JPEG, not PNG: a review sheet is a thumbnail, and PNG sheets were 3-5 MB each in git
        rk.contact_sheet(main_out, os.path.join(out, f"{reel.name}-sheet.jpg"), fps=2, cols=8, rows=rows, scale=200)
    print("done", *outputs)


if __name__ == "__main__":
    main()
