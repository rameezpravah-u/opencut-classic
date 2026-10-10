#!/usr/bin/env python3
"""NixWall match-cut reel — a recreation of @rippotai's DYHpEYFJYfY (12.6 s, 2M views: a brick held still
between two hands while guide lines lock onto it, then a rapid cut through a dozen places with the brick
never moving). Rameez, 10 Oct: "Instead of a lamp use NixWall" — the solid wood wall bar with the warm
downlight (the "The wall was fine" ad).

Clean images only: the four 5 Aug shoot frames of the compact wooden wall light (AC4I9629 40-inch over the
dark artwork, 9641 over the TV, 9644 and 9645 24-inch over the pink artwork). Each is cropped so the bar
lands in exactly the same place and width on screen (bar centre x 540, y 384, 864 px wide). Where a frame
has too little wall above the bar for that crop (9629, 9641), the plain wall is extended upward from its
own top rows. Each wall also appears relit to evening (room down to a teal dark, the bar's own light kept,
its pool on the wall), so four frames give eight looks. Nothing generated.

  0.00-6.00  9644 held still; amber guide lines glide in and lock onto the bar's ends, centre, top and
             bottom, one per beat of the build, each with a soft tick
  6.00-end   the drop: 20 cuts on the half-beat (0.302 s), the bar locked in place: a bar of the
             four walls by day, then lights out and three rounds of the same walls at night
Music: music3-design from 4.752 s, so its drop (10.752 s) lands on the first cut.

    python3 brand-reels/matchcut/matchcut_reel.py   # -> brand-reels/matchcut/NW-MATCHCUT-nixwall-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageOps
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
OUT = os.path.join(HERE, "NW-MATCHCUT-nixwall-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music3-design.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
BEAT, DROP = 0.6036, 10.752
P1 = 6.0                                           # the still; the drop lands here
HALF = BEAT / 2
AMBER = (232, 162, 74)

# bar bounding box in each photo, as fractions (x0, x1, y0, y1), measured by brand-reels/matchcut (dark wood
# component in the top 30% of the frame)
BARS = {"9629": (0.1721, 0.8564, 0.0614, 0.1016), "9641": (0.2368, 0.7160, 0.0651, 0.1089),
        "9644": (0.2423, 0.7215, 0.1111, 0.1586), "9645": (0.1901, 0.4730, 0.1195, 0.1809)}
BAR_W, BAR_CX, BAR_CY = 864, 540, 384              # where the bar sits on screen in every shot
# a bar of day (8 half-beats), then lights out on the bar line and three rounds of night; no day/night
# flicker (MOTION: never strobe)
SEQ = ["9629d", "9645d", "9641d", "9644d"] * 2 + ["9629n", "9645n", "9641n", "9644n"] * 3          # ends held on 9644: badge, artwork
N_CUTS = 20


def ease_expo_out(u):
    u = min(max(u, 0.0), 1.0)
    return 1 - 2 ** (-10 * u) if u < 1 else 1.0


def frame_of(key):
    """Crop (and where needed extend the wall upward) so the bar lands at BAR_CX/BAR_CY, BAR_W wide.
    Returns the 1080x1920 float image and the bar box in output pixels."""
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    x0f, x1f, y0f, y1f = BARS[key]
    bw = (x1f - x0f) * im.width
    s = BAR_W / bw                                                    # output px per photo px
    cw, ch = W / s, H / s
    bcx, bcy = (x0f + x1f) / 2 * im.width, (y0f + y1f) / 2 * im.height
    left, top = bcx - BAR_CX / s, bcy - BAR_CY / s
    assert left >= 0 and left + cw <= im.width and top + ch <= im.height, (key, left, top, cw, ch)
    pad = max(0, -top)                                                # wall missing above the bar, photo px
    src = im.resize((round(cw * s), round((ch - pad) * s)), Image.LANCZOS,
                    box=(left, max(top, 0), left + cw, top + ch))
    a = np.asarray(src).astype(np.float32) / 255
    if pad > 0:                                                       # extend the plain wall upward
        p = round(pad * s)
        row = gaussian_filter(a[:24].mean(0), (40, 0))                # the wall's own colour, column by column
        trend = (a[24:64].mean() - a[:24].mean()) / 40                # its vertical falloff, continued
        ext = row[None] - trend * np.arange(p, 0, -1)[:, None, None] * 0.6
        rng = np.random.default_rng(int(key))
        noise = a[:24] - gaussian_filter(a[:24], (2, 2, 0))           # the photo's own grain
        ext = ext + rng.choice(noise.reshape(-1, 3), size=(p * W,)).reshape(p, W, 3)
        a = np.concatenate([np.clip(ext, 0, 1), a], 0)
        k = 40                                                        # feather the seam into the photo's top rows
        w_ = np.linspace(0.5, 1, k)[:, None, None]
        a[p:p + k] = a[p:p + k] * w_ + (row[None] + a[p:p + k] - gaussian_filter(a[p:p + k], (3, 3, 0))) * (1 - w_)
    a = a[:H]
    bh = (y1f - y0f) * im.height * s
    box = (BAR_CX - BAR_W / 2, BAR_CX + BAR_W / 2, BAR_CY - bh / 2, BAR_CY + bh / 2)
    return a, box


def day(a):
    return np.clip(a * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)


def night(a, box, key):
    """The same wall after dark: the room falls to a teal dark, the bar's light and its pool on the wall stay."""
    x0, x1, y0, y1 = [int(round(v)) for v in box]
    L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    seed = np.zeros((H, W), np.float32)
    seed[y1 - 6:y1 + 4, x0 + 10:x1 - 10] = 1                         # the light leaves the bar's underside
    small = seed[::4, ::4]
    near = gaussian_filter(small, (6, 14)).repeat(4, 0).repeat(4, 1)[:H, :W]
    wide = gaussian_filter(small, (40, 60)).repeat(4, 0).repeat(4, 1)[:H, :W]
    below = np.clip((np.arange(H)[:, None] - (y0 - 10)) / 30, 0.15, 1)  # it throws down, barely up
    pool = (near / near.max() * 1.0 + wide / wide.max() * 0.75) * below
    amb = np.array([0.17, 0.21, 0.23], np.float32)                     # teal room light
    out = a * amb[None, None] + a * pool[..., None] * np.array([1.08, 0.94, 0.74], np.float32)
    strip = np.zeros((H, W), np.float32)                              # the strip itself stays at full
    strip[y0:y1 + 8, x0:x1] = np.clip((L[y0:y1 + 8, x0:x1] - 0.62) / 0.2, 0, 1)
    strip = gaussian_filter(strip, 1.2)[..., None]
    out = out * (1 - strip) + a * strip
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    out = out * np.clip(1.08 - 0.35 * r, 0, 1)[..., None]
    rng = np.random.default_rng(int(key) + 1)
    out = out + rng.normal(0, 0.012, (H, W, 1)).astype(np.float32)
    return np.clip(out, 0, 1)


