#!/usr/bin/env python3
"""Aurora "Same bed. One bar of teak." — E1 reel from the approved reel-engine script.

Script: nixwoods-os 40-Content/reel-engine/scripts/NW-CREATIVE-SCRIPT-20261116-nixwoods-aurora-linear-wall-light-above-the-bed-v1.json
(owner approved 2026-11-16, hook 1). Beats 3/4/4/4 s. Clips: VEO-002, VEO-007, REAL-026 (still), VEO-006.
Brand: Fraunces + Archivo, Bone #F6F1E7 / Muted Bone #D7D0C5, scrim from y=1120 peak 0.55 (nixwoods-brand-kit).
VO: ElevenLabs Sarah (EXAVITQu4vr4xnSDxMaL), audio-vo/vo-1..4.mp3. Music: music2-meaning at -13 dB.

Run from nixwoods-reel/:  python3 aurora-reels/build_above_the_bed.py
Writes aurora-reels/out/above-the-bed/{music,clean}.mp4, cover.jpg, sheet.jpg
"""
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
SRC, VO, OUT = HERE / "src", HERE / "audio-vo", HERE / "out" / "above-the-bed"
TMP = OUT / "_build"
W, H, FPS = 1080, 1920, 30
BONE, MUTED = (246, 241, 231), (215, 208, 197)
F_HEAD = str(ROOT / "assets" / "Fraunces-600.ttf")
F_BODY = str(ROOT / "assets" / "DM_Sans-500.ttf")  # Archivo is not in assets; DM Sans is the shipped supporting face
GRADE = "eq=contrast=1.05:saturation=1.06,vignette=angle=PI/5:mode=forward"

BEATS = [  # (seconds, on-screen text, vo file, vo start)
    (3.0, ["Same bed.", "One bar of teak."], "vo-1.mp3", 0.25),
    (4.0, ["Solid teak", "warm 3000K"], "vo-2.mp3", 3.30),
    (4.0, ["Down, or", "up and down"], "vo-3.mp3", 7.25),
    (4.0, ["Above the bed"], "vo-4.mp3", 11.20),
]
CTA = (["Above the bed or a painting:", "where would yours go?"], "nixwoods.com", 13.2)


def sh(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def ff(*args):
    sh(["ffmpeg", "-v", "error", "-y", *args])


def segments():
    v = f"scale={W}:{H}:flags=lanczos,fps={FPS},{GRADE},format=yuv420p"
    def push(rate):  # slow push-in so a near-static clip keeps moving (freezedetect gate)
        return (f"scale={W}:{H}:flags=lanczos,fps={FPS},zoompan=z='1+{rate}*on':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2'"
                f":d=1:s={W}x{H}:fps={FPS},{GRADE},format=yuv420p")
    # 1: cold ceiling light -> dark -> warm wash, 4.5 s of source played at 1.5x = 3.0 s
    ff("-ss", "1.8", "-t", "4.5", "-i", str(SRC / "VEO-002-aurora-wall-light-coldwarm-flip-9x16-clean.mp4"),
       "-vf", f"setpts=PTS/1.5,{v}", "-an", "-t", "3.0", str(TMP / "s1.mp4"))
    # 2: grain macro along the bar
    ff("-ss", "0.5", "-t", "4.0", "-i", str(SRC / "VEO-007-aurora-wall-light-detail-grain-9x16-clean.mp4"),
       "-vf", push(0.0008), "-an", str(TMP / "s2.mp4"))
    # 3: REAL still, 4:5 kept whole (a linear fixture is not a cropping problem): blurred fill + slow push
    still = SRC / "REAL-026-aurora-wall-wash-real-4x5.jpg"
    ff("-loop", "1", "-t", "4.0", "-i", str(still), "-filter_complex",
       f"[0]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg];"
       f"[0]scale={W}:-1,zoompan=z='1+0.05*on/{int(4*FPS)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x1350:fps={FPS}[fg];"
       f"[bg][fg]overlay=0:(H-h)/2,fps={FPS},{GRADE},format=yuv420p", "-t", "4.0", "-an", str(TMP / "s3.mp4"))
    # 4: bedroom, bar above the headboard
    ff("-ss", "2.0", "-t", "4.0", "-i", str(SRC / "VEO-006-aurora-wall-light-placement-bedroom-9x16-clean.mp4"),
       "-vf", push(0.0004), "-an", str(TMP / "s4.mp4"))
    (TMP / "list.txt").write_text("".join(f"file 's{i}.mp4'\n" for i in range(1, 5)))
    ff("-f", "concat", "-safe", "0", "-i", str(TMP / "list.txt"), "-c", "copy", str(TMP / "base.mp4"))


def scrim():
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(1120, H):
        a = int(255 * 0.55 * ((y - 1120) / (H - 1120)) ** 0.85)
        for x in range(W):
            px[x, y] = (0, 0, 0, a)
    return im


def text_png(lines, path, size=72, sub=None, y_top=1340):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F_HEAD, size)
    y = y_top
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=BONE)
        y += int(size * 1.18)
    if sub:
        fs = ImageFont.truetype(F_BODY, 30)
        w = d.textlength(sub, font=fs)
        d.text(((W - w) / 2, y + 18), sub, font=fs, fill=MUTED)
    alpha = im.split()[3].filter(ImageFilter.GaussianBlur(6)).point(lambda a: int(a * 0.5))
    base = Image.merge("RGBA", (Image.new("L", (W, H), 0),) * 3 + (alpha,))  # soft black shadow under the type
    base.alpha_composite(im)
    base.save(path)


