# Luma Pillar, "money can't buy happiness but it can buy cool stuff for your room"

**Reference:** instagram.com/reel/DeXK2zJqm7S by @exen3d.ir (6.34 s, one lamp lit in the dark). The owner asked on
13 Oct: "Use the exact music and style and rhythm and fonts."

## What is matched
- **Rhythm:** 13 hard cuts at the reference's own times, each landing on an onset of its track: 0, 0.60, 1.17, 1.87,
  2.43, 2.90, 3.40, 3.83, 4.30, 4.73, 5.07, 5.43 and 5.80 s, running to 6.34 s.
- **Style:**
  - every cut is a different angle of the one lamp, lit, in a low-key room;
  - one word per cut, centred at mid-frame;
  - a small brand mark low in the frame.
- **Font:**
  - The reference's face is a wide, fat serif with ball terminals. Its exact name is not identifiable from the
    video.
  - The closest free face is **Ultra** (Apache 2.0, `assets/Ultra-400.ttf`, licence beside it). It is set at 69 px,
    so "happiness" is about 450 px wide, as in the reference.
  - The colour is the reference's yellow, **#F1F811**.
  - A thin dark edge keeps the words legible where they cross our lamp's bright bar. The reference's lamp is blue, so
    it needs none.
- **Words:** the reference's own line, one word a cut. Its track is instrumental, so the words are on screen only.
- **Music:**
  - The posting master (`…-in-app-audio.mp4`) has a silent track. On Instagram, tap "Use audio" on the reference
    reel and start it at 0:00; the cuts sit on its beats.
  - The review copy that carries the reference audio was sent to the owner and is not committed.
  - `…-music3.mp4` keeps the same cuts on our own music3-design track, for ads or if that audio is not offered to a
    business account.

## Footage
- **Source:** the owner's styling clip (`../luma-styled/src/luma-styling-20260331.mov`), lit shots only. No faces;
  hands only on one cut.
- **Shots:** cut by `../luma-styled/luma_shots.py`, which straightens lit shots and holds them upright.
- **Grade:** low-key: the lamp's true warm light is kept, shadows are pushed down, and a soft vignette is added.
- **No price on screen**, as in the reference. The caption carries ₹1,599 (live 13 Oct).

```bash
python3 brand-reels/cool-stuff/cool_stuff.py [--ref-audio ref.wav --preview /tmp/preview.mp4]
```
