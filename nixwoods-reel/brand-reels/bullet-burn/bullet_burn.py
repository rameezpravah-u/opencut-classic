"""NixWoods "Too warm to care": the NixLine bullet reel, after @nninecoffee_'s cold-brew bullet reel
(instagram.com/reel/DeuQ7gQtvsM, 15.4 s, silent).

The reference, frame by frame: one still product shot on a white set with viewfinder corners, a REC timecode and a
round badge. A bullet creeps at the cup in extreme slow motion while "FRAMES TO IMPACT" counts down 070 → 017
(0–6.6 s); a cut in closer, a "● chilling" timer counts up, the bullet frosts over: "THEN IT GOT / too close"; it
drops to the floor frozen: "It never stood / a chance"; "NNINE Cold Brew / Too chill to care".

Ours, owner's brief 21 Oct: the NixLine instead of the cup, and the bullet burns instead of freezing; "no compromise
with quality, it needs to be as I have shared". Three stills were generated (Higgsfield Nano Banana 2.1, 2k, about
6 credits, owner's choice after the free Hugging Face quota ran out): the white set with the real NixLine (referenced
on the owner's own clip nx04 and the product page photo), the bullet, and the burnt lump. Everything that moves is
done here: the creep, the countdown, the cut, the heat, sparks, smoke, the melt and the fall. The stills are AI, so
the post needs Instagram's "Made with AI" label (no on-screen label, as the owner chose for the heist reel). The heat
is a visual metaphor only: no line says the lamp gets hot.

    python3 brand-reels/bullet-burn/bullet_burn.py
"""
import os, subprocess, sys, wave

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "festive-ad-cuts"))
sys.path.insert(0, os.path.join(ROOT, "brand-reels", "made-well"))
from festive_cuts import A, FF, FPS, H, W, font, sstep  # noqa: E402
from made_well import encoder                            # noqa: E402

GEN = os.path.join(HERE, "gen")
OUT = os.path.join(HERE, "out")
NAME = "NW-CREATIVE-VID-20261021-nix-line-solid-wood-floor-lamp-bullet-burn-v1-AI"
SR = 48000
DUR = 15.4
CUT = 6.6                      # the cut in closer, as the reference
HEAT = (7.2, 9.2)              # the bullet heats from copper to white
MELT = (9.0, 9.8)              # it slumps and crumples
FALL = (9.8, 10.3)             # the lump drops to the floor
INK = (36, 30, 27)
RNG = np.random.default_rng(11)

SCALE, OFF = 0.76, (0.12, 0.02)        # the set is shown at 80% so the lamp sits above the text, as the cup does
Y_LINE = 0.43                          # bullet height: the lamp's middle
TIP0, TIP1, TIP2 = 0.20, 0.50, 0.53   # tip x: start, at the cut, where it stops in the lamp's glow
FLOOR = 0.672                          # where the lump lands, level with the lamp's foot
L = 170.0                              # bullet length in wide-shot px
ZOOM, ZC = 1.4, (0.45, 0.55)           # the closer framing after the cut: everything stays above the text


def base_frame():
    """the white set at SCALE, centred so the lamp sits where the reference's cup sits; the margins continue the
    wall and floor (replicated edges, softened)"""
    im = np.asarray(Image.open(os.path.join(GEN, "set.jpg")).convert("RGB"), np.float32) / 255
    h0, w0 = im.shape[:2]
    ch = round(w0 * H / W)
    y0 = (h0 - ch) // 2
    im = cv2.resize(im[y0:y0 + ch], (round(W * SCALE), round(H * SCALE)), interpolation=cv2.INTER_AREA)
    l, t = round(OFF[0] * W), round(OFF[1] * H)
    big = cv2.copyMakeBorder(im, t, H - t - im.shape[0], l, W - l - im.shape[1], cv2.BORDER_REPLICATE)
    soft = cv2.GaussianBlur(big, (0, 0), 25)
    m = np.zeros((H, W), np.float32)
    m[t:t + im.shape[0], l:l + im.shape[1]] = 1
    m = cv2.GaussianBlur(m, (0, 0), 12)[..., None]
    return big * m + soft * (1 - m)


