#!/usr/bin/env python3
"""Assemble the NixWoods wall-light brand film: grade, crossfade, end card, score.
Run from brand-reels/wall-light-film/.
"""
import subprocess
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
CLIPS = os.path.join(ROOT, "clips")
OUT = os.path.join(ROOT, "out")
ASSETS = os.path.join(REPO, "assets")
MUSIC = os.path.join(REPO, "rubik-reels", "audio", "music3-design.mp3")
LOGO = os.path.join(ASSETS, "logo.png")

os.makedirs(OUT, exist_ok=True)

SCENES = [
    "01-home-aurora.mp4",
    "02-office-nixline.mp4",
    "03-hotel-sconce.mp4",
    "04-gallery-vertical.mp4",
    "05-restaurant-timber.mp4",
    "06-suite-arden.mp4",
]

W, H = 1920, 1080
FPS = 24
XF = 0.8          # crossfade duration
CLIP_DUR = 6.0417  # source clip duration
END_DUR = 3.6   # held a touch longer than the silent cut so the VO closing line lands cleanly

# the approved "aesthetic" cinematic grade from system/presets.json
GRADE = "eq=contrast=0.97:brightness=0.015:saturation=0.94,vignette=angle=PI/4.6:mode=forward,noise=alls=5:allf=t+u"

NORM = (
    f"scale={W}:{H}:force_original_aspect_ratio=increase,"
    f"crop={W}:{H},setsar=1,fps={FPS}," + GRADE
)

inputs = []
filters = []
next_idx = 0

for i, name in enumerate(SCENES):
    inputs += ["-i", os.path.join(CLIPS, name)]
    filters.append(f"[{i}:v]{NORM}[v{i}]")
    next_idx += 1

# end card: teak ground background + logo + cta line, held 3s with a slow fade in
end_idx = next_idx
inputs += ["-f", "lavfi", "-t", str(END_DUR), "-i", f"color=c=0x2E1E14:s={W}x{H}:r={FPS}"]
next_idx += 1
logo_idx = next_idx
inputs += ["-i", LOGO]
next_idx += 1
music_idx = next_idx

cormorant = os.path.join(ASSETS, "Cormorant_Garamond-500-i.ttf")
dm_sans = os.path.join(ASSETS, "DM_Sans-500.ttf")

filters.append(
    f"[{logo_idx}:v]scale=150:-1[logo]"
)
filters.append(
    f"[{end_idx}:v][logo]overlay=(W-w)/2:H*0.38:format=auto,"
    f"drawtext=fontfile={cormorant}:text='solid wood lighting':fontcolor=0xF6EFE4:fontsize=54:"
    f"x=(w-text_w)/2:y=H*0.58:alpha='if(lt(t,0.6),t/0.6,1)',"
    f"drawtext=fontfile={dm_sans}:text='nixwoods.com':fontcolor=0xC9B79E:fontsize=30:"
    f"x=(w-text_w)/2:y=H*0.68:alpha='if(lt(t,0.6),t/0.6,1)',"
    f"fade=t=in:st=0:d=0.5[vend]"
)

# crossfade chain across the 5 graded clips + end card
labels = [f"v{i}" for i in range(len(SCENES))] + ["vend"]
durs = [CLIP_DUR] * len(SCENES) + [END_DUR]

cur = labels[0]
cur_total = durs[0]
for i in range(1, len(labels)):
    nxt = labels[i]
    out_lab = f"x{i}"
    offset = cur_total - XF
    filters.append(f"[{cur}][{nxt}]xfade=transition=dissolve:duration={XF}:offset={offset:.4f}[{out_lab}]")
    cur_total = cur_total + durs[i] - XF
    cur = out_lab

final_video_label = cur
total_dur = cur_total
print(f"Final video duration: {total_dur:.3f}s")

filter_complex = ";".join(filters)

cmd = [
    "ffmpeg", "-y",
    *inputs,
    "-stream_loop", "-1", "-i", MUSIC,
    "-filter_complex", filter_complex,
    "-map", f"[{final_video_label}]",
    "-map", f"{music_idx}:a",
    "-filter:a:0", f"afade=t=out:st={total_dur-1.2:.3f}:d=1.2,afade=t=in:st=0:d=1.0",
    "-t", f"{total_dur:.3f}",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
    "-c:a", "aac", "-b:a", "192k",
    "-movflags", "+faststart",
    os.path.join(OUT, "NixWoods-Wall-Light-Film.mp4"),
]

print(" ".join(cmd))
subprocess.run(cmd, check=True)
