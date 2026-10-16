"""NixWoods Scandinavian Rosewood Pendant: one room, then three details, after @iranway_studio's linear pendant reel
(instagram.com/reel/Deew9uBo446, 10.2 s).

The reference, frame by frame:
  0.0-3.3  a moody wide of the pendant over a dining table, the camera tilting down from the bar to the table
  3.3-6.0  the room fades to dark while three detail panels come in, top to bottom: the bar's end and cord (3.5 s),
           a diagonal close-up of the lit underside (5.0 s), the bar from the side (6.0 s)
  6.0-10.2 the three panels hold, each drifting slowly. No text.
Our cuts sit on the same times, so its audio fits through "Use audio".

Footage: the 5 Aug shoot's three clips of this pendant (Drive, raw/2026-08-05-shoot-by-product). Their file names say
"nordic … curved", but the lamp on screen is a straight bar with round ends on two cables, in the same dining room as
the Scandinavian Rosewood Pendant's own product photos (rosewood-reels/hf/sh00, sh01). The Nordic pendant is a
curved arm. Fetched into library/cache with library/fetch.py; their last 3.5 s carry a burned-in NX mark, never used.

    python3 brand-reels/pendant-triptych/pendant_triptych.py
"""
import glob, os, subprocess, sys, wave

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import FF, FPS, H, W, grade_shot      # noqa: E402
from made_well import encoder, mark                     # noqa: E402

CACHE = os.path.join(ROOT, "library", "cache")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261016-scandinavian-rosewood-round-pendant-light-one-room-three-details-v1"
SR = 48000
DUR = 10.24

WIDE = "lifestyle-dining-wide-9x16-v1.mp4"
ANGLED = "detail-angled-close-9x16-v1.mp4"
MACRO = "detail-underside-macro-9x16-v1.mp4"

HERO_END = 3.3                 # the tilt ends; the room starts to fade
DARK = (3.3, 5.6)              # the room fades to black over this span
# panels: (top y, height, enters at, source, in-point s, framing at start, framing at end); framing = cx, cy, zoom,
# roll deg, all on the 1080x1920 source; zoom 1 = the panel shows the full source width
PANELS = [
    (0, 600, 3.50, ANGLED, 9.1, (0.80, 0.553, 2.3, 0), (0.82, 0.56, 2.5, 0)),        # the rounded end and its cord
    (600, 720, 5.00, MACRO, 8.4, ("track", 0.50, 2.4, -58), ("track", 0.56, 2.6, -58)),   # the lit underside
    (1320, 600, 6.00, ANGLED, 0.2, (0.42, 0.535, 1.15, 0), (0.58, 0.545, 1.25, 0)),  # the bar from the side
]


def src(tail):
    hits = glob.glob(os.path.join(CACHE, f"*{tail}"))
    if not hits:
        sys.exit(f"missing *{tail}: fetch it with library/fetch.py (drive id in the private INDEX.tsv)")
    return hits[0]


def decode(path, t_in, secs, speed=1.0):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", path, "-t", f"{secs:.3f}", "-vf",
                          (f"setpts=PTS/{speed},minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
                           if speed < 0.98 else "fps=30,") + "scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)


