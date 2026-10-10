#!/usr/bin/env python3
"""NixWoods "What making a solid teak lamp feels like sometimes." — a recreation of @westcodesignerinc's
Dd6t3EnglRt (8.8 s, "What making custom doors feels like sometimes").

The reference's joke: calm, lingering shots of the finished piece under a soft song keep getting broken by
0.25-0.4 s flashes of the workshop, each one a burst of loud tool noise, then straight back to calm. The
hook line sits at the top the whole way through.

  calm     clean 5 Aug shoot photos (drive-pull/shoot-20260805), slow push, MOTION photo grade
  flashes  real workshop phone clips (shelf-reels/src, floor-reels/src), 30% desaturated like the other
           workshop "befores"
  sound    music1-aesthetic (68 bpm, 0.8824 s), flashes on its beats; tool noise from ElevenLabs
           eleven_text_to_sound_v2 (sfx/, 6 takes, 3 used), music ducked under each burst
Only the sound effects are generated; every frame is real.

    python3 brand-reels/feels/feels_reel.py   # -> brand-reels/feels/NW-FEELS-making-a-teak-lamp-9x16.mp4
"""
import glob, os, subprocess, wave
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SHOOT = os.path.join(ROOT, "drive-pull", "shoot-20260805")
A = os.path.join(ROOT, "assets")
OUT = os.path.join(HERE, "NW-FEELS-making-a-teak-lamp-9x16.mp4")
MUSIC = os.path.join(ROOT, "floor-reels", "audio", "music1-aesthetic.mp3")
MUSIC_IN = 0.86                                    # the track's first beat lands on t = 0
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 30
B = 0.8824
HOOK = ["What making a solid teak lamp", "feels like sometimes."]

# calm: (photo, crop cx, cy, height fraction); flash: (clip, in-point, sfx file, sfx in-point)
CALM, FLASH = "calm", "flash"
SHOTS = [
    (CALM, ("9815", 0.58, 0.50, 1.00), 2 * B),                                   # NixLine in its corner
    (FLASH, ("shelf-reels/src/IMG_7745.mp4", 0.5, "sfx-sander-1.mp3", 0.0), 9),  # hands sanding the planks
    (CALM, ("9815", 0.75, 0.68, 0.60), 4 * B - 2 * B - 9 / FPS),                 # closer: the teak block, channel clear of the hook
    (FLASH, ("floor-reels/src/nx05-7920.mp4", 3.6, "sfx-saw-2.mp3", 0.35), 12),  # a raw bar swinging past
    (CALM, ("9776", 0.45, 0.50, 1.00), 6 * B - 4 * B - 12 / FPS),                # floor lamp, living room at dusk
    (FLASH, ("floor-reels/src/nx00-hero.mp4", 6.3, "sfx-router-2.mp3", 0.15), 8),  # the bundle of bars
    (CALM, ("9706", 0.42, 0.50, 1.00), 9 * B - 6 * B - 8 / FPS),                 # floor lamp by the shelf, the long hold
    (FLASH, ("shelf-reels/src/IMG_7745.mp4", 3.0, "sfx-sander-2.mp3", 0.75), 9),
    (CALM, ("9815", 0.58, 0.50, 1.00), 1.2 - 9 / FPS),                           # back to calm, and out
]


def font(n, s):
    return ImageFont.truetype(os.path.join(A, n), s)


def grade(a, raw):
    a = a.astype(np.float32) / 255
    if raw:
        lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
        a = lum + (a - lum) * 0.7
    a = np.clip(a * np.array([1.06, 1.0, 0.88], np.float32), 0, 1) ** (1 / 1.04)
    return (a * 255).astype(np.uint8)


