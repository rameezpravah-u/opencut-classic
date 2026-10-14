"""NixWoods, "I know I should sleep, but the voices in my head go…": music, then the workshop's own sound.

The pattern follows @dreamspace_interiors_calgary's reel (instagram.com/reel/Dd-QOeRvf0Q, 12.7 s). The owner asked on
14 Oct: "Interesting music and then sound, can you do the same?"
- 0-2.97 s: a calm line plays over a quiet shot, "I know / I should sleep, / but the voices / in my head go…" set large
  in a cream condensed serif.
- 2.97-6.9 s: the "voices" are the shop. Seven hard cuts every 0.567 s, each a machine at work with its own sound.
- 6.9-12.7 s: one held wide shot, "the sound / of custom…", then "custom millwork" with a small brand line.

Ours:
- the line plays over our music (music1-aesthetic) and the Luma Pillar lit in a dark room at night;
- on the cut the music stops dead and our own floor takes over, every shot with the sound it was recorded with: the
  CNC router, strips cut in the sawdust, the router close, routed Aurora bars, black-finished bars, a bar switched on
  on test (its click) and a lit bar;
- it ends on the lamp lit in the room, smoke drifting through its glow, "the sound / of handmade…" then
  "handmade lighting" with "NixWoods · India", over a quiet room tone.

The reference's audio is never used: its vocal line is not ours, and its machine sounds are another workshop's, which
would misrepresent our floor. So the master carries our own sound and is postable as is, including in ads. The type
is Instrument Serif (OFL, assets/Instrument_Serif-400.ttf), the closest free face to the reference's.

    python3 brand-reels/voices-in-my-head/voices.py
"""
import os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "luma-styled"))
import luma_shots as L                                                   # noqa: E402
from made_well import encoder, footage                                    # noqa: E402
from festive_cuts import FF, FPS, H, W, R, SRC, font, grade_shot         # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261014-nixwoods-voices-in-my-head-sound-of-handmade-v1"
DUR = 12.7
SR = 48000
DROP = 2.967                                        # the music stops, the shop starts (the reference's cut)
HELD = 6.9                                          # the held last shot
SWAP = 8.6                                          # "the sound of handmade…" becomes "handmade lighting"
CREAM = (244, 240, 210)

# the seven "voices": (cut-in, source, in-point, frame-x for landscape sources), every 0.567 s as in the reference
SHOP = [(2.967, "IMG_7698.mov", 0.00, .5),         # the CNC router in the cut
        (3.533, "IMG_7653.mov", 0.40, .5),         # strips cut, in the sawdust
        (4.100, "IMG_7699.mov", 0.60, .5),         # the router again, closer
        (4.667, "IMG_7984.mov", 0.20, .45),        # routed bars with diffusers
        (5.233, "IMG_7990.mov", 0.50, .5),         # black-finish bars
        (5.767, "IMG_7991.mov", 0.25, .5),         # a bar switched on, on test (its click)
        (6.333, "IMG_7992.mov", 0.00, .5)]         # a lit bar over the black bars


def clip_audio(path, t0, dur):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", path, "-t", f"{dur:.3f}", "-vn", "-ac", "2",
                          "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = int(round(dur * SR))
    return np.pad(a, ((0, max(0, n - len(a))), (0, 0)))[:n]


def level(seg, target, most=12):
    rms = 20 * np.log10(np.sqrt(np.mean(seg ** 2)) + 1e-9)
    return seg * 10 ** (np.clip(target - rms, -most, most) / 20) if rms > -100 else seg


def soundtrack():
    """music under the line, cut dead on the drop; then each shop shot with its own recorded sound (levelled to
    -18 dB RMS, quiet handling lifted at most 12 dB, 15 ms crossfades); then a quiet room tone under the held shot,
    from a lamp-lit room clip (IMG_7664), fading out"""
    n = int(DUR * SR)
    mix = np.zeros((n, 2), np.float32)
    mus = level(clip_audio(R("aurora-reels/audio/music1-aesthetic.mp3"), 0.0, DROP), -17, 30)
    mus *= np.clip(np.arange(len(mus)) / (0.03 * SR), 0, 1)[:, None]
    mus[-int(0.012 * SR):] *= np.linspace(1, 0, int(0.012 * SR))[:, None]
    mix[:len(mus)] += mus
    xf = int(0.015 * SR)
    ends = [s[0] for s in SHOP[1:]] + [HELD]
    for (a, clip, t_in, _), b in zip(SHOP, ends):
        seg = level(clip_audio(SRC(clip), t_in, b - a + 0.015), -18)
        ramp = np.ones(len(seg), np.float32)
        ramp[:xf] = np.linspace(0, 1, xf)
        ramp[-xf:] = np.linspace(1, 0, xf)
        i = int(a * SR)
        mix[i:i + len(seg)] += (seg * ramp[:, None])[:n - i]
    tone = level(clip_audio(SRC("IMG_7664.mov"), 0.0, 3.6), -36, 14)
    tone = np.concatenate([tone, tone[::-1]])[:int((DUR - HELD) * SR)]      # 3.6 s mirrored to cover the shot
    tone *= np.clip(np.arange(len(tone)) / (0.25 * SR), 0, 1)[:, None]
    tone *= np.clip((len(tone) - np.arange(len(tone))) / (1.2 * SR), 0, 1)[:, None]
    i = int(HELD * SR)
    mix[i:i + len(tone)] += tone[:n - i]
    return mix * 0.89 / (np.abs(mix).max() + 1e-9)


