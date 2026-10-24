"""The film that plays on the billboard: our own lamp footage (real, no AI) on the left, a black type panel on the right,
as the Westwing film at Piccadilly does. One continuous 21.2 s timeline at 30 fps; each city shot shows whatever is
playing at that moment, so the screen keeps running across the cuts like a real screen.

    from screen_film import ScreenFilm      # piccadilly_billboard.py maps its frames onto the green screen
    python3 brand-reels/piccadilly-billboard/screen_film.py --sheet out.jpg   # check it alone
"""
import argparse, os, subprocess, sys

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
from festive_cuts import FF, FPS, font, sstep  # noqa: E402

SW, SH = 1560, 600                       # the screen's own frame, about 2.6:1 like the curved Piccadilly screen
FILM_W = 968                             # the film area; the rest is the black panel
DUR = 21.2
R = lambda p: os.path.join(ROOT, p)
# (film start, film end, source, source in-point, crop centre 0..1 down the 9:16 frame). Each beat answers the
# reference's: a warm round light, the product lit, details, hands at work, a light changing colour.
CUTS = [
    (0.0, 2.6, "brand-reels/lamps-under-3000/src/drive-edison-dimmer-demo-wa.mp4", 12.6, 0.47),  # bulb comes up
    (2.6, 4.6, "floor-reels/src/nx00-hero.mp4", 3.0, 0.45),                 # the NixLine's light line, close
    (4.6, 6.4, "floor-reels/src/nx04-7930.mp4", 0.6, 0.55),                 # a row of bars, one lit
    (6.4, 9.6, "rubik-reels/src/14-1.mp4", 8.5, 0.62),                      # the cube in amber
    (9.6, 12.0, "brand-reels/luma-styled/src/luma-styling-20260331.mov", 8.0, 0.62),  # a hand sets down the Luma
    (12.0, 14.0, "brand-reels/lamps-under-3000/src/drive-edison-dimmer-demo-wa.mp4", 8.0, 0.62),  # hand on the dimmer
    (14.0, 17.0, "rubik-reels/src/14-1.mp4", 3.4, 0.62),                    # red, then amber (two colours; not
                                                                             # green, which reads as chroma here)
    (17.0, 19.0, "brand-reels/lamps-under-3000/src/drive-aurora-v3-fullshoot-hook.mp4", 3.0, 0.22),  # wall wash
    (19.0, 21.2, "brand-reels/luma-styled/src/luma-styling-20260331.mov", 19.4, 0.55),  # the Luma lit
]
WARM = np.array([1.08, 1.0, 0.86], np.float32)
WHITE = (238, 232, 222)


def load_cut(src, t_in, dur, cy):
    """the source frames for one cut, cropped to the film area's landscape shape around crop centre cy"""
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", R(src), "-t", f"{dur + 0.1:.3f}", "-vf",
                          f"fps={FPS},scale=1080:-2", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    h = len(raw) // (1080 * 3)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", R(src)], capture_output=True, text=True).stdout.split(",")
    fh = round(1080 * int(probe[1]) / int(probe[0]))
    fr = np.frombuffer(raw, np.uint8)[:(len(raw) // (1080 * fh * 3)) * 1080 * fh * 3].reshape(-1, fh, 1080, 3)
    ch = round(1080 * SH / FILM_W)
    y0 = int(min(max(cy * fh - ch / 2, 0), fh - ch))
    out = []
    for f in fr:
        im = Image.fromarray(f[y0:y0 + ch]).resize((FILM_W, SH), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255
        out.append(np.clip(a * WARM, 0, 1))
    n = round(dur * FPS)
    return [out[min(i, len(out) - 1)] for i in range(n)]


def panel(phase):
    """the black type panel with thin white rules, three cells, as the reference's (our words, MOTION.md fonts)"""
    w = SW - FILM_W
    im = Image.new("RGB", (w, SH), (6, 5, 5))
    d = ImageDraw.Draw(im)
    d.line((0, 0, 0, SH), fill=WHITE, width=3)                 # the divider between film and panel
    for y in (SH // 3, 2 * SH // 3):
        d.line((40, y, w - 30, y), fill=WHITE, width=2)
    top, bottom = [("Light, made by hand.", "nixwoods.com"), ("nixwoods.com", "The Lighting Collection")][phase]
    f_top = font("Fraunces-500-i.ttf", 46) if phase == 0 else font("Fraunces-600.ttf", 40)
    f_mid = font("Inter-600.ttf", 25)
    f_bot = font("Fraunces-600.ttf", 40)

    def centred(text, f, cy):
        bb = d.textbbox((0, 0), text, font=f)
        d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]), text, font=f, fill=WHITE)
    centred(top, f_top, SH / 6)
    centred("NIXWOODS  |  SOLID WOOD LIGHTING", f_mid, SH / 2)
    centred(bottom, f_bot, 5 * SH / 6)
    return np.asarray(im, np.float32) / 255


class ScreenFilm:
    def __init__(self):
        self.frames = []
        for a, b, src, t_in, cy in CUTS:
            self.frames += load_cut(src, t_in, b - a, cy)
        self.panels = [panel(0), panel(1)]

    def at(self, t):
        """the screen frame at time t, float RGB (SH, SW, 3)"""
        k = min(int(round(t * FPS)), len(self.frames) - 1)
        out = np.zeros((SH, SW, 3), np.float32)
        out[:, :FILM_W] = self.frames[k]
        swap = sstep((t - 8.0) / 0.4)                          # the panel changes its lines once, as the reference
        out[:, FILM_W:] = self.panels[0] * (1 - swap) + self.panels[1] * swap
        return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    a = ap.parse_args()
    sf = ScreenFilm()
    ts = np.arange(0.3, DUR, 0.7)
    cells = [Image.fromarray((sf.at(t) * 255).astype(np.uint8)).resize((390, 150)) for t in ts]
    sheet = Image.new("RGB", (390 * 5, 150 * ((len(cells) + 4) // 5)))
    for i, c in enumerate(cells):
        sheet.paste(c, ((i % 5) * 390, (i // 5) * 150))
    sheet.save(a.sheet, quality=88)
    print(len(sf.frames), "frames")
