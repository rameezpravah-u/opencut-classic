#!/usr/bin/env python3
"""Add a voiceover version of the wall-light film using OpenMontage's Piper TTS
(already set up at /home/user/OpenMontage) and its AudioMixer ducking tool.

VO script, scene-timed delays, and the whole plan are documented in SCRIPT.md.
Run from brand-reels/wall-light-film/ — this script shells out to
OpenMontage's own venv for the ducking step (it needs that package's imports).
"""
import subprocess
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, "..", ".."))
OUT = os.path.join(ROOT, "out")
VO = os.path.join(ROOT, "vo")
MUSIC = os.path.join(REPO, "rubik-reels", "audio", "music3-design.mp3")
CLICK = os.path.join(REPO, "brand-reels", "edison-stages", "sfx", "sfx-dimmer-click.mp3")
BASE_FILM = os.path.join(OUT, "NixWoods-Wall-Light-Film.mp4")
OM = "/home/user/OpenMontage"
OM_PY = os.path.join(OM, ".venv", "bin", "python")

# scene start times in the base film (see SCRIPT.md), + a short lead-in so each
# line starts once its scene's dissolve has settled
DELAYS_S = [0.4, 6.44, 11.68, 16.93, 22.17, 27.41, 32.00]

FILM_DUR = float(
    subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", BASE_FILM],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)


def narration_mix():
    inputs = []
    filters = []
    for i, delay in enumerate(DELAYS_S, start=1):
        inputs += ["-i", os.path.join(VO, f"line{i}.wav")]
        ms = int(delay * 1000)
        filters.append(f"[{i-1}:a]adelay={ms}|{ms}[l{i}]")
    mix_in = "".join(f"[l{i}]" for i in range(1, len(DELAYS_S) + 1))
    filters.append(f"{mix_in}amix=inputs={len(DELAYS_S)}:duration=longest:dropout_transition=0,apad=whole_dur={FILM_DUR}[vo]")
    out = os.path.join(VO, "narration_mix.wav")
    cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[vo]", out]
    subprocess.run(cmd, check=True)
    return out


def dimmer_click_layer():
    # a soft click as the end card settles, same touch as the ad cuts
    out = os.path.join(VO, "click_layer.wav")
    click_at_ms = int(31.9 * 1000)
    cmd = [
        "ffmpeg", "-y", "-i", CLICK,
        "-filter_complex", f"[0:a]atrim=0:0.6,adelay={click_at_ms}|{click_at_ms},volume=0.6,apad=whole_dur={FILM_DUR}[out]",
        "-map", "[out]", out,
    ]
    subprocess.run(cmd, check=True)
    return out


def music_bed():
    out = os.path.join(VO, "music_trimmed.wav")
    cmd = [
        "ffmpeg", "-y", "-i", MUSIC,
        "-filter_complex", f"[0:a]atrim=0:{FILM_DUR},afade=t=in:st=0:d=0.8,afade=t=out:st={FILM_DUR-1.3:.3f}:d=1.3[out]",
        "-map", "[out]", out,
    ]
    subprocess.run(cmd, check=True)
    return out


def duck(narration_path, music_path):
    """Call OpenMontage's own AudioMixer.execute(duck) from its venv."""
    out = os.path.join(VO, "ducked.wav")
    script = f"""
import sys
sys.path.insert(0, {OM!r})
from tools.audio.audio_mixer import AudioMixer
m = AudioMixer()
r = m.execute({{
    "operation": "duck",
    "primary_audio": {narration_path!r},
    "secondary_audio": {music_path!r},
    "duck_level": -14,
    "ducking": {{"attack_ms": 120, "release_ms": 600}},
    "output_path": {out!r},
}})
print("success:", r.success, "error:", r.error)
assert r.success, r.error
"""
    subprocess.run([OM_PY, "-c", script], check=True, cwd=OM)
    return out


def layer_click(ducked_path, click_path):
    out = os.path.join(VO, "final_audio.wav")
    cmd = [
        "ffmpeg", "-y", "-i", ducked_path, "-i", click_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=0[out]",
        "-map", "[out]", out,
    ]
    subprocess.run(cmd, check=True)
    return out


def mux_onto_film(audio_path):
    out = os.path.join(OUT, "NixWoods-Wall-Light-Film-VO.mp4")
    cmd = [
        "ffmpeg", "-y", "-i", BASE_FILM, "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart",
        out,
    ]
    subprocess.run(cmd, check=True)
    return out


if __name__ == "__main__":
    print(f"Base film duration: {FILM_DUR:.2f}s")
    n = narration_mix()
    print("narration mix:", n)
    m = music_bed()
    print("music bed:", m)
    d = duck(n, m)
    print("ducked:", d)
    c = dimmer_click_layer()
    f = layer_click(d, c)
    print("final audio:", f)
    out = mux_onto_film(f)
    print("FINAL:", out)