def sstep(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def lerp(a, b, u):
    return a + (b - a) * u


def look(fr, cx, cy, z, rot, w, h):
    """a w x h view of a source frame: (cx, cy) brought to the centre, scaled so the view spans 1/z of the source
    width, rolled by rot degrees"""
    s = w / (1080 / z)
    M = cv2.getRotationMatrix2D((cx * 1080, cy * 1920), rot, s)
    M[:, 2] += (w / 2 - cx * 1080, h / 2 - cy * 1920)
    return cv2.warpAffine(fr, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def strip_x(fr):
    """x of the lit strip in the macro clip (the brightest column), 0-1"""
    g = cv2.resize(fr, (216, 96)).astype(np.float32).mean(2).mean(0)
    return (np.argmax(g) + 0.5) / 216


def moody(frames, target):
    """MOTION.md montage grade, dimmed for an evening room; the lit strip keeps its cream core"""
    out = grade_shot(frames, keep=0.38, target=target)
    h, w = out[0].shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    vig = np.clip(1.08 - 0.55 * (((xx - w / 2) / w) ** 2 + ((yy - h * 0.45) / h) ** 2) * 2.2, 0.55, 1)[..., None]
    return [(np.clip(f.astype(np.float32) * vig, 0, 255)).astype(np.uint8) for f in out]


def main():
    os.makedirs(OUT, exist_ok=True)
    n = round(DUR * FPS)
    hero = moody(list(decode(src(WIDE), 1.0, DARK[1] + 0.2)), 0.16)
    pans = []
    for top, ph, t0, tail, t_in, a, b in PANELS:
        # the angled clip flashes white at 4.6-5.0 s and 8.6-9.0 s, and its end cap leaves the frame at 12.5 s: the
        # end-cap panel plays 9.1-12.5 s at half speed (motion-interpolated), the side view 0.2-4.45 s
        fr = list(decode(src(tail), t_in, DUR - t0 + 0.03, 0.5 if t_in == 9.1 else 1.0))
        xs = None
        if a[0] == "track":
            xs = np.convolve(np.pad([strip_x(f) for f in fr], 6, mode="edge"), np.ones(13) / 13, "valid")
        pans.append((top, ph, t0, moody(fr, 0.26), xs, a, b))

    wavs = {k: os.path.join(OUT, f".{k}.wav") for k in ("in-app-audio", "music1")}
    audio(wavs["in-app-audio"], False)
    audio(wavs["music1"], True)
    encs = {k: encoder(v, os.path.join(OUT, f"{NAME}-{k}.mp4"), crf=20) for k, v in wavs.items()}
    mk = mark()
    keep = {}
    for i in range(n):
        t = i / FPS
        x = np.full((H, W, 3), 0.02, np.float32)
        if t < DARK[1]:
            u = sstep(t / HERO_END)                                    # the tilt: from the bar down to the table
            hf = hero[min(i, len(hero) - 1)]
            v = look(hf, lerp(0.55, 0.50, u), lerp(0.36, 0.60, u), 1.32, 0, W, H).astype(np.float32) / 255
            fade = 1 - sstep((t - DARK[0]) / (DARK[1] - DARK[0]))
            x = v * fade + 0.02 * (1 - fade)
        for top, ph, t0, frames, xs, a, b in pans:
            if t < t0:
                continue
            j = min(round((t - t0) * FPS), len(frames) - 1)
            u = sstep((t - t0) / (DUR - t0))                          # the slow drift inside each panel
            cx = xs[j] if xs is not None else lerp(a[0], b[0], u)
            cy, z, rot = lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u)
            p = look(frames[j], cx, cy, z, rot, W, ph).astype(np.float32) / 255
            # it wipes in from the left over 0.45 s, with a soft edge
            r = sstep((t - t0) / 0.45)
            edge = np.clip((r * (W + 160) - np.arange(W)) / 160, 0, 1)[None, :, None]
            x[top:top + ph] = x[top:top + ph] * (1 - edge) + p * edge
        if t >= PANELS[0][2]:                                         # thin dark seams between the panels
            for top, ph, t0, *_ in PANELS[1:]:
                if t >= PANELS[0][2]:
                    x[top - 3:top + 3] = 0.03
        mv = 0.8 * (1 - sstep((t - DARK[0]) / 0.6))                 # the mark sits on the room, not on the panels
        x = x * (1 - mk[..., 3:] * mv) + mk[..., :3] * mk[..., 3:] * mv
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        for e in encs.values():
            e.stdin.write(px.tobytes())
        if i in (30, 90, 120, 160, 200, 260, 300):
            keep[i] = px
    for e in encs.values():
        e.stdin.close()
        e.wait()
    for v in wavs.values():
        os.remove(v)
    from PIL import Image
    ims = [Image.fromarray(keep[k]).resize((270, 480)) for k in sorted(keep)]
    sheet = Image.new("RGB", (270 * len(ims), 480))
    for k, im in enumerate(ims):
        sheet.paste(im, (270 * k, 0))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep[260]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", n, "frames")


def audio(path, sound):
    """sound=True: music1-aesthetic, eased in and out; False: silent, for the master that takes the reference's
    audio in the app"""
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)
    if sound:
        raw = subprocess.run([FF, "-v", "error", "-i", os.path.join(ROOT, "brand-reels", "audio", "music1-aesthetic.mp3"),
                              "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                             capture_output=True, check=True).stdout
        mu = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        m[:len(mu)] = mu / (np.sqrt(np.mean(mu ** 2)) + 1e-9) * 10 ** (-17 / 20)
        t = np.arange(n) / SR
        m *= (np.clip(t / 0.4, 0, 1) * np.clip((DUR - t) / 0.8, 0, 1))[:, None]
        m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
