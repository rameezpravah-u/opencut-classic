#!/usr/bin/env python3
"""NixLine "Switch on warm." — the wall-switch reel.

Idea from @sviola_handmade's DeL0bVzt1As (a woman walks to a bare wall, reaches up to a giant on/off
toggle, it flips on and a launch poster appears on the wall). Look from @faisal_saleh_photography's
DePramhoNWl (teal shadows, amber highlights, night, shallow focus, grain). Rameez: "instead of the
cloth just use nix line in the night picture".

Plate: one generated shot (Higgsfield Seedance 2.5, job 2f7280ab…, static camera, 8 s, 24 fps) of a
woman walking to an empty night wall and pressing a spot above her head; Higgsfield's video
background remover (job d83c3caf…) gives her cutout on black. Everything NixWoods is composited
here, so the product, type and price are exact:
  - an iOS-style toggle under her fingertip (grey off, amber on), drawn UNDER her, so her hand covers it
  - on the press, the NixLine night picture (scenes/A-diwali-dusk, generated) appears on the wall as a
    framed print, with a warm spill of light; her shadow falls across it (shaded by frame/plate ratio)
  - a slow push into the print once she lowers her arm; she walks out of the shot
Music: music7-noir (103.4 bpm); its strong hit at 2.31 s lands on the press. A switch click on the press.
AI-generated footage and picture: tick the AI label anywhere this runs.

    python3 floor-reels/static/switch_reel.py   # -> concepts/switch/NX-SWITCH-nixline-switch-on-warm-9x16.mp4
"""
import os, subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
D = os.path.join(ROOT, "concepts", "switch")
SRC = os.path.join(D, "gen-woman-wall-1080p.mp4")
CUT = os.path.join(D, "gen-woman-wall-cutout.mp4")
POSTER = os.path.join(D, "poster-nixline-night.png")
OUT = os.path.join(D, "NX-SWITCH-nixline-switch-on-warm-9x16.mp4")
MUSIC = os.path.join(ROOT, "audio", "music7-noir.mp3")
TURN = os.path.join(ROOT, "audio", "sfx-turn.mp3")
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, SFPS, FPS = 1080, 1920, 24, 30
DUR = 9.6
AMBER, CREAM = np.array([232, 162, 74], np.float32), (246, 239, 228)
PCX, PCY, PW = 756, 742, 470            # print centre and width on the wall (right half, clear of her)
PUSH0, PUSH1, Z1 = 5.6, DUR, 1.25       # push in once her arm is down
SCREEN_C = (620, 880)                   # print centre on screen at the end: the switch and the print both stay whole


