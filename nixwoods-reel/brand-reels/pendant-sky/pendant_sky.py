#!/usr/bin/env python3
"""Rosewood linear pendant, "lights" edit — after @graphicpact's DcMR2E3z519 (9.9 s, 1.9M views: three stills
brought to life with no footage — a streetlamp flickering against a sunset sky, a symmetric graphic look-up
with a red disc in teal, tower windows lighting one by one — all moved with 2D camera moves).

Rameez, 10 Oct: "think of pendant light. Background needs to be recreated. That goes off and on as shows
and then move to camera movements that you can do on an image without using credits."

  source      one real photo: the 30" rosewood linear pendant in the 5 Aug shoot (AC4I9798), cut out here
              (matte from distance to the wall colour) into an ON and an OFF plate (channel dimmed)
  background  recreated in code, no generation: a sunset sky from layered noise, a flat amber disc in a
              teal night, a deeper dusk
  camera      every move is 2.5D on stills, zero credits: parallax push (sky and pendant on separate
              layers, scaled at different rates), dolly zoom (subject holds, world swells), forward dolly
              through a row of pendants in perspective
No roll: the reference tilts its frame, but a rolled frame tips the lamp (MOTION 7.1).

On music4-genz (140 bpm, 0.4286 s) from 26.96 s:
  S1  0-10 beats   the pendant against the sunset; off/on on the beat, then on to stay; parallax push 7%
  S2  10-16        centred over an amber disc in teal; dolly zoom (disc and sky swell 38%, pendant holds)
  S3  16-24        a row of five receding; they come on one per beat, far to near, as the camera dollies in

    python3 brand-reels/pendant-sky/pendant_sky.py   # -> brand-reels/pendant-sky/NW-PENDANT-lights-9x16.mp4
"""
import glob, os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from scipy.ndimage import gaussian_filter, binary_opening

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
OUT = os.path.join(HERE, "NW-PENDANT-lights-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music4-genz.mp3")
MUSIC_IN = 26.96
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = 0.4286
S1, S2, S3 = 10, 6, 8                                   # scene lengths in beats
CORE, AMBER = np.array([255, 238, 210], np.float32) / 255, np.array([232, 162, 74], np.float32) / 255

# S1 lamp state by beat: (beat, on?) — the reference's faulty-lamp rhythm, then on to stay
FLICKER = [(0, 0), (1, 1), (1.5, 0), (2, 1), (3, 0), (3.5, 1), (4, 0), (5, 1), (7, 0), (7.5, 1)]


