# Luma Pillar: two reels from the owner's styling clip (13 Oct 2026)

**Source:** `src/luma-styling-20260331.mov` (27.6 s, 480×848 phone export, committed).
- **What happens in it:** hands style a black dresser (a coral and marigold mat, books, a candle lit with a match).
  Then the pale-wood pillar lamp is set down, it is lit, and smoke drifts through its glow.
- **Product:** the owner confirmed it is the **Luma Pillar** (Shopify `luma-pillar-ambient-lamp`, ₹1,599 live
  13 Oct).
- **Faces:** a woman's head enters the right edge at 6.4–8.8 s and 12–14 s. No shot uses those spans.
- **Resolution:** the source is 480 px wide, so shots are upscaled. A full-resolution original would sharpen a v2.

`luma_shots.py` cuts every shot once:
- motion-compensated slow motion;
- cover-scaled to 1080×1920;
- lit shots straightened.

Shots are cached in `work/`, which is untracked.

## E1: "Your corner is missing one thing." (`luma_colour.py`)
Owner brief: "Free hand go crazy, aesthetic, sellable, fomo created, play with colors, be creative."

- **Colour off, colour on.**
  - While the corner is styled and the lamp is off, each step is a bold duotone in a colour taken from the props on
    the dresser: coral, marigold, green, plum. Colour-block wipes carry the cuts. Labels read "mat ✓", "books ✓",
    "candle ✓", "still… something's off".
  - On the beat, the lamp switches on with a warm bloom, and true colour floods back.
  - The lamp's light is never recoloured.
- **Timing:** music1-aesthetic, 17 beats = 15.0 s.
- **End card:** a Dusk ground, a colour strip, the logo, "Luma Pillar", "₹1,599", "₹100 off prepaid · code FLY100",
  and nixwoods.com.
- **Colour exception:** the colours outside MOTION.md's palette are the owner's ask ("play with colors"). They come
  only from the clip's own props.

## E2: the method reel (`../../hyperframes/projects/luma-method/`)
**Method:** after instagram.com/p/DeZh4eFAAGV ("how Claude made a 2M-view video"):
- brand files in;
- the hook written first;
- an ElevenLabs voice;
- every word synced on screen;
- the motion described in a HyperFrames composition rather than keyframed;
- then sound and render.

**Voice:**
- ElevenLabs "Koyal – Relatable Lifestyle Creator", Indian English.
- One take, 231 credits, owner-approved.
- Saved as `src/luma-vo-koyal-elevenlabs.mp3`.
- The voice is synthetic; the caption says so.

**Script:**
> "Books. Candle. Cute mat. And it still looks… off? That's because it's missing light at eye level. Meet the Luma
> Pillar. Solid wood, a soft warm glow, and grain no one else will have. Just fifteen ninety-nine. On nixwoods dot com."

Every claim is on the product page: solid wood; a soft, warm, diffused LED; each grain its own.

**Word timing:**
- A local faster-whisper pass (`src/luma-vo-words.json`, free).
- Phrase starts are snapped to the voice's own pauses.
- Each word pops on its onset over a colour block for the key words.

**Cuts:** `prep.py` cuts the footage bed to the voice:
- "off?" lands on the lamp set down unlit;
- "light" lands on it switching on;
- "grain no one else will have" lands on the close-up.

**Duration:** 22.0 s, rendered with the pinned HyperFrames CLI (`hyperframes/hf.sh render`).

## FOMO
The owner asked what works. Our own top posts (Vibiz analytics, last 90 days) are short proof lines over the product
lit: "It arrives in one piece." (154 shares, 175 saves) and "Lit before it leaves the bench."

Both reels use only levers that are true today:
- **Price:** an impulse price under ₹1,600.
- **Grain:** "no two grains alike" (the product page: each piece one of a kind).
- **Prepaid code:** FLY100, on the product page. Re-check it is still live before posting.

**Not used:**
- no stock count, deadline or "festive price";
- no COD claim (confirmed for the NixLine only).

## Files in `out/`
| File | Length | Audio | Use |
|---|---|---|---|
| `…-corner-missing-one-thing-v1.mp4` | 15.0 s | music1-aesthetic | organic and ads |
| `…-voiceover-method-v1.mp4` | 22.0 s | voice + music1 (ducked) | organic and ads |

Each reel also has a `-cover.jpg` and a `-sheet.jpg`.
