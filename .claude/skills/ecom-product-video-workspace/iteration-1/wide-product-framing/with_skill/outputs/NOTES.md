# Double Arm Teak Pendant — 9:16 product reel

`reel.mp4` · 1080×1920 · 25 fps · 14.4 s · 3.4 MB · music, no voice-over
Built from the six PDP photographs in `nixwoods-reel/teak-reels/hf/`. **No generated frames** —
every pixel is real Shopify product photography, so there is nothing to disclose as AI.

---

## The problem this cut is built around

All six source images are **square (1:1)**. A 9:16 crop that fills the frame keeps
`9/16 = 56%` of the width. The Double Arm Teak is a **49-inch bar** — its length *is* the
product — so the obvious "crop to fill" treatment amputates the ends of the thing being sold in
every single shot.

Two measured facts shaped everything else:

1. **On a square source only the horizontal crop centre does anything.** The 9:16 window already
   spans the full height, so a vertical crop parameter is a no-op. (Worth knowing: the product's
   entry in `system/presets.json` carries `crop_cy: 0.45` for the dark hero, which has no effect
   at all on a square file. Not wrong, just inert.)
2. **The tightest sharp crop is already 1.5×.** Filling 1920 px of height from a 1254 px square
   is a 1.53× upscale before any camera move. Cropping *tighter* for scale variety costs
   resolution fast, so scale variety comes from alternating fill-the-frame and
   whole-image-on-a-mat instead.

So: four beats that deliberately withhold the length, then **one pull-back** where the whole four
feet lands over a dining table as the payoff. The hook asks a question the tight framing makes it
impossible to answer, which is the same move that hides the length.

## What I measured in the source images

`measure_sources.py` (included) prints this; re-run it whenever the PDP photography changes.

| file | px | mean lum | p5 | p95 | R/G/B | fill-frame | whole-image |
|---|---|---|---|---|---|---|---|
| sh00-marble-dining.jpg | 1254² | 186 | 68 | 234 | 198/183/168 | 1.53× | **0.86×** |
| sh01-underside-twin.jpg | 1254² | 141 | 69 | 203 | 168/135/101 | **1.53×** | 0.86× |
| sh02-strip-fluted.jpg | 595² | 199 | 69 | 235 | 217/195/177 | 3.23× ✗ | 1.82× |
| sh03-dark-two-lines.jpg | 1170² | **36** | **17** | 74 | 45/35/18 | **1.64×** | 0.92× ✗ |
| sh04-end-channels.webp | 493² | 145 | 42 | 181 | 169/138/114 | 3.89× ✗ | 2.19× ⚠ |
| sh05-canopy-cables.jpg | 819² | 191 | 83 | 225 | 206/188/169 | 2.34× ✗ | **1.32×** |

Bold = the mode each shot actually uses. What the numbers decided:

- **sh03 is the only genuinely dark frame** (mean 36, darkest 5% at 17). It must fill the frame:
  put it on a blurred backing and the backing is black too, and the fixture becomes a thin lit
  band in an empty rectangle. It also has no headroom for a shadow crush, so it gets the only
  per-shot tone move in the cut — a gamma 0.86 **lift**, not a crush, so the teak body separates
  from the wall behind it.
- **sh02 and sh04 are small files.** At fill-frame they are 3.2× and 3.9× upscales — visibly soft
  on a phone. sh04 survives as a whole-image shot at 2.19× because it is a shallow-depth macro
  on a 1.9 s beat; that is the one softness compromise in the reel and it is deliberate.
- **sh05 at fill-frame is 2.34×**, so it also goes in whole-image at 1.32×.
- **sh00 contains at 0.86× — a downscale.** The payoff shot is the sharpest frame in the cut,
  which is the right way round.

**sh02-strip-fluted is not in the reel.** Two reasons: the 3.2×/1.8× softness, and more
importantly the product's own `ref/REFERENCE.md` says a cut that shows only one strip is wrong —
from that dead-on distance the two channels merge into a single line. It is a nice photograph
that quietly contradicts the thing the reel is claiming.

**One deliberate design choice worth flagging:** the whole-image shots sit on a backing dimmed to
42% brightness rather than the usual light touch. Undimmed, a blurred copy of this bright studio
photography lands near 150 luma and white type on it is unreadable. At 42% the surround reads as
a dark mat, the sharp subject pops off it, and the band below the image is clean enough to carry
a line of copy inside the safe zone. That is how the payoff shot gets both the whole 49 inches
*and* legible type.

## Shot list

