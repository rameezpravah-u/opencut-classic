#!/usr/bin/env python3
"""NixWoods "raw teak to warm light" — a recreation of DdorMSnv-Pk (20.5 s, an interior site going from bare
shell to finished home, cut inside a phone editor's timeline). Rameez, 9 Oct: raw workshop footage for the
build-up, clean images for the finished rooms.

  build-up  real workshop phone clips (shelf-reels/src, floor-reels/src): planks being finished, raw teak
            bars, the first light in the channels. Drive's raw workshop .MOVs (7-130 MB) are over the
            connector's download cap, so these are the repo copies of that footage.
  reveal    the 5 Aug 2026 studio shoot (drive-pull/shoot-20260805, never the watermarked archive),
            cropped to 9:16 with a slow creep. Nothing generated.

The reference's grammar, copied:
  - an editor strip (filmstrip clips, trim handles, a fixed white playhead, "+") scrolls left at a constant
    speed; whatever sits under the playhead plays full-screen, a gap is black
  - the clip's length sits above the strip ("1.3s")
  - the sound only plays while a clip is under the playhead, so the build-up stutters; once the clips butt
    up against each other the music flows and the cuts tighten
Cuts land on music5-3040's beat (94 bpm, 0.6385 s). Music starts 0.7185 s in so its lift (beat 16) lands
on the first abutting cut.

    python3 brand-reels/timeline/timeline_reel.py   # -> brand-reels/timeline/NW-TIMELINE-raw-teak-to-warm-light-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
A = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "NW-TIMELINE-raw-teak-to-warm-light-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music5-3040.mp3")
MUSIC_IN = 0.7185
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = 0.6385
GAP_BLACK = (9, 8, 7)                                  # MOTION: no pure black
INK, AMBER_DK = (58, 38, 24), (176, 104, 40)

# the strip, measured off the reference and scaled 720 -> 1080
SX0, SX1, SY0, SY1 = 172, 953, 436, 558               # band
PH = 562                                              # fixed playhead x
V = 330.0                                             # scroll speed, px per second
TILE_H = SY1 - SY0 - 8
TILE_W = round(TILE_H * 9 / 16)
LABEL_Y = 318

# (kind, source, in-point s or crop (cx, cy, h), beats); None = gap
V_ = "video"; P_ = "photo"
TIMELINE = [
    (V_, "shelf-reels/src/IMG_7745.mp4", 0.0, 2), None,    # hands finishing dark planks
    (V_, "floor-reels/src/nx05-7920.mp4", 3.4, 2), None,   # a raw teak bar in the hand
    (V_, "floor-reels/src/nx06-7921.mp4", 2.0, 2), None,   # the bare grain
    (V_, "shelf-reels/src/IMG_7749.mp4", 1.4, 2), None,    # first light in the channels
    (V_, "floor-reels/src/nx06-7921.mp4", 6.1, 2), None,   # a lit bar, held up
    (V_, "curve-reels/src/IMG_7752.mp4", 2.0, 1),          # from here on the clips touch
    (P_, "9665", (0.50, 0.5, 1.0), 1),                     # dining room, linear pendant
    (P_, "9776", (0.45, 0.5, 1.0), 1),                     # living room at dusk, floor lamp
    (P_, "9751", (0.40, 0.5, 1.0), 1),                     # bedroom, spiral
    (P_, "9798", (0.50, 0.5, 1.0), 1),                     # pendant over the table, warm
    (P_, "9629", (0.50, 0.5, 1.0), 0.5),
    (P_, "9706", (0.42, 0.5, 1.0), 0.5),
    (P_, "9882", (0.50, 0.5, 1.0), 0.5),
    (P_, "9861", (0.55, 0.5, 1.0), 0.5),
    (P_, "9658", (0.50, 0.5, 1.0), 0.5),
    (P_, "9652", (0.53, 0.5, 1.0), 0.5),
    (P_, "9815", (0.58, 0.5, 1.0), 6),                     # NixLine and the plant, as the reference ends
]
GAP_BEATS = 1


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def layout():
    t, items = 0.0, []
    for it in TIMELINE:
        d = (it[3] if it else GAP_BEATS) * B
        items.append(dict(start=t, dur=d, item=it))
        t += d
    return items, t


def grade(a, raw):
    """MOTION photo grade (x[1.06, 1, 0.88], gamma 1.04). The workshop "before" also loses 30% of its
    colour, so the finished rooms are where the warmth arrives."""
    a = a.astype(np.float32) / 255
    if raw:
        lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        a = lum + (a - lum) * 0.7
    a = np.clip(a * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)
    return (a * 255).astype(np.uint8)


def video_frames(path, start, n, size):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", os.path.join(ROOT, path),
                          "-frames:v", str(n), "-vf", f"fps={FPS},scale={size[0]}:{size[1]}", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, size[1], size[0], 3)
    assert len(fr) >= n, (path, len(fr), n)
    return fr[:n]


def photo(key, crop, scale=1.05):
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    cx, cy, h = crop
    ch = h * im.height; cw = ch * 9 / 16
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    im = im.resize((round(W * scale), round(H * scale)), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return Image.fromarray(grade(np.asarray(im), False))


def rounded_mask(w, h, r):
    m = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), r * 4, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def handle():
    w, h = 30, 46
    im = Image.new("RGBA", (w * 4, h * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * 4 - 1, h * 4 - 1), 9 * 4, fill=(255, 255, 255, 255))
    d.rounded_rectangle((w * 2 - 7, h * 2 - 44, w * 2 + 7, h * 2 + 44), 7, fill=(20, 18, 16, 255))
    return im.resize((w, h), Image.LANCZOS)


def clip_strip(thumbs, dur):
    """One clip on the strip: filmstrip tiles, rounded ends, a trim handle at each end."""
    w = max(round(dur * V) - 5, 2 * 34)
    im = Image.new("RGBA", (w, TILE_H), (0, 0, 0, 255))
    for i in range(0, w, TILE_W):
        th = thumbs[min(int(i / w * len(thumbs)), len(thumbs) - 1)]
        im.paste(th, (i, 0))
    im.putalpha(rounded_mask(w, TILE_H, 9))
    hd = handle()
    for x in (2, w - hd.width - 2):
        im.alpha_composite(hd, (x, (TILE_H - hd.height) // 2))
    return im


def plus_button():
    s = 62
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s * 4 - 1, s * 4 - 1), 15 * 4, fill=(255, 255, 255, 255))
    c, L, t = s * 2, 15 * 4, 3 * 4
    d.rounded_rectangle((c - L, c - t, c + L, c + t), t, fill=(20, 18, 16, 255))
    d.rounded_rectangle((c - t, c - L, c + t, c + L), t, fill=(20, 18, 16, 255))
    return im.resize((s, s), Image.LANCZOS)


def label(text):
    """The clip length above the strip: white, bold, with a soft shadow so it holds on white walls."""
    lay = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((PH, 80), text, font=font("Inter-600.ttf", 46), fill=(255, 255, 255, 255), anchor="mm")
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    sh.putalpha(lay.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.55)))
    out = Image.new("RGBA", lay.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 3)); out.alpha_composite(lay)
    return out


def end_text(alpha):
    """Over the last shot only, on the plain wall between the picture and the plant, clear of the lamp's
    channel (x ~810): teak ink on a soft cream wash (MOTION 6)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wash = Image.new("L", (W, H), 0)
    ImageDraw.Draw(wash).rounded_rectangle((180, 600, 760, 900), 80, fill=80)
    wash = wash.filter(ImageFilter.GaussianBlur(90)).point(lambda v: int(v * alpha))
    lay.paste(Image.new("RGBA", (W, H), (246, 239, 228, 255)), (0, 0), wash)
    d = ImageDraw.Draw(lay)
    a = int(255 * alpha)
    d.text((700, 690), "Raw teak.", font=font("Fraunces-600.ttf", 84), fill=INK + (a,), anchor="rs")
    d.text((700, 784), "Warm light.", font=font("Fraunces-500-i.ttf", 84), fill=AMBER_DK + (a,), anchor="rs")
    d.text((700, 846), "nixwoods.com", font=font("Inter-600.ttf", 34), fill=INK + (int(a * 0.85),), anchor="rs")
    return lay


