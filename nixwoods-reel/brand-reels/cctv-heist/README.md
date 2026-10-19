# NixWoods "CAM 02": the NixLine heist (AI skit)

**The idea:** the owner sent instagram.com/reel/DekLWdWN6eH on 17 Oct: a breakdown of a 13.8M-view restaurant ad. In
high-angle CCTV of a kitchen, a hooded man walks in, the staff put their hands up, and he ignores the till and cooks
the burger. It works because it does not look like an ad, and the product is the centre of the scene the whole time.

The ask: "This is the robbery ad you need to plan for nixwoods and then execute." On 17 Oct the owner chose AI
footage and the NixLine floor lamp. The plan was approved on 19 Oct.

## v2 (current) and why v1 was withdrawn

**v1 showed the wrong product.** It was generated from the 5 Aug photo AC4I9815, which our notes called "the real
NixLine". The owner's verdict on 19 Oct: "you have got the wrong product, get the original NixLine." That photo
shows a lit rod on a square block, and nixwoods-os already files it as the corner floor lamp. The v1 clips and
render have been taken out of the repo. `floor-reels/ref/REFERENCE.md` and `PRODUCT-ID.md` are corrected.

**The NixLine, as on nixwoods.com/products/nix-line-solid-wood-floor-lamp and in the owner's own clips nx00–nx08:**
- one honey-coloured solid teak bar, 27 in, 1.5 x 1.5 in;
- softly rounded ends;
- a frosted LED strip down nearly its whole front face;
- no separate base: it leans in a corner, with the cord leaving from its foot.

**The end shot:** the owner then asked to "generate an image that is sexy and aesthetic and use that". `gen2/hero.jpg`
is a moody night corner: the NixLine leaning and lit, a boucle chair, a glass of wine on travertine.

## The reel

17.6 s, 9:16. Workshop CCTV at night. Every tool is on the bench and the cash box is open; the thief takes only the lamp.

| Time | Shot | On screen |
|---|---|---|
| 0.0–4.4 | A: the thief tiptoes in past the sleeping watchman; the NixLine leans unlit in the far corner | "CAM 02 caught this at 2:47 AM" |
| 4.4–7.6 | B: the watchman wakes, hands up; the thief goes "shh" | |
| 7.6–11.4 | C: a click, a warm flash, and he holds up the lit NixLine. Its light is the only colour in the grey frame | "He skipped the cash." |
| 11.4–14.2 | D: he walks out with it on his shoulder; the watchman shrugs | "Took the ₹999 lamp." |
| 14.2–17.6 | Cut out of CCTV to the hero still | "Nobody steals a tubelight." · NixLine floor lamp · solid teak · ₹999 ~~₹1,599~~ · nixwoods.com |

**AI disclosure:**
- Every frame, the end shot included, is AI-generated. "Skit and photo made with AI." sits on every frame.
- Turn on Instagram's "Made with AI" toggle when it goes up.
- As a Meta ad, tick Meta's AI disclosure as well.

**Guardrails:**
- no weapon, and no aggression beyond the hands-up gag;
- in C, the shot starts at 1.1 s, after he has raised the bar upright, so it never reads as a bat;
- the thief is masked, and the watchman's face is synthetic;
- the HUD reads "CAM 02 · NIXWOODS CCTV": no news strap, no real place, no real date;
- claims: ₹999 (was ₹1,599) and solid teak only (`PRODUCT-FACTS.md`). No COD, length, dimmer or switch claim. The
  hero reads a little longer than 27 in, so make no size claim with it.

## Generation (Higgsfield, 19 Oct)

**References:**
- `refs/nixline-owner-clip-nx04.jpg`: the owner's own clip nx04 at 1.2 s, the whole lamp from end to end;
- `refs/nixline-pdp-marble-corner.jpg`: the live product page's marble-corner photo.

**Stills:** Nano Banana 2.1, 9:16.
- `gen2/A-start.jpg` was made from both references.
- B, C and D were made from A plus the clip reference, so the room and camera stay the same.
- `gen2/hero.jpg` was made at 2k from both references. A second hero variant failed on Higgsfield's side and was refunded.

**Clips:** Kling 3.0 Turbo image-to-video, 5 s, 720p.
- Every frame was viewed.
- All four are approved: the lamp keeps its shape, the camera does not move, and there is no weapon.
- The verdicts are in `system/presets.json` → `products.floor.assets` (`clip_status.heist_*`, `status.heist_v2_*`).
- The v1 entries are marked rejected (wrong product).

