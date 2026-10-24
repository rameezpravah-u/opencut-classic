# NixWoods on the Piccadilly Lights (9:16, 21.2 s, AI city + real lamps)

**The ask:** on 24 Oct the owner sent instagram.com/reel/De1nWfEjkAf with "Make this". It is Westwing × Victoria
Beckham's "Serving Style" film, a real out-of-home campaign on the curved Piccadilly Circus screen: 21.2 s, 80k
views.

**The owner's answers:**
- Piccadilly Circus, exact;
- Higgsfield, about 50 credits (47.5 spent);
- a brand film, no price.

## The reference, frame by frame (every frame viewed at 4 fps)

| Time | Shot |
|---|---|
| 0–2.6 s | Dusk drone over London; a round warm light pulses on the screen |
| 2.6–9.6 s | Dusk, street level under the curved screen; a man walks through the foreground. The film plays on the left and a black panel on the right reads "Serving Style / WESTWING \| VICTORIA BECKHAM / westwing.co.uk / The Dining Collection" |
| 9.6–14 s | Night, low angle: hands with a napkin, a glass, a table from above |
| 14–17 s | Night, wet pavement, silhouettes watching |
| 17–21.2 s | A night drone pull-out over the dark city, fading to dark |

## Ours

| Time | City shot (AI) | On the screen (our real footage) |
|---|---|---|
| 0–2.6 s | A: dusk drone, push-in | The Edison bedside lamp's bulb glowing, a hand on the dimmer |
| 2.6–7.6 s | B: dusk, street level, a man walks toward the camera | The NixLine's light line up close, a row of bars with one lit, then the Rubik's Cube in amber |
| 7.6–12.6 s | C: night, a slow tilt up to the screen | The Rubik's Cube, then a hand setting down the Luma Pillar, then a hand on the Edison dimmer |
| 12.6–17.0 s | D: night, wet pavement, silhouettes | The Rubik's Cube red, then amber |
| 17.0–21.2 s | E: night drone over the city | The Aurora wall wash, then the Luma lit; fading to dark over the last 0.8 s |

**The black panel**, in our words and MOTION.md fonts (Fraunces, Inter). It changes its lines once at 8 s, as the
reference's does:
- top: "Light, made by hand." → "nixwoods.com";
- middle: "NIXWOODS | SOLID WOOD LIGHTING";
- bottom: "nixwoods.com" → "The Lighting Collection".

**Copy rules:**
- No price.
- No "Discover now", which is a banned word for us.
- Claims are limited to solid wood and made by hand.

**Sound, all ours:** a synthesized city bed plus music1-aesthetic. The reference's audio is not used.

## How it is made
1. **City stills** (`gen/*-start.jpg`): five Nano Banana 2.1 2k stills (10 credits), generated with the screen a
   flat chroma green.
   - Real-brand signs were blurred in C (a Boots-style roundel, a blue sign, a bus sign) and D (a large lettered
     sign) before animating.
   - All faces are synthetic.
2. **City clips** (`gen/*.mp4`): Kling 3.0 Turbo image-to-video, 5 s, 720p (37.5 credits).
   - Every frame was viewed.
   - The screens stay green throughout.
   - D shows white specks on the screen after 4.5 s, so only 0–4.5 s is used.
   - The verdicts are in `system/presets.json` under brand `clip_status.picc_*`.
3. **`screen_film.py`:** the screen's own 1560x600 frame, about 2.6:1.
   - The left part is our real clips, warm-graded and cropped landscape. Sources: `floor-reels/src` nx00 and nx04,
     `rubik-reels/src/14-1.mp4`, `luma-styled/src`, and `lamps-under-3000/src`.
   - The right part is the type panel.
4. **`piccadilly_billboard.py`:** the compositor.
   - **Key:** the green is keyed per frame, and the screen's top and bottom edges are fitted as curves.
   - **Mapping:** the film is mapped column by column between those edges, so it follows the camera move and the
     screen's curve. Lamp posts and heads in front stay in front.
   - **Spill:** the green light on the street and the wet ground is shifted to the colour the screen is showing.
   - **Finish:** a soft bloom on the screen, a light warm grade and grain.
   - **Encode:** CRF 20.

## Before it goes up
- **AI:** the city is AI and the lamps are real. Instagram's "Made with AI" toggle must be on. As an ad, tick Meta's
  AI disclosure.
- **Location:** this is not a real ad buy. The caption is worded as an imagined takeover ("Imagine our lamps on the
  Piccadilly Lights"), not a claim that we advertised there.
- **Reach:** ads go to nixwoods.com only.

```bash
python3 brand-reels/piccadilly-billboard/piccadilly_billboard.py              # → out/NW-CREATIVE-VID-20261024-…-v1-AI.mp4
python3 brand-reels/piccadilly-billboard/piccadilly_billboard.py --still 5 15  # stills to check a change
python3 brand-reels/piccadilly-billboard/screen_film.py --sheet /tmp/screen.jpg # the screen film alone
```

<details><summary>Prompts (Higgsfield, 24 Oct)</summary>

Every still says: "the giant curved LED screen shows one flat, uniform, bright chroma-green colour (pure #00FF00)
… No logos, no brand names, no readable text on any sign or screen." Every clip says: "The giant curved screen stays
one flat, solid, uniform chroma-green colour the whole time, nothing appears on it … No logos, no text."

**Stills:**
- **A:** a dusk drone high above central London looking down at Piccadilly Circus, the curved corner building with
  its giant curved LED screen; overcast sky, the BT Tower on the horizon, red buses, shop lights.
- **B:** street level at dusk looking up at the screen, which fills the upper half. The lit arched arcade is below,
  and a crowd stands in the plaza; a man in a dark puffer jacket walks across the foreground.
- **C:** night, a low angle from the pavement up at the screen. The dark facade is above it, and the lit arcade and
  street lamps are below.
- **D:** night after rain, wet reflective paving, a crowd of silhouettes from behind looking up at the screen.
- **E:** a night drone very high over a dark London of warm lights, the screen small and the brightest thing in the
  frame.

**Clips:**
- **A:** a slow drone push-in.
- **B:** a near-static camera; the man walks toward the camera and out of frame.
- **C:** a slow tilt up; people, a red bus and taxis pass.
- **D:** static; the silhouettes shift, and a taxi passes.
- **E:** a slow pull-back, rising.

</details>