def music_track(items, total, path):
    """music5-3040 from MUSIC_IN, gated: silent while the playhead is over a gap (25 ms ramps)."""
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{MUSIC_IN:.4f}", "-i", MUSIC, "-t", f"{total:.3f}",
                          "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    g = np.ones(len(x), np.float32)
    ramp = int(0.025 * sr)
    for it in items:
        if it["item"] is None:
            a, b = int(it["start"] * sr), int((it["start"] + it["dur"]) * sr)
            g[a:b] = 0
            g[max(a - ramp, 0):a] = np.minimum(g[max(a - ramp, 0):a], np.linspace(1, 0, a - max(a - ramp, 0)))
            g[b:b + ramp] = np.minimum(g[b:b + ramp], np.linspace(0, 1, len(g[b:b + ramp])))
    fade = int(0.8 * sr)
    g[-fade:] *= np.linspace(1, 0, fade)
    x = np.clip(x * g[:, None] * 0.9, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def main():
    items, total = layout()
    n_total = round(total * FPS)
    # sources: full-size frames for playback, small ones for the filmstrip
    for it in items:
        src = it["item"]
        if src is None:
            continue
        kind, path, arg, _ = src
        n = round(it["dur"] * FPS) + 1
        if kind == V_:
            it["frames"] = [grade(f, True) for f in video_frames(path, arg, n, (W, H))]
            small = video_frames(path, arg, n, (TILE_W, TILE_H))
            k = max(1, round(it["dur"] * V / TILE_W))
            it["thumbs"] = [Image.fromarray(grade(small[min(int(i * n / k), n - 1)], True)) for i in range(k)]
        else:
            it["photo"] = photo(path, arg)
            it["thumbs"] = [it["photo"].resize((TILE_W, TILE_H), Image.LANCZOS)]
        it["strip"] = clip_strip(it["thumbs"], it["dur"])
    plus = plus_button()
    band_mask = rounded_mask(SX1 - SX0, SY1 - SY0, 6)
    labels = {}

    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    last = items[-1]
    for k in range(n_total):
        t = k / FPS + 1e-6
        cur = next(it for it in items if it["start"] <= t < it["start"] + it["dur"]) if t < total else last
        u = (t - cur["start"]) / cur["dur"]
        if cur["item"] is None:
            fr = Image.new("RGBA", (W, H), GAP_BLACK + (255,))
        elif cur["item"][0] == V_:
            fr = Image.fromarray(cur["frames"][min(int((t - cur["start"]) * FPS), len(cur["frames"]) - 1)]).convert("RGBA")
        else:
            im = cur["photo"]
            z = 1.0 + 0.04 * u if cur is not last else 1.0 + 0.05 * (u * u * (3 - 2 * u))
            bw, bh = W / z, H / z                                       # the photo is 1.05x: 5% headroom
            x0, y0 = (im.width - bw) / 2, (im.height - bh) / 2
            fr = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)).convert("RGBA")
        if cur is last:
            a = min(max((t - cur["start"] - 0.6) / 0.3, 0), 1)
            if a > 0:
                fr.alpha_composite(end_text(a * a * (3 - 2 * a)))
        # the strip
        band = Image.new("RGBA", (SX1 - SX0, SY1 - SY0), (0, 0, 0, 255))
        for it in items:
            if it["item"] is None:
                continue
            x0 = PH + (it["start"] - t) * V - SX0
            if x0 > band.width or x0 + it["strip"].width < 0:
                continue
            band.paste(it["strip"], (round(x0), 4), it["strip"])
        band.alpha_composite(plus, (band.width - plus.width - 20, (band.height - plus.height) // 2))
        band.putalpha(band_mask)
        fr.alpha_composite(band, (SX0, SY0))
        d = ImageDraw.Draw(fr)
        d.rounded_rectangle((PH - 3, SY0 - 12, PH + 2, SY1 + 12), 3, fill=(255, 255, 255, 255))
        txt = f"{cur['dur']:.1f}s"
        if txt not in labels:
            labels[txt] = label(txt)
        fr.alpha_composite(labels[txt], (0, LABEL_Y - 80))
        proc.stdin.write(fr.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()

    wav = OUT + ".music.wav"
    music_track(items, total, wav)
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{n_total / FPS:.3f}", OUT], check=True)
    os.remove(tmp); os.remove(wav)
    print(os.path.relpath(OUT, ROOT), f"{n_total / FPS:.2f}s, {sum(1 for i in items if i['item'])} clips")


if __name__ == "__main__":
    main()
