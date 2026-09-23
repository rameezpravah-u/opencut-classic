#!/usr/bin/env python3
"""Programmatic assertion checks for the ecom-product-video evals.

Usage:  python3 check.py <run_dir>
where <run_dir> contains outputs/ (reel.mp4, NOTES.md, ...).
Writes grading.json into <run_dir>.
"""
import sys, os, re, json, subprocess
import numpy as np
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 4  # sampling rate for all frame measurements


def probe(path):
    """ffmpeg has no ffprobe here, so parse the banner it prints to stderr."""
    out = subprocess.run([FF, "-nostdin", "-i", path], capture_output=True,
                          text=True, stdin=subprocess.DEVNULL).stderr
    info = {"raw": out}
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if m:
        h, mi, s = m.groups()
        info["duration"] = int(h) * 3600 + int(mi) * 60 + float(s)
    m = re.search(r"Video: .*?, (\w+)\(([^)]*)\)?.*?, (\d+)x(\d+)", out)
    if m:
        info["pix_fmt"] = m.group(1)
        info["colour"] = m.group(2)
        info["w"], info["h"] = int(m.group(3)), int(m.group(4))
    else:
        m = re.search(r"Video: .*?, (\d+)x(\d+)", out)
        if m:
            info["w"], info["h"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"Video: (\w+)", out)
    if m:
        info["codec"] = m.group(1)
    return info


def real_duration(path):
    """Decode the whole stream and read the end timestamp.

    The container banner is usually right, but a truncated or mis-muxed file
    can report a length it does not actually play - which is how a dropped
    end card hides. Decoding settles it.
    """
    out = subprocess.run([FF, "-nostdin", "-i", path, "-map", "0:v:0", "-f", "null", "-"],
                         capture_output=True, text=True,
                         stdin=subprocess.DEVNULL, timeout=600).stderr
    ts = re.findall(r"time=(\d+):(\d+):([\d.]+)", out)
    fr = re.findall(r"frame=\s*(\d+)", out)
    d = None
    if ts:
        h, m, sec = ts[-1]
        d = int(h) * 3600 + int(m) * 60 + float(sec)
    return d, (int(fr[-1]) if fr else None)


