# Floating light shelf — vertical reel

**`reel.mp4`** · 1080×1920 · 12.33 s · 25 fps · H.264 + AAC · 7.6 MB · cut 2026-09-23

Dark, quiet, workshop-to-wall. Built from your three phone clips, nothing generated for this cut
except the one closing frame noted under *Disclosure*.

---

## The hook

> **"watch this plank turn into a wall light."**

On screen from 0.12 s, holds 1.5 s.

Scored with the system's Gap / Truth / Pull gates (`system/hooks.py`) against ten candidates:

| line | score | gates |
|---|---|---|
| **watch this plank turn into a wall light.** | **11/12** | gap ✓ truth ✓ pull ✓ |
| three of these, one wall, no lamp. | 11/12 | ✓✓✓ — but it gives the payoff away in frame 1 |
| your wall does not need a lamp. | 10/12 | ✓✓✓ |
| this is not a shelf. watch. | 9/12 | ✓✓✓ |
| wait for it to light up. *(the line on the earlier S1 cut)* | 8/12 | gap ✓ truth ✓ **pull ✗** |
| wait for the line. | 7/12 | pull ✗ |

The winner names exactly what the first three shots are withholding — the plank is dark and
unlit for 3.5 s — and the opening frame (a hand and a cloth on a black plank) makes the promise
credible. The two 11/12 lines tied on score; I took the one that does *not* show the ending.

Second line **"there it is."** lands on the first lit frame (3.48 s). Third, **"three on one
wall."**, lands on the closing shot. Nine words, six words, four words — nothing over the
12-words-a-screen rule, no banned words, no price or size claim (the Shopify handle for this
particular dark rosewood shelf is still unconfirmed, so there is nothing to claim from).

## Shot list

Beat = 1.16 s. Hard cuts throughout — a dissolve at this pace reads as a mistake.

| # | t | clip | in | dur | camera | what you see |
|---|---|---|---|---|---|---|
| 1 | 0.00 | IMG_7745 | 0.30 | 1.74 | pull | hand + cloth on the black plank · **hook** |
| 2 | 1.74 | IMG_7745 | 2.10 | 1.16 | push hard | craftsman working down the length |
| 3 | 2.90 | IMG_7745 | 4.70 | 0.58 | hold | the plank alone, grain and bullnose end |
| 4 | 3.48 | IMG_7747 | 0.20 | 1.16 | push | **first lit frame** · "there it is." · whoosh on the cut |
| 5 | 4.64 | IMG_7749 | 0.15 | 0.87 | pull | tight on one warm channel |
| 6 | 5.51 | IMG_7747 | 1.60 | 0.58 | push hard | three lines leaning on the wall |
| 7 | 6.09 | IMG_7747 | 2.30 | 0.58 | drift back | same, lateral drift |
| 8 | 6.67 | IMG_7749 | 1.60 | 1.45 | pull | pull back to all three, lit |
| 9 | 8.12 | still | — | 2.61 | push | three installed on a wall · "three on one wall." · whoosh |
| 10 | 10.33 | end card | — | 2.00 | fade | logo · *made by hand. lit by a line.* · nixwoods.com (0.4 s fade over the tail of shot 9) |

Arc: **make → light → three → wall.** The product is withheld for the first three shots on
purpose; that withholding is what the hook sells.

## What I measured

- **Sources are already tonemapped.** All three files in `src/` are 1080×1920 SDR bt709 H.264,
  not the original HEVC 10-bit HLG off the phone, so no tonemap pass was needed. Durations:
  7745 = 5.93 s, 7747 = 3.10 s, 7749 = 3.27 s. **12.3 s of usable source in total** — that is the
  real constraint on length, and why two clips get revisited at different seconds and crops.
- **Luminance, per clip** (1 fps sample, greyscale): 7745 mean 116 / p5 32 / p95 201 · 7747 mean
  131 / p5 60 / p95 244 · 7749 mean 139 / p5 55 / p95 239. That p5 of 32 is why I did **not** use
  the house `noir` grade (brightness −0.30, contrast 1.50) — it was tuned on pendant footage whose
  darkest 5 % sits at 122, and on this workshop footage it buries the craftsman and the plank in
  solid black. The grade here lifts the toe with a curve (`0/0.05 0.3/0.27 0.75/0.80 1/1`) and gets
  the dark look from contrast 1.25 and a vignette instead.