def zoomed(img):
    cw, chh = W / ZOOM, H / ZOOM
    x0 = min(max(ZC[0] * W - cw / 2, 0), W - cw)
    y0 = min(max(ZC[1] * H - chh / 2, 0), H - chh)
    M = np.float32([[ZOOM, 0, -x0 * ZOOM], [0, ZOOM, -y0 * ZOOM]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC), (x0, y0, ZOOM)


def to_screen(px, py, cam):
    x0, y0, z = cam
    return (px - x0) * z, (py - y0) * z


def cutout(path, thresh=0.10, keep_largest=True):
    """an object shot on pure white → RGBA: alpha from the distance to white, holes filled, edge feathered"""
    rgb = np.asarray(Image.open(path).convert("RGB"), np.float32) / 255
    bgc = np.median(np.concatenate([rgb[:20].reshape(-1, 3), rgb[-20:].reshape(-1, 3)]), axis=0)
    dist = np.abs(rgb - bgc).max(2)
    m = dist > thresh
    m = ndimage.binary_closing(m, iterations=6)
    m = ndimage.binary_fill_holes(m)
    if keep_largest:
        lab, n = ndimage.label(m)
        if n > 1:
            sizes = ndimage.sum(m, lab, range(1, n + 1))
            m = lab == (1 + int(np.argmax(sizes)))
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return np.dstack([rgb, a])[y0:y1, x0:x1]


BLACKBODY = np.array([[0.62, 0.10, 0.03], [1.0, 0.40, 0.06], [1.0, 0.78, 0.40], [1.0, 0.97, 0.88]], np.float32)


def heat_tint(rgb, heat):
    """copper → dull red → orange → white-hot, keeping the photo's shading"""
    if heat <= 0:
        return rgb
    lum = rgb @ np.array([0.3, 0.55, 0.15], np.float32)
    k = np.clip(heat * 3, 0, 3)
    i = int(min(k, 2.999))
    col = BLACKBODY[i] + (BLACKBODY[min(i + 1, 3)] - BLACKBODY[i]) * (k - i)
    hot = np.clip(0.35 + 0.9 * lum, 0, 1.2)[..., None] * col
    w = np.interp(heat, [0, 0.3, 0.7, 1], [0, 0.55, 0.85, 0.95])
    return np.clip(rgb * (1 - w) + hot * w, 0, 1)


def place(dst, spr, cx, cy, alpha=1.0):
    """composite an RGBA float sprite centred at (cx, cy) onto dst in place"""
    h, w = spr.shape[:2]
    x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb:
        return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]
    a = s[..., 3:] * alpha
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - a) + s[..., :3] * a


def soft_blob(dst, cx, cy, rx, ry, color, alpha):
    """a soft coloured halo, normal blend (it has to read on a white set)"""
    pad = int(max(rx, ry) * 2.2)
    xa, ya, xb, yb = max(int(cx - pad), 0), max(int(cy - pad), 0), min(int(cx + pad), W), min(int(cy + pad), H)
    if xa >= xb or ya >= yb:
        return
    yy, xx = np.mgrid[ya:yb, xa:xb].astype(np.float32)
    g = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2))[..., None] * alpha
    dst[ya:yb, xa:xb] = dst[ya:yb, xa:xb] * (1 - g) + np.array(color, np.float32) * g


