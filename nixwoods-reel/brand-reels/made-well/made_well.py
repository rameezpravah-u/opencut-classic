"""NixWoods, "making something look good, and making something well".

The pattern, voice and script follow @artevita_interiors' reel (instagram.com/reel/Db3S5z4s8do, 29.2 s). The owner
asked on 14 Oct: "Use this voice and script on our work."
- A calm male voice reads four lines over slow, close process shots of a workshop:
  "There is a difference between making something look good and making something well. / The details people never
  see often matter the most. / A piece reveals what its maker values through its materials, its construction and
  the care invested in every decision. / Quality is not a feature, it's a reflection of character."
- Each spoken phrase sits in small white capitals at mid-frame while it is said, gone in the pauses.
- A small brand mark low in the frame throughout; it ends on a wood surface with soft light, the logo tile fading in,
  then black.

Ours keeps the reference's shot lengths (its two long holds are split in two, as our clips are shorter) on our own
real footage: teak planks, the CNC router, cut strips, routed and black-finished Aurora bars, bars lit on test, and
the Aurora coming on a wall. No faces. The voice is theirs, reached through Instagram's "Use audio", so the caption
times come from a local transcription of that reel (word onsets, faster-whisper small.en).

    python3 brand-reels/made-well/made_well.py [--ref-audio ref.wav --preview /tmp/p.mp4]

Writes out/<NAME>-in-app-audio.mp4 (silent track; tap "Use audio" on the reference at 0:00, the captions land on its
words) and out/<NAME>-music1.mp4 (the same cut on our own music1-aesthetic track, words on screen only, for ads), plus
a cover and a sheet.
"""
import argparse, os, subprocess, sys, wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import A, CREAM, FF, FPS, H, W, R, SRC, font, grade_shot, src_dims, sstep   # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261014-nixwoods-made-well-v1"
DUR = 29.2
SR = 48000
LOGO_ON, BLACK_ON = 27.75, 28.55

# (cut-in, source, in-point, frame-x for landscape sources, speed; < 1 is motion-interpolated slow motion[, the grade's
# mean luma when not 0.30])
SHOTS = [
    (0.000, SRC("FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4"), 1.20, .5, 0.55),  # teak planks (clean span 1.2-2.6 s)
    (2.625, SRC("IMG_7698.mov"), 0.40, .5, 1.0),                               # the CNC router in the cut
    (3.792, SRC("IMG_7653.mov"), 0.40, .5, 0.85),                              # strips cut, in the sawdust
    (6.000, SRC("IMG_7699.mov"), 0.00, .5, 0.70),                              # the router again, closer
    (9.542, SRC("IMG_7984.mov"), 0.20, .45, 1.0),                              # routed bars with diffusers
    (12.000, SRC("IMG_7990.mov"), 0.40, .5, 1.0),                              # black-finish bars
    (14.042, SRC("NW-RAW-20261011-unknown-7d43cbb6.mov"), 0.20, .5, 1.0),      # bars bundled, then lit
    (15.750, SRC("NW-RAW-20261011-unknown-0e06e8d3.mov"), 1.40, .5, 1.0),      # a bar lit, standing
    (17.042, SRC("IMG_7991.mov"), 0.10, .5, 1.0),                              # a bar switched on, on test
    (18.042, SRC("IMG_7992.mov"), 0.60, .5, 1.0),                              # a lit bar over the black bars
    (19.083, SRC("NW-RAW-20261011-unknown-e23f692e.mov"), 1.80, .5, 1.0),      # a lit bar on the floor, diagonal
    (21.083, R("floor-reels/src/nx07-7922.mp4"), 0.30, .5, 1.0),               # a lit bar in the hand
    # the Aurora on a wall coming on: source 0-1.95 s only, before the clip's own zoom transition
    (22.833, SRC("aurora-dimming-9x16.mp4"), 0.00, .5, 0.45, 0.17),
    (27.167, None, 0, 0, 0),                                                   # wood, soft light, the logo, black
]

# the spoken phrases and when they are on screen (first word's onset to the next phrase, or the line's end)
PHRASES = [
    ("THERE IS A", 0.00), ("DIFFERENCE BETWEEN", 0.34), ("MAKING SOMETHING", 1.18), ("LOOK GOOD", 1.88),
    ("AND MAKING", 2.64), ("SOMETHING WELL", 3.58), (None, 4.90),
    ("THE DETAILS", 6.00), ("PEOPLE NEVER SEE", 6.78), ("OFTEN MATTER", 8.00), ("THE MOST", 9.02), (None, 9.95),
    ("A PIECE", 10.44), ("REVEALS", 10.78), ("WHAT ITS MAKER VALUES", 11.42), ("THROUGH ITS MATERIALS", 12.82),
    ("ITS CONSTRUCTION", 14.50), ("AND THE CARE", 15.12), ("INVESTED IN", 16.52), ("EVERY DECISION", 17.54),
    (None, 19.00),
    ("QUALITY", 19.94), ("IS NOT A", 20.22), ("FEATURE", 21.04), ("IT'S A REFLECTION", 21.80), ("OF CHARACTER", 22.82),
    (None, 24.70),
]