- **Colour, after the grade** — R > G > B on every sampled frame (0.6 s, 3.9 s, 6.5 s, 10.0 s), so
  the warm LED reads warm and there is no magenta or cool cast. Graded frames land at mean
  luminance 48–71 with p95 ≈ 160, i.e. dark but with the light line still well short of clipping.
- **No truncation.** The system refuses a shot that would read past the end of its source; the
  render then decodes to **308 frames = 12.32 s**, matching the 12.33 s the container reports. (An
  earlier cut of this product shipped 1.4 s short because ffmpeg ran out of frames on the last shot
  and dropped the end card silently — the container still reported full length.)
- **End card present** — last frame extracted and checked, logo + line + URL.
- **Audio** — −14.0 LUFS integrated, true peak −0.6 dBFS. That is the Instagram/TikTok target, so
  nothing will be turned down on upload. Track: `music7-noir.mp3` at −3 dB, two whooshes 0.2 s
  before the cut into the lit shot and the cut into the wall.
- **Size** — 7.6 MB, well under the repo's ~21 MB re-encode ceiling.
- **Text on a dark grade** — contrast boxes switched off on all three lines; they read as grey
  smudges over this footage. The type carries a shadow instead. All three cues sit inside the
  safe zone (checked by the runner, not by eye).

`verify.sh` in this folder re-runs every one of those checks against `reel.mp4`.

## Disclosure

**One frame is AI-generated**: the closing shot (shot 9), three shelves installed on a wall. Your
phone clips never leave the workshop, so without it the reel ends with the product lying on a
floor and a viewer never sees what it actually is or where it goes. That frame was generated
earlier from your own end-cap photo plus a frame of the finished shelves, and is marked approved
in `presets.json` — dark plank, bullnose ends, one warm line inset in the top face, which is the
real product.

- Organic post: a line in the caption ("last shot is a render") covers it.
- **Paid placement on Meta: tick the AI disclosure.**
- Don't caption that shot as a photograph of an install.

Nothing else was generated, no spec, price, dispatch time or material claim is stated anywhere in
the cut, and the "turns into a light" promise is carried by footage of the thing actually lit.

## Files

| file | what |
|---|---|
| `reel.mp4` | the cut — 1080×1920, 12.33 s, with music |
| `reel-cover.jpg` | cover frame (t = 6.2 s, the three warm lines, no workshop clutter) |
| `reel-contact-sheet.jpg` | 15-frame sheet for a quick look at framing and text placement |
| `reel-timeline.json` | every shot, cue, audio item and check result from the build |
| `S2-shelf-glow.json` | the brief this was built from |
| `verify.sh` | the post-render checks above, re-runnable |
| `build/` | render intermediates (text layers, end card, log, filter graph) |

## Re-render or tweak

The brief drives everything; it is also copied to `nixwoods-reel/system/briefs/S2-shelf-glow.json`.

```bash
cd /home/user/opencut-classic/nixwoods-reel
python3 system/make_reel.py system/briefs/S2-shelf-glow.json \
        --out <dir> --audio music --no-sheet        # ~6 min on 4 cores
```

Add `--audio both` for a music-free version to drop trending audio over in-app. Worth knowing if
you re-cut: `minterpolate` slow-motion (the `slow` key) roughly doubles render time on this box —
I dropped it from shot 8 for that reason and the pull reads fine at speed.

## Possible next cuts, same footage

- **A 6-second version** — shots 1, 4, 9 only, hook and payoff. Better for paid, where the first
  two seconds are all you get.
- **A no-text version** for reposting with a different caption or a voice-over.
- **"three of these, one wall, no lamp."** as the hook on a variant — it also scored 11/12 and
  gives you a genuine A/B against this one: withheld payoff vs. stated payoff.
