#!/usr/bin/env python3
"""remux_audio.py — rebuild the reel's audio bed over the already-rendered video.

`audio/music7-noir.mp3` is 20.04 s. This cut is 26.25 s. The engine lays the bed down at
t=0 with `afade=t=out:st=24.850:d=1.4` — a fade that never fires, because the track has
already run out. The result is 6.2 s of silence over the workshop beat, the room shot and
the whole end card, and nothing in the pipeline complains about it.

`linear-reels/audio/music7-noir-x2.mp3` is the same track crossfaded into itself
(`acrossfade=d=2.5`) so it runs 37.5 s. `L3-teak-assembly.json` now points at it, so a
re-render produces this directly. This script does the same thing to an already-finished
master without paying for another 8-minute render: it copies the video stream untouched
and rebuilds the audio with the engine's own filter chain, read straight out of the
rendered `.graph`:

    whoosh  adelay=7899   volume=-10dB
    whoosh  adelay=12900  volume=-10dB
    music   adelay=0  afade in 0.15  afade out @24.85 d=1.4  volume=-3dB
    amix(3, normalize=0) -> atrim 0:26.250 -> loudnorm I=-14:TP=-1.5:LRA=11

With `--crf N` it also re-encodes the video in the same pass, so the delivered file is one
generation away from the CRF 18 master rather than two. `nixwoods-reel/README.md` says a
finished reel over ~21 MB is re-encoded at CRF 23, which is what shipped.

    python3 remux_audio.py <master.mp4> <out.mp4> [--crf 23]
"""
import os
import subprocess
import sys

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
NR = "/home/user/opencut-classic/nixwoods-reel"
AUD = os.path.join(NR, "linear-reels", "audio")

MASTER = sys.argv[1]
OUT = sys.argv[2]
DUR = 26.250

whoosh = os.path.realpath(os.path.join(AUD, "sfx-whoosh.mp3"))
music = os.path.realpath(os.path.join(AUD, "music7-noir-x2.mp3"))
fmt = "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"

fc = (f"[1:a]{fmt},adelay=7899|7899,volume=-10dB[a0];"
      f"[2:a]{fmt},adelay=12900|12900,volume=-10dB[a1];"
      f"[3:a]{fmt},adelay=0|0,afade=t=in:st=0.000:d=0.15,"
      f"afade=t=out:st={DUR-1.4:.3f}:d=1.4,volume=-3.0dB[a2];"
      f"[a0][a1][a2]amix=inputs=3:duration=longest:normalize=0,"
      f"atrim=0:{DUR:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

if "--crf" in sys.argv:
    crf = sys.argv[sys.argv.index("--crf") + 1]
    vcodec = ["-c:v", "libx264", "-crf", crf, "-preset", "medium", "-pix_fmt", "yuv420p",
              "-profile:v", "high", "-level", "4.0"]
else:
    vcodec = ["-c:v", "copy"]

cmd = [FF, "-y", "-v", "error", "-i", MASTER, "-i", whoosh, "-i", whoosh, "-i", music,
       "-filter_complex", fc, "-map", "0:v:0", "-map", "[aout]",
       *vcodec, "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", OUT]
r = subprocess.run(cmd, capture_output=True, text=True)
print("exit", r.returncode)
if r.stderr.strip():
    print(r.stderr[:2000])
