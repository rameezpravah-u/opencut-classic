# NixWoods, "making something look good, and making something well"

**Reference:** instagram.com/reel/Db3S5z4s8do by @artevita_interiors (29.2 s, 112k views). The owner asked on 14 Oct:
"Use this voice and script on our work."

## The reference, every frame seen
**Voice and script:** a calm male voice reads four lines (local transcription, faster-whisper small.en):
> "There is a difference between making something look good and making something well. The details people never
> see often matter the most. A piece reveals what its maker values through its materials, its construction and the
> care invested in every decision. Quality is not a feature, it's a reflection of character."

**Picture:** 12 slow, close shots of the shop: a hand plane, a sander, a press wheel, a shear, finished trays and the
makers. Cuts at 2.63, 3.79, 9.54, 14.04, 15.75, 17.04, 18.04, 19.08, 21.08, 22.83 and 27.17 s.

**Type and brand:**
- Each spoken phrase is set in small white capitals at mid-frame while it is said, and it is gone in the pauses.
- A small wordmark sits low in the frame.
- The reel ends on a wood surface with soft light, the logo tile fades in, then black.

## Ours
**Picture:** the reference's shot lengths on our real footage, with no faces:
- teak planks;
- the CNC router;
- cut strips;
- routed and black-finished Aurora bars;
- bars lit on test;
- lit bars on the floor and in the hand;
- the Aurora coming on a wall;
- last, our teak close with warm light and the NX tile.

The two long holds (3.8–9.5 s and 9.5–14.0 s) are split in two, since our clips are shorter. Three shots are slowed
with motion interpolation. The Aurora shot uses only the clip's first 1.95 s, before its own zoom transition.

**Captions:** the reference's phrases at the reference's word onsets, with its typos corrected ("construction",
"character", "values"). Inter 400, about 480 px wide for the long phrases. The NIXWOODS mark sits at y 1500, inside
the safe zone.

**Grade:** the MOTION.md montage grade, keeping a little more of each shot's own colour (55 %), as the reference does.

## Voice
| File | Audio | Use |
|---|---|---|
| `…-in-app-audio.mp4` | silent track | **Organic posting.** On Instagram, tap "Use audio" on the reference reel and start it at 0:00. Their voice then reads every caption as it appears. |
| `…-music1.mp4` | our music1-aesthetic | **Ads**, and the fallback if that audio is not offered to a business account. The words are on screen only. |

- **Their audio is never committed or posted from here.** The review copy carrying it was sent to the owner from
  scratch storage.
- **Their voice is not cloned.** Copying a real person's voice without consent is not done. If we want our own voice
  for ads, it would be one ElevenLabs take of the same script with a calm male voice. That costs credits, about 330
  for the script's length, so it needs the owner's approval first.

```bash
python3 brand-reels/made-well/made_well.py [--ref-audio ref.wav --preview /tmp/preview.mp4]
```
