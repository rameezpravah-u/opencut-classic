#!/usr/bin/env python3
"""Render the shelf reel from the timeline the nixwoods system planned.

Why this exists: `nixwoods-reel/system/make_reel.py` plans the cut, writes the type
layers and the end card, and then renders one enormous ffmpeg graph in which every
shot is upscaled to 2160x3840 with lanczos before zoompan. On a loaded box that runs
at ~0.004x realtime and the render did not survive. This script takes the same plan
(`<name>-timeline.json`, `<name>-c*.png`, `<name>-end.png`) and renders it shot by
shot with a 1.5x bilinear supersample instead of a 2x lanczos one, so the camera
moves are still sub-pixel smooth but the render finishes in minutes.

Nothing creative is decided here: the cut, the grade, the type and the audio all
come out of the brief and the timeline.

    python3 build_reel.py <timeline.json> <output.mp4>
"""
import json, os, subprocess, sys, tempfile
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = "/home/user/opencut-classic/nixwoods-reel/shelf-reels"
FPS, W, H = 25, 1080, 1920
SS_W, SS_H = 1620, 2880          # 1.5x supersample; the system uses 2x lanczos
GRADE = ("curves=all='0/0 0.22/0.07 0.5/0.24 0.78/0.62 1/1',"
         "eq=brightness=-0.02:contrast=1.12:saturation=1.10,"
         "colorbalance=rm=0.05:bm=-0.05:rh=0.05:bh=-0.07,"
         "vignette=angle=PI/3.4:mode=forward")
POST = {3: "eq=brightness=0.05:contrast=0.98",   # the polish clip has no LED to carry it
        4: "eq=brightness=0.05:contrast=0.98",
        5: "eq=brightness=0.04:contrast=1.00"}


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode:
        sys.exit(f"ffmpeg failed:\n{' '.join(args)[:400]}\n{p.stderr[-2500:]}")


def zoompan(cam, n):
    z0, z1 = cam.get("z0", 1.0), cam.get("z1", 1.0)
    px0, px1 = cam.get("px0", 0.0), cam.get("px1", 0.0)
    py0, py1 = cam.get("py0", 0.0), cam.get("py1", 0.0)
    s = f"(min(on/{max(n-1,1)},1)*min(on/{max(n-1,1)},1)*(3-2*min(on/{max(n-1,1)},1)))"   # smoothstep
    return (f"zoompan=z='({z0}+({z1}-{z0})*{s})'"
            f":x='(iw-iw/zoom)*(0.5+0.5*({px0}+({px1}-{px0})*{s}))'"
            f":y='(ih-ih/zoom)*(0.5+0.5*({py0}+({py1}-{py0})*{s}))'"
            f":d=1:s={W}x{H}:fps={FPS}")


def main(tl_path, out_path):
    tl = json.load(open(tl_path))
    d = os.path.dirname(os.path.abspath(tl_path))
    tmp = tempfile.mkdtemp(prefix="reelseg-")
    segs, body_end = [], 0.0

    for i, sh in enumerate(tl["shots"]):
        dur = round(sh["end"] - sh["start"], 3)
        seg = os.path.join(tmp, f"seg{i:02d}.mp4")
        if sh["kind"] == "still":
            src = sh["src"] if os.path.isabs(sh["src"]) else os.path.join(d, sh["src"])
            run([FF, "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                 "-t", f"{dur:.3f}", "-i", src,
                 "-vf", f"scale={W}:{H},fps={FPS},format=yuv420p,setsar=1",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-an", seg])
        else:
            n = max(int(round(dur * FPS)), 1)
            vf = (f"fps={FPS},scale={SS_W}:{SS_H}:flags=bilinear,{zoompan(sh['cam'] or {}, n)},"
                  f"trim=end_frame={n},setpts=PTS-STARTPTS,{GRADE}")
            if i in POST:
                vf += "," + POST[i]
            vf += ",format=yuv420p,setsar=1"
            run([FF, "-v", "error", "-y", "-ss", f"{sh['ss']:.3f}", "-t", f"{dur + 0.2:.3f}",
                 "-i", os.path.join(ROOT, sh["src"]), "-vf", vf, "-frames:v", str(n),
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-an", seg])
            body_end = sh["end"]
        segs.append((seg, sh, dur))
        print(f"  shot {i}: {os.path.basename(sh['src'])} {dur:.3f}s -> {os.path.basename(seg)}")

    # body = hard cuts; the end card cross-fades in, exactly as the timeline says
    card, card_sh, card_dur = segs[-1]
    body_list = os.path.join(tmp, "body.txt")
    with open(body_list, "w") as f:
        for s, _, _ in segs[:-1]:
            f.write(f"file '{s}'\n")
    body = os.path.join(tmp, "body.mp4")
    run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", body_list,
         "-c", "copy", body])

    total = tl["duration"]
    xf_at, xf_dur = card_sh["start"], (card_sh["xfade"] or ["fade", 0.4])[1]

    ins = ["-i", body, "-i", card]
    fc = [f"[0:v][1:v]xfade=transition=fade:duration={xf_dur}:offset={xf_at}[bg]"]
    prev = "bg"
    for j, c in enumerate(tl["cues"]):                       # the type layers, with fades
        st, en, fd = c["start"], c["end"], 0.18
        # the PNG must be LOOPED into a real stream: a single frame sits at pts 0, so a
        # fade filter would evaluate its alpha ramp on that one frame and leave it at 0.
        ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{en-st:.3f}",
                "-i", os.path.join(d, c["png"])]
        fc.append(f"[{j+2}:v]format=rgba,fps={FPS},fade=t=in:st=0:d={fd}:alpha=1,"
                  f"fade=t=out:st={en-st-fd:.3f}:d={fd}:alpha=1,"
                  f"setpts=PTS-STARTPTS+{st}/TB[c{j}]")
        fc.append(f"[{prev}][c{j}]overlay=eof_action=pass:enable='between(t,{st},{en})'[v{j}]")
        prev = f"v{j}"
    fc.append(f"[{prev}]format=yuv420p[vout]")

    amix, alab = [], []
    for k, a in enumerate(tl["audio"]):
        ins += ["-i", os.path.join(ROOT, "audio", a["src"])]
        n = len(tl["cues"]) + 2 + k
        f = f"[{n}:a]volume={a['gain']}dB,atrim=0:{total},asetpts=PTS-STARTPTS"
        if a["music"]:
            f += f",afade=t=in:st=0:d=0.15,afade=t=out:st={total-1.4:.3f}:d=1.4"
        if a["start"] > 0:
            f += f",adelay={int(a['start']*1000)}|{int(a['start']*1000)}"
        amix.append(f + f"[a{k}]"); alab.append(f"[a{k}]")
    amix.append("".join(alab) + f"amix=inputs={len(alab)}:normalize=0:duration=longest,"
                                f"atrim=0:{total},aresample=48000[aout]")

    run([FF, "-v", "error", "-y"] + ins +
        ["-filter_complex", ";".join(fc + amix), "-map", "[vout]", "-map", "[aout]",
         "-t", f"{total:.3f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
         "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out_path])
    print("wrote", out_path)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
