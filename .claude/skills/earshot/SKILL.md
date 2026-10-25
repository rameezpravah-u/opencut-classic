---
name: earshot
description: Ears and a sound bank for NixWoods reels. Earshot (github.com/Leonxlnx/earshot, MIT, pinned v0.4.0) renders 252 sound effects stored as code (whooshes, pops, wood knocks, hits, mallets, shutters), builds a reel's sound kit with measured sync points and levels against the music, and listens to a finished reel (timeline, annotated sheet, critique against professional launch films). Use when adding or checking sound effects on a reel, when a sound must land on a cut or a word, or when the owner says a reel's sound feels cheap, late, too loud or missing.
---

# Earshot (sound for code-made reels)

The owner asked for this on 25 Oct (instagram.com/reel/De4XVvXPTWY: "three free tools add pro sound effects to
Claude edits").

**What placing sound on a reel means here:** `nixwoods-reel/system/sfx/place.py` places and mixes the effects. It
always works, because its sounds are synthesized in our code, with real CC0 recordings from Openverse used where
they can be fetched. Earshot raises the quality: a better bank, measured sync points, and a way to listen to the
result.

## Setup, once per cloud session (needs the owner's permission)
On 25 Oct the session's safety check blocked installing or running externally fetched code. Once the owner allows it:

```bash
bash .claude/skills/earshot/setup.sh          # clones 591fa3e into ~/.cache/earshot, CPU torch venv, `earshot doctor`
~/.cache/earshot/.venv/bin/earshot doctor --fetch   # optional: the two listening models (~1.1 GB, Hugging Face)
```

`sfx` and `kit` need no models and no network.

## Use
- **Find a sound:** `earshot sfx list --kind whoosh` (also `knock`, `ui_pop`, `cut_hit`, `mallet`, `shutter` and
  more).
- **Render a take aimed at a moment:** `earshot sfx render whoosh_fast/crisp -o w.wav --dur 0.8 --apex 0.32`. Here
  `--apex` puts the whoosh's peak within 5 ms of the target, and `--pitch` takes a note name for mallets and knocks.
- **A whole reel's kit:** `earshot kit init --preset calm -o audio/kit.json`, then
  `earshot kit render audio/kit.json --out audio/kit`. That writes takes plus `kit.lock.json` with each take's onset,
  peak and end.
  - Use `calm` for our quiet product reels.
  - Use `launch` for reels cut to music: it sets each effect's level over the music bed and its offset from the cut.
- **Listen to the result** (models needed):
  - `earshot timeline out.mp4 --video out.mp4` reports events, loudness and sync to the cuts;
  - `earshot sheet out.mp4 -o sheet.png` makes a picture to look at;
  - `earshot critique out.mp4` gives a scorecard with timestamped fixes.

## NixWoods rules
- Our own sound only. Never a reference creator's audio.
- Never the `llm` command: it uploads audio to Gemini.
- **Where effects land** (Earshot's medians, also coded in `place.py`):
  - a whoosh peaks 37 ms after the cut;
  - a pop lands 30 ms after its text;
  - a knock comes 40 ms before contact;
  - a click comes 11 ms early;
  - effects sit 3–10 dB over the music bed.
- **Keep the brand calm:** one effect per beat. No whoosh on a fade, no risers on product shots. Music fades over the
  last 0.7–0.9 s (MOTION.md).
- Check by measurement: loudness before and after (`ffmpeg ... ebur128`), a spectrogram, and Earshot's critique when
  available. Never trust one listen.
