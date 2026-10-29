# Art light: the Circular Hole Wall Light over a painting (29 Oct 2026)

The owner sent 10 iPhone clips (IMG_8114–8123, HLG, vertical) and asked for one reel for social and one for Meta ads.
The goal: shares, saves and likes, with an aesthetic that makes people want the light.

## What the footage holds
| Clip | Content | Used |
|---|---|---|
| 8114 | painting → tilt up → the light over the frame | no (8115 is the same move, cleaner) |
| 8115 | painting (figure on a golden boat in sunset clouds) → tilt up → the light settles above the frame | hook (social), frame 1 (ad), end-card still |
| 8116 | the light → tilt down onto the painting | the styling tip (social), the facts (ad) |
| 8118 | macro: the wood grain and the row of lit holes | "Real wood." in both cuts |
| 8121 | the light over the painting, close, for the last 0.9 s | no (too short) |
| 8117, 8119, 8120, 8122, 8123 | blank wall and moulding, no lamp | no |

Only the three used clips are in `src/`.

## The two ideas
- **Social: "Everyone looks at the painting. / Until they look up."** It is a curiosity hook on the most beautiful
  frame we have, and the tilt answers it. The save is driven by a styling tip people can use with any wall light: "Hang
  it above your art. The glow becomes the frame." 10.0 s, with no price on screen; the price goes in the caption.
- **Ad: "Light that frames your art."** The product and the price (₹3,999) are on frame 1, followed by the wood
  macro, the facts (30 in, 20 W warm LED, 3-year wood warranty) and an end card with the price, the real FLY100 prepaid
  saving and "Shop at nixwoods.com". 10.0 s, in 9:16 and 4:5.

## Facts (live page, 29 Oct)
- 30 in, ₹3,999 (the page changed from 24 in / ₹2,999; see PRODUCT-FACTS.md).
- Wood with natural grain ("real wood"). Integrated 20 W warm LED. Hardwired.
- 3 years on the wood, 1 year on the LED and electricals. "Save ₹100 prepaid with FLY100".
- Not claimed: solid wood (only the title says it), a species, dimmable.
- Real footage only, so there is no AI label.

## Build
```bash
python3 brand-reels/art-light/art_light.py                     # social + ad 9:16 + ad 4:5 into out/
python3 system/sfx/place.py out/<social>.mp4 <final>.mp4 --cues brand-reels/art-light/cues-social.json --no-auto-cuts --style calm --master -14
python3 system/sfx/place.py out/<ad>.mp4 <final>.mp4 --cues brand-reels/art-light/cues-ad.json --no-auto-cuts --style calm --master -14
```
- **Tone-map:** the HLG footage goes through the house tone-map (system ffmpeg with zscale).
- **Grade:** a slightly warmer version of the photo grade (×[1.08, 1.02, 0.84]), because the tone-map turns the bar
  mauve. The lit holes are pulled toward the cream line core.
- **Music:** music6-corners. The cuts land on its grid at beats 2/3, 5/6 and 8.
- **Re-encode:** the CRF 17 renders come out at about 35 MB because of the grain, so the committed files are the
  sound-passed versions re-encoded at CRF 19 (about 11–15 MB). The audio is copied unchanged.
- **Paid 9:16:** all ad text ends above y 1250. On the end card, the still is lifted by a 1.18× crop so the name,
  the price and "Shop at nixwoods.com" fit between the light and the CTA bar. The ad end cards carry no logo.