def frames(path, w=180, fps=4, ss=None, t=None, dims=None):
    """Decode to a small RGB array so we can measure the picture itself.

    The height must come from the file's real aspect ratio - inferring it from
    the byte count picks up false divisors and invents frames that are not there.
    """
    if dims is None:
        info = probe(path)
        dims = (info.get("w"), info.get("h"))
    if not dims[0] or not dims[1]:
        return None
    h = int(round(w * dims[1] / dims[0] / 2)) * 2
    cmd = [FF, "-nostdin", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", str(ss)]
    if t is not None:
        cmd += ["-t", str(t)]
    cmd += ["-i", path, "-vf", f"fps={fps},scale={w}:{h}",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    d = np.frombuffer(subprocess.run(cmd, capture_output=True,
                      stdin=subprocess.DEVNULL, timeout=600).stdout, dtype=np.uint8)
    if d.size < w * h * 3:
        return None
    n = d.size // (w * h * 3)
    return d[:n * w * h * 3].reshape(n, h, w, 3).astype(np.float32)


def luma(f):
    return f[..., 0] * 0.2126 + f[..., 1] * 0.7152 + f[..., 2] * 0.0722


def notes_text(run):
    txt = ""
    for root, _, fs in os.walk(os.path.join(run, "outputs")):
        for fn in fs:
            if fn.lower().endswith((".md", ".txt", ".json", ".py", ".sh")):
                try:
                    txt += open(os.path.join(root, fn), errors="ignore").read() + "\n"
                except OSError:
                    pass
    return txt


# ---------------------------------------------------------------- assertions

def a_vertical_mp4(run, mp4, info, f, txt):
    """Output is a playable 1080x1920 vertical mp4"""
    ok = info.get("w") == 1080 and info.get("h") == 1920 and f is not None
    return ok, f"{info.get('w')}x{info.get('h')}, {len(f) if f is not None else 0} frames decoded"


def a_tonemapped(run, mp4, info, f, txt):
    """Output is tagged bt709, not left on the source's HLG/bt2020 transfer"""
    c = info.get("colour", "")
    bad = "arib-std-b67" in c or "bt2020" in c
    return (not bad), f"colour tags: {c or 'none reported'}"


def a_no_black_frames(run, mp4, info, f, txt):
    """No sustained dead stretch in the body of the reel (fades in/out excluded)"""
    if f is None or len(f) < 8:
        return False, "too few frames to judge"
    skip = int(0.6 * FPS)
    body = f[skip:len(f) - skip]
    if len(body) == 0:
        return False, "body empty after trimming fades"
    per = luma(body).mean(axis=(1, 2))
    run_len = best = 0
    for d in (per < 12):
        run_len = run_len + 1 if d else 0
        best = max(best, run_len)
    worst = best / FPS
    return bool(worst < 0.75), (f"longest dark stretch {worst:.2f}s "
                                f"(min frame luma {per.min():.1f}, mean {per.mean():.1f})")


def a_tail_plays(run, mp4, info, f, txt):
    """The reel plays to its stated end - decoded runtime matches the container"""
    cd, rd = info.get("container_duration"), info.get("duration")
    if not cd or not rd:
        return False, "could not measure duration"
    if f is None or len(f) < 2:
        return False, "no frames"
    drift = rd - cd
    tail_ok = bool(luma(f[-2:]).mean() >= 8)
    ok = abs(drift) <= 0.75 and tail_ok
    return ok, (f"container says {cd:.2f}s, decoded {rd:.2f}s (drift {drift:+.2f}s); "
                f"final frames mean luma {luma(f[-2:]).mean():.1f}")


def a_not_frozen(run, mp4, info, f, txt):
    """The reel actually moves - consecutive frames differ (not a slideshow of one still)"""
    if f is None or len(f) < 4:
        return False, "too few frames"
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2, 3))
    moving = (d > 1.0).mean()
    return bool(moving >= 0.6), f"{moving*100:.0f}% of frame pairs differ by >1/255"


def a_measured_values(run, mp4, info, f, txt):
    """Write-up cites a measured number from the sources, not just adjectives"""
    pats = [r"\blum(inance|a)\b", r"\bmean\s*(luma|luminance|brightness)",
            r"\b\d{3,4}\s*[x×]\s*\d{3,4}\b", r"\bupscal", r"\b\d+(\.\d+)?\s*s(ec|econds)?\b.*\bdur"]
    hits = [p for p in pats if re.search(p, txt, re.I)]
    return len(hits) >= 2, f"matched {len(hits)} of {len(pats)} evidence patterns"


def a_hook_present(run, mp4, info, f, txt):
    """A hook line is stated and justified/scored rather than left implicit"""
    ok = re.search(r"\bhook\b", txt, re.I) is not None
    scored = re.search(r"hook.{0,200}?(\d+\s*/\s*12|gap|truth|pull)", txt, re.I | re.S) is not None
    return bool(ok and scored), f"hook mentioned={bool(ok)}, gated/scored={scored}"


def a_full_width_shot(run, mp4, info, f, txt):
    """At least one shot shows the fixture across the frame, not centre-cropped away"""
    if f is None:
        return False, "no frames"
    best, bf = 0.0, -1
    for i, fr in enumerate(f):
        l = luma(fr)
        thr = max(l.mean() + 1.2 * l.std(), 60)
        cols = (l > thr).any(axis=0)
        if cols.any():
            ext = (np.where(cols)[0][-1] - np.where(cols)[0][0] + 1) / l.shape[1]
            if ext > best:
                best, bf = ext, i
    return bool(best >= 0.80), f"widest lit extent {best*100:.0f}% of frame width (frame {bf})"


def a_no_upscale_blowout(run, mp4, info, f, txt):
    """Low-res sources are identified by pixel size before use"""
    ok = re.search(r"(595|493|1254|1170)\s*(px|x|×)", txt, re.I) or \
         re.search(r"sh0[24][^\n]{0,120}\d{3,4}\s*[x×]\s*\d{3,4}", txt, re.I)
    return bool(ok), "source pixel dimensions cited" if ok else "no source pixel dimensions cited"


