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
