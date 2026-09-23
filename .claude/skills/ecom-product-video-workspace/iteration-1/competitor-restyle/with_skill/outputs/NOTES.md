# Teak linear-light assembly reel — build notes

**Deliverable:** `reel.mp4` — 1080x1920, 25 fps, 26.24 s, 30.7 MB, music mix.
**Cost:** zero. Nothing was generated in this session; every frame came out of
`nixwoods-reel/`.

---

## 1. First, the thing worth saying once

Their footage is theirs. What is fair to take from a competitor's reel is the *structure* —
the shot list, the order, the pacing — and that is in fact what is being admired here: a 3D
assembly animation that starts on a bench and ends on a ceiling. So this reel copies their
structure beat for beat and uses **none of their frames**. Every pixel in `reel.mp4` is a
NixWoods asset.

Second disclosure, which matters if this ever runs as a paid placement: **the four bench /
assembly frames are AI-generated in origin**, not photographs of a NixWoods product. No
linear bar has been photographed on a workbench. They were generated on 17 Sep
(seedream-5-pro) and recoloured to teak; stages 3 and 4 were then *derived* from stage 2
with numpy rather than generated. The room and product beats are real NixWoods photography
(four stills) plus real workshop footage. Meta's AI disclosure needs ticking by hand, and
the caption should not call the bench sequence a photograph. `presets.json` already carries
an approve/reject verdict per frame with this caveat on it.

One more thing to look at with open eyes before this runs: the bench frames show a
**single**-channel bar, and the room photography is the Double Arm Teak Pendant, which has
**two** light lines. Nobody reading it as a genre piece will trip on that, but it is not
one product from end to end. The cut is honest about materials and about the canopy —
wooden canopy, cables, no chrome gripper the customer would not receive — but if this
becomes a real SKU page's video, the bench stage should be reshot or regenerated to match
whichever fixture it sells.

---

## 2. What was already in the repo (checked before building anything)

This is the step that saved the money. The competitor reel had already been read and
measured in an earlier session — `linear-reels/README.md` records it as
`instagram.com/reel/DbVnOOksf-c` (alumaetg, 28.5 s), read through the Vibiz connector
because plain HTTP hits Instagram's login wall — and its cut points had already been
measured off the source at 10 fps:

```
8.1  |  0.4  |  3.1  |  1.5  |  11.9  |  0.6  |  2.9   seconds
```

Seven shots, not the rapid cutting the format suggests: one long 8.1 s assembly take and
one long 11.9 s install take carry the reel.

Existing assets found by reading filenames against *this* shot list:

| asset | what it is | origin |
|---|---|---|
| `linear-reels/hf/teak-stage1-channel.png` | teak bar on bench, channel routed, driver beside it | generated 17 Sep, recoloured to teak |
| `linear-reels/hf/teak-stage2-led.png` | LED strip seated in the channel, dots visible | generated 17 Sep, recoloured to teak |
| `linear-reels/hf/teak-stage3-diffuser.png` | the same frame with the dots blurred into one line | **derived**, numpy, no generation |
| `linear-reels/hf/teak-stage4-lit.png` | the same frame with a warm bloom | **derived**, numpy, no generation |
| `teak-reels/hf/sh01-underside-twin.jpg` | teak pendant underside, lit line, rounded end | real photography |
| `teak-reels/hf/sh03-dark-two-lines.jpg` | the fixture lit in a dark room | real photography |
| `teak-reels/hf/sh05-canopy-cables.jpg` | wooden ceiling canopy + suspension cables | real photography |
| `teak-reels/hf/sh00-marble-dining.jpg` | installed over a dining table, warm room | real photography |
| `shelf-reels/src/IMG_7745.mp4` | Rameez's own workshop footage, hand-finishing wood | real footage |
| `system/briefs/L2-linear-teak.json` | a brief that already rebuilds exactly this structure | — |

Because the brief existed, the build was: re-derive nothing, generate nothing, change one
line of copy, re-render, verify.

---

## 3. Shot list, beat by beat

