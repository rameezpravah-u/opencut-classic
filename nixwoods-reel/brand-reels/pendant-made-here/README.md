# Double Arm Teak Pendant: "Made here. Lives here."

Product: Double Arm Teak Pendant Light (Shopify handle `double-arm-teak-pendant-light-sculptural-led`),
₹9,999 on the store on 11 Oct 2026. The reel is 9:16, 30 fps and 10.03 s long, with music6-corners from its
first beat, cut on the beat.

From the owner's upload of seven clips on 11 Oct, it uses the three that are real footage of this product:
- `src/IMG_2602-sdr.mp4`: the pendant lit in the workshop, at 60 fps (played at half speed);
- `src/workshop-frame-fitting.mp4`: the teak frame and its brass joint;
- `src/IMG_7292-sdr.mp4`: the pendant over a dining table, from a 4K60 source.

The iPhone HLG clips were tone-mapped to SDR (zscale linear, then hable, then bt709). The original .mov files are not in the repo.
Not used:
- the two AI clips ("Where stories begin", a different product; and a poster with burned-in text);
- the teak plank pendant, a different product;
- a 720x544 clip, too low to upscale;
- IMG_7292 after 2.1 s, where people walk in and no on-camera release is signed.

| Time | Shot | Text |
|---|---|---|
| 0–1.67 s | The loop's knot, workshop, half speed | Made here. |
| 1.67–2.51 s | The teak frame's brass joint, by hand | |
| 2.51–4.18 s | Along the loop to the frame's end, half speed | |
| 4.18–6.69 s | The dining room, 12% push | Lives here. |
| 6.69–10.03 s | End card | Double Arm Teak Pendant. ₹9,999 · Teak · Curved LED · nixwoods.com |

The MOTION.md montage grade warms the LED, which reads cool white in the raw footage. Text is placed where the lit loop never
goes during that shot. Nothing is generated, so no AI label is needed.

    python3 brand-reels/pendant-made-here/pendant_made_here.py
