# motion-libs: open-source motion libraries, on our beat grid, in our brand

**The ask:** on 23 Oct the owner sent Ian Tang's "Claude Motion Tips" (instagram.com/reel/DeWzv0mMi8_) with "Build
these in your capacity". This folder is the build. Each tip maps to something here that runs in a cloud session,
offline, with nothing to sign up for.

| Tip | What it says | Where it lives here |
|---|---|---|
| 1. Use open-source effects | Hand-drawn and physical looks from free libraries, not stock templates | `vendor/`, below, and `templates/` |
| 2. Direct the timing | Use your own music and put reveals on its downbeats | `beats.py` measures beats and downbeats; `render.py --beats` hands them to the page as `window.BEATS` |
| 3. A brand file | Give the model your palette and type roles so every piece matches | `../MOTION.md` (colours, type, timing, motion) and `../brand.md`; prompt template below |
| 4. Use your own work as material | Frame your real product and footage instead of generic shapes | Templates draw the real product (the NixLine's bar, light line and cord); cut-outs and our photos come from `source/` and the product CDN |
| 5. Share the prompt | Keep a reusable prompt so results repeat | The prompt template below |

## The libraries (`vendor/`, pinned, licences alongside)

All are local files, because the render browser cannot reach CDNs (FREE-TOOLS.md, HyperFrames notes). Each version
was published at least three weeks before it was vendored.

| Library | Version | Licence | Good for |
|---|---|---|---|
| p5.js | 2.3.4 | LGPL-2.1 | the canvas and drawing loop |
| p5.brush | 2.2.3 | MIT | pencil, pen and watercolour strokes and fills (`brush.line`, `brush.spline`, `brush.polygon`, `fillBleed`, `fillTexture`) |
| Rough.js | 4.6.6 | MIT | sketchy, hand-drawn shapes and arrows |
| Matter.js | 0.20.0 | MIT | 2D physics: lamps dropping, stacking, tipping |
| Anime.js | 4.5.0 | MIT | timelines and easing for DOM and SVG |
| PixiJS | 8.22.0 | MIT | fast 2D WebGL sprites |
| pixi-filters | 6.1.5 | MIT | glow, bloom, grain and blur filters for PixiJS |

## Tools

**`beats.py`** finds where the beats and downbeats fall in a music track:

```bash
python3 motion-libs/beats.py brand-reels/audio/music3-design.mp3 --out beats.json
```

- It prints `bpm`, `beat`, `first_beat`, `beats`, `downbeats` and `strong`, all in seconds.
- `strong` are the beats with the loudest onsets, for accents.
- It uses `system/beatgrid.py` for the tempo. Measured on music3-design: 99.38 bpm, downbeats at 1.068 s and 3.483 s.

**`render.py`** renders an HTML sketch to video, frame by frame:

```bash
python3 motion-libs/render.py motion-libs/templates/brush-reveal/index.html out.mp4 --dur 6 \
    --audio brand-reels/audio/music3-design.mp3 --beats beats.json
```

- **The page contract:** the page defines `window.ready` (a Promise) and `window.renderAt(t)`.
  - `renderAt` repaints the whole frame for time `t` from a fixed seed.
  - Nothing may depend on the clock or on the previous frame (seek-safe).
- **Browser:** it uses the pre-installed Chromium (`/opt/pw-browsers/chromium`, WebGL through SwiftShader).
- **Output:** H.264, CRF 17, yuv420p, with the audio faded out.
- **Stills:** `--still 1.5 3.0` writes PNG stills instead, to check a change.
- **Speed:** WebGL brush pages render slowly in software, at a few frames a second. Render in the background.

## Templates

**`templates/brush-reveal/`** paints the NixLine in on the beat. It runs at 9:16 on a paper ground made by
`make_paper.py`.

| When | What happens |
|---|---|
| Before downbeat 1 | A pencil outline of the bar draws itself. |
| Downbeat 1 | An amber watercolour glow blooms behind it. |
| A beat later | The honey-teak wash fills the bar from the foot up. |
| Two beats in | The light line runs up its face. |
| After that | The cord is drawn in pen. |
| Downbeat 2 | The title lands: "NixLine / floor lamp · solid teak · ₹999". |
| After the title | NIXWOODS.COM appears. |

All colours are MOTION.md tokens, and the claims are only the ones on the product page.

## Prompt template (tips 3 and 5)

Paste this, then fill in the brackets:

> Build a [length] s [9:16 / 4:5] motion piece for NixWoods in `motion-libs/templates/<name>/index.html`, using
> [p5.brush / Rough.js / Matter.js / PixiJS] from `motion-libs/vendor/`.
> - **Brand first:** read `nixwoods-reel/MOTION.md` in full. Every colour, font and timing comes from it. Use Paper
>   or Dusk grounds, Fraunces for the voice, Inter for the facts, and ease-out moves with no bounce.
> - **Subject:** the real [product], identified with `PRODUCT-ID.md`. Draw what the product actually is:
>   [its tell, e.g. "one honey-teak bar, frosted light line down its face, no base, leaning, cord at the foot"].
> - **Timing:** run `motion-libs/beats.py` on [track]. Land [the reveal] on downbeat 1 and [the title] on downbeat
>   2, from `window.BEATS`.
> - **Copy:** [headline, 12 words or fewer]. Use only claims from `PRODUCT-FACTS.md` (price, wood). No banned words.
> - **Contract:** `renderAt(t)` repaints from a fixed seed, so it is seek-safe. Check stills with `render.py
>   --still`, compare them with MOTION.md, fix what fails, then render.

Renders from these templates are drafts. A render that goes into the repo is registered in the OS like any other
(D-086).
