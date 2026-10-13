"""NixWoods "The sound of craft": our workshop, heard (the pattern of @thenohea's reel instagram.com/reel/DeZUtdbASYZ).

The reference is 22.3 s long:
- a furniture workshop in 14 shots of 0.9-2.6 s (CNC, saw, sander, router, welding, hammer);
- each shot plays its own machine sound;
- "THE / SOUND OF / CRAFT" is set small and staggered across the frame for the whole reel;
- it ends on the logo.

This version keeps the reference's cut lengths and its staggered words, using our own real workshop footage with the
**sound it was recorded with**:
- the CNC router cutting a channel;
- strips cut in the sawdust;
- the teak planks;
- routed and black-finished bars;
- bars lit on test (with their switch clicks);
- the Aurora coming on a wall.

The reference's audio is another workshop's noise, so it is never laid over our floor. The master is postable as is,
including in ads.

    python3 brand-reels/sound-of-craft/sound_of_craft.py
"""
import os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import (A, AMBER, CREAM, FF, FPS, H, W, S, SRC, font, grade_shot,  # noqa: E402
                          shot_frames, sstep)

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261013-nixwoods-sound-of-craft-v1"
SR = 48000

# the reference's cuts; the end card from 20.3 s
CUTS = [0.0, 1.633, 3.1, 4.233, 6.833, 7.833, 9.467, 10.667, 11.967, 13.333, 14.233, 15.633, 16.9, 18.833, 20.3]
DUR = 22.27
# (clip, in-point s, landscape frame-x, straighten): loud machine shots first, the light last
SHOTS = [("IMG_7698.mov", 0.00, .5, False),                     # CNC router cutting a channel
         ("IMG_7653.mov", 0.20, .5, False),                     # strips cut, in the sawdust
         ("IMG_7699.mov", 0.30, .5, False),                     # the router again, closer
         ("FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4", 1.50, .5, False),   # teak planks, handled
         ("IMG_7984.mov", 0.40, .45, False),                    # routed bars with diffusers
         ("IMG_7698.mov", 1.20, .5, False),                     # the router, deeper in the cut
         ("IMG_7990.mov", 0.30, .5, False),                     # black-finish bars
         ("NW-RAW-20261011-unknown-7d43cbb6.mov", 0.10, .5, False),       # bars bundled, then lit
         ("NW-RAW-20261011-unknown-0e06e8d3.mov", 1.20, .5, True),        # a bar lit, standing
         ("NW-RAW-20261011-unknown-e23f692e.mov", 2.00, .5, False),       # a lit bar on the floor
         ("IMG_7991.mov", 0.10, .5, False),                     # a bar switched on, on test (its click)
         ("NW-RAW-20261011-unknown-ea1e0467.mov", 1.80, .5, True),        # a lit bar at the bench
         ("NW-RAW-20261011-unknown-3c4db763.mov", 1.50, .5, False),       # a long bar lit on test
         ("aurora-dimming-9x16.mp4", 0.10, .5, False)]          # the Aurora on a wall coming on (no sound: a click)
assert len(SHOTS) == len(CUTS) - 1
WORDS = [("THE", 760, 470), ("SOUND OF", 80, 820), ("CRAFT", 760, 1180)]    # clear of the Aurora bar


def clip_audio(path, t0, dur):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", path, "-t", f"{dur:.3f}", "-vn", "-ac", "2",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(round(dur * SR))
    return np.pad(a, ((0, max(0, n - len(a))), (0, 0)))[:n]


def soundtrack():
    """each shot with its own recorded sound, levelled (loud shots to -20 dB RMS, quiet room tone lifted at most 12 dB),
    30 ms crossfades at the cuts; the Aurora gets the test bar's switch click; the end card keeps a fading room tone"""
    n = int(DUR * SR)
    mix = np.zeros((n, 2), np.float32)
    xf = int(0.03 * SR)
    for (clip, t_in, _, _), a, b in zip(SHOTS, CUTS, CUTS[1:]):
        seg = clip_audio(SRC(clip), t_in, b - a + 0.03)
        rms = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
        if rms > -100:
            seg *= 10 ** (np.clip(-20 - rms, -12, 12) / 20)
        ramp = np.ones(len(seg), np.float32)
        ramp[:xf] = np.linspace(0, 1, xf)
        ramp[-xf:] = np.linspace(1, 0, xf)
        i = int(a * SR)
        j = min(n, i + len(seg))
        mix[i:j] += (seg * ramp[:, None])[:j - i]
    # the switch click from the test clip (IMG_7991 at ~0.5 s), on the Aurora's own switch-on
    t_in = SHOTS[-1][1]
    click = clip_audio(SRC("IMG_7991.mov"), 0.45, 0.25)
    click *= np.linspace(1, 0, len(click))[:, None] ** 2
    k = int((CUTS[-2] + 0.40 - t_in) * SR)
    mix[k:k + len(click)] += click * 0.9
    # room tone under the end card, from the quiet planks clip, fading out
    tone = clip_audio(SRC(SHOTS[3][0]), 0.2, DUR - CUTS[-1])
    tone *= 10 ** (8 / 20) * np.linspace(1, 0, len(tone))[:, None]
    mix[int(CUTS[-1] * SR):int(CUTS[-1] * SR) + len(tone)] += tone[:n - int(CUTS[-1] * SR)]
    mix *= 0.89 / (np.abs(mix).max() + 1e-9)
    return mix


