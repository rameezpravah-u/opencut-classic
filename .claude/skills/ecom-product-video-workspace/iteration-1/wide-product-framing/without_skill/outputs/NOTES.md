# Double Arm Teak Pendant — 9:16 product reel

**Deliverable:** `reel.mp4` — 1080×1920, 25 fps, 20.21 s, H.264 (yuv420p, CRF 18) + AAC 192 k, 4.3 MB.
**Also here:** `build_teak_reel.py` (the build script — deterministic, re-run it to rebuild) and
`shot-sheet.jpg` (one frame per beat, for review).

Everything was made locally from the six existing photos with Pillow + `imageio_ffmpeg`.
No paid generation API was used, nothing was generated, and nothing was committed.

---

## The problem the edit had to solve

The product is a **four-foot linear pendant** and **every source photo is square (1:1)**. A 9:16
frame is 56.25 % as wide as it is tall, so a centre crop of a square image keeps only the middle
**56.25 % of the width** and throws away 43.75 % — 21.9 % off each end.

I measured the fixture's horizontal extent in each file before deciding anything:

| File | Pixels | Fixture spans (fraction of image width) | Survives a 9:16 centre crop? |
|---|---|---|---|
| `sh00-marble-dining.jpg` | 1254×1254 | ~100 % (canopy + bar + window furniture) | **No** — both ends cut |
| `sh01-underside-twin.jpg` | 1254×1254 | 0.10 → 0.93 (**83 %**) | **No** — both ends cut |
| `sh02-strip-fluted.jpg` | 595×595 | 0.00 → 1.00 (**100 %**, runs off both edges) | **No** — 44 % of the bar lost |
| `sh03-dark-two-lines.jpg` | 1170×1170 | 0.00 → 0.95 (**95 %**) | **No** — both ends cut |
| `sh04-end-channels.webp` | 493×493 | 0.13 → 0.83 (70 %, macro) | No (and it doesn't matter — it's a detail) |
| `sh05-canopy-cables.jpg` | 819×819 | 0.16 → 0.86 (70 %, canopy + cables) | **No** — canopy ends cut |

**Not one of the six survives a 9:16 centre crop with the fixture intact.** For a product whose
entire selling point is that it is one unbroken four-foot bar, cropping the ends off is the single
worst thing the edit could do — it would make a 49 in pendant look like a 24 in one.

### What I did instead

The product is **never cropped horizontally**. Each shot is a **full-width band** of the source
(the whole original width, scaled to 1000 px, with a 40 px margin each side), cropped **only
vertically** to cut dead ceiling and floor. The band sits on a full-bleed field built from that
same photo's own pixels — blurred, warm-toned and darkened — so there are no black letterbox bars
and the frame reads as a designed layout rather than a squeezed-in square.

Consequences of that rule, deliberately accepted:

- **No push-in or zoom on the product.** Any scale above 1.0 pushes the ends of the bar out of
  frame. All camera movement is **vertical-only parallax**: the band drifts 8 px one way, the
  blurred field drifts ~40 px the other. Slow and calm, which suits a ₹9,999 considered purchase
  anyway.
- The caption block lives **below** the band, at y 1330–1480, entirely inside the
  Instagram safe zone.

Other things I measured or checked:

- **Resolution headroom.** `sh04` (493 px) and `sh02` (595 px) are the two small files. At the
  1000 px band width `sh04` would have been a 2.03× upscale and visibly soft, so it's shown as a
  **780 px inset card** instead (1.58× upscale) — it's a macro, it doesn't need the full width.
  `sh02` at 1000 px is a 1.68× upscale and holds up.
- **`sh03` grade.** It's a genuinely dark evening shot. My first pass lifted it to +28 % brightness
  and pulled blue down, which turned the wall **olive** and, when I tried to correct it, pushed the
  clipped LED highlights **magenta**. The fix was to stop fighting it: +10 % brightness, +4 %
  saturation, no channel gains. The wall stays warm, the LED stays white.
- **Safe zone.** All 16 text lines checked against the repo's stated Instagram safe area
  (x 70–950, y 230–1500). All 16 sit inside it; widest line is "One bar. The whole table." at
  759 px (x 160–920).
- **Copy rules.** Max 6 words per screen (the house limit is 12). No word from the repo's banned
  list. Every claim is from the product's approved facts list in `system/presets.json`.
- **Audio.** `music5-3040.mp3` (indie folk, 95 bpm) — the track the repo already assigns to the
  30–40 audience, which is the pendant buyer. Its measured beat grid is **2.526 s**, so every cut
  in the reel lands on a beat. Levels: mean −19.3 dB, peak −2.6 dB. Fade in 0.4 s, out 1.1 s.