def a_duration_matches_ref(run, mp4, info, f, txt):
    """Runtime lands near the 28s reference (24-32s)"""
    d = info.get("duration", 0)
    return bool(24 <= d <= 32), f"decoded runtime {d:.2f}s (container said {info.get('container_duration')})"


def a_assets_inventoried(run, mp4, info, f, txt):
    """Each beat is mapped to a named existing asset file"""
    named = set(re.findall(r"sh0\d[-\w]*", txt))
    return len(named) >= 4, f"named {len(named)} existing assets: {sorted(named)[:8]}"


def a_derived_not_bought(run, mp4, info, f, txt):
    """A missing beat is derived with a free technique, and nothing paid was called"""
    derived = re.search(r"\b(wipe|bloom|blur|screen[- ]composit|crossfade|zoompan|derive)", txt, re.I)
    paid = re.search(r"\b(seedream|seedance|gemini-3-pro-image|elevenlabs|higgsfield)\b.{0,80}\b(generat|render|call)", txt, re.I)
    return bool(derived and not paid), f"derivation technique named={bool(derived)}, paid-generation evidence={bool(paid)}"


def a_no_competitor_footage(run, mp4, info, f, txt):
    """No attempt to reuse the competitor's own video"""
    bad = re.search(r"(download|scrape|rip|reus\w*|re-encod\w*)\b.{0,60}\b(competitor|their (video|reel|footage)|instagram)", txt, re.I)
    return not bool(bad), "no competitor-footage reuse found" if not bad else "references reusing competitor footage"


SUITES = {
    "phone-footage-reel": [a_vertical_mp4, a_tonemapped, a_no_black_frames,
                           a_tail_plays, a_not_frozen, a_measured_values, a_hook_present],
    "wide-product-framing": [a_vertical_mp4, a_no_black_frames, a_not_frozen,
                             a_full_width_shot, a_no_upscale_blowout, a_measured_values],
    "competitor-restyle": [a_vertical_mp4, a_no_black_frames, a_not_frozen,
                           a_duration_matches_ref, a_assets_inventoried,
                           a_derived_not_bought, a_no_competitor_footage],
}


def main(run):
    name = os.path.basename(os.path.dirname(run.rstrip("/")))
    outs = os.path.join(run, "outputs")
    mp4 = None
    for root, _, fs in os.walk(outs):
        for fn in fs:
            if fn.lower().endswith((".mp4", ".mov")):
                p = os.path.join(root, fn)
                if mp4 is None or fn.lower() == "reel.mp4":
                    mp4 = p
    txt = notes_text(run)
    info, f = ({}, None)
    if mp4:
        info = probe(mp4)
        f = frames(mp4, fps=FPS, dims=(info.get("w"), info.get("h")))
        # The container banner routinely disagrees with what actually decodes,
        # which is how a dropped end card hides. Trust the frames.
        info["container_duration"] = info.get("duration")
        rd, nfr = real_duration(mp4)
        info["frame_count"] = nfr
        if rd:
            info["duration"] = rd

    exps = []
    for fn in SUITES.get(name, []):
        if mp4 is None:
            passed, ev = False, "no mp4 produced"
        else:
            try:
                passed, ev = fn(run, mp4, info, f, txt)
            except Exception as e:
                passed, ev = False, f"check errored: {e}"
        exps.append({"text": fn.__doc__.strip(), "passed": bool(passed), "evidence": ev})

    res = {"eval_name": name, "mp4": mp4, "expectations": exps,
           "pass_rate": (sum(e["passed"] for e in exps) / len(exps)) if exps else 0.0}
    with open(os.path.join(run, "grading.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"{name:22s} {os.path.basename(run.rstrip('/')):14s} "
          f"{sum(e['passed'] for e in exps)}/{len(exps)}")
    for e in exps:
        print(f"   {'PASS' if e['passed'] else 'FAIL'}  {e['text']}\n         {e['evidence']}")
    return res


if __name__ == "__main__":
    main(sys.argv[1])