def footage(src, t_in, xf, speed, secs):
    """1080x1920 frames: a 9:16 strip of a landscape source (or the whole of a portrait one), slowed with motion
    interpolation at the strip's own size, then scaled up once"""
    n = round(secs * FPS)
    sw, sh = src_dims(src)
    vf = [f"trim=start={t_in:.3f}", "setpts=PTS-STARTPTS"]
    if sw / sh > W / H:
        cw = round(sh * W / H / 2) * 2
        vf.append(f"crop={cw}:{sh}:{round((sw - cw) * xf)}:0")
    if speed < 0.98:
        vf += [f"setpts=PTS/{speed:.4f}", "minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"]
    else:
        vf.append("fps=30")
    vf += [f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase", f"crop={W}:{H}", "unsharp=5:5:0.4"]
    raw = subprocess.run([FF, "-v", "error", "-i", src, "-vf", ",".join(vf), "-frames:v", str(n), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = list(np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3))
    assert len(fr) >= n - 2, (src, len(fr), n)
    return (fr + [fr[-1]] * n)[:n]


def caption(text):
    """small white capitals at mid-frame, like the reference (a neutral grotesque, about 480 px for the long ones)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("Inter-400.ttf", 40)
    track = 1.0
    widths = [f.getlength(c) for c in text]
    tw = sum(widths) + track * (len(text) - 1)
    x, y = (W - tw) / 2, 960 - 15
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # a firm soft shadow and a thin dark edge keep the white legible where a phrase crosses a lit bar
    for d, fill, dy in ((sh, (0, 0, 0, 160), 2), (None, (255, 255, 255, 255), 0)):
        if d is None:
            lay = sh.filter(ImageFilter.GaussianBlur(5))
            d = lay
        xx = x
        for c, w in zip(text, widths):
            ImageDraw.Draw(d).text((xx, y + dy), c, font=f, fill=fill, anchor="ls", stroke_width=2,
                                   stroke_fill=(30, 20, 12, 190))
            xx += w + track
    return np.asarray(lay, np.float32) / 255


def mark():
    """the small brand mark low in the frame, where the reference keeps its own (inside the safe zone)"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f = font("Inter-600.ttf", 22)
    t = "N I X W O O D S"
    ImageDraw.Draw(lay).text(((W - f.getlength(t)) / 2, 1500), t, font=f, fill=(246, 239, 228, 210))
    return np.asarray(lay, np.float32) / 255


def logo_tile():
    """the logo in Dusk ink on a cream rounded tile, as the reference ends on its app-icon tile"""
    s = 150
    tile = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(tile).rounded_rectangle((0, 0, s - 1, s - 1), 30, fill=(246, 239, 228, 255))
    lg = Image.open(A("logo.png")).convert("RGBA")
    lg = lg.resize((104, round(104 * lg.height / lg.width)), Image.LANCZOS)
    ink = Image.new("RGBA", lg.size, (49, 33, 26, 255))
    ink.putalpha(lg.getchannel("A"))
    tile.alpha_composite(ink, ((s - lg.width) // 2, (s - lg.height) // 2))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(((W - s) // 2, (H - s) // 2 + 8, (W + s) // 2, (H + s) // 2 + 8), 30,
                                         fill=(0, 0, 0, 90))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    lay.alpha_composite(tile, ((W - s) // 2, (H - s) // 2))
    return np.asarray(lay, np.float32) / 255


def wood_end(secs):
    """the last shot: our teak planks close, defocused, with two soft pools of warm lamp light drifting across, a slow
    push; the logo tile fades in, then the frame goes to black"""
    n = round(secs * FPS)
    raw = subprocess.run([FF, "-v", "error", "-ss", "2.10", "-i", SRC("FBB4C770-C6F4-4B5A-8DF5-F9199E630A62.MP4"),
                          "-frames:v", "1", "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    base = Image.frombytes("RGB", (W, H), raw).filter(ImageFilter.GaussianBlur(5))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    tile = logo_tile()
    out = []
    for k in range(n):
        t = k / FPS
        z = 1.2 + 0.03 * t / secs                                       # 1.2: the packing cloth at the left edge stays out
        cw, ch = W / z, H / z
        cx = W / 2 + 80                                                 # and the crop sits right of centre
        im = np.asarray(base.resize((W, H), Image.LANCZOS, box=(cx - cw / 2, (H - ch) / 2, cx + cw / 2,
                                                              (H + ch) / 2)), np.float32) / 255
        im = im * 0.62
        for cx, cy, rx, ry in ((420 + 18 * t, 1010, 70, 140), (510 + 18 * t, 1180, 75, 150)):
            g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2) ** 1.6)[..., None]
            im = im + g * np.array([0.42, 0.30, 0.17], np.float32)
        u = float(sstep((DUR_END0 + t - LOGO_ON) / 0.45))
        im = im * (1 - tile[..., 3:] * u) + tile[..., :3] * tile[..., 3:] * u
        im = im * (1 - float(sstep((DUR_END0 + t - BLACK_ON) / 0.55)))
        out.append((np.clip(im, 0, 1) * 255 + 0.5).astype(np.uint8))
    return out


DUR_END0 = SHOTS[-1][0]


def wav(path, src=None, start=0.0, gain_db=0.0):
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)
    if src:
        raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", src, "-t", f"{DUR:.3f}", "-ac", "2",
                              "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        m[:len(a)] = a
        m *= np.clip((DUR - np.arange(n) / SR) / 1.2, 0, 1)[:, None]
        m *= 0.89 / (np.abs(m).max() + 1e-9) * 10 ** (gain_db / 20)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((m * 32767).astype(np.int16).tobytes())


def encoder(wavp, path, crf=17):
    return subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                             str(FPS), "-i", "-", "-i", wavp, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf",
                             str(crf), "-preset", "slow", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                             "-color_trc", "bt709", "-colorspace", "bt709", "-c:a", "aac", "-b:a", "192k", "-shortest",
                             "-movflags", "+faststart", path], stdin=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref-audio")
    ap.add_argument("--preview")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    caps = {t: caption(t) for t, _ in PHRASES if t}
    mk = mark()
    # every version is written in one pass (the frames are never all held in memory)
    jobs = [(os.path.join(OUT, "_silent.wav"), None, 0.0, os.path.join(OUT, f"{NAME}-in-app-audio.mp4")),
            (os.path.join(OUT, "_music1.wav"), R("aurora-reels/audio/music1-aesthetic.mp3"), -2.0,
             os.path.join(OUT, f"{NAME}-music1.mp4"))]
    if a.ref_audio and a.preview:
        jobs.append((os.path.join(OUT, "_ref.wav"), a.ref_audio, 0.0, a.preview))
    encs = []
    for wp, src, g, path in jobs:
        wav(wp, src, 0.0, g)
        encs.append(encoder(wp, path, crf=23))                          # 29 s: CRF 23 keeps it under ~21 MB
    mids, done = [], 0
    ends = [s[0] for s in SHOTS[1:]] + [DUR]
    for (t0, src, t_in, xf, sp, *tg), t1 in zip(SHOTS, ends):
        n = round(t1 * FPS) - round(t0 * FPS)
        fr = wood_end(n / FPS) if src is None else grade_shot(footage(src, t_in, xf, sp, n / FPS), keep=0.55,
                                                              target=tg[0] if tg else 0.30)
        for k, f in enumerate(fr):
            t = (round(t0 * FPS) + k) / FPS
            o = f.astype(np.float32) / 255
            cur = [p for p, s in PHRASES if s <= t + 1e-6]
            lays = ([caps[cur[-1]]] if cur and cur[-1] else []) + ([mk] if src is not None else [])
            for lay in lays:
                o = o * (1 - lay[..., 3:]) + lay[..., :3] * lay[..., 3:]
            b = (np.clip(o, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
            for e in encs:
                e.stdin.write(b)
            done += 1
            if k == n // 2:
                mids.append(np.frombuffer(b, np.uint8).reshape(H, W, 3))
        print(f"{t1:5.2f} s", flush=True)
    assert done == round(DUR * FPS), done
    for e, (wp, _, _, path) in zip(encs, jobs):
        e.stdin.close()
        assert e.wait() == 0, path
        os.remove(wp)
    Image.fromarray(mids[12]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=92)
    sh = Image.new("RGB", (270 * 7, 480 * 2))
    for i, im in enumerate(mids):
        sh.paste(Image.fromarray(im).resize((270, 480)), (270 * (i % 7), 480 * (i // 7)))
    sh.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=88)
    print("wrote", done, "frames")


if __name__ == "__main__":
    main()