def guide_lines(t, box):
    """The reference's construction lines, in amber: each glides in (expo-out, 0.5 s) and locks on a beat."""
    x0, x1, y0, y1 = box
    beats = [P1 - k * BEAT for k in range(8, 0, -1)]                  # 1.17 ... 5.40
    lines = [("v", x0, W + 30, beats[0]), ("v", x1, W + 30, beats[1]), ("v", W / 2, W + 30, beats[2]),
             ("h", y0, -30, beats[4]), ("h", y1, -30, beats[5]),
             ("h", y1 + 1.6 * (y1 - y0), H + 30, beats[6])]
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for kind, target, start, settle in lines:
        u = (t - (settle - 0.5)) / 0.5
        if u <= 0:
            continue
        p = start + (target - start) * ease_expo_out(u)
        if kind == "v":
            d.line((p + 2, 0, p + 2, H), fill=(0, 0, 0, 60), width=3); d.line((p, 0, p, H), fill=AMBER + (240,), width=3)
        else:
            d.line((0, p + 2, W, p + 2), fill=(0, 0, 0, 60), width=3); d.line((0, p, W, p), fill=AMBER + (240,), width=3)
    return lay, [settle for *_, settle in lines]


def main():
    looks = {}
    for key in BARS:
        a, box = frame_of(key)
        looks[key + "d"] = (Image.fromarray((day(a) * 255).astype(np.uint8)), box)
        looks[key + "n"] = (Image.fromarray((night(day(a), box, key) * 255).astype(np.uint8)), box)
    hero, hero_box = looks["9644d"]
    cuts = SEQ[:N_CUTS]
    total = P1 + N_CUTS * HALF + 2 * HALF                              # the last look (NixWall at night) holds
    nf = round(total * FPS)

    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    ticks = []
    for f in range(nf):
        t = f / FPS
        if t < P1:
            fr = hero.convert("RGBA")
            lay, ticks = guide_lines(t, hero_box)
            fr.alpha_composite(lay)
            fr = fr.convert("RGB")
        else:
            i = min(int((t - P1) / HALF), N_CUTS - 1)
            fr = looks[cuts[i]][0]
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()

    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{DROP - P1:.3f}", "-i", MUSIC, "-t", f"{total:.3f}", "-ac", "2",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    mus = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    n = round(total * sr); mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n] * 0.9
    rng = np.random.default_rng(3)
    click = rng.normal(0, 1, int(0.025 * sr)).astype(np.float32)       # a soft tick as each line locks
    click = np.convolve(click, np.ones(6) / 6, "same") * np.exp(-np.linspace(0, 9, len(click)))
    click = click / np.abs(click).max() * 0.22
    for s in ticks:
        a = int(s * sr); mus[a:a + len(click)] += click[:, None]
    k = int(0.8 * sr); mus[-k:] *= np.linspace(1, 0, k)[:, None]
    mus = mus * min(1.0, 0.7 / max(np.abs(mus).max(), 1e-3))
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mus * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{nf / FPS:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{nf / FPS:.2f}s, {N_CUTS} cuts")


if __name__ == "__main__":
    main()
