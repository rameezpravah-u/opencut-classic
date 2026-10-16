# NixWoods "9 ways to look at a lamp": an effects lookbook

**The idea:** @tenfoldmarc's "17 video effects Claude can create" (instagram.com/reel/Def_oOUzJeS) lists its effects
on a talking head. The owner asked on 16 Oct for a 15–20 s reel trying several of them on our work: "don't get stuck
on one product or one type. Go crazy."

**Material:** nine effects, each on a different product and a different kind of material. All of it is real photos
and footage built in code, with no generated frames.

**Two cuts:**
- `….mp4`: the clean cut, to post.
- `…-tagged.mp4`: the same reel with a small "01 / 09 · orbit" tag on each section, for choosing which effects to use
  in future reels.

| Time | Effect | Product | Material |
|---|---|---|---|
| 0.00 | Orbit: six lamps' photo cards circle the lamp in 3D, passing behind and in front of it. They speed up on the drop. | Sculpted Glow, ₹9,999 | Shoot photo AC4I9882, cut out (GrabCut) |
| 3.15 | Cover story: a magazine cover, with the lamp standing in front of its own "NIXLINE" masthead. | NixLine floor lamp, ₹999 | Shoot photo AC4I9815, cut out |
| 4.87 | Paper cut: "HAND / MADE" in ransom-note scraps, one a half-beat, then "in Uttar Pradesh". | (the workshop) | CNC router clip IMG_7698 |
| 6.58 | Doodle boil: hand-drawn stars, a heart, a ring, an arrow and "₹1,599!". They are redrawn every third frame, so they shiver. | Luma Pillar, ₹1,599 | The owner's styling clip (smoke) |
| 8.30 | Frame break: the Aurora in a white photo frame. Its line of light runs out past the frame and washes the wall. | Aurora, from ₹1,999 | Aurora clip (lit part only) |
| 10.01 | Glass type: frosted, refracting glass letters, "warm", over the lamp, with a light sheen across them. | Globe Edison, ₹2,999 | Shoot photo AC4I9873 |
| 11.73 | Vertigo: the lamp holds still while the room rushes in behind it. The room is inpainted where the lamp was. | Minimalist floor lamp, from ₹6,999 | Shoot photo AC4I9776, cut out |
| 13.45 | Chart grow: the range's live prices as a rising line on a log scale, each point with its lamp's photo. | Nine products, ₹999 to ₹9,999 | Shopify, 14 Oct |
| 15.16 | Pull-back reveal: the full-screen photo pulls back into a phone on nixwoods.com, then the logo. | Compact wall light, from ₹4,999 | Shoot photo AC4I9629 |

**Products and prices:**
- Every product is named per `PRODUCT-ID.md`, including the 5 Aug shoot table confirmed by the owner on 14 Oct.
- Prices are live on Shopify (14 Oct). Re-check them before posting.

**Music:**
- music4-genz, the phonk track, starts 26.0 s in, so its drop lands at 1.43 s.
- Each section is one bar (1.716 s) from there.
- A whoosh (sfx-whoosh) peaks on each cut.
- All of it is generated and cleared for paid use, so both cuts can run as ads.

```bash
python3 brand-reels/effects-lookbook/make_masks.py        # once: the three cut-outs in masks/
python3 brand-reels/effects-lookbook/effects_lookbook.py
```
