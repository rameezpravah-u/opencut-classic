#!/usr/bin/env python3
"""place.py: find every moment in a finished reel that needs a sound, place one on the exact frame at the right level
against the music, and mix it in. Our own "Real SFX" (the tool in instagram.com/reel/De4XVvXPTWY is not published).

    python3 system/sfx/place.py in.mp4 out.mp4 [--cues cues.json] [--no-auto-cuts] [--style calm|crisp] [--sheet cues.tsv]

Cues come from two places:
- auto: hard cuts, found by frame difference (every cut gets a whoosh whose peak lands just after it);
- cues.json, written by the reel's own script, which knows when a caption or a lamp lands:
  [{"t": 0.75, "kind": "set"}, {"t": 2.3, "kind": "text"}, ...]. kinds: cut, text, set, light, end, tap, zoom.

Taste (FREE-TOOLS.md "Sound"):
- a cut -> a short whoosh, peak 37 ms after the cut;
- text on -> a soft rounded pop, onset 30 ms after the text lands;
- a lamp set down -> a real wood knock, 40 ms before contact (the ear expects the knock with the touch);
- a light coming on -> the lamp-switch click, 11 ms early, with a low soft bloom under it;
- the end card -> one warm mallet note over a sub hit;
- a tap -> a tick, 60 ms early.
The offsets and the levels over the music (3-10 dB, measured on the loudest 50 ms of the effect against the music's
median level in the second before it) are the medians Earshot (MIT, github.com/Leonxlnx/earshot) published from
professional launch films; runs keep a minimum gap (pops 114 ms, ticks 66 ms).

Sounds: synthesized here (pop, tick, sub hit, mallet, air whoosh) or real CC0 recordings fetched once from Openverse
(system/sfx/openverse.py: wood knock, lamp switch, whoosh). Nothing from a reference creator.
"""
import argparse, json, os, subprocess, sys, wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import openverse  # noqa: E402

SR = 48000
FF = "ffmpeg"
# role: (offset of the sound's anchor from the cue in s, anchor = "onset" or "peak", level over the bed in dB, min gap s)
ROLES = {
    "cut":   (+0.037, "peak", 4.0, 0.30),
    "text":  (+0.030, "onset", 6.0, 0.114),
    "set":   (-0.040, "onset", 7.0, 0.20),
    "light": (-0.011, "onset", 6.5, 0.30),
    "end":   (+0.000, "onset", 8.0, 1.00),
    "tap":   (-0.060, "onset", 5.0, 0.066),
    "zoom":  (+0.000, "onset", 5.0, 0.20),
}
# real recordings (CC0, Openverse ids) for the roles where a recording beats synthesis
REAL = {
    "set": "47aa1d50-ccbd-4743-9228-cf749f21d5d2",     # "Wood Knock Clean Close" (Geoff-Bremner-Audio, CC0)
    "light": "97e34a23-3c7d-4b0b-94f5-db728a7ace68",   # "StandardLamp-Switch" (Mindloop, CC0)
    "cut": "f1dc6045-7965-41de-87f8-4731d2583fd2",     # "Swosh swoosh whoosh air sound" (qubodup, CC0)
}


# ------------------------------------------------------------------------------------------------ sounds
def _env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay)


