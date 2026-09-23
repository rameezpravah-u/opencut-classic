#!/usr/bin/env python3
"""render_reel.py — 9:16 product reel for the Double Arm Teak Pendant, built frame by frame.

    python3 render_reel.py [--out reel.mp4]

Why not the repo's make_reel.py: its still path supersamples to 2160x3840 and runs the
"contain" composite through gblur at that size. On this box that renders at 0.4 fps — a 14 s
cut takes ~15 minutes and got killed twice. Everything here is PIL at 1080x1920 (~20 ms a
frame) with one ffmpeg encode at the end. It reuses the repo's type, palette, logo and safe
zone (reelkit + presets.json) so the output still looks like a NixWoods reel.

THE FRAMING PROBLEM THIS FILE EXISTS TO SOLVE
Every source still is square (1:1). A 9:16 cover crop keeps 9/16 = 56% of the width, so a
49-inch bar loses its ends — the length IS the product. Two consequences drive the shot list:

  * On a square source, only the horizontal crop centre matters; the vertical one is a no-op
    (the window already spans the full height). `cx` below is therefore the real control.
  * The tightest sharp cover crop on a 1254 px square is already 1.53x upscale. Going tighter
    costs resolution fast, so scale variety comes from alternating cover and contain rather
    than from cropping harder. Every shot prints its upscale factor at render time.

Structure: four tight/mid beats that withhold the length, then one deliberate contain
pull-back on the bright dining frame where the whole four feet lands as the payoff.
"""
import argparse, os, subprocess, sys, math
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
REEL = os.path.abspath(os.path.join(HERE, *[".."] * 7, "nixwoods-reel"))
sys.path.insert(0, os.path.join(REEL, "rubik-reels"))
sys.path.insert(0, os.path.join(REEL, "system"))
import reelkit as rk                      # type, logo, palette, safe zone

W, H, FPS = 1080, 1920, 25
AR = W / H
HF = os.path.join(REEL, "teak-reels", "hf")
MUSIC = os.path.join(REEL, "teak-reels", "audio", "music3-design.mp3")

TEXT = (245, 245, 242)
ACCENT = (232, 162, 74)
CARD = (12, 12, 12)
HEAD_FONT, SUB_FONT, KICK_FONT = "Space_Grotesk-700.ttf", "Inter-300.ttf", "Inter-600.ttf"

# --------------------------------------------------------------------------
# the cut
# --------------------------------------------------------------------------
# fit      cover   = fill the frame from a 9:16 window of the source; cx picks the window
#          contain = whole frame over a blurred, dimmed copy of itself; top = where it sits
# z0/z1    camera zoom across the shot (1.0 = the widest window that still fills)
# cx0/cx1  horizontal centre of the window, 0..1, animated across the shot
# gamma    <1 lifts the toe. Only sh03 gets one: it is the one genuinely dark frame here.
SHOTS = [
    dict(name="hook · dark, two lines, ends out of frame",
         src="sh03-dark-two-lines.jpg", dur=3.0, fit="cover",
         z0=1.00, z1=1.10, cx0=0.40, cx1=0.48, gamma=0.86,
         text=["How many lines", "do you see?"], size=62, y=1290),
    dict(name="proof · lit underside, twin channels, other end of the bar",
         src="sh01-underside-twin.jpg", dur=3.0, fit="cover",
         z0=1.08, z1=1.00, cx0=0.64, cx1=0.56,
         # type sits below the bar, not across it: at y=1290 the second line crossed the lit
         # channel and the copy fought the product. 1430 puts it on the fluted wall, still
         # inside the safe zone (bottom 1500).
         text=["Two. Cut into one", "piece of teak."], size=54, y=1430),
    dict(name="macro · the end cap, both channels open",
         src="sh04-end-channels.webp", dur=1.9, fit="contain", top="centre",
         z0=1.00, z1=1.10),
    dict(name="mount · one teak canopy, two cables",
         src="sh05-canopy-cables.jpg", dur=2.3, fit="contain", top=250,
         z0=1.06, z1=1.00,
         text=["One teak canopy.", "Two cables."], size=50, y=1430),
    dict(name="payoff · pull back, the whole 49 in over the table",
         src="sh00-marble-dining.jpg", dur=3.8, fit="contain", top=250,
         z0=1.10, z1=1.00,
         text=["49 inches,", "right over the table."], size=54, y=1430),
]
CARD_DUR = 2.4
XFADE = 0.40          # dissolve between shots; the end card fades from black-ish


