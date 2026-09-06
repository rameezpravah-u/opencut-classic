#!/usr/bin/env python3
"""Build the NixWoods 20s 9:16 reel from the raw Drive clips.

Beat grid: brand-film music has a hit every 1.19s; reel offset chosen so hits land at
0.80 (light switches on), 1.99, 3.18, 4.37, 5.56, 6.75, 7.94, 9.13, 10.33, 11.52,
12.71, 13.90, 15.09, 16.28, 17.47, 18.66.
"""
import os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
ASSETS = os.path.join(ROOT, "assets")
OUT = os.path.join(ROOT, "out")
os.makedirs(OUT, exist_ok=True)

W, H, FPS, DUR = 1080, 1920, 25, 20.0
MUSIC = os.path.join(SRC, "brandfilm-9x16ish-4x5.mp4")
MUSIC_OFFSET = 4.35  # music 5.15s hit lands on reel 0.80s

# ---- palette -------------------------------------------------------------
IVORY = (244, 234, 219)
AMBER = (227, 165, 82)
ESPRESSO = (20, 17, 14)
RED = (229, 71, 60)
GREEN = (69, 194, 122)
GOLD = (242, 180, 78)
PURPLE = (181, 123, 255)

F_SERIF = os.path.join(ASSETS, "Playfair_Display-600.ttf")
F_SANS = os.path.join(ASSETS, "DM_Sans-500.ttf")
F_SANS_B = os.path.join(ASSETS, "DM_Sans-600.ttf")

# ---- edit: (source clip, source in-point, reel start, reel end, extra vf) ---
B = [0.80 + 1.19 * n for n in range(16)]  # beat grid
SEGS = [
    ("03",   0.00, 0.00, B[2],  ""),                                   # hook: dark -> Aurora on at 0.80
    ("04",   8.00, B[2], B[4],  ""),                                   # Aurora angled, warm wash on art
    ("16",   9.85, B[4], B[6],  ""),                                   # hand clicks brass dimmer, bulb ignites on B5
    ("07",   8.35, B[6], B[7],  ""),                                   # macro: teak pendant strip
    ("09",  14.00, B[7], B[8],  "colortemperature=temperature=5000"),  # macro: angled pendant, warmed slightly
    ("13",   4.60, B[8], B[10], ""),                                   # 360 loop pendant over dining
    ("14-1",12.90, B[10],B[13], ""),                                   # Glass Block: amber -> red -> green -> warm
    ("06",  10.00, B[13],B[14], ""),                                   # purple mood floor lamp
]
XFADE = 0.35
END_START = B[14] - 0.10           # 17.37: purple shot keeps most of its beat
END_LEN = DUR - END_START          # 2.63
GRADE = "eq=contrast=1.05:saturation=1.06,vignette=angle=PI/5:mode=forward"

# ---- text helpers --------------------------------------------------------
def font(path, size):
    return ImageFont.truetype(path, size)

