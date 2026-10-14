# NixWoods, "I know I should sleep, but the voices in my head go…"

**Reference:** instagram.com/reel/Dd-QOeRvf0Q by @dreamspace_interiors_calgary (12.7 s, 43k views). The owner asked on
14 Oct: "Interesting music and then sound, can you do the same?"

## The reference, every frame seen and the audio measured
1. **0–2.97 s:** the line "I know I should sleep, but the voices in my head go…" plays as tonal audio (transcribed),
   over a POV walk into the shop. The same words are set large in a cream condensed serif.
2. **2.97–6.9 s:** the "voices" are the shop. Seven hard cuts, exactly 0.567 s apart, each a machine with its own sound:
   router, clamp, mitre saw, sanding, table saw, CNC and drill. The audio turns from tonal to broadband noise right on
   the first cut.
3. **6.9–12.7 s:** one held wide shot of the shop floor, over a low hum. The text reads "the sound / of custom…", then
   from about 8.6 s "custom millwork" with a small "DreamSpace · Calgary".

## Ours (`voices.py`, 12.7 s)
1. **0–2.97 s:** our music1-aesthetic under the Luma Pillar lit in a dark room at night (it is bedtime).
   - The line is set in Instrument Serif, the closest free face (OFL, `assets/Instrument_Serif-400.ttf`), in the
     reference's cream.
2. **2.97 s:** the music stops dead, a 12 ms cut, and the floor takes over: seven cuts at the reference's 0.567 s
   spacing, each with the sound it was recorded with:
   1. the CNC router;
   2. strips cut in the sawdust;
   3. the router close;
   4. routed Aurora bars;
   5. black-finished bars;
   6. a bar switched on, on test (its click);
   7. a lit bar.

   **Levelling:** each shot is levelled to −18 dB RMS, with quiet handling lifted at most 12 dB, and 15 ms crossfades
   at the cuts.
3. **6.9–12.7 s:** the lamp held, with smoke drifting through the glow in slow motion.
   - **Text:** "the sound / of handmade…", then "handmade lighting" with "NixWoods · India".
   - **Sound:** a quiet room tone from a lamp-lit room clip (IMG_7664).

**Audio rights:**
- Every sound is ours, so the master is postable as is, organic and in ads.
- The reference's audio is never used. Its vocal line is not ours, and its machines are another workshop's, which
  would misrepresent our floor.

**Faces:** none. Hands only.

```bash
python3 brand-reels/voices-in-my-head/voices.py
```
