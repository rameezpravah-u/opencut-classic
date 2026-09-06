# NixWoods — 20s viral reel (9:16)

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
