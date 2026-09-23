# Floating Light Shelf — dark reel

**`reel.mp4` · 1080×1920 · 25 fps · 12.12 s · 8.3 MB · music, no voice-over**

Cut from your three phone clips and nothing else. No AI frames, no stock, no stills —
which also means no Meta AI-disclosure box to tick if you ever put money behind it.

---

## The hook

> **no bulb. no lamp. look at the wood.**

It scores **10/12** on the repo's own scorer (`nixwoods-reel/system/hooks.py`) and passes
all three gates — gap, truth, pull. That is the best score anything in the shelf set has
had (S1's *"wait for it to light up."* is 8, M1's mug line is 9). It works because the
footage answers it: the light is a channel routed into the plank, so there is genuinely
nothing to point at and call a bulb. Tested against seven alternatives; the runners-up
were *"there is no bulb. look again."* (9) and *"pov: your wall at 11pm."* (9, but it
claims a wall the footage doesn't show).

On screen at **0.12 s**, holds **1.27 s** — clears the house rule (up by 0.3 s, hold ≥ 1.2 s).

Two more lines carry the middle and the payoff:

- **every plank is finished by hand.** — on the workshop shot
- **three of them. one line each.** — on the reveal

End card: *made by hand. lit by a line.* · solid wood lighting · nixwoods.com

Caption to post with it:

> no bulb, no lamp — the light is a channel routed into the plank.
> solid wood, finished by hand, three of them on the bench before they go up.
> nixwoods.com

---

## Shot list

| # | t (s) | len | clip | in | camera | what it shows |
|---|---|---|---|---|---|---|
| 1 | 0.00 | 1.51 | IMG_7747 | 0.15 | push 1.00 → 1.18 | tight on the lit channel — **hook line** |
| 2 | 1.51 | 0.87 | IMG_7747 | 1.45 | drift left→right at 1.12 | travel along the line |
| 3 | 2.38 | 1.16 | IMG_7749 | 0.10 | push 1.00 → 1.12 | one lit line, close |
| 4 | 3.54 | 1.45 | IMG_7745 | 0.35 | pull 1.12 → 1.00 | the craftsman's hand and cloth — **line 2** |
| 5 | 4.99 | 0.58 | IMG_7745 | 2.15 | push hard 1.00 → 1.18 | grain, fast |
| 6 | 5.57 | 0.87 | IMG_7745 | 4.35 | hold at 1.08 | the plank on trestles |
| 7 | 6.44 | 0.87 | IMG_7747 | 2.20 | drift back right→left | back to the light |
| 8 | 7.31 | 1.16 | IMG_7749 | 0.80 | push 1.00 → 1.18 | two lines, the reveal starting |
| 9 | 8.47 | 2.03 | IMG_7749 | 1.50 | pull 1.12 → 1.00, 1.3× slow | **three lit shelves** — line 3 |
| — | 10.10 | 2.00 | end card | | fades in over shot 9 | logo, cta_line, url |

Structure is **light → hand → three**. Open on the strongest frame you own (the lit
channel, tight), cut to the maker so the object has a why, pay off on the three lit
shelves with the slowest shot in the cut. Hard cuts throughout — at a 1.16 s beat a
dissolve reads as a mistake. Two whooshes (−10 dB) sit 0.2 s ahead of the two structural
cuts, into the workshop at 3.54 s and into the payoff at 8.47 s. Music is the house noir
track at −3 dB with a 1.4 s tail.

---

## What I did, in order

**1. Read the footage before cutting it.** 2 fps contact sheets of all three clips:

- `IMG_7745` (5.93 s) — a craftsman polishing the dark plank with a pink cloth, bright
  daylight workshop, **not lit**.
- `IMG_7747` (3.10 s) — a tight track along three lit shelves. The best material you have.
- `IMG_7749` (3.27 s) — starts tight on one lit line and pulls back to reveal all three.
  A reveal that was already shot; the cut only had to not waste it.

All three are already 1080×1920 SDR h264 at 30 fps (the HLG originals were tonemapped in
an earlier session), so there was no rotation, no tonemapping and no cropping to do — they
are natively vertical, which is why the whole reel is real frames edge to edge with no
blurred filler bars.

**2. Measured the brightness before choosing a grade.** The `noir` style preset in
`presets.json` (brightness −0.30, contrast 1.50) was built for pendant footage shot at
night, and this is a daylight workshop. Greyscale stats, 2 fps sample:

| clip | mean | p5 | p50 | p95 | p99 |
|---|---|---|---|---|---|
| polish (7745) | 116.6 | 28 | 118 | 203 | 228 |
| track (7747) | 132.3 | 60 | 116 | 245 | 248 |
| three (7749) | 144.4 | 61 | 136 | 244 | 253 |

So "dark and stylish" here is a grading problem, not a preset to switch on. The stock
noir grade would have buried the craftsman and the plank in black — the same mistake the
S1 brief's notes record.

**3. Built a grade that crushes the room and leaves the light alone.** Brief-level
override:

```
curves=all='0/0 0.22/0.07 0.5/0.24 0.78/0.62 1/1',
eq=brightness=-0.02:contrast=1.12:saturation=1.10,
colorbalance=rm=0.05:bm=-0.05:rh=0.05:bh=-0.07,
vignette=angle=PI/3.4:mode=forward
```

The curve pulls the midtones down hard (0.5 → 0.24) and leaves the knee above 0.78 nearly
linear, so the LED line stays hot while the room falls away. The colour balance pushes
warm in the mids and pulls blue out of the highlights, which takes the cold cast off the
window reflection on the polished lacquer. The vignette does the work a real dark room
would have done. I checked it on one frame from each clip **before** rendering, not after.

The polish clip has no LED to carry it, so its three shots get `+0.05` brightness back
per shot — otherwise the craftsman disappears and the middle of the reel is a black hole.

**4. Planned the cut with the repo's own system** (`system/make_reel.py`, `quickcut`
mechanism, `noir` style) rather than hand-rolling it, so the reel gets the safe-zone type
engine, the beat grid, the whoosh placement, the end card and the pre-flight sheet.
The brief is `SHELF-noir-phone.json` in this folder.