**Credits:**

| Round | What | Credits |
|---|---|---|
| v1 | 6 frames × 1.5, 4 clips × 7.5 | 39 |
| v2 | hero 2, 4 frames × 1.5, 4 clips × 7.5 | 38 |
| **Total** | | **77**, against the cap of 80 |

<details><summary>v2 prompts</summary>

**Hero:** Sultry, moody editorial interior photograph at night, shot for a design magazine. The only light in the
room comes from one floor lamp that is EXACTLY the lamp in the reference images: a single slim straight bar of
honey-coloured solid teak with visible grain, square cross-section about 4 cm with softly rounded ends, about 70 cm
long, with a frosted white LED diffuser strip running almost its full length down its front face, glowing warm 3000K.
It has no base: the bar leans casually into the corner of the room, its foot on the floor and its top against the
wall, a thin black cord trailing from its bottom end. Its warm light pours up and across the textured lime-plaster
corner walls in a soft gradient, falling off into deep warm shadow. Around it, minimal and sensual: a low boucle lounge
chair half in shadow, a linen throw draped over it, a ceramic vase with a single dried branch, a glass of red wine on
a small travertine side table catching the glow. Rich chiaroscuro, deep shadows, warm amber and cream tones, shallow
depth of field, 50mm lens, slightly low camera angle, the lamp sharp and centre-right in the frame, generous dark
negative space in the upper left. No people, no text, no logos.

**A:** CCTV still, camera high in a corner of a small Indian woodworking workshop at night, wide-angle with slight
fisheye, low-light and grainy; one weak tube light by the door. A workbench with hand planes, clamps, a drill, stacked
teak planks and an open grey cash box showing banknotes. In the far corner, on its own, the lamp from the references
(a slim straight honey-teak bar with rounded ends, about 70 cm, frosted white strip down its front face, no base,
leaning in the corner), switched OFF. A night watchman asleep on a plastic chair by the door. A thief in a black
hoodie and balaclava creeping in, crouched. No weapons. No text, no logos, no timestamp.

**B, C, D:** "The exact same CCTV security camera view … as the first reference image", then:
- **B:** the watchman jolts awake, hands up; the thief faces him with a finger to his lips.
- **C:** the thief in the corner holds the lamp in front of him with both hands like a trophy, switched ON, glowing
  warm along its length; the watchman's hands still up.
- **D:** the thief steps out of the door carrying the lit lamp over his shoulder, cord dangling; the corner is empty;
  the watchman lowers his hands and shrugs.

Each ends: "No weapons. Low-light grainy surveillance look. No text, no logos, no timestamp."

**Clips:** each starts with "Fixed security camera, absolutely no camera movement, no zoom. Grainy night CCTV
footage.", then:
- **A:** he tiptoes in past the sleeping watchman; the lamp stays leaning in the corner.
- **B:** "shh", then he points.
- **C:** he gently raises the glowing lamp straight upright and admires it, nodding; he does not swing it; the lamp
  keeps its exact shape.
- **D:** he walks out with the lamp on his shoulder; the watchman shrugs, glances at the untouched cash box and shakes
  his head.

Each clip prompt ends with "No weapons."

</details>

## Post (`cctv_heist.py`)

**Grade:** night CCTV.
- green-grey and crushed, with a vignette, scanlines and coarse grain;
- held to 15 fps, as a CCTV feed records (this also keeps the file near 14 MB);
- a selective-colour mask keeps only warm light, pushed to a 3000K cream, so the lamp is the one colour in the frame;
- a band-slip glitch after each cut, and a warm flash as the lamp comes on.

**HUD:** REC dot, "CAM 02 · NIXWOODS CCTV" and a ticking 02:47 AM clock in Space Grotesk.

**Captions and end card:**
- captions in Inter 600 on dark bars;
- end card in Fraunces and Inter, cream type in the dark space above the chair.

**Sound:** all ours.
- music7-noir over a room hum;
- a switch click, and the noir cuts out at the lamp;
- music1 warms the hero.

The reference's audio is never used.

**Before it goes up:** the owner approves it. As an ad, tick Meta's AI disclosure; ads go to .com only.

```bash
python3 brand-reels/cctv-heist/cctv_heist.py
```
