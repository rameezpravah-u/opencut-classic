# NixLine voice-over reels (Hindi and English), made with MoneyPrinterTurbo

| File | Language | Voice | Length |
|---|---|---|---|
| `NW-CREATIVE-VID-20261011-nix-line-solid-wood-floor-lamp-voiceover-hi-v1.mp4` | Hindi | Edge TTS `hi-IN-SwaraNeural`, 1.1x | 30.7 s |
| `NW-CREATIVE-VID-20261011-nix-line-solid-wood-floor-lamp-voiceover-en-v1.mp4` | English | Edge TTS `en-IN-NeerjaNeural`, 1.1x | 30.1 s |

Both are 9:16, 30 fps, with music6-corners under the voice. Every frame is real (the NixLine workshop clips and the
5 Aug shoot photo AC4I9815), so nothing is generated and no AI label is needed. The voice is synthetic (Edge TTS).
The scripts (`script-en.txt`, `script-hi.txt`) use brand.md facts only: 30-inch solid teak, handmade in UP,
stands on its own teak block, plug in, no electrician, ₹999, COD, free delivery. There are no banned words.

## How it was made
1. `prep_materials.py`: footage graded with MOTION.md's montage grade (first pass, superseded by step 3).
2. MoneyPrinterTurbo (`cli.py --stop-at subtitle`) voices each script. The caption timings are saved as `timing-<lang>.srt`.
3. `build_materials.py <lang>` cuts a shot list to those timings, one shot per line group, every lamp vertical.
   Clips are slowed to no less than 0.7x. The room photo gets three framings with slow pushes.
4. MoneyPrinterTurbo assembles the shots in order: local source, sequential, no transitions, 15 s max clip,
   voice and music. Its own captions are switched off.
5. `burn_captions.py <lang> <in> <out>` sets the captions in a side column clear of each shot's lit channel. It uses
   Inter 600 or Hind SemiBold, cream with the price in amber, on a dark gradient, above y 1250.

Why step 5 exists: MoneyPrinterTurbo can only centre captions, and the channel stands on the centre line, so
its captions crossed the light (MOTION.md 7.2).

**Known compromise:** "Made by hand / हाथ से बनी" sits over the bundle shot, where lit bars fill the whole frame.
Those captions cross other bars' channels. No side is clear.

## Setup notes (cloud)
- Edge TTS uses its own certifi bundle. The sandbox egress CAs are appended to the MoneyPrinterTurbo venv's
  `cacert.pem`, so verification stays on.
- MoneyPrinterTurbo only accepts background music from `storage/bgm` or `resource/songs`.
- The Hindi font is Hind SemiBold (`assets/Hind-SemiBold.ttf`, SIL OFL, `assets/Hind-OFL.txt`). PIL has raqm, so
  Devanagari shapes correctly.

## Ad cut-downs (12 Oct 2026, social desk request of 11 Oct)

`NW-CREATIVE-VID-20261012-nix-line-solid-wood-floor-lamp-voiceover-en-ad-cut-v1.mp4` and `…-hi-ad-cut-v1.mp4`:
- 9:16, 14.95 s each, for paid use.
- ₹999 is spoken and on screen at 7.1 s (EN) and 7.5 s (HI). The ad rule is price before 10 s; the full reels show it
  at about 22 s.
- Made by `ad_cut.py en|hi`, then `burn_captions.py en-ad|hi-ad` (called by `ad_cut.py`).

**Voice:** not re-voiced. Edge TTS was refused on 12 Oct (Bing returns 403 to the websocket from this sandbox). The
lines are cut from the same voice-only tracks the full reels used (MoneyPrinterTurbo tasks `…e1` and `…a1`), in this
order, with the pauses tightened:
1. the tubelight hook;
2. "one line of warm light, set in thirty inches of solid teak";
3. "only ₹999";
4. "made by hand in Uttar Pradesh";
5. "cash on delivery, free delivery".

Every line is from the approved full scripts. The Hindi runs 0.9% faster to fit 15 s (1.1x × 1.009).

**Footage:**
- Real NixLine workshop clips only, one per caption. Hands are in frame on the price, offer and closing shots.
- The 5 Aug photo AC4I9815 is deliberately not used: whether it shows the NixLine or the corner floor lamp is still an
  open owner check, and ₹999 must not sit on a ₹6,999 lamp.
- **The full 30 s reels still use that photo; confirm it before they run as ads.**

**Timings:** `timing-en-ad.srt` and `timing-hi-ad.srt`.
