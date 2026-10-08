# MOTION.md — NixWoods

Read this in full before designing, generating or animating anything for NixWoods: reels, carousels,
ads, HyperFrames compositions, Python frame pipelines, generated scenes.

Written 8 Oct 2026 with the `brand-intake` skill. It is based on five pieces that passed review and
shipped or were scheduled:
1. Mosaic reel: `brand-reels/mosaic/NW-CREATIVE-VID-20261007-nixwoods-mosaic-grid-v1.mp4`
2. "Follow the line" carousel: `floor-reels/concepts/follow-line/`
3. V2 "one line of light" montage: `floor-reels/concepts/meta-set/NX-META-V2-one-line-9x16*.mp4`
4. Diya ad: `floor-reels/concepts/meta-set/NX-META-G-tallest-diya-*.jpg`
5. Diwali corner A: `floor-reels/concepts/meta-set/NX-META-A-diwali-price-drop-*.jpg`

Every value below was read from the scripts that made those frames, not sampled from a JPEG.
**ASK ME** marks the places the frames do not settle.

## 0. Two looks, one brand

The frames hold two looks. Each look has its own job.

| Look | Ground | Ink | Use for |
|---|---|---|---|
| **Dusk** | teak ground `#2E1E14`, or a real photo graded warm and dim | cream `#F6EFE4` | reels, video ads, 9:16 statics, end cards |
| **Paper** | cream `#F6EFE4` / paper `#EEE4D4` | teak ink `#3A2618` | carousels, explainers, slides with numbers |

The lamp's light is the brightest thing on screen in both looks. In Paper, the glowing line plays the
lamp's part.

## 1. Colour

| Name | Hex | RGB | What it is for |
|---|---|---|---|
| Cream | `#F6EFE4` | 246 239 228 | Dusk headlines; the Paper ground; price cards |
| Paper | `#EEE4D4` | 238 228 212 | the second Paper tone (cards on cream) |
| Teak ground | `#2E1E14` | 46 30 20 | the Dusk flat ground (mosaic, end cards) |
| Teak ink | `#3A2618` | 58 38 24 | Paper headlines and body; the logo on light |
| Teak ink, dark | `#342216` | 52 34 22 | the reveal carousel's ink, and the same job as teak ink |
| Amber | `#E8A24A` | 232 162 74 | the price on dark, one accent word, the URL on dark, the glow halo |
| Amber, dark | `#B06828` | 176 104 40 | the price on light (amber fails contrast on cream) |
| Line core | `#FFEED2` | 255 238 210 | the centre of a glowing line, never text |
| Pill | `#F0D6B2` | 240 214 178 | chip fill on Paper |
| Muted on light | `#7C6452` | 124 100 82 | secondary text on Paper, the was-price, @nix_woods |
| Muted on dark | `#C8BEB2` | 200 190 178 | secondary text on Dusk, the was-price |

Rules:
- Amber appears once or twice a frame: the price, and at most one accent word or the URL.
- Cool white, blue and grey appear only as the "before" (the tubelight). The cool side of the colour-temperature scale is the only other place.
- No pure black and no pure white. The darkest Dusk value is lifted (+0.02) so blacks keep a little air.

## 2. Type

Use two families: Fraunces for the voice and Inter for the facts. Add Gochi Hand only for one handwritten note.

| Role | Font | 9:16 (1080×1920) | 4:5 (1080×1350) |
|---|---|---|---|
| Headline | Fraunces 600 | 86–96 px, 2 lines max | 78–86 px |
| Hook over footage | Fraunces 600 | 84–96 px on a top scrim (V1); 56–64 px split either side of the lamp when the lamp fills the frame (V2) | — |
| Accent word | Fraunces 500 italic, in amber | same size as the headline | same |
| Price | Inter 600 | 112 px | 92–120 px |
| Was-price | Inter 400, struck through | 46 px | 40–48 px |
| Chips (Solid teak · COD · Free delivery) | Inter 600 in an outlined pill | 30–40 px | 26–34 px |
| Body / fact lines | Inter 400 | 40–44 px | 36–42 px |
| Handwritten note | Gochi Hand, with a drawn arrow | 40–48 px | 40–48 px |
| Handle `@nix_woods` | Inter 600, muted, top right | 26–28 px | 26–28 px |

- Headlines are sentence case and end with a full stop: "Follow the line.", "Light up the corner."
- Track large serif type tight (−0.02 em) with leading about 1.05.
- Keep each screen to 12 words or fewer, not counting the price block.
- Never centre a price block under a headline that is set ragged left. A price sits with its chips.

## 3. Layout and safe zone

- Use the 9:16 safe zone from `system/presets.json`: x 70–950, y 230–1500. Instagram covers the top
  ~220 px, the bottom ~400 px and the right ~130 px.
- On paid 9:16 keep text above y 1250, because Meta's CTA bar sits lower (V2's `SAFE_BOTTOM`).
- Never let type cross the lamp's lit channel. Split the words either side of it, at least 84 px from
  the channel's centre and 140 px on close-ups (V2's `split()`).
- The lamp is upright, centred or on a third, and never cropped through its teak block on an end card.
- The logo is `assets/logo.png`, about 520 px wide on a 9:16 end card. It is tinted cream on Dusk and
  sits on a soft shadow (blur 14, offset 4/8).

## 4. Timing

- **Frame rate: 30 fps** for every 9:16 piece made in Oct 2026. The older `make_reel.py` pipeline
  runs at 25. **ASK ME** before changing either.
