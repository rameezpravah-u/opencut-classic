#!/usr/bin/env python3
"""NixWoods "Lamps under ₹3,000." A list reel in the shape of @scoopedfriday's "Lamps under Rs. 1500"
(Dc6DAC5zsGH, 14.7 s, 169k views): a big hook over the first lamp, then one lamp per shot in a dim warm room,
its name fading in and its price just after. Here it is four NixWoods lamps, all real footage, on the
music6-corners beat grid (12 beats = 10.03 s, so every price is on screen before 10 s).

Products identified with PRODUCT-ID.md; prices from live Shopify on 11 Oct 2026:
  0     - 2.507  Rubik's Cube Lamp, ₹2,999   rubik-reels/src/14-1.mp4 from 1.0 s (green, then red: two colours)
  2.507 - 5.014  NixLine Floor Lamp, ₹999     floor-reels/src/nx04-7930.mp4 from 0.75 s (upright on its block)
  5.014 - 7.521  Aurora Wall Light, from ₹1,999  src/drive-aurora-v3-fullshoot-hook.mp4 from 3.35 s (angled wash)
  7.521 - 10.03  Edison Dimmer Lamp, ₹2,499   src/drive-edison-dimmer-demo-wa.mp4 from 10.7 s (the hand turns
                 the brass dimmer and the tube bulb comes up), then "All four at nixwoods.com"
The two src/ clips are the small copies on Drive (Drive's connector stops at 10 MB): the WhatsApp copy of
shoot clip 16 and the Aurora v3 hook cut of shoot clip 03. Text frames of that cut (0-2 s, 6.6 s on) are not used.

Look: MOTION.md, not the reference's yellow type. Hook in Fraunces 600 cream with the price in amber italic,
names in Fraunces, prices in Inter 600 amber, on a soft dark scrim. The montage grade runs at 45% on the
three warm shots; the Rubik's Cube shot keeps its own colour, since its colours are the product.
    python3 brand-reels/lamps-under-3000/lamps_under_3000.py
"""
import os, subprocess, sys, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy.ndimage import binary_dilation

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "floor-reels", "static"))
from line_montage import axis, grade                                   # noqa: E402

OUT = os.path.join(HERE, "NW-CREATIVE-VID-20261011-nixwoods-lamps-under-3000-v1.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music6-corners.mp3")
A = os.path.join(ROOT, "assets")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B, FIRST = 0.8357, 0.396
CREAM, AMBER, MUTED = (246, 239, 228), (232, 162, 74), (200, 190, 178)
R = lambda p: os.path.join(ROOT, p)
# (source, fps, in-point, beats, grade strength, name, price, extra line)
SHOTS = [(R("rubik-reels/src/14-1.mp4"), 25, 1.00, 3, 0.0, "Rubik's Cube Lamp", "₹2,999", None),
         (R("floor-reels/src/nx04-7930.mp4"), 30, 0.75, 3, 0.45, "NixLine Floor Lamp", "₹999", None),
         (os.path.join(HERE, "src", "drive-aurora-v3-fullshoot-hook.mp4"), 30, 3.35, 3, 0.45,
          "Aurora Wall Light", "from ₹1,999", None),
         (os.path.join(HERE, "src", "drive-edison-dimmer-demo-wa.mp4"), 25, 10.70, 3, 0.45,
          "Edison Dimmer Lamp", "₹2,499", "All four at nixwoods.com")]
HOOK = ("Lamps under ", "₹3,000.")
NAME_AT = (1.55, 0.35, 0.35, 1.25)
MASKS = ("white", "channel", "white", "white")
STRAIGHTEN = {1}                          # the NixLine: the phone was tilted 4-5 degrees; MOTION.md says
                                          # the lamp stands upright, so its channel is rotated vertical and
                                          # the frame zoomed just enough (about 15%) to hide the corners        # seconds into each shot; on shot 1 the hook reads first, on the
                                          # Edison shot the name waits for the bulb to come up


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


