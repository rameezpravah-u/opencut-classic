# NixWoods "the art of handmade": the Aurora's making on @heycarmenta's cut pattern

**Reference:** instagram.com/reel/DcyiiBGPYjc by @heycarmenta (7.98 s, 23k views). It is a woodshop montage with the
small lowercase line "the art of handmade" on screen throughout. The owner asked on 13 Oct to "adapt and use the same
music and pattern".

## The pattern, measured from the reference
- **Cuts:** 26 cuts, each on an onset of its audio (matched within one frame), in a fast-slow-fast ramp:
  - for the first 0.9 s the cuts come about 0.1 s apart;
  - they widen to a 1.27 s hold from 3.13 s;
  - they close back to about 0.1 s;
  - the last 0.4 s (from 7.57 s) is the finished piece.
- **Timing kept here:** this cut uses the reference's cut times to the frame (`CUTS` in `handmade_cut.py`).

## This cut
- **Footage:** real Aurora workshop footage only, with no faces. The clips are Drive copies in
  `../festive-ad-cuts/src/` and are not committed. Most are listed in `../festive-ad-cuts/README.md`; IMG_7653 (strips
  in sawdust) and IMG_7992 (bars lit, second angle) are not in that list yet.
- **Order:**
  1. teak planks, cut strips in sawdust, routed bars, black-finish bars;
  2. the bars lit on test, held for the long beat;
  3. faster details;
  4. the Aurora lit on a wall to close.
- **Grade:** the MOTION.md montage grade.
- **Text:** "the art of handmade" in Inter 400, 34 px, white, centred at y 640. The reference has it at about 25%
  height. It sits a little lower here so it clears the lit Aurora bar in the last shot.
- **Left out:** the CNC-router clips (IMG_7698/7699), so the "handmade" line never sits over a machine. The bulb table
  lamp (IMG_7664) and the NixLine bars are also out, so every shot shows the Aurora.

## Files in `out/`
| File | Audio | Use |
|---|---|---|
| `…-in-app-audio.mp4` | silent track | **Posting master.** On Instagram, tap "Use audio" on the reference reel and start it at 0:00. The cuts are timed to it. |
| `…-music6.mp4` | music6-corners | Ads, or if that audio is not offered to a business account. The same pattern on music6's 1/8-beat grid, with the hold on a downbeat (track from 1.441 s). |
| `…-cover.jpg`, `…-sheet.jpg` | | Cover from the lit end frame; review sheet. |

The reference audio is not ours to publish, so the review copy carrying it was sent to the owner and never committed.

## Re-render
```bash
python3 brand-reels/art-of-handmade/handmade_cut.py [--ref-audio ref.wav --preview /tmp/preview.mp4]
```