def text_layer(lines, y_center, size=84, fpath=F_SERIF, colors=None, kicker=None,
               kicker_color=AMBER, sub=None, sub_color=None, sub_size=40, line_gap=14):
    """Render centred text (with soft shadow) onto a transparent 1080x1920 layer."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(img), ImageDraw.Draw(shadow)
    f = font(fpath, size)
    heights = []
    for ln in lines:
        bb = f.getbbox(ln)
        heights.append(bb[3] - bb[1])
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = y_center - total / 2
    if kicker:
        kf = font(F_SANS_B, 30)
        # letter-spaced kicker
        spaced = "  ".join(kicker)  # wide tracking
        kb = kf.getbbox(spaced)
        kw = kb[2] - kb[0]
        ky = y - 64
        ds.text(((W - kw) / 2, ky), spaced, font=kf, fill=(0, 0, 0, 200))
        d.text(((W - kw) / 2, ky), spaced, font=kf, fill=kicker_color + (255,))
    for i, ln in enumerate(lines):
        # per-word colouring: colors is a dict word->colour, else single colour
        words = ln.split(" ")
        # measure whole line
        bb = f.getbbox(ln)
        lw = bb[2] - bb[0]
        x = (W - lw) / 2 - bb[0]
        yy = y - bb[1]
        ds.text((x, yy), ln, font=f, fill=(0, 0, 0, 210))
        if isinstance(colors, dict):
            cx = x
            for wi, wd in enumerate(words):
                piece = wd + (" " if wi < len(words) - 1 else "")
                col = colors.get(wd.strip(".,?!"), IVORY)
                d.text((cx, yy), piece, font=f, fill=col + (255,))
                cx += f.getlength(piece)
        else:
            d.text((x, yy), ln, font=f, fill=(colors or IVORY) + (255,))
        y += heights[i] + line_gap
    if sub:
        sf = font(F_SANS, sub_size)
        sb = sf.getbbox(sub)
        sw = sb[2] - sb[0]
        sy = y + 18
        ds.text(((W - sw) / 2, sy), sub, font=sf, fill=(0, 0, 0, 200))
        d.text(((W - sw) / 2, sy), sub, font=sf, fill=(sub_color or IVORY) + (235,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    # strengthen shadow a little
    a = shadow.split()[3].point(lambda v: min(255, int(v * 1.35)))
    shadow.putalpha(a)
    return Image.alpha_composite(shadow, img)

def end_card():
    img = Image.new("RGBA", (W, H), ESPRESSO + (255,))
    # warm radial glow behind the logo
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2, 800
    for r in range(520, 0, -20):
        a = int(70 * (1 - r / 520) ** 1.6)
        gd.ellipse((cx - r, cy - r * 0.9, cx + r, cy + r * 0.9), fill=AMBER + (a,))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    logo = Image.open(os.path.join(ASSETS, "logo.png")).convert("RGBA")
    lw = 380
    logo = logo.resize((lw, int(logo.height * lw / logo.width)), Image.LANCZOS)
    img.alpha_composite(logo, ((W - lw) // 2, cy - logo.height // 2))
    d = ImageDraw.Draw(img)
    f1 = font(F_SERIF, 72)
    t1 = "Stop buying boring lights."
    b1 = f1.getbbox(t1)
    d.text(((W - (b1[2] - b1[0])) / 2 - b1[0], 1110 - b1[1]), t1, font=f1, fill=IVORY + (255,))
    f2 = font(F_SANS_B, 46)
    t2 = "nixwoods.com"
    b2 = f2.getbbox(t2)
    d.text(((W - (b2[2] - b2[0])) / 2 - b2[0], 1230 - b2[1]), t2, font=f2, fill=AMBER + (255,))
    f3 = font(F_SANS, 34)
    t3 = "Solid wood lighting  ·  Handmade in India  ·  Free shipping"
    b3 = f3.getbbox(t3)
    d.text(((W - (b3[2] - b3[0])) / 2 - b3[0], 1300 - b3[1]), t3, font=f3, fill=IVORY + (190,))
    return img

# ---- text cues: (file, start, end, layer) --------------------------------
CUES = [
    ("t1", 0.00, 3.05, text_layer(["Still lit by", "one tubelight?"], 1180, size=88)),
    ("t2", B[2] + 0.15, B[4] - 0.10,
     text_layer(["Warm light on the wall.", "Not in your eyes."], 900, size=74,
                kicker="AURORA · SOLID TEAK · 3000K")),
    ("t3", B[4] + 0.15, B[6] - 0.10,
     text_layer(["One switch.", "The whole mood changes."], 760, size=74)),
    ("t4", B[6] + 0.10, B[8] - 0.10,
     text_layer(["Solid teak.", "Solid rosewood."], 1180, size=80,
                sub="Handmade in India  ·  3-year wood warranty", sub_size=40)),
    ("t5", B[8] + 0.15, B[10] - 0.10,
     text_layer(["One light.", "The whole room."], 1200, size=84)),
    ("t6", B[10] + 0.20, B[13] - 0.10,
     text_layer(["Red. Green. Amber."], 840, size=84,
                colors={"Red": RED, "Green": GREEN, "Amber": GOLD},
                kicker="ONE LAMP · THREE MOODS")),
    ("t6b", B[12] - 0.20, B[13] - 0.10,
     text_layer(["Your room. Your mood."], 950, size=56, fpath=F_SANS)),
    ("t7", B[13] + 0.12, END_START - 0.05,
     text_layer(["Or purple."], 1180, size=84, colors={"purple": PURPLE})),
]

def build():
    for name, s, e, layer in CUES:
        layer.save(os.path.join(OUT, f"{name}.png"))
    end_card().save(os.path.join(OUT, "endcard.png"))

    cmd = ["ffmpeg", "-hide_banner", "-y"]
    fc = []
    # footage inputs
    for i, (clip, ss, rs, re, extra) in enumerate(SEGS):
        cmd += ["-ss", f"{ss:.3f}", "-t", f"{re - rs + 0.2:.3f}", "-i", os.path.join(SRC, f"{clip}.mp4")]
        vf = f"scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,{GRADE}"
        if extra:
            vf += "," + extra
        n = round((re - rs) * FPS)
        fc.append(f"[{i}:v]{vf},trim=end_frame={n},setpts=PTS-STARTPTS[s{i}]")
    nseg = len(SEGS)
    fc.append("".join(f"[s{i}]" for i in range(nseg)) + f"concat=n={nseg}:v=1:a=0,settb=1/{FPS},fps={FPS}[foot]")
    # end card
    idx = nseg
    cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{END_LEN + 0.1:.3f}", "-i", os.path.join(OUT, "endcard.png")]
    fc.append(f"[{idx}:v]format=yuv420p,setsar=1,settb=1/{FPS},fps={FPS}[end]")
    fc.append(f"[foot][end]xfade=transition=fade:duration={XFADE}:offset={END_START:.3f},settb=1/{FPS}[base]")
    # text overlays
    cur = "base"
    for k, (name, s, e, _) in enumerate(CUES):
        idx += 1
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", f"{DUR:.3f}", "-i", os.path.join(OUT, f"{name}.png")]
        fi, fo = 0.22, 0.22
        fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={s:.3f}:d={fi}:alpha=1,"
                  f"fade=t=out:st={e - fo:.3f}:d={fo}:alpha=1[o{k}]")
        fc.append(f"[{cur}][o{k}]overlay=0:0:enable='between(t,{s:.3f},{e:.3f})':format=auto[v{k}]")
        cur = f"v{k}"
    fc.append(f"[{cur}]format=yuv420p[vout]")
    # music
    idx += 1
    cmd += ["-ss", f"{MUSIC_OFFSET:.3f}", "-t", f"{DUR:.3f}", "-i", MUSIC]
    fc.append(f"[{idx}:a]afade=t=in:st=0:d=0.30,afade=t=out:st={DUR - 1.6:.2f}:d=1.6,"
              f"loudnorm=I=-14:TP=-1.5:LRA=11[aout]")
    graph = ";".join(fc)
    with open(os.path.join(OUT, "graph.txt"), "w") as fh:
        fh.write(graph)
    cmd += ["-filter_complex_script", os.path.join(OUT, "graph.txt"),
            "-map", "[vout]", "-map", "[aout]",
            "-r", str(FPS), "-t", f"{DUR:.3f}",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-profile:v", "high",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart",
            os.path.join(OUT, "NixWoods-Reel-20s-9x16.mp4")]
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)

if __name__ == "__main__":
    build()