def words_layer():
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("Inter-600.ttf", 34)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for t, x, y in WORDS:
        ImageDraw.Draw(sh).text((x, y + 2), t, font=f, fill=(0, 0, 0, 150))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(4)))
    d = ImageDraw.Draw(lay)
    for t, x, y in WORDS:
        xx = x
        for ch in t:                                                     # tracked out a little, like the reference
            d.text((xx, y), ch, font=f, fill=CREAM + (250,))
            xx += f.getlength(ch) + 3
    return np.asarray(lay, np.float32) / 255


def end_card():
    """Dusk ground, vignette and grain; the logo in cream and nixwoods.com in amber (MOTION.md end card)"""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / np.sqrt(2)
    g = np.ones((H, W, 3), np.float32) * (np.array([46, 30, 20], np.float32) / 255 + 0.02)
    g *= np.clip(1.08 - 0.35 * r, 0, 1.2)[..., None]
    g += np.random.default_rng(5).normal(0, 2.2 / 255, g.shape).astype(np.float32)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    logo = Image.open(A("logo.png")).convert("RGBA")
    lw = 520
    logo = logo.resize((lw, round(logo.height * lw / logo.width)), Image.LANCZOS)
    tint = Image.new("RGBA", logo.size, CREAM + (255,))
    tint.putalpha(logo.split()[3])
    top = 640
    lay.alpha_composite(tint, ((W - lw) // 2, top))
    fu = font("Inter-600.ttf", 46)
    ImageDraw.Draw(lay).text(((W - fu.getlength("nixwoods.com")) / 2, top + logo.height + 80), "nixwoods.com",
                             font=fu, fill=AMBER)
    a = np.asarray(lay, np.float32) / 255
    return np.clip(g * (1 - a[..., 3:]) + a[..., :3] * a[..., 3:], 0, 1)


def main():
    os.makedirs(OUT, exist_ok=True)
    words = words_layer()
    wa = words[..., 3:]
    card = end_card()
    n = round(DUR * FPS)
    wav = os.path.join(OUT, "_a.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((soundtrack() * 32767).astype(np.int16).tobytes())
    path = os.path.join(OUT, f"{NAME}.mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                          str(FPS), "-i", "-", "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "17",
                          "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                          path], stdin=subprocess.PIPE)
    keep, done, last = [], 0, None
    for (clip, t_in, xf, straight), a, b in zip(SHOTS, CUTS, CUTS[1:]):
        k = round(b * FPS) - round(a * FPS)
        fr = grade_shot(shot_frames(S(SRC(clip), 30, t_in, xf=xf, straight=straight), k / FPS)[:k])
        for f in fr:
            o = f.astype(np.float32) / 255
            last = np.clip(o * (1 - wa) + words[..., :3] * wa, 0, 1)
            p.stdin.write((last * 255 + 0.5).astype(np.uint8).tobytes())
            done += 1
        keep.append((np.clip(fr[len(fr) // 2].astype(np.float32) / 255 * (1 - wa) + words[..., :3] * wa, 0, 1)
                     * 255 + 0.5).astype(np.uint8))
    while done < n:                                                      # the end card crossfades in over 0.3 s
        u = float(sstep((done / FPS - CUTS[-1]) / 0.3))
        o = last * (1 - u) + card * u
        p.stdin.write((np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        done += 1
    p.stdin.close()
    assert p.wait() == 0, path
    os.remove(wav)
    Image.fromarray((card * 255 + 0.5).astype(np.uint8)).save(os.path.join(OUT, f"{NAME}-endcard.jpg"), quality=90)
    Image.fromarray(keep[8]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 7, 480 * 2))
    for i, im in enumerate(keep[:14]):
        sh.paste(Image.fromarray(im).resize((270, 480)), (270 * (i % 7), 480 * (i // 7)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", path)


if __name__ == "__main__":
    main()
