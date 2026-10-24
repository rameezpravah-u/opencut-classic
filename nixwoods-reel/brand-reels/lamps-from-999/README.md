# "Lamps from ₹999": the tablet ad (4:5, 15.4 s)

**The ask:** on 24 Oct the owner sent instagram.com/p/DZsWYgMDE-e (RAS Oils): "Make this exact, just replace the
product."

The owner chose:
- a free composite, so no generation credits were spent;
- the offer "Lamps from ₹999".

## The reference, frame by frame (15.46 s, 720x900, every frame viewed)

| Time | What happens |
|---|---|
| 0.0–15.5 | A tablet on a desk plays a clip. A gold-lit wall sits behind it. "Buy Any 3 @1399" is in a gold frame at the top, with a small hashtag line above it. The logo sits top-right. |
| ≈0.75 | A hand sets the first jar down in front of the tablet. |
| ≈6.0 | A second product is lowered onto the first. |
| ≈7.0 | A third product is set down beside them. |
| 13.1–15.5 | A black end card. The logo fades in, with a tagline under it. |

## Ours

Same layout and timings, with our three lamps priced from ₹999.

| Time | What happens |
|---|---|
| 0.0 | The tablet (portrait) plays our CAM 02 heist reel (cctv-heist v3) with its own sound. "@nix_woods · Lamps from ₹999" sits in a gold frame. The logo sits top-right. |
| 0.75 | The NixLine comes in from the left, as the reference's hand does, and is set down leaning. Its light pools on the wall. The tag reads "NixLine ₹999". |
| 6.0 | The Luma Pillar comes in from the left. The tag reads "Luma Pillar ₹1,599". |
| 7.0 | The Rubik's Cube is set down from above, as the reference's second product is. The tag reads "Rubik's Cube from ₹2,999". |
| 10.0 | The cube's light turns from amber to red. Both photos are real, so the cube is shown in two colours. |
| 13.1 | Cut to a near-black end card. The logo fades up, with "SOLID WOOD LIGHTING" and "nixwoods.com" under it. |

## What we changed, and why

**The clip on the tablet.** The reference plays *Friends*. That footage is copyrighted and we hold no licence. The
owner offered to take the risk, but it was not used: a takedown or a muted reel would hit our account, not only the
post. The tablet plays our own CAM 02 heist reel instead, so the tablet still tells a story.

**The tablet's shape.** It stands in portrait, because CAM 02 is 9:16. The crop keeps the REC line and the captions
inside the screen.

**No hand.** Each lamp moves in along the path the reference's hand takes. The move is an ease-out with no overshoot
(MOTION.md §5).

**Price tags.** The reference has none. We added a small cream card under each lamp so all three prices can be read.

**Sound.**
- 0–13.1 s: CAM 02's own soundtrack, all ours, filtered to sound like a tablet speaker.
- A soft wooden knock as each lamp is set down.
- music1 under the end card.
- The reference's audio is not used.

**Departures from MOTION.md**, as in lamps-under-3000 v2 when the owner asks for an exact copy:
- the big serif price in Fraunces 600, not Inter;
- a gold frame;
- sparkles in the top light.

All colours still come from MOTION.md: the gold is amber and amber-dark, the wall is paper, the type is teak ink.

**The NixLine leans.** MOTION.md says a lamp never leans, but the NixLine has no base and is sold leaning
(PRODUCT-ID.md), as it is in the heist and bullet-burn reels.

## Claims

- **Prices:** from the live product JSON on 24 Oct. NixLine ₹999 (was ₹1,599); Luma Pillar ₹1,599; Rubik's Cube from
  ₹2,999 (Candy Glass, the cube shown).
- **Other claims:** none. No size, COD, dimmer, switch or wood-species claim. The Luma's species is not stated on
  its page. "Solid wood lighting" is the brand line.
- **D-017:** the cube is named "Rubik's Cube".

## Sources

| Element | Source | AI? |
|---|---|---|
| NixLine | cut out of `bullet-burn/gen/set.jpg` | AI, Nano Banana 2.1, approved 21 Oct |
| Luma Pillar | cut out of the product page photo `16b3b563-…` | page photography |
| Rubik's Cube | page photos AC4I9838 (Candy Glass, amber) and AC4I9835 (red) | real shoot |
| Tablet screen | `cctv-heist/out/…cctv-heist-v3-AI.mp4` | AI |
| Desk, wall, tablet, frame, type | drawn in code | no |

- **Cut-outs:** made for free with rembg 2.0.67 (MIT, isnet-general-use model), plus GrabCut for the red cube's dark
  base. `make_cutouts.py` records the steps. Verdicts are in `system/presets.json` under `lamps999_nixline_cut` and
  `lamps999_cube_cuts`.
- **Fonts:** Fraunces and Inter (`assets/`).

**AI disclosure:**
- The tablet footage and the NixLine are AI.
- There is no on-screen label, matching the owner's call on the CAM 02 reels.
- Instagram's "Made with AI" toggle must be on.
- If this runs as an ad, tick Meta's AI disclosure.
- The caption ends: "The clip on the tablet and the NixLine photo are made with AI."

## Encode

CRF 21, not MOTION.md's 17: at 17 the fine grain made a 26 MB file, over the ~21 MB ceiling. At 21 it is
6.2 MB, with no visible loss in the full-resolution checks.

## Run

```bash
python3 brand-reels/lamps-from-999/lamps_from_999.py               # → out/NW-CREATIVE-VID-20261024-…-v1-AI.mp4
python3 brand-reels/lamps-from-999/lamps_from_999.py --still 1.1 9  # stills to check a change
```
