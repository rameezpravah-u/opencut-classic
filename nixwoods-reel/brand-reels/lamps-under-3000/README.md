# "Lamps under ₹3,000." (four NixWoods lamps, one list reel)

After @scoopedfriday's "Lamps under Rs. 1500" (instagram.com/reel/Dc6DAC5zsGH, 14.7 s, 169k views, 2.3k comments):
a big hook over the first lamp, then one lamp per shot in a dim warm room, its name fading in and its price just after.
Ours is four NixWoods lamps, all real footage, 9:16, 30 fps, 10.03 s on the music6-corners beat grid, so every
price is on screen before 10 s. The look follows MOTION.md (Fraunces and Inter, cream and amber), not the reference's
yellow type. The reference's "dripping" hook lettering is not used: MOTION.md doesn't cover it.

| Time | Lamp (product, live price 11 Oct) | Footage |
|---|---|---|
| 0–2.5 s | **Lamps under ₹3,000.** Rubik's Cube Lamp, ₹2,999 | `rubik-reels/src/14-1.mp4`, green then red (two colours) |
| 2.5–5.0 s | NixLine Floor Lamp, ₹999 | `floor-reels/src/nx04-7930.mp4`, straightened 4–5° so it stands upright |
| 5.0–7.5 s | Aurora Wall Light, from ₹1,999 | `src/drive-aurora-v3-fullshoot-hook.mp4` (Drive cut of shoot clip 03), the angled wash |
| 7.5–10.0 s | Edison Dimmer Lamp, ₹2,499, then "All four at nixwoods.com" | `src/drive-edison-dimmer-demo-wa.mp4` (Drive's small copy of shoot clip 16): a hand turns the brass dimmer and the tube bulb comes up |

Products identified with `nixwoods-reel/PRODUCT-ID.md`. Two things to confirm with the owner:
- The Aurora shot shows two parallel lines of light. The owner's Drive files and FOOTAGE-INDEX call this shoot
  the Aurora (and the Duo Glow, which has two lines, was listed after the shoot), so it is named Aurora here.
- AC4I9815 (a lit bar on a square block in a stairwell) is filed on Drive as the NixLine but sits on the Shopify
  page of the corner floor lamp. It was not used.

The montage grade runs at 45% on the three warm shots; the Rubik's Cube shot keeps its own colour, because its
colours are the product. Nothing is generated, so no AI label is needed. A hand appears; no faces.

    python3 brand-reels/lamps-under-3000/lamps_under_3000.py
