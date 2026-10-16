"""NixWoods "one lamp, every move": the Rubik's Cube lamp held centre frame while the camera snaps around it, after
@d2_shots' cow reel (instagram.com/reel/DdhF_atB_JM, 7.04 s). The reference is sixteen fast camera moves (pull-back,
push-in, whip pan, dutch roll, low angle, a pass behind a foreground post), each eased in 0.1-0.25 s and followed by
a near-still hold. Our moves land on its measured move frames, so its audio sits on them via "Use audio".

Footage, all real and on the lamp's own sheesham base (prototype clips on a white LED slab are left out because they
show a light the product does not have):
  14-1.mp4                  the 5 Aug shoot hero clip (rubik-reels/src): green, red, amber, warm, then a hand turning it
  NW-RAW-...-92973dce/2e5660bf  owner phone clips, the camera trucking past the lamp (festive-ad-cuts/src)
  IMG_6986, 3076C2D2         owner workshop clips from Drive (library/cache, fetched with library/fetch.py)
The moves are digital (crop, scale, roll) on that footage; the two trucking clips and IMG_6986 also move for real.

    python3 brand-reels/one-lamp-moves/one_lamp_moves.py
"""
import glob, math, os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import FF, FPS, H, W               # noqa: E402
from made_well import encoder, mark                  # noqa: E402

OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261016-rubiks-cube-table-lamp-sheesham-wood-one-lamp-every-move-v1"
SR = 48000
DUR = 7.04
CACHE = os.path.join(ROOT, "library", "cache")
HERO = os.path.join(ROOT, "rubik-reels", "src", "14-1.mp4")
TRUCK1 = os.path.join(ROOT, "brand-reels", "festive-ad-cuts", "src", "NW-RAW-20261011-unknown-92973dce.mov")
TRUCK2 = os.path.join(ROOT, "brand-reels", "festive-ad-cuts", "src", "NW-RAW-20261011-unknown-2e5660bf.mov")
CLOSE = (glob.glob(os.path.join(CACHE, "*-IMG_6986.mov")) or [os.path.join(CACHE, "IMG_6986.mov")])[0]   # library/fetch.py

# the reference's camera moves (start, end), measured frame by frame on its 24 fps file
MOVES = [(0.00, 0.21), (0.42, 0.62), (0.92, 1.10), (1.54, 1.71), (1.83, 1.92), (2.17, 2.35), (2.79, 3.00),
         (3.08, 3.21), (3.46, 3.71), (3.875, 4.10), (4.375, 4.50), (4.875, 5.13), (5.21, 5.33), (5.625, 5.83),
         (6.25, 6.42), (6.54, 6.60)]

# shots: (source, in-point s, tracked?, [framings (cx, cy, zoom, roll deg)], transition into the next shot)
# cx, cy: where the lamp sits in the source, 0-1; zoom 1 = the whole 9:16 frame; "track" follows the lit glass.
SHOTS = [
    (HERO,   0.30, False, [(0.30, 0.55, 5.0, 0), (0.30, 0.55, 3.0, 0), (0.50, 0.50, 1.0, 0), (0.30, 0.60, 2.0, 0)],
     "push"),                                   # ECU of the glass pulls back, back again to wide, then a push in
    (TRUCK1, 0.00, True,  [(0, 0, 1.70, 0), (0, 0, 1.95, 0)], "tilt"),           # the camera trucks past for real
    (CLOSE,  0.20, False, [(0.50, 0.62, 1.00, 0), (0.50, 0.45, 1.50, 0), (0.50, 0.50, 1.25, -3)], "spin"),  # low
    (HERO,   3.40, False, [(0.36, 0.69, 2.10, 9)], "whip"),                     # dutch on the red face
    (HERO,   6.00, False, [(0.28, 0.54, 1.90, 0)], "whip"),                     # whip pan to amber
    (CLOSE,  1.20, False, [(0.50, 0.50, 1.10, 0)], "push"),                     # behind the post as the camera passes
    (HERO,  12.30, False, [(0.45, 0.58, 1.60, 0), (0.45, 0.56, 2.10, 0)], "whip"),   # a hand turns it
    (TRUCK2, 0.40, True,  [(0, 0, 1.70, 0)], "pull"),
    (HERO,   9.30, False, [(0.30, 0.62, 1.55, 0), (0.30, 0.62, 1.45, 0)], None),     # warm white, settles
]


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def decode(path, t_in, secs):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{max(t_in, 0):.3f}", "-i", path, "-t", f"{secs:.3f}", "-vf",
                          "fps=30,scale=1080:1920:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, 1920, 1080, 3)