def text_layer(lines, size, top, step, small=None):
    """centred lines in the reference's cream serif, with a soft shadow so they hold over the lit lamp"""
    f = font("Instrument_Serif-400.ttf", size)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rows = [(t, f, top + i * step) for i, t in enumerate(lines)]
    if small:
        rows.append((small, font("Instrument_Serif-400.ttf", round(size * 0.46)), top + len(lines) * step - 30))
    for t, ff, y in rows:
        ImageDraw.Draw(sh).text(((W - ff.getlength(t)) / 2, y + 3), t, font=ff, fill=(0, 0, 0, 150), anchor="ls")
    lay = sh.filter(ImageFilter.GaussianBlur(9))
    for t, ff, y in rows:
        # the small line gets a thin dark edge: it crosses the lamp's lit bar
        edge = dict(stroke_width=2, stroke_fill=(40, 26, 16, 170)) if t == small else {}
        ImageDraw.Draw(lay).text(((W - ff.getlength(t)) / 2, y), t, font=ff, fill=CREAM + (255,), anchor="ls",
                                 **edge)
    return np.asarray(lay, np.float32) / 255


def lamp(name, secs):
    """the Luma Pillar lit in the dark room, low-key (its warm light kept, shadows pushed down)"""
    out = []
    for f in L.shot(name, secs):
        x = f.astype(np.float32) / 255
        out.append((np.clip(np.clip(x * np.array([1.05, 1.0, 0.9], np.float32), 0, 1) ** 1.25, 0, 1) * 255
                    + 0.5).astype(np.uint8))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    hook = text_layer(["I know", "I should sleep,", "but the voices", "in my head go…"], 111, 680, 118)
    snd = text_layer(["the sound", "of handmade…"], 96, 860, 100)
    end = text_layer(["handmade lighting"], 92, 905, 110, small="NixWoods · India")
    wavp = os.path.join(OUT, "_a.wav")
    with wave.open(wavp, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((soundtrack() * 32767).astype(np.int16).tobytes())
    enc = encoder(wavp, os.path.join(OUT, f"{NAME}.mp4"))
    parts = [(0.0, lambda s: lamp("wide-on", s))]
    ends = [s[0] for s in SHOP[1:]] + [HELD]
    for (a, clip, t_in, xf), b in zip(SHOP, ends):
        parts.append((a, lambda s, c=clip, t=t_in, x=xf: grade_shot(footage(SRC(c), t, x, 1.0, s), keep=0.6,
                                                                       target=0.33)))
    parts.append((HELD, lambda s: lamp("smoke-a", s)))
    mids, done = [], 0
    for (t0, make), t1 in zip(parts, [p[0] for p in parts[1:]] + [DUR]):
        n = round(t1 * FPS) - round(t0 * FPS)
        fr = make(n / FPS)
        for k, f in enumerate(fr[:n]):
            t = (round(t0 * FPS) + k) / FPS
            lay = hook if t < DROP else (snd if HELD <= t < SWAP else end if t >= SWAP else None)
            o = f.astype(np.float32) / 255
            if lay is not None:
                o = o * (1 - lay[..., 3:]) + lay[..., :3] * lay[..., 3:]
            b = (np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8)
            enc.stdin.write(b.tobytes())
            done += 1
            if k == n // 2 or (t0 == HELD and k in (n // 4, 3 * n // 4)):
                mids.append(b)
        print(f"{t1:5.2f} s", flush=True)
    assert done == round(DUR * FPS), done
    enc.stdin.close()
    assert enc.wait() == 0
    os.remove(wavp)
    Image.fromarray(mids[0]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 5, 480 * 2))
    for i, im in enumerate(mids[:10]):
        sh.paste(Image.fromarray(im).resize((270, 480)), (270 * (i % 5), 480 * (i // 5)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", done, "frames")


if __name__ == "__main__":
    main()