---

## Shot list

Eight beats of 2.526 s each (one music bar), 0.30 s cross-dissolve between them.

| # | In | Source | Frame | On screen |
|---|---|---|---|---|
| 1 | 0.00 | `sh00-marble-dining` | Wide hero, whole dining room. Opens at 88 % exposure and comes up to 100 % over 0.55 s — a subtle "light coming on" without a dark first frame (frame 1 is the thumbnail). | **Two lines of light.** / **One piece of teak.** |
| 2 | 2.53 | `sh01-underside-twin` | Evening three-quarter. The shot where you can actually see there are *two* channels — the whole product name. | **Twin LED channels.** / warm 3000K, along the underside |
| 3 | 5.05 | `sh02-strip-fluted` | The length shot, bar running edge to edge. An architect's **dimension line draws left end to right end** over 1.1 s and locks with end ticks. | **49 in, end to end.** / four feet of solid teak |
| 4 | 7.58 | `sh02-strip-fluted` | Same plate, no dissolve — the beat is marked by the bracket releasing and the caption swapping. Keeps the length on screen for a full 5 s without a dead hold. | **One bar. The whole table.** / lights the table, not your eyeline |
| 5 | 10.10 | `sh04-end-channels` | Macro end cap as a 780 px inset card — rounded solid-teak cap, the two channels running into it. The material-proof beat. | **Handcrafted in India.** / solid teak · rounded end caps |
| 6 | 12.63 | `sh03-dark-two-lines` | Dark room, both strips lit. The "what it looks like at 9 pm" beat. | **Dimmable, by remote.** / 3000K warm · 18W |
| 7 | 15.16 | `sh05-canopy-cables` | Ceiling up-shot: one teak canopy, two cables. Answers the install question buyers ask. | **One canopy. Two cables.** / solid teak, ceiling to bar |
| 8 | 17.68 | end card | `sh00` dropped to 55 % under an espresso plate. Logo, name, spec strip, price, URL. | NIXWOODS · **Double Arm Teak Pendant** · solid teak · 49 in · 3000K · dimmable · **₹9,999** (was ₹12,999) · nixwoods.com |

**Structure:** hook → mechanism → scale → benefit → material → mood → install → price. The repo's
own creative notes say pendant copy should *qualify* rather than *stop the scroll* (pendants run
low CTR / very high ROAS), so the length and the price are stated plainly and early rather than
teased.

---

## Brand values used

Pulled from `nixwoods-reel/system/presets.json`, style `3040` ("30–40 trust"), which is the
audience profile for a considered pendant purchase:

- Canvas 1080×1920 @ 25 fps · cut grid 2.526 s · safe area x 70–950, y 230–1500
- Playfair Display 600 @ 66 px headline / DM Sans 500 @ 38 px support (the repo's "serif = considered
  purchase" pairing)
- Ivory `#F4EADB` text · honey accent `#D9A05B` · espresso `#14110E` card
- Price ₹9,999, compare ₹12,999, nixwoods.com — all from the product record, not invented

---

## Two things worth your call

1. **"Four foot" vs "49 in."** You described it as a four-foot pendant; the product record in
   `presets.json` says **49 in** (= 4.08 ft), and 49 in is on its approved-facts list while
   "4 ft" is not. I used **"49 in, end to end."** as the headline with **"four feet of solid teak"**
   as the sub, so both readings are covered and neither is wrong. If the PDP spec should read
   48 in / 4 ft exactly, shot 3's copy is a one-line change in `build_teak_reel.py`.
2. **Shot 7's sub line.** I wrote "solid teak, ceiling to bar" rather than "cable height adjusts to
   your ceiling". Cable adjustment is on the *Rosewood* pendant's fact list, not this product's, and
   I wasn't going to assert it here without confirmation. If this pendant's drop is adjustable, that
   is a stronger line and worth swapping in.

Also worth knowing: this reel was built with a standalone script rather than through
`system/make_reel.py`, so it has **not** been through the repo's lint / hook-score / QA gates, and
it has not been filed, named, registered or handed off per the NixWoods OS contract in
`CLAUDE.md`. I left it out of git as instructed. If you want it inside the system, the shot list
above maps cleanly onto a `system/briefs/*.json` brief for the `teak` product with style `3040`.

---

## Rebuilding

```bash
python3 build_teak_reel.py     # ~90 s, writes reel.mp4 next to the script
```

Needs `pillow`, `numpy`, `imageio-ffmpeg`, and the source photos plus fonts and music at their
current paths under `/home/user/opencut-classic/nixwoods-reel/`. The shot list, crops, grades and
copy are all in the `SHOTS` table at the top of the script.
