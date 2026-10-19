# NixWoods "CAM 02": the NixLine heist (AI skit, real lamp)

**The idea:** the owner sent instagram.com/reel/DekLWdWN6eH on 17 Oct. It is a breakdown of a restaurant ad that got
13.8M views:
- high-angle CCTV of a kitchen;
- a hooded man walks in and the staff put their hands up;
- he ignores the till and everything else, and cooks the burger.

It works because it does not look like an ad, and the product is the centre of the scene the whole time. The ask:
"This is the robbery ad you need to plan for nixwoods and then execute."

**Owner's choices (17 Oct):**
- footage: AI-generate it;
- product: the NixLine floor lamp.

The plan was approved on 19 Oct.

**Ours:** 17.6 s, 9:16, workshop CCTV at night. Every tool sits on the bench and the cash box lies open; the thief takes only the lamp.

| Time | Shot | On screen |
|---|---|---|
| 0.0–4.4 | A: the thief tiptoes in past the sleeping watchman | "CAM 02 caught this at 2:47 AM" |
| 4.4–7.6 | B: the watchman wakes, hands up; the thief goes "shh" and points at the lamp | |
| 7.6–11.4 | C: a click, a warm flash, and he holds up the lit NixLine. Its light is the only colour in the grey frame | "He skipped the cash." |
| 11.4–14.2 | D: he leaves with it; the watchman shrugs | "Took the ₹999 lamp." |
| 14.2–17.6 | Hard cut out of CCTV to the real lamp in a real room (photo AC4I9815, 5 Aug shoot) | "Nobody steals a tubelight." · NixLine floor lamp · solid teak · ₹999 ~~₹1,599~~ · nixwoods.com |

**AI disclosure:**
- "Skit made with AI. The lamp is real." sits on every frame, including the end card.
- Instagram's "Made with AI" toggle must be on when it goes up, and Meta's AI disclosure must be ticked if it runs as an ad.
- The end shot is a real photograph, so the product as bought is never AI.

**Guardrails held:**
- no weapon anywhere, and no aggression beyond the hands-up gag;
- the thief is masked; the watchman is a synthetic face on AI-labelled frames;
- no "BREAKING NEWS" strap, real place or real date: the HUD reads "CAM 02 · NIXWOODS CCTV", so it cannot be taken
  for a real crime report;
- claims: ₹999 (was ₹1,599) and solid teak only (`PRODUCT-FACTS.md`). No COD, length, dimmer or switch claim.

## Generation (Higgsfield, 19 Oct)

**Reference:** `refs/nixline-real-crop.jpg`, cropped from AC4I9815 (`refs/nixline-real.jpg`): an upright square teak
bar with an LED channel down its front face, on a square teak block.

**Start frames:** Nano Banana 2.1, 9:16, 1k, 1.5 credits each.
- A was made from the reference alone.
- B, C and D were made from A plus the reference, so the room and camera stay the same.

| Frame | Verdict |
|---|---|
| `gen/A-start.jpg` | approved: thief entering, watchman asleep, NixLine upright on its block |
| `gen/B-start.jpg` | approved: hands up, "shh" |
| `gen/C-start-rejected-too-tall.jpg` | **rejected**: the lamp drawn far taller than hip height |
| `gen/C-start.jpg` | approved after one retry that fixed the height in the prompt (no size claim is made in the reel) |
| `gen/D-start-rejected-too-tall.jpg` | **rejected**: too tall again |
| `gen/D-start.jpg` | approved after one retry |

**Clips:** Kling 3.0 Turbo image-to-video, 5 s, 720p, 7.5 credits each. All four were approved after watching every frame:
- the lamp keeps its shape;
- there is no camera move;
- there is no weapon.

The verdicts are recorded in `system/presets.json` → `products.floor.assets`:
- `clip_status.heist_a`–`heist_d` for the clips;
- `status.heist_start_*` for the start frames.

The start frames are deliberately not in `stills`, so no mechanism cuts them into an ordinary floor-lamp reel.

**Credits:** 6 frames × 1.5 = 9, plus 4 clips × 7.5 = 30, so 39 in total, against a plan cap of 80.

<details><summary>Prompts</summary>

**A (start frame).** Security camera (CCTV) still, camera mounted high in a corner of a small Indian woodworking
workshop at night, looking down diagonally across the room, wide-angle lens with slight fisheye distortion, low-light
surveillance quality, slightly soft and grainy. The room is dim: one weak tube light near the door on the right.
Concrete floor with sawdust. Along the left wall a long wooden workbench with hand planes, clamps, a power drill,
stacked teak planks, and a small grey metal cash box with its lid open showing banknotes. Near the back wall, standing
alone on the floor, one floor lamp that is EXACTLY the lamp in the reference image: a slim straight square bar of solid
teak, about hip height, standing perfectly upright on its own small square teak block, with a long narrow light channel
down its front face; the lamp is switched OFF. A night watchman in a plain shirt sits asleep on a plastic chair by the
door, chin on his chest, face not visible. A thief in a black hoodie and black balaclava is creeping in through the open
door, crouched, tiptoeing. No weapons. No text, no logos, no timestamp.

