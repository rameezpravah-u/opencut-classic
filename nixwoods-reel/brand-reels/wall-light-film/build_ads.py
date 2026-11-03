#!/usr/bin/env python3
"""Build the two brand-driven ad cuts (Meta 4:5, Instagram 9:16) from the wall-light-film clips.
See SCRIPT.md for the hook, cut list, motion and audio plan this implements.
Run from brand-reels/wall-light-film/.
"""
import subprocess
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
CLIPS = os.path.join(ROOT, "clips")
OUT = os.path.join(ROOT, "out")
ASSETS = os.path.join(REPO, "assets")
MUSIC = os.path.join(REPO, "rubik-reels", "audio", "music3-design.mp3")
WHOOSH = os.path.join(REPO, "rubik-reels", "audio", "sfx-whoosh.mp3")
CLICK = os.path.join(REPO, "brand-reels", "edison-stages", "sfx", "sfx-dimmer-click.mp3")
LOGO = os.path.join(ASSETS, "logo.png")
CORMORANT = os.path.join(ASSETS, "Cormorant_Garamond-500-i.ttf")
DM_SANS = os.path.join(ASSETS, "DM_Sans-500.ttf")

os.makedirs(OUT, exist_ok=True)

SCENES = [
    "01-home-aurora.mp4",
    "02-office-nixline.mp4",
    "03-hotel-sconce.mp4",
    "04-gallery-vertical.mp4",
    "05-restaurant-timber.mp4",
    "06-suite-arden.mp4",
]

HOOK = "one wall light. six rooms. watch what changes."

TRIM_IN = 0.8     # skip the first 0.8s of each 6.0417s clip — motion already read clearly
TRIM_DUR = 3.0    # length of the window used per scene
XF = 0.4          # dissolve duration between cuts
END_DUR = 2.5

GRADE = "eq=contrast=0.97:brightness=0.015:saturation=0.94,vignette=angle=PI/4.6:mode=forward,noise=alls=5:allf=t+u"


