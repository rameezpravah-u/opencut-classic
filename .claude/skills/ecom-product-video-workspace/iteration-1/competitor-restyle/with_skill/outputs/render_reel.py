#!/usr/bin/env python3
"""render_reel.py — build L3-teak-assembly.json with nixwoods-reel's own engine.

Why this wrapper exists instead of calling make_reel.py directly:

reelkit's `fit="contain"` path builds the blurred backing plate at 2x supersample
(2160x3840) and runs `gblur=sigma=44` on it *every frame*. Measured on this box:

    cover  still chain ....  3.8 s of wall clock per 1 s of output
    contain still chain ... 28.7 s per 1 s of output      <-- the whole render's cost

This cut has 11.5 s of `contain` stills (t_underside x3, t_canopy, t_dining), so the
single filter_complex needs ~450 s and blows any sane foreground timeout.

A Gaussian blur is a low-pass filter, so blurring at 1/4 linear scale with sigma/4 and
scaling back up is visually equivalent to blurring at full size — the information the
big blur would have thrown away is exactly what the downscale throws away. Measured:
28.7 s -> 11.3 s per second of output, ~2.5x, with no visible difference in the plate
(checked frame-to-frame: see NOTES.md).

Nothing else about the engine, the brief, the grade or the timings is changed.

    python3 render_reel.py [--audio music|clean|both]
"""
import os
import sys

NR = "/home/user/opencut-classic/nixwoods-reel"
sys.path.insert(0, os.path.join(NR, "system"))
sys.path.insert(0, os.path.join(NR, "rubik-reels"))

import reelkit as rk  # noqa: E402

_orig_still_chain = rk.still_chain
W, H, FPS = rk.W, rk.H, rk.FPS


def fast_still_chain(n_frames, cam=None, crop_cx=0.5, crop_cy=0.5, post="", fit="cover", uid=0,
                     bg_blur=44, bg_dim=-0.18, contain=0.98):
    """reelkit.still_chain with a cheaper — not different — contain backing plate."""
    if fit != "contain":
        return _orig_still_chain(n_frames, cam=cam, crop_cx=crop_cx, crop_cy=crop_cy, post=post,
                                 fit=fit, uid=uid, bg_blur=bg_blur, bg_dim=bg_dim, contain=contain)
    bw, bh = W // 2, H // 2                      # 1/4 of the linear size reelkit uses
    cov = (f"scale='if(gte(iw/ih,{W/H}),-2,{bw})':'if(gte(iw/ih,{W/H}),{bh},-2)':flags=bilinear,"
           f"crop={bw}:{bh}:'(iw-{bw})*0.5':'(ih-{bh})*0.5'")
    con = (f"scale='if(gte(iw/ih,{W/H}),{int(W*2*contain)},-2)':'if(gte(iw/ih,{W/H}),-2,{int(H*2*contain)})'"
           f":flags=lanczos")
    head = (f"split=2[bg{uid}][fg{uid}];"
            f"[bg{uid}]{cov},gblur=sigma={bg_blur/4.0},eq=brightness={bg_dim}:saturation=0.85,"
            f"scale={W*2}:{H*2}:flags=bilinear[bgb{uid}];"
            f"[fg{uid}]{con}[fgs{uid}];"
            f"[bgb{uid}][fgs{uid}]overlay=(W-w)/2:(H-h)/2:format=auto,")
    parts = [head + "setsar=1",
             rk.cam_filter(n_frames, **(cam or {})),
             f"trim=end_frame={n_frames},setpts=PTS-STARTPTS"]
    if post:
        parts.append(post)
    parts.append(f"fps={FPS},format=yuv420p,settb=1/{FPS}")
    return ",".join(parts)


rk.still_chain = fast_still_chain

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    import make_reel
    brief = os.path.join(HERE, "L3-teak-assembly.json")
    audio = "music"
    if "--audio" in sys.argv:
        audio = sys.argv[sys.argv.index("--audio") + 1]
    sys.argv = ["make_reel.py", brief, "--audio", audio, "--no-sheet"]
    make_reel.main()


# guarded: importing this module must only install the patch, never start a render.
# (It did once, and the duplicate render raced the real one over the same output path.)
if __name__ == "__main__":
    main()