def track(frames):
    """centre of the lit glass in each frame (the brightest blob), smoothed"""
    pts = []
    for f in frames:
        c = cv2.resize(f, (108, 192)).astype(np.float32)
        g = (c[..., 0] + c[..., 1]) / 2 - c[..., 2]          # the warm glass, not the white wall behind it
        m = g > np.percentile(g, 85)
        ys, xs = np.nonzero(m)
        pts.append((xs.mean() / 108, ys.mean() / 192))
    p = np.array(pts)
    k = np.ones(7) / 7
    pad = np.pad(p, ((3, 3), (0, 0)), mode="edge")
    return np.stack([np.convolve(pad[:, i], k, "valid") for i in range(2)], 1)


def view(frame, cx, cy, z, rot):
    """the 1080x1920 output of one framing: lamp centre (cx, cy) brought to the frame centre at zoom z, rolled"""
    sh, sw = frame.shape[:2]
    s = z = max(z, 1.0)                     # source is 1080x1920 already: zoom 1 shows all of it
    hw, hh = W / 2 / s, H / 2 / s           # half the visible source size
    r = abs(math.radians(rot))
    need_w = hw * math.cos(r) + hh * math.sin(r)       # keep the rolled view inside the source
    need_h = hw * math.sin(r) + hh * math.cos(r)
    x = min(max(cx * sw, need_w), sw - need_w) if need_w * 2 < sw else sw / 2
    y = min(max(cy * sh, need_h), sh - need_h) if need_h * 2 < sh else sh / 2
    M = cv2.getRotationMatrix2D((x, y), rot, s)
    M[:, 2] += (W / 2 - x, H / 2 - y)
    return cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def timeline():
    """for every output frame, the shot, the framing parameters and the source frame, with motion-blur subsamples"""
    # hold intervals: framing k of the whole reel is held between move k-1 and move k
    flat = []                                  # (shot index, framing index)
    for si, s in enumerate(SHOTS):
        for fi in range(len(s[3])):
            flat.append((si, fi))
    assert len(flat) == len(MOVES) + 1, (len(flat), len(MOVES))
    return flat