def build(ratio_label, W, H, out_name):
    inputs = []
    filters = []
    idx = 0

    for name in SCENES:
        inputs += ["-i", os.path.join(CLIPS, name)]
        idx += 1

    end_idx = idx
    inputs += ["-f", "lavfi", "-t", str(END_DUR), "-i", f"color=c=0x2E1E14:s={W}x{H}:r=24"]
    idx += 1
    logo_idx = idx
    inputs += ["-i", LOGO]
    idx += 1
    music_idx = idx
    whoosh_idx = idx + 1
    click_idx = idx + 2

    # per-scene: trim the 3s window, grade, then composite fit-within over a blurred cover-fill
    # of itself — a horizontal wall-light fixture never gets cropped, just reframed (PLAYBOOK §5)
    for i, name in enumerate(SCENES):
        v = f"[{i}:v]trim=start={TRIM_IN}:duration={TRIM_DUR},setpts=PTS-STARTPTS,fps=24,{GRADE}[g{i}]"
        sp = f"[g{i}]split=2[g{i}a][g{i}b]"
        bg = (
            f"[g{i}a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"gblur=sigma=28,eq=brightness=-0.06[bg{i}]"
        )
        fg = f"[g{i}b]scale={W}:{H}:force_original_aspect_ratio=decrease[fg{i}]"
        comp = f"[bg{i}][fg{i}]overlay=(W-w)/2:(H-h)/2,setsar=1[v{i}]"
        filters += [v, sp, bg, fg, comp]

    # hook line over scene 1, safe-zone left aligned, in 0.2s / held to 1.8s
    safe_x = int(W * 0.065)
    fs = max(26, int(W * 0.052))
    filters.append(
        f"[v0]drawtext=fontfile={CORMORANT}:text='{HOOK}':fontcolor=0xF6EFE4:fontsize={fs}:"
        f"x={safe_x}:y=H*0.78:line_spacing=6:"
        f"alpha='if(lt(t,0.2),0,if(lt(t,0.5),(t-0.2)/0.3,if(lt(t,1.8),1,if(lt(t,2.1),1-(t-1.8)/0.3,0))))'"
        f"[v0h]"
    )

    end_idx_label = end_idx
    filters.append(f"[{logo_idx}:v]scale={int(W*0.22)}:-1[logo]")
    filters.append(
        f"[{end_idx_label}:v][logo]overlay=(W-w)/2:H*0.38:format=auto,"
        f"drawtext=fontfile={CORMORANT}:text='solid wood lighting':fontcolor=0xF6EFE4:fontsize={int(fs*0.92)}:"
        f"x=(w-text_w)/2:y=H*0.58:alpha='if(lt(t,0.6),t/0.6,1)',"
        f"drawtext=fontfile={DM_SANS}:text='nixwoods.com':fontcolor=0xC9B79E:fontsize={int(fs*0.5)}:"
        f"x=(w-text_w)/2:y=H*0.68:alpha='if(lt(t,0.6),t/0.6,1)',"
        f"fade=t=in:st=0:d=0.5[vend]"
    )

    labels = ["v0h"] + [f"v{i}" for i in range(1, len(SCENES))] + ["vend"]
    durs = [TRIM_DUR] * len(SCENES) + [END_DUR]

    cur = labels[0]
    cur_total = durs[0]
    cut_offsets = []
    for i in range(1, len(labels)):
        nxt = labels[i]
        out_lab = f"x{i}"
        offset = cur_total - XF
        if i < len(SCENES):
            cut_offsets.append(offset + XF / 2)
        filters.append(f"[{cur}][{nxt}]xfade=transition=dissolve:duration={XF}:offset={offset:.4f}[{out_lab}]")
        cur_total = cur_total + durs[i] - XF
        cur = out_lab

    end_card_offset = cur_total - durs[-1] + (durs[-1] - XF) - (durs[-1] - XF)  # unused, kept for clarity
    final_video_label = cur
    total_dur = cur_total

    # audio: music bed + a whoosh at each scene-to-scene cut + a dimmer click into the end card
    a_parts = [f"[{music_idx}:a]atrim=0:{total_dur:.3f},afade=t=in:st=0:d=0.6,afade=t=out:st={total_dur-1.0:.3f}:d=1.0[bed]"]
    mix_inputs = ["[bed]"]
    n_cuts = len(cut_offsets)
    wh_split_labels = "".join(f"[wha{n}]" for n in range(n_cuts))
    a_parts.append(f"[{whoosh_idx}:a]asplit={n_cuts}{wh_split_labels}")
    for n, off in enumerate(cut_offsets):
        lab = f"wh{n}"
        a_parts.append(f"[wha{n}]atrim=0:0.5,adelay={int(off*1000)}|{int(off*1000)},volume=0.5[{lab}]")
        mix_inputs.append(f"[{lab}]")
    click_off = cur_total - END_DUR + 0.05
    a_parts.append(f"[{click_idx}:a]atrim=0:0.6,adelay={int(click_off*1000)}|{int(click_off*1000)},volume=0.7[click]")
    mix_inputs.append("[click]")
    a_parts.append("".join(mix_inputs) + f"amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0[aout]")

    filter_complex = ";".join(filters + a_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-i", MUSIC,
        "-i", WHOOSH,
        "-i", CLICK,
        "-filter_complex", filter_complex,
        "-map", f"[{final_video_label}]",
        "-map", "[aout]",
        "-t", f"{total_dur:.3f}",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        os.path.join(OUT, out_name),
    ]
    print(f"\n=== {ratio_label} ({W}x{H}) -> {out_name}, total {total_dur:.2f}s ===")
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("meta", "both"):
        build("Meta Feed 4:5", 1080, 1350, "NixWoods-Wall-Light-Film-Meta-4x5.mp4")
    if which in ("ig", "instagram", "both"):
        build("Instagram Reels 9:16", 1080, 1920, "NixWoods-Wall-Light-Film-Instagram-9x16.mp4")