def photo(key, cx, cy, hf, scale=1.04):
    f = glob.glob(os.path.join(SHOOT, f"*AC4I{key}*"))[0]
    im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
    ch = hf * im.height; cw = ch * 9 / 16
    x0 = min(max(cx * im.width - cw / 2, 0), im.width - cw)
    y0 = min(max(cy * im.height - ch / 2, 0), im.height - ch)
    im = im.resize((round(W * scale), round(H * scale)), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    return Image.fromarray(grade(np.asarray(im), False))


def clip_frames(path, start, n):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", os.path.join(ROOT, path), "-frames:v", str(n),
                          "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    assert len(fr) >= n, (path, len(fr), n)
    return [grade(f, True) for f in fr[:n]]


def hook_layer():
    """The hook, up the whole time like the reference: Inter 600 on a soft top gradient (MOTION 6)."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = np.clip(1 - np.arange(H) / 560, 0, 1) ** 1.6 * 0.42
    lay.putalpha(Image.fromarray((np.repeat(g[:, None], W, 1) * 255).astype(np.uint8)))
    txt = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(txt)
    for i, line in enumerate(HOOK):
        d.text((W // 2, 300 + i * 62), line, font=font("Inter-600.ttf", 50), fill=(246, 239, 228, 255), anchor="ma")
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sh.putalpha(txt.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5)))
    lay.alpha_composite(sh, (0, 2)); lay.alpha_composite(txt)
    return lay


def load_sfx(name, start, dur, sr):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{start:.3f}", "-i", os.path.join(HERE, "sfx", name), "-t",
                          f"{dur:.3f}", "-ac", "2", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def main():
    t, plan = 0.0, []
    for kind, src, d in SHOTS:
        n = d if kind == FLASH else round((t + d) * FPS) - round(t * FPS)
        plan.append((kind, src, round(t * FPS), n))
        t = (round(t * FPS) + n) / FPS
    nf = plan[-1][2] + plan[-1][3]
    total = nf / FPS
    hook = hook_layer()

    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "18", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", OUT + ".video.mp4"], stdin=subprocess.PIPE)
    for kind, src, f0, n in plan:
        if kind == FLASH:
            frames = [Image.fromarray(a) for a in clip_frames(src[0], src[1], n)]
        else:
            im = photo(*src)
            frames = []
            for k in range(n):
                u = k / max(n - 1, 1)
                z = 1.0 + 0.035 * (u * u * (3 - 2 * u))                     # slow push, a hold
                bw, bh = W / z, H / z
                x0, y0 = (im.width - bw) / 2, (im.height - bh) / 2
                frames.append(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh)))
        for fr in frames:
            fr = fr.convert("RGBA"); fr.alpha_composite(hook)
            proc.stdin.write(fr.convert("RGB").tobytes())
    proc.stdin.close(); proc.wait()

    # sound: the song, ducked under each burst of tool noise
    sr = 44100
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{MUSIC_IN:.3f}", "-i", MUSIC, "-t", f"{total:.3f}", "-ac", "2",
                          "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    mus = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    mus = np.pad(mus, ((0, max(0, round(total * sr) - len(mus))), (0, 0)))[:round(total * sr)]
    duck = np.ones(len(mus), np.float32)
    sfx = np.zeros_like(mus)
    for kind, src, f0, n in plan:
        if kind != FLASH:
            continue
        a, d = round(f0 / FPS * sr), n / FPS + 0.06
        s = load_sfx(src[2], src[3], d, sr)
        env = np.ones(len(s), np.float32)
        env[:int(0.006 * sr)] = np.linspace(0, 1, int(0.006 * sr))            # hard in, like the cut
        k = int(0.05 * sr); env[-k:] = np.linspace(1, 0, k)
        s = s * env[:, None] / max(np.abs(s).max(), 1e-3) * 0.7
        sfx[a:a + len(s)] += s[:len(sfx) - a]
        duck[a:a + len(s)] = np.minimum(duck[a:a + len(s)], 0.3)
    duck = np.convolve(duck, np.ones(int(0.02 * sr)) / int(0.02 * sr), "same").astype(np.float32)
    mix = mus * 0.85 * duck[:, None] + sfx
    k = int(0.7 * sr); mix[-k:] *= np.linspace(1, 0, k)[:, None]
    mix = mix * min(1.0, 0.7 / max(np.abs(mix).max(), 1e-3))           # headroom for the AAC encode
    with wave.open(OUT + ".wav", "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", OUT + ".video.mp4", "-i", OUT + ".wav", "-map", "0:v",
                    "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                    "-t", f"{total:.3f}", OUT], check=True)
    os.remove(OUT + ".video.mp4"); os.remove(OUT + ".wav")
    print(os.path.relpath(OUT, ROOT), f"{total:.2f}s;", ", ".join(f"{k}@{f0 / FPS:.2f}" for k, _, f0, _ in plan))


if __name__ == "__main__":
    main()