# ---------------------------------------------------------------- the pendant, cut out of AC4I9798
def pendant_plates():
    f = glob.glob(os.path.join(SHOOT, "*AC4I9798*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    x0, x1, y0, y1 = 572 - 14, 2974 + 14, 1645 - 14, 1768 + 10       # measured bar box (+ margin)
    a = np.asarray(im.crop((x0, y0 - 60, x1, y1 + 60))).astype(np.float32) / 255
    wall = np.concatenate([a[:40], a[-40:]]).mean(0)                    # wall colour per column, above + below
    wall = gaussian_filter(wall, (25, 0))
    d = np.sqrt(((a - wall[None]) ** 2).sum(2))
    m = np.clip((d - 0.06) / 0.10, 0, 1)
    m[:52] = 0; m[-50:] = 0                                             # only the bar's rows
    core = binary_opening(m > 0.5, iterations=2)
    m = m * gaussian_filter(core.astype(np.float32), 1.5).clip(0, 1) ** 0.5
    L = a.mean(2)
    chan = np.clip((L - 0.72) / 0.18, 0, 1) * (m > 0.2)                 # the lit channel
    rgb_on = a.copy()
    rgb_on = rgb_on * (1 - chan[..., None]) + CORE * chan[..., None]
    off = np.array([0.30, 0.27, 0.24], np.float32) * (0.6 + 0.4 * L[..., None])
    rgb_off = a * (1 - chan[..., None]) + off * chan[..., None]
    # cut to the bar's rows
    sl = slice(46, a.shape[0] - 46)
    on = np.dstack([rgb_on[sl], m[sl]]); offp = np.dstack([rgb_off[sl], m[sl]])
    ch = chan[sl]
    return on, offp, ch                                                  # float RGBA, channel mask


def to_img(rgba):
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- backgrounds, recreated in code
def fbm(h, w, seed, scales=(200, 100, 48, 22, 10, 5), weights=(1, 0.6, 0.38, 0.24, 0.14, 0.08)):
    rng = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    for s, wt in zip(scales, weights):
        n = rng.normal(0, 1, (h // 4 + 2, w // 4 + 2)).astype(np.float32)
        n = gaussian_filter(n, s / 4)
        n = np.array(Image.fromarray(n).resize((w, h), Image.BICUBIC))
        out += wt * n / (n.std() + 1e-6)
    return (out - out.mean()) / out.std()


def lerp_stops(t, stops):
    t = np.clip(t, 0, 1)
    out = np.zeros(t.shape + (3,), np.float32)
    for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
        u = np.clip((t - t0) / (t1 - t0), 0, 1)[..., None]
        sel = ((t >= t0) & (t <= t1))[..., None]
        out = np.where(sel, np.array(c0) / 255 * (1 - u) + np.array(c1) / 255 * u, out)
    return out


def sunset_sky(w, h, seed, late=0.0):
    y = np.linspace(0, 1, h)[:, None] * np.ones((1, w))
    stops = [(0, (20, 30, 58)), (0.45, (62, 58, 92)), (0.75, (178, 104, 78)), (1, (226, 146, 92))]
    if late:
        stops = [(0, (10, 16, 34)), (0.5, (30, 34, 60)), (0.8, (98, 64, 70)), (1, (150, 92, 70))]
    sky = lerp_stops(y, stops)
    n = fbm(h, w, seed)
    dens = np.clip((n - 0.05) * 1.5, 0, 1) ** 1.1                       # cloud cover, crisp edges
    ny = np.gradient(gaussian_filter(n, 6), axis=0)                     # undersides catch the sun
    warm = np.clip(0.35 + y * 0.9 + ny * 6, 0, 1)[..., None]
    lit = np.array([238, 156, 104]) / 255 * (1 - late * 0.5)
    shadow = np.array([54, 46, 66]) / 255 * (1 - late * 0.4)
    cloud = shadow * (1 - warm) + lit * warm
    return sky * (1 - dens[..., None] * 0.85) + cloud * dens[..., None] * 0.85


def teal_disc(w, h, r):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    rr = np.sqrt((xx - w / 2) ** 2 + (yy - h * 0.46) ** 2)
    teal = lerp_stops(np.clip(rr / (0.75 * h), 0, 1), [(0, (22, 70, 76)), (1, (6, 24, 30))])
    disc = np.clip(r - rr + 1.5, 0, 1)[..., None]                       # flat, crisp edge
    halo = np.exp(-np.clip(rr - r, 0, None) / (0.22 * r))[..., None] * 0.35
    out = teal * (1 - disc) + AMBER * disc
    return np.clip(out + AMBER * halo * (1 - disc) * 0.6, 0, 1)


def finish(a, rng, vign=True):
    if vign:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        a = a * np.clip(1.08 - 0.35 * r, 0, 1)[..., None]
    a = a + rng.normal(0, 2.2 / 255, (H, W, 1))                         # MOTION: grain on flat grounds
    return (np.clip(a, 0, 1) * 255).astype(np.uint8)


# ---------------------------------------------------------------- compositing helpers
def place(canvas, layer, cx, cy, scale):
    """Alpha-composite a float RGBA layer onto a PIL RGBA canvas, centred at (cx, cy), at a scale."""
    img = to_img(layer) if isinstance(layer, np.ndarray) else layer
    w, h = max(1, round(img.width * scale)), max(1, round(img.height * scale))
    img = img.resize((w, h), Image.LANCZOS)
    canvas.alpha_composite(img, (round(cx - w / 2), round(cy - h / 2))) if (cx - w / 2 >= 0 and cy - h / 2 >= 0 and cx + w / 2 <= W and cy + h / 2 <= H) \
        else canvas.paste(img, (round(cx - w / 2), round(cy - h / 2)), img)
    return canvas


def draw_cables(canvas, xs, y_bar, top=-10, width=3):
    d = ImageDraw.Draw(canvas)
    for x in xs:
        d.line((x, top, x, y_bar), fill=(28, 22, 20, 235), width=width)


def lamp(canvas, plates, cx, cy, scale, level, light, cables=True):
    """One pendant: cables, then the OFF plate with the ON plate faded in by `level`. Its channel goes into
    `light` (a screen-space mask) so the glow is built at screen scale by add_light()."""
    on, off, ch, w_px, h_px = plates
    if cables:
        bw = w_px * scale
        draw_cables(canvas, [cx - bw * 0.36, cx + bw * 0.36], cy - h_px * scale / 2, width=max(2, round(3 * scale / 0.38)))
    mix = off * (1 - level) + on * level
    place(canvas, mix, cx, cy, scale)
    if level > 0:
        m = Image.fromarray((ch * 255).astype(np.uint8)).resize((max(1, round(w_px * scale)), max(1, round(h_px * scale))), Image.BILINEAR)
        x0, y0 = round(cx - m.width / 2), round(cy - m.height / 2)
        a = np.asarray(m).astype(np.float32) / 255 * level
        xs, ys = max(x0, 0), max(y0, 0)
        xe, ye = min(x0 + m.width, W), min(y0 + m.height, H)
        if xe > xs and ye > ys:
            light[ys:ye, xs:xe] = np.maximum(light[ys:ye, xs:xe], a[ys - y0:ye - y0, xs - x0:xe - x0])
    return canvas


def add_light(rgb, light, strength=1.0):
    """MOTION's glowing line at screen scale: cream core, amber halo (~55%) and a wide halo (~25%), plus a
    soft haze thrown downward. Additive, so it lights whatever is behind it."""
    if light.max() <= 0:
        return rgb
    sm = light[::4, ::4]
    near = gaussian_filter(sm, 3.5)
    wide = gaussian_filter(sm, 26)
    down = gaussian_filter(np.roll(gaussian_filter(sm, (40, 10)), 30, axis=0), 6)
    up = lambda x: np.array(Image.fromarray(x.astype(np.float32)).resize((W, H), Image.BILINEAR))
    near, wide, down = up(near), up(wide), up(down)
    glow = (AMBER * (near * 4.0)[..., None] * 0.55 + AMBER * (wide * 9.0)[..., None] * 0.25
            + CORE * (near * 4.0)[..., None] * 0.35 + AMBER * (down * 10.0)[..., None] * 0.10)
    return np.clip(rgb + glow * strength, 0, 1)


def mux(video, total):
    """music4-genz from MUSIC_IN, normalised in numpy (an ffmpeg limiter let the AAC encode peak at 1.3)."""
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{MUSIC_IN:.3f}", "-i", MUSIC, "-t", f"{total:.3f}", "-ac", "2",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    k = int(0.05 * sr); x[:k] *= np.linspace(0, 1, k)[:, None]
    k = int(0.8 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x = x * (0.6 / max(np.abs(x).max(), 1e-3))
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", video, "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", OUT],
                   check=True)
    os.remove(OUT + ".wav")


def main():
    on, off, ch = pendant_plates()
    plates = (on, off, ch, on.shape[1], on.shape[0])
    rng = np.random.default_rng(11)

    sky1 = sunset_sky(int(W * 1.2), int(H * 1.2), seed=4)                # oversized, the camera moves in it
    sky3 = sunset_sky(int(W * 1.3), int(H * 1.3), seed=9, late=1.0)
    sky1_img = Image.fromarray((sky1 * 255).astype(np.uint8))
    sky3_img = Image.fromarray((sky3 * 255).astype(np.uint8))

    n1, n2, n3 = [round(s * B * FPS) for s in (S1, S2, S3)]
    nf = n1 + n2 + n3
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    base_scale = 940 / on.shape[1]                                       # the bar 940 px wide in S1
    for f in range(nf):
        t = f / FPS
        beat = t / B
        if f < n1:                                                       # S1: sunset, flicker, parallax push
            u = f / (n1 - 1); e = u * u * (3 - 2 * u)
            zs = 1 + 0.03 * e                                            # the sky moves less (far)
            bw, bh = W / zs, H / zs
            ox = (sky1_img.width - bw) / 2 - 40 * e; oy = (sky1_img.height - bh) / 2 + 30 * e
            canvas = sky1_img.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + bw, oy + bh)).convert("RGBA")
            state = [s for b_, s in FLICKER if b_ <= beat][-1]
            last = [b_ for b_, s in FLICKER if b_ <= beat][-1]
            ramp = 0.30 if last == FLICKER[-1][0] else 0.05             # the final switch-on warms up 0.3 s
            k = min((t - last * B) / ramp, 1)
            level = k if state else 1 - k if last > 0 else 0.0
            light = np.zeros((H, W), np.float32)
            lamp(canvas, plates, W / 2 + 30 * e, 760 - 20 * e, base_scale * (1 + 0.07 * e), max(level, 0), light)
            rgb = add_light(np.asarray(canvas.convert("RGB")).astype(np.float32) / 255, light)
            fr = finish(rgb, rng)
        elif f < n1 + n2:                                                # S2: dolly zoom over the disc
            u = (f - n1) / (n2 - 1); e = u * u * (3 - 2 * u)
            bg = teal_disc(W, H, r=300 * (1 + 0.38 * e))
            canvas = Image.fromarray((bg * 255).astype(np.uint8)).convert("RGBA")
            light = np.zeros((H, W), np.float32)
            lamp(canvas, plates, W / 2, H * 0.46, base_scale * 0.9, 1.0, light)
            rgb = add_light(np.asarray(canvas.convert("RGB")).astype(np.float32) / 255, light, 0.8)
            fr = finish(rgb, rng, vign=False)
        else:                                                            # S3: a row, one by one, dolly forward
            u = (f - n1 - n2) / (n3 - 1); e = u * u * (3 - 2 * u)
            zs = 1 + 0.06 * e
            bw, bh = W / zs, H / zs
            ox, oy = (sky3_img.width - bw) / 2, (sky3_img.height - bh) / 2
            canvas = sky3_img.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + bw, oy + bh)).convert("RGBA")
            cam = 1.1 * e                                                # the camera moves forward in depth
            vpx, vpy = W * 0.62, H * 0.58
            b3 = beat - S1 - S2
            light = np.zeros((H, W), np.float32)
            for i in range(6)[::-1]:                                     # far first, so near ones draw over
                z = 2.2 + i * 1.9 - cam
                s = base_scale * 1.6 / z
                X, Y = -900, -1900                                       # one line, above and left of the eye
                cx, cy = vpx + X / z, vpy + Y / z * 0.55
                on_at = 5 - i                                            # far (i=5) comes on first
                lvl = np.clip((b3 - 1 - on_at) * B / 0.25, 0, 1)
                lamp(canvas, plates, cx, cy, s, float(lvl), light)
            rgb = add_light(np.asarray(canvas.convert("RGB")).astype(np.float32) / 255, light)
            fr = finish(rgb, rng)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close(); proc.wait()
    total = nf / FPS
    mux(OUT + ".video.mp4", total)
    os.remove(OUT + ".video.mp4")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f}s")


if __name__ == "__main__":
    if sys.argv[1:] == ["--remux"]:                                      # re-do the sound on the existing render
        v = OUT + ".v.mp4"
        subprocess.run([FF, "-v", "error", "-y", "-i", OUT, "-an", "-c:v", "copy", v], check=True)
        mux(v, float(subprocess.run([FF, "-i", v], capture_output=True, text=True).stderr.split("Duration: ")[1].split(",")[0].split(":")[-1]))
        os.remove(v)
    else:
        main()
