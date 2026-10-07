#!/usr/bin/env python3
"""NixLine Meta video ad — 10 s, 9:16. "Still lit by one tubelight?" -> click -> the corner glows -> price.

Why this shape (research 7 Oct, concepts/meta-set/README.md):
  - 8-10 s floor-lamp / pendant videos on the .in account returned 4-8x; 19 s+ cuts 0.1-3.9x.
  - the live winner is a warm dusk corner + Rs 999 + COD; this is that, set in motion.
  - before/after openings are rare in home decor yet last ~2.2x longer.
The before and after frames are the same generated room (the after was made by editing the
before), so the light change is a real cut between two aligned photographs, not a morph.

Beats sit on music6-corners' measured grid (71.8 bpm, beat 0.8357 s, track started at 0.396 s):
  0.000  tubelight room, hook on screen by 0.15 s          "Still lit by one tubelight?"
  1.671  click: tubelight off (beat 2)
  2.507  lamp on (beat 3), push in on the lit corner        "Not brighter. Warmer."
  5.850  dusk living room, Diwali                           "Solid teak. Made by hand."
  7.521  end card = concept A                               Rs 999 / Rs 1,599 / COD / free delivery
 10.029  end (beat 12)
Generated scenes: tick Meta's AI disclosure.

    python3 floor-reels/static/meta_video.py   # -> concepts/meta-set/NX-META-V1-tubelight-to-teak-9x16.mp4
"""
import os, subprocess, sys
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_set as m
import meta_set_916 as v

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
BEAT, OFF = 0.8357, 0.396
T_OFF, T_ON, T_DUSK, T_END, DUR = 2 * BEAT, 3 * BEAT, 7 * BEAT, 9 * BEAT, 12 * BEAT
AUD = os.path.join(m.ROOT, "audio")
OUT = os.path.join(m.OUT, "NX-META-V1-tubelight-to-teak-9x16.mp4")


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def big(path, fx=0.5, scale=1.25):
    """Scene filled to an oversized canvas so we can push in without upscaling past the source."""
    return v.crop_fill(path, fx, (round(W * scale), round(H * scale)))


def push(img, t, z0, z1, cx=0.5, cy=0.5):
    """Crop a zoom window from the oversized canvas; z is the fraction of the canvas shown."""
    z = z0 + (z1 - z0) * ease(t)
    w, h = img.width * z, img.height * z
    x = (img.width - w) * cx
    y = (img.height - h) * cy
    return img.resize((W, H), Image.LANCZOS, box=(x, y, x + w, y + h))


def text_layer(draw_fn):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer), layer)
    return layer


def over(frame, layer, a):
    if a <= 0:
        return frame
    l = layer.copy()
    l.putalpha(l.getchannel("A").point(lambda p: int(p * min(a, 1.0))))
    out = frame.convert("RGBA")
    out.alpha_composite(l)
    return out.convert("RGB")


def main():
    before = big(f"{m.SCN}/B-before-tubelight.jpg", 0.55)
    after = big(f"{m.SCN}/B-after-nixline.jpg", 0.55)
    dark = ImageEnhance.Brightness(before).enhance(0.10)
    dark = Image.blend(dark, Image.new("RGB", dark.size, (6, 9, 18)), 0.35)
    dusk = big(f"{m.SCN}/A-diwali-dusk.jpg", 0.30)
    endcard, _, _ = v.a()                                  # the 9:16 concept A, already composed
    endcard = endcard.convert("RGB")

    hook = text_layer(lambda d, l: m.headline(d, W // 2, 330, ["Still lit by", "one tubelight?"], 96, anchor="ma"))
    warm = text_layer(lambda d, l: m.headline(d, W // 2, 330, ["Not brighter.", "Warmer."], 104, fill=m.CREAM, anchor="ma"))
    teak = text_layer(lambda d, l: m.headline(d, 80, 330, ["Solid teak.", "Made by hand."], 96))

    n = round(DUR * FPS)
    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
                             "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        if t < T_OFF:                                       # 1. tubelight room, slow push
            f = push(before, t / T_OFF, 0.86, 0.82, 0.55, 0.5)
            f = over(f, hook, ease((t - 0.05) / 0.12))
        elif t < T_ON:                                      # 2. lights off
            f = push(dark, 1.0, 0.82, 0.82, 0.55, 0.5)
        elif t < T_DUSK:                                    # 3. the lamp comes on, push to the corner
            k = (t - T_ON)
            a = push(after, k / (T_DUSK - T_ON), 0.82, 0.62, 0.78, 0.62)
            d0 = push(dark, k / (T_DUSK - T_ON), 0.82, 0.62, 0.78, 0.62)
            f = Image.blend(d0, a, ease(k / 0.30))          # 0.3 s warm-up, like an LED driver
            f = over(f, warm, ease((k - 0.35) / 0.25))
        elif t < T_END:                                     # 4. dusk living room
            k = (t - T_DUSK) / (T_END - T_DUSK)
            f = push(dusk, k, 0.84, 0.76, 0.60, 0.45)
            f = over(f, teak, ease((t - T_DUSK - 0.10) / 0.25))
        else:                                               # 5. end card, held
            k = (t - T_END) / (DUR - T_END)
            prev = push(dusk, 1.0, 0.84, 0.76, 0.60, 0.45)
            f = Image.blend(prev, endcard, ease((t - T_END) / 0.25))
        proc.stdin.write(f.tobytes())
    proc.stdin.close(); proc.wait()

    # audio: the piano bed from its downbeat, a soft switch click on the cut, the turn swell on the lamp
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp,
                    "-ss", f"{OFF:.3f}", "-t", f"{DUR:.3f}", "-i", os.path.join(AUD, "music6-corners.mp3"),
                    "-i", os.path.join(AUD, "sfx-turn.mp3"),
                    "-f", "lavfi", "-t", "0.06", "-i", "anoisesrc=color=pink:amplitude=0.9:d=0.06",
                    "-filter_complex",
                    f"[1:a]volume=0.85,afade=t=in:d=0.25,afade=t=out:st={DUR - 0.7:.3f}:d=0.7[m];"
                    f"[2:a]volume=0.55,adelay={int(T_ON * 1000)}|{int(T_ON * 1000)}[s];"
                    f"[3:a]highpass=f=1800,afade=t=out:st=0.01:d=0.05,volume=0.8,"
                    f"adelay={int(T_OFF * 1000)}|{int(T_OFF * 1000)}[c];"
                    f"[m][s][c]amix=inputs=3:normalize=0,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{DUR:.3f}", OUT], check=True)
    os.remove(tmp)
    print(os.path.relpath(OUT, m.ROOT), f"{DUR:.2f}s")


if __name__ == "__main__":
    main()