class Particles:
    def __init__(self):
        self.p = []

    def emit(self, n, x, y, kind, spread=1.0):
        for _ in range(n):
            if kind == "spark":
                a = np.pi + RNG.normal(0, 0.9) * spread
                v = RNG.uniform(250, 850)
                self.p.append([x, y, np.cos(a) * v, np.sin(a) * v - 120, RNG.uniform(0.25, 0.6), 0, kind, 0])
            elif kind == "ember":
                self.p.append([x + RNG.normal(0, 8), y, RNG.normal(0, 35), RNG.uniform(-140, -50),
                               RNG.uniform(0.7, 1.6), 0, kind, RNG.uniform(1.5, 3.2)])
            else:
                self.p.append([x + RNG.normal(0, 4), y, RNG.normal(6, 10), RNG.uniform(-110, -60),
                               RNG.uniform(1.6, 2.8), 0, kind, RNG.uniform(4, 7)])

    def step(self, dt):
        keep = []
        for q in self.p:
            q[5] += dt
            if q[5] >= q[4]:
                continue
            q[3] += (900 if q[6] == "spark" else -15) * dt
            q[0] += q[2] * dt
            q[1] += q[3] * dt
            if q[6] == "smoke":
                q[7] += 9 * dt
                q[2] += 25 * np.sin(q[5] * 3 + q[7]) * dt
            keep.append(q)
        self.p = keep

    def draw(self, cam):
        """smoke on its own layer (blurred later), sparks and embers on another"""
        smk = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hot = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ds, dh = ImageDraw.Draw(smk), ImageDraw.Draw(hot)
        z = cam[2]
        for x, y, vx, vy, life, age, kind, size in self.p:
            u = age / life
            sx, sy = to_screen(x, y, cam)
            if kind == "spark":
                ex, ey = to_screen(x - vx * 0.03, y - vy * 0.03, cam)
                dh.line([(ex, ey), (sx, sy)], fill=(255, int(150 - 70 * u), int(20 - 15 * u), int(255 * (1 - u * u))),
                        width=max(3, int(3 * z)))
            elif kind == "ember":
                r = size * z * (1 - 0.4 * u)
                dh.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(240, int(110 - 50 * u), 20, int(235 * (1 - u))))
            else:
                r = size * z
                ds.ellipse((sx - r, sy - r, sx + r, sy + r),
                           fill=(150, 145, 140, int(48 * np.sin(np.pi * min(u, 1)))))
        return smk, hot


def layer(fn):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay))
    return np.asarray(lay, np.float32) / 255


def over(base, lay, a=1.0):
    return base * (1 - lay[..., 3:] * a) + lay[..., :3] * lay[..., 3:] * a


LAB = font("Inter-600.ttf", 24)
BIG = font("Space_Grotesk-500.ttf", 112)
REG, BOLD = font("Inter-400.ttf", 52), font("Inter-600.ttf", 52)
SMALL = font("Inter-400.ttf", 30)
TY = 1478                      # the text block's top, under the lamp, inside the safe zone


def tracked(d, text, y, f, fill, gap=4):
    tw = sum(f.getlength(c) + gap for c in text) - gap
    x = (W - tw) / 2
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += f.getlength(c) + gap


def two(label, a, b):
    def f(d):
        tracked(d, label.upper(), TY, LAB, INK + (200,))
        w1, w2 = REG.getlength(a + " "), BOLD.getlength(b)
        x0 = (W - w1 - w2) / 2
        d.text((x0, TY + 38), a + " ", font=REG, fill=INK + (255,))
        d.text((x0 + w1, TY + 38), b, font=BOLD, fill=INK + (255,))
    return layer(f)


def countdown(num):
    def f(d):
        tracked(d, "FRAMES TO IMPACT", TY, LAB, INK + (200,))
        s = f"{num:03d}"
        d.text(((W - BIG.getlength(s)) / 2, TY + 28), s, font=BIG, fill=INK + (255,))
    return layer(f)


