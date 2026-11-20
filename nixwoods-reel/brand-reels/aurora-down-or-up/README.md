# Aurora: "Down only, or up & down?" (20 Nov 2026)

**The ask:** the owner: "make a reel for aurora".

**The idea:** the one real choice on the Aurora page is the direction of the light. The page puts it plainly:
- "Down only: a warm pool of light below. The wall above stays dark."
- "Up and down: … the whole wall glows."

A reel that answers it is worth saving. Its payoff is the wall above the bar lighting up.

## Material
- **No real footage of the live bar.** Every Aurora video on Drive is from the August shoot, which shows the
  discontinued Black bar. Natural Teak is the only live finish (owner, 20 Oct).
- **The live product-page images are treated as AI.** All eight (Shopify CDN, 20 Nov) are 1254×1254 with no camera
  metadata, which is an image generator's output size. So: "Made with AI" on, plus a caption line. The owner can
  confirm whether they are renders.
- **Images used, in `src/`:**
  - 03: the page's own Downward / Up & Down pair. The up & down room is also the end card.
  - 04: above a bed.
  - 05: above a painting, 30 in.
  - 06: above a bathroom mirror, 30 in.
  - 02: the grain and the light line.

## Facts (live page, 20 Nov)
- **Claimed on screen:**
  - solid teak, no MDF, no veneer;
  - 30 or 48 inch;
  - warm white 3000K;
  - down only, or up and down.
- **Price:** from ₹1,999 (30 in, down only), in the caption only.
- **Not on screen:** hardwired, watts, lumens, dimmable, Black.

## The cut (`aurora_down_or_up.py`, music6-corners, 11.26 s)
| Beat | Picture | Text |
|---|---|---|
| 0–G4 | 03 down only, a slow push | "AURORA · WHICH ONE IS YOURS?" / "Down only: / a warm pool *below.*" |
| G4–G6 | the up-light rises from the bar into the up & down room (a soft amber edge rides it) | "Up & down: / the whole wall *glows.*" |
| G6–G9 | three rooms, one a beat | chips: above a bed (30 or 48 inch) · above a painting (30 inch) · above a mirror (30 inch) |
| G9–G11 | the grain macro | "Solid teak. / No MDF, *no veneer.*" |
| G11–end | the up & down room, darkened low | Aurora Wall Light · Solid teak · 30 or 48 inch · warm 3000K · nixwoods.com |

**Sound:** `cues.json` adds text pops, a tap on each room, and an end hit.

```bash
/usr/bin/python3 brand-reels/aurora-down-or-up/aurora_down_or_up.py
/usr/bin/python3 system/sfx/place.py out/<name>.mp4 <final>.mp4 --cues brand-reels/aurora-down-or-up/cues.json \
    --no-auto-cuts --style calm --master -14
```
