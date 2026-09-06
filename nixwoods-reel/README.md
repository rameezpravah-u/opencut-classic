# NixWoods reel system

Brief-driven 9:16 reels for NixWoods, with the quality gates that keep them on-brand and ad-legal.
**New here?** Read `system/PLAYBOOK.md`, then `system/README.md`. Agents: invoke the `nixwoods-reels` skill or read `CLAUDE.md`.

```bash
pip install pillow numpy imageio-ffmpeg
python3 system/make_reel.py system/briefs/T1-transformation.json     # one reel
python3 system/make_reel.py system/briefs --all                      # all thirteen
```

| Want | Go to |
|---|---|
| How any of this works | `system/PLAYBOOK.md` |
| Brief schema, adding a product or mechanism | `system/README.md` |
| The twelve reels and the ad cut | `rubik-reels/out/system/` |
| What the product actually looks like | `rubik-reels/ref/REFERENCE.md` |
| Image and video prompts that produced the assets | `rubik-reels/hf/PROMPTS.md` |
| Voice-over scripts | `system/scripts/vo-scripts.md` |
| Which Drive clip is which product | `FOOTAGE-INDEX.md` |

---

## The first reel — 20s brand cut (9:16)

Output: `out/NixWoods-Reel-20s-9x16.mp4` (1080×1920, 25 fps, H.264 + AAC, −15 LUFS) and `out/NixWoods-Reel-cover.jpg` (Reels cover frame).

Built entirely from the raw product clips in Google Drive → `NixWoods Creatives / 1 - Inbox / New Videos` (renamed 6 Sep 2026, see `FOOTAGE-INDEX.md`) and the music track from `NIXWOODS-brand-film-music-4x5.mp4`.

## Structure (hook → problem → value → craft → mood → CTA)

Every cut lands on the music's pulse (a hit every 1.19 s, grid starts at 0.80 s).

| Reel time | Clip | What happens | On-screen text |
|---|---|---|---|
| 0.00–3.18 | 03 | Dark room. Aurora wall light snaps ON at 0.80 s on the first hit. | *Still lit by one tubelight?* |
| 3.18–5.56 | 04 | Aurora angled, warm wash over the painting. | kicker AURORA · SOLID TEAK · 3000K — *Warm light on the wall. Not in your eyes.* |
| 5.56–7.94 | 16 | Hand turns the brass dimmer, Edison bulb ignites on the beat at 6.75 s. | *One switch. The whole mood changes.* |
| 7.94–9.13 | 07 | Macro: teak pendant light strip. | *Solid teak. Solid rosewood.* — Handmade in India · 3-year wood warranty |
| 9.13–10.33 | 09 | Macro: angled twin-line pendant (warmed slightly). | (same) |
| 10.33–12.71 | 13 | 360° loop pendant over the dining table. | *One light. The whole room.* |
| 12.71–16.28 | 14-1 | Glass Block lamp: hand cycles amber → red → green → warm. Music climax lands on green. | kicker ONE LAMP · THREE MOODS — *Red. Green. Amber.* then *Your room. Your mood.* |
| 16.28–17.47 | 06 | Floor lamp in purple RGB mood. | *Or purple.* |
| 17.37–20.00 | end card | Espresso card, warm glow, NX logo. | *Stop buying boring lights.* — nixwoods.com — Solid wood lighting · Handmade in India · Free shipping |

## Colour choices

- **Ivory** `#F4EADB` for all headline text: reads like warm paper against 3000K wood footage, never the cold white of the "tubelight" the hook attacks.
- **Honey amber** `#E3A552` for kickers, the URL and the end-card glow: the colour of the light the products actually give off, and the gold the Indian metro buyer (30–55, festive-season shopper) associates with warmth and occasion.
- **Espresso** `#14110E` end card: the dark sheesham/rosewood tone, keeps the logo and amber glowing.
- **Red / green / amber / purple** words are coloured to match the lamp on screen at that moment, so the copy and the product say the same thing.
- Footage grade: +5 % contrast, +6 % saturation, light vignette; clip 09 warmed to 5000 K so the one cool-white shot matches the set.
- Type: Playfair Display 600 (serif, matches the existing NixWoods reels) + DM Sans for kickers and sub-lines. Both are OFL fonts, included in `assets/`.