Their beat → our beat → the asset that covered it. `cut: 1.0` in the brief means `beats`
are literal seconds, so these numbers are the competitor's measured durations.

| shot | s | their beat | ours | asset | how it was covered |
|---|---|---|---|---|---|
| 1 | 2.5 | aluminium extrusion on a bench | slow pull-out on the teak bar, driver beside it | `t_channel` | direct |
| 2 | 2.2 | LED strip lowers into the channel | **wipe** `t_channel` → `t_led` (starts 0.5 s in, runs 1.3 s) | `t_channel` + `t_led` | **derived motion.** A wipe between two stills of the same setup at two stages produces assembly motion from photographs — no animation, no generation |
| 3 | 1.7 | diffuser slides in | **wipe** `t_led` → `t_diffuser` | `t_led` + `t_diffuser` | **derived frame.** `t_diffuser` is `t_led` with the LED dots blurred into one continuous line — which is optically what a diffuser does, so the frame is honest as well as free |
| 4 | 1.7 | (they go straight to the cap) | **wipe** `t_diffuser` → `t_lit` — it comes on | `t_diffuser` + `t_lit` | **derived frame.** `t_lit` is `t_led` with a warm bloom screen-composited off the brightest pixels |
| | | | *shots 1–4 = 8.1 s, their single assembly take, assembled inside the take as theirs is* | | |
| 5 | 0.4 | end cap | hard push into the rounded end of the real fixture, `crop_cx 0.32` | `t_underside` | the literal end-cap photograph was too small to use — see §5 |
| 6 | 3.1 | — | drift along the lit underside | `t_underside` | direct |
| 7 | 1.5 | — | push on the fixture lit in a dark room | `t_dark` | direct |
| 8 | 4.5 | ceiling mount and suspension | tilt down the wooden canopy and its cables | `t_canopy` | direct — real photography of the actual canopy, so no mechanism is depicted that the customer will not receive |
| 9 | 3.7 | | pull back on the dark room | `t_dark` | direct |
| 10 | 3.7 | | **the workshop** — a craftsman hand-polishing a teak bar | `polish` clip, in at `ss 0.0` | real footage; this is where "we make it ourselves" lands, and unlike their CGI it is a real bench. In-point changed — see §5 |
| | | | *shots 8–10 = 11.9 s, their ceiling-install take* | | |
| 11 | 0.6 | | cut back to the fixture, second crop centre | `t_underside` | direct |
| 12 | 2.9 | finished pendant over a table in a room | pull back on the dining room | `t_dining` | direct |
| 13 | 2.0 | (their logo) | end card, `teak. not aluminium.` | system end card | — |

