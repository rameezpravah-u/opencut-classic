#!/usr/bin/env python3
"""render_lowmem.py — render a nixwoods-reel brief inside a memory-capped container.

Why this exists
---------------
`system/make_reel.py` builds one giant ffmpeg filtergraph: every shot is decoded at
2x supersample (2160x3840, see reelkit.still_chain/video_chain) and all of them stay
alive in the same process while the xfade chain folds them together. For L2-linear-teak
that is 13 simultaneous 2160x3840 chains, and in this container the kernel OOM-killed it:

    Memory cgroup out of memory: Killed process 1874 (ffmpeg)
    total-vm:11472424kB, anon-rss:4987512kB          (dmesg, oom_memcg=claude-code-bash)

Nothing creative is changed here. The reel is still built by `mechanisms.build()`, so the
shot list, durations, camera moves, grade, text layers, end card and audio are exactly what
the brief and presets.json specify. Only the *execution* differs:

  stage A  one ffmpeg per shot            -> seg_NN.mp4   (peak = ONE supersampled chain)
  stage B  one ffmpeg per dissolve        -> trans_NN.mp4 (two 1080x1920 inputs, d seconds)
  stage C  bodies (the non-overlap parts) -> body_NN.mp4
  stage D  concat demuxer, -c copy        -> base.mp4
  stage E  text cue PNGs + music/sfx      -> <name>-music.mp4

Stages B/C are frame-exact: a dissolve of nd frames consumes the last nd frames of the
outgoing shot and the first nd frames of the incoming one, which is precisely what
xfade(duration=d, offset=len-d) does in the monolithic graph.

Usage:  python3 render_lowmem.py <brief.json> [-o final.mp4] [--work DIR]
"""
import argparse, json, os, subprocess, sys

REEL_ROOT = "/home/user/opencut-classic/nixwoods-reel"
sys.path.insert(0, os.path.join(REEL_ROOT, "system"))
sys.path.insert(0, os.path.join(REEL_ROOT, "rubik-reels"))

import reelkit as rk
import mechanisms as MX
from imageio_ffmpeg import get_ffmpeg_exe

FFMPEG = get_ffmpeg_exe()
FPS = rk.FPS


def run(cmd, log):
    with open(log, "w") as fh:
        r = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        sys.stderr.write(open(log).read()[-2500:])
        raise SystemExit(f"ffmpeg failed (rc={r.returncode}) -> {log}")