Copy stays inside the brand rules from `NixWoods-Master.md` and `AD-COPY.md`: warm, plain, specific, no banned words (discover / elevate / luxury / premium / stunning / curated …).

## Rebuild

```bash
pip install pillow numpy imageio-ffmpeg      # ffmpeg 7 static binary comes with imageio-ffmpeg
# put the Drive clips in ./src as 03.mp4, 04.mp4, 16.mp4, 07.mp4, 09.mp4, 13.mp4, 14-1.mp4, 06.mp4
# and the music source as ./src/brandfilm-9x16ish-4x5.mp4 (Drive: NIXWOODS-brand-film-music-4x5.mp4)
python3 build.py
```

`build.py` renders the text layers and end card with Pillow, then assembles everything in one ffmpeg filter graph. Timings, copy and colours are all at the top of the file.

## Suggested caption

> Still lit by one tubelight? One solid-teak light changes how the whole room feels. Handmade in India, 3000K warm, free shipping. nixwoods.com

Hashtags: #nixwoods #woodenlights #homedecorindia #interiordesignindia #warmlighting #pendantlight #walllight #tablelamp

## Notes

- Music is the track from the existing NixWoods brand film; confirm its licence covers paid placement before running it as an ad.
- The 3-colour Glass Block beat is the hero product moment the master doc requires for any Rubik's/Glass Block creative.
- Per the deployment hard rules, preview-verify in Ads Manager before spending.

---

## Where content is saved (standing rule, set 6 Sep 2026)

The session container is ephemeral. Anything not committed is gone when the session ends, so **this repo on `main` is the store of record** and renders are committed as each one passes review, not batched at the end.

What goes in, and what it costs today:

| Class | Path | Size now | Rule |
|---|---|---|---|
| System (code, presets, briefs, playbook, fonts) | `system/`, `rubik-reels/reelkit.py` | 3 MB | always; this is the part that matters |
| Design reference | `rubik-reels/ref/` | <1 MB | always; every product needs its own before any generation |
| Generated stills and short clips | `rubik-reels/hf/` | 17 MB | always, approved and rejected alike — the rejects are the fidelity gate's evidence |
| Finished reels | `rubik-reels/out/…` | 454 MB | the approved final cut only, music + clean, re-encoded at CRF 23 above ~21 MB |
| Review sheets and timelines | alongside the reels | 40 MB | JPEG sheets, never PNG (11× smaller; the PNG era ended 6 Sep) |
| Intermediates | — | — | never: wipe fragments (`*-ba.mp4`, `*-tri.mp4`), superseded takes, `__pycache__` |

**Where we are against the ceiling (6 Sep, four products).** Adding 20 reels took `.git` from 560 MB to about 940 MB even after re-encoding the set at CRF 24. That is the last product whose finished mp4s belong in git. **Product five moves the videos to Git LFS or Drive** and keeps only covers, sheets and timelines here — the system regenerates every mp4 from `system/` and the product folders with one command, so the videos are the expendable part.

**The ceiling to watch.** A product set is roughly 300 MB of video. The repo is at 560 MB after one product. GitHub starts warning past 1 GB and refuses past 5 GB, and git keeps every version forever, so a re-render of a committed reel costs its full size again. At product three, either move finished mp4s to Drive or Git LFS and keep only covers, sheets and timelines here. Everything in `out/` regenerates from what is in `system/` and `hf/` with one command, so the videos are the expendable part, not the system.

**Rendering a batch.** A long render must not write into the working tree: a half-written mp4 will be picked up by any `git add`, and a corrupt file in history is worse than no file. Render a batch to a staging directory with `--out`, review it, then copy the finished set in and commit:

```bash
python3 system/make_reel.py system/briefs --all --out /tmp/stage
# review the sheets, then
cp /tmp/stage/<name>-* <product>-reels/out/system/ && git add … && git commit
```

Single reels can render in place; the risk only appears when a batch runs for tens of minutes.

**Google Drive** stays the human-side archive (`NixWoods Creatives`). This session can read from Drive but cannot write video to it, so uploads there are manual. Drop new source footage into `1 - Inbox` and `system/sources.py` will register it.