Beats sum to 28.5 s and the end card adds 2.0 s, so the cut is 30.5 s of material. The
finished file is **26.25 s**, because each transition overlaps its two shots:
30.5 − (11 dissolves × 0.35 + the end card's 0.4 fade) = 26.25, which is exactly what the
timeline reports. That is the only place the timing departs from the reference's
28.5 s, it is a property of the dissolves rather than a truncation, and it was verified by
decoding the file and counting frames rather than trusting the container (§6). Every
individual beat still occupies the duration measured off the reference.

---

## 4. What changed from the on-record brief

Three things, all found by checking rather than by taste: the **hook** (below), the
**music bed** (§6 — the track was 6 s shorter than the reel) and the **workshop clip's
in-point** (§5 — it was landing after the craftsman left frame). Shots, durations, grade
and structure are untouched.

### The hook

`L2-linear-teak.json` opens with **"this one is not aluminium."** Scored through
`system/hooks.py`:

```
 8/12   gap ✓   truth ✓   pull ✗     "this one is not aluminium."
```

It opens a gap (what *is* it?) and it is true, but it gives no reason to keep watching —
it is a statement to agree with. Candidates scored against the same gates:

```
 4/12   gap ✗ truth ✓ pull ✗   "everyone makes these in aluminium."   (states a category)
 7/12   gap ✓ truth ✓ pull ✓   "this one is wood. watch it go together."
 8/12   gap ✓ truth ✓ pull ✓   "watch this one. it is not aluminium."
 9/12   gap ✓ truth ✓ pull ✓   "this one is not aluminium. watch."     <-- shipped
 9/12   gap ✓ truth ✓ pull ✓   "not aluminium. watch what goes in."
10/12   gap ✓ truth ✓ pull ✓   "your linear light is not aluminium."   (scores well, but it is
                                a claim about the viewer's light that we cannot make — rejected
                                on truth grounds even though the gate passed it)
```

Shipped line keeps the settled contrast and adds the pull word, and "watch." is honest:
the next six seconds are the assembly. All three gates pass, and the system's pre-flight
now reports `HOOK 9/12 gates gap/truth/pull ✓✓✓`.

---

## 5. Things measured, and what the measurement changed

**Upscale factor per still** (source px → the 1080-wide frame). Anything much past ~1.7x
reads soft on a phone:

```
asset          source     fit       upscale
t_channel      2048x1152  cover      1.67
t_led          2048x1152  cover      1.67
t_diffuser     2048x1152  cover      1.67
t_lit          2048x1152  cover      1.67
t_underside    1254x1254  contain    1.53 (cover)
t_dark         1170x1170  cover      1.64
t_canopy        819x 819  contain    1.32
t_dining       1254x1254  contain    1.53 (cover)
t_endcap        493x 493  contain    2.19   <-- kept out of the cut
t_strip         595x 595  contain    1.82   <-- kept out of the cut
```

`t_endcap` (`sh04-end-channels.webp`) is the literal end-cap photograph and is the obvious
asset for their 0.4 s end-cap beat — a close-up of the rounded teak end. At 493 px it needs
2.19x to fill the frame and is visibly soft, so shot 5 is instead a 0.4 s hard push into
`crop_cx 0.32` of `t_underside`, which puts the same rounded end in frame at 1.53x. Same
information, 1.4x sharper. If someone reshoots that end cap at 1500 px it should go back in.

**The workshop beat was pointing at the wrong two seconds.** The contact sheet is what
caught it: at the brief's `ss 2.1`, the 3.7 s "we make it ourselves" beat was a blurred
dark bar with a cold blue window reflection sliding across it — the one cold, unreadable
smudge in an otherwise warm reel, sitting on the reel's most important claim. Sampling the
clip every 0.4 s shows why: the craftsman with the pink polishing cloth is in frame from
0.0 s to about 2.2 s, and the camera swings off him at 2.4 s. In-point moved to **0.0**, so
the beat opens on the hands and the cloth and then drifts down the bar. This is the one
change a contact sheet could find and a frame count could not — it is why you look at the
pictures as well as the numbers.

**Luminance, to check the noir grade suits this footage** (the grade lifts the toe rather
than crushing it: `curves=all='0/0.02 0.3/0.29 0.75/0.80 1/1'`, brightness −0.04):

```
              mean   p5    p95
t_channel    170.0   20    255
t_underside  141.1   69    203
t_canopy     191.0   83    225
t_dining     186.1   68    234
t_dark        36.3   17     74
```

Bright studio photography sitting at p5 = 68–83 tolerates this grade; `t_dark` at p5 = 17
is the one shot that could go muddy, which is why the curve lifts 0 → 0.02 instead of
crushing to black. `contain` is used only on the bright stills — on `t_dark` it would put
the subject in a near-black blurred surround, so that shot is `cover`.

**Warm-light check.** Bloom and recolour tricks that zero luma while leaving chroma alone
produce magenta glows that look fine in a thumbnail. Per-channel means on the lit beats are
printed by `verify_reel.py` and must satisfy R > G > B. Result in §6.

**Teak recolour.** Stages 1–4 were originally rosewood renders; the teak target was
sampled from NixWoods' own teak photography and applied as a continuous per-pixel weight
(how much each pixel already resembles wood) rather than a binary colour mask, so dark and
lit grain move together and neutral pixels — the bench, the driver, the wall — stay put.
Visually confirmed against the real teak photography in the same cut: the bench frames and
`t_underside` read as the same species.

---

## 6. Verification before shipping

`verify_reel.py` in this folder, run against the finished file:

```
== reel.mp4  30.7 MB
   Duration: 00:00:26.30, start: 0.000000, bitrate: 9324 kb/s
   Stream #0:0[0x1](und): Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive), 1080x1920 [SAR 1:1 DAR 9:16], 9172 kb/s, 25 fps, 25 tbr, 12800 tbn (default)
   Stream #0:1[0x2](und): Audio: aac (LC) (mp4a / 0x6134706D), 48000 Hz, stereo, fltp, 165 kb/s (default)
   decoded frames: 656  -> 26.24 s at 25 fps
   frame-diff cuts (>12.9): [10.68, 14.96, 15.08, 18.44, 18.64, 19.24, 19.44, 19.64, 19.84, 20.04, 20.08, 20.12, 20.16, 20.2, 20.24, 20.28, 20.32, 20.36, 20.4, 20.44, 20.48, 20.52, 20.56, 20.6, 20.64, 20.68, 20.84, 21.04, 21.44, 21.64, 21.8]
   last frame: mean lum 5.2, ink pixels (>200) 1.90%  -> end card present: True
   t=  6.5s  R  85.9 G  67.3 B  51.4   warm(R>G>B): True
   t= 12.0s  R 130.9 G 114.2 B  94.5   warm(R>G>B): True
   t= 17.0s  R  10.2 G   5.7 B   3.8   warm(R>G>B): True
   t= 23.0s  R 125.0 G 112.1 B  95.8   warm(R>G>B): True
   contact sheet -> contact-sheet.jpg
   audio: 26.26 s decoded vs 26.24 s of video
   audio RMS per second: 0.201 0.221 0.225 0.198 0.223 0.233 0.234 0.210 0.223 0.220 0.206 0.201 0.206 0.214 0.211 0.222 0.223 0.212 0.124 0.176 0.209 0.201 0.227 0.233 0.220 0.135
   last 4 s audible (RMS > 0.005): True
   dark-frame centre column: 39 distinct levels over 1920 px (low numbers = banding)
   size 30.7 MB  under 50 MB ceiling: True
```

- **The `frame-diff cuts` line is not a cut list.** Everything in this reel is a dissolve,
  not a cut, so the only boundary that clears the threshold is 10.68 s; the cluster from
  18.4 to 21.8 s is the handheld workshop footage moving, which is the same measurement
  reading real motion. It is printed as a sanity check that the pacing is what the timeline
  says, not as shot detection.
- **Not truncated.** Container duration and decoded frame count agree. This matters: when
  ffmpeg runs out of source frames it does not error, it just stops, and the container
  still reports the full length — which silently eats the end card.
- **End card present.** Last frame extracted and checked for ink, not assumed.
- **Contact sheet** written to `contact-sheet.jpg` for framing and text placement — but the
  file itself was watched, because a sheet cannot show pacing or a dead tail.
- **Source overrun.** The one video shot is `polish` (`shelf-reels/src/IMG_7745.mp4`),
  a 5.93 s clip. At the brief's original `ss 2.1` it consumed 2.1 → 5.80 s, leaving 0.13 s
  of margin — and reelkit asks for 0.4 s of padding beyond that, so it was already reading
  past the end of the file. Harmless here (the trim only takes the 92 frames it needs) but
  with no room at all to lengthen the beat. Moving the in-point to 0.0 for the reason below
  takes the margin to 1.83 s. If anyone re-times this reel, that is the shot that will
  silently truncate everything after it, end card included; the frame count in §6 is what
  proves it did not.

**The music bed was 6.2 seconds too short and nothing said so.** `audio/music7-noir.mp3`
is 20.04 s; this cut is 26.25 s. The engine lays the bed at t=0 and fades it out at
24.85 s — a fade that never fires, because the track has already ended. The reel therefore
ran silent through the workshop beat, the room shot and the *entire end card*, and no stage
of the pipeline complains: the mix filter is `duration=longest`, so the file is the right
length with nothing in it. It only shows up if you decode the audio and look at its RMS
second by second, which `verify_reel.py` now does. Fixed by crossfading the track into
itself to 37.5 s (`linear-reels/audio/music7-noir-x2.mp3`, `acrossfade=d=2.5`); the brief
points at it, so a re-render gets it directly, and `remux_audio.py` applied the same bed to
the finished master without paying for another render. **This affects the existing
`NW-...-teak-not-aluminium-*-v1.mp4` renders in `linear-reels/out/system/` too** — same
track, same length — so they should be re-rendered before anyone posts them.

**One render was thrown away, and the check is the only reason anyone would know.** A
second copy of the render started by accident (importing the wrapper module executed it —
now fixed with an `if __name__ == "__main__"` guard) and rebuilt `*-wipe1..3.mp4` *while
the real render had those files open as inputs*. The resulting master still reported
26.24 s and still decoded 656 frames; it was only when the frames were actually decoded
that ffmpeg reported `Invalid NAL unit size` and `Error splitting the input into NAL units`
scattered through it. A container header and a frame count both looked correct on a broken
file. It was re-rendered from scratch with nothing else touching those paths.

---

## 7. Files in this folder

| file | what |
|---|---|
| `reel.mp4` | the deliverable — 1080x1920, 25 fps, 26.24 s, CRF 23 |
| `L3-teak-assembly.json` | the brief; `python3 nixwoods-reel/system/make_reel.py L3-teak-assembly.json` reproduces the master |
| `render_reel.py` | the render wrapper (see below) |
| `remux_audio.py` | rebuilds the music bed over a finished master and encodes the delivery copy |
| `verify_reel.py` | the pre-ship checks |
| `verify.txt` | their output on the shipped file |
| `contact-sheet.jpg` | 4x4 sheet from the finished file |
| `render.log` | the engine's own run log |

One asset was added to the repo: `music7-noir-x2.mp3`, the looped music bed (see §6).
`linear-reels/audio/` is a symlink to the shared track folder, so it lands in
`nixwoods-reel/rubik-reels/audio/` and every product can use it. Nothing was committed —
`git status` shows it, the new master and the wipe intermediates as untracked.

`render_reel.py` exists for one reason: reelkit's `fit="contain"` builds the blurred
backing plate at 2160x3840 and runs `gblur=sigma=44` on it every frame. Measured on this
box, that is 28.7 s of wall clock per second of output against 3.8 s for a `cover` shot,
and this cut has 11.5 s of `contain`. The wrapper blurs the plate at quarter scale with
sigma/4 and scales it back up — a Gaussian blur is a low-pass filter, so the detail the big
blur would have destroyed is exactly what the downscale destroys. 28.7 s → 11.3 s per
second of output. Checked rather than assumed — same frame rendered both ways and
differenced:

```
mean abs difference   0.085 / 255
99th percentile       2.0
max                   5.0
subject band          0.000   (bit-identical — the fg path is untouched)
blurred plate band    0.133
```

Nothing else in the engine, the brief, the grade or the timings is touched. It is worth
upstreaming into `reelkit.still_chain`.

## 8. Not done here

Per `nixwoods-reel/CLAUDE.md` the NixWoods OS contract wants a render **filed** under the
`NW-...` name, **registered** in `ASSET_REGISTRY.md`, **reachable** via the rebuilt index
and **handed off** with a TASK_LEDGER row. None of that was done, because this session was
asked not to commit or push. To file it properly:
`python3 nixwoods-reel/system/file_for_os.py --date 20260923`, then the registry row with
`status = STAGED` (it needs the AI-disclosure note in its caption before it can run as an
ad), `usable-for` including ADS and SOCIAL.


---

## 9. Caption to post it with

The disclosure costs one line and protects the brand, so it is in the caption rather than
in a note to yourself:

> this one is not aluminium.
>
> solid teak, routed channel, LED, diffuser, wooden canopy — cut and finished in our own
> workshop. the bench sequence is a render; everything from the ceiling shot on is the real
> fixture.
>
> nixwoods.com

If it runs as a paid placement, tick Meta's AI-disclosure box as well — the caption is not
a substitute for it.