def synth(role, rng):
    if role == "text":                                     # a rounded mid pop: a falling sine, 0.15 s
        n = int(0.15 * SR)
        t = np.arange(n) / SR
        f = 820 * np.exp(-t / 0.05) + 560
        y = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.045)
        return y + rng.standard_normal(n) * _env(n, 0.0005, 0.004) * 0.05
    if role == "tap":                                      # a tick
        n = int(0.05 * SR)
        y = rng.standard_normal(n) * _env(n, 0.0003, 0.003)
        return np.convolve(y, [1, -0.6], "same") + np.sin(2 * np.pi * 2600 * np.arange(n) / SR) * _env(n, 0.0005, 0.006) * 0.4
    if role == "end":                                      # a sub hit under a warm mallet note (marimba-like partials)
        n = int(1.2 * SR)
        t = np.arange(n) / SR
        sub = np.sin(2 * np.pi * (48 + 30 * np.exp(-t / 0.05)) * t) * _env(n, 0.003, 0.35)
        f0 = 523.25
        mal = sum(a * np.sin(2 * np.pi * f0 * k * t) * np.exp(-t / d) for k, a, d in
                  [(1, 1.0, 0.45), (3.93, 0.25, 0.12), (9.2, 0.08, 0.04)]) * np.minimum(1, t / 0.002)
        return sub * 0.9 + mal * 0.45
    if role == "zoom":                                     # a two-stage shutter click
        y = np.zeros(int(0.12 * SR))
        for t0, a in [(0.0, 1.0), (0.055, 0.7)]:
            i = int(t0 * SR)
            m = int(0.02 * SR)
            y[i:i + m] += rng.standard_normal(m) * _env(m, 0.0003, 0.004) * a
        return y
    if role == "set":                                      # a wood knock: a short noise strike into damped wood modes
        n = int(0.22 * SR)
        t = np.arange(n) / SR
        modes = sum(a * np.sin(2 * np.pi * f * t + ph) * np.exp(-t / d) for f, a, d, ph in
                    [(190, 1.0, 0.045, 0.0), (430, 0.7, 0.030, 0.6), (780, 0.45, 0.018, 1.1), (1350, 0.25, 0.010, 0.3)])
        strike = np.convolve(rng.standard_normal(n), np.ones(6) / 6, "same") * _env(n, 0.0004, 0.003)
        return modes * np.minimum(1, t / 0.0008) + strike * 0.6
    if role == "switch":                                   # a lamp's rocker switch: two bright clicks 9 ms apart
        n = int(0.06 * SR)
        y = np.zeros(n)
        for t0, amp in [(0.0, 1.0), (0.009, 0.55)]:
            i = int(t0 * SR)
            m = int(0.015 * SR)
            k = rng.standard_normal(m) * _env(m, 0.0002, 0.0015)
            y[i:i + m] += np.convolve(k, [1, -0.9], "same") * amp
            y[i:i + m] += np.sin(2 * np.pi * 3100 * np.arange(m) / SR) * _env(m, 0.0002, 0.003) * 0.5 * amp
        return y
    if role == "light":                                    # the bloom under the switch click: a soft low swell
        n = int(0.6 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * 110 * t) * np.minimum(1, t / 0.12) * np.exp(-t / 0.25) * 0.5
    if role == "cut":                                      # an air whoosh: noise swept low -> high -> low, peak at 0.24 s
        from scipy.signal import butter, sosfilt
        n = int(0.5 * SR)
        t = np.arange(n) / SR
        noise = rng.standard_normal(n)
        bands = [sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), noise)
                 for lo, hi in [(250, 700), (700, 1800), (1800, 4500), (4500, 9000)]]
        pos = np.clip(1 - np.abs(t - 0.24) / 0.24, 0, 1)        # 0 at the ends, 1 at the peak: the sweep's height
        w = [np.clip(1 - np.abs(pos * 3 - k), 0, 1) for k in range(4)]
        y = sum(wk * bk for wk, bk in zip(w, bands))
        env = np.where(t < 0.24, (t / 0.24) ** 2.2, np.exp(-(t - 0.24) / 0.07))   # slow rise, quick fall
        return y * env
    raise KeyError(role)


