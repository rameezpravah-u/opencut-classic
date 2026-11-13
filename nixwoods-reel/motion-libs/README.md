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

**Brush and crisp shapes.** The sketch, the glow and the cord use the brush. The bar and its light line are
drawn as crisp p5 shapes. A p5.brush watercolour fill gave the bar a sawtooth edge in the 24 Oct test render (6 s,
decoded clean), and the lamp itself has to read true.

## Prompt libraries: look here before building a new motion piece

**Added 13 Nov 2026.** The owner sent @ux.robin's carousel "100+ Claude Motion Prompts"
(instagram.com/p/DfCG01WiB-Y, 28 Oct, 7 slides, all read) with "add these in your library for uses".
Each site below was opened on 13 Nov and checked. All five are galleries of public videos made with Claude, and
each video comes with the prompt or skill that made it.

| Site | What is there (13 Nov) | Access | Best for us |
|---|---|---|---|
| **skillry.dev/ai-videos** | 418 videos, each shown next to a remake of it | Prompts free, no account. Paid Pro is only for its own skills. | Motion graphics (229), 3D scenes (56), explainers |
| **prompt-motion.com** | 240 videos, sorted into **Prompt** (one video) and **Skill** (a whole style) | Free to browse and copy | Product UI, kinetic type, particles, charts, photos: closest to our code-built reels |
| **claudevideo.org** | 1,276 videos from 1,007 creators; 457 come with the prompt | Free to read. Unofficial, not run by Anthropic. | The **Product & Ads** filter, which is our category |
| **promptmotion.org** | 230 films, plus a library of 1,662 prompts | Appears open; Copy button on each | **Product launch** films and showreels |
| **jasonzhu.ai/en/prompts** | About 2.8K Claude works, 642 with prompts; updated daily | Has a sign-in, and it doesn't say what that unlocks | A wide sweep when the others have nothing |

**How to use them:**
1. **Search before building.** For a new motion idea (a pop-up, a reveal, kinetic type, a 3D turn), search the
   sites for the technique first: prompt-motion.com and claudevideo.org "Product & Ads", then promptmotion.org
   "Product launch". Open the video and watch every frame, the same as any reference.
2. **Take the technique, not the piece.** These are about *how* a move is built: the structure of the prompt, the
   timing, the library it uses. Rewrite it with the prompt template above, so the colours, type and timing come
   from MOTION.md and the copy from PRODUCT-FACTS.md.
3. **Run it with what we have.** Anything that needs a library goes through `vendor/` and `render.py`, so it renders
   offline, frame-exact, and on our beat grid. HyperFrames is the other option.
4. **Credit the creator.** On every site, the videos and prompts belong to their creators, and none gives a reuse
   licence. Never paste a creator's prompt word for word into anything published. Never use their footage,
   images or audio. When a build closely follows one video, the build's README names it with the creator and a
   link (claudevideo.org asks for this).
5. **Our rules still win.** These sites don't change any NixWoods rule: the AI label on generated content,
   product facts only from PRODUCT-FACTS.md, no faces without a release, and no banned words.

**The post itself (for formats):**
- **Slide layout:** a cover with a big two-tone headline and a lime highlight box; one slide per site, each a
  browser-window screenshot with the URL in large type underneath; a last slide saying "Want all the links? Comment
  Claude".
- **Results:** 632 likes and 441 comments. The comments came from the comment-to-DM ask.
- **For us:** that's a format we could use for a "5 ways to light a reading corner" save post. The DMs would be sent
  by the owner or an approved tool, never by me.

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
