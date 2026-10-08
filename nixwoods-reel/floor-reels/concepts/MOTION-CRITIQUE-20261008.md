# Motion critique — V1, V2, mosaic (8 Oct 2026)

**Method.** I pulled frames at fixed times from each reel and measured every frame's mean luma, R/G
and B/G at 135×240. I judged them against `MOTION.md`, the `apple-design` motion rules (no strobing,
no abrupt brightness jumps, justified motion) and the `review-animations` standards (ease-out on
entrances, staggered groups, cohesion, delete what has no purpose).

## Findings

| Reel | Before | After | Why |
|---|---|---|---|
| V2 | Each source graded for exposure only. Phone footage stays grey (R/G 1.3, B/G 0.7); generated rooms stay deep orange (R/G 2.3, B/G 0.2). They swap about 3 times a second: 21 of 48 cuts jump more than 8/255 in luma, R/G spread 0.41. | **Fixed in r2.** Each source keeps 35% of its colour and takes the rest from one warm tint, and every frame lands on mean luma 0.31. Now 4 of 48 cuts jump, R/G spread 0.09, B/G spread 0.07, luma spread 2.8 (was 6.1). | Colour-temperature pumping reads as flicker. `apple-design` warns against strobing and abrupt brightness jumps, and `review-animations` puts cohesion first. "Count the cuts" should be a game, not a strain. |
| V2 | Hook ("Count / the cuts.") and mark ("one line / of light.") on the raw frame. On the bright close-ups (0.3 s, 1.5 s, 2.3 s) cream text sits on cream wall. | **Fixed in r2.** A top dark scrim (0.55, 26% of the height) behind the words on every montage frame. | MOTION.md 6: text over photos sits on a gradient. The hook is the most-watched second of an ad. |
| V2 | First fix tried: gray-world channel gains toward a warm target. | Rejected before commit. The phone close-ups went neon orange-red. | Recorded in MOTION.md so nobody repeats it. |
| V1 | 1.67–2.5 s: the room cuts from luma 102 to 9 and holds near-black for a beat. | **No change, flagged.** | This is the brightest-to-darkest jump in the three reels, and `apple-design` advises easing such changes. Here it *is* the story (the tubelight switching off) and it lands on the beat with a click. **ASK ME:** if the 3-second hold rate on V1 is weak, try lifting the dark frame to luma ~20 so the room's outline stays visible. |
| V1 | 7.3–7.8 s: "Solid teak. / Made by hand." fades out, then the end card fades in at the same spot. | No change. | Sequential, not overlapping, so it reads cleanly frame by frame. A blur bridge isn't needed. |
| Mosaic | The URL "nixwoods.com" is fully visible for only about 1.1 s (5.27–6.4 s) before the reel loops. | No change, flagged. | Within the reference's grammar and the loop shows it again. If the mosaic is ever used as an ad, hold the end 1 s longer. |
| Mosaic | Hard tile pops every 3 frames, and the logo lands with no fade. | No change. | This is the reference's grammar: deliberate, on the beat, and limited to this piece (MOTION.md 5). |
| HyperFrames starter | Price, accent word and URL all in amber; the headline 30 px off the line's centre; the line drawn with a CSS `scaleY(0)` that GSAP overwrote (caught by `hyperframes check`). | Fixed before commit: URL in cream, headline centred, line owned by `fromTo`. | MOTION.md 1: amber at most twice a frame. The self-check rule in CLAUDE.md worked on its first run. |

## Verdict

- **V2: Block → Approve as r2.** The feel-breaking colour flicker is gone and the text is readable.
  The r1 files stay as they were: they are what is scheduled for Sat 10 Oct and inside the paused
  Meta ads V2A/V2B.
  - Rameez approved the swap (8 Oct).
  - **Saturday's Metricool post now carries r2** (no-hook version, commit `5417b02`). Updating the
    post changed its id from 390211045 to **391213873** (uuid unchanged, -975991933635575715).
    Metricool's re-hosted file is byte-identical to the repo's r2 (md5 5004f788…).
  - **V2A/V2B in Meta: not swapped yet.** This session's safety check blocked the r2 video upload.
    The ads still carry r1.
- **V1: Approve.** One flagged judgement call (the black beat).
- **Mosaic: Approve.** One flagged note for paid use.

Files:
- `concepts/meta-set/NX-META-V2-one-line-9x16-r2-hookA.mp4`
- `concepts/meta-set/NX-META-V2-one-line-9x16-r2-hookB.mp4`
- `concepts/meta-set/*-r2-*-timeline.json`

Generated rooms are still in the mix, so the AI label is still needed.