F_HOOK, F_HOOK_I = font("Fraunces-600.ttf", 92), font("Fraunces-500-i.ttf", 92)
F_NAME, F_PRICE, F_LINE = font("Fraunces-600.ttf", 72), font("Inter-600.ttf", 104), font("Inter-400.ttf", 42)


def shot_frames(src, sfps, t0, beats, strength, start, straighten=False):
    n = round((start + beats * B) * FPS) - round(start * FPS)
    need = int(np.ceil(n * sfps / FPS)) + 2
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t0:.3f}", "-i", src, "-frames:v", str(need),
                          "-vf", f"fps={sfps},scale={W}:{H}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    idx = [min(int(k * sfps / FPS), len(fr) - 1) for k in range(n)]
    if straighten:                                                     # the channel's angle per frame, smoothed
        angs = {i: axis(Image.fromarray(fr[i]))[1] for i in sorted(set(idx))}
        ks = sorted(angs); sm = np.convolve(np.pad([angs[i] for i in ks], 7, mode="edge"), np.ones(15) / 15, "valid")
        angs = dict(zip(ks, sm))
    out = []
    for k in range(n):
        a = fr[idx[k]]
        u = k / max(n - 1, 1); z = 1 + 0.05 * u * u * (3 - 2 * u)      # MOTION.md: a 5% push on a hold
        im = Image.fromarray(a)
        if straighten:                                                 # rotate the channel vertical, then zoom
            th = np.radians(abs(angs[idx[k]]))                         # just enough that no corner shows black
            zc = np.cos(th) + (H / W) * np.sin(th)
            im = im.rotate(-angs[idx[k]], resample=Image.BICUBIC)
            cw, ch = W / zc, H / zc
            im = im.resize((W, H), Image.LANCZOS, box=((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2))
        bw, bh = W / z, H / z
        im = im.resize((W, H), Image.LANCZOS, box=((W - bw) / 2, (H - bh) / 2, (W + bw) / 2, (H + bh) / 2))
        if strength:
            g = np.asarray(grade(im)).astype(np.float32)
            out.append((strength * g + (1 - strength) * np.asarray(im)).astype(np.uint8))
        else:
            out.append(np.asarray(im))
    return out


def light_mask(frames, mode="white"):
    """Where type may not go. "white": near-white light. "channel": a vertical lit channel only (the bright
    columns of a lamp standing in a white workshop, where the wall is as bright as the light)."""
    m = np.zeros((H, W), bool)
    for a in frames[:: max(1, len(frames) // 8)]:
        if mode == "channel":
            hot = (a.min(2) > 235).sum(0) > H * 0.25                     # columns lit for a quarter of the height
            cols = np.where(hot)[0]
            if len(cols):
                m[:, max(0, cols.min() - 140):cols.max() + 140] = True
        else:
            m |= (a.max(2) > 225) & (a.max(2).astype(int) - a.min(2) < 80)    # near-white light, not lit colour
    return binary_dilation(m, iterations=84) if mode == "white" else m


def block(lines):
    """lines: [(text, font, colour)] stacked, each 1.12 x its size apart. Returns an RGBA layer at (0, 0)."""
    probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    widths = [sum(probe.textlength(t, font=f) for t, f, _ in ln) for ln in lines]
    heights = [int(max(f.size for _, f, _ in ln) * 1.18) for ln in lines]
    return widths, heights


def text_layer(lines, frames, ys, avoid_top=0, mode="white", aligns=("left", "center", "right")):
    """Find a light-free spot for a stacked text block and draw it on a soft scrim with a shadow."""
    widths, heights = block(lines)
    bw, bh = int(max(widths)), sum(heights)
    mask = light_mask(frames, mode)
    for y in ys:
        if y < avoid_top:
            continue
        for align in aligns:
            x = {"left": 70, "center": (W - bw) / 2, "right": 950 - bw}[align]
            box = (int(x), y, int(x + bw), y + bh)
            if box[3] > 1250 or mask[box[1]:box[3], box[0]:box[2]].any():
                continue
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ys_ = np.arange(H)[:, None]
            g = np.broadcast_to(np.clip(1 - np.maximum(0, np.abs(ys_ - (y + bh / 2)) - bh / 2) / 260, 0, 1) * 0.5, (H, W))
            lay.paste(Image.new("RGBA", (W, H), (24, 14, 8, 255)), (0, 0),
                      Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(30)))
            txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt); yy = y
            for ln, w, h in zip(lines, widths, heights):
                xx = {"left": 70, "center": (W - w) / 2, "right": 950 - w}[align]
                for t, f, c in ln:
                    d.text((xx, yy), t, font=f, fill=c + (255,)); xx += d.textlength(t, font=f)
                yy += h
            sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(7)).point(lambda v: int(v * 0.5)))
            lay.alpha_composite(sh, (2, 4)); lay.alpha_composite(txt)
            print(f"  {[''.join(t for t, _, _ in ln) for ln in lines]} at y {y}, {align}")
            return np.asarray(lay).astype(np.float32) / 255, box + (align,)
    raise SystemExit(f"no light-free spot for {lines[0][0][0]}")