def enc(crf="12"):
    """Visually lossless intermediate; the only lossy step that matters is stage E.

    The colour tags are load-bearing, not cosmetic. Stills carry no colour metadata while
    the workshop clip is tagged bt709, so a `-c copy` concat of the two produced a stream
    whose parameters change mid-file. ffmpeg then logged

        Reconfiguring filter graph because video parameters changed to yuv420p(tv, bt709)

    and deadlocked (55 threads in futex_do_wait, CPU time frozen, progress line stuck on
    one frame while the log kept ticking). Tagging every piece identically removes the
    mid-stream reconfiguration."""
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", crf,
            "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
            "-colorspace", "bt709", "-an"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("-o", "--out", required=True, help="final mp4 path")
    ap.add_argument("--work", default="/tmp/reel-work")
    ap.add_argument("--root", default=None)
    a = ap.parse_args()

    brief = json.load(open(a.brief, encoding="utf-8"))
    root = os.path.abspath(a.root) if a.root else os.path.join(
        REEL_ROOT, MX.PRESETS["products"][brief.get("product", "rubik")]["root"])
    work = os.path.abspath(a.work)
    os.makedirs(work, exist_ok=True)

    # the system builds the reel: shots, camera, grade, text layers, cards, audio
    reel = MX.build(brief, root, work)
    segs = reel.segs
    print(f"built {reel.name}: {reel.duration:.2f}s, {len(segs)} segments, "
          f"{len(reel.cues)} text cues, {len(reel.audio)} audio")

    n = [int(round(s["dur"] * FPS)) for s in segs]                       # frames per shot
    nd = [int(round(s["xfade"][1] * FPS)) if s["xfade"] else 0 for s in segs]  # dissolve into shot i
    nd[0] = 0
    kind = [(s["xfade"][0] if s["xfade"] else None) for s in segs]

    # --- clamp dissolves that do not fit their shot -------------------------
    # The brief gives every boundary a 0.35 s dissolve, but two shots are flash cuts
    # (0.4 s = 10f and 0.6 s = 15f) and cannot carry 9+9 frames of dissolve. The monolithic
    # graph does not complain: it just lets the outgoing and incoming dissolves OVERLAP, so
    # the flash shot never reaches full opacity and the beat is effectively lost. Here the
    # two dissolves around a short shot are shrunk symmetrically until at least one frame of
    # that shot plays clean, which is what a punch cut is supposed to do.
    for _ in range(8):
        changed = False
        for i in range(len(segs)):
            out_i = nd[i + 1] if i + 1 < len(segs) else 0
            if nd[i] + out_i >= n[i]:
                room = n[i] - 1
                tot = nd[i] + out_i
                a_ = max(0, int(nd[i] * room / tot)) if tot else 0
                b_ = max(0, room - a_)
                if nd[i] != a_:
                    nd[i] = a_; changed = True
                if i + 1 < len(segs) and nd[i + 1] != b_:
                    nd[i + 1] = b_; changed = True
                print(f"  ! shot {i} ({n[i]}f) cannot carry its dissolves; "
                      f"clamped to {nd[i]}f in / {nd[i+1] if i+1 < len(segs) else 0}f out")
        if not changed:
            break
    nd[0] = 0

    # ---- stage A: one ffmpeg per shot -------------------------------------
    seg_mp4 = []
    for i, s in enumerate(segs):
        p = os.path.join(work, f"seg{i:02d}.mp4")
        seg_mp4.append(p)
        if os.path.exists(p):
            continue
        kw = dict(s["kw"])
        post = kw.pop("post", "")
        grade = kw.pop("grade", reel.grade)
        post = ",".join(x for x in [grade, post] if x)
        cmd = [FFMPEG, "-hide_banner", "-y"]
        if s["kind"] == "video":
            slow = kw.get("slow", 1.0) or 1.0
            speed = kw.get("speed", 1.0) or 1.0
            src_dur = s["dur"] / slow * speed + 0.4
            cmd += ["-ss", f"{s['ss']:.3f}", "-t", f"{src_dur:.3f}", "-i", s["path"],
                    "-filter_complex", f"[0:v]{rk.video_chain(n[i], post=post, **kw)}[v]"]
        else:
            cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{s['dur'] + 0.2:.3f}",
                    "-i", s["path"],
                    "-filter_complex", f"[0:v]{rk.still_chain(n[i], post=post, uid=i, **kw)}[v]"]
        cmd += ["-map", "[v]", "-frames:v", str(n[i]), "-r", str(FPS)] + enc() + [p]
        run(cmd, p + ".log")
        print(f"  A shot {i:02d} {n[i]:4d}f  {os.path.basename(s['path'])}", flush=True)

    # ---- stages B and C: dissolves and bodies -----------------------------
    pieces = []
    for i, s in enumerate(segs):
        if nd[i]:                                    # dissolve INTO this shot
            t = os.path.join(work, f"trans{i:02d}.mp4")
            d = nd[i] / FPS
            # xfade refuses a stream whose frame rate is unknown, and trim+setpts erases it
            # ("current rate of 1/0 is invalid"), so re-assert fps/timebase on both branches.
            fc = (f"[0:v]trim=start_frame={n[i-1]-nd[i]}:end_frame={n[i-1]},setpts=PTS-STARTPTS,"
                  f"fps={FPS},settb=1/{FPS}[a];"
                  f"[1:v]trim=end_frame={nd[i]},setpts=PTS-STARTPTS,"
                  f"fps={FPS},settb=1/{FPS}[b];"
                  f"[a][b]xfade=transition={kind[i]}:duration={d:.3f}:offset=0,"
                  f"fps={FPS},settb=1/{FPS}[v]")
            run([FFMPEG, "-hide_banner", "-y", "-i", seg_mp4[i-1], "-i", seg_mp4[i],
                 "-filter_complex", fc, "-map", "[v]", "-frames:v", str(nd[i]),
                 "-r", str(FPS)] + enc() + [t], t + ".log")
            pieces.append(t)
        # body = frames this shot contributes on its own
        start = nd[i]
        end = n[i] - (nd[i+1] if i + 1 < len(segs) else 0)
        if end <= start:
            raise SystemExit(f"shot {i} is shorter than its two dissolves ({n[i]}f vs "
                             f"{nd[i]}+{nd[i+1] if i+1 < len(segs) else 0}f)")
        b = os.path.join(work, f"body{i:02d}.mp4")
        run([FFMPEG, "-hide_banner", "-y", "-i", seg_mp4[i], "-filter_complex",
             f"[0:v]trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS,"
             f"fps={FPS},settb=1/{FPS}[v]", "-map", "[v]",
             "-frames:v", str(end - start), "-r", str(FPS)] + enc() + [b], b + ".log")
        pieces.append(b)

    total = sum(n) - sum(nd)
    dur = total / FPS      # true runtime after the dissolve clamp above
    print(f"  B/C {len(pieces)} pieces, {total} frames = {dur:.2f}s "
          f"(brief said {reel.duration:.2f}s)")

    # ---- stage D: concat, no re-encode ------------------------------------
    lst = os.path.join(work, "concat.txt")
    with open(lst, "w") as fh:
        for p in pieces:
            fh.write(f"file '{p}'\n")
    base = os.path.join(work, "base.mp4")
    run([FFMPEG, "-hide_banner", "-y", "-f", "concat", "-safe", "0", "-i", lst,
         "-c", "copy", base], base + ".log")

    # ---- stage E: text cues + audio (mirrors reelkit.Reel.render) ---------
    # Split into a video pass and an audio pass. In one combined pass ffmpeg has to
    # interleave a slow filtered video stream with a fast audio mix, which is where the
    # deadlock above surfaced; separately neither can wait on the other.
    cmd_v = [FFMPEG, "-hide_banner", "-y", "-i", base]
    fc_v, idx, cur = [], 1, "0:v"
    for k, (p_, s_, e_, fi, fo, rise) in enumerate(reel.cues):
        cmd_v += ["-loop", "1", "-framerate", str(FPS), "-t", f"{e_ - s_ + 0.2:.3f}", "-i", p_]
        fc_v.append(f"[{idx}:v]format=rgba,fade=t=in:st=0:d={fi}:alpha=1,"
                    f"fade=t=out:st={e_ - s_ - fo:.3f}:d={fo}:alpha=1,setpts=PTS+{s_:.3f}/TB[o{k}]")
        yexpr = f"{rise}*(1-min((t-{s_:.3f})/{max(fi, 0.05):.3f},1))" if rise else "0"
        fc_v.append(f"[{cur}][o{k}]overlay=0:'{yexpr}':enable='between(t,{s_:.3f},{e_:.3f})':"
                    f"format=auto[v{k}]")
        cur = f"v{k}"
        idx += 1
    fc_v.append(f"[{cur}]format=yuv420p[vout]")

    cmd_a = [FFMPEG, "-hide_banner", "-y"]
    fc_a, alabels, aidx = [], [], 0
    for j, au in enumerate(reel.audio):
        # music7-noir.mp3 is 20.04 s but this reel runs 26.56 s. Without looping,
        # amix=duration=longest ends at 20 s, which left the dining-room payoff AND the end
        # card silent -- and, with -shortest on the mux, actually truncated the video to 20 s.
        # Loop the bed and let atrim below cut it to length.
        if au.get("music"):
            cmd_a += ["-stream_loop", "-1"]
        cmd_a += ["-i", au["path"]]
        chain = ["aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"]
        if au["start"] < 0:
            chain.append(f"atrim=start={-au['start']:.3f},asetpts=PTS-STARTPTS")
            st = 0.0
        else:
            delay = int(au["start"] * 1000)
            chain.append(f"adelay={delay}|{delay}")
            st = au["start"]
        if au["fi"]:
            chain.append(f"afade=t=in:st={st:.3f}:d={au['fi']}")
        if au["fo"]:
            chain.append(f"afade=t=out:st={dur - au['fo']:.3f}:d={au['fo']}")
        chain.append(f"volume={au['gain']}dB")
        if au.get("duck"):
            env = "+".join(f"between(t,{d0},{d1})*{db}" for d0, d1, db in au["duck"])
            chain.append(f"volume='pow(10,({env})/20)':eval=frame")
        fc_a.append(f"[{aidx}:a]{','.join(chain)}[a{j}]")
        alabels.append(f"a{j}")
        aidx += 1
    if alabels:
        fc_a.append("".join(f"[{l}]" for l in alabels) +
                    f"amix=inputs={len(alabels)}:duration=longest:normalize=0,"
                    f"atrim=0:{dur:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    graph = os.path.join(work, "final-v.graph")
    open(graph, "w").write(";\n".join(fc_v))
    vonly = os.path.join(work, "vonly.mp4")
    run(cmd_v + ["-filter_complex_script", graph, "-map", "[vout]", "-an",
                 "-r", str(FPS), "-t", f"{dur:.3f}",
                 "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                 "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                 "-profile:v", "high", vonly], os.path.join(work, "final-v.log"))
    print("  E1 text burned ->", os.path.basename(vonly), flush=True)

    aonly = None
    if alabels:
        agraph = os.path.join(work, "final-a.graph")
        open(agraph, "w").write(";\n".join(fc_a))
        aonly = os.path.join(work, "aonly.m4a")
        run(cmd_a + ["-filter_complex_script", agraph, "-map", "[aout]", "-vn",
                     "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                     "-t", f"{dur:.3f}", aonly], os.path.join(work, "final-a.log"))
        print("  E2 audio mixed ->", os.path.basename(aonly), flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    mux = [FFMPEG, "-hide_banner", "-y", "-i", vonly]
    if aonly:
        mux += ["-i", aonly, "-map", "0:v", "-map", "1:a", "-c", "copy", "-shortest"]
    else:
        mux += ["-c", "copy"]
    run(mux + ["-movflags", "+faststart", a.out], os.path.join(work, "final-mux.log"))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