def badge():
    """the round brand badge top right, where the reference keeps its own"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    r, cx, cy = 50, W - 140, 236
    ImageDraw.Draw(lay).ellipse((cx - r, cy - r, cx + r, cy + r), fill=(49, 33, 26, 245))
    lg = Image.open(A("logo.png")).convert("RGBA")
    lg = lg.resize((66, round(66 * lg.height / lg.width)), Image.LANCZOS)
    ink = Image.new("RGBA", lg.size, (246, 239, 228, 255))
    ink.putalpha(lg.getchannel("A"))
    lay.alpha_composite(ink, (cx - lg.width // 2, cy - lg.height // 2))
    return np.asarray(lay, np.float32) / 255


def hud(t):
    """viewfinder corners, the REC timecode (wide) or the 'glowing' timer (after the cut), the site line"""
    g = font("Space_Grotesk-500.ttf", 24)

    def f(d):
        c, m, k = INK + (150,), 56, 44
        for x, y, sx, sy in ((m, 170, 1, 1), (W - m, 170, -1, 1), (m, H - 250, 1, -1), (W - m, H - 250, -1, -1)):
            d.line([(x, y), (x + sx * k, y)], fill=c, width=3)
            d.line([(x, y), (x, y + sy * k)], fill=c, width=3)
        if t < CUT:
            if int(t * 2) % 2 == 0:
                d.ellipse((92, 229, 106, 243), fill=(222, 50, 40, 255))
            d.text((116, 222), f"REC   00:{t + 1.55:05.2f}", font=g, fill=INK + (190,))
        else:
            d.ellipse((92, 229, 106, 243), fill=(240, 140, 30, 255))
            d.text((116, 222), f"glowing   {t - CUT + 0.04:05.2f}", font=g, fill=INK + (190,))
        if t < 12.9:                                          # the end line carries the site from there
            d.text(((W - g.getlength("nixwoods.com")) / 2, H - 330), "nixwoods.com", font=g, fill=INK + (150,))
    return layer(f)


def bullet_frame(spr0, heat, melt, z):
    """the bullet sprite at camera zoom z: heat-tinted, and crumpled from the nose back as it melts"""
    h0, w0 = spr0.shape[:2]
    s = (L * z) / w0
    spr = cv2.resize(spr0, (max(2, round(w0 * s)), max(2, round(h0 * s))), interpolation=cv2.INTER_AREA)
    spr = np.dstack([heat_tint(spr[..., :3], heat), spr[..., 3]])
    if melt > 0:
        h, w = spr.shape[:2]
        sx, sy = 1 - 0.45 * melt, 1 + 0.35 * melt
        nw, nh = max(2, round(w * sx)), max(2, round(h * sy))
        spr = cv2.resize(spr, (nw, nh), interpolation=cv2.INTER_AREA)
        yy, xx = np.mgrid[0:nh, 0:nw].astype(np.float32)
        droop = melt * nh * 0.35 * (xx / nw) ** 1.5              # the nose sags first
        wob = melt * 2.5 * np.sin(xx / 6.0 + yy / 9.0)
        spr = cv2.remap(spr, xx, yy - droop + wob, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        pad = int(nh * 0.4)
        spr = np.pad(spr, ((0, pad), (0, 0), (0, 0)))
    return spr


def main():
    os.makedirs(OUT, exist_ok=True)
    wavp = os.path.join(OUT, ".a.wav")
    audio(wavp)
    enc = encoder(wavp, os.path.join(OUT, f"{NAME}.mp4"), crf=17)
    wide = base_frame()
    close, cam_c = zoomed(wide)
    cam_w = (0.0, 0.0, 1.0)
    bullet = cutout(os.path.join(GEN, "bullet.jpg"), 0.10)
    lump = cutout(os.path.join(GEN, "lump.jpg"), 0.16)
    caps = [(CUT + 0.6, 9.5, two("Then it got", "too", "close")),
            (9.7, 12.8, two("It never stood", "a", "chance")),
            (13.0, DUR + 1, two("NixLine floor lamp", "Too warm", "to care"))]
    END = "solid teak   ·   ₹999   ·   nixwoods.com"
    price = layer(lambda d: d.text(((W - SMALL.getlength(END)) / 2, TY + 116), END, font=SMALL, fill=INK + (205,)))
    bdg = badge()
    parts = Particles()
    yb = Y_LINE * H
    lump_from = None
    keep, n, dt = {}, round(DUR * FPS), 1 / FPS
    for i in range(n):
        t = i * dt
        if t < CUT:
            x, cam = wide.copy(), cam_w
            tip = (TIP0 + (TIP1 - TIP0) * t / CUT) * W
        else:
            x, cam = close.copy(), cam_c
            tip = (TIP1 + (TIP2 - TIP1) * sstep((t - CUT) / (HEAT[0] + 0.8 - CUT))) * W
        z = cam[2]
        heat = 0.8 * float(np.clip((t - HEAT[0]) / (HEAT[1] - HEAT[0]), 0, 1))
        melt = float(np.clip((t - MELT[0]) / (MELT[1] - MELT[0]), 0, 1))
        cxw, cyw = tip - L / 2, yb                               # the bullet's centre, wide-shot px
        if t < FALL[0]:
            trail = 1 - min(1.0, heat * 2)
            if trail > 0:                                        # the vapour trail and shock lines, as the reference
                lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                dl = ImageDraw.Draw(lay)
                tx, ty = to_screen(tip - L, yb, cam)
                dl.line([(0, ty), (tx, ty)], fill=(255, 255, 255, int(235 * trail)), width=max(3, int(5 * z)))
                hx, hy = to_screen(tip, yb, cam)
                for sgn in (-1, 1):
                    dl.line([(hx, hy), (hx - 1400 * z, hy + sgn * 420 * z)], fill=INK + (int(38 * trail),), width=1)
                lay = lay.filter(ImageFilter.GaussianBlur(1.2))
                x = over(x, np.asarray(lay, np.float32) / 255)
            sx, sy = to_screen(cxw, cyw, cam)
            if heat > 0:
                soft_blob(x, sx, sy, (80 + 150 * heat) * z, (34 + 60 * heat) * z, (1.0, 0.52, 0.12), 0.75 * heat)
                soft_blob(x, sx, sy, (40 + 60 * heat) * z, (16 + 22 * heat) * z, (1.0, 0.85, 0.5), 0.55 * heat)
            spr = bullet_frame(bullet, heat, melt, z)
            place(x, spr, sx, sy + spr.shape[0] * 0.13 * (melt > 0))
            if heat > 0.25:
                parts.emit(int(1 + 7 * heat), tip - L * 0.15, yb + RNG.normal(0, 5), "spark", 0.8)
            if heat > 0.35:
                parts.emit(2, tip - L * RNG.uniform(0.2, 0.7), yb - 8, "smoke")
            if melt > 0:
                parts.emit(2, tip - L * 0.3, yb + 8, "ember")
            lump_from = (cxw + L * 0.12, cyw)
        else:
            fu = float(np.clip((t - FALL[0]) / (FALL[1] - FALL[0]), 0, 1))
            lx, ly0 = lump_from
            ly = ly0 + (FLOOR * H - ly0) * fu ** 2
            glow = float(np.clip(1 - (t - FALL[1]) / 3.5, 0, 1))
            sx, sy = to_screen(lx, ly, cam)
            lw = 82 * z
            s = lw / lump.shape[1]
            spr = cv2.resize(lump, (round(lump.shape[1] * s), round(lump.shape[0] * s)), interpolation=cv2.INTER_AREA)
            spr = np.dstack([heat_tint(spr[..., :3], 0.55 * glow * (1 - 0.3 * fu)), spr[..., 3]])
            if fu >= 1:                                          # a contact shadow once it lands
                soft_blob(x, sx, sy + spr.shape[0] * 0.42, lw * 0.55, lw * 0.09, (0.55, 0.53, 0.52), 0.55)
            if glow > 0:
                soft_blob(x, sx, sy, lw * 0.9, lw * 0.45, (1.0, 0.5, 0.12), 0.3 * glow)
            place(x, spr, sx, sy)
            if fu >= 1 and t - FALL[1] < dt * 1.5:
                parts.emit(26, lx, FLOOR * H + 10, "spark", 1.6)
            if fu >= 1 and glow > 0.05:
                parts.emit(1, lx + RNG.normal(0, 6), FLOOR * H - 6, "smoke")
                if glow > 0.4:
                    parts.emit(1, lx, FLOOR * H - 4, "ember")
        parts.step(dt)
        smk, hot = parts.draw(cam)
        x = over(x, np.asarray(smk.filter(ImageFilter.GaussianBlur(int(5 * z))), np.float32) / 255)
        x = over(x, np.asarray(hot.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255, 0.6)
        x = over(x, np.asarray(hot.filter(ImageFilter.GaussianBlur(0.5)), np.float32) / 255)
        if t < CUT:
            x = over(x, countdown(int(round(88 - (88 - 17) * t / CUT))))
        if CUT <= t < CUT + 0.1:
            x = np.clip(x + 0.4 * (1 - (t - CUT) / 0.1), 0, 1)
        for a0, b0, c in caps:
            if a0 <= t < b0:
                x = over(x, c, sstep((t - a0) / 0.3))
        if t >= 13.2:
            x = over(x, price, sstep((t - 13.2) / 0.3))
        x = over(x, hud(t))
        x = over(x, bdg)
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(px.tobytes())
        if i in (15, 120, 200, 240, 270, 285, 300, 330, 420):
            keep[i] = px
    enc.stdin.close()
    enc.wait()
    os.remove(wavp)
    ims = [Image.fromarray(keep[k]).resize((240, 427)) for k in sorted(keep)]
    sheet = Image.new("RGB", (240 * len(ims), 427))
    for k, im in enumerate(ims):
        sheet.paste(im, (240 * k, 0))
    sheet.save(os.path.join(OUT, f"{NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep[120]).save(os.path.join(OUT, f"{NAME}-cover.jpg"), quality=90)
    print("done", n, "frames")


def audio(path):
    """our own sound (the reference is silent): a low drone under the countdown, a whoosh on the cut, a sizzle and
    crackle as the bullet burns, a soft thud when it lands, music1 under the end line"""
    n = int(DUR * SR)
    t = np.arange(n) / SR
    m = np.zeros((n, 2), np.float32)
    rng = np.random.default_rng(3)

    def load(p, gain_db):
        raw = subprocess.run([FF, "-v", "error", "-i", p, "-t", f"{DUR:.3f}", "-ac", "2", "-ar", str(SR), "-f",
                              "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32).reshape(-1, 2)[:n]
        out = np.zeros((n, 2), np.float32)
        out[:len(a)] = a / (np.sqrt(np.mean(a ** 2)) + 1e-9) * 10 ** (gain_db / 20)
        return out

    drone = (np.sin(2 * np.pi * 55 * t) * 0.6 + np.sin(2 * np.pi * 82.5 * t) * 0.3) * 10 ** (-30 / 20)
    m += (drone * np.clip(t / 1.0, 0, 1) * np.clip((CUT + 0.2 - t) / 0.2, 0, 1))[:, None]
    tick = np.zeros(n, np.float32)                        # a quiet tick every 0.5 s of the countdown
    for k in np.arange(0.25, CUT, 0.5):
        i0 = int(k * SR)
        L = int(0.012 * SR)
        tick[i0:i0 + L] += np.sin(2 * np.pi * 2400 * np.arange(L) / SR) * np.exp(-np.arange(L) / (L / 5)) * 0.12
    m += tick[:, None]
    wh = load(os.path.join(ROOT, "brand-reels", "audio", "sfx-whoosh.mp3"), -22)
    i0 = int((CUT - 0.35) * SR)
    m[i0:] += wh[:n - i0]
    noise = rng.standard_normal(n).astype(np.float32)
    hiss = noise - np.convolve(noise, np.ones(8) / 8, "same")                 # a high, hissing sizzle
    env = np.clip((t - HEAT[0]) / 1.5, 0, 1) * np.clip((FALL[1] + 1.8 - t) / 1.5, 0, 1)
    crackle = (rng.random(n) < 0.0009 * env).astype(np.float32) * rng.uniform(0.3, 0.9, n)
    crackle = np.convolve(crackle, np.exp(-np.arange(200) / 30), "same")
    m += ((hiss * 0.05 + crackle * 0.25) * env)[:, None]
    i0 = int(FALL[1] * SR)
    L = int(0.25 * SR)
    m[i0:i0 + L] += (np.sin(2 * np.pi * 70 * np.arange(L) / SR) * np.exp(-np.arange(L) / (L / 6)) * 0.5)[:, None]
    mus = load(os.path.join(ROOT, "brand-reels", "audio", "music1-aesthetic.mp3"), -20)
    m += mus * (np.clip((t - 12.4) / 1.0, 0, 1) * np.clip((DUR - t) / 0.6, 0, 1))[:, None]
    m *= np.clip(t / 0.05, 0, 1)[:, None]
    m *= min(1.0, 0.89 / (np.abs(m).max() + 1e-9))
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(m, -1, 1) * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    main()
