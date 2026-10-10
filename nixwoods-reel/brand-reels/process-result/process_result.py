#!/usr/bin/env python3
"""NixWoods "Process. / Result." — an original reel in the style of @kaya.outdoor's DeSAzBgJuu7 (7.7 s: a
small "Process" label over very fast factory cuts, then on the beat drop "Result" over finished pieces cut
on the beat). Every frame is ours.

  process  real workshop phone clips (shelf-reels/src, floor-reels/src, curve-reels/src), 14 cuts on the
           half-beat (0.302 s), the raw "before" look (30% less colour)
  result   the clean 5 Aug 2026 shoot (drive-pull/shoot-20260805), one per beat with a slow push, MOTION
           photo grade, ending held on NixLine
Music: music3-design from 6.552 s, so its drop (10.752 s) lands on the switch at 4.2 s.

    python3 brand-reels/process-result/process_result.py   # -> brand-reels/process-result/NW-PROCESS-RESULT-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
A = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "NW-PROCESS-RESULT-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music3-design.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B, DROP = 0.6036, 10.752
SWITCH = 7 * B                                       # 4.23 s: 14 half-beat cuts, then the drop
MUSIC_IN = DROP - SWITCH

PROCESS = [("shelf-reels/src/IMG_7745.mp4", 0.2), ("floor-reels/src/nx05-7920.mp4", 3.6),
           ("floor-reels/src/nx06-7921.mp4", 0.6), ("shelf-reels/src/IMG_7745.mp4", 2.9),
           ("floor-reels/src/nx04-7930.mp4", 0.4), ("floor-reels/src/nx06-7921.mp4", 2.6),
           ("floor-reels/src/nx00-hero.mp4", 6.2), ("shelf-reels/src/IMG_7747.mp4", 0.4),
           ("floor-reels/src/nx05-7920.mp4", 4.9), ("shelf-reels/src/IMG_7749.mp4", 1.4),
           ("floor-reels/src/nx03-7926.mp4", 0.3), ("floor-reels/src/nx06-7921.mp4", 6.4),
           ("curve-reels/src/IMG_7753.mp4", 2.4), ("floor-reels/src/nx00-hero.mp4", 7.4)]
RESULT = [("9815", 0.62, 0.62, 0.62), ("9798", 0.50, 0.45, 0.75), ("9644", 0.48, 0.30, 0.55),
          ("9751", 0.30, 0.55, 0.80), ("9861", 0.66, 0.60, 0.72), ("9776", 0.45, 0.58, 0.75),
          ("9665", 0.50, 0.40, 0.80), ("9882", 0.50, 0.50, 0.85), ("9815", 0.58, 0.50, 1.00)]
RESULT_BEATS = [1, 1, 1, 1, 1, 1, 1, 1, 3]


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def grade(a, raw):
    a = a.astype(np.float32) / 255
    if raw:
        lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        a = lum + (a - lum) * 0.7
    a = np.clip(a * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)
    return (a * 255).astype(np.uint8)


def clip(path, start, n):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", os.path.join(ROOT, path), "-frames:v", str(n),
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    assert len(fr) >= n, (path, len(fr), n)
    return fr[:n]


def photo(key, cx, cy, hf, scale=1.05):
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    ch = hf * im.height; cw = ch * 9 / 16
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    im = im.resize((round(W * scale), round(H * scale)), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return Image.fromarray(grade(np.asarray(im), False))


def label(word):
    """The reference's small centred label: Inter, white, a soft shadow so it holds on any frame."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(txt).text((W // 2, H // 2), word, font=font("Inter-600.ttf", 46), fill=(246, 239, 228, 255), anchor="mm")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.6)))
    lay.alpha_composite(sh, (0, 2)); lay.alpha_composite(txt)
    return lay


def main():
    lab_p, lab_r = label("Process."), label("Result.")
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "19", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    t, nf = 0.0, 0
    for path, start in PROCESS:                                        # half-beat cuts
        n = round((t + B / 2) * FPS) - round(t * FPS)
        for a in clip(path, start, n):
            fr = Image.fromarray(grade(a, True)).convert("RGBA"); fr.alpha_composite(lab_p)
            proc.stdin.write(fr.convert("RGB").tobytes()); nf += 1
        t += B / 2
    for (key, cx, cy, hf), beats in zip(RESULT, RESULT_BEATS):        # one per beat, slow push
        img = photo(key, cx, cy, hf)
        n = round((t + beats * B) * FPS) - round(t * FPS)
        for k in range(n):
            u = k / max(n - 1, 1); z = 1 + 0.03 * beats * (u * u * (3 - 2 * u))
            bw, bh = W / z, H / z
            x0, y0 = (img.width - bw) / 2, (img.height - bh) / 2
            fr = img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)).convert("RGBA")
            fr.alpha_composite(lab_r)
            proc.stdin.write(fr.convert("RGB").tobytes()); nf += 1
        t += beats * B
    proc.stdin.close(); proc.wait()
    total = nf / FPS
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{MUSIC_IN:.3f}", "-i", MUSIC, "-t", f"{total:.3f}", "-ac", "2",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    x = np.pad(x, ((0, max(0, round(total * sr) - len(x))), (0, 0)))[:round(total * sr)]
    k = int(0.04 * sr); x[:k] *= np.linspace(0, 1, k)[:, None]
    k = int(0.8 * sr); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x = x * (0.6 / max(np.abs(x).max(), 1e-3))
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f}s")


if __name__ == "__main__":
    main()