**B (start frame).** The exact same CCTV security camera view of the same workshop as the first reference image: same
high corner angle, same fisheye lens, same room, same workbench with the open cash box full of banknotes, same lamp
standing upright on its square block by the back wall (switched OFF, matching the second reference image exactly). A
moment later: the night watchman has jolted awake on his plastic chair and raises both hands in surprise. The thief in
the black hoodie and black balaclava now stands in the middle of the room facing him, holding one finger to his lips in
a 'shhh' gesture. No weapons. Low-light grainy surveillance look. No text, no logos, no timestamp.

**C (start frame, the retry that was approved).** The exact same CCTV security camera view … same workbench with the
open cash box full of banknotes left untouched. The thief in the black hoodie and black balaclava stands by the back
wall holding the small floor lamp from the second reference image upright in front of his belly with both hands, like
holding a trophy. The lamp is SHORT: only about 75 cm tall in total (a 70 cm slim square solid teak bar on a small
square teak block about 12 cm wide) - held at his waist, its top only reaches his chest. It is switched ON, its narrow
front light channel glowing warm white, casting a warm glow on the wall and on the thief. The night watchman sits on
his plastic chair by the door with both hands still raised, staring. No weapons. Low-light grainy surveillance look. No
text, no logos, no timestamp.

**D (start frame, the retry that was approved).** The exact same CCTV security camera view … the open cash box full of
banknotes still untouched. The thief in the black hoodie and black balaclava is stepping out through the open door on
the right, hugging the small floor lamp from the second reference image upright against his chest with both arms. The
lamp is SHORT: only about 75 cm tall in total (a 70 cm slim square solid teak bar on a small square teak block) - it
spans only from his waist to his chin. Its narrow front light channel glows warm. The empty spot by the back wall where
the lamp stood. The night watchman on his plastic chair lowers his hands and shrugs. No weapons. Low-light grainy
surveillance look. No text, no logos, no timestamp.

**Clips:** every prompt starts with "Fixed security camera, absolutely no camera movement, no zoom. Grainy night CCTV
footage." and continues:
- **A:** "The thief in the black hoodie and balaclava slowly tiptoes in through the door and sneaks past the sleeping
  watchman toward the middle of the room, crouched, looking left and right. The watchman stays asleep. Everything else
  in the room stays still. No weapons."
- **B:** "The startled watchman keeps both hands raised in the air. The masked thief keeps one finger on his lips
  saying shhh, then slowly turns his head toward the wooden floor lamp standing by the back wall and points at it. The
  lamp stays exactly as it is. No weapons."
- **C:** "The masked thief holds the small glowing wooden floor lamp upright in front of him and admires it, tilting
  his head and nodding slowly, the warm light glowing on the wall. The lamp keeps its exact shape and size: a short
  slim square teak bar on a small square block with a glowing front channel. The watchman keeps his hands up and
  stares. No weapons."
- **D:** "The masked thief hurries out through the open door hugging the small glowing wooden lamp and disappears into
  the dark doorway. The watchman lowers his hands, shrugs, glances at the untouched cash box full of money on the bench
  and shakes his head. No weapons."

</details>

## Post (`cctv_heist.py`)

**Grade:** night CCTV.
- green-grey and crushed, with a vignette, scanlines and coarse grain;
- held to 15 fps, as a CCTV feed records (this also keeps the file at 13 MB);
- a selective-colour mask keeps only warm light, pushed to a 3000K cream, so the lamp is the one colour in the frame;
- a band-slip glitch on the first three frames after each cut, and a warm flash as the lamp comes on.

**HUD:** REC dot, "CAM 02 · NIXWOODS CCTV" and a ticking 02:47 AM clock in Space Grotesk.

**Captions and end card:**
- captions in Inter 600 on dark bars;
- end card in Fraunces and Inter on cream cards, clear of the painting and the plant in the photo.

**Sound:** all ours.
- music7-noir creeps under the CCTV, over a 50/100 Hz room hum;
- a switch click, and the noir cuts out at the lamp;
- music1 warms the real shot.

The reference's audio is never used: that reel is a commentary.

**Before it runs as an ad:** the owner approves it, and Meta's AI disclosure is ticked. Ads go to .com only.

```bash
python3 brand-reels/cctv-heist/cctv_heist.py
```
