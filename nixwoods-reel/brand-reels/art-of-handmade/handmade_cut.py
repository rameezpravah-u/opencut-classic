"""NixWoods "the art of handmade": the Aurora's making, cut on @heycarmenta's pattern (instagram.com/reel/DcyiiBGPYjc).

The reference is a 7.98 s woodshop montage with 26 cuts. Every cut sits on an onset of its audio, in a fast-slow-fast
ramp: about 0.1 s apart for the first 0.9 s, widening to a 1.27 s hold at 3.13 s, then closing back to about 0.1 s
before the finished piece. The text "the art of handmade" stays up the whole time. This cut keeps that timing to the
frame and swaps in real Aurora workshop footage (hands only, no faces), ending on the Aurora lit on a wall.

    python3 brand-reels/art-of-handmade/handmade_cut.py [--ref-audio <reference.wav>]

Writes, in out/:
  ...-in-app-audio.mp4  posting master with a silent track. On Instagram, tap "Use audio" on the reference reel: the
                        cuts start at 0.00, so its audio lands on them.
  ...-music6.mp4        the same pattern quantised to music6-corners (1/8-beat grid, the hold on a downbeat), for
                        ads or if the reference audio is not available to a business account.
  cover and sheet.
With --ref-audio, also a review preview carrying the reference audio, written to the given --preview path (never into
the repo, never for posting).
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import FF, FPS, H, W, M6, S, SRC, font, grade_shot, shot_frames  # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261013-nixwoods-aurora-linear-wall-light-art-of-handmade-v1"
DUR = 7.98

# The reference's cut times (scene detection, each on an audio onset within one frame).
CUTS = [0.0, 0.1, 0.167, 0.267, 0.367, 0.467, 0.567, 0.633, 0.767, 0.9, 1.2, 1.467, 1.8, 2.333, 3.133, 4.4,
        5.233, 5.667, 6.067, 6.333, 6.533, 6.7, 7.067, 7.2, 7.3, 7.4, 7.567]

PLANKS = "FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4"   # raw teak planks
STRIPS = "IMG_7653.mov"                                # cut strips in sawdust
BARS = "IMG_7984.mov"                                  # routed teak bars with diffusers
BLACK = "IMG_7990.mov"                                 # black-finish bars
TEST = "IMG_7991.mov"                                  # one bar lit on test
TEST2 = "IMG_7992.mov"                                 # bars lit on test, second angle
WALL = "aurora-dimming-9x16.mp4"                       # the Aurora on a wall (its logo comes at 3.9 s: never reached)

# One (clip, in-point s, landscape frame-x) per segment, in the reference's arc: material, shaping, finish, the light
# on test in the long hold, faster details, then the lit Aurora.
SEQ = [(PLANKS, 0.3, .5), (STRIPS, 0.5, .5), (PLANKS, 1.5, .5), (BARS, 0.3, .45), (STRIPS, 1.8, .5),
       (BLACK, 0.4, .5), (PLANKS, 2.8, .5), (BARS, 1.4, .45), (STRIPS, 2.6, .5), (PLANKS, 3.2, .5),
       (BARS, 2.0, .45), (BLACK, 1.2, .5), (STRIPS, 0.9, .5), (BARS, 0.5, .45),
       (TEST, 0.15, .5),                                                # the 1.27 s hold
       (BLACK, 1.8, .5), (TEST2, 0.2, .5), (PLANKS, 0.8, .5), (BARS, 2.3, .45), (TEST2, 1.2, .5),
       (STRIPS, 2.2, .5), (TEST, 0.05, .5), (BLACK, 2.5, .5), (PLANKS, 2.0, .5), (TEST2, 1.8, .5),
       (WALL, 1.2, .5), (WALL, 3.2, .5)]
assert len(SEQ) == len(CUTS)


def music6_cuts():
    """the reference cuts quantised to music6's 1/8-beat grid, with the hold landing on a downbeat"""
    off = M6["b0"] + 5 * M6["beat"] - CUTS[14]                           # music start offset: hold on beat 5
    g = M6["beat"] / 8
    q = [round((t + off - M6["b0"]) / g) * g + M6["b0"] - off for t in CUTS[1:]]
    out = [0.0]
    for t in q:
        out.append(max(t, out[-1] + 2 / FPS))                            # never shorter than 2 frames
    return out, off


def frames_for(cuts):
    fr = []
    ends = cuts[1:] + [DUR]
    for (clip, t_in, xf), a, b in zip(SEQ, cuts, ends):
        n = round(b * FPS) - round(a * FPS)
        sh = S(SRC(clip), 30, t_in, xf=xf, t_src=None)
        fr += grade_shot(shot_frames(sh, n / FPS)[:n])
    return fr


def text_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("Inter-400.ttf", 34)
    t = "the art of handmade"
    x = (W - f.getlength(t)) / 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x, 642), t, font=f, fill=(0, 0, 0, 150))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(lay).text((x, 640), t, font=f, fill=(255, 255, 255, 242))
    return np.asarray(lay, np.float32)


def silent(path, dur):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(b"\0" * int(dur * 48000) * 4)


def track(src, start, dur, path, peak=0.65):
    sr = 48000
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", src, "-t", f"{dur:.3f}", "-ac", "2", "-ar",
                          str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(dur * sr)
    m = np.pad(m, ((0, max(0, n - len(m))), (0, 0)))[:n]
    m *= np.clip((dur - np.arange(n) / sr) / 0.25, 0, 1)[:, None]
    m *= peak / (np.abs(m).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def encode(frames, wav, path):
    txt = text_layer()
    a = txt[..., 3:] / 255
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                          path], stdin=subprocess.PIPE)
    for f in frames:
        o = f.astype(np.float32) * (1 - a) + txt[..., :3] * a
        p.stdin.write((o + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    assert p.wait() == 0, path


def sheet(frames, cuts, path):
    pick = [round((a + b) / 2 * FPS) for a, b in zip(cuts, cuts[1:] + [DUR])][::2][:12]
    th = [Image.fromarray(frames[min(i, len(frames) - 1)]).resize((270, 480)) for i in pick]
    s = Image.new("RGB", (270 * 6, 480 * 2))
    for k, im in enumerate(th):
        s.paste(im, (270 * (k % 6), 480 * (k // 6)))
    s.save(path, quality=88)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio")
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    tmp = os.path.join(OUT, "_a.wav")
    n = round(DUR * FPS)

    fr = frames_for(CUTS)[:n]
    assert len(fr) == n, len(fr)
    silent(tmp, DUR)
    encode(fr, tmp, os.path.join(OUT, f"{NAME}-in-app-audio.mp4"))
    Image.fromarray(fr[-4]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sheet(fr, CUTS, os.path.join(OUT, f"{NAME}-sheet.jpg"))
    if a.ref_audio and a.preview:
        track(a.ref_audio, 0.0, DUR, tmp, peak=0.89)
        encode(fr, tmp, a.preview)
    print("in-app-audio cut: cuts at", " ".join(f"{t:.2f}" for t in CUTS))

    c6, off = music6_cuts()
    fr6 = frames_for(c6)[:n]
    track(M6["path"], off, DUR, tmp)
    encode(fr6, tmp, os.path.join(OUT, f"{NAME}-music6.mp4"))
    print(f"music6 cut (track from {off:.3f} s): cuts at", " ".join(f"{t:.2f}" for t in c6))
    os.remove(tmp)


if __name__ == "__main__":
    main()
