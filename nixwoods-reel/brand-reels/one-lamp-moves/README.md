# NixWoods "one lamp, every move": the Rubik's Cube lamp

**The idea:** @d2_shots' cow reel (instagram.com/reel/DdhF_atB_JM, 7.04 s, 1.38M views) holds one subject centre
frame while the camera snaps around it. It makes sixteen fast moves, each eased over 0.1–0.25 s and followed by a
near-still hold:
- an extreme close-up pulling back, and a pull to wide;
- push-ins and a high angle;
- a low angle, a zoom and a dutch roll;
- a whip pan, and a pass behind a foreground post;
- a final settle.

The owner asked on 16 Oct: "Choose one product where you can do all of what is done in the below reel."

**Product:** the Rubik's Cube lamp. It has the most real, faceless video on Drive of any product (77 clips in the 16
Oct tags), from many angles and in all three colours. D-017: "Rubik's Cube" stays.

**Facts (`PRODUCT-FACTS.md`):**
- Candy Glass ₹2,999 · Ocean ₹3,299 · Bubble ₹3,199.
- Sheesham base; plug-in.
- Turn the block for red, green or amber. That holds for Candy and Ocean only, not Bubble.
- No dimmer, no remote and no app.

**Footage:** every clip is real and shows the lamp on its own sheesham base.
- **Shoot clip** (`rubik-reels/src/14-1.mp4`, 5 Aug): green, red, amber, warm white, then a hand turning the block.
- **Owner phone clips** (`festive-ad-cuts/src` NW-RAW 92973dce and 2e5660bf): the camera trucks past the lamp for
  real. They are tracked on the warm glass, so the lamp stays centred.
- **IMG_6986** (Drive, workshop): a low close-up with the NX badge, and a wooden post passing in front.
- **Left out:** the workshop prototype clips on a white LED slab. They show a cool light the product does not have.

**Moves:**
- Digital (crop, scale, roll) on that footage, with a 180° shutter blur from seven subsamples per frame.
- The moves land on the reference's measured move frames, so its audio fits through "Use audio".

| Time | Move | Shot |
|---|---|---|
| 0.00–1.54 | ECU pull-back, pull to wide, push in | green |
| 1.54–2.17 | Tilt cut, then a push | the camera trucking past for real |
| 2.17–3.46 | Spin into a low angle, push, roll | IMG_6986 close-up, NX badge |
| 3.46–3.88 | Dutch roll | red face |
| 3.88–4.38 | Whip pan | amber |
| 4.38–4.88 | Push, then the post passes in front | IMG_6986 |
| 4.88–5.63 | Whip, push | a hand turns it |
| 5.63–6.25 | Whip | the second trucking clip |
| 6.25–7.04 | Pull back, settle | warm white, wide |

**Two cuts:**
- `…-in-app-audio.mp4`: silent. Post it and tap "Use audio" on the reference.
- `…-music4.mp4`: our music4-genz track from its drop, with a soft whoosh on each move. It can run as an ad.

The reference's audio is never committed; a preview with it stays in the session scratchpad. The name and price go in
the caption, because the reference has no text and its holds are too short to read.

```bash
python3 brand-reels/one-lamp-moves/one_lamp_moves.py
```
