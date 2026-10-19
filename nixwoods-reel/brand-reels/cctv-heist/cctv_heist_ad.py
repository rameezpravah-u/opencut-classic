"""The Meta ad cut of "CAM 02" (cctv_heist.py), to the ads engine's rules (system/presets.json → engine):
- 27.5 s: ads land best at 25–30 s (ad_length);
- specs and price on frame 1, written as a CCTV metadata line under the clock: NIXLINE · SOLID TEAK · 3000K · ₹999;
- the price again in a caption before 10 s;
- a 6 s proof beat of real footage after the skit: the owner's own NixLine workshop clips (floor-reels/src), so the
  product as bought is shown for real, not only as AI.

Same AI clips (gen2/), grade, HUD, captions, hero still and end card as the organic cut; no on-screen AI label (owner,
19 Oct), so tick Meta's AI disclosure on the ad.

    python3 brand-reels/cctv-heist/cctv_heist_ad.py
"""
import os, subprocess, sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cctv_heist as C                                   # noqa: E402
from cctv_heist import FF, FPS, H, W, sstep, encoder     # noqa: E402
from festive_cuts import grade_shot                      # noqa: E402

C.SHOTS = [("A", 0.2, 4.8), ("B", 0.4, 4.6), ("C", 1.1, 3.9), ("D", 0.0, 2.8)]
C.CUTS = np.cumsum([0] + [s[2] for s in C.SHOTS])        # 0, 4.8, 9.4, 13.3, 16.1
C.SWITCH = float(C.CUTS[2])
PROOF = [("nx05-7920.mp4", 3.0, "Solid Indian teak. No MDF."),          # the grain, in a hand
         ("nx03-7926.mp4", 0.2, "Made by hand in Uttar Pradesh."),      # rows of finished bars
         ("nx04-7930.mp4", 1.0, "Warm 3000K. Plug in and place.")]      # one standing, lit
PROOF_S = 2.0
END = 5.4
C.DUR = float(C.CUTS[-1] + PROOF_S * len(PROOF) + END)   # 27.5 s
C.NAME = "NW-CREATIVE-VID-20261019-nix-line-solid-wood-floor-lamp-cctv-heist-ad-27s-v1-AI"
SPEC = "NIXLINE · SOLID TEAK · 3000K · ₹999"
CAPS = [(0.25, 3.0, "CAM 02 caught this at 2:47 AM"),
        (5.4, C.CUTS[2] - 0.1, "Cash box open. Tools on the bench."),
        (C.SWITCH + 0.4, C.CUTS[3] - 0.1, "He skipped the cash."),
        (C.CUTS[3] + 0.15, C.CUTS[4] - 0.05, "Took the ₹999 lamp.")]
SRC = os.path.join(C.ROOT, "floor-reels", "src")


def real_clip(name, t_in):
    raw = subprocess.run([FF, "-v", "error", "-ss", f"{t_in:.3f}", "-i", os.path.join(SRC, name), "-t",
                          f"{PROOF_S:.3f}", "-vf", "fps=30,scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    n = round(PROOF_S * FPS)
    return grade_shot([fr[min(i, len(fr) - 1)] for i in range(n)], keep=0.55, target=0.30)


def main():
    os.makedirs(C.OUT, exist_ok=True)
    wavp = os.path.join(C.OUT, ".ad.wav")
    C.audio(wavp)
    enc = encoder(wavp, os.path.join(C.OUT, f"{C.NAME}.mp4"), crf=23)
    caps = [(a, b, C.caption(s)) for a, b, s in CAPS]
    card = C.end_card()
    keep, i = {}, 0

    def emit(x, key=None):
        nonlocal i
        t = i / FPS
        for a, b, c in caps:
            if a <= t < b:
                x = C.over(x, c, sstep((t - a) / 0.12))
        px = (np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)
        enc.stdin.write(px.tobytes())
        if key:
            keep[key] = px
        i += 1

    for k, (name, t_in, secs) in enumerate(C.SHOTS):
        for j, f in enumerate(C.clip(name, t_in, secs)):
            x = C.cctv(f, i)
            if j < 3 and k > 0:
                x = C.tear(x, 1 - j / 3)
            if name == "C" and j < 8:
                x = np.clip(x + (1 - j / 8) * 0.35 * np.array([1.0, 0.8, 0.55], np.float32), 0, 1)
            x = C.over(x, C.hud(i / FPS, (i // 15) % 2 == 0, SPEC))
            emit(x, ("frame1" if i == 0 else name if j == round(secs * FPS) // 2 else None))
    for k, (name, t_in, cap) in enumerate(PROOF):
        t0 = i / FPS
        caps.append((t0 + 0.1, t0 + PROOF_S - 0.05, C.caption(cap)))
        for j, f in enumerate(real_clip(name, t_in)):
            x = f.astype(np.float32) / 255
            if j < 2 and k == 0:
                x = np.clip(x + 0.5 * (1 - j / 2), 0, 1)                 # the CCTV feed cuts to the real lamp
            emit(x, f"proof{k}" if j == 30 else None)
    for j, x in enumerate(C.real_frames(round(END * FPS))):
        x = C.over(x, card, sstep((j / FPS - 0.25) / 0.4))
        emit(x, "end" if j == round(END * FPS) - 10 else None)
    enc.stdin.close()
    enc.wait()
    os.remove(wavp)
    order = ["frame1", "A", "B", "C", "D", "proof0", "proof1", "proof2", "end"]
    ims = [Image.fromarray(keep[k]).resize((240, 427)) for k in order]
    sheet = Image.new("RGB", (240 * len(ims), 427))
    for k, im in enumerate(ims):
        sheet.paste(im, (240 * k, 0))
    sheet.save(os.path.join(C.OUT, f"{C.NAME}-sheet.jpg"), quality=86)
    Image.fromarray(keep["frame1"]).save(os.path.join(C.OUT, f"{C.NAME}-cover.jpg"), quality=90)
    print("done", i, "frames", f"{C.DUR:.2f}s")


if __name__ == "__main__":
    main()