def fade(t, t0, dur):
    u = min(1.0, max(0.0, (t - t0) / dur))
    return u * u * (3 - 2 * u)


def main():
    frames, t = [], 0.0
    for j, (src, sfps, t0, beats, strength, name, price, extra) in enumerate(SHOTS):
        fr = shot_frames(src, sfps, t0, beats, strength, t, straighten=j in STRAIGHTEN)
        layers = []                                                     # (layer, appear-at, fade)
        top = 250
        if j == 0:
            hook, hb = text_layer([[(HOOK[0], F_HOOK, CREAM), (HOOK[1], F_HOOK_I, AMBER)]], fr, (250, 290, 330, 380))
            layers.append((hook, 0.05, 0.12)); top = hb[3] + 40
        nm, nb = text_layer([[(name, F_NAME, CREAM)]], fr, tuple(range(top, 1100, 40)), mode=MASKS[j])
        layers.append((nm, NAME_AT[j], 0.25))
        pr, pb = text_layer([[(price, F_PRICE, AMBER)]], fr, (nb[3] + 6,) + tuple(range(nb[3] + 46, 1150, 40)), mode=MASKS[j], aligns=(nb[4],))
        layers.append((pr, NAME_AT[j] + 0.30, 0.25))
        if extra:
            ex, _ = text_layer([[(extra, F_LINE, CREAM)]], fr, (pb[3] + 20,) + tuple(range(pb[3] + 60, 1200, 40)), mode=MASKS[j], aligns=(nb[4],))
            layers.append((ex, NAME_AT[j] + 0.75, 0.30))
        for i, a in enumerate(fr):
            a = a.astype(np.float32); tt = i / FPS
            for lay, at, du in layers:
                al = lay[..., 3:4] * fade(tt, at, du)
                a = a * (1 - al) + lay[..., :3] * 255 * al
            frames.append(np.clip(a, 0, 255).astype(np.uint8))
        t += beats * B
    total = len(frames) / FPS

    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                          "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", OUT + ".video.mp4"],
                         stdin=subprocess.PIPE)
    for a in frames:
        p.stdin.write(a.tobytes())
    p.stdin.close(); assert p.wait() == 0
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{FIRST:.3f}", "-t", f"{total:.3f}", "-i", MUSIC, "-ac", "2", "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    k = int(0.04 * sr); x[:k] *= np.linspace(0, 1, k)[:, None]
    k = int(0.8 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x *= 0.65 / max(np.abs(x).max(), 1e-3)
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f} s, {len(frames)} frames")


if __name__ == "__main__":
    main()