def overlays():
    scrim().save(TMP / "scrim.png")
    t, cues = 0.0, []
    for i, (dur, lines, _, _) in enumerate(BEATS):
        p = TMP / f"t{i + 1}.png"
        text_png(lines, p, size=76 if i == 0 else 72)
        start = 0.3 if i == 0 else t + 0.15
        end = CTA[2] - 0.05 if i == len(BEATS) - 1 else t + dur - 0.1
        cues.append((p, start, end))
        t += dur
    p = TMP / "cta.png"
    text_png(CTA[0], p, size=62, sub=CTA[1], y_top=1300)
    cues.append((p, CTA[2], 15.0))
    return cues


def compose(cues, with_music):
    inputs = ["-i", str(TMP / "base.mp4"), "-loop", "1", "-i", str(TMP / "scrim.png")]
    for p, _, _ in cues:
        inputs += ["-loop", "1", "-i", str(p)]
    vo_idx = 2 + len(cues)
    for _, _, f, _ in BEATS:
        inputs += ["-i", str(VO / f)]
    fc = ["[0][1]overlay=0:0:shortest=1[v0]"]
    for k, (_, s, e) in enumerate(cues):
        fc.append(f"[{2 + k}]format=rgba,fade=t=in:st={s}:d=0.2:alpha=1,fade=t=out:st={e - 0.15}:d=0.15:alpha=1[o{k}]")
        fc.append(f"[v{k}][o{k}]overlay=0:0:enable='between(t,{s},{e})'[v{k + 1}]")
    vlast = f"v{len(cues)}"
    amix = []
    for j, (_, _, _, at) in enumerate(BEATS):
        ms = int(at * 1000)
        fc.append(f"[{vo_idx + j}]adelay={ms}|{ms},volume=1.0[a{j}]")
        amix.append(f"[a{j}]")
    n = len(BEATS)
    if with_music:
        inputs += ["-i", str(HERE / "audio" / "music2-meaning.mp3")]
        fc.append(f"[{vo_idx + n}]atrim=0:15,volume=-13dB,afade=t=in:d=0.5,afade=t=out:st=13.5:d=1.5[m]")
        amix.append("[m]")
        n += 1
    fc.append(f"{''.join(amix)}amix=inputs={n}:normalize=0,atrim=0:15,loudnorm=I=-16:TP=-1.5:LRA=11[aout]")
    name = "music" if with_music else "clean"
    ff(*inputs, "-filter_complex", ";".join(fc), "-map", f"[{vlast}]", "-map", "[aout]", "-t", "15",
       "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", str(FPS),
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(OUT / f"{name}.mp4"))


def stills():
    m = OUT / "music.mp4"
    ff("-ss", "12.0", "-i", str(m), "-frames:v", "1", "-q:v", "2", str(OUT / "cover.jpg"))
    ff("-i", str(m), "-vf", "fps=1,scale=216:-1,tile=8x2", "-frames:v", "1", "-q:v", "3", str(OUT / "sheet.jpg"))


if __name__ == "__main__":
    TMP.mkdir(parents=True, exist_ok=True)
    segments()
    cues = overlays()
    compose(cues, with_music=True)
    compose(cues, with_music=False)
    stills()
    print(OUT)