def load_audio(path, start=0.0, dur=None):
    cmd = [FF, "-v", "error", "-ss", f"{start:.3f}", "-i", path]
    if dur:
        cmd += ["-t", f"{dur:.3f}"]
    raw = subprocess.run(cmd + ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def real(role):
    """the real CC0 recording for a role, trimmed to its sound and peak-normalized; None when offline"""
    try:
        path = openverse.get(REAL[role])
    except (Exception, SystemExit) as e:
        print(f"place: no real {role} recording here ({e}); using the one made in code", file=sys.stderr)
        return None
    y = load_audio(path).mean(1)
    env = np.abs(y)
    on = int(np.argmax(env > env.max() * 0.08))
    y = y[max(0, on - int(0.004 * SR)):]
    y = y[:int(0.9 * SR)]
    fade = np.ones(len(y))
    k = min(len(y), int(0.08 * SR))
    fade[-k:] = np.linspace(1, 0, k)
    return y * fade / (np.abs(y).max() + 1e-9)


# Earshot's bank (github.com/Leonxlnx/earshot, MIT; installed by .claude/skills/earshot/setup.sh): sounds made in code
# by its forge, measured and audited. Used first when installed; `--sounds synth` forces our own.
EARSHOT = os.environ.get("EARSHOT_BIN", os.path.expanduser("~/.cache/earshot/.venv/bin/earshot"))
EARSHOT_IDS = {
    "calm":  {"cut": ["swipe/glide"], "text": ["ui_pop/soft"], "set": ["knock/wood"], "light": ["fit/snap/switch_flip"],
              "end": ["mallet/marimba", "cut_hit/sub"], "tap": ["knock/desk"], "zoom": ["shutter/quick"]},
    "crisp": {"cut": ["whoosh_fast/tight"], "text": ["ui_pop/step"], "set": ["knock/wood"],
              "light": ["fit/snap/switch_flip"], "end": ["mallet/glock", "cut_hit/punch"], "tap": ["knock/snap"],
              "zoom": ["shutter/dslr"]},
}
EARSHOT_CACHE = os.path.expanduser("~/.cache/nixwoods-sfx/earshot")


def earshot_take(sid):
    """render one bank sound by id (cached); None when Earshot is not installed or the render fails"""
    if not os.path.exists(EARSHOT):
        return None
    os.makedirs(EARSHOT_CACHE, exist_ok=True)
    path = os.path.join(EARSHOT_CACHE, sid.replace("/", "__") + ".wav")
    if not os.path.exists(path):
        r = subprocess.run([EARSHOT, "sfx", "render", sid, "-o", path], capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            print(f"place: earshot could not render {sid}: {r.stderr.strip()[:200]}", file=sys.stderr)
            return None
    return load_audio(path).mean(1)


def earshot_role(style, role):
    parts = [earshot_take(sid) for sid in EARSHOT_IDS[style][role]]
    if not parts or any(p is None for p in parts):
        return None
    z = np.zeros(max(len(p) for p in parts))
    for k, p in enumerate(parts):                         # layers: the first leads, the rest sit under it
        z[:len(p)] += p / (np.abs(p).max() + 1e-9) * (1.0 if k == 0 else 0.7)
    return z


def bank(style, rng, source="auto"):
    out = {}
    for role in ROLES:
        y = earshot_role(style, role) if source in ("auto", "earshot") else None
        if y is not None:
            if role == "light":                            # the switch with our soft bloom under it
                bloom = synth("light", rng)
                z = np.zeros(max(len(y), len(bloom)))
                z[:len(y)] += y / (np.abs(y).max() + 1e-9)
                z[:len(bloom)] += bloom * 0.35
                y = z
            out[role] = (y / (np.abs(y).max() + 1e-9)).astype(np.float32)
            continue
        if source == "earshot":
            raise SystemExit(f"place: Earshot is not installed (bash .claude/skills/earshot/setup.sh) or {role} failed")
        y = real(role) if role in REAL else None
        if role == "light":                                # the click (real, or made here) with a soft bloom under it
            if y is None:
                y = synth("switch", rng)
            bloom = synth("light", rng)
            z = np.zeros(max(len(y), len(bloom)))
            z[:len(y)] += y
            z[:len(bloom)] += bloom * 0.35
            y = z
        if y is None:
            y = synth(role, rng)
        y = y / (np.abs(y).max() + 1e-9)
        if style == "calm" and role in ("cut", "zoom"):
            y = y * 0.7
        out[role] = y.astype(np.float32)
    return out


def anchor_index(y, how):
    env = np.convolve(np.abs(y), np.ones(int(0.005 * SR)) / int(0.005 * SR), "same")
    if how == "peak":
        return int(np.argmax(env))
    return int(np.argmax(env > env.max() * 0.1))


# ------------------------------------------------------------------------------------------------ cues
def find_cuts(video, thresh=0.42):
    """hard cuts: big jumps in the 64x36 grey thumbnail between consecutive frames"""
    p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                        "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip().split("/")
    fps = float(p[0]) / float(p[1] if len(p) > 1 else 1)
    raw = subprocess.run([FF, "-v", "error", "-i", video, "-vf", "scale=64:36,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 36, 64).astype(np.float32) / 255
    d = np.abs(np.diff(fr, axis=0)).mean((1, 2))
    med = np.median(d) + 1e-4
    cuts = [(i + 1) / fps for i, v in enumerate(d) if v > max(thresh * d.max(), 6 * med) and v > 0.06]
    out = []
    for c in cuts:                                         # one cut per transition
        if not out or c - out[-1] > 0.25:
            out.append(c)
    return out, fps


def bed_level_db(bed, t):
    """the music's median level (dB, 50 ms windows) in the second before t"""
    a, b = int(max(0, t - 1.0) * SR), int(max(0.05, t) * SR)
    seg = bed[a:b].mean(1)
    if len(seg) < SR // 20:
        return -40.0
    w = SR // 20
    rms = [np.sqrt(np.mean(seg[i:i + w] ** 2)) + 1e-6 for i in range(0, len(seg) - w + 1, w)]
    return float(20 * np.log10(np.median(rms)))


def peak50_db(y):
    w = SR // 20
    c = np.convolve(y ** 2, np.ones(w) / w, "same")
    return float(10 * np.log10(c.max() + 1e-12))


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("out")
    ap.add_argument("--cues")
    ap.add_argument("--no-auto-cuts", action="store_true")
    ap.add_argument("--style", default="calm", choices=["calm", "crisp"])
    ap.add_argument("--sheet")
    ap.add_argument("--gain", type=float, default=0.0, help="dB on every effect")
    ap.add_argument("--master", type=float, help="master the result to this integrated loudness (e.g. -14 LUFS for "
                    "web, Earshot's reference median), true peak at most -1 dBTP; two-pass linear, no pumping")
    ap.add_argument("--sounds", default="auto", choices=["auto", "earshot", "synth"],
                    help="auto: Earshot's bank when installed, else real CC0 recordings or our synthesis")
    a = ap.parse_args()
    rng = np.random.default_rng(7)
    cues = []
    if not a.no_auto_cuts:
        cuts, fps = find_cuts(a.video)
        cues += [{"t": c, "kind": "cut", "src": "auto"} for c in cuts]
    else:
        fps = 30.0
    if a.cues:
        cues += [dict(c, src="script") for c in json.load(open(a.cues))]
    for c in cues:                                         # every cue on the exact frame
        c["t"] = round(c["t"] * fps) / fps
    cues.sort(key=lambda c: c["t"])
    bed = load_audio(a.video)
    n = len(bed)
    sounds = bank(a.style, rng, a.sounds)
    mix = bed.copy()
    last = {}
    rows = []
    for c in cues:
        role = c["kind"]
        off, how, over, gap = ROLES[role]
        if c["t"] - last.get(role, -9) < gap:
            rows.append((c, None, "skipped: closer than the role's minimum gap"))
            continue
        last[role] = c["t"]
        y = sounds[role]
        level = bed_level_db(bed, c["t"]) + over + a.gain
        g = 10 ** ((level - peak50_db(y)) / 20)
        start = int((c["t"] + off) * SR) - anchor_index(y, how)
        s0, s1 = max(0, start), min(n, start + len(y))
        if s1 <= s0:
            continue
        seg = y[s0 - start:s1 - start] * g
        if role == "cut":                                  # a whoosh travels left to right across its peak
            pan = np.linspace(-0.35, 0.35, len(seg))
            l, r = seg * np.sqrt(0.5 - pan / 2) * 1.414, seg * np.sqrt(0.5 + pan / 2) * 1.414
        else:
            l = r = seg
        room = 0.84 / max(1e-6, np.abs(np.stack([mix[s0:s1, 0] + l, mix[s0:s1, 1] + r])).max())
        if room < 1:                                       # trim this effect, never the music
            l, r = l * room, r * room
            level += 20 * np.log10(room)
        mix[s0:s1, 0] += l
        mix[s0:s1, 1] += r
        rows.append((c, start / SR, f"{role} at {level:.1f} dB ({over:+.0f} over the bed)"))
    wavp = a.out + ".wav"
    with wave.open(wavp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    af = []
    if a.master is not None:                               # measure, then one linear gain + true-peak ceiling
        meas = subprocess.run([FF, "-hide_banner", "-nostats", "-i", wavp, "-af",
                               f"loudnorm=I={a.master}:TP=-1:LRA=20:print_format=json", "-f", "null", "-"],
                              capture_output=True, text=True).stderr
        m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
        af = ["-af", f"loudnorm=I={a.master}:TP=-1:LRA=20:linear=true:measured_I={m['input_i']}:"
                     f"measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                     f"offset={m['target_offset']},aresample={SR},apad"]
    subprocess.run([FF, "-v", "error", "-y", "-i", a.video, "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    *af, "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out], check=True)
    os.remove(wavp)
    lines = ["# t_cue\tkind\tsource\tsound_start\tnote"]
    for c, st, note in rows:
        lines.append(f"{c['t']:.3f}\t{c['kind']}\t{c['src']}\t{'' if st is None else f'{st:.3f}'}\t{note}")
    sheet = a.sheet or os.path.splitext(a.out)[0] + "-cues.tsv"
    open(sheet, "w").write("\n".join(lines) + "\n")
    print(f"{sum(1 for r in rows if r[1] is not None)} sounds placed, {len(rows)} cues; sheet {sheet}")


if __name__ == "__main__":
    main()
