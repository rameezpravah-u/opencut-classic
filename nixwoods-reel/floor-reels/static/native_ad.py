#!/usr/bin/env python3
"""NixLine "native" static ad - phone frame + Instagram-style caption boxes.

Lesson taken from a reference post (sannidhyabaweja, DeGkawhCB2j, slide 3: "Make it look pretty" vs
"Make it look native"): a phone-shot product in a hand, in a real place, with text that looks typed in
the Instagram app, beats a styled studio shot. Our own account agrees - the raw workshop reels drew
174 and 95 likes against 3-23 for the polished posts.

What is NOT borrowed: the reference's "reply to a customer's comment" sticker. NixWoods has no customer
comment to quote, and the system never fabricates a testimonial, so every line here is the brand's own
voice and every claim is a PDP fact (solid teak, no MDF, no veneer, handcrafted).

Frames are Rameez's own footage (floor-reels/src, tonemapped from the iPhone HLG originals). No AI.

    python3 floor-reels/static/native_ad.py          # writes floor-reels/out/static/*.jpg
"""
import os, subprocess
import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                       # floor-reels/
FONT = os.path.join(ROOT, "..", "assets", "DM_Sans-600.ttf")
OUT = os.path.join(ROOT, "out", "static")
FF = imageio_ffmpeg.get_ffmpeg_exe()

# card -> source frame, caption boxes (one box per line, Instagram "classic" style), where they sit
CARDS = {
    "lit": {
        "src": ("src/nx07-7922.mp4", 0.05),
        "boxes": [["stop buying metal", "floor lamps."], ["solid teak.", "no veneer.", "handmade."]],
        "box_x": [540, None],          # None = beside the lamp, so the lit end stays clear
    },
    # Fully generated (Higgsfield gpt_image_2_5, 7 Oct, reference = the real PDP marble-corner photo).
    # Lamp matches the reference; it reads taller than its real 30 in, so this card carries no size claim.
    # Meta AI disclosure must be ticked if this runs paid; isAiGenerated true if posted organically.
    "gen": {
        "src": ("hf/nx-gen-native-bedroom.jpg",),
        "boxes": [["stop buying metal", "floor lamps."], ["solid teak.", "warm light.", "plug in."]],
        "box_x": [430, 330],
        "formats": ["4x5"],
    },
    "back": {
        "src": ("src/nx06-7921.mp4", 0.25),
        "boxes": [["flip it.", "still solid teak."], ["no mdf. no veneer."]],
        "box_x": [540, 540],
    },
}
# per format: output size, crop window into the 1080x1920 frame (y0), box anchor y for each box (top edge)
FORMATS = {
    "4x5":  {"size": (1080, 1350), "y0": {"lit": 430, "back": 300, "gen": 0}, "box_y": {"lit": [70, 860], "back": [80, 1060], "gen": [120, 560]}, "beside_x": 870},
    "9x16": {"size": (1080, 1920), "y0": {"lit": 0,   "back": 0},   "box_y": {"lit": [260, 1130], "back": [280, 1330]}, "beside_x": 790},
}
SAFE_9x16 = (230, 1500)        # presets.json safe zone: y 230-1500, x 70-950 (Reels / Stories UI)


def grab(clip, t=None):
    if clip.startswith("hf/"):                    # a generated still, already 4:5 - scale to the frame width
        im = Image.open(os.path.join(ROOT, clip)).convert("RGB")
        return im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
    p = subprocess.run([FF, "-nostdin", "-v", "error", "-ss", f"{t:.3f}", "-i", os.path.join(ROOT, clip),
                        "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                       capture_output=True, stdin=subprocess.DEVNULL, check=True)
    return Image.fromarray(np.frombuffer(p.stdout, np.uint8).reshape(1920, 1080, 3))


def caption_block(lines, font, pad_x=22, pad_y=12, radius=14, gap=-2):
    """White rounded box per line, centred, touching lines merged - the in-app 'classic' text style."""
    asc, desc = font.getmetrics()
    lh = asc + desc
    widths = [font.getlength(l) for l in lines]
    W = int(max(widths) + 2 * pad_x)
    H = int(len(lines) * (lh + 2 * pad_y) + (len(lines) - 1) * gap)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    y = 0
    for l, w in zip(lines, widths):
        bw = int(w + 2 * pad_x)
        x = (W - bw) // 2
        d.rounded_rectangle([x, y, x + bw, y + lh + 2 * pad_y], radius=radius, fill=(255, 255, 255, 255))
        y += lh + 2 * pad_y + gap
    y = 0
    for l, w in zip(lines, widths):
        d.text(((W - w) / 2, y + pad_y), l, font=font, fill=(17, 17, 17, 255))
        y += lh + 2 * pad_y + gap
    return im


def render(card, fmt):
    c, f = CARDS[card], FORMATS[fmt]
    frame = grab(*c["src"])
    W, H = f["size"]
    y0 = f["y0"][card]
    img = frame.crop((0, y0, W, y0 + H)).convert("RGB")
    # a phone shot, so only a light unsharp to undo the video-frame softness; no grade, no vignette
    img = img.filter(ImageFilter.UnsharpMask(radius=1.6, percent=55, threshold=2))
    font = ImageFont.truetype(FONT, 50)
    for lines, by, cx in zip(c["boxes"], f["box_y"][card], c["box_x"]):
        blk = caption_block(lines, font)
        bx = (cx if cx is not None else f["beside_x"]) - blk.width // 2
        if fmt == "9x16":
            assert SAFE_9x16[0] <= by and by + blk.height <= SAFE_9x16[1], (card, lines, by, blk.height)
            assert bx >= 70 and bx + blk.width <= 950, (card, lines, bx, blk.width)
        shadow = Image.new("RGBA", blk.size, (0, 0, 0, 0))
        shadow.putalpha(blk.getchannel("A").point(lambda a: a * 0.22))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        img.paste(shadow, (bx, by + 3), shadow)
        img.paste(blk, (bx, by), blk)
    words = sum(len(l.split()) for b in c["boxes"] for l in b)
    assert words <= 12, (card, words)                 # PLAYBOOK: 12 words a screen
    os.makedirs(OUT, exist_ok=True)
    out = os.path.join(OUT, f"nixline-native-{card}-{fmt}.jpg")
    img.save(out, quality=93, subsampling=0)
    return out, words


if __name__ == "__main__":
    for card in CARDS:
        for fmt in CARDS[card].get("formats", FORMATS):
            out, words = render(card, fmt)
            print(f"{os.path.relpath(out, ROOT)}  {words} words")