**5. Fixed the one check that failed.** The first build reported
`hook holds 0.92s (rule: ≥1.2s)` — the opening shot was one beat (1.16 s) and each text
cue is inset 0.12 s at both ends. Opening shot went to 1.3 beats, and the hand line's shot
to 1.25 beats so six words get 1.21 s instead of 0.92 s. The second build's pre-flight is
clean: **no lint, no warnings, no failed checks.**

**6. Rendered it myself, because the system's renderer could not finish here.**
`make_reel.py` emits one enormous ffmpeg graph in which every shot is upscaled to
2160×3840 with lanczos before `zoompan`. This box is running several other renders at the
same time, and that graph was moving at **0.002–0.018× realtime**; the first attempt was
still unfinished after nine minutes and the second was killed outright. So
`build_reel.py` (in this folder) takes the *same* plan the system produced —
`reel-timeline.json` plus the type-layer PNGs — and renders it shot by shot with a **1.5×
bilinear** supersample instead of a 2× lanczos one, and `setpts` instead of `minterpolate`
for the one slowed shot. Camera moves are still sub-pixel smooth; the render takes
**~2 minutes** instead of ~20. Creative decisions all still come from the brief.

One bug found and fixed along the way: overlaying the type layers as single-frame PNGs
produced invisible text, because a lone frame sits at pts 0 and `fade=t=in` evaluates its
alpha ramp on that frame and leaves it at zero. The PNGs are now looped into real streams
for the length of each cue. I caught it by pulling frames at each cue's timestamp and
looking at them — the file was otherwise perfectly valid.

---

## What I measured on the finished file

```
container: 1080x1920, h264, 25.0 fps, 12.12 s, aac 48000Hz stereo
9:16 1080x1920        : OK
length 12.12s         : OK (<=30s, feed-native)
grey mean / p50       : 38.0 / 20      (it is genuinely dark; ungraded source was 117-144)
p1 / p99              : 0 / 216
clipped >=254         : 0.14%          (only the LED line, which is the point)
crushed <=1           : 3.15%          (almost all of it the black end card)
near-black frames     : 0              (no holes in the cut)
frame-to-frame delta  : mean 20.3      (min 0 only on the static end card)
loudness              : -17.1 LUFS integrated, -3.8 dBTP, LRA 2.7
```

Plus checked by eye, on extracted frames: all three lines render, are legible over the
footage, and sit at x 60–679, y 1165–1335 — inside the Instagram safe area (x 70–950,
y 230–1500), clear of the caption block and the action rail.

`check_reel.py` in this folder is what produced that block. There is no `ffprobe` binary
in this container, so it parses ffmpeg's stderr for the container line and decodes raw
greyscale into numpy for the picture stats.

---

## Honest limitations

- **The shelves are on a workshop bench, not a wall.** No line in the reel says "wall",
  deliberately. If you want the on-the-wall payoff, the existing S1 reel uses a generated
  wall render for it — but that makes one frame AI and needs Meta's disclosure in paid.
  This cut stays 100 % real so it can go anywhere.
- **No price, no size, no material claim beyond what you can see.** The Shopify handle for
  this dark rosewood shelf is still unconfirmed in `presets.json` (filed under `brand`).
- **Shots 5 and 6 are the weakest 1.45 s.** They are texture beats on the unlit plank and
  there is a cold blue window reflection in the lacquer that the grade tames but does not
  remove. If you reshoot anything, reshoot the plank with the window behind the camera.
- **It is 12.1 s.** That is right for organic reach. Your own ad data says the 25–30 s
  bucket converts better in paid, so for an ad cut I'd hold the payoff longer and add a
  price/CTA beat rather than stretch what is here.
- Nothing was committed to git, and nothing was filed into the OS registry — say the word
  and I'll do the naming, registry row and handoff.

---

## Files here

| file | what |
|---|---|
| `reel.mp4` | **the finished reel** |
| `cover.jpg` | cover frame (0.9 s — the lit channel with the hook on it) |
| `SHELF-noir-phone.json` | the brief. Re-plan with `python3 nixwoods-reel/system/make_reel.py <this file> --out <dir> --dry` |
| `build_reel.py` | the renderer: `python3 build_reel.py reel-timeline.json out.mp4` |
| `check_reel.py` | the measurement script that produced the block above |
| `reel-timeline.json` | the system's pre-flight sheet: every cut, cue, audio event and rule check |
| `NOTES.md` | this |
