#!/usr/bin/env python3
"""beats.py — where the beats and downbeats fall in a music track, as JSON, so a reveal can land on one.

    python3 motion-libs/beats.py brand-reels/audio/music3-design.mp3 [--out beats.json]

system/beatgrid.py measures the tempo; this adds the phase: the beat grid is slid until it sits on the
strongest onsets, and every fourth beat that is loudest on average becomes the downbeat. Output:
{"bpm", "beat", "first_beat", "beats": [...], "downbeats": [...], "strong": [...]} in seconds.
"strong" are the beats whose onset is in the top quarter, for accents.
"""
import argparse, json, os, sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "system"))
from beatgrid import SR, onset_envelope, pcm, tempo   # noqa: E402

HOP = 256


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--out")
    a = ap.parse_args()
    x = pcm(a.track)
    env, fps = onset_envelope(x, hop=HOP)
    bpm, period = (float(v) for v in tempo(env, fps)[:2])
    step = period * fps
    n = len(env)
    best, phase = -1, 0.0
    for k in np.linspace(0, step, 64, endpoint=False):           # slide the grid onto the onsets
        idx = (k + np.arange(0, n - k, step)).astype(int)
        s = env[np.clip(idx, 0, n - 1)].sum()
        if s > best:
            best, phase = s, k
    idx = (phase + np.arange(0, n - phase, step)).astype(int)
    idx = idx[idx < n]
    beats = idx / fps
    vals = np.array([env[max(0, i - 2):i + 3].max() for i in idx])
    acc = [vals[j::4].mean() for j in range(4)]                   # which of the four is the downbeat
    d0 = int(np.argmax(acc))
    out = {"track": os.path.basename(a.track), "bpm": round(bpm, 2), "beat": round(period, 4),
           "first_beat": round(float(beats[0]), 3),
           "beats": [round(float(b), 3) for b in beats],
           "downbeats": [round(float(b), 3) for b in beats[d0::4]],
           "strong": [round(float(b), 3) for b, v in zip(beats, vals) if v >= np.quantile(vals, 0.75)]}
    js = json.dumps(out)
    if a.out:
        open(a.out, "w").write(js)
    print(f"{out['bpm']} bpm, beat {out['beat']} s, first beat {out['first_beat']} s, "
          f"downbeats {out['downbeats'][:6]} ...")


if __name__ == "__main__":
    main()