- **Cuts land on the music grid.** Never cut by eye.
  - music6-corners: 71.8 bpm, beat 0.8357 s, first beat at 0.396 s.
  - music3-design: 99.4 bpm, beat 0.6036 s, drop at 10.752 s. The montage cuts on quarter-beats
    (0.151 s) and holds the end for 4 beats.
- **In:** the hook text is on screen and readable by 0.17 s (a 0.12 s smoothstep from 0.05 s). Other
  text fades over 0.25–0.30 s. The light comes on over 0.30 s, like an LED driver warming up, and is
  never an instant pop.
- **Hold:**
  - The hook holds 2 beats.
  - The end card holds at least 4 beats (V2: 2.4 s; V1: 2.5 s), and the price is readable for all of it.
  - The mosaic logo holds alone for 1.4 s.
- **Out:** a scene leaves on a cut, not a fade, unless it is going to the end card. The music fades
  out over the last 0.7–0.9 s. Nothing animates out after the end card lands.
- **Total length:**
  - Organic reels: 6–10 s.
  - Ads: 9.5–10 s, so the price is on screen before 10 s.

## 5. How things move

- **Easing:**
  - Smoothstep (`t²(3−2t)`) for fades and push-ins.
  - Expo-out for a line drawing itself.
  - No bounce, no overshoot, no springy scale-up of text. The brand is calm.
- **Camera:**
  - Slow push-ins: about 5% when the shot is a hold, up to about 25% when the move is the reveal
    (V1 pushes into the lit corner). Each push runs over the whole shot, never faster than 4 beats.
  - No whip pans, no shake, no spinning.
  - Rotation only to keep the lamp's channel vertical, and then the background comes from the
    unrotated source so a corner never shows black.
- **Pops are allowed in one place:** the mosaic grid tiles, which fill and swap as hard cuts every 3
  frames. That is the reference's grammar. Do not carry it into other pieces.
- **The glowing line** is the brand's moving element. It has a cream core (`#FFEED2`) and an amber halo
  (`#E8A24A` at about 55% alpha, plus a wide 25% halo). It travels or draws; it never blinks or strobes.
- **What makes it feel handmade:**
  - Real photos of the real lamp.
  - The Gochi Hand note with a drawn arrow.
  - Fine grain on flat grounds.

## 6. Texture and finish

- **Photo grade** (statics and carousels): RGB × [1.06, 1.0, 0.88], gamma 1.04.
- **Deep grade** (mosaic tiles): 20% desaturate, × 0.88, gamma 1.35, × [1.10, 1.0, 0.80], lift 0.02.
  **ASK ME:** which grade is the master for future reels.
- **Montage grade** (fast cuts between sources; V2 r2, `line_montage.py`):
  - Each source keeps 35% of its own colour and takes the rest from one warm tint (1.30, 1.0, 0.66).
  - The lit channel keeps a cream core.
  - Every frame lands on a mean luma of 0.31.
  - Never match sources with gray-world channel gains: tried 8 Oct, they turn phone close-ups neon.
- **Every cut in a sequence shares one colour balance.** Phone footage and generated rooms must not
  trade grey for orange on the cut. Measure it: per-frame R/G and B/G spread under 0.1 across the
  montage, and no more than a few cuts whose mean luma jumps more than 8/255.
- **Flat Dusk grounds:**
  - A soft vignette (1.08 − 0.35·r).
  - Gaussian grain σ 2.2, so gradients never band.
- **Text over photos** always sits on a cream wash or a dark gradient that fades with the text,
  including text on fast montages (V2 r1 lost its hook on bright close-ups without one). There are no
  boxes behind headlines. The exception is a price card: a rounded cream card at 236/255 alpha.
- **Encode:**
  - H.264, yuv420p, bt709, CRF 17, `+faststart`.
  - AAC 192k.
  - Covers are JPEG.

## 7. Five things our motion must never do

1. Never show the lamp leaning, or in cool white light. It stands upright and glows warm (2700–3000K).
2. Never put type across the lit channel, or in Instagram's UI zones.
3. Never bounce, spin, shake or strobe anything. That includes the light, which warms up and never flickers.
4. Never show a black rotation corner, a stretched photo, or the same photo twice on screen at once.
5. Never use a banned word, a made-up review or a delivery promise. Never use a generated frame without
   the AI label in paid placements.

## 8. One example done right: V1 "tubelight to teak" (9:16, 10.0 s, music6-corners)

| Beats | What happens |
|---|---|
| 0–2 | The scene is a corner lit by one cool tubelight. The hook ("Still lit by / one tubelight?", Fraunces 96, cream) sits on a top scrim and is up by 0.17 s. A slow 5% push-in runs under it. |
| 2 | The tubelight goes off on the beat, with a 0.06 s switch click under the music. The room drops to a blue-black. |
| 3–7 | The NixLine warms up over 0.30 s. "Not brighter. / Warmer." fades in 0.35 s later, over 0.25 s. The camera pushes 24% into the lit corner over 4 beats. The lamp stays upright and only the camera moves. |
| 7–9 | Cut to a Diwali dusk room. "Solid teak. / Made by hand." (Fraunces 88, set left) fades in over 0.25 s and out just before the end card. |
| 9–12 | The end card fades in over 0.30 s while the dusk push continues: `₹999` in amber Inter 600, `₹1,599` struck through, and the chips (Solid teak · COD · Free delivery). It holds to the end while the music fades over the last 0.7 s. |

The room scenes in V1 are generated, so its paid versions carry the AI label.

## 9. Checking your own frames

Before you show anything, pull frames at the hook (0.5 s), the middle, and the end card. Check them
against sections 1–7. Then run the `apple-design` and `review-animations` skills as a second pass.
Write what failed and what you fixed in the commit message.
