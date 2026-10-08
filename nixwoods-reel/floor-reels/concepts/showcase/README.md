# NixLine — "Follow the line" (HyperFrames, 8 Oct 2026)

The first reel made with the new motion setup: MOTION.md, the HyperFrames renderer, and the critique
skills. 9:16, 10.03 s, 30 fps, 12 beats of music6-corners.

- **Source:** `hyperframes/projects/nixline-showcase/` (`index.html`; `prep.py` makes the photo asset).
- **Render:** `cd hyperframes/projects/nixline-showcase && ../../hf.sh render --quality delivery --output <out.mp4>`.
  It takes 30 s here.
- **Real photo only:** the 5 Aug shoot, AC4I9815. Nothing is generated, so no AI label is needed.

| Beat | What happens | What it shows the setup can do |
|---|---|---|
| 0 | Cool tubelight-grey ground. "Follow the line." rises word by word through a mask. A glowing line starts drawing. | Masked kinetic type; SVG path draw with MOTION.md's cream-core, amber-halo glow |
| 0–6 | The ground warms from cool grey to cream as the line travels. | Colour tweens on the beat grid |
| 2 | "Solid Indian teak. / No MDF. No veneer." | Copy swaps on the beat |
| 4 | The line turns and rises 30 inches. A counter and a tick per inch keep exact pace with it. Beside it: 2700–3000K, with a scale marker sliding to warm. | Three elements on one curve, so they always agree |
| 6 | **Match cut.** The real room wipes open from the line, which lands exactly on the lamp's lit channel (measured: x 535–552, y 413–1603, 0.82°). A slow 5% push follows, centred on the channel. | Pixel-exact match to a real photo; clip-path wipe; push-in |
| 8 | The room dims to an oval of light around the lamp. The headline turns cream and "warm" turns amber. Price, chips and nixwoods.com come in on a 60 ms stagger and hold for 4 beats. | The Dusk end card from MOTION.md |

**Self-check before showing.** `hyperframes check` passed with 40/40 text-contrast checks. These were
caught and fixed on the way:
- The line was off-screen for the first second.
- The line was too pale on the light ground, so the glow was raised to the carousel's strength.
- The end-card dim left a light column running the full height of the frame; it is now an oval.
- GSAP rounds pixel values, so a dash offset normalised to 0–1 snapped instead of drawing. It now uses
  the path's real length.
- A rolling odometer drifted out of sync. It was replaced by a counter that is placed per inch.
- The accent word was low-contrast on the grey wall before the dim.

The 5 remaining lint warnings ask for each scene to be split into a sub-composition. That is a
Studio-editing convenience and does not affect the render.
