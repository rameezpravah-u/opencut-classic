"""How cut/*.png were made (24 Oct). Run once; the reel reads the PNGs, not this script.

Free and local: rembg 2.0.67 (MIT) with its isnet-general-use model, in a throwaway venv so nothing is added to the
repo's requirements:

    python3 -m venv /tmp/rembg && /tmp/rembg/bin/pip install "rembg==2.0.67" onnxruntime pillow opencv-python scipy
    SSL_CERT_FILE=/root/.ccr/ca-bundle.crt /tmp/rembg/bin/python make_cutouts.py <src dir>

<src dir> holds the inputs:
- nixline-set.jpg: brand-reels/bullet-burn/gen/set.jpg (AI, on white);
- luma.jpg: the Luma Pillar page photo 16b3b563-… (cdn.shopify.com, ?width=1200);
- cube-amber.jpg, cube-red.jpg: the Rubik's Cube page photos AC4I9838 (Candy Glass) and AC4I9835 (?width=1200).
"""
import os, sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
SESS = new_session("isnet-general-use")


def largest(m):
    lab, n = ndi.label(m)
    if n < 2:
        return m
    return lab == 1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1))))


def save(rgb, a, name, h):
    out = np.dstack([rgb, (np.clip(a, 0, 1) * 255).astype(np.uint8)])
    ys, xs = np.nonzero(out[..., 3] > 10)
    im = Image.fromarray(out).crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    if im.height > h:
        im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    im.save(os.path.join(HERE, "cut", name), optimize=True)


def matte(path):
    rgb = np.asarray(Image.open(path).convert("RGB"))
    return rgb, np.asarray(remove(Image.fromarray(rgb), session=SESS))[..., 3].astype(np.float32) / 255


def main(src):
    os.makedirs(os.path.join(HERE, "cut"), exist_ok=True)
    # NixLine: the white lit strip reads as background to the model, so the holes are filled back in
    rgb, a = matte(os.path.join(src, "nixline-set.jpg"))
    m = largest(a > 0.16)
    filled = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=4))
    a = np.where(filled & ~m, 1.0, a * ndi.binary_dilation(m, iterations=2))
    save(rgb, a, "nixline.png", 1300)
    # Luma: clean on the model alone; the bowl beside it is dropped
    rgb, a = matte(os.path.join(src, "luma.jpg"))
    save(rgb, a * ndi.binary_dilation(largest(a > 0.16), iterations=2), "luma-pillar.png", 900)
    # the cube photos have a vase on the right: keep the cube only
    rgb, a = matte(os.path.join(src, "cube-amber.jpg"))
    m = a > 0.16
    m[:, 620:] = False
    m = ndi.binary_fill_holes(ndi.binary_closing(largest(m), iterations=3))
    save(rgb, a * m, "rubiks-cube-candy-amber.png", 700)
    # the red photo's sheesham base is too dark for the model: GrabCut, seeded with the model's cube and the base
    img = cv2.imread(os.path.join(src, "cube-red.jpg"))
    _, rb = matte(os.path.join(src, "cube-red.jpg"))
    gm = np.full(img.shape[:2], cv2.GC_BGD, np.uint8)
    gm[590:1125, 105:615] = cv2.GC_PR_BGD
    gm[978:1105, 118:600] = cv2.GC_PR_FGD
    gm[rb > 0.5] = cv2.GC_FGD
    gm[1000:1090, 140:580] = cv2.GC_FGD
    gm[:, 620:] = cv2.GC_BGD
    cv2.grabCut(img, gm, None, np.zeros((1, 65)), np.zeros((1, 65)), 6, cv2.GC_INIT_WITH_MASK)
    m = (gm == cv2.GC_FGD) | (gm == cv2.GC_PR_FGD)
    m[:, 620:] = False
    m = ndi.binary_fill_holes(ndi.binary_opening(largest(m), iterations=2))
    a = np.maximum(cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2), rb * m)
    e = cv2.erode((a > 0.5).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32)
    save(img[..., ::-1], np.minimum(a, cv2.GaussianBlur(e, (0, 0), 1.3)), "rubiks-cube-candy-red.png", 700)


if __name__ == "__main__":
    main(sys.argv[1])
