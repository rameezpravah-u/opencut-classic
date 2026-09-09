#!/usr/bin/env python3
"""beatgrid.py — measure a music track's tempo and the cut interval to use with it.

`presets.json` carries a `cut` per style (`styles.aesthetic.cut = 1.766`), and the audio README
says those grids are "measured from these exact files". They were measured by hand. A new track
needs the same number, so this measures it:

    python3 system/beatgrid.py rubik-reels/audio/music6-corners.mp3

Spectral flux onset envelope -> autocorrelation -> the strongest lag in a plausible tempo band.
Prints the tempo, the beat period, and the multiples of it that make usable shot lengths, because
a cut every beat is frantic at 70 BPM and right at 140.
"""
import argparse, subprocess, sys
import numpy as np

SR = 11025


def pcm(path):
    """decode to mono float32 at SR with the ffmpeg imageio-ffmpeg ships (there is no ffprobe)"""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        exe = "ffmpeg"
    out = subprocess.run([exe, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True)
    if out.returncode or not out.stdout:
        sys.exit(f"could not decode {path}: {out.stderr.decode()[:400]}")
    return np.frombuffer(out.stdout, dtype=np.float32)


def onset_envelope(x, hop=256, win=1024):
    n = 1 + (len(x) - win) // hop
    w = np.hanning(win)
    frames = np.lib.stride_tricks.as_strided(
        x, shape=(n, win), strides=(x.strides[0] * hop, x.strides[0])) * w
    mag = np.abs(np.fft.rfft(frames, axis=1))
    flux = np.diff(mag, axis=0, prepend=mag[:1])
    env = np.maximum(flux, 0).sum(axis=1)                 # rectified spectral flux
    env -= env.mean()
    return env / (env.std() or 1.0), SR / hop             # envelope, frames per second


def tempo(env, fps, lo_bpm=55, hi_bpm=170):
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    ac[0] = 0
    lags = np.arange(len(ac))
    with np.errstate(divide="ignore"):
        bpm = 60.0 * fps / lags
    ok = (bpm >= lo_bpm) & (bpm <= hi_bpm) & (lags > 0)
    if not ok.any():
        sys.exit("no plausible tempo found")
    lag = lags[ok][np.argmax(ac[ok])]
    return 60.0 * fps / lag, lag / fps, ac, ok, lags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("track")
    ap.add_argument("--reel", type=float, default=18.5, help="target reel length, for the shot maths")
    a = ap.parse_args()

    x = pcm(a.track)
    env, fps = onset_envelope(x)
    bpm, beat, ac, ok, lags = tempo(env, fps)

    print(f"{a.track}")
    print(f"  length     {len(x)/SR:.1f}s")
    print(f"  tempo      {bpm:.1f} BPM")
    print(f"  beat       {beat:.3f}s")
    for mult in (1, 2, 4):
        n = a.reel / (beat * mult)
        print(f"  cut x{mult}     {beat*mult:.3f}s  -> {n:.1f} shots in {a.reel:.1f}s"
              f"{'   <- a shot every beat is frantic below ~100 BPM' if mult == 1 and bpm < 100 else ''}")
    # confidence: how far the peak stands above the rest of the plausible band
    band = ac[ok]
    ref = np.abs(band).mean() or 1.0        # autocorrelation goes negative; a signed mean prints nonsense
    ratio = band.max() / ref
    print(f"  confidence peak is {ratio:.1f}x the mean absolute correlation in the band "
          f"({'clear' if ratio > 2.5 else 'weak — check by ear'})")


if __name__ == "__main__":
    main()