| # | t | source | framing | camera | on screen |
|---|---|---|---|---|---|
| 1 | 0.0–3.0 | sh03 dark | fill frame, window centred at 40%→48% of width, 1.81× | push 1.00→1.10 | **"How many lines do you see?"** |
| 2 | 3.0–6.0 | sh01 underside | fill frame, window at 64%→56%, 1.65× | pull 1.08→1.00 | "Two. Cut into one piece of teak." |
| 3 | 6.0–7.9 | sh04 end cap | whole image, centred, 2.19× | push 1.00→1.10 | — (let the detail read) |
| 4 | 7.9–10.2 | sh05 canopy | whole image, raised, 1.32× | settle 1.06→1.00 | "One teak canopy. Two cables." |
| 5 | 10.2–14.0 | sh00 dining | whole image, raised, 0.86× | **pull back 1.10→1.00** | "49 inches, right over the table." |
| 6 | 14.0–14.4 | end card | — | — | logo · "Two lines. One piece of teak." · solid teak · 3000K · 49 in · nixwoods.com |

Shots 1 and 2 use opposite ends of the bar (window at 40% vs 64% of the source width) so the two
tight beats do not read as the same frame twice. 0.4 s dissolves throughout; the end card fades.
Audio is `teak-reels/audio/music3-design.mp3` at −5 dB with a 0.5 s fade in and 1.8 s out.

## The hook

**"How many lines do you see?"** — scored 9/12 by `system/hooks.py`, passing all three gates
(gap / truth / pull), families: question, curiosity, POV. It is on screen at 0.12 s and holds
2.5 s, against the house rule of ≤0.3 s and ≥1.2 s.

It earns its place structurally, not just verbally: the tight crop that answers the framing
problem is also what makes the question hard to answer, and shot 2 pays it off. Rejected
alternatives — "Four feet of solid teak" (4/12: states a category, opens nothing) and "Count the
lines" (4/12: an instruction with no gap).

## Claims

Everything on screen is on the PDP or in `ref/REFERENCE.md`: 49 inches, solid teak, 3000K, two
channels, one canopy, two cables. **I wrote "49 inches" rather than "four feet"** — the fixture is
49 in, which is 4 ft 1 in. "Four foot" is fine in conversation and in the brief; on screen next to
a product page it is a spec, and the spec is 49. No price, no dispatch claim, no testimonial.

## Checks run on the finished file

`check_render.py reel.mp4` → **PASS**

- duration 14.40 s (matches the shot list — nothing read past the end of a source and truncated)
- 3.43 MB against a 25 MB ceiling
- last frame present and non-blank: mean luma 15.9, 2.1% of pixels lit — the end card is there
- warm-light check at 25/50/75%: R>G>B at all three (178/144/111, 154/141/127, 143/131/121), so
  nothing in the grade has gone magenta or cold
- text: no contrast plates anywhere, drop shadow only — a plate over the dark hook frame reads as
  a smudge. All four text layers sit inside the safe zone (y 230–1500, x 70–950).
- I pulled eight frames across the cut and looked at them. That caught one real fault: shot 2's
  copy was set at y=1290 and its second line crossed the lit channel. Moved to y=1430, onto the
  fluted wall below the bar. Re-rendered.

## How it was built, and one thing that did not work

The repo's `system/make_reel.py` can express this cut — the brief is included as
`teak-four-foot.json` and it lints clean, scores the hook and passes pre-flight. But its still
path supersamples to 2160×3840 and runs the whole-image composite through a large-sigma blur at
that size. On this machine it rendered at **0.4 fps**; a 14 s cut is ~15 minutes and it was killed
twice before finishing.

So the delivered file comes from `render_reel.py`, which builds the frames in PIL at 1080×1920 and
streams them straight into one ffmpeg encode: **67 seconds**. It reuses the repo's type, palette,
logo and safe zone (`reelkit`, `presets.json`) so the output still looks like a NixWoods reel. Two
details worth keeping if anyone extends it: the backing blur is done on a ⅙-scale copy and
upscaled (identical look, ~40× cheaper), and frames are generated lazily — holding a whole reel in
memory costs ~2.8 GB and is what got the first attempt OOM-adjacent.

## Files

| file | what it is |
|---|---|
| `reel.mp4` | the deliverable |
| `render_reel.py` | the renderer; the shot list lives at the top as a plain table of dicts |
| `measure_sources.py` | source measurement — run before choosing any framing |
| `check_render.py` | post-render guards (duration, end card, colour, size) |
| `build.sh` | measure → render → check, in order |
| `teak-four-foot.json` | the same cut as a brief for `system/make_reel.py`, for whoever prefers that route |
| `render.log` | the last render's per-shot report |

## Not done

- Nothing committed to git, as instructed.
- Not filed under the NixWoods OS contract (naming, `ASSET_REGISTRY.md` row, index rebuild,
  handoff line). If this is going to a real consumer rather than staying in the workspace, that
  is the next step — `system/file_for_os.py --date 20260923` does the naming.
- No 25–30 s ad cut. The pre-flight in the repo prefers that length for paid; this is a 14 s
  organic-first cut. Stretching it means holding each beat longer, not adding shots — there are
  only five usable frames in the set.
