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

## v2: day / night (29 Oct, the same day)
The owner, on v1: "of all the videos I sent you, you worked on the most blurred… you created so basic". The owner
pointed me to the Hook Master carousel (instagram.com/p/De8I3VcjtKq) to learn from.

**What went wrong.** v1 was cut from a contact sheet whose tiles were squashed middle strips of vertical frames. Six
clips read as "blank wall" and were skipped:
- 8122 and 8123: the light switched off, with sharp flame grain; 8123 is 4K 60p.
- 8117 and 8119: the lit holes, close.
- 8120 and 8121: pulls back to the painting.

v1 was built on the two softest tilts instead (8115 and 8116). The fix for next time is `system/clip_triage.py`,
recorded in the PLAYBOOK.

**v2 (`art_light_v2.py`)** uses the sharpest clips, scored by Laplacian variance at 2 fps and checked at native
resolution:
| Shot | Clip | Line |
|---|---|---|
| Day | 8123 at 0.6× from 60p (social) / 8122 (ad) | "By day, a piece of wood." (+ ₹3,999 chip on the ad) |
| Switch, on the beat at 2.07 s | 8118 macro, the LEDs warming up over 0.3 s | "By night, this." |
| Lit | 8117 | "Warm light, through every hole." + spec cards: wood natural grain · 20 W warm LED · 30 in |
| Over the art | 8114, settled | "Save this styling tip / Hang it above your art. The glow becomes the frame." (ad: "3-year wood warranty") |
| End card | 8114, last frame | name, facts or price + FLY100, nixwoods.com |

**From the carousel:**
- **Clear, then curious:** frame 1 shows and says what it is, and the line opens the gap the switch pays off.
- **The six-viewer read**, done before the render.
- **Its UI craft in our palette:** a glass DAY/NIGHT toggle that flips on the switch, small-caps amber labels on glass
  spec cards, and a serif headline with one amber italic accent.

**Sound:** `cues-v2-*.json`, with a lamp-switch click and bloom on the switch.

## Off / on film (30 Oct)
**Reference:** instagram.com/reel/DfCN36XNLWO, Studio96's BiFROST table lamp (15.9 s, 35k views). The owner: "Do
this". Its song has vocals and is licensed to them, so it is never used here.

**Its shape:** the lamp off with slow drifts and a material close-up, then a hard cut to it lit in nearly the same
frame at 7.4 s, a long lit hold, then off again and a fade to black. No text.

**Ours (`off_on_film.py`):** the same beats on the owner's sharpest clips, on music1's grid, 15.88 s:
| Time (s) | Beat | Clip |
|---|---|---|
| 0–3.5 | off hero | 8123, 4K 60p slowed |
| 3.5–6.2 | off detail, the holes | 8122 |
| 6.2–7.1 | off, the bar above the painting | 8123's end |
| **7.06** | **the switch** | 8121, framed so the bar sits at y ≈ 700 in both; the LEDs warm up over 0.3 s, with a switch click |
| 7.1–8.8 | on, same frame | 8121 |
| 8.8–11.5 | lit macro | 8118 |
| 11.5–13.7 | the long lit hold over the painting, pushed in slowly | 8115's settled last frame |
| 13.7–14.6 | lit close | 8117 |
| 14.6–15.9 | off again, then a fade to black | 8123's end |

The only text is the name and nixwoods.com on the fade. The file is CRF 22 to stay under 21 MB.