# --------------------------------------------------------------------------
# framing
# --------------------------------------------------------------------------
def cover_window(src_w, src_h, z, cx):
    """9:16 window inside the source. z=1.0 is the largest such window (the cover crop)."""
    win_h = src_h / z
    win_w = win_h * AR
    if win_w > src_w:                       # source narrower than 9:16 — width binds instead
        win_w = src_w / z
        win_h = win_w / AR
    x = (src_w - win_w) * cx
    y = (src_h - win_h) * 0.5
    return x, y, win_w, win_h


def contain_base(im, top, bg_dim=0.42, bg_blur=38):
    """Whole frame over a blurred, dimmed copy of itself.

    The dimming is not decoration: an undimmed blurred backing of bright studio photography
    lands near 150 luma, and white type on it is unreadable. At 0.42 the surround reads as a
    deliberate dark mat, the sharp subject pops off it, and the lower band is clean enough to
    carry a line of copy inside the safe zone.

    Never call this on a dark source — there the backing is already black and the subject
    becomes a thin lit band in an empty frame. sh03 is why every shot above states its fit.
    """
    # Backing: blur small then upscale. Same look as a big-sigma gaussian at full size and
    # about forty times cheaper, which matters because this box is already loaded.
    sw, sh = W // 6, H // 6
    scale = max(sw / im.width, sh / im.height)
    small = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.BILINEAR)
    bx, by = (small.width - sw) // 2, (small.height - sh) // 2
    small = small.crop((bx, by, bx + sw, by + sh)).filter(ImageFilter.GaussianBlur(bg_blur / 6))
    bg = small.resize((W, H), Image.BICUBIC)
    bg = ImageEnhance.Brightness(bg).enhance(bg_dim)
    bg = ImageEnhance.Color(bg).enhance(0.8)

    fw = int(W * 0.965)
    fg = im.resize((fw, max(1, round(im.height * fw / im.width))), Image.LANCZOS)
    y = (H - fg.height) // 2 if top == "centre" else int(top)
    bg.paste(fg, ((W - fg.width) // 2, y))
    return bg


def shot_frames(sh):
    """yield every output frame of one shot. Frames are produced lazily and written straight to
    the encoder: holding a whole 14 s reel at 1080x1920 costs ~2.8 GB and gets the job killed."""
    im = Image.open(os.path.join(HF, sh["src"])).convert("RGB")
    if sh.get("gamma"):
        lut = [min(255, round(255 * (i / 255) ** sh["gamma"])) for i in range(256)]
        im = im.point(lut * 3)

    n = max(1, round(sh["dur"] * FPS))
    if sh["fit"] == "contain":
        base = contain_base(im, sh.get("top", "centre"))
        up = W / im.width                   # what the sharp subject is actually scaled by
        src = base
    else:
        src = im
        up = H / (im.height / max(sh["z0"], sh["z1"]))

    lay = line_layer(sh["text"], sh["size"], sh["y"]) if sh.get("text") else None
    fin = fout = int(0.35 * FPS)
    hold_in = int(0.12 * FPS)
    arr = np.asarray(lay) if lay is not None else None

    def gen():
        for i in range(n):
            t = 0 if n == 1 else i / (n - 1)
            e = t * t * (3 - 2 * t)         # smoothstep: no visible start/stop on the move
            z = sh["z0"] + (sh["z1"] - sh["z0"]) * e
            c0 = sh.get("cx0", 0.5)
            cx = c0 + (sh.get("cx1", c0) - c0) * e
            x, y, ww, wh = cover_window(src.width, src.height, z, cx)
            f = src.resize((W, H), Image.LANCZOS, box=(x, y, x + ww, y + wh))
            if lay is None:
                yield f; continue
            a = 1.0
            if i < hold_in:
                a = 0.0
            elif i < hold_in + fin:
                a = (i - hold_in) / fin
            elif i > n - 1 - fout:
                a = max(0.0, (n - 1 - i) / fout)
            if a <= 0.001:
                yield f; continue
            l = lay if a >= 0.999 else Image.fromarray(
                np.dstack([arr[:, :, :3], (arr[:, :, 3] * a).astype(np.uint8)]), "RGBA")
            yield Image.alpha_composite(f.convert("RGBA"), l).convert("RGB")
    return gen(), n, up


# --------------------------------------------------------------------------
# type
# --------------------------------------------------------------------------
def line_layer(lines, size, y):
    return rk.text_layer(lines, y_center=y, size=size, fontfile=HEAD_FONT, color=TEXT,
                         align="left", x_left=96, line_gap=10,
                         shadow_blur=18, shadow_alpha=225, box=None)   # no plate: a shadow only


def end_card():
    card = rk.solid_card(CARD)
    logo = rk.logo_layer(width=300, cy=690)
    head = rk.text_layer(["Two lines.", "One piece of teak."], y_center=1010, size=64,
                         fontfile=HEAD_FONT, color=TEXT, align="center", line_gap=12,
                         kicker="solid teak · 3000K · 49 in", kicker_color=ACCENT,
                         kicker_font=KICK_FONT, kicker_size=27,
                         sub="nixwoods.com", sub_color=TEXT, sub_size=38, sub_font=SUB_FONT,
                         shadow_blur=0, shadow_alpha=0)
    for lay in (logo, head):
        card = Image.alpha_composite(card.convert("RGBA"), lay)
    return card.convert("RGB")


# --------------------------------------------------------------------------
# assemble — one pass, straight into the encoder
# --------------------------------------------------------------------------
def ffmpeg_exe():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def segments():
    """(frame iterator, frame count, upscale factor, label) for every segment of the cut"""
    for sh in SHOTS:
        it, n, up = shot_frames(sh)
        yield it, n, up, f"{sh['name']}  [{sh['src']} · {sh['fit']}]"
    card = end_card()
    n = round(CARD_DUR * FPS)
    yield (card for _ in range(n)), n, 1.0, "end card"


def render(out_path):
    xf = int(XFADE * FPS)
    dur_est = sum(round(sh["dur"] * FPS) for sh in SHOTS) + round(CARD_DUR * FPS)
    dur_est = (dur_est - xf * len(SHOTS)) / FPS

    cmd = [ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", MUSIC,
           "-filter_complex",
           f"[1:a]atrim=0:{dur_est:.3f},asetpts=PTS-STARTPTS,volume=-5dB,"
           f"afade=t=in:st=0:d=0.5,afade=t=out:st={max(0.0, dur_est - 1.8):.3f}:d=1.8[a]",
           "-map", "0:v", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "160k", "-shortest", out_path]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    print(f"{'segment':62s} {'dur':>6s} {'upscale':>8s}")
    written = 0
    pending = []                     # the outgoing segment's dissolve tail, at most xf frames
    for it, n, up, label in segments():
        flag = "  ! soft" if up > 2.0 else ""
        print(f"{label:62s} {n / FPS:5.2f}s {up:7.2f}x{flag}")
        k = min(xf, n, len(pending)) if pending else 0
        for i, f in enumerate(it):
            if i < k:                                   # dissolve: blend over the held tail
                f = Image.blend(pending[i], f, (i + 1) / (k + 1))
            elif pending and i == k:
                pending = []
            if n - i <= xf:                             # hold this segment's own tail
                if n - i == xf:
                    pending = []
                pending.append(f)
                continue
            p.stdin.write(f.tobytes()); written += 1
        if len(pending) > xf:
            pending = pending[-xf:]
    for f in pending:                                   # last segment's tail has nothing to fade to
        p.stdin.write(f.tobytes()); written += 1
    p.stdin.close()
    if p.wait() != 0:
        raise SystemExit("encode failed")
    print(f"\n{written} frames · {written / FPS:.2f}s @ {FPS} fps · {W}x{H}")
    return out_path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(HERE, "reel.mp4"))
    a = ap.parse_args()
    render(a.out)
    print("wrote", a.out, f"{os.path.getsize(a.out) / 1e6:.2f} MB")
