"""Night grade for real daylight phone footage, after the look of @faisal_saleh_photography's
DePramhoNWl: everything away from the LED line drops into deep teal dark, the background defocuses,
the light blooms amber, grain and vignette on top. Pure grading of real frames: nothing is generated."""
import numpy as np
from PIL import Image, ImageFilter

W, H = 1080, 1920
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIGN = np.clip(1.15 - 0.55 * np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 1.7, 0.45, 1)[..., None]
TEAL = np.array([0.10, 0.24, 0.28], np.float32)        # shadow tint
AMBER = np.array([1.00, 0.70, 0.36], np.float32)       # highlight tint


def grade(img, rng, reach=0.11, floor=0.12, defocus=14, thr=0.78):
    """img: PIL RGB 1080x1920. reach: how far the light's pool spreads (fraction of width)."""
    a = np.asarray(img).astype(np.float32) / 255
    L = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    hot = np.clip((L - thr) / max(0.99 - thr, 0.02), 0, 1)                              # the LED line itself
    pool = np.asarray(Image.fromarray((hot * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(W * reach))).astype(np.float32) / 255
    pool = np.clip(pool * 3.2, 0, 1)                                    # light falloff around the line
    near = np.clip(pool * 1.6, 0, 1)[..., None]
    blurred = np.asarray(img.filter(ImageFilter.GaussianBlur(defocus))).astype(np.float32) / 255
    a = near * a + (1 - near) * blurred                                 # far from the light = out of focus
    lift = (floor + (1 - floor) * pool)[..., None]                      # dark room, lit only near the line
    a = a * lift
    lum = (a @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    sh = np.clip(1 - lum * 3.0, 0, 1)                                   # split-tone: teal shadows, amber highs
    a = a * (1 - 0.6 * sh) + TEAL * 0.75 * sh * (lum * 3 + 0.35)
    hi = np.clip((lum - 0.35) / 0.5, 0, 1)
    a = a * (1 - 0.35 * hi) + a * AMBER * 0.35 * hi * 1.35
    glow = np.asarray(Image.fromarray((np.clip(hot, 0, 1)[..., None] * AMBER * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(28))).astype(np.float32) / 255
    a = a + glow * 0.55                                                 # bloom
    a = np.clip(a, 0, 1) ** 1.08 * VIGN
    a = a + rng.normal(0, 0.018, (H, W, 1))                             # grain
    return Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