def main():
    os.makedirs(OUT, exist_ok=True)
    flat = timeline()
    # when each shot is on screen (from the middle of the move into it to the middle of the move out of it)
    span = {}
    for k, (si, fi) in enumerate(flat):
        a = 0.0 if k == 0 else (MOVES[k - 1][0] + MOVES[k - 1][1]) / 2
        b = DUR if k == len(MOVES) else (MOVES[k][0] + MOVES[k][1]) / 2
        lo, hi = span.get(si, (a, b))
        span[si] = (min(lo, a), max(hi, b))
    # the source clock: each shot starts at its in-point when it first appears
    frames, centres = {}, {}

    def load(si):
        if si not in frames:
            s = SHOTS[si]
            secs = span[si][1] - span[si][0] + 0.3
            frames[si] = decode(s[0], s[1], secs)
            centres[si] = track(frames[si]) if s[2] else None
        return frames[si]

    def params(si, fi):
        cx, cy, z, rot = SHOTS[si][3][fi]
        return [cx, cy, z, rot]

    def render(si, t, p):
        fr = load(si)
        i = min(len(fr) - 1, max(0, round((t - span[si][0]) * FPS)))
        cx, cy, z, rot = p
        if SHOTS[si][2]:
            cx, cy = centres[si][i]
        return view(fr[i], cx, cy, z, rot).astype(np.float32)

    def state(t):
        """list of (shot, params) to render at time t; transitions between shots push the outgoing view off and
        bring the incoming one in from the other side"""
        for k, (a, b) in enumerate(MOVES):
            if t < a:
                si, fi = flat[k]
                return si, params(si, fi)
            if t <= b:
                u = ease((t - a) / max(b - a, 1e-3))
                (s0, f0), (s1, f1) = flat[k], flat[k + 1]
                p0, p1 = params(s0, f0), params(s1, f1)
                if s0 == s1:
                    return s0, [p0[j] + (p1[j] - p0[j]) * u for j in range(4)]
                kind = SHOTS[s0][4]
                if u < 0.5:
                    v, si, p, sign = u * 2, s0, p0[:], 1
                else:
                    v, si, p, sign = (1 - u) * 2, s1, p1[:], -1
                if kind == "whip":
                    p[0] += sign * 0.9 * v / p[2]
                elif kind == "tilt":
                    p[1] += sign * 0.6 * v / p[2]
                elif kind == "spin":
                    p[3] += sign * 25 * v
                    p[2] *= 1 + 1.2 * v
                elif kind == "push":
                    p[2] *= (1 + 1.8 * v) if sign > 0 else 1 / (1 + 0.6 * v) * (1 + 1.2 * v)
                elif kind == "pull":
                    p[2] *= 1 / (1 + 0.45 * v) if sign > 0 else (1 + 1.0 * v)
                return si, p
        si, fi = flat[-1]
        return si, params(si, fi)

    wavs = {k: os.path.join(OUT, f".{k}.wav") for k in ("in-app-audio", "music4")}
    audio(wavs["in-app-audio"], False)
    audio(wavs["music4"], True)
    encs = {k: encoder(v, os.path.join(OUT, f"{NAME}-{k}.mp4"), crf=21) for k, v in wavs.items()}
    mk = mark()
    n = round(DUR * FPS)
    keep = []
    for i in range(n):
        t0 = i / FPS
        acc = np.zeros((H, W, 3), np.float32)
        subs = 7
        for j in range(subs):                    # a 180-degree shutter: blur across half the frame interval
            t = t0 + (j / (subs - 1) - 0.5) * 0.5 / FPS
            si, p = state(min(max(t, 0), DUR))
            acc += render(si, max(t, 0), p)
        x = acc / subs / 255
        x = x * 0.98 + 0.02                      # MOTION.md: blacks keep a little air
        x = x * (1 - mk[..., 3:] * 0.85) + mk[..., :3] * mk[..., 3:] * 0.85
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        for e in encs.values():
            e.stdin.write(px.tobytes())
        if i % 9 == 4:
            keep.append(px)
        for si in list(frames):                  # free shots that are done
            if span[si][1] + 0.1 < t0:
                del frames[si]
    for e in encs.values():
        e.stdin.close()
        e.wait()
    for v in wavs.values():
        os.remove(v)
    ims = [Image.fromarray(k).resize((180, 320)) for k in keep[:24]]
    sheet = Image.new("RGB", (180 * 12, 320 * 2), (20, 20, 20))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % 12) * 180, (i // 12) * 320))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep[-1]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", n, "frames")


def audio(path, sound):
    """sound=True: music4-genz from its drop (26.0 s) with a soft whoosh on each move; False: silent, for the master
    that takes the reference's audio in the app"""
    n = int(DUR * SR)
    m = np.zeros((n, 2), np.float32)
    if sound:
        def load(p, ss=0.0):
            raw = subprocess.run([FF, "-v", "error", "-ss", f"{ss:.3f}", "-i", p, "-t", f"{DUR:.3f}", "-ac", "2",
                                  "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout
            return np.frombuffer(raw, np.float32).reshape(-1, 2)
        mu = load(os.path.join(ROOT, "brand-reels", "audio", "music4-genz.mp3"), 26.0 - 1.433 + 1.54)
        mu = mu[:n] / (np.sqrt(np.mean(mu[:n] ** 2)) + 1e-9) * 10 ** (-17 / 20)
        m[:len(mu)] += mu
        wh = load(os.path.join(ROOT, "brand-reels", "audio", "sfx-whoosh.mp3"))
        wh = wh / (np.abs(wh).max() + 1e-9)
        peak = int(np.argmax(np.abs(wh[:, 0])))
        for a, b in MOVES:
            if b - a < 0.1:
                continue
            i0 = int((a + b) / 2 * SR) - peak
            seg = wh[max(0, -i0):]
            i0 = max(0, i0)
            seg = seg[: n - i0] * 10 ** (-14 / 20)
            m[i0:i0 + len(seg)] += seg
        t = np.arange(n) / SR
        m *= np.clip((DUR - t) / 0.35, 0, 1)[:, None]
        m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