def frames(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def matte(orig, cut):
    """Person where the cutout reproduces the original frame; background where it went to black."""
    d = np.abs(orig.astype(np.int16) - cut.astype(np.int16)).mean(2)
    m = np.clip((26 - d) / 18, 0, 1)                          # d < 8 -> person, d > 26 -> wall
    m[(cut.max(2) < 6) & (orig.max(2) > 40)] = 0              # clearly removed
    im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MedianFilter(5))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def toggle(on):
    """iOS-style switch; on: 0..1 (knob position and amber fill)."""
    s = 2
    tw, th = 200 * s, 104 * s
    im = Image.new("RGBA", (tw + 40 * s, th + 40 * s), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((20 * s, 26 * s, 20 * s + tw, 26 * s + th), th // 2, fill=(0, 0, 0, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9 * s)))
    off = np.array([214, 214, 210], np.float32)
    col = tuple(int(v) for v in off + (AMBER - off) * on)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * s, 20 * s, 20 * s + tw, 20 * s + th), th // 2, fill=col + (255,))
    k = th - 12 * s
    kx = 20 * s + 6 * s + (tw - 12 * s - k) * on
    d.ellipse((kx + 1 * s, 26 * s + 3 * s, kx + k + 1 * s, 26 * s + k + 3 * s), fill=(0, 0, 0, 60))
    d.ellipse((kx, 26 * s, kx + k, 26 * s + k), fill=(252, 250, 246, 255))
    return im.resize((im.width // s, im.height // s), Image.LANCZOS)


def over(base, layer, xy, alpha=1.0, shade=None):
    """Alpha-composite an RGBA PIL layer onto a float RGB array at xy, optionally shaded per pixel."""
    x, y = xy
    a = np.asarray(layer).astype(np.float32) / 255
    h, w = a.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x1 <= x0 or y1 <= y0:
        return
    a = a[y0 - y:y1 - y, x0 - x:x1 - x]
    rgb, al = a[..., :3] * 255, a[..., 3:] * alpha
    if shade is not None:
        sh = shade[y0:y1, x0:x1]
        rgb = rgb * (sh if sh.ndim == 3 else sh[..., None])
    base[y0:y1, x0:x1] = base[y0:y1, x0:x1] * (1 - al) + rgb * al


def main():
    src, cut = frames(SRC), frames(CUT)
    n_src = min(len(src), len(cut))
    plate = src[0].astype(np.float32)                         # she is only at the very edge in frame 0
    lp = plate.mean(2) + 4
    # the room's light on the wall (teal from the left, amber from the right), normalised to the wall's
    # brightest point; prints and the switch are lit by it so they sit in the room instead of on the screen
    pl = np.asarray(Image.fromarray(src[0]).filter(ImageFilter.GaussianBlur(40))).astype(np.float32)
    wall = pl[int(.1 * H):int(.8 * H)]
    light = np.clip(pl / np.percentile(wall.max(2), 99) * 1.08, 0.3, 1.05)
    yy0, xx0 = np.mgrid[0:H, 0:W].astype(np.float32)
    vign = np.clip(1.12 - 0.42 * np.sqrt(((xx0 - W / 2) / W) ** 2 + ((yy0 - H / 2) / H) ** 2) * 1.6, 0.62, 1)[..., None]

    # the press: her fingertip at its highest, between 1.5 and 3.5 s
    tops = []
    for i in range(int(1.5 * SFPS), int(3.5 * SFPS)):
        m = matte(src[i], cut[i]) > 0.5
        ys, xs = np.nonzero(m[:, :int(.6 * W)])
        tops.append((ys.min(), i, int(np.median(xs[ys < ys.min() + 12]))))
    ymin = min(t[0] for t in tops)
    press = next(t for t in tops if t[0] <= ymin + 6)
    T_ON = press[1] / SFPS
    tip = (press[2], ymin)
    print(f"press at {T_ON:.2f}s, fingertip {tip}")

    tg_off, tg_on = toggle(0.0), toggle(1.0)
    TX, TY = tip[0] - tg_off.width // 2 + 10, tip[1] - 26     # fingers sit on the lower half of the switch

    poster = Image.open(POSTER).convert("RGBA")
    ph = round(PW * poster.height / poster.width)
    poster = poster.resize((PW, ph), Image.LANCZOS)
    # a thin shadow under the print, so it sits on the wall
    pshadow = Image.new("RGBA", (PW + 80, ph + 80), (0, 0, 0, 0))
    ImageDraw.Draw(pshadow).rectangle((40, 48, 40 + PW, 48 + ph), fill=(0, 0, 0, 120))
    pshadow = pshadow.filter(ImageFilter.GaussianBlur(16))
    PX, PY = PCX - PW // 2, PCY - ph // 2

    # warm spill of light from the print onto the wall
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - PCX) / (PW * 1.05)) ** 2 + ((yy - PCY) / (ph * 0.95)) ** 2)
    spill = np.clip(1.25 - r, 0, 1) ** 1.6

    tmp = OUT + ".video.mp4"
    proc = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
                             "-crf", "17", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries",
                             "bt709", "-color_trc", "bt709", tmp], stdin=subprocess.PIPE)
    rng = np.random.default_rng(9)
    n = round(DUR * FPS)
    for k in range(n):
        t = k / FPS
        i = min(round(t * SFPS), n_src - 1)
        f = src[i].astype(np.float32)
        m = matte(src[i], cut[i])[..., None]
        shade = np.clip(np.asarray(Image.fromarray(np.clip(f.mean(2) / lp * 128, 0, 255).astype(np.uint8))
                                   .filter(ImageFilter.GaussianBlur(10))).astype(np.float32) / 128, 0.32, 1.08)
        lit = light * shade[..., None]                          # room light x her shadow
        on = ease_out((t - T_ON) / 0.14)
        comp = f.copy()
        if t >= T_ON:                                          # the room answers the switch
            glow = ease((t - T_ON) / 0.45) * (0.55 + 0.05 * np.sin(t * 2.1))
            comp += (spill * glow)[..., None] * AMBER * 0.42 * shade[..., None]
            comp *= 1 + 0.06 * ease((t - T_ON) / 0.6) * np.array([1.0, 0.2, -0.8])  # a touch warmer overall
            pa = ease_out((t - T_ON) / 0.12)
            sc = 0.97 + 0.03 * ease_out((t - T_ON) / 0.28)
            if sc < 0.999:
                pz = poster.resize((round(PW * sc), round(ph * sc)), Image.LANCZOS)
            else:
                pz = poster
            over(comp, pshadow, (PCX - pshadow.width // 2, PCY - pshadow.height // 2 + 6), pa)
            over(comp, pz, (PCX - pz.width // 2, PCY - pz.height // 2), pa, lit * (1 + 0.25 * glow))
        tg = tg_off if on <= 0 else tg_on if on >= 1 else toggle(on)
        over(comp, tg, (TX, TY), 1.0, lit * (1 - 0.55 * on) + 0.55 * on)   # once on, the switch glows
        comp = m * f + (1 - m) * comp                          # she stays in front of everything
        comp = 255 * ((comp / 255) ** 1.12) * vign             # a little deeper, a soft vignette (the reference's mood)
        # push into the print
        z = 1 + (Z1 - 1) * ease((t - PUSH0) / (PUSH1 - PUSH0))
        if z > 1.0005:
            u = ease((t - PUSH0) / (PUSH1 - PUSH0))
            bw, bh = W / z, H / z
            # crop-box centre: frame centre at the start -> the box that puts the print centre on SCREEN_C
            tx, ty = PCX - SCREEN_C[0] / z + bw / 2, PCY - SCREEN_C[1] / z + bh / 2
            fx, fy = W / 2 + (tx - W / 2) * u, H / 2 + (ty - H / 2) * u
            img = Image.fromarray(np.clip(comp, 0, 255).astype(np.uint8))
            x0 = min(max(fx - bw / 2, 0), W - bw); y0 = min(max(fy - bh / 2, 0), H - bh)
            comp = np.asarray(img.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + bw, y0 + bh))).astype(np.float32)
        if i == n_src - 1:                                     # past the end of the plate: keep it alive
            comp += rng.normal(0, 3.0, (H, W, 1))
        proc.stdin.write(np.clip(comp, 0, 255).astype(np.uint8).tobytes())
    proc.stdin.close(); proc.wait()

    click = f"{T_ON:.3f}"
    subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-i", tmp, "-i", MUSIC, "-i", TURN,
                    "-f", "lavfi", "-t", "0.05", "-i", "anoisesrc=color=pink:amplitude=0.9:d=0.05",
                    "-filter_complex",
                    f"[1:a]atrim=0:{DUR:.3f},volume=0.85,afade=t=in:d=0.15,afade=t=out:st={DUR - 0.9:.3f}:d=0.9[m];"
                    f"[2:a]volume=0.45,adelay={int((T_ON + 0.05) * 1000)}|{int((T_ON + 0.05) * 1000)}[s];"
                    f"[3:a]highpass=f=1800,afade=t=out:st=0.01:d=0.04,volume=0.9,"
                    f"adelay={int(T_ON * 1000)}|{int(T_ON * 1000)}[c];"
                    f"[m][s][c]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-t", f"{DUR:.3f}", OUT], check=True)
    os.remove(tmp)
    print(os.path.relpath(OUT, ROOT), f"{DUR:.2f}s, press {click}s")


if __name__ == "__main__":
    main()
