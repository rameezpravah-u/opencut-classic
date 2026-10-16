"""Cut-out masks for the effects lookbook, made once with OpenCV GrabCut from a box around each lamp on the clean
5 Aug shoot photos, then saved as 8-bit PNGs (full photo size) in masks/. Run once; the reel script reads the PNGs.

    python3 brand-reels/effects-lookbook/make_masks.py
"""
import os

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SHOOT = os.path.join(os.path.dirname(os.path.dirname(HERE)), "drive-pull", "shoot-20260805")
# photo tag: the box around the lamp (x0, y0, x1, y1 in 3648 x 5472 pixels)
BOXES = {
    "AC4I9882": (880, 900, 3150, 4830),     # Sculpted Glow: frame, rope and base
    "AC4I9815": (2620, 2820, 3140, 4900),   # NixLine floor lamp: the bar and its block
    "AC4I9776": (1330, 1700, 1780, 4930),   # Minimalist floor lamp: the rod and its round base
}
# the wall's colour (Lab, OpenCV scale) where it shows through or beside the lamp, sampled outside the box
WALL = {"AC4I9882": None}
BASE_FROM = {"AC4I9882": 4080}              # from this row down, the plain box cut (the plinth) is used
S = 0.25                                    # GrabCut at quarter size, then the mask is scaled up and feathered


def main():
    os.makedirs(os.path.join(HERE, "masks"), exist_ok=True)
    f = [x for x in os.listdir(SHOOT) if "AC4I9882" in x][0]
    lab = cv2.cvtColor(cv2.imread(os.path.join(SHOOT, f)), cv2.COLOR_BGR2LAB)
    WALL["AC4I9882"] = tuple(np.median(lab[1000:2600, 200:700].reshape(-1, 3), axis=0))
    for tag, (x0, y0, x1, y1) in BOXES.items():
        f = [x for x in os.listdir(SHOOT) if tag in x][0]
        img = cv2.imread(os.path.join(SHOOT, f))
        small = cv2.resize(img, None, fx=S, fy=S, interpolation=cv2.INTER_AREA)
        m = np.zeros(small.shape[:2], np.uint8)
        rect = (int(x0 * S), int(y0 * S), int((x1 - x0) * S), int((y1 - y0) * S))
        bg, fg = np.zeros((1, 65), np.float64), np.zeros((1, 65), np.float64)
        m[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]] = cv2.GC_PR_FGD
        lum = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        m[(m == cv2.GC_PR_FGD) & (lum > 235)] = cv2.GC_FGD                # the lit LED is always the lamp
        if tag in WALL:                                                     # the wall seen through or beside it
            lab = cv2.cvtColor(small, cv2.COLOR_BGR2LAB).astype(np.float32)
            ref = np.array(WALL[tag], np.float32)
            d = np.linalg.norm((lab - ref)[..., 1:], axis=2)                # colour only, not brightness
            m[(m == cv2.GC_PR_FGD) & (d < 9) & (lum < 200)] = cv2.GC_BGD
        plain = np.zeros(small.shape[:2], np.uint8)
        cv2.grabCut(small, plain, rect, np.zeros((1, 65)), np.zeros((1, 65)), 8, cv2.GC_INIT_WITH_RECT)
        cv2.grabCut(small, m, None, bg, fg, 8, cv2.GC_INIT_WITH_MASK)
        a = np.where((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
        if tag in BASE_FROM:                                        # below the frame there is no wall to confuse it
            y = int(BASE_FROM[tag] * S)
            a[y:] = np.where((plain[y:] == cv2.GC_FGD) | (plain[y:] == cv2.GC_PR_FGD), 255, 0)
        a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        n, lab, st, _ = cv2.connectedComponentsWithStats(a)
        if n > 1:                                                   # keep the biggest piece only
            k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
            a = np.where(lab == k, 255, 0).astype(np.uint8)
        a = cv2.resize(a, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_LINEAR)
        a = cv2.GaussianBlur(a, (0, 0), 3)
        cv2.imwrite(os.path.join(HERE, "masks", f"{tag}.png"), a)
        print(tag, "fg share", round(float((a > 127).mean()), 4))


if __name__ == "__main__":
    main()
